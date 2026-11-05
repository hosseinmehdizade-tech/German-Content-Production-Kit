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
ANCHOR_KIND = "SOURCE_ANCHORED_HISTORICAL__INTERMEDIATE_LINEAGE_GAP"
ANCHOR_HISTORICAL = "PINNED_HISTORICAL_SOURCE_ANCHOR__WIP73_TO_WIP91_GAP__NOT_STAGE_PASS"


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



def validate_source_anchor(record, expected, idx, fetch_json):
    """Admit a dated real-byte source anchor separately from full packaged-source evidence.

    The WIP92 compact ZIP has no embedded original PDF and the intermediate
    WIP73..WIP91 edit chain was not replayed. Git verifies pinned *reports*
    rather than repeating real PDF/Library ZIP readback.
    """
    require(record.get("evidence_kind") == ANCHOR_KIND, "INVALID_SOURCE_ANCHOR_KIND")
    require(record.get("target_type") == "GIT_WORKSPACE"
            and record.get("target_id") == "workspace:aber-hallo-listen-tabellen"
            and expected["git_dir"] == "Workspaces/aber-hallo-listen-tabellen",
            "SOURCE_ANCHOR_WRONG_OWNER")
    documents = {}
    for key, sha_key in (("receipt_path", "receipt_git_blob_sha"),
                         ("profile_path", "profile_git_blob_sha"),
                         ("phase4_receipt_path", "phase4_receipt_git_blob_sha")):
        path, pin = record.get(key), record.get(sha_key)
        require(graph.safe_relative(path), "UNSAFE_SOURCE_ANCHOR_PATH:" + key)
        require(isinstance(pin, str) and re.fullmatch("[0-9a-f]{40}", pin),
                "SOURCE_ANCHOR_INVALID_PIN:" + key)
        require(idx.get(path) == pin, "SOURCE_ANCHOR_GIT_PIN_DRIFT:" + key)
        documents[key] = fetch_json(path)
        require(isinstance(documents[key], dict),
                "SOURCE_ANCHOR_MISSING_DOCUMENT:" + key)
    receipt, profile, phase4 = (documents["receipt_path"],
                                documents["profile_path"],
                                documents["phase4_receipt_path"])
    require(profile.get("schema") == "gcpk-source-anchor-historical-profile@1.0.0"
            and receipt.get("schema") == "gcpk-control-center-phase5-source-anchor-checkpoint@1.0.0"
            and phase4.get("schema") == "gcpk-control-center-phase4-aber-hallo-source-archive-readback@1.0.0",
            "SOURCE_ANCHOR_SCHEMA_MISMATCH")
    require(receipt.get("status") ==
            "PASS_SCOPED_REAL_EMBEDDED_SOURCES_AND_STABLE_PROVENANCE__NOT_FULL_LINEAGE_OR_STAGE_PASS"
            and phase4.get("status") ==
            "PASS_EXACT_SOURCE_HASHES_AND_COMPACT_ARCHIVE_INTEGRITY__NOT_EMBEDDED_SOURCE_ATTESTATION"
            and profile.get("scope") ==
            "PINNED_HISTORICAL_SOURCE_ANCHOR_WITH_INTERMEDIATE_LINEAGE_GAP__NO_STAGE_CERTIFICATION",
            "SOURCE_ANCHOR_SCOPE_NOT_PINNED")
    require(profile.get("target_id") == record["target_id"] == receipt.get("target_id") ==
            phase4.get("target_id") and
            profile.get("parent_family_id") == record["parent_family_id"] ==
            receipt.get("parent_family_id") == phase4.get("parent_family_id"),
            "SOURCE_ANCHOR_IDENTITY_MISMATCH")
    require(profile.get("phase4_receipt_path") == record["phase4_receipt_path"]
            and profile.get("phase4_receipt_git_blob_sha") == record["phase4_receipt_git_blob_sha"]
            and profile.get("phase5_receipt_path") == record["receipt_path"]
            and profile.get("phase5_receipt_git_blob_sha") == record["receipt_git_blob_sha"],
            "SOURCE_ANCHOR_CROSS_RECEIPT_PIN_MISMATCH")
    require(profile.get("phase5_internal_phase4_pointer") ==
            "KNOWN_STALE_NONEXISTENT_REFERENCE__PHASE4_RECEIPT_RESOLVED_SEPARATELY_BY_PIN"
            and receipt.get("git_authority", {}).get("phase4_receipt_path") !=
            record["phase4_receipt_path"],
            "SOURCE_ANCHOR_STALE_PHASE4_ALIAS_NOT_ISOLATED")

    source_hashes = record.get("source_sha256s")
    sources = receipt.get("historical_source_pdf_bytes", {})
    source_list = phase4.get("sources", [])
    require(isinstance(source_hashes, dict) and
            set(source_hashes) == {"a1_a2", "b1_c2"} and
            isinstance(source_list, list) and len(source_list) == 2,
            "SOURCE_ANCHOR_WRONG_SOURCE_UNIVERSE")
    for key, role, ix in (("a1_a2", "A1-A2", 0), ("b1_c2", "B1-C2", 1)):
        actual_hash = source_hashes[key]
        require(isinstance(actual_hash, str) and
                re.fullmatch("[0-9a-f]{64}", actual_hash) and
                actual_hash == profile.get("source_sha256s", {}).get(key) ==
                sources.get(key, {}).get("sha256") == source_list[ix].get("sha256")
                and source_list[ix].get("role") == role
                and sources[key].get("bytes") == profile.get("source_sizes", {}).get(key) ==
                source_list[ix].get("bytes")
                and sources[key].get("same_actual_bytes_in_recovery_base_and_wip72") is True,
                "SOURCE_ANCHOR_SOURCE_MISMATCH:" + key)

    archives = receipt.get("verified_archive_bytes", {})
    for key, profile_key, record_key in (
        ("recovery_wip77", "recovery_zip_sha256", "recovery_zip_sha256"),
        ("embedded_immutable_wip72", "embedded_wip72_sha256", "immutable_wip72_sha256"),
        ("current_at_preflight_wip92", "artifact_sha256", "artifact_sha256")):
        observed = archives.get(key, {}).get("sha256")
        require(observed == profile.get(profile_key) == record.get(record_key) and
                isinstance(observed, str) and re.fullmatch("[0-9a-f]{64}", observed),
                "SOURCE_ANCHOR_ARCHIVE_SHA_MISMATCH:" + key)
    require(archives.get("embedded_base_v336", {}).get("sha256") ==
            profile.get("embedded_base_sha256"), "SOURCE_ANCHOR_BASE_SHA_MISMATCH")
    require(receipt.get("payload_crosschecks", {}).get("wip92_canonical_sha256") ==
            record.get("canonical_sha256") == profile.get("canonical_sha256") ==
            phase4.get("payload", {}).get("canonical_sha256") and
            receipt.get("payload_crosschecks", {}).get("wip92_tsv_sha256") ==
            record.get("content_sha256") == profile.get("content_sha256") ==
            phase4.get("payload", {}).get("tsv_sha256"),
            "SOURCE_ANCHOR_CONTENT_SHA_MISMATCH")
    require(phase4.get("artifact", {}).get("sha256") == record["artifact_sha256"]
            and phase4.get("artifact", {}).get("zip_crc") == "PASS"
            and phase4.get("artifact", {}).get("sha256sums_verified") ==
            "102_OF_102_EXACT_COVERAGE"
            and archives.get("current_at_preflight_wip92", {}).get("sha256sums") ==
            "102_OF_102" and archives.get("embedded_immutable_wip72", {}).get("sha256sums") ==
            "483_OF_483" and archives.get("recovery_wip77", {}).get("content_hash_manifest") ==
            "9_OF_9_EXACT",
            "SOURCE_ANCHOR_PACKAGING_EVIDENCE_MISMATCH")
    require(receipt.get("payload_crosschecks", {}).get(
            "canonical_788_provenance_sources_arrays_exactly_identical_wip72_wip92") is True
            and receipt.get("payload_crosschecks", {}).get(
            "canonical_788_ids_types_headwords_order_identical_wip72_wip92") is True
            and receipt.get("payload_crosschecks", {}).get(
            "lexical_tsv_787_ids_same_order_wip72_wip92") is True
            and receipt.get("reproducible_report", {}).get("sha256") ==
            profile.get("phase5_library_zip_sha256")
            and receipt.get("reproducible_report", {}).get("library_file_id") ==
            profile.get("phase5_library_file_id"),
            "SOURCE_ANCHOR_PROVENANCE_EVIDENCE_MISMATCH")

    limits = receipt.get("explicit_limits", {})
    require(limits.get("all_wip73_to_wip91_intermediate_artifact_bytes_replayed") is False
            and limits.get("all_transitive_edit_deltas_proven") is False
            and limits.get("original_pdf_to_card_semantic_fidelity_certified") is False
            and limits.get("linguistic_stage4") == "OPEN"
            and limits.get("stage5_final") == "NOT_RUN"
            and limits.get("native_stage6_browser_and_indexeddb") == "NOT_RUN"
            and limits.get("stage7_release") == "NOT_RUN"
            and limits.get("current_or_final_certificates") == 0
            and limits.get("added_to_control_center_full_evidence_registry") is False
            and receipt.get("payload_crosschecks", {}).get(
            "wip92_compact_zip_embeds_original_pdf_bytes") is False
            and phase4.get("evidence_limits", {}).get("source_pdfs_embedded_in_compact_zip") is False
            and phase4.get("evidence_limits", {}).get("semantic_source_to_card_fidelity") ==
            "NOT_ATTESTED"
            and record.get("continuous_lineage_verified") is False
            and record.get("source_to_card_semantics_certified") is False
            and record.get("stage4_semantic_approval") == "OPEN_NOT_ACCEPTED"
            and record.get("stage5_6_7_status") == "NOT_RUN"
            and profile.get("not_current_or_final") is True
            and profile.get("raw_sources_embedded_in_wip92") is False
            and all(profile.get(k) == v for k, v in (
                ("stage4", "OPEN"), ("stage5", "NOT_RUN"),
                ("stage6", "NOT_RUN"), ("stage7", "NOT_RUN"))),
            "SOURCE_ANCHOR_FALSE_STAGE_OR_LINEAGE_PROMOTION")
    expected_latest = expected["git_dir"] + "/LATEST.json"
    require(record.get("latest_path") == expected_latest ==
            profile.get("latest_path") == receipt.get("git_authority", {}).get("latest_path") ==
            phase4.get("github_at_preflight", {}).get("latest_path")
            and record.get("latest_git_blob_at_readback") ==
            profile.get("latest_git_blob_at_readback") ==
            receipt.get("git_authority", {}).get("latest_blob_at_preflight") ==
            phase4.get("github_at_preflight", {}).get("latest_git_blob"),
            "SOURCE_ANCHOR_LATEST_PREIMAGE_MISMATCH")
    latest_relation = "GIT_POINTER_CHANGED_OR_MISSING__REVERIFY_BEFORE_RESUME"
    if idx.get(expected_latest) == record["latest_git_blob_at_readback"]:
        latest = fetch_json(expected_latest)
        require(isinstance(latest, dict) and
                latest.get("authority", {}).get("current_portable", {}).get("sha256") ==
                record["artifact_sha256"] and
                latest.get("authority", {}).get("current_portable", {}).get("stage4") ==
                "OPEN",
                "SOURCE_ANCHOR_LATEST_ARTIFACT_DISAGREES_WITH_RECEIPT")
        latest_relation = "GIT_POINTER_UNCHANGED_SINCE_READBACK__STILL_NOT_CERTIFIED_CURRENT"
    return {
        "evidence_id": record["evidence_id"],
        "target_id": record["target_id"],
        "parent_family_id": record["parent_family_id"],
        "historical_evidence_status": ANCHOR_HISTORICAL,
        "readback_receipt_path": record["receipt_path"],
        "readback_receipt_git_blob_sha": record["receipt_git_blob_sha"],
        "source_sha256_historically_attested": dict(source_hashes),
        "artifact_sha256_historically_attested": record["artifact_sha256"],
        "immutable_full_source_parent_sha256": record["immutable_wip72_sha256"],
        "manifest_entries_historically_attested": "SOURCE_CHAIN_PARTIAL_V1",
        "stage4_risk_gate": "OPEN__NOT_STAGE4_PASS",
        "stage5_final": "NOT_ATTESTED_BY_OVERLAY",
        "stage6_browser": "NOT_ATTESTED_BY_OVERLAY",
        "stage7_release": "NOT_ATTESTED_BY_OVERLAY",
        "git_pointer_relation": latest_relation,
        "intermediate_versions_replayed": False,
        "source_to_card_semantics_certified": False,
        "current_user_source_automatically_resolved": False,
        "source_bytes_freshly_read_in_github_runner": False,
    }


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
    if record.get("evidence_kind") == ANCHOR_KIND:
        return validate_source_anchor(record, expected, idx, fetch_json)
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
                           "evidence_status": r["historical_evidence_status"] if r else NONE,
                           "evidence_id": r["evidence_id"] if r else None,
                           "current_or_stage_verified": False})
    roots = []
    for x in catalog["root_workstreams"]:
        identifier = "root:" + x["key"]
        r = next((r for r in rows if r["target_id"] == identifier), None)
        roots.append({"target_id": identifier, "family_id": x["parent_family_id"],
                      "evidence_status": r["historical_evidence_status"] if r else NONE,
                      "evidence_id": r["evidence_id"] if r else None,
                      "current_or_stage_verified": False})
    families = []
    for x in catalog["families"]:
        attached = [r["evidence_id"] for r in rows if r["parent_family_id"] == x["id"]]
        families.append({"family_id": x["id"], "name": x["name"],
                         "historical_real_byte_receipt_ids": attached,
                         "source_anchor_only_receipt_ids": [r["evidence_id"] for r in rows
                             if r["parent_family_id"] == x["id"] and
                             r["historical_evidence_status"] == ANCHOR_HISTORICAL],
                         "family_current_certified": False,
                         "family_stage4_5_6_7_certified": False})
    return {
        "schema": SCHEMA,
        "status": "PINNED_TWO_FULL_HISTORICAL_BYTE_RECEIPTS_PLUS_ONE_SOURCE_ANCHOR__NOT_CURRENT",
        "counts": {
            "catalog_families": len(families),
            "catalog_git_workspaces": len(workspaces),
            "catalog_root_workstreams": len(roots),
            "historical_byte_receipts_git_workspaces": sum(x["evidence_status"] == BYTES_HISTORICAL for x in workspaces),
            "source_anchored_historical_git_workspaces": sum(
                x["evidence_status"] == ANCHOR_HISTORICAL for x in workspaces),
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
            "Aber Hallo WIP72-WIP92 provenance anchor is not a verified continuous WIP73-WIP91 edit chain",
            "A root-workstream without Git workspace must not create a fictitious Git pointer",
            "No Stage5, browser Stage6 or final release inferred from byte-level integrity",
        ],
    }


def markdown(result):
    c = result["counts"]
    lines = ["# Project Control Center — Scoped Attested Evidence Overlay", "",
             "**Historical exact-byte readback receipts, NOT CURRENT and NOT full Stage acceptance.**", "",
             f"Families: {c['catalog_families']} | Git workspaces: {c['catalog_git_workspaces']} | Root keys: {c['catalog_root_workstreams']}.",
             f"Full historical Git workspace receipts: {c['historical_byte_receipts_git_workspaces']}; root-only: {c['historical_byte_receipts_root_workstreams']}; source-anchor only: {c['source_anchored_historical_git_workspaces']}.",
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
            # GitHub Actions writes only this generated ephemeral directory in the checkout.
            # Arbitrary worktree locations (including all sources) remain forbidden.
            allow_ci = out == (ROOT / "attested-evidence-output").resolve()
            require(allow_ci or (out != ROOT.resolve() and ROOT.resolve() not in out.parents),
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
