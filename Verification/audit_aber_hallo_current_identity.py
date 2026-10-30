#!/usr/bin/env python3
"""OP-02 NONACTIVE read-only adapter for native Aber Hallo WIP50 LATEST/receipt.

This validates the real, tracked metadata *relationships*, not the remote
binary artifact, externally authorized CURRENT, source PDFs or Stage4 PASS.
Never modifies pointers, cards, Git, Library or release ZIPs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKSTREAM = "aber-hallo-listen-tabellen"
BASE = f"Workspaces/{WORKSTREAM}"
LATEST = f"{BASE}/LATEST.json"
SOURCES = f"{BASE}/00-source/SOURCE-MANIFEST.json"
SCHEMA = "gcpk-op02-native-aber-hallo-current-identity@1"
SHA = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")


def _read(raw: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    def constant(_):
        raise ValueError("NONFINITE_JSON_VALUE")
    if not isinstance(raw, bytes) or len(raw) > 250_000:
        raise ValueError("INVALID_JSON_BYTES")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=constant)


def _valid_sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None and value != "0" * 64


def _artifact_check(left, right, label, errors):
    if not isinstance(left, dict) or not isinstance(right, dict):
        errors.append("ARTIFACT_METADATA_MISSING:" + label)
        return
    for field in ("filename", "sha256", "drive_id"):
        if not left.get(field) or left.get(field) != right.get(field):
            errors.append("ARTIFACT_IDENTITY_DRIFT:" + label + ":" + field)
    if not _valid_sha(left.get("sha256")):
        errors.append("ARTIFACT_SHA_INVALID:" + label)


def verify_wip50_historical(latest_bytes: bytes, receipt_bytes: bytes, source_bytes: bytes,
                            *, receipt_relative_path: str):
    """HISTORICAL WIP50 contract, tested with frozen synthetic fixtures only."""
    errors = []
    try:
        latest, receipt, source = (_read(latest_bytes), _read(receipt_bytes), _read(source_bytes))
    except (UnicodeError, TypeError, ValueError, RecursionError):
        return _result(["UNTRUSTED_JSON_OR_DUPLICATE_KEYS"])
    if not all(isinstance(x, dict) for x in (latest, receipt, source)):
        return _result(["DOCUMENT_NOT_AN_OBJECT"])
    if latest.get("schema") != "gcpk-workstream-latest@1.0.0" or latest.get("workstream") != WORKSTREAM:
        errors.append("LATEST_WRONG_SCHEMA_OR_WORKSTREAM")
    if receipt.get("schema") != "flashcards-work-outcome-receipt@1.0.0" or receipt.get("workstream") != WORKSTREAM:
        errors.append("RECEIPT_WRONG_SCHEMA_OR_WORKSTREAM")
    if source.get("schema") != "gcpk-source-manifest@1.1.0" or source.get("dataset") != WORKSTREAM:
        errors.append("SOURCE_MANIFEST_WRONG_IDENTITY")
    stored_receipt = latest.get("latest_receipt_path")
    if (not isinstance(receipt_relative_path, str)
            or not isinstance(stored_receipt, str)
            or not stored_receipt.startswith(BASE+"/")
            or ".." in stored_receipt.split("/")
            or not stored_receipt.endswith(".json")
            or stored_receipt != receipt_relative_path):
        errors.append("LATEST_RECEIPT_PATH_DRIFT")
    if not isinstance(latest.get("latest_receipt_commit_sha"), str) or not COMMIT.fullmatch(latest["latest_receipt_commit_sha"]):
        errors.append("RECEIPT_COMMIT_POINTER_INVALID")

    current = latest.get("authority", {}).get("current_portable") if isinstance(latest.get("authority"), dict) else None
    master = latest.get("wip50_master_files")
    artifacts = receipt.get("artifacts")
    if not isinstance(current, dict) or not isinstance(master, dict) or not isinstance(artifacts, dict):
        errors.append("NATIVE_WIP50_ARTIFACT_STRUCTURE_MISSING")
    else:
        _artifact_check(current, artifacts.get("zip"), "zip", errors)
        _artifact_check(master.get("canonical"), artifacts.get("canonical"), "canonical", errors)
        _artifact_check(master.get("import"), artifacts.get("import"), "import", errors)
        for key in ("canonical", "import"):
            obj = master.get(key)
            if not isinstance(obj, dict) or current.get(key+"_sha256") != obj.get("sha256"):
                errors.append("NATIVE_CURRENT_MASTER_DRIFT:" + key)
        if (current.get("stage4") != "OPEN" or
                receipt.get("verification", {}).get("stage5") != "NOT_RUN" if isinstance(receipt.get("verification"), dict) else True):
            errors.append("STAGE4_OR_STAGE5_BOUNDARY_UNEXPECTED")
    if (not isinstance(receipt.get("milestone"), dict)
            or receipt["milestone"].get("state") != "IN_PROGRESS"
            or receipt["milestone"].get("quality") != "PASS_SCOPED_ONLY_NOT_GLOBAL_STAGE4"):
        errors.append("RECEIPT_SCOPED_QUALITY_BOUNDARY_UNEXPECTED")
    selected = source.get("source_set")
    if not isinstance(selected, list) or len(selected) != 2 or any(
            not isinstance(i, dict) or not _valid_sha(i.get("sha256"))
            or i.get("source_type") != "pdf" for i in selected):
        errors.append("SOURCE_MANIFEST_SET_INVALID")
    if receipt.get("artifacts") and isinstance(receipt.get("artifacts"), dict):
        for k in ("zip", "canonical", "import"):
            x=receipt["artifacts"].get(k)
            if not isinstance(x, dict) or not isinstance(x.get("bytes"), int) or x["bytes"] <= 0:
                errors.append("RECEIPT_ARTIFACT_SIZE_INVALID:"+k)
    return _result(errors)



def _verify_wip52(latest, receipt, source, receipt_relative_path):
    """Only WIP52 current tracked metadata parity, not portable-byte proof."""
    errors = []
    if latest.get("schema") != "gcpk-workstream-latest@1.0.0" or latest.get("workstream") != WORKSTREAM:
        errors.append("LATEST_WRONG_SCHEMA_OR_WORKSTREAM")
    if source.get("schema") != "gcpk-source-manifest@1.1.0" or source.get("dataset") != WORKSTREAM:
        errors.append("SOURCE_MANIFEST_WRONG_IDENTITY")
    if receipt.get("schema") != "gcpk-aber-hallo-wip52-milestone@1.0.0" or receipt.get("scope") != "ABER_HALLO_REKTION_CASE_SENSE_WIP52":
        errors.append("WIP52_RECEIPT_IDENTITY_UNEXPECTED")
    stored_path = latest.get("latest_receipt_path")
    if (not isinstance(stored_path, str) or
            not stored_path.startswith(BASE + "/") or
            ".." in stored_path.split("/") or
            not stored_path.endswith(".json") or
            receipt_relative_path != stored_path):
        errors.append("LATEST_RECEIPT_PATH_DRIFT")
    commit = latest.get("latest_receipt_commit_sha")
    if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
        errors.append("RECEIPT_COMMIT_POINTER_INVALID")
    if (not isinstance(latest.get("latest_milestone"), str)
            or not latest["latest_milestone"].startswith("WIP52_")
            or "WIP52" not in latest.get("status", "")):
        errors.append("WIP52_CURRENT_ROLE_OR_MILESTONE_DRIFT")
    if receipt.get("status") != "PASS_SCOPED_ONLY_STAGE4_OPEN" or receipt.get("validation", {}).get("no_formal_stage4_claim") is not True:
        errors.append("WIP52_SCOPED_NOT_STAGE4_BOUNDARY_MISSING")
    current = latest.get("authority", {}).get("current_portable") if isinstance(latest.get("authority"), dict) else None
    package = latest.get("complete_working_content_package")
    portable = receipt.get("portable")
    if not all(isinstance(v, dict) for v in (current, package, portable)):
        errors.append("WIP52_CURRENT_PORTABLE_STRUCTURE_MISSING")
    else:
        if not _valid_sha(current.get("sha256")):
            errors.append("WIP52_PORTABLE_SHA_INVALID")
        for field, rhs in (("filename", "filename"), ("sha256", "sha256"),
                           ("size_bytes", "size_bytes"), ("library_path", "library_path"),
                           ("library_file_id", "library_file_id")):
            if not current.get(field) or current.get(field) != portable.get(rhs):
                errors.append("WIP52_PORTABLE_RECEIPT_DRIFT:" + field)
        for left, right in (("filename", "name"), ("sha256", "sha256"),
                            ("size_bytes", "bytes"), ("library_path", "library_path"),
                            ("library_file_id", "library_file_id")):
            if current.get(left) != package.get(right):
                errors.append("WIP52_CURRENT_PACKAGE_DRIFT:" + left)
        if current.get("stage4") != "OPEN" or package.get("stage4") != "OPEN" or package.get("stage5_6_7") != "NOT_RUN":
            errors.append("WIP52_STAGE4_7_BOUNDARY_UNEXPECTED")
        for field in ("canonical_sha256", "import_sha256"):
            if not _valid_sha(current.get(field)):
                errors.append("WIP52_INTERNAL_MASTER_HASH_UNVERIFIED:" + field)
        if type(portable.get("size_bytes")) is not int or portable["size_bytes"] <= 0:
            errors.append("WIP52_PORTABLE_SIZE_INVALID")
    parent = receipt.get("parent")
    if not isinstance(parent, dict) or parent.get("version") != "WIP51" or not _valid_sha(parent.get("sha256")):
        errors.append("WIP52_PARENT_REFERENCE_INVALID")
    elif not isinstance(package, dict) or parent["sha256"] != package.get("source_parent_wip51_sha256"):
        errors.append("WIP52_PARENT_REFERENCE_DRIFT")
    summary = latest.get("wip52_evidence_bounded_rektion")
    counts = receipt.get("counts")
    progress = latest.get("progress")
    if not all(isinstance(v, dict) for v in (summary, counts, progress)):
        errors.append("WIP52_COUNTS_OR_DISPOSITION_STRUCTURE_MISSING")
    else:
        for key_a, key_b in (("confirmed_new", "new_exact_duden_confirmed"),
                             ("confirmed_cumulative", "cumulative_external_confirmed"),
                             ("holds_total", "remaining_external_holds"),
                             ("holds_legacy", "remaining_old_holds"),
                             ("holds_outside_original_824", "remaining_outside_824"),
                             ("changed_lexical_cards", "changed_cards"),
                             ("source_queue", "all_original_pending_reviewed_in_ledger")):
            if (type(summary.get(key_a)) is not int or type(counts.get(key_b)) is not int
                    or summary[key_a] != counts[key_b]):
                errors.append("WIP52_SCOPE_COUNTER_DRIFT:" + key_a)
        if any(type(counts.get(k)) is not int for k in ("learning_units", "import_cards")) or counts.get("learning_units") != 788 or counts.get("import_cards") != 787:
            errors.append("WIP52_UNIT_IDENTITY_COUNT_UNEXPECTED")
        if (type(summary.get("confirmed_cumulative")) is not int or
            type(summary.get("holds_total")) is not int or
            summary["confirmed_cumulative"] + summary["holds_total"] != 984):
            errors.append("WIP52_REKTION_TOTAL_ACCOUNTING_INVALID")
        if (type(summary.get("holds_legacy")) is not int or
            type(summary.get("holds_outside_original_824")) is not int or
            type(summary.get("holds_total")) is not int or
            summary["holds_legacy"] + summary["holds_outside_original_824"] != summary["holds_total"]):
            errors.append("WIP52_HOLDS_DISPOSITION_ACCOUNTING_INVALID")
        if summary.get("review_scoped_only") is not True or summary.get("source_pdf_immutable") is not True:
            errors.append("WIP52_SOURCE_OR_REVIEW_LIMIT_UNEXPECTED")
        if (not isinstance(current, dict) or
                summary.get("portable_sha256") != current.get("sha256")):
            errors.append("WIP52_SUMMARY_PORTABLE_SHA_DRIFT")
        for summary_key, progress_key in (
            ("confirmed_new", "wip52_new_exact_duden"),
            ("confirmed_cumulative", "rektion_external_attested_total"),
            ("holds_total", "rektion_evidence_holds")
        ):
            if summary.get(summary_key) != progress.get(progress_key):
                errors.append("WIP52_PROGRESS_COUNTER_DRIFT:" + summary_key)
        if progress.get("independent_expert_unreviewed_units") != 788 or progress.get("pending_independent_expert_stage4") is not True:
            errors.append("WIP52_INDEPENDENT_STAGE4_NOT_PROVEN_OPEN")
    sources = source.get("source_set")
    if not isinstance(sources, list) or len(sources) != 2 or any(
            not isinstance(x, dict) or not _valid_sha(x.get("sha256")) or x.get("source_type") != "pdf"
            for x in sources):
        errors.append("SOURCE_MANIFEST_SET_INVALID")
    result = _result(errors)
    result["evaluated_contract"] = "WIP52_CURRENT_TRACKED_METADATA_ONLY"
    result["historical_wip50_not_current"] = True
    return result




def _verify_direct_duden_checkpoint(latest, receipt, source, receipt_relative_path):
    """WIP56+ *schema-based* metadata QA; source/binary semantic checks remain OPEN.

    No specific WIP number or fixed attestation count is trusted as CURRENT.
    The exact version is taken from LATEST then cross-checked against the
    registered receipt path, parent portable, counts, and workstream metadata.
    A new receipt schema (not this same contract) MUST still fail closed.
    """
    errors = []
    if latest.get("schema") != "gcpk-workstream-latest@1.0.0" or latest.get("workstream") != WORKSTREAM:
        errors.append("LATEST_WRONG_SCHEMA_OR_WORKSTREAM")
    if source.get("schema") != "gcpk-source-manifest@1.1.0" or source.get("dataset") != WORKSTREAM:
        errors.append("SOURCE_MANIFEST_WRONG_IDENTITY")
    if (receipt.get("schema") != "gcpk-aber-hallo-direct-duden-scoped-checkpoint@1.0.0"
            or receipt.get("workstream") != WORKSTREAM
            or receipt.get("status") != "PASS_SCOPED_STAGE4_OPEN"):
        errors.append("DIRECT_DUDEN_RECEIPT_IDENTITY_UNEXPECTED")
    label = latest.get("latest_milestone")
    match = re.match(r"^WIP([0-9]+)_", label) if isinstance(label, str) else None
    version = int(match.group(1)) if match else 0
    if version < 56:
        errors.append("DIRECT_DUDEN_CURRENT_MILESTONE_INVALID")
    stored_path = latest.get("latest_receipt_path")
    if (not isinstance(stored_path, str) or
            not stored_path.startswith(BASE + "/") or
            ".." in stored_path.split("/") or
            not stored_path.endswith(".json") or
            stored_path != receipt_relative_path or
            not version or f"WIP{version}" not in stored_path):
        errors.append("LATEST_RECEIPT_PATH_DRIFT")
    if (not isinstance(latest.get("latest_receipt_commit_sha"), str)
            or not COMMIT.fullmatch(latest["latest_receipt_commit_sha"])):
        errors.append("RECEIPT_COMMIT_POINTER_INVALID")
    current = latest.get("authority", {}).get("current_portable") if isinstance(latest.get("authority"), dict) else None
    package = latest.get("complete_working_content_package")
    portable = receipt.get("portable")
    parent = receipt.get("parent")
    if not all(isinstance(x, dict) for x in (current, package, portable, parent)):
        errors.append("CURRENT_PORTABLE_PACKAGE_PARENT_STRUCTURE_MISSING")
    else:
        if not all(_valid_sha(x.get("sha256")) for x in (current, package, portable, parent)):
            errors.append("DIRECT_DUDEN_PORTABLE_OR_PARENT_SHA_INVALID")
        for left, right in (("filename", "filename"), ("sha256", "sha256"),
                            ("size_bytes", "size_bytes"),
                            ("library_file_id", "library_file_id"),
                            ("library_path", "library_path"),
                            ("canonical_sha256", "canonical_sha256"),
                            ("import_sha256", "import_sha256")):
            if (not current.get(left) or current.get(left) != portable.get(right)):
                errors.append("DIRECT_DUDEN_CURRENT_RECEIPT_DRIFT:" + left)
        for left, right in (("filename", "name"), ("sha256", "sha256"),
                            ("size_bytes", "bytes"),
                            ("library_file_id", "library_file_id"),
                            ("library_path", "library_path")):
            if current.get(left) != package.get(right):
                errors.append("DIRECT_DUDEN_CURRENT_PACKAGE_DRIFT:" + left)
        if (type(current.get("size_bytes")) is not int or current["size_bytes"] <= 0
                or type(portable.get("size_bytes")) is not int
                or type(package.get("bytes")) is not int):
            errors.append("DIRECT_DUDEN_PORTABLE_SIZE_INVALID")
        if (type(package.get("member_count")) is not int
                or type(receipt.get("validation", {}).get("zip_members")) is not int
                or package.get("member_count") != receipt["validation"]["zip_members"]):
            errors.append("DIRECT_DUDEN_ZIP_MEMBER_COUNT_DRIFT")
        if current.get("stage4") != "OPEN" or package.get("stage4") != "OPEN" or package.get("stage5_6_7") != "NOT_RUN":
            errors.append("DIRECT_DUDEN_STAGE4_7_BOUNDARY_UNEXPECTED")
        if parent.get("sha256") != package.get("parent_sha256") or not _valid_sha(parent.get("sha256")):
            errors.append("DIRECT_DUDEN_PARENT_SHA_DRIFT")
        old = latest.get(f"previous_wip{version}_source_current")
        previous = old.get("portable") if isinstance(old, dict) else None
        if (not isinstance(previous, dict)
                or previous.get("sha256") != parent.get("sha256")
                or previous.get("filename") != parent.get("filename")):
            errors.append("DIRECT_DUDEN_PREVIOUS_CURRENT_LINEAGE_DRIFT")
        if (not version or
                not isinstance(current.get("filename"), str) or
                f"WIP{version}-" not in current["filename"] or
                current["filename"] != portable.get("filename")):
            errors.append("DIRECT_DUDEN_MILESTONE_PORTABLE_VERSION_DRIFT")
        if (not isinstance(portable.get("library_roundtrip"), str)
                or not portable["library_roundtrip"].startswith("PASS_")):
            errors.append("DIRECT_DUDEN_PORTABLE_ROUNDTRIP_CLAIM_MISSING")
        for name in ("canonical_sha256", "import_sha256"):
            if not _valid_sha(current.get(name)):
                errors.append("DIRECT_DUDEN_INTERNAL_MASTER_HASH_INVALID:" + name)
    counts = receipt.get("counts")
    progress = latest.get("progress")
    if not isinstance(counts, dict) or not isinstance(progress, dict):
        errors.append("DIRECT_DUDEN_COUNTERS_MISSING")
    else:
        names = ("new_duden_exact", "cumulative_external_attested",
                 "remaining_external_holds", "governed_patterns",
                 "non_governed_optional_adjuncts", "unit_count", "import_cards")
        if any(type(counts.get(x)) is not int or counts[x] < 0 for x in names):
            errors.append("DIRECT_DUDEN_COUNTERS_INVALID")
        else:
            if counts["unit_count"] != 788 or counts["import_cards"] != 787:
                errors.append("DIRECT_DUDEN_UNIT_IMPORT_COUNT_DRIFT")
            if (counts["cumulative_external_attested"] + counts["remaining_external_holds"]
                    != counts["governed_patterns"]):
                errors.append("DIRECT_DUDEN_GOVERNED_PATTERN_TOTAL_INVALID")
            if counts["governed_patterns"] + counts["non_governed_optional_adjuncts"] != 984:
                errors.append("DIRECT_DUDEN_ORIGINAL_UNIVERSE_TOTAL_INVALID")
            if (progress.get("rektion_independent_external_attested_cumulative")
                    != counts["cumulative_external_attested"]
                    or progress.get("rektion_external_holds_remaining")
                    != counts["remaining_external_holds"]):
                errors.append("DIRECT_DUDEN_PROGRESS_COUNTER_DRIFT")
            if (version and progress.get(f"rektion_wip{version}_new_duden") is not None
                    and progress[f"rektion_wip{version}_new_duden"] != counts["new_duden_exact"]):
                errors.append("DIRECT_DUDEN_MILESTONE_NEW_COUNTER_DRIFT")
        if (progress.get("pending_independent_expert_stage4") is not True
                or progress.get("independent_expert_unreviewed_units") != 788):
            errors.append("DIRECT_DUDEN_INDEPENDENT_REVIEW_OPEN_NOT_PROVEN")
    validation = receipt.get("validation")
    if not isinstance(validation, dict):
        errors.append("DIRECT_DUDEN_VALIDATION_STRUCTURE_MISSING")
    else:
        for field, desired in (
            ("full_stage4", "OPEN"),
            ("stages_5_6_7", "NOT_RUN"),
            ("original_source_PDFs", "UNCHANGED"),
            ("learning_card_examples_translations", "UNCHANGED"),
            ("zip_crc", "PASS"),
            ("sha256", "PASS"),
            ("canonical_import_rection_qa", "PASS"),
        ):
            if validation.get(field) != desired:
                errors.append("DIRECT_DUDEN_SCOPE_VALIDATION_DRIFT:" + field)
    sources = source.get("source_set")
    if (not isinstance(sources, list) or len(sources) != 2
            or len({x.get("source_id") for x in sources if isinstance(x, dict)}) != 2
            or any(not isinstance(x, dict) or x.get("source_type") != "pdf"
                   or not _valid_sha(x.get("sha256")) for x in sources)):
        errors.append("SOURCE_MANIFEST_SET_INVALID")
    result = _result(errors)
    result["evaluated_contract"] = "DIRECT_DUDEN_SCOPED_TRACKED_METADATA_ONLY"
    result["resolved_milestone"] = label if isinstance(label, str) else None
    result["historical_wip52_not_current"] = True
    return result


def verify(latest_bytes: bytes, receipt_bytes: bytes, source_bytes: bytes,
           *, receipt_relative_path: str):
    """Dispatch by the *receipt* contract; never silently coerce WIP52 to WIP50."""
    try:
        latest, receipt, source = (_read(latest_bytes), _read(receipt_bytes),
                                   _read(source_bytes))
    except (UnicodeError, TypeError, ValueError, RecursionError):
        return _result(["UNTRUSTED_JSON_OR_DUPLICATE_KEYS"])
    if not all(isinstance(x, dict) for x in (latest, receipt, source)):
        return _result(["DOCUMENT_NOT_AN_OBJECT"])
    if receipt.get("schema") == "gcpk-aber-hallo-direct-duden-scoped-checkpoint@1.0.0":
        return _verify_direct_duden_checkpoint(latest, receipt, source, receipt_relative_path)
    if receipt.get("schema") == "gcpk-aber-hallo-wip52-milestone@1.0.0":
        return _verify_wip52(latest, receipt, source, receipt_relative_path)
    if receipt.get("schema") == "flashcards-work-outcome-receipt@1.0.0":
        # This historical shape cannot certify current WIP52 even if its
        # old field names/hashes are still present as archive metadata.
        if (isinstance(latest.get("latest_milestone"), str) and
                latest["latest_milestone"].startswith("WIP52_")):
            return _result(["HISTORICAL_WIP50_RECEIPT_CANNOT_CERTIFY_WIP52_CURRENT"])
        result = verify_wip50_historical(latest_bytes, receipt_bytes, source_bytes,
                                         receipt_relative_path=receipt_relative_path)
        result["evaluated_contract"] = "WIP50_HISTORICAL_SCHEMA_ONLY"
        return result
    return _result(["UNSUPPORTED_OR_FUTURE_RECEIPT_SCHEMA"])

def _result(errors):
    return {
        "schema": SCHEMA,
        "status": "PASS_SCOPED_NATIVE_METADATA_CONSISTENCY_ONLY" if not errors else "BLOCKED",
        "errors": sorted(set(errors)),
        "production_stage5_allowed": False,
        "stage4_independent_semantic_review_completed": False,
        "real_current_issuer_authenticated": False,
        "source_pdf_or_portable_bytes_verified": False,
        "no_writes_performed": True,
        "limitations": [
            "Native metadata equality is not independent commit authorization",
            "Latest may change: select exact current commit and source artifact separately",
            "Git blob/current/receipt/Drive binary bytes not authenticated by this function",
            "An actual Stage5 4-role sidecar and independent Stage4 signoff are absent",
            "Never treat this WIP50-only adapter as a universal LATEST parser",
        ],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--latest", type=Path, default=ROOT/LATEST)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--sources", type=Path, default=ROOT/SOURCES)
    args=ap.parse_args()
    try:
        receipt=args.receipt.resolve(strict=True)
        relative=receipt.relative_to(ROOT.resolve()).as_posix()
        if any(p.is_symlink() for p in (args.latest,args.sources,args.receipt)):
            raise ValueError("SYMLINK_INPUT")
        outcome=verify(args.latest.read_bytes(),receipt.read_bytes(),
                       args.sources.read_bytes(),receipt_relative_path=relative)
    except (ValueError, OSError):
        outcome=_result(["INPUT_PATH_NOT_TRACKED_OR_UNSAFE"])
    print(json.dumps(outcome,indent=2,ensure_ascii=False))
    return 0 if outcome["status"].startswith("PASS_SCOPED") else 2

if __name__=="__main__":
    raise SystemExit(main())
