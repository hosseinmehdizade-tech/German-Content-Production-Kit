#!/usr/bin/env python3
"""NONACTIVE OP-02: bind Stage4 corrected claims to actual before/after/readback bytes.

Never signs off semantic QA, authenticates a writer, performs CAS, writes content,
or authorizes Stage5/6/7. An externally supplied expected post-edit SHA is a
comparison value, NOT independently authenticated authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_stage4_snapshot_review_receipt import (
    digest, parse, unit_hash, verify as verify_receipt, clean_hash,
)

SCHEMA = "gcpk-op02-stage4-corrected-application-byte-binding@1"
CORRECTION_PENDING = "CORRECTED_REQUIRES_SEPARATE_POSTEDIT_CAS_EVIDENCE:"


def report(errors, *, expected, observed, corrected, changed, review_status):
    return {
        "schema": SCHEMA,
        "status": ("PASS_SCOPED_CORRECTED_BYTES_ONLY_NOT_STAGE4_SIGNOFF"
                   if not errors else "BLOCKED_CORRECTED_APPLICATION_BYTES"),
        "errors": sorted(set(errors)),
        "expected_postedit_sha256_reference_only": expected,
        "observed_postedit_sha256": observed,
        "claimed_corrected_units": corrected,
        "observed_changed_units": changed,
        "original_receipt_status": review_status,
        "old_source_content_modified": False,
        "postedit_bytes_read": True,
        "remote_cas_verified": False,
        "issuer_authenticated": False,
        "source_fidelity_verified": False,
        "stage4_semantic_pass": False,
        "stage5_allowed": False,
        "stage6_pass": False,
        "stage7_release_final": False,
        "production_authorized": False,
        "performed_writes": False,
        "limitations": [
            "Supplied post-edit digest, anchor and readback are not authenticated by this tool.",
            "Unit-byte identity does not establish German/Persian/English correctness.",
            "No remotely verified Git CAS, user approval, independent reviewer method or Stage4 signoff.",
            "Current workstream LATEST and portable ZIP must be resolved separately.",
        ]
    }


def bind_corrections(anchor, before_bytes, import_bytes, worksheet_bytes,
                     source_pdf_bytes, receipt_bytes,
                     after_bytes, readback_bytes, expected_after_sha256):
    errors = []
    changed = []
    corrected = []
    before_status = "UNREADABLE_OR_UNVERIFIED"
    observed = digest(after_bytes) if isinstance(after_bytes, bytes) else None
    if not clean_hash(expected_after_sha256):
        errors.append("EXPECTED_POSTEDIT_SHA256_INVALID")
    if not isinstance(after_bytes, bytes) or not isinstance(readback_bytes, bytes):
        errors.append("POSTEDIT_OR_READBACK_NOT_BYTES")
    else:
        if observed != expected_after_sha256:
            errors.append("POSTEDIT_EXPECTED_SHA_MISMATCH")
        if after_bytes != readback_bytes:
            errors.append("POSTEDIT_READBACK_BYTE_MISMATCH")
    try:
        before_receipt = verify_receipt(
            anchor, before_bytes, import_bytes, worksheet_bytes,
            source_pdf_bytes, receipt_bytes
        )
        before_status = before_receipt["status"]
        # v0.1 rightly blocks EVERY corrected claim. Only that very specific
        # blocker may be excused here; all stale/synthetic/self-issued claims
        # and all other structural problems remain blocked.
        unexpected = [error for error in before_receipt["errors"]
                      if not error.startswith(CORRECTION_PENDING)]
        if unexpected:
            errors.extend("BASE_RECEIPT:" + error for error in unexpected)
        receipt = parse(receipt_bytes)
        before = parse(before_bytes)
        after = parse(after_bytes)
        if not isinstance(receipt, dict) or not isinstance(before, dict) or not isinstance(after, dict):
            raise ValueError("TOPLEVEL_JSON_MUST_BE_OBJECT")
        if not isinstance(before.get("learning_units"), list) or not isinstance(after.get("learning_units"), list):
            raise ValueError("LEARNING_UNITS_MUST_BE_LIST")
        older, newer = before["learning_units"], after["learning_units"]
        old_ids = [u["id"] for u in older]
        new_ids = [u["id"] for u in newer]
        if (len(old_ids) != len(set(old_ids)) or len(new_ids) != len(set(new_ids))
            or old_ids != new_ids or
            any(not isinstance(u, dict) or not isinstance(u.get("id"), str) or not u["id"]
                for u in older + newer)):
            errors.append("POSTEDIT_UNIT_IDENTITY_OR_ORDER_DRIFT")
        if set(before) != set(after) or any(
            before[key] != after[key] for key in before if key != "learning_units"
        ):
            errors.append("POSTEDIT_ROOT_METADATA_DRIFT")
        if len(older) != len(newer):
            errors.append("POSTEDIT_UNIT_COUNT_CHANGED")
        prior = {u["id"]: u for u in older if isinstance(u, dict) and isinstance(u.get("id"), str)}
        successor = {u["id"]: u for u in newer if isinstance(u, dict) and isinstance(u.get("id"), str)}
        changed = sorted(
            uid for uid in (set(prior) & set(successor))
            if prior[uid] != successor[uid]
        )
        if not isinstance(receipt.get("reviews"), list):
            errors.append("REVIEW_LIST_INVALID")
            reviews = []
        else:
            reviews = receipt["reviews"]
        declarations = {}
        for item in reviews:
            if not isinstance(item, dict) or not isinstance(item.get("unit_id"), str):
                errors.append("INVALID_REVIEW_CORRECTION_RECORD")
                continue
            uid = item["unit_id"]
            if uid in declarations:
                errors.append("DUPLICATE_CORRECTED_REVIEW")
            declarations[uid] = item
        corrected = sorted(
            uid for uid, review in declarations.items()
            if review.get("disposition") == "corrected"
        )
        if not corrected:
            errors.append("NO_CORRECTED_UNITS_CLAIMED")
        if set(changed) != set(corrected):
            errors.append("CHANGED_UNITS_DIFFER_FROM_CORRECTED_RECEIPT")
        for uid in corrected:
            if uid not in prior or uid not in successor:
                errors.append("UNKNOWN_CORRECTED_UNIT:" + uid)
                continue
            review = declarations[uid]
            if review.get("unit_sha256") != unit_hash(prior[uid]):
                errors.append("CORRECTED_BEFORE_UNIT_SHA_MISMATCH:" + uid)
            after_sha = review.get("applied_change_sha256")
            if not clean_hash(after_sha) or after_sha != unit_hash(successor[uid]):
                errors.append("CORRECTED_POSTEDIT_UNIT_SHA_MISMATCH:" + uid)
            if prior[uid] == successor[uid]:
                errors.append("CORRECTED_UNIT_UNCHANGED:" + uid)
            if prior[uid].get("provenance") != successor[uid].get("provenance"):
                errors.append("CORRECTED_UNIT_PROVENANCE_MUTATED:" + uid)
    except (ValueError, TypeError, KeyError, UnicodeError, AttributeError, RecursionError, OverflowError) as exc:
        errors.append("MALFORMED_CORRECTION_BINDING:" + type(exc).__name__)
    return report(errors, expected=expected_after_sha256, observed=observed,
                  corrected=corrected, changed=changed, review_status=before_status)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("anchor", "before", "import_tsv", "worksheet", "source_a1_a2",
                 "source_b1_c2", "receipt", "after", "readback"):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--expected-after-sha256", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        sources = {
            "a1-a2": args.source_a1_a2.read_bytes(),
            "b1-c2": args.source_b1_c2.read_bytes(),
        }
        output = bind_corrections(
            json.loads(args.anchor.read_text(encoding="utf-8")),
            args.before.read_bytes(), args.import_tsv.read_bytes(),
            args.worksheet.read_bytes(), sources, args.receipt.read_bytes(),
            args.after.read_bytes(), args.readback.read_bytes(),
            args.expected_after_sha256,
        )
    except (OSError, ValueError, TypeError) as exc:
        output = report(["UNREADABLE_INPUT:" + type(exc).__name__],
                        expected=args.expected_after_sha256, observed=None,
                        corrected=[], changed=[], review_status="UNREADABLE")
    raw = json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(raw, encoding="utf-8")
    else:
        print(raw)
    return 0 if output["status"].startswith("PASS_SCOPED_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
