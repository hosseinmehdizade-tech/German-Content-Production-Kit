#!/usr/bin/env python3
"""OP-02 NONACTIVE Stage4→Stage5 didactic proof and exact import parity.

Metadata/bytes only: no content writer, no package, no linguistic certification.
A synthetic matching receipt is not independent AI review evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

SCHEMA = "gcpk-stage45-teaching-delta-parity@1"
STATUS = "NONACTIVE_VERSIONED_DRY_RUN"
HEX = re.compile(r"[0-9a-f]{64}\Z")
DELTA_KINDS = {
    "governed_case_or_preposition", "collocation", "fixed_phrase",
    "sense_specific_object", "register", "reusable_context", "lexical_pattern",
    "meaningful_contrast", "noun_verb", "support_verb", "other_with_reason",
}
PROVENANCE = {
    "REGISTERED_SOURCE", "SOURCE_EXACT", "SOURCE_ATTESTED",
    "CURATED_PEDAGOGICAL", "PARENT_CANONICAL_RELATION", "PARENT_GENERATED_EXAMPLE",
}
SOURCE_KINDS = {"REGISTERED_SOURCE", "SOURCE_EXACT", "SOURCE_ATTESTED"}
REQUIRED = {"id", "front", "back", "card_type", "category", "custom_fields"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def text(x) -> bool:
    return isinstance(x, str) and bool(x.strip())


def hexsha(x) -> bool:
    return isinstance(x, str) and HEX.fullmatch(x) is not None


def strict_pairs(items):
    result = {}
    for name, value in items:
        if name in result:
            raise ValueError("DUPLICATE_JSON_OBJECT_KEY")
        result[name] = value
    return result


def read_json(data: bytes):
    return json.loads(data, object_pairs_hook=strict_pairs)


def load_tsv(data: bytes):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""),
                            delimiter="\t")
    if (not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames))
            or not REQUIRED.issubset(reader.fieldnames)):
        raise ValueError("INVALID_TSV_HEADER")
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("INVALID_TSV_ROW")
    return rows


def verify(contract: dict, stage4_bytes: bytes, review_bytes: bytes,
           stage5_tsv_bytes: bytes) -> dict:
    issues = []
    def block(reason):
        issues.append(reason)

    if (not isinstance(contract, dict) or contract.get("schema") != SCHEMA
            or contract.get("status") != STATUS):
        return {"status": "BLOCKED", "errors": ["NONACTIVE_CONTRACT_REQUIRED"]}
    for field, value in (("stage4_sha256", stage4_bytes),
                         ("stage4_review_sha256", review_bytes),
                         ("stage5_tsv_sha256", stage5_tsv_bytes)):
        if not hexsha(contract.get(field)) or contract[field] != sha(value):
            block("EXACT_INPUT_SHA_MISMATCH:" + field)
    if not hexsha(contract.get("source_authority_sha256")):
        block("SOURCE_AUTHORITY_SHA_REQUIRED")
    if issues:
        return {"status": "BLOCKED", "errors": sorted(set(issues))}
    try:
        stage4, review, rows = (read_json(stage4_bytes), read_json(review_bytes),
                                load_tsv(stage5_tsv_bytes))
    except (ValueError, UnicodeError, TypeError) as exc:
        return {"status": "BLOCKED", "errors": ["MALFORMED_INPUT:" + str(exc)]}
    if not isinstance(stage4, dict) or not isinstance(review, dict):
        return {"status": "BLOCKED", "errors": ["MALFORMED_REVIEW_OR_STAGE4"]}
    cards = stage4.get("cards")
    if not isinstance(cards, list):
        return {"status": "BLOCKED", "errors": ["STAGE4_CARDS_NOT_ARRAY"]}
    if stage4.get("source_authority_sha256") != contract["source_authority_sha256"]:
        block("STAGE4_SOURCE_AUTHORITY_DRIFT")
    if (review.get("status") != "PASS_AI_LINGUISTIC_QA_AND_TECHNICAL_GATES"
            or review.get("scope") != "WHOLE_EXACT_STAGE4_CONTENT"
            or review.get("review_kind") != "AI_INDEPENDENT_ADVERSARIAL"
            or review.get("reviewed_stage4_sha256") != contract["stage4_sha256"]
            or review.get("source_authority_sha256") != contract["source_authority_sha256"]
            or not text(review.get("authoring_method"))
            or not text(review.get("independent_method"))
            or review.get("authoring_method") == review.get("independent_method")
            or not text(review.get("adversarial_method_evidence"))
            or type(review.get("risk_queue_open")) is not int
            or review.get("risk_queue_open") != 0
            or type(review.get("deterministic_scanned_cards")) is not int
            or review["deterministic_scanned_cards"] != len(cards)):
        block("STAGE4_INDEPENDENT_EXACT_REVIEW_RECEIPT_NOT_PROVEN")
    ids = [c.get("id") for c in cards if isinstance(c, dict)]
    projected_ids = [r.get("id") for r in rows]
    if (len(ids) != len(cards) or any(not text(cid) for cid in ids)
            or len(set(ids)) != len(ids)):
        block("STAGE4_DUPLICATE_OR_MISSING_CARD")
    if any(not text(cid) for cid in projected_ids) or len(set(projected_ids)) != len(projected_ids):
        block("STAGE5_DUPLICATE_OR_MISSING_CARD")
    if ids != projected_ids:
        block("STAGE4_STAGE5_CARD_ORDER_OR_ID_DRIFT")
    reviews = review.get("item_dispositions")
    if not isinstance(reviews, list):
        reviews = []
        block("STAGE4_ITEM_REVIEW_UNIVERSE_MISSING")
    by_key = {}
    for record in reviews:
        if (not isinstance(record, dict) or not text(record.get("card_id"))
                or not text(record.get("item_id"))):
            block("INVALID_STAGE4_REVIEW_RECORD")
            continue
        key = record["card_id"], record["item_id"]
        if key in by_key:
            block("DUPLICATE_STAGE4_REVIEW_RECORD")
        by_key[key] = record

    seen = set()
    counts = Counter()
    for i, card in enumerate(cards):
        if not isinstance(card, dict) or not text(card.get("id")):
            continue
        cid = card["id"]
        combos = card.get("kombinationen")
        if not isinstance(combos, list):
            block("STAGE4_COMBINATIONS_NOT_ARRAY:" + cid)
            continue
        counts["cards"] += 1
        if not combos:
            counts["closed_no_force"] += 1
            if (card.get("combination_disposition") != "CLOSED_NO_FORCE"
                    or not text(card.get("combination_close_reason"))):
                block("EMPTY_COMBINATIONS_UNJUSTIFIED:" + cid)
        elif card.get("combination_disposition") != "PRESENT":
            block("NONEMPTY_COMBINATIONS_NOT_PRESENT:" + cid)
        if i < len(rows):
            row = rows[i]
            if (row.get("card_type") != "de-vocabulary"
                    or not text(row.get("category"))
                    or row["category"] != card.get("category")):
                block("NON_NEUTRAL_ENVELOPE_OR_CATEGORY_DRIFT:" + cid)
            try:
                fields = read_json(row.get("custom_fields", "").encode("utf-8"))
            except (ValueError, UnicodeError, TypeError):
                fields = None
                block("INVALID_STAGE5_CUSTOM_FIELDS:" + cid)
            if not isinstance(fields, dict):
                block("STAGE5_CUSTOM_FIELDS_NOT_OBJECT:" + cid)
            else:
                if fields.get("presentation_contract") != "gfp-vocabulary-neutral@1":
                    block("NON_NEUTRAL_PRESENTATION_CONTRACT:" + cid)
                projected = fields.get("kombinationen")
                if not isinstance(projected, list):
                    block("STAGE5_COMBINATIONS_NOT_ARRAY:" + cid)
                elif canonical(projected) != canonical(combos):
                    block("STAGE45_COMBINATION_OR_METADATA_DRIFT:" + cid)
        for combo in combos:
            if not isinstance(combo, dict) or not text(combo.get("item_id")):
                block("STABLE_COMBINATION_ID_REQUIRED:" + cid)
                continue
            key = cid, combo["item_id"]
            if key in seen:
                block("DUPLICATE_STAGE4_COMBINATION_ID:" + cid)
            seen.add(key)
            counts["items"] += 1
            if not all(text(combo.get(f)) for f in ("de", "fa", "en", "kind")):
                block("INCOMPLETE_COMBINATION_TRILINGUAL_OR_TYPE:" + cid)
            provenance = combo.get("provenance")
            if not isinstance(provenance, str) or provenance not in PROVENANCE:
                block("MISSING_OR_UNRECOGNIZED_PROVENANCE:" + cid)
            if isinstance(provenance, str) and provenance in SOURCE_KINDS:
                ref = combo.get("source_ref")
                if (not isinstance(ref, dict) or not text(ref.get("source_id"))
                        or not text(ref.get("locator"))
                        or not hexsha(ref.get("source_sha256"))):
                    block("SOURCE_PROVENANCE_WITHOUT_EXACT_LOCATOR:" + cid)
            if provenance == "PARENT_GENERATED_EXAMPLE" and combo.get("source_ref") is not None:
                block("GENERATED_EXAMPLE_FALSE_SOURCE_CLAIM:" + cid)
            delta = combo.get("teaching_delta")
            if (not isinstance(delta, dict) or not isinstance(delta.get("kind"), str)
                    or delta["kind"] not in DELTA_KINDS or not text(delta.get("reason"))):
                block("MISSING_OR_UNJUSTIFIED_TEACHING_DELTA:" + cid)
            adjudication = by_key.get(key)
            if (not isinstance(adjudication, dict) or
                    adjudication.get("disposition") != "KEEP_WITH_REASON"
                    or adjudication.get("stage4_item_sha256") != sha(canonical(combo))
                    or not text(adjudication.get("reason"))):
                block("MISSING_OR_STALE_ITEM_LEVEL_STAGE4_REVIEW:" + cid)
    if seen != set(by_key):
        block("STAGE4_REVIEW_ITEM_UNIVERSE_MISMATCH")
    return {
        "schema": "gcpk-stage45-teaching-delta-parity-result@1",
        "status": "PASS_SCOPED_DETERMINISTIC_PARITY_ONLY" if not issues else "BLOCKED",
        "errors": sorted(set(issues)),
        "counts": dict(counts),
        "not_proven": [
            "Real independent linguistic AI review (only receipt form/hash checked)",
            "Original registered source text and locator verified independently",
            "Official Stage5 full importer/package and projection acceptance",
            "Stage6 exact CURRENT live runtime and Stage7 release acceptance",
            "Any change to active framework, writer, content or user UI",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("contract", "stage4", "stage4_review", "stage5_tsv"):
        ap.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    args = ap.parse_args()
    try:
        files = [getattr(args, key).read_bytes() for key in
                 ("stage4", "stage4_review", "stage5_tsv")]
        result = verify(json.loads(args.contract.read_text(encoding="utf-8")), *files)
    except (OSError, ValueError, UnicodeError) as exc:
        result = {"status": "BLOCKED", "errors": ["MISSING_OR_INVALID_INPUT:" + str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "PASS_SCOPED_DETERMINISTIC_PARITY_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
