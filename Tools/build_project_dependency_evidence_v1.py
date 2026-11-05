#!/usr/bin/env python3
"""Evidence-aware read-only project dependency graph and prospective change impact.

No inferences of learner content quality, full source provenance, Stage4 or Stage6.
All mutable status is a Git-index metadata hint until independent SHA/receipt QA.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
STATE = "PROJECT-STATE.json"
SCHEMA = "gcpk-project-dependency-evidence@1.0.0"

spec = importlib.util.spec_from_file_location(
    "control_center_phase1", ROOT / "Tools/build_project_control_center_v1.py")
phase1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phase1)


def index_blobs(root=ROOT):
    raw = phase1.git("ls-files", "--stage", "-z", "--", "Workspaces/",
                     "Prompt/", "Verification/", "Tools/",
                     "Optimization-Program/", STATE, "README.md",
                     "WORKSTREAM-RESUME-CURRENTNESS-POLICY.json",
                     "LINGUISTIC-QA-AUTHORITY-POLICY.json",
                     "STAGE4-RISK-BASED-ACCEPTANCE-POLICY-v1.0.1.json",
                     "CONTENT-OUTPUT-DELIVERY-POLICY.json",
                     root=root)
    result = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        header, path = entry.split(b"\t", 1)
        mode, sha, stage = header.decode("ascii").split(" ")
        if stage != "0":
            raise ValueError("UNMERGED_GIT_INDEX")
        key = path.decode("utf-8")
        if key in result:
            raise ValueError("DUPLICATE_GIT_INDEX_ENTRY")
        result[key] = sha
    return result


def source_json(path, idx, root=ROOT):
    return phase1.load_json_from_index(path, idx, root=root)


def safe_relative(path):
    if not isinstance(path, str) or not path or "\\" in path:
        return False
    if ":" in path.split("/")[0]:
        return False
    p = PurePosixPath(path)
    return not p.is_absolute() and ".." not in p.parts and str(p) == path


def binding_failures(reg, idx):
    errors = []
    if reg.get("schema") != "gcpk-global-policy-registry@1.0.0":
        errors.append("REGISTRY_SCHEMA_INVALID")
    bindings = reg.get("policy_bindings")
    if not isinstance(bindings, dict) or not bindings:
        return ["POLICIES_MISSING"]
    for key, val in bindings.items():
        if not isinstance(val, dict):
            errors.append("POLICY_BINDING_NOT_OBJECT:" + key)
            continue
        path, pin = val.get("path"), val.get("blob_sha")
        if not safe_relative(path):
            errors.append("UNSAFE_POLICY_PATH:" + key)
        elif idx.get(path) is None:
            errors.append("PINNED_POLICY_NOT_IN_GIT_INDEX:" + key)
        elif idx[path] != pin:
            errors.append("POLICY_PIN_DRIFT:" + key)
        if not isinstance(val.get("scope"), str):
            errors.append("POLICY_SCOPE_MISSING:" + key)
    return sorted(errors)


def classify_scope(binding, workspace):
    """Return intended review edge classification, NOT producer certification."""
    scope = binding["scope"]
    kind = workspace["kind"]
    if scope == "ALL_WORKSTREAM_STARTUP":
        return "MANDATORY_ROUTING_SCOPE__NOT_IMPLEMENTATION_PROOF"
    if kind == "CROSS_SOURCE_QA_OR_RUNTIME_WORKSPACE":
        return None
    if scope == "ALL_PRODUCERS":
        return "GENERAL_SOURCE_WORKSPACE_EXPECTED__NOT_IMPLEMENTATION_PROOF"
    if scope in ("NEUTRAL_VOCABULARY_PROJECTION", "CLEAN_DELIVERY"):
        return "CONDITIONAL_CONSUMER_SCHEMA__ONLY_IF_USING_TARGET_BUILDER"
    if scope == "LINGUISTIC_REVIEW":
        return "CONDITIONAL_STAGE4_REVIEW__RECEIPT_REQUIRED"
    if scope in ("LEXICAL_MUTABLE", "LEXICAL_MUTABLE_AND_VISIBLE_PROJECTION",
                 "USER_FACING_LEXICAL_DELIVERY", "LEXICAL_QA_ADVISORY"):
        return "CONDITIONAL_LEXICAL_OUTPUT__NO_ASSUMED_ADAPTER_PARITY"
    return "CONDITIONAL_UNRECOGNIZED_SCOPE__REVIEW"


def normalize_receipt_pointer(value, directory, idx):
    """Report a candidate path if unambiguous; never synthesize source evidence."""
    if not isinstance(value, str) or not value.strip():
        return {"declaration": "NOT_A_STRING_RECEIPT", "git_path": None, "git_blob": None}
    value = value.strip()
    if value.startswith(("http://", "https://", "libfile_", "/")):
        return {"declaration": "EXTERNAL_OR_ABSOLUTE_REFERENCE_NOT_GIT_PROOF",
                "git_path": None, "git_blob": None}
    if not safe_relative(value):
        return {"declaration": "UNSAFE_OR_AMBIGUOUS_RELATIVE_REFERENCE",
                "git_path": None, "git_blob": None}
    candidates = [value] if value.startswith(("Workspaces/", "Verification/",
                 "Optimization-Program/")) else [directory + "/" + value, value]
    matched = [p for p in candidates if p in idx]
    if len(matched) == 1:
        return {"declaration": "GIT_RECEIPT_PATH_TRACKED__CONTENT_NOT_AUDITED",
                "git_path": matched[0], "git_blob": idx[matched[0]]}
    if len(matched) > 1:
        return {"declaration": "AMBIGUOUS_RECEIPT_PATH_HOLD",
                "git_path": None, "git_blob": None}
    return {"declaration": "DECLARED_RECEIPT_PATH_NOT_TRACKED_HOLD",
            "git_path": None, "git_blob": None}


def scan_evidence(directory, pointer, idx, selected_path):
    if not isinstance(pointer, dict):
        return {"status": "NO_PARSEABLE_POINTER__NO_CERTIFICATE",
                "pointer_path": None, "pointer_blob": None,
                "artifact_sha256_claim": None, "receipt_refs": []}
    digest = pointer.get("artifact_sha256")
    if not isinstance(digest, str):
        artifact = pointer.get("artifact")
        digest = artifact.get("sha256") if isinstance(artifact, dict) else None
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        digest = None
    receipts = []
    for field in ("receipt", "latest_receipt", "stage4_official_gate_receipt",
                  "stage5_receipt", "authoritative_checkpoint"):
        val = pointer.get(field)
        if isinstance(val, str) and val:
            receipts.append({"field": field, **normalize_receipt_pointer(val, directory, idx)})
    return {
        "status": "METADATA_AND_REFERENCES_ONLY__NOT_INDEPENDENT_ARTIFACT_PROOF",
        "pointer_path": selected_path,
        "pointer_blob": idx.get(selected_path),
        "artifact_sha256_claim": digest,
        "artifact_sha256_readback": "NOT_PERFORMED__SOURCE_ARTIFACT_NOT_MOUNTED",
        "receipt_refs": receipts,
        "linguistic_stage4": "NOT_CERTIFIED_BY_THIS_REPORT",
        "stage5_exact_build": "NOT_CERTIFIED_BY_THIS_REPORT",
        "native_stage6": "NOT_CERTIFIED_BY_THIS_REPORT",
    }


def build_graph(cat, reg, idx, root_state, pointers, changed_paths=None):
    cat_issues = phase1.catalog_errors(cat)
    if cat_issues:
        raise ValueError("CATALOG_INVALID:" + ",".join(cat_issues))
    pin_issues = binding_failures(reg, idx)
    if pin_issues:
        raise ValueError("POLICY_DRIFT_BLOCKED:" + ",".join(pin_issues))
    base = phase1.build(cat, idx, root_state, pointers)
    workspace_defs = {x["git_dir"]: x for x in cat["workspaces"]}
    nodes = []
    edges = []
    for family in cat["families"]:
        nodes.append({"id": family["id"], "type": "CONTENT_FAMILY",
                      "name": family["name"]})
    for workspace in cat["workspaces"]:
        nodes.append({"id": workspace["id"], "type": "GIT_WORKSPACE",
                      "path": workspace["git_dir"],
                      "family_id": workspace["parent_family_id"]})
        edges.append({"from": workspace["id"], "to": workspace["parent_family_id"],
                      "kind": "WORKSPACE_OWNERSHIP_EXPLICIT"})
    for root in cat["root_workstreams"]:
        rid = "root:" + root["key"]
        nodes.append({"id": rid, "type": "ROOT_SUMMARY_KEY", "name": root["key"]})
        edges.append({"from": rid, "to": root["parent_family_id"],
                      "kind": "ROOT_SUMMARY_MAPPING_NOT_CURRENTNESS"})
    policies = reg["policy_bindings"]
    for key, binding in sorted(policies.items()):
        pid = "policy:" + key
        nodes.append({"id": pid, "type": "PINNED_POLICY", "path": binding["path"],
                      "scope": binding["scope"], "git_sha": binding["blob_sha"]})
        for workspace in cat["workspaces"]:
            applicability = classify_scope(binding, workspace)
            if applicability:
                edges.append({"from": pid, "to": workspace["id"],
                              "kind": "POTENTIAL_POLICY_DEPENDENCY_NOT_NATIVE_QA",
                              "applicability": applicability})
    evidence_rows = []
    for ws in base["workspaces"]:
        directory = ws["git_dir"]
        selected = ws["display_pointer"]
        datum = pointers.get(selected) if selected else None
        proof = scan_evidence(directory, datum, idx, selected)
        evidence_rows.append({"workspace_id": ws["id"], "directory": directory,
                              "parent_family_id": ws["parent_family_id"],
                              "metadata_authority": ws["authority"],
                              **proof})
    impact = []
    known_paths = {v["path"]: k for k, v in policies.items()}
    for path in sorted(set(changed_paths or [])):
        if not safe_relative(path):
            impact.append({"changed_path": path, "classification": "UNSAFE_PATH_HOLD",
                           "possibly_affected_workspace_ids": []})
            continue
        affected = []
        why = "OUTSIDE_REGISTERED_GRAPH__MANUAL_REVIEW"
        if path in known_paths:
            key = known_paths[path]
            why = "PINNED_POLICY_VERSION_CHANGED__REPIN_BEFORE_ACCEPTANCE"
            affected = [w["id"] for w in cat["workspaces"]
                        if classify_scope(policies[key], w) is not None]
        elif path.startswith("Workspaces/") and len(path.split("/")) >= 3:
            d = "/".join(path.split("/")[:2])
            if d in workspace_defs:
                why = "DIRECT_WORKSPACE_INPUT_CHANGED__VERIFY_OWN_RECEIPTS"
                affected = [workspace_defs[d]["id"]]
            else:
                why = "UNREGISTERED_WORKSPACE_HOLD"
        elif path in (CATALOG, REGISTRY, STATE):
            why = "GLOBAL_ROUTING_OR_IDENTITY_CHANGE__ALL_ADOPTION_SCOPES_REVIEW"
            affected = sorted(w["id"] for w in cat["workspaces"])
        impact.append({"changed_path": path, "classification": why,
                       "possibly_affected_workspace_ids": sorted(affected),
                       "impact_is_prospective_only": True,
                       "locked_sources_reopened": False})
    return {
        "schema": SCHEMA,
        "status": "SCOPED_READONLY_DEPENDENCY_GRAPH__NO_STAGE_CERTIFICATION",
        "source": {"catalog_index_sha": idx.get(CATALOG),
                   "registry_index_sha": idx.get(REGISTRY),
                   "root_state_index_sha": idx.get(STATE),
                   "exact_git_index": True,
                   "portable_artifact_readback": False,
                   "library_native_binary_readback": False},
        "counts": {"families": len(cat["families"]),
                   "workspaces": len(cat["workspaces"]),
                   "root_keys": len(cat["root_workstreams"]),
                   "policies": len(policies),
                   "graph_nodes": len(nodes), "graph_edges": len(edges),
                   "source_artifact_shas_independently_verified": 0,
                   "stage4_5_6_7_certificates_issued": 0},
        "nodes": nodes, "edges": edges,
        "workspace_evidence": evidence_rows,
        "catalog_navigation_issues": base["issues"],
        "prospective_impact": impact,
    }


def report_md(g):
    c = g["counts"]
    lines = [
        "# Phase 2: Project dependency and evidence graph",
        "",
        "**Only metadata and possible impact. This is NOT semantic QA, source-integrity certification or Stage6.**",
        "",
        f"Families: **{c['families']}** · Workspaces: **{c['workspaces']}** · Root keys: **{c['root_keys']}** · Pinned policies: **{c['policies']}**.",
        f"Graph: **{c['graph_nodes']}** nodes and **{c['graph_edges']}** typed relations.",
        "",
        "## Evidence by workspace", "",
        "| Workspace | Pointer | Claimed SHA? | Receipt references | Proven stage acceptance |",
        "|---|---|---|---:|---|",
    ]
    for e in g["workspace_evidence"]:
        lines.append("| {} | {} | {} | {} | {} |".format(
            e["directory"], e.get("pointer_path") or "—",
            "yes, not read back" if e.get("artifact_sha256_claim") else "no",
            len(e["receipt_refs"]), "NONE from this report"))
    lines += ["", "## Changed-path impact — prospective only", "",
              "| Changed path | Scope of review | Potential workspaces |",
              "|---|---|---:|"]
    for row in g["prospective_impact"]:
        lines.append("| {} | {} | {} |".format(row["changed_path"],
                     row["classification"], len(row["possibly_affected_workspace_ids"])))
    lines += ["", "## Limits", "",
              "Git-index receipt path presence does not validate receipt content, source hashes or linguistic quality.",
              "A potentially affected workspace is not automatically scheduled for destructive rewriting.",
              "An explicit newer user artifact overrides stale Git authority after validating its identity and integrity.",
              "Locked historical content, app UI/runtime and FSRS/SRS are never modified.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--changed-path", action="append", default=[])
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--github-summary", action="store_true")
    args = ap.parse_args()
    try:
        idx = index_blobs()
        cat, reg, state = (source_json(CATALOG, idx), source_json(REGISTRY, idx),
                           source_json(STATE, idx))
        if not all(isinstance(obj, dict) for obj in (cat, reg, state)):
            raise ValueError("MISSING_OR_UNPARSEABLE_CORE_GIT_INDEX_DOCUMENT")
        pointers = {}
        for d in phase1.tracked_dirs(idx):
            for name in ("LATEST.json", "CHECKPOINT.json"):
                path = d + "/" + name
                if path in idx:
                    pointers[path] = source_json(path, idx)
        g = build_graph(cat, reg, idx, state, pointers, args.changed_path)
        print(json.dumps({"status": g["status"], "counts": g["counts"],
                          "navigation_issue_count": len(g["catalog_navigation_issues"]),
                          "changed_path_count": len(g["prospective_impact"])}, indent=2))
        if args.output_dir:
            output = args.output_dir.resolve()
            if output == ROOT.resolve() or any(
                output == (ROOT / path).resolve()
                or (ROOT / path).resolve() in output.parents
                for path in ("Workspaces", "Prompt", "Data", "01-App", "06-Content")):
                raise ValueError("UNSAFE_OUTPUT_LOCATION")
            output.mkdir(parents=True, exist_ok=True)
            (output / "DEPENDENCY-EVIDENCE.json").write_text(
                json.dumps(g, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (output / "DEPENDENCY-EVIDENCE.md").write_text(report_md(g),
                                                            encoding="utf-8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
                f.write(report_md(g))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc),
                          "stage_certification": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
