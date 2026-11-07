#!/usr/bin/env python3
"""Read-only GFP-OPT P1 gate over a REAL source owner's current Git checkout.

Checks active central policy bytes, source ownership and stage boundaries.
A PASS here is a *routing/preflight* result, never Stage4 approval or adoption.
No source, learner data, archive, Library, app or checkpoint is written.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

REGISTRY = "Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
DOMAINS = "Optimization-Program/Control-Center/Profiles/P1-ALL-FAMILY-APPLICABILITY-v1.json"
OWNER = "Workspaces/aspekte-b1plus-v336"
FAMILY = "family:aspekte-b1plus"
WORKSPACE = "workspace:aspekte-b1plus-v336"
PROJECT = "aspekte-b1plus"
MANDATORY_STAGE4 = {"curated_current_delta_qa", "seven_stages",
                    "risk_based_stage4", "linguistic_qa"}
# Current was curated for three months; never use raw textbook re-inventory as a gate.
STAGE4_NONIMPORT = "STAGE4_G2_"

class P1GateError(ValueError):
    pass

def require(condition: bool, reason: str) -> None:
    if not condition:
        raise P1GateError(reason)

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\\0" + data).hexdigest()

def is_blob(data: bytes, expected: str) -> bool:
    return bool(re.fullmatch(r"[a-f0-9]{40}", str(expected))) and (
        git_blob(data) == expected or
        (b"\\r\\n" in data and git_blob(data.replace(b"\\r\\n", b"\\n")) == expected)
    )

def file_bytes(root: Path, rel: str) -> bytes:
    candidate = Path(rel)
    require(not candidate.is_absolute() and ".." not in candidate.parts,
            "UNSAFE_PATH")
    file = root / candidate
    require(file.is_file() and not file.is_symlink() and
            file.resolve().is_relative_to(root.resolve()), "MISSING_OR_UNSAFE_FILE:" + rel)
    return file.read_bytes()

def read_json(root: Path, rel: str) -> tuple[dict, str]:
    raw = file_bytes(root, rel)
    value = json.loads(raw.decode("utf-8-sig"))
    require(isinstance(value, dict), "JSON_NOT_OBJECT:" + rel)
    return value, git_blob(raw)

def evaluate(root: Path, *, registry: dict | None = None,
             catalog: dict | None = None, domains: dict | None = None,
             latest: dict | None = None, checkpoint: dict | None = None) -> dict:
    """Fresh source-specific gate. Injected objects are only for negative tests."""
    root = Path(root).resolve()
    actual_registry, reg_blob = read_json(root, REGISTRY)
    actual_catalog, cat_blob = read_json(root, CATALOG)
    actual_domains, domain_blob = read_json(root, DOMAINS)
    actual_latest, latest_blob = read_json(root, OWNER + "/LATEST.json")
    actual_checkpoint, checkpoint_blob = read_json(root, OWNER + "/CHECKPOINT.json")
    reg = copy.deepcopy(actual_registry if registry is None else registry)
    cat = copy.deepcopy(actual_catalog if catalog is None else catalog)
    prof = copy.deepcopy(actual_domains if domains is None else domains)
    lat = copy.deepcopy(actual_latest if latest is None else latest)
    cp = copy.deepcopy(actual_checkpoint if checkpoint is None else checkpoint)

    require(reg.get("schema") == "gcpk-global-policy-registry@1.0.0"
            and reg.get("status"), "REGISTRY_NOT_ACTIVE")
    bindings = reg.get("policy_bindings")
    require(isinstance(bindings, dict) and len(bindings) >= 22,
            "CENTRAL_BINDING_INVENTORY_INCOMPLETE")
    require(MANDATORY_STAGE4.issubset(bindings),
            "MANDATORY_STAGE4_POLICY_MISSING")
    for key, rule in bindings.items():
        require(isinstance(rule, dict) and isinstance(rule.get("stages"), list),
                "MALFORMED_POLICY_BINDING:" + str(key))
        content = file_bytes(root, rule.get("path", ""))
        require(is_blob(content, rule.get("blob_sha", "")),
                "POLICY_GIT_BLOB_DRIFT:" + key)

    workspace = [x for x in cat.get("workspaces", [])
                 if x.get("id") == WORKSPACE]
    family = [x for x in cat.get("families", [])
              if x.get("id") == FAMILY]
    scoped = [x for x in prof.get("families", [])
              if x.get("id") == FAMILY]
    require(len(workspace) == len(family) == len(scoped) == 1,
            "MISSING_OR_DUPLICATE_SOURCE_OWNER")
    require(workspace[0].get("git_dir") == OWNER
            and workspace[0].get("parent_family_id") == FAMILY
            and workspace[0].get("kind") == "CONTENT_OR_SOURCE_SPECIFIC_WORKSPACE"
            and scoped[0].get("declared_domain") == "LEXICAL_SOURCE_CANDIDATE",
            "WRONG_FAMILY_WORKSPACE_OR_DOMAIN")

    require(lat.get("project_id") == cp.get("project_id") == PROJECT,
            "OWNER_PROJECT_ID_DRIFT")
    require(lat.get("source_sha256") == cp.get("source_sha256")
            and bool(re.fullmatch(r"[a-f0-9]{64}", str(lat.get("source_sha256", "")))),
            "CURATED_OWNER_SOURCE_IDENTITY_DRIFT")
    require(cp.get("production_authorized") is True,
            "SOURCE_OWNER_PRODUCTION_NOT_AUTHORIZED")
    require(lat.get("stage1_lexical_records_processed") == cp.get("source_rows")
            and isinstance(cp.get("source_rows"), int)
            and cp["source_rows"] > 0, "SOURCE_ROW_COVERAGE_DRIFT")
    require(str(lat.get("current_stage", "")).startswith(STAGE4_NONIMPORT),
            "UNEXPECTED_SOURCE_STAGE_REVIEW_REQUIRED")
    require(lat.get("import_ready") is False
            and lat.get("stage4_formal_acceptance") is False
            and cp.get("stage5") == cp.get("stage6") == cp.get("stage7") == "NOT_STARTED",
            "FALSE_STAGE4_5_6_7_OR_IMPORT_PROMOTION")
    require("NONIMPORT" in str(lat["current_stage"])
            and "NONIMPORT" in str(cp.get("status", "")),
            "OWNER_NONIMPORT_BOUNDARY_LOST")
    require(4 in bindings["risk_based_stage4"]["stages"]
            and 4 in bindings["linguistic_qa"]["stages"]
            and 4 in bindings["curated_current_delta_qa"]["stages"]
            and 4 in bindings["seven_stages"]["stages"],
            "STAGE4_POLICY_ROUTING_GAP")
    visible = re.search(r"_(\\d+)_REMAIN_NONIMPORT", lat["current_stage"])
    remaining = int(visible.group(1)) if visible else None
    active = sorted(key for key, rule in bindings.items() if 4 in rule["stages"])
    return {
        "schema": "gfp-opt-p1-real-owner-stage4-preflight@1.0.0",
        "owner": {"family_id": FAMILY, "workspace_id": WORKSPACE, "project_id": PROJECT,
                  "curated_source_sha256": lat["source_sha256"],
                  "source_rows": cp["source_rows"],
                  "pending_form_scope_checks_from_latest": remaining,
                  "current_stage": lat["current_stage"]},
        "scope": "REAL_SOURCE_OWNER_CURRENT_GIT_CHECKOUT_READONLY",
        "policy": {"registry_git_blob": reg_blob, "catalog_git_blob": cat_blob,
                   "domain_profile_git_blob": domain_blob,
                   "registered_bindings": len(bindings),
                   "byte_pinned_bindings_verified": len(bindings),
                   "stage4_routed_binding_ids": active},
        "owner_git_blobs": {"latest": latest_blob, "checkpoint": checkpoint_blob},
        "stage4": "HOLD_NO_FORMAL_LINGUISTIC_APPROVAL",
        "stage5": "BLOCKED_NO_NEW_SOURCE_OWNER_STAGE4_APPROVAL",
        "stage6": "NOT_RUN",
        "stage7": "NOT_RUN",
        "new_formal_policy_adoptions": 0,
        "report_status": "PASS_REAL_OWNER_AND_ALL_POLICY_BYTES__NO_STAGE5_ADOPTION",
        "next": "Complete source-owned 274 remaining G2 form checks and independent semantic Stage4; after a NEW explicit owner Stage5 decision, verify original four roles, live Git main and Library bytes. Do not reuse historic ZIPs."
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    a = ap.parse_args()
    try:
        print(json.dumps(evaluate(a.root), indent=2, ensure_ascii=False, sort_keys=True))
    except (P1GateError, OSError, ValueError) as err:
        print(json.dumps({"status": "BLOCKED", "reason": str(err)}))
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
