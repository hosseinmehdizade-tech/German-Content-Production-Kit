#!/usr/bin/env python3
"""Read-only fail-closed global policy router and adoption-matrix integrity audit.

This is a PROCESS CONSISTENCY test, NEVER learner Stage4/5/6/7 acceptance.
Run: python Verification/audit_global_policy_sync_v1.py --check
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
MATRIX = "Optimization-Program/Verification/GLOBAL-POLICY-ADOPTION-MATRIX-20261105.json"
START = "Prompt/START-PROMPT-v3.3.6.md"
MASTER = "Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.3.6.md"
CONTRACT = "Prompt/GLOBAL-POLICY-SYNCHRONIZATION-v1.0.0.md"
ENTRY = "Prompt/ACTIVE-PROMPT.txt"
README = "README.md"
BOOTSTRAP = "PROJECT-BOOTSTRAP.md"
REQUIRED_POLICIES = {
    "currentness", "seven_stages", "stage3_onepass", "linguistic_qa",
    "risk_based_stage4", "kombinationen_pointer", "kombinationen_source_first",
    "related_taxonomy", "lexical_relation_display", "stage5_neutral_validator",
    "stage5_clean_builder", "stage5_delivery", "stage5_hygiene",
    "related_advisory", "lexical_relation_advisory",
}
REQUIRED_INVARIANTS = {
    "user_explicit_newer_validated_source_precedes_stale_git",
    "immutable_raw_and_locked",
    "no_unapproved_app_ui_or_importer_or_srs_fsrs_change",
    "no_source_or_card_mutation_from_optimization_audit",
    "no_inference_of_stage4_from_machine_qa",
    "no_inference_of_real_adapter_coverage_from_synthetic_envelopes",
    "no_inference_of_native_stage6_from_static_build",
    "no_forced_related_or_combination_quota",
    "no_fabricated_graph_ids_or_lexical_senses",
    "cross_workstream_state_isolation",
    "evidence_sha_and_exact_stage_scope_required",
    "write_once_report_and_compare_and_swap",
}
AXES = [
    "SOURCE_AUTHORITY_CURRENTNESS", "NORMATIVE_POLICY_VERSION",
    "PRODUCER_ADAPTER_CAPABILITY", "STAGE_ACCEPTANCE_EVIDENCE",
]


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def safe_path(value: str) -> bool:
    if not isinstance(value, str) or not value.strip() or "\\" in value:
        return False
    p = Path(value)
    return not p.is_absolute() and ".." not in p.parts and str(p).startswith(value)


def tracked_workspaces(root: Path = ROOT) -> list[str]:
    proc = subprocess.run(["git", "ls-files", "-z", "--", "Workspaces/"],
                          cwd=root, capture_output=True, check=True)
    paths = proc.stdout.decode("utf-8").split("\0")
    return sorted({"Workspaces/" + a.split("/")[1]
                   for a in paths if a.startswith("Workspaces/")
                   and len(a.split("/")) >= 3})


def load_snapshot(root: Path = ROOT):
    reg = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    mat = json.loads((root / MATRIX).read_text(encoding="utf-8"))
    files = {}
    paths = {ENTRY, START, MASTER, CONTRACT, README, BOOTSTRAP, REGISTRY, MATRIX}
    for policy in reg.get("policy_bindings", {}).values():
        if isinstance(policy, dict) and safe_path(policy.get("path")):
            paths.add(policy["path"])
    for path in paths:
        p = root / path
        if p.is_file() and not p.is_symlink():
            files[path] = p.read_bytes()
    return reg, mat, tracked_workspaces(root), files


def audit_snapshot(reg: dict, mat: dict, tracked_dirs: list[str],
                   files: dict[str, bytes]) -> list[str]:
    errors = []
    if reg.get("schema") != "gcpk-global-policy-registry@1.0.0":
        errors.append("REGISTRY_SCHEMA")
    if mat.get("schema") != "gcpk-global-policy-adoption-matrix@1.0.0":
        errors.append("MATRIX_SCHEMA")
    if reg.get("active_entrypoint") != START or mat.get("registry") != REGISTRY:
        errors.append("ENTRYPOINT_OR_MATRIX_MISMATCH")
    if reg.get("architecture") != CONTRACT or reg.get("adoption_matrix") != MATRIX:
        errors.append("GLOBAL_POINTER_MISMATCH")
    if reg.get("decision_axes") != AXES:
        errors.append("INDEPENDENT_DECISION_AXES_CHANGED")
    inv = reg.get("protected_invariants", {})
    if any(inv.get(k) is not True for k in REQUIRED_INVARIANTS):
        errors.append("PROTECTED_SAFETY_INVARIANT_MISSING_OR_DISABLED")
    pre = reg.get("precedence", {})
    if not all(isinstance(pre.get(x), str) and pre[x].strip()
               for x in ("source_authority", "norms", "stage_proof")):
        errors.append("PRECEDENCE_UNDEFINED")
    policies = reg.get("policy_bindings", {})
    if set(policies) != REQUIRED_POLICIES:
        errors.append("MANDATORY_POLICY_BINDINGS_CHANGED")
    aliases = {}
    for key, obj in policies.items():
        if not isinstance(obj, dict):
            errors.append("INVALID_BINDING:" + key)
            continue
        path, digest = obj.get("path"), obj.get("blob_sha")
        if not safe_path(path):
            errors.append("UNSAFE_POLICY_PATH:" + key)
            continue
        if path in aliases:
            errors.append("DUPLICATE_POLICY_PATH:" + key)
        aliases[path] = key
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{40}", digest):
            errors.append("INVALID_POLICY_PIN:" + key)
        elif path not in files:
            errors.append("MISSING_ACTIVE_POLICY:" + key)
        elif git_blob_sha(files[path]) != digest:
            errors.append("STALE_POLICY_BLOB_PIN:" + key)
        if obj.get("scope") not in {
            "ALL_WORKSTREAM_STARTUP", "ALL_PRODUCERS", "LEXICAL_MUTABLE",
            "LINGUISTIC_REVIEW", "LEXICAL_MUTABLE_AND_VISIBLE_PROJECTION",
            "NEUTRAL_VOCABULARY_PROJECTION", "USER_FACING_LEXICAL_DELIVERY",
            "CLEAN_DELIVERY", "LEXICAL_QA_ADVISORY",
        }:
            errors.append("INVALID_POLICY_SCOPE:" + key)
        stages = obj.get("stages")
        if not isinstance(stages, list) or not stages or any(
                type(v) is not int or v < 0 or v > 7 for v in stages):
            errors.append("INVALID_POLICY_STAGE:" + key)

    for name in (ENTRY, START, MASTER, CONTRACT, README, BOOTSTRAP):
        if name not in files:
            errors.append("MISSING_ROUTER_FILE:" + name)
    def txt(path):
        return files.get(path, b"").decode("utf-8", "replace")
    if txt(ENTRY).strip() != Path(START).name:
        errors.append("WRONG_ACTIVE_PROMPT_POINTER")
    for target in (START, MASTER, README, BOOTSTRAP):
        first = txt(target)[:1600]
        if REGISTRY not in first or CONTRACT not in first:
            errors.append("MISSING_ENTRYPOINT_ROUTER:" + target)
    if "Historical 2026-11-04 A1 V25 replay" not in txt(README):
        errors.append("OLD_RELATED_V1_ACTIVE_DESCRIPTION_NOT_RELABELED")
    if "Exact per-workstream adapter/CI parity remains unverified" in txt(START):
        errors.append("STALE_ADAPTER_CI_CLAIM")
    if "normative full v3.3.6 master prompt" not in txt(MASTER):
        errors.append("PORTABLE_MASTER_LOCATOR_MISSING")
    if "four independent axes" not in txt(CONTRACT).lower():
        errors.append("DECISION_AXIS_CONTRACT_MISSING")
    if mat.get("no_blanket_certification") is not True:
        errors.append("FALSE_BULK_ACCEPTANCE")
    fi = mat.get("family_catalog")
    if not isinstance(fi, list) or len(fi) != 21:
        errors.append("LIBRARY_FAMILY_INVENTORY_SIZE")
        fi = []
    names = [f.get("name") for f in fi if isinstance(f, dict)]
    if len(names) != len(fi) or len(set(names)) != len(names):
        errors.append("LIBRARY_FAMILY_IDENTITY_DUPLICATE")
    dirs = mat.get("git_workspaces")
    if not isinstance(dirs, list):
        errors.append("MATRIX_WORKSPACES_NOT_LIST")
        dirs = []
    actual_names = [x.get("path") for x in dirs if isinstance(x, dict)]
    if sorted(actual_names) != sorted(tracked_dirs):
        errors.append("WORKSPACE_INVENTORY_DRIFT")
    if len(set(actual_names)) != len(actual_names):
        errors.append("WORKSPACE_DUPLICATE")
    for entry in dirs:
        if not isinstance(entry, dict):
            errors.append("WORKSPACE_ENTRY_NOT_OBJECT")
            continue
        path = str(entry.get("path", ""))
        if entry.get("global_policy_routing") != "INHERITS_NORMATIVE_GLOBAL_ENTRYPOINT_FOR_FUTURE_AUTHORIZED_WORK":
            errors.append("UNROUTED_WORKSPACE:" + path)
        for field, expected in (
            ("native_adapter_verified", "NO_WORKSPACE_SPECIFIC_PROOF"),
            ("real_output_verified", "NO_WORKSPACE_WIDE_PROOF"),
            ("semantic_stage4", "NOT_ATTESTED_BY_SYNC"),
            ("stage6_runtime", "NOT_ATTESTED_BY_SYNC"),
        ):
            if entry.get(field) != expected:
                errors.append("UNSUPPORTED_ADOPTION_PROMOTION:" + path + ":" + field)
        if entry.get("immutable_history_changes") is not False:
            errors.append("HISTORIC_MUTATION_CLAIM:" + path)
    obs = mat.get("scoped_observations", [])
    if not any(isinstance(x, dict) and x.get("failing_rows") == 145 and
               "FAIL_CLOSED" in x.get("result", "") for x in obs):
        errors.append("B1_145_REAL_BLOCKER_HIDDEN")
    gaps = " ".join(mat.get("open_gaps", []))
    if "Vocabulary" not in gaps or "B1" not in gaps:
        errors.append("REAL_PARITY_GAPS_NOT_RECORDED")
    for path in (REGISTRY, MATRIX):
        if path not in files:
            errors.append("MISSING_REGISTRY_OR_MATRIX:" + path)
    return sorted(set(errors))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    reg, mat, dirs, files = load_snapshot()
    failures = audit_snapshot(reg, mat, dirs, files)
    outcome = {
        "schema": "gcpk-global-policy-sync-audit@1.0.0",
        "status": "PASS_POLICY_ROUTING_ONLY_NOT_ALL_WORKSTREAM_QA" if not failures else "BLOCKED",
        "policy_bindings": len(reg.get("policy_bindings", {})),
        "workspace_directories": len(dirs),
        "library_families_declared_not_git_verified": len(mat.get("family_catalog", [])),
        "all_native_producer_parity_verified": False,
        "independent_stage4_acceptance": False,
        "native_stage6_acceptance": False,
        "errors": failures,
    }
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
