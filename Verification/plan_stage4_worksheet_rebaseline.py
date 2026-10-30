#!/usr/bin/env python3
"""OP-02 NONACTIVE: deterministic, read-only Stage4 worksheet rebaseline PREVIEW.

Only accepts exact externally pinned Canonical + old worksheet bytes.
Never changes workstream data, overwrites reviewer decisions, signs off semantics,
authenticates issuer, or authorizes Stage5/6/7. Caller pins are NOT a trust root.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

from audit_stage4_current_worksheet_freshness import (
    FROZEN, REVIEW_FIELDS, audit, projected, sha256,
)
from audit_stage4_snapshot_review_receipt import parse as strict_json

SCHEMA = "gcpk-op02-stage4-worksheet-rebaseline-preview@1"
FIELDS = ("id",) + FROZEN + REVIEW_FIELDS
MAX_BYTES = 32_000_000
UNSAFE_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def result(status, errors, *, canonical_sha, old_sha, candidate=None,
           affected=0, field_drifts=None, decisions=0, count=0):
    return {
        "schema": SCHEMA,
        "status": status,
        "errors": sorted(set(errors)),
        "canonical_sha256_observed": canonical_sha,
        "old_worksheet_sha256_observed": old_sha,
        "preview_worksheet_sha256": sha256(candidate) if candidate is not None else None,
        "preview_worksheet_bytes": len(candidate) if candidate is not None else None,
        "expected_units": count,
        "stale_affected_units": affected,
        "stale_fields": field_drifts or {},
        "prior_reviewer_cells_populated": decisions,
        "proposed_reviewer_cells_populated": 0,
        "candidate_persisted": False,
        "source_or_locked_modified": False,
        "workstream_currentness_authenticated": False,
        "issuer_authenticated": False,
        "stage4_semantic_pass": False,
        "stage5_allowed": False,
        "stage6_pass": False,
        "stage7_release_final": False,
        "production_authorized": False,
        "limitations": [
            "Only the caller supplied Canonical/worksheet SHA pins are checked.",
            "A freshly generated reviewer worksheet is NOT an independent linguistic review.",
            "No Git CAS/readback, workstream approval, original PDF validation or portable ZIP replay.",
            "Never overwrite a worksheet with existing reviewer cells or other columns.",
        ],
    }


def plan(canonical_bytes: bytes, old_worksheet_bytes: bytes, *,
         expected_canonical_sha256: str, expected_worksheet_sha256: str,
         expected_units: int = 788):
    errors = []
    ch = sha256(canonical_bytes) if isinstance(canonical_bytes, bytes) else None
    wh = sha256(old_worksheet_bytes) if isinstance(old_worksheet_bytes, bytes) else None

    def blocked(errs, *, affected=0, fields=None, decisions=0):
        return (result("BLOCKED_REBASELINE_PREVIEW", errs, canonical_sha=ch,
                       old_sha=wh, affected=affected, field_drifts=fields,
                       decisions=decisions, count=expected_units), None)

    if type(expected_units) is not int or not 1 <= expected_units <= 100_000:
        return blocked(["INVALID_EXPECTED_UNITS"])
    if (not isinstance(canonical_bytes, bytes)
        or not isinstance(old_worksheet_bytes, bytes)
        or len(canonical_bytes) > MAX_BYTES or len(old_worksheet_bytes) > MAX_BYTES):
        return blocked(["INVALID_OR_OVERSIZED_INPUT"])
    if not isinstance(expected_canonical_sha256, str) or len(expected_canonical_sha256) != 64:
        errors.append("INVALID_CANONICAL_EXTERNAL_PIN")
    if not isinstance(expected_worksheet_sha256, str) or len(expected_worksheet_sha256) != 64:
        errors.append("INVALID_WORKSHEET_EXTERNAL_PIN")
    if ch != expected_canonical_sha256:
        errors.append("CANONICAL_EXTERNAL_PIN_MISMATCH")
    if wh != expected_worksheet_sha256:
        errors.append("WORKSHEET_EXTERNAL_PIN_MISMATCH")
    if errors:
        return blocked(errors)

    # Strict JSON parser rejects duplicate keys and NaN/Infinity, which the
    # older exploratory worksheet audit need not reject.
    try:
        canonical = strict_json(canonical_bytes)
        if not isinstance(canonical, dict) or not isinstance(canonical.get("learning_units"), list):
            raise ValueError("INVALID_CANONICAL_STRUCTURE")
        units = canonical["learning_units"]
        ids = [u["id"] for u in units]
        if (len(units) != expected_units
            or any(not isinstance(u, dict) or not isinstance(u.get("id"), str)
                   or not u["id"] for u in units)
            or len(set(ids)) != len(ids)):
            raise ValueError("INVALID_UNIQUE_UNIT_IDS")
        worksheet_text = old_worksheet_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(worksheet_text, newline=""),
                                restkey="__EXTRA__")
        if reader.fieldnames is None or set(reader.fieldnames) != set(FIELDS) or len(reader.fieldnames) != len(FIELDS):
            raise ValueError("UNSUPPORTED_REVIEWER_WORKSHEET_COLUMNS")
        old_rows = list(reader)
    except (ValueError, TypeError, KeyError, UnicodeError, AttributeError, RecursionError) as exc:
        return blocked(["MALFORMED_INPUT:" + str(exc)])

    baseline = audit(canonical_bytes, old_worksheet_bytes,
                     expected_units=expected_units,
                     expected_canonical_sha256=expected_canonical_sha256,
                     expected_worksheet_sha256=expected_worksheet_sha256)
    if baseline["status"] == "BLOCKED_INVALID_REVIEW_SNAPSHOT":
        return blocked(["EXISTING_WORKSHEET_STRUCTURE_INVALID", *baseline["errors"]],
                       affected=baseline["affected_units"],
                       fields=baseline["drifts_by_field"])

    occupied = sum(bool((row.get(field) or "").strip())
                   for row in old_rows for field in REVIEW_FIELDS)
    if occupied:
        return blocked(["EXISTING_REVIEWER_CELLS_MUST_BE_PRESERVED"],
                       affected=baseline["affected_units"],
                       fields=baseline["drifts_by_field"], decisions=occupied)
    candidate = io.StringIO(newline="")
    writer = csv.DictWriter(candidate, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    try:
        for unit in units:
            projection = projected(unit)
            row = {"id": unit["id"]}
            for field in FROZEN:
                value = projection[field]
                if field.endswith("_json"):
                    value = json.dumps(value, ensure_ascii=False, allow_nan=False,
                                       sort_keys=True, separators=(",", ":"))
                if not isinstance(value, str):
                    raise ValueError("NON_STRING_FROZEN_VALUE:" + field)
                if value.lstrip().startswith(UNSAFE_PREFIXES) or "\x00" in value:
                    raise ValueError("UNSAFE_SPREADSHEET_CELL:" + field)
                row[field] = value
            if unit["id"].lstrip().startswith(UNSAFE_PREFIXES):
                raise ValueError("UNSAFE_SPREADSHEET_UNIT_ID")
            for field in REVIEW_FIELDS:
                row[field] = ""
            writer.writerow(row)
        output_bytes = candidate.getvalue().encode("utf-8")
        # Independently replay the existing audit over the newly generated
        # bytes: exact IDs/fields/order and null semantic approval.
        second = audit(canonical_bytes, output_bytes,
                       expected_units=expected_units,
                       expected_canonical_sha256=expected_canonical_sha256,
                       expected_worksheet_sha256=sha256(output_bytes))
        if (second["status"] != "CURRENT_WORKSHEET_ONLY_STAGE4_REVIEW_NOT_CERTIFIED"
            or second["affected_units"] != 0 or second["decisions_entered"] != 0
            or second["errors"]):
            return blocked(["GENERATED_WORKSHEET_FAILED_FRESHNESS_REPLAY",
                            *second["errors"]])
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        return blocked(["PROJECTION_REJECTED:" + str(exc)],
                       affected=baseline["affected_units"],
                       fields=baseline["drifts_by_field"])

    return (result(
        "PASS_SCOPED_REBASELINE_PREVIEW_ONLY_NOT_STAGE4"
        if baseline["status"] == "STALE_WORKSHEET_BLOCKS_STAGE4"
        else "ALREADY_FRESH_PREVIEW_ONLY_NOT_STAGE4",
        [], canonical_sha=ch, old_sha=wh, candidate=output_bytes,
        affected=baseline["affected_units"], field_drifts=baseline["drifts_by_field"],
        count=expected_units), output_bytes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--old-worksheet", type=Path, required=True)
    parser.add_argument("--expected-canonical-sha256", required=True)
    parser.add_argument("--expected-worksheet-sha256", required=True)
    parser.add_argument("--expected-units", type=int, default=788)
    parser.add_argument("--report", type=Path, default=None,
                        help="Optional diagnostic JSON only; never output or overwrite learner worksheet")
    args = parser.parse_args()
    try:
        report, _ = plan(args.canonical.read_bytes(), args.old_worksheet.read_bytes(),
                         expected_canonical_sha256=args.expected_canonical_sha256,
                         expected_worksheet_sha256=args.expected_worksheet_sha256,
                         expected_units=args.expected_units)
    except OSError as exc:
        report = result("BLOCKED_REBASELINE_PREVIEW",
                        ["UNREADABLE_INPUT:" + type(exc).__name__],
                        canonical_sha=None, old_sha=None, count=args.expected_units)
    raw = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.write_text(raw, encoding="utf-8")
    else:
        print(raw)
    return 0 if report["status"].startswith(("PASS_SCOPED_", "ALREADY_FRESH_")) else 2


if __name__ == "__main__":
    raise SystemExit(main())
