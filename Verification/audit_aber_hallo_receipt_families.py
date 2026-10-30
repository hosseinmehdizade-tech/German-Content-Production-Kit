#!/usr/bin/env python3
"""OP-02: explicit historical/current Aber Hallo receipt family adapters.

Only SCOPED TRACKED METADATA comparisons; no source PDF, Library ZIP,
semantic Stage4, signed issuer, or release proof. Unknown schema blocks.
Every field mapping is deliberately registered here: no name-guessing.
"""
from __future__ import annotations

import re

SHA = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
VERSION = re.compile(r"^WIP([0-9]{2,4})_")
WORKSTREAM = "aber-hallo-listen-tabellen"
BASE = "Workspaces/aber-hallo-listen-tabellen"


# Immutable schema identity + exact version + provenance of fields
# used by the observed historical 58/59 and current 60 checkpoint formats.
SCHEMAS = {
    "gcpk-aber-hallo-wip58-direct-duden-checkpoint@1.0.0": {
        "version": 58, "artifact": "current",
        "parent": ("parent_wip57_sha256",),
        "counts": ("counts", "cumulative_attested", "external_holds",
                   "governed_patterns", None, "canonical_units", "import_cards"),
        "new": ("counts", "new_duden_attested"),
        "members": ("tests", "zip_members"),
        "source": ("tests", "source_PDFs", "IMMUTABLE_AND_SHA256_PASS"),
        "stage4": ("boundaries", "full_stage4_trilingual_semantic_source_adversarial", "OPEN_NOT_RUN"),
        "stages": (("boundaries", "stage5", "NOT_RUN"),
                   ("boundaries", "stage6_current_v503", "NOT_RUN"),
                   ("boundaries", "stage7", "NOT_RUN")),
        "quality": ("status", "PASS_SCOPED_STAGE4_OPEN"),
    },
    "gcpk-aber-hallo-wip59-direct-evidence-checkpoint@1.0.0": {
        "version": 59, "artifact": "current",
        "parent": ("parent", "sha256"),
        "counts": ("counts", "cumulative_independent_attested",
                   "external_lexical_case_sense_holds",
                   "total_governed_display_patterns",
                   "reclassified_optional_adjuncts", "total_learning_units",
                   "lexical_import_cards"),
        "new": ("counts", "new_exact_external_duden"),
        "members": ("qa", "zip_members"),
        "source": ("qa", "registered_original_pdf", "SHA256_PRESERVED"),
        "stage4": ("gate", "full_788_unit_adversarial_AI_de_fa_en_source_stage4", "OPEN"),
        "stages": (("gate", "stage5", "NOT_RUN"),
                   ("gate", "stage6_current_app_v503", "NOT_RUN"),
                   ("gate", "stage7", "NOT_RUN")),
        "quality": ("quality", "PASS_SCOPED_STAGE4_OPEN"),
    },
    "gcpk-aber-hallo-wip60-checkpoint@1": {
        "version": 60, "artifact": "flat",
        "parent": ("parent_sha256",),
        "counts": (None, "cumulative_attested", "remaining_holds",
                   None, None, "learning_units", "lexical_cards"),
        "new": (None, "new_attested"),
        "members": (None, "zip_members"),
        "source": (None, "source_pdfs", "PASS_2_UNCHANGED"),
        "stage4": (None, "global_stage4", "OPEN"),
        "stages": ((None, "stage5_to_7", "NOT_RUN"),),
        "quality": ("status", "PASS_SCOPED_STAGE4_OPEN"),
    },
    # WIP61 is a distinct observed receipt contract, not an alias of WIP60.
    # Registration authorizes *reading* this shape only. The actual WIP61
    # LATEST has stale WIP60 package metadata and missing predecessor pointer,
    # therefore audit_family must continue to BLOCK real CURRENT until fixed
    # through the independently authorized content producer.
    "gcpk-wip61-checkpoint@1": {
        "version": 61, "artifact": "flat",
        "parent": ("parent_sha256",),
        "counts": (None, "cumulative_attested", "external_holds",
                   None, None, "units", "lexical_cards"),
        "new": (None, "new_attested"),
        "members": (None, "zip_members"),
        "source": (None, "source_pdfs", "UNCHANGED"),
        "stage4": (None, "full_stage4", "OPEN"),
        "stages": ((None, "stage5_to_7", "NOT_RUN"),),
        "quality": ("status", "PASS_SCOPED_STAGE4_OPEN"),
    },
}


def value(obj, path):
    current = obj
    for part in path:
        if part is None:
            continue
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def valid_sha(s):
    return isinstance(s, str) and SHA.fullmatch(s) is not None and s != "0"*64


def audit_family(latest, receipt, source, receipt_path):
    """Return (error_codes, contract). Cannot authorize any production action."""
    errors = []
    schema = receipt.get("schema") if isinstance(receipt, dict) else None
    spec = SCHEMAS.get(schema) if isinstance(schema, str) else None
    if spec is None:
        return ["UNSUPPORTED_OR_FUTURE_RECEIPT_SCHEMA"], None
    version = spec["version"]
    contract = ("WIP61_EXPLICIT_KNOWN_SCOPED_RECEIPT_METADATA_ONLY" if version == 61
                else "WIP58_60_EXPLICIT_KNOWN_SCOPED_RECEIPT_METADATA_ONLY")
    if latest.get("schema") != "gcpk-workstream-latest@1.0.0" or latest.get("workstream") != WORKSTREAM:
        errors.append("LATEST_WRONG_SCHEMA_OR_WORKSTREAM")
    if source.get("schema") != "gcpk-source-manifest@1.1.0" or source.get("dataset") != WORKSTREAM:
        errors.append("SOURCE_MANIFEST_WRONG_IDENTITY")
    milestone = latest.get("latest_milestone")
    match = VERSION.match(milestone) if isinstance(milestone, str) else None
    if not match or int(match.group(1)) != version:
        errors.append("KNOWN_RECEIPT_NOT_CURRENT_MILESTONE")
    if not isinstance(receipt_path, str) or (
        receipt_path != latest.get("latest_receipt_path") or
        not receipt_path.startswith(BASE+"/") or
        ".." in receipt_path.split("/") or
        not receipt_path.endswith(".json") or
        f"WIP{version}" not in receipt_path
    ):
        errors.append("KNOWN_RECEIPT_PATH_NOT_CURRENT")
    if not isinstance(latest.get("latest_receipt_commit_sha"), str) or not HEX40.fullmatch(latest["latest_receipt_commit_sha"]):
        errors.append("KNOWN_RECEIPT_COMMIT_POINTER_INVALID")
    if value(receipt, spec["quality"][:1]) != spec["quality"][1]:
        errors.append("KNOWN_RECEIPT_SCOPED_STATUS_INVALID")
    if spec["artifact"] == "current":
        artifact = receipt.get("current")
        if receipt.get("workstream") != WORKSTREAM:
            errors.append("KNOWN_RECEIPT_WORKSTREAM_INVALID")
        if version == 59 and value(artifact, ("version",)) != "WIP59":
            errors.append("KNOWN_RECEIPT_VERSION_INVALID")
    else:
        artifact = {
            "filename": receipt.get("zip"), "sha256": receipt.get("zip_sha256"),
            "library_file_id": receipt.get("library_file_id"),
            "canonical_sha256": receipt.get("canonical_sha256"),
            "import_sha256": receipt.get("import_sha256"),
        }
    current = value(latest, ("authority", "current_portable"))
    package = latest.get("complete_working_content_package")
    if not isinstance(current, dict) or not isinstance(package, dict) or not isinstance(artifact, dict):
        errors.append("KNOWN_RECEIPT_ARTIFACT_STRUCTURE_MISSING")
    else:
        keys = ("filename", "sha256", "canonical_sha256", "import_sha256",
                "library_file_id")
        if spec["artifact"] == "current":
            keys = keys + ("size_bytes", "library_path")
        for key in keys:
            if not current.get(key) or current.get(key) != artifact.get(key):
                errors.append("KNOWN_RECEIPT_CURRENT_ARTIFACT_DRIFT:"+key)
        for a,b in (("filename","name"),("sha256","sha256"),
                    ("size_bytes","bytes"),("library_file_id","library_file_id"),
                    ("library_path","library_path")):
            if not current.get(a) or current.get(a) != package.get(b):
                errors.append("KNOWN_CURRENT_PACKAGE_DRIFT:"+a)
        for key in ("sha256","canonical_sha256","import_sha256"):
            if not valid_sha(current.get(key)):
                errors.append("KNOWN_CURRENT_HASH_INVALID:"+key)
        if (type(current.get("size_bytes")) is not int or current["size_bytes"] <= 0
                or type(package.get("bytes")) is not int or package["bytes"] <= 0):
            errors.append("KNOWN_CURRENT_SIZE_INVALID")
        if not isinstance(current.get("filename"), str) or f"WIP{version}-" not in current["filename"]:
            errors.append("KNOWN_CURRENT_ARTIFACT_VERSION_MISMATCH")
        if current.get("stage4") != "OPEN" or package.get("stage4") != "OPEN" or package.get("stage5_6_7") != "NOT_RUN":
            errors.append("KNOWN_STAGE4_7_BOUNDARY_DRIFT")
        if not isinstance(package.get("member_count"), int) or type(package["member_count"]) is not int or package["member_count"] != value(receipt, spec["members"]):
            errors.append("KNOWN_ZIP_MEMBER_COUNT_DRIFT")
    parent = value(receipt, spec["parent"])
    previous = value(latest, (f"previous_wip{version}_source_current", "portable"))
    if not valid_sha(parent) or not isinstance(package,dict) or parent != package.get("parent_sha256") or not isinstance(previous,dict) or parent != previous.get("sha256"):
        errors.append("KNOWN_PARENT_PORTABLE_LINEAGE_DRIFT")
    counter_paths = spec["counts"]
    counts = {}
    for key, pos in zip(("cumulative", "holds", "governed", "optional", "units", "import"), counter_paths[1:]):
        if pos is not None:
            counts[key] = value(receipt, (counter_paths[0],pos))
    new_count = value(receipt, spec["new"])
    for key, num in list(counts.items())+[("new",new_count)]:
        if type(num) is not int or num < 0:
            errors.append("KNOWN_COUNT_INVALID:"+key)
    if all(type(counts.get(x)) is int for x in ("units","import")) and (
        counts["units"] != 788 or counts["import"] != 787):
        errors.append("KNOWN_788_787_COUNT_DRIFT")
    if all(type(counts.get(x)) is int for x in ("cumulative","holds")):
        governed=counts["cumulative"]+counts["holds"]
        if governed != 981 or (
            "governed" in counts and counts["governed"] != governed):
            errors.append("KNOWN_981_GOVERNED_COUNT_DRIFT")
        if "optional" in counts and (
            type(counts["optional"]) is not int or counts["optional"] != 3
        ):
            errors.append("KNOWN_984_UNIVERSE_COUNT_DRIFT")
        progress=latest.get("progress")
        if not isinstance(progress,dict) or (
            progress.get("rektion_independent_external_attested_cumulative") != counts["cumulative"]
            or progress.get("rektion_external_holds_remaining") != counts["holds"]
        ):
            errors.append("KNOWN_LATEST_PROGRESS_COUNT_DRIFT")
        if (not isinstance(progress,dict)
                or progress.get("pending_independent_expert_stage4") is not True
                or progress.get("independent_expert_unreviewed_units") != 788):
            errors.append("KNOWN_STAGE4_INDEPENDENT_REVIEW_NOT_OPEN")
    if value(receipt,spec["source"][:2]) != spec["source"][2]:
        errors.append("KNOWN_SOURCE_IMMUTABILITY_CLAIM_DRIFT")
    if value(receipt,spec["stage4"][:2]) != spec["stage4"][2]:
        errors.append("KNOWN_STAGE4_CLAIM_DRIFT")
    for descriptor in spec["stages"]:
        if value(receipt,descriptor[:2]) != descriptor[2]:
            errors.append("KNOWN_STAGE5_7_CLAIM_DRIFT")
    src=source.get("source_set")
    if (not isinstance(src,list) or len(src)!=2
        or any(not isinstance(r,dict) or not isinstance(r.get("source_id"),str)
               or r.get("source_type")!="pdf" or not valid_sha(r.get("sha256"))
               for r in src)
        or len({r["source_id"] for r in src if isinstance(r,dict) and isinstance(r.get("source_id"),str)})!=2):
        errors.append("SOURCE_MANIFEST_SET_INVALID")
    # Original source files & Library binaries have NOT been independently read.
    return sorted(set(errors)), contract
