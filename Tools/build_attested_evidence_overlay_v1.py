#!/usr/bin/env python3
"""Read-only project evidence overlay for exact historical source-package readback receipts.

Never treats a Git receipt as fresh PDF/ZIP access, nor Stage4/5/6/7 acceptance.
Identity mapping follows the Phase1 catalog: Git workspaces and root keys differ.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "Optimization-Program/Control-Center/EVIDENCE-REGISTRY-v1.json"
PHASE2 = ROOT / "Tools/build_project_dependency_evidence_v1.py"
spec = importlib.util.spec_from_file_location("phase2_graph_for_evidence", PHASE2)
graph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph)

SCHEMA = "gcpk-attested-evidence-overlay@1.0.0"
BYTES_HISTORICAL = "PINNED_HISTORICAL_EXTERNAL_READBACK_RECEIPT__NOT_FRESH_GITHUB_BINARY_QA"
NONE = "NO_REAL_BYTE_ATTESTATION_REGISTERED"


def require(ok, code):
    if not ok:
        raise ValueError(code)


def extract_receipt(rec):
    schema = rec.get("schema")
    if schema == "gcpk-phase3-vmp-r7-real-source-package-byte-attestation@1.0.0":
        source = rec.get("readback", {})
        check = rec.get("official_stage4_reexecution", {})
        require(rec.get("status") == "PASS_REAL_EXACT_SOURCE_AND_ARCHIVE_BYTES_PLUS_PINNED_RISK_STAGE4_GATE__NOT_FINAL",
                "R7_RECEIPT_NOT_SCOPED_PASS")
        require(source.get("embedded_original_matches_user_pdf_byte_for_byte") is True
                and source.get("zip_crc") == "PASS"
                and source.get("sha256sum_manifest_entries") ==
                     "24_OF_24_HASHED_MEMBERS_VERIFIED_AND_EXACT_FULL_COVERAGE",
                "R7_RECEIPT_BYTE_INTEGRITY_FIELDS_INVALID")
        require(check.get("return_code") == 0 and check.get("stdout_status") == "PASS_RISK_BASED_STAGE4"
                and check.get("blockers") == [], "R7_STAGE4_RISK_RESULT_NOT_PROVEN")
        boundary = rec.get("acceptance_boundary", {})
        require(boundary.get("official_stage5_final") == "NOT_RUN"
                and boundary.get("real_stage6_browser_origin_and_indexeddb") == "NOT_RUN"
                and boundary.get("stage7_final_release") == "NOT_RUN", "R7_FALSE_RELEASE_PROMOTION")
        return {
            "source_sha256": source.get("mounted_user_pdf_sha256"),
            "artifact_sha256": source.get("actual_library_zip_sha256"),
            "content_sha256": source.get("content_tsv_sha256"),
            "zip_members": source.get("zip_members_exact"),
            "manifest_entries": 24,
            "stage4": "RISK_GATE_REEXECUTED_PASS__NOT_PERFECT_SEMANTIC_QA",
        }
    if schema == "gcpk-phase3-nvv-r61-real-byte-receipt@1.0.0":
        require(rec.get("status") ==
                "PASS_SCOPED_REAL_SOURCE_AND_PACKAGE_BYTE_INTEGRITY__NOT_STAGE_ACCEPTANCE",
                "NVV_RECEIPT_NOT_SCOPED_PASS")
        require(rec.get("embedded_source_byte_identical_to_uploaded_source") is True
                and rec.get("manifest_entries_sha256_matches") == "54_OF_54_PASS"
                and rec.get("manifest_coverage") == "EXACT_ALL_NON_MANIFEST_MEMBERS"
                and rec.get("zip_crc") == "PASS", "NVV_RECEIPT_BYTE_INTEGRITY_FIELDS_INVALID")
        require(rec.get("official_stage4_gate_reexecuted") is False
                and rec.get("official_stage5") == "NOT_ATTESTED"
                and rec.get("native_stage6") == "NOT_ATTESTED"
                and rec.get("stage7_release") == "NOT_ATTESTED",
                "NVV_FALSE_STAGE_PROMOTION")
        return {
            "source_sha256": rec.get("source_sha256"),
            "artifact_sha256": rec.get("archive_sha256"),
            "content_sha256": rec.get("content_sha256"),
            "zip_members": rec.get("zip_members"),
            "manifest_entries": rec.get("manifest_entries"),
            "stage4": "NOT_ATTESTED_IN_THIS_CHECK",
        }
    raise ValueError("UNRECOGNIZED_HISTORICAL_RECEIPT_SCHEMA")


def validate_one(record, catalog, idx, fetch_json):
    require(isinstance(record, dict), "RECORD_NOT_OBJECT")
    ident = record.get("evidence_id", "")
    require(isinstance(ident, str) and re.fullmatch("[a-z0-9][a-z0-9-]{5,100}", ident),
            "EVIDENCE_ID_INVALID")
    workspaces = {x["id"]: x for x in catalog["workspaces"]}
    roots = {"root:" + x["key"]: x for x in catalog["root_workstreams"]}
    target = record.get("target_id")
    ttype = record.get("target_type")
    if ttype == "GIT_WORKSPACE":
        expected = workspaces.get(target)
        require(expected is not None, "UNREGISTERED_GIT_WORKSPACE_TARGET")
    elif ttype == "ROOT_WORKSTREAM":
        expected = roots.get(target)
        require(expected is not None, "UNREGISTERED_ROOT_WORKSTREAM_TARGET")
    else:
        raise ValueError("INVALID_TARGET_TYPE")
    require(expected["parent_family_id"] == record.get("parent_family_id"),
            "TARGET_FAMILY_MISMATCH")
    loaded = {}
    for key, pin_key in (("receipt_path", "receipt_git_blob_sha"),
                         ("profile_path", "profile_git_blob_sha")):
        path, pin = record.get(key), record.get(pin_key)
        require(graph.safe_relative(path), "UNSAFE_EVIDENCE_PATH")
        require(isinstance(pin, str) and re.fullmatch("[a-f0-9]{40}", pin),
                "INVALID_EVIDENCE_GIT_PIN")
        require(idx.get(path) == pin, "EVIDENCE_GIT_PIN_DRIFT:" + key)
        data = fetch_json(path)
        require(isinstance(data, dict), "INVALID_PINNED_EVIDENCE_JSON:" + key)
        loaded[key] = data
    profile, receipt = loaded["profile_path"], loaded["receipt_path"]
    require(profile.get("schema") == "gcpk-scoped-byte-attestation-profile@1.0.0",
            "INVALID_SOURCE_ARTIFACT_PROFILE_SCHEMA")
    hashes = extract_receipt(receipt)
    for field in ("source_sha256", "artifact_sha256", "content_sha256"):
        value = record.get(field)
        require(isinstance(value, str) and re.fullmatch("[a-f0-9]{64}", value),
                "INVALID_SOURCE_ARTIFACT_SHA:" + field)
        require(value == profile.get(
            {"source_sha256": "original_source_sha256",
             "artifact_sha256": "artifact_sha256",
             "content_sha256": "content_sha256"}[field]), "PROFILE_SHA_MISMATCH:" + field)
        require(value == hashes[field], "RECEIPT_SHA_MISMATCH:" + field)
    require(record.get("manifest_entries_verified") == hashes["manifest_entries"],
            "MANIFEST_ENTRY_COUNT_MISMATCH")
    require(record.get("zip_members") == hashes["zip_members"], "ZIP_MEMBER_COUNT_MISMATCH")
    if ttype == "GIT_WORKSPACE":
        require(record.get("latest_path") == expected["git_dir"] + "/LATEST.json",
                "WRONG_WORKSPACE_LATEST")
        now = idx.get(record["latest_path"])
        require(isinstance(record.get("latest_git_blob_at_readback"), str),
                "MISSING_HISTORICAL_LATEST_PIN")
        currentness = ("GIT_POINTER_UNCHANGED_SINCE_READBACK__STILL_NOT_CERTIFIED_CURRENT"
                       if now == record["latest_git_blob_at_readback"]
                       else "GIT_POINTER_CHANGED_OR_MISSING__REVERIFY_BEFORE_RESUME")
        if now == record["latest_git_blob_at_readback"]:
            latest = fetch_json(record["latest_path"])
            require(isinstance(latest, dict) and latest.get("artifact", {}).get("sha256") ==
                    record["artifact_sha256"], "LATEST_ARTIFACT_DISAGREES_WITH_RECEIPT")
    else:
        require(record.get("latest_path") is None and record.get("latest_git_blob_at_readback") is None,
                "FABRICATED_ROOT_GIT_WORKSPACE_LATEST")
        currentness = "NO_NATIVE_GIT_LATEST__ROOT_SUMMARY_NOT_PORTABLE_CURRENT"
    return {
        "evidence_id": ident,
        "target_id": target,
        "parent_family_id": record["parent_family_id"],
        "historical_evidence_status": BYTES_HISTORICAL,
        "readback_receipt_path": record["receipt_path"],
        "readback_receipt_git_blob_sha": record["receipt_git_blob_sha"],
        "source_sha256_historically_attested": hashes["source_sha256"],
        "artifact_sha256_historically_attested": hashes["artifact_sha256"],
        "manifest_entries_historically_attested": hashes["manifest_entries"],
        "stage4_risk_gate": hashes["stage4"],
        "stage5_final": "NOT_ATTESTED_BY_OVERLAY",
        "stage6_browser": "NOT_ATTESTED_BY_OVERLAY",
        "stage7_release": "NOT_ATTESTED_BY_OVERLAY",
        "git_pointer_relation": currentness,
        "current_user_source_automatically_resolved": False,
        "source_bytes_freshly_read_in_github_runner": False,
    }


def build(reg, catalog, idx, fetch_json):
    require(reg.get("schema") == "gcpk-project-evidence-registry@1.0.0", "REGISTRY_SCHEMA")
    require(reg.get("role") ==
            "PINNED_HISTORICAL_INDEPENDENT_BYTE_READBACK_RECEIPTS__NOT_CURRENT_STATUS_OR_STAGE_ACCEPTANCE",
            "REGISTRY_WRONG_SCOPE")
    errors = graph.phase1.catalog_errors(catalog)
    require(not errors, "INVALID_IDENTITY_CATALOG:" + ",".join(errors))
    rows, seen_ids, seen_targets = [], set(), set()
    for record in reg.get("records", []):
        row = validate_one(record, catalog, idx, fetch_json)
        require(row["evidence_id"] not in seen_ids, "DUPLICATE_EVIDENCE_ID")
        require(row["target_id"] not in seen_targets, "MULTIPLE_RECEIPTS_FOR_SAME_TARGET_REQUIRES_REVIEW")
        seen_ids.add(row["evidence_id"])
        seen_targets.add(row["target_id"])
        rows.append(row)
    workspaces = []
    for x in catalog["workspaces"]:
        r = next((r for r in rows if r["target_id"] == x["id"]), None)
        workspaces.append({"target_id": x["id"], "family_id": x["parent_family_id"],
                           "evidence_status": BYTES_HISTORICAL if r else NONE,
                           "evidence_id": r["evidence_id"] if r else None,
                           "current_or_stage_verified": False})
    roots = []
    for x in catalog["root_workstreams"]:
        identifier = "root:" + x["key"]
        r = next((r for r in rows if r["target_id"] == identifier), None)
        roots.append({"target_id": identifier, "family_id": x["parent_family_id"],
                      "evidence_status": BYTES_HISTORICAL if r else NONE,
                      "evidence_id": r["evidence_id"] if r else None,
                      "current_or_stage_verified": False})
    families = []
    for x in catalog["families"]:
        attached = [r["evidence_id"] for r in rows if r["parent_family_id"] == x["id"]]
        families.append({"family_id": x["id"], "name": x["name"],
                         "historical_real_byte_receipt_ids": attached,
                         "family_current_certified": False,
                         "family_stage4_5_6_7_certified": False})
    return {
        "schema": SCHEMA,
        "status": "PINNED_TWO_HISTORICAL_BYTE_RECEIPTS__ALL_OTHER_TARGETS_UNATTESTED",
        "counts": {
            "catalog_families": len(families),
            "catalog_git_workspaces": len(workspaces),
            "catalog_root_workstreams": len(roots),
            "historical_byte_receipts_git_workspaces": sum(x["evidence_id"] is not None for x in workspaces),
            "historical_byte_receipts_root_workstreams": sum(x["evidence_id"] is not None for x in roots),
            "unattested_git_workspaces": sum(x["evidence_id"] is None for x in workspaces),
            "fresh_pdf_zip_bytes_rehashed_by_github_ci": 0,
            "current_or_final_stage_certificates": 0,
        },
        "evidence": rows, "workspace_evidence": workspaces,
        "root_workstream_evidence": roots, "families": families,
        "limits": [
            "Git-index pin verifies registered receipt unchanged, not the PDF/ZIP bytes again",
            "Historical R7 and R6.1 may be superseded by newer user-provided verified source",
            "A root-workstream without Git workspace must not create a fictitious Git pointer",
            "No Stage5, browser Stage6 or final release inferred from byte-level integrity",
        ],
    }


def markdown(result):
    c = result["counts"]
    lines = ["# Project Control Center — Scoped Attested Evidence Overlay", "",
             "**Historical exact-byte readback receipts, NOT CURRENT and NOT full Stage acceptance.**", "",
             f"Families: {c['catalog_families']} | Git workspaces: {c['catalog_git_workspaces']} | Root keys: {c['catalog_root_workstreams']}.",
             f"Git workspace historical byte receipts: {c['historical_byte_receipts_git_workspaces']}; root-only: {c['historical_byte_receipts_root_workstreams']}.",
             f"Git workspaces without such receipt: {c['unattested_git_workspaces']}.",
             "", "| Target | Evidence | Stage4 boundary | Latest relation |",
             "|---|---|---|---|"]
    for r in result["evidence"]:
        lines.append(f"| {r['target_id']} | {r['historical_evidence_status']} | {r['stage4_risk_gate']} | {r['git_pointer_relation']} |")
    lines += ["", "## Project families", "",
              "| Project | Historical byte receipts | CURRENT certified? |",
              "|---|---:|---|"]
    for fam in result["families"]:
        lines.append(f"| {fam['name']} | {len(fam['historical_real_byte_receipt_ids'])} | No |")
    lines += ["", "Receipts are pinned historical declarations from a separate independent real-file readback.",
              "GitHub CI cannot access the Library ZIP or mounted original PDF and does not rerun their hashes.",
              "No learner cards, source, LOCKED records, app UI or FSRS changed.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--github-summary", action="store_true")
    args = ap.parse_args()
    try:
        idx = graph.index_blobs()
        reg = graph.source_json(REGISTRY, idx)
        cat = graph.source_json(graph.CATALOG, idx)
        require(isinstance(reg, dict) and isinstance(cat, dict), "REGISTRY_OR_CATALOG_GIT_INDEX_MISSING")
        result = build(reg, cat, idx, lambda p: graph.source_json(p, idx))
        text = markdown(result)
        print(json.dumps({"status": result["status"], "counts": result["counts"]},
                         ensure_ascii=False, indent=2))
        if args.output_dir:
            out = args.output_dir.resolve()
            require(out != ROOT.resolve() and ROOT.resolve() not in out.parents,
                    "GIT_WORKTREE_OUTPUT_FORBIDDEN")
            out.mkdir(parents=True, exist_ok=True)
            (out / "ATTESTED-EVIDENCE.json").write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (out / "ATTESTED-EVIDENCE.md").write_text(text, encoding="utf-8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
                f.write(text)
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc),
                          "current_or_final_stage_acceptance": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
