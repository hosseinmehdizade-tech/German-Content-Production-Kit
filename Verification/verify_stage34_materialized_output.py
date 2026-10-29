#!/usr/bin/env python3
"""OP01/OP02: independent byte-to-unit binding for NONACTIVE Stage3/4 proposal.

A metadata-only Stage3/4 compatibility PASS does NOT prove hashes correspond
to any output bytes. This adapter requires a separately supplied expected
whole-file digest, raw final Stage3 output, and full ID-to-unit hash parity.
It NEVER certifies source fidelity, semantic Stage4 or publication authority.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

from validate_stage3_stage4_unification import validate_candidate

SCHEMA = "gcpk-stage34-materialized-output-identity@1"
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_BYTES = 64 * 1024 * 1024


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("DUPLICATE_JSON_KEY")
        d[k] = v
    return d


def reject_nonfinite(value):
    raise ValueError("NONFINITE_JSON_VALUE")


def unit_digest(unit: dict) -> str:
    # Versioned canonicalization for a JSON object; byte-exact whole-file hash
    # separately checks original order, formatting and additional metadata.
    raw = json.dumps(unit, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return digest(raw)


def verify(stage3: dict, stage4: dict, output_bytes: bytes,
           independently_pinned_sha256: str) -> dict:
    errors = []
    unit_count = 0
    if not isinstance(stage3, dict) or not isinstance(stage4, dict):
        return _result(["STAGE_METADATA_MUST_BE_OBJECTS"], 0)
    # Reuse the original dry-run contract. Its PASS is necessary but NOT a
    # substitution for a read of actual output bytes.
    try:
        errors += ["METADATA:" + e for e in validate_candidate(stage3, stage4)]
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        errors.append("MALFORMED_STAGE_METADATA:" + type(exc).__name__)
    if (not isinstance(independently_pinned_sha256, str)
            or not SHA.fullmatch(independently_pinned_sha256)
            or independently_pinned_sha256 == "0" * 64):
        errors.append("INDEPENDENT_EXTERNAL_OUTPUT_PIN_MISSING_OR_INVALID")
    if not isinstance(output_bytes, bytes) or not 0 < len(output_bytes) <= MAX_BYTES:
        return _result(errors + ["OUTPUT_BYTES_MISSING_OR_TOO_LARGE"], 0)
    actual = digest(output_bytes)
    if actual != independently_pinned_sha256:
        errors.append("ACTUAL_OUTPUT_BYTES_DIFFER_FROM_EXTERNAL_PIN")
    if stage3.get("output_sha256") != actual:
        errors.append("STAGE3_OUTPUT_SHA_NOT_ACTUAL_BYTES")
    if stage4.get("reviewed_output_sha256") != actual:
        errors.append("STAGE4_REVIEWED_SHA_NOT_ACTUAL_BYTES")
    try:
        doc = json.loads(output_bytes.decode("utf-8"),
                         object_pairs_hook=unique_pairs,
                         parse_constant=reject_nonfinite)
        if not isinstance(doc, dict) or not isinstance(doc.get("learning_units"), list):
            raise ValueError("UNSUPPORTED_OUTPUT_SCHEMA_EXPECT_LEARNING_UNITS")
        units = doc["learning_units"]
        if not units:
            raise ValueError("EMPTY_LEARNING_UNITS")
        seen = {}
        for unit in units:
            if not isinstance(unit, dict):
                raise ValueError("UNIT_NOT_AN_OBJECT")
            uid = unit.get("id")
            if not isinstance(uid, str) or not uid.strip():
                raise ValueError("MISSING_UNIT_ID")
            if uid in seen:
                raise ValueError("DUPLICATE_UNIT_ID")
            seen[uid] = unit_digest(unit)
        unit_count = len(seen)
        declared = stage3.get("unit_sha256_by_id")
        if not isinstance(declared, dict) or declared != seen:
            errors.append("DECLARED_PER_UNIT_DIGESTS_DO_NOT_MATCH_MATERIALIZED_OUTPUT")
        if stage3.get("lexical_cards_total") != unit_count:
            errors.append("STAGE3_DECLARED_COUNT_DIFFERS_FROM_REAL_OUTPUT")
        if stage4.get("deterministic_scanned_units") != unit_count:
            errors.append("STAGE4_DECLARED_SCAN_COUNT_DIFFERS_FROM_REAL_OUTPUT")
        reviews = stage4.get("unit_dispositions")
        if not isinstance(reviews, list) or len(reviews) != unit_count:
            errors.append("REAL_OUTPUT_UNIT_REVIEW_COUNT_MISMATCH")
        else:
            for review in reviews:
                if not isinstance(review, dict):
                    errors.append("MALFORMED_REVIEW_ENTRY")
                    continue
                uid = review.get("unit_id")
                if not isinstance(uid, str) or uid not in seen:
                    errors.append("REVIEW_REFERENCES_UNKNOWN_MATERIALIZED_UNIT")
                elif review.get("unit_sha256") != seen[uid]:
                    errors.append("REVIEW_SHA_DIFFERS_FROM_REAL_UNIT_BYTES:" + uid)
    except (UnicodeError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        errors.append("UNREADABLE_MATERIALIZED_OUTPUT:" + str(exc)[:90])
    return _result(errors, unit_count)


def _result(errors: list[str], unit_count: int) -> dict:
    return {
        "schema": SCHEMA,
        "status": "BLOCKED_UNBOUND_OUTPUT" if errors
                  else "PASS_SCOPED_OUTPUT_BYTES_UNIT_IDENTITY_ONLY",
        "errors": sorted(set(errors)),
        "materialized_units": unit_count,
        "source_fidelity_verified": False,
        "stage4_semantic_pass": False,
        "issuer_authenticated": False,
        "production_authorized": False,
        "performed_writes": False,
        "note": ("Caller must authenticate the expected output SHA outside"
                 " metadata/PR; self-supplied external pin is NOT proof of"
                 " real CURRENT authority. JSON learning_units only.")
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage3", type=Path, required=True)
    parser.add_argument("--stage4", type=Path, required=True)
    parser.add_argument("--materialized-output", type=Path, required=True)
    parser.add_argument("--external-output-sha256", required=True)
    args = parser.parse_args()
    try:
        s3 = json.loads(args.stage3.read_text(encoding="utf-8"))
        s4 = json.loads(args.stage4.read_text(encoding="utf-8"))
        raw = args.materialized_output.read_bytes()
        report = verify(s3, s4, raw, args.external_output_sha256)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        report = _result(["INPUT_FILE_ERROR:" + type(exc).__name__], 0)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"].startswith("PASS_SCOPED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
