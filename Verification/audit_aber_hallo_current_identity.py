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


def verify(latest_bytes: bytes, receipt_bytes: bytes, source_bytes: bytes,
           *, receipt_relative_path: str):
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
