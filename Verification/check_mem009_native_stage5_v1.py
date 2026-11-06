#!/usr/bin/env python3
"""MEM-009 structural gate on REAL Universal v2 Stage5 TSV bytes (read-only).

No guesswork from delimited Persian glosses; typed senses are validated only when
actually present in custom_fields.canonical_unit.meanings (or explicit custom_fields.meanings).
Missing one example per meaning is informational, never an import failure.
This gate is NOT linguistic Stage4, full meaning retention proof, or runtime Stage6.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_multi_meaning_one_card_v1 import audit_cards


def _fail(code: str, detail: str = "") -> dict:
    return {
        "schema": "mem009-native-stage5-structural@1.0.0",
        "status": "FAIL_MEM009_NATIVE_STRUCTURE_ONLY",
        "errors": [{"code": code, "detail": detail}],
        "stage4_approved": False,
        "runtime_approved": False,
        "content_mutated": False,
    }


def audit_tsv_bytes(payload: bytes) -> dict:
    try:
        decoded = payload.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded, newline=""), delimiter="\t", strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            return _fail("INVALID_OR_DUPLICATE_TSV_HEADER")
        required = {"id", "front", "back", "custom_fields"}
        if not required <= set(reader.fieldnames):
            return _fail("MISSING_NATIVE_TSV_COLUMNS", str(sorted(required-set(reader.fieldnames))))
        rows = list(reader)
        if not rows:
            return _fail("EMPTY_NATIVE_TSV")
        if any(None in row or any(k is None for k in row) for row in rows):
            return _fail("TSV_ROW_FIELD_COUNT_INVALID")
    except (UnicodeError, csv.Error, ValueError) as exc:
        return _fail("INVALID_NATIVE_TSV", str(exc))

    cards = []
    for ix, row in enumerate(rows, 1):
        cid = str(row.get("id") or f"row:{ix}").strip()
        try:
            custom = json.loads(row.get("custom_fields") or "{}")
        except (TypeError, ValueError):
            return _fail("INVALID_CUSTOM_FIELDS_JSON", cid)
        if not isinstance(custom, dict):
            return _fail("CUSTOM_FIELDS_NOT_OBJECT", cid)
        canonical = custom.get("canonical_unit") or {}
        if not isinstance(canonical, dict):
            return _fail("CANONICAL_UNIT_NOT_OBJECT", cid)
        lexical_id = canonical.get("lexical_target_id") or custom.get("lexical_target_id")
        if lexical_id is not None and not isinstance(lexical_id, str):
            return _fail("LEXICAL_TARGET_ID_NOT_STRING", cid)
        new = {"card_id": row.get("id"), "front": row.get("front"),
               "lexical_target_id": lexical_id}
        # Legacy source adapters may store meanings as plain strings, language
        # maps or gloss objects without sense IDs. Such data is UNSTRUCTURED,
        # not malformed; do not introduce a new Stage5 schema requirement.
        # If any sense is explicitly typed, audit that whole typed list,
        # including missing IDs on sibling entries.
        raw_meanings = (canonical["meanings"] if "meanings" in canonical
                        else custom.get("meanings"))
        if (isinstance(raw_meanings, list) and
                any(isinstance(item, dict) and "sense_id" in item
                    for item in raw_meanings)):
            new["meanings"] = raw_meanings

        # Canonical example objects are the source of truth, not the rendered
        # Universal v2 language-fragment list. Examples with explicit bilingual
        # fields are validated; established untyped language-fragment formats
        # are not incorrectly rejected as broken DE/FA pairs.
        examples = canonical.get("examples")
        if examples is not None:
            if not isinstance(examples, list):
                return _fail("CANONICAL_EXAMPLES_WRONG_TYPE", cid)
            typed = []
            for ex in examples:
                if not isinstance(ex, dict):
                    continue
                sid = ex.get("sense_id")
                if "de" in ex or "fa" in ex:
                    typed.append({"sense_id": sid, "de": ex.get("de"), "fa": ex.get("fa")})
                elif sid:
                    de = ex.get("text") if str(ex.get("lang") or "de").lower().startswith("de") else None
                    translations = ex.get("translations") or []
                    if not isinstance(translations, list):
                        return _fail("CANONICAL_EXAMPLE_TRANSLATIONS_WRONG_TYPE", cid)
                    fa = next((t.get("text") for t in translations
                               if isinstance(t, dict) and
                               str(t.get("lang") or "").lower().startswith("fa")), None)
                    # A monolingual source example is not silently counted as
                    # satisfying the per-sense bilingual preference.
                    if de and fa:
                        typed.append({"sense_id": sid, "de": de, "fa": fa})
            new["examples"] = typed

        for section in ("relations", "synonyms", "antonyms", "combinations",
                        "related_words", "word_family", "rektion"):
            if section in canonical:
                new[section] = canonical[section]
        cards.append(new)

    result = audit_cards(cards, "universal_v2_tsv", len(rows))
    result["schema"] = "mem009-native-stage5-structural@1.0.0"
    result["status"] = ("PASS_MEM009_NATIVE_STRUCTURE_ONLY"
                        if not result["errors"] else "FAIL_MEM009_NATIVE_STRUCTURE_ONLY")
    result["input_tsv_sha256"] = hashlib.sha256(payload).hexdigest()
    result["native_stage5_tsv"] = True
    result["full_meaning_retention_verified"] = False
    result["independent_linguistic_stage4"] = False
    result["runtime_stage6"] = False
    result["no_content_mutation"] = True
    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tsv", type=Path)
    parser.add_argument("--expected-cards", type=int)
    args = parser.parse_args()
    try:
        raw = args.tsv.read_bytes()
        result = audit_tsv_bytes(raw)
        if args.expected_cards is not None and args.expected_cards != result.get("cards_seen"):
            result["status"] = "FAIL_MEM009_NATIVE_STRUCTURE_ONLY"
            result.setdefault("errors", []).append({
                "code": "COUNT_MISMATCH",
                "detail": f"expected {args.expected_cards}, found {result.get('cards_seen')}",
            })
    except OSError as exc:
        result = _fail("INPUT_READ_FAILURE", str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS_MEM009_NATIVE_STRUCTURE_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
