#!/usr/bin/env python3
"""OP-02 proposed stable typed checkpoint contract; NEVER a release/writer gate.

A producer would explicitly emit gcpk-content-milestone-typed@1. This function
does NOT translate unknown legacy schemas automatically, does NOT verify raw ZIP
or PDF bytes, and does NOT authenticate an issuer. A trusted, separately pinned
workstream profile is mandatory; no profile is inferred from receipt claims.
"""
from __future__ import annotations

import json
import re

SCHEMA = "gcpk-content-milestone-typed@1"
PROFILE_SCHEMA = "gcpk-op02-typed-receipt-profile@1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
WIP = re.compile(r"^WIP([1-9][0-9]*)_")
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]{4}$")
TOP = {"schema", "workstream", "milestone", "receipt_path", "status",
       "portable", "parent_sha256", "source_sha256", "counts", "zip_members",
       "gates"}
PORTABLE = {"filename", "sha256", "size_bytes", "library_file_id",
            "library_path", "canonical_sha256", "import_sha256"}
COUNTS = {"learning_units", "import_cards", "attested", "holds",
          "governed_patterns", "new_attested", "changed_cards",
          "changed_card_ids"}
GATES = {"stage4", "stage5_7", "import_parity"}

def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out

def parse_strict(payload: bytes):
    return json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("NONFINITE_JSON")))

def sha(value):
    return isinstance(value, str) and bool(HEX64.fullmatch(value)) and value != "0" * 64

def ints(*values):
    return all(type(v) is int and v >= 0 for v in values)

def evaluate(latest, receipt, sources, profile):
    """Read-only deterministic metadata test. True content/release PASS is impossible."""
    errors = []
    result = {
        "schema": "gcpk-op02-typed-receipt-diagnostic@1",
        "status": "BLOCKED_NONACTIVE_METADATA",
        "errors": errors,
        "scope": "SYNTHETIC_OR_EXPLICITLY_TYPED_TRACKED_METADATA_ONLY",
        "trusted_issuer": False,
        "source_pdf_bytes_verified": False,
        "zip_bytes_verified": False,
        "stage4_semantic_pass": False,
        "stage5_allowed": False,
        "stage6_accepted": False,
        "stage7_final": False,
        "writer_granted": False,
        "performed_writes": False,
    }
    if not all(isinstance(x, dict) for x in (latest, receipt, sources, profile)):
        errors.append("DOCUMENT_NOT_OBJECT")
        return result
    if profile.get("schema") != PROFILE_SCHEMA or not isinstance(profile.get("workstream"), str):
        errors.append("TRUSTED_PROFILE_IDENTITY_INVALID")
    workstream = profile.get("workstream")
    expected_source_ids = profile.get("source_ids")
    expected_source_hashes = profile.get("source_sha256")
    if not (isinstance(expected_source_ids, list) and
            isinstance(expected_source_hashes, list) and
            len(expected_source_ids) == len(expected_source_hashes) and
            len(expected_source_ids) > 0 and
            all(isinstance(x, str) and x for x in expected_source_ids) and
            len(set(expected_source_ids)) == len(expected_source_ids) and
            all(sha(x) for x in expected_source_hashes)):
        errors.append("TRUSTED_PROFILE_SOURCE_PINS_INVALID")

    if (receipt.get("schema") != SCHEMA or
            set(receipt) != TOP or
            receipt.get("workstream") != workstream):
        errors.append("TYPED_SCHEMA_OR_FIELDS_INVALID")
    if latest.get("schema") != "gcpk-workstream-latest@1.0.0" or latest.get("workstream") != workstream:
        errors.append("LATEST_WORKSTREAM_MISMATCH")
    if sources.get("schema") != profile.get("source_manifest_schema") or sources.get("dataset") != workstream:
        errors.append("SOURCE_MANIFEST_IDENTITY_MISMATCH")

    source_set = sources.get("source_set")
    if (not isinstance(source_set, list) or
            not all(isinstance(x, dict) for x in source_set) or
            [x.get("source_id") for x in source_set] != expected_source_ids or
            [x.get("sha256") for x in source_set] != expected_source_hashes or
            any(x.get("source_type") != "pdf" for x in source_set)):
        errors.append("SOURCE_MANIFEST_PROFILE_PIN_DRIFT")
    if (not isinstance(receipt.get("source_sha256"), list) or
            receipt["source_sha256"] != expected_source_hashes):
        errors.append("RECEIPT_SOURCE_ORDER_OR_HASH_DRIFT")

    milestone = latest.get("latest_milestone")
    match = WIP.match(milestone) if isinstance(milestone, str) else None
    version = int(match.group(1)) if match else None
    path = latest.get("latest_receipt_path")
    if (version is None or receipt.get("milestone") != milestone or
            not isinstance(path, str) or
            path != receipt.get("receipt_path") or
            not path.startswith("Workspaces/" + str(workstream) + "/") or
            ".." in path.split("/") or
            not path.endswith(".json") or
            f"WIP{version}" not in path):
        errors.append("MILESTONE_PATH_OR_VERSION_DRIFT")
    if not isinstance(latest.get("latest_receipt_commit_sha"), str) or not HEX40.fullmatch(latest["latest_receipt_commit_sha"]):
        errors.append("LATEST_COMMIT_POINTER_FORMAT_INVALID")
    if receipt.get("status") != "PASS_SCOPED_STAGE4_OPEN":
        errors.append("RECEIPT_SCOPED_STATUS_INVALID")

    portable = receipt.get("portable")
    live = latest.get("authority")
    live_portable = live.get("current_portable") if isinstance(live, dict) else None
    package = latest.get("complete_working_content_package")
    if (not isinstance(portable, dict) or set(portable) != PORTABLE or
            not isinstance(live_portable, dict) or not isinstance(package, dict)):
        errors.append("PORTABLE_PACKAGE_SCHEMA_INVALID")
    else:
        for field in PORTABLE:
            if not portable.get(field) or portable.get(field) != live_portable.get(field):
                errors.append("RECEIPT_PORTABLE_DRIFT:" + field)
        for left, right in (("filename", "name"), ("sha256", "sha256"),
                            ("size_bytes", "bytes"), ("library_file_id", "library_file_id"),
                            ("library_path", "library_path")):
            if portable.get(left) != package.get(right):
                errors.append("CURRENT_PACKAGE_ROLE_DRIFT:" + left)
        if (not all(sha(portable.get(k)) for k in
                    ("sha256", "canonical_sha256", "import_sha256")) or
                type(portable.get("size_bytes")) is not int or portable["size_bytes"] <= 0 or
                not isinstance(portable.get("filename"), str) or
                version is None or f"WIP{version}-" not in portable["filename"] or
                not isinstance(portable.get("library_path"), str) or
                not portable["library_path"].endswith("/" + portable["filename"])):
            errors.append("PORTABLE_IDENTITY_INVALID")

    previous = latest.get(f"previous_wip{version}_source_current") if version is not None else None
    previous_portable = previous.get("portable") if isinstance(previous, dict) else None
    parent = receipt.get("parent_sha256")
    if (not sha(parent) or not isinstance(previous_portable, dict) or
            previous_portable.get("sha256") != parent or
            not isinstance(package, dict) or package.get("parent_sha256") != parent or
            not isinstance(live_portable, dict) or parent == live_portable.get("sha256")):
        errors.append("PARENT_LINEAGE_INVALID")

    counts = receipt.get("counts")
    progress = latest.get("progress")
    if not isinstance(counts, dict) or set(counts) != COUNTS:
        errors.append("COUNTS_SCHEMA_INVALID")
    elif not isinstance(progress, dict):
        errors.append("LATEST_PROGRESS_INVALID")
    else:
        names = ("learning_units", "import_cards", "attested", "holds",
                 "governed_patterns", "new_attested", "changed_cards")
        if not ints(*(counts.get(x) for x in names)):
            errors.append("COUNTS_NUMERIC_INVALID")
        else:
            if (counts["learning_units"] != profile.get("learning_units") or
                    counts["import_cards"] != profile.get("import_cards") or
                    counts["governed_patterns"] != profile.get("governed_patterns") or
                    counts["attested"] + counts["holds"] != counts["governed_patterns"] or
                    counts["new_attested"] > counts["attested"] or
                    counts["changed_cards"] > counts["import_cards"]):
                errors.append("COUNTS_PROFILE_OR_CONSERVATION_DRIFT")
            if (counts["attested"] != progress.get("rektion_independent_external_attested_cumulative") or
                    counts["holds"] != progress.get("rektion_external_holds_remaining")):
                errors.append("COUNTS_LATEST_PROGRESS_DRIFT")
        ids = counts.get("changed_card_ids")
        if (not isinstance(ids, list) or len(ids) != counts.get("changed_cards") or
                not all(isinstance(v, str) and ID.fullmatch(v) for v in ids) or
                len(set(str(v) for v in ids)) != len(ids) or
                any(not v.startswith(str(profile.get("card_id_prefix")) + "-") for v in ids)):
            errors.append("CHANGED_CARD_IDS_INVALID")

    if (type(receipt.get("zip_members")) is not int or receipt["zip_members"] <= 0 or
            not isinstance(package, dict) or
            receipt.get("zip_members") != package.get("member_count")):
        errors.append("ZIP_MEMBER_COUNT_DRIFT")
    gates = receipt.get("gates")
    if (not isinstance(gates, dict) or set(gates) != GATES or
            gates.get("stage4") != "OPEN" or
            gates.get("stage5_7") != "NOT_RUN" or
            gates.get("import_parity") != "PASS_SCOPED_CANONICAL_IMPORT_CLAIM" or
            not isinstance(live_portable, dict) or
            live_portable.get("stage4") != "OPEN" or
            not isinstance(package, dict) or
            package.get("stage4") != "OPEN" or
            package.get("stage5_6_7") != "NOT_RUN" or
            not isinstance(progress, dict) or
            progress.get("pending_independent_expert_stage4") is not True or
            progress.get("independent_expert_unreviewed_units") != profile.get("learning_units")):
        errors.append("STAGE_BOUNDARY_OR_SCOPED_PARITY_CLAIM_INVALID")

    result["errors"] = sorted(set(errors))
    if not errors:
        result["status"] = "PASS_NONACTIVE_TYPED_METADATA_ONLY_NOT_RELEASE"
    return result
