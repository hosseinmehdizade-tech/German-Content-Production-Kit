#!/usr/bin/env python3
"""MEM-009 read-only card/sense structural QA; never asserts linguistic or runtime PASS.

Usage:
  python Verification/audit_multi_meaning_one_card_v1.py INPUT.csv --expect-cards 158
  python Verification/audit_multi_meaning_one_card_v1.py INPUT.json

Input profiles: existing flat B2-style preview CSV, or explicitly typed {"cards":[...]}
JSON. Untyped translation strings are NOT split on slashes/semicolons to invent senses.
No content edits, no per-sense example quota, no card/ID/SRS migration.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def finding(code: str, severity: str, card_id: str, detail: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "card_id": card_id, "detail": detail}


def load_cards(path: Path) -> tuple[list[dict[str, Any]], str]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            cards = list(csv.DictReader(stream))
        return cards, "flat_csv"
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        cards = data.get("cards") if isinstance(data, dict) else data
        if not isinstance(cards, list):
            raise ValueError("JSON_CARDS_MUST_BE_LIST")
        if not all(isinstance(card, dict) for card in cards):
            raise ValueError("JSON_CARD_MUST_BE_OBJECT")
        return cards, "structured_json"
    raise ValueError("UNSUPPORTED_INPUT_EXTENSION")


def audit_cards(cards: list[dict[str, Any]], profile: str,
                expected_count: int | None = None) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    advisories: list[dict[str, str]] = []
    seen_cards: set[str] = set()
    seen_lexical_targets: dict[str, str] = {}
    structured_sense_cards = 0
    untyped_sense_cards = 0
    missing_per_sense_examples = 0
    examples_checked = 0

    if expected_count is not None and len(cards) != expected_count:
        errors.append(finding("COUNT_MISMATCH", "ERROR", "",
                              f"expected {expected_count}, observed {len(cards)}"))

    for row_number, card in enumerate(cards, 1):
        if not isinstance(card, dict):
            errors.append(finding("CARD_NOT_OBJECT", "ERROR", str(row_number), ""))
            continue
        cid = str(card.get("card_id") or card.get("unit_id") or card.get("id") or "").strip()
        if not cid:
            errors.append(finding("CARD_ID_MISSING", "ERROR", str(row_number), ""))
            continue
        if cid in seen_cards:
            errors.append(finding("CARD_ID_DUPLICATE", "ERROR", cid, "same stable card ID repeated"))
        seen_cards.add(cid)

        # Only a trusted, explicit lexical-target identity can show two cards were
        # generated from the SAME target. Never auto-merge equal-looking fronts.
        lexical_target_id = card.get("lexical_target_id")
        if isinstance(lexical_target_id, str) and lexical_target_id.strip():
            key = lexical_target_id.strip()
            other = seen_lexical_targets.get(key)
            if other and other != cid:
                errors.append(finding("LEXICAL_TARGET_SPLIT", "ERROR", cid,
                                      f"same explicit lexical target on {other}"))
            seen_lexical_targets.setdefault(key, cid)

        raw_meanings = card.get("meanings")
        if raw_meanings is None and isinstance(card.get("meanings_json"), str):
            encoded = card["meanings_json"].strip()
            if encoded:
                try:
                    raw_meanings = json.loads(encoded)
                except json.JSONDecodeError:
                    errors.append(finding("MEANINGS_JSON_INVALID", "ERROR", cid, ""))
                    continue

        senses: set[str] | None = None
        if raw_meanings is None or isinstance(raw_meanings, str):
            # Plain back_fa_preview may contain several meanings. Neither slash
            # nor semicolon proves sense identity; no missing-example verdict.
            untyped_sense_cards += 1
        elif not isinstance(raw_meanings, list):
            errors.append(finding("MEANINGS_WRONG_TYPE", "ERROR", cid, "expected list"))
        else:
            structured_sense_cards += 1
            senses = set()
            if not raw_meanings:
                errors.append(finding("MEANINGS_EMPTY", "ERROR", cid, "typed meanings have no entries"))
            for item in raw_meanings:
                if not isinstance(item, dict):
                    errors.append(finding("MEANING_NOT_OBJECT", "ERROR", cid, ""))
                    continue
                sid = str(item.get("sense_id") or "").strip()
                fa = str(item.get("fa") or item.get("translation_fa") or "").strip()
                if not sid:
                    errors.append(finding("SENSE_ID_MISSING", "ERROR", cid, ""))
                elif sid in senses:
                    errors.append(finding("SENSE_ID_DUPLICATE", "ERROR", cid, sid))
                else:
                    senses.add(sid)
                if not fa:
                    errors.append(finding("SENSE_FA_MISSING", "ERROR", cid, sid))

        example_items = card.get("examples")
        if example_items is None:
            # Existing B2 flat preview uses parallel example_1_de/fa fields.
            indices = sorted({key[8:-3] for key in card
                              if key.startswith("example_") and key.endswith("_de")
                              and key[8:-3].isdigit()}, key=int)
            example_items = [
                {"de": card.get(f"example_{n}_de", ""),
                 "fa": card.get(f"example_{n}_fa", "")}
                for n in indices
            ]
        if not isinstance(example_items, list):
            errors.append(finding("EXAMPLES_WRONG_TYPE", "ERROR", cid, ""))
            continue
        illustrated: set[str] = set()
        for example in example_items:
            if not isinstance(example, dict):
                errors.append(finding("EXAMPLE_NOT_OBJECT", "ERROR", cid, ""))
                continue
            de = str(example.get("de") or "").strip()
            fa = str(example.get("fa") or "").strip()
            if bool(de) != bool(fa):
                errors.append(finding("EXAMPLE_BILINGUAL_PAIR_BROKEN", "ERROR", cid,
                                      "DE/FA must be present together"))
            elif de and fa:
                examples_checked += 1
            sid = str(example.get("sense_id") or "").strip()
            if sid:
                if senses is not None:
                    if sid not in senses:
                        errors.append(finding("EXAMPLE_UNKNOWN_SENSE", "ERROR", cid, sid))
                    elif de and fa:
                        illustrated.add(sid)
                else:
                    advisories.append(finding("EXAMPLE_SENSE_UNVERIFIABLE", "INFO", cid,
                                             f"{sid}: no typed meanings"))
        # Absence of example for a sense is ONLY an informational observation.
        if senses is not None:
            for sid in sorted(senses - illustrated):
                missing_per_sense_examples += 1
                advisories.append(finding("PER_SENSE_EXAMPLE_MISSING", "INFO", cid, sid))

        # Typed relations (if present) may refer to senses, without turning
        # sense IDs into graph target_ids or forcing every relation to be tagged.
        for section in ("relations", "synonyms", "antonyms", "combinations",
                        "related_words", "word_family", "rektion"):
            entries = card.get(section)
            if entries is None:
                continue
            if isinstance(entries, dict):
                entries = [e for value in entries.values()
                           for e in (value if isinstance(value, list) else [value])]
            if not isinstance(entries, list):
                continue  # Legacy free-text source profiles are out of scope.
            for relation in entries:
                if not isinstance(relation, dict):
                    continue
                sid = str(relation.get("sense_id") or "").strip()
                if not sid:
                    continue
                if senses is not None and sid not in senses:
                    errors.append(finding("RELATION_UNKNOWN_SENSE", "ERROR", cid,
                                          f"{section}: {sid}"))
                elif senses is None:
                    advisories.append(finding("RELATION_SENSE_UNVERIFIABLE", "INFO", cid,
                                             f"{section}: {sid}"))

    return {
        "schema": "mem009-one-card-multi-meaning-audit@1.0.0",
        "status": ("STRUCTURAL_PASS_NOT_STAGE4_5_6_7"
                   if not errors else "STRUCTURAL_FAIL_NOT_STAGE4_5_6_7"),
        "profile": profile,
        "cards_seen": len(cards),
        "unique_card_ids": len(seen_cards),
        "structured_sense_cards": structured_sense_cards,
        "untyped_sense_cards": untyped_sense_cards,
        "examples_paired": examples_checked,
        "per_sense_example_missing_info_only": missing_per_sense_examples,
        "errors": errors,
        "advisories": advisories,
        "independent_semantic_qa": False,
        "import_or_runtime_verified": False,
        "content_mutated": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--expect-cards", type=int)
    args = parser.parse_args()
    try:
        if args.expect_cards is not None and args.expect_cards < 0:
            raise ValueError("NEGATIVE_EXPECTED_CARD_COUNT")
        cards, profile = load_cards(args.input)
        result = audit_cards(cards, profile, args.expect_cards)
    except (OSError, ValueError, csv.Error) as exc:
        result = {"status": "INPUT_ERROR", "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "STRUCTURAL_PASS_NOT_STAGE4_5_6_7" else 2


if __name__ == "__main__":
    raise SystemExit(main())
