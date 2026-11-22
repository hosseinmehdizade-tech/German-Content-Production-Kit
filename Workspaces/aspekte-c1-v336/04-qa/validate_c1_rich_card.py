#!/usr/bin/env python3
"""C1 source-owned structural pre-release check; never linguistic or runtime PASS.

Run against the actual mutable C1 canonical card JSON or its exact projected TSV.
Unknown/unmapped fields fail closed instead of guessing from a Persian back.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

SECTIONS = ("Synonyme", "Antonyme", "Wortfamilie", "Verwandte Wörter", "Kombinationen")
CLOSED = {"CLOSED_NO_FORCE", "NOT_APPLICABLE"}


def populated(value):
    return isinstance(value, str) and bool(value.strip())


def parse_json_field(value, label):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{label}: invalid JSON: {exc}") from exc
    return value


def load(path):
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        rows = data.get("cards") if isinstance(data, dict) else data
    elif path.suffix.lower() == ".tsv":
        with path.open(encoding="utf-8-sig", newline="") as fp:
            rows = list(csv.DictReader(fp, delimiter="\t"))
    else:
        raise ValueError("expected .json canonical cards or .tsv projection")
    if not isinstance(rows, list) or not rows or not all(isinstance(x, dict) for x in rows):
        raise ValueError("nonempty list of card objects required")
    return rows


def norm(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


def validate(rows):
    errors = []
    seen = set()

    def fail(cid, code, detail=""):
        errors.append({"id": cid, "code": code, "detail": detail})

    for number, row in enumerate(rows, 1):
        cid = str(row.get("id") or row.get("card_id") or "").strip()
        if not cid:
            cid = f"row:{number}"
            fail(cid, "MISSING_ID")
        if cid in seen:
            fail(cid, "DUPLICATE_ID")
        seen.add(cid)
        if not populated(row.get("front")):
            fail(cid, "MISSING_FRONT")
        try:
            custom = parse_json_field(row.get("custom_fields", {}), "custom_fields") or {}
            meanings = parse_json_field(row.get("meanings", custom.get("c1_meanings")) if isinstance(custom, dict) else row.get("meanings"), "meanings")
            examples = parse_json_field(row.get("examples"), "examples")
            details = parse_json_field(row.get("details"), "details")
            review = parse_json_field(row.get("c1_right_review", custom.get("c1_right_review")) if isinstance(custom, dict) else row.get("c1_right_review"), "c1_right_review")
        except ValueError as exc:
            fail(cid, "UNREADABLE_STRUCTURED_FIELD", str(exc))
            continue
        if not isinstance(custom, dict):
            fail(cid, "CUSTOM_FIELDS_NOT_OBJECT")
        if not isinstance(meanings, list) or not meanings:
            fail(cid, "MISSING_TYPED_MEANINGS_DE_FA_EN")
        else:
            for index, meaning in enumerate(meanings, 1):
                if not isinstance(meaning, dict) or any(not populated(meaning.get(lang)) for lang in ("de", "fa", "en")):
                    fail(cid, "INCOMPLETE_MEANING", str(index))
        if not isinstance(examples, list) or len(examples) != 4:
            fail(cid, "EXACTLY_FOUR_EXAMPLES_REQUIRED", str(len(examples)) if isinstance(examples, list) else "unstructured")
            examples = []
        example_de = []
        for index, example in enumerate(examples, 1):
            if not isinstance(example, dict):
                fail(cid, "EXAMPLE_NOT_OBJECT", str(index))
                continue
            de = example.get("de", example.get("text"))
            translations = example.get("translations", {})
            translations = translations if isinstance(translations, dict) else {}
            fa = example.get("fa", translations.get("fa"))
            en = example.get("en", translations.get("en"))
            if any(not populated(value) for value in (de, fa, en)):
                fail(cid, "EXAMPLE_MISSING_DE_FA_EN", str(index))
            elif norm(de) in example_de:
                fail(cid, "DUPLICATED_EXAMPLE_DE", str(index))
            if populated(de):
                example_de.append(norm(de))
        if not isinstance(details, list):
            fail(cid, "MISSING_STRUCTURED_DETAILS")
            details = []
        details_by_title = {}
        for section in details:
            if isinstance(section, dict) and populated(section.get("title")):
                if section["title"] in details_by_title:
                    fail(cid, "REPEATED_DETAIL_SECTION", section["title"])
                details_by_title[section["title"]] = section
        if not isinstance(review, dict):
            fail(cid, "MISSING_FIVE_RIGHT_SECTION_REVIEWS")
            review = {}
        for title in SECTIONS:
            rec = review.get(title)
            if not isinstance(rec, dict):
                fail(cid, "SECTION_NOT_REVIEWED", title)
                continue
            status = rec.get("decision")
            visible = details_by_title.get(title)
            items = visible.get("items") if isinstance(visible, dict) else None
            if status == "VERIFIED_PRESENT":
                if not isinstance(items, list) or not items:
                    fail(cid, "VERIFIED_SECTION_WITHOUT_ITEMS", title)
                    continue
                for index, item in enumerate(items, 1):
                    if not isinstance(item, dict) or any(not populated(item.get(lang)) for lang in ("de", "fa")):
                        fail(cid, "SECTION_ITEM_MISSING_DE_FA", f"{title}:{index}")
                        continue
                    if title == "Kombinationen":
                        if not populated(item.get("en")):
                            fail(cid, "COMBINATION_MISSING_EN", str(index))
                        surface = norm(item["de"])
                        if surface in example_de:
                            fail(cid, "COMBINATION_EQUALS_EXAMPLE", surface)
                        elif any(surface in sentence for sentence in example_de) and not (
                            populated(item.get("source")) and populated(item.get("teaching_delta"))
                        ):
                            fail(cid, "OVERLAPPING_COMBINATION_NEEDS_INDEPENDENT_EVIDENCE", surface)
            elif status in CLOSED:
                if not populated(rec.get("reason")):
                    fail(cid, "SECTION_CLOSURE_WITHOUT_REASON", title)
                if isinstance(items, list) and items:
                    fail(cid, "CLOSED_SECTION_HAS_VISIBLE_ITEMS", title)
            else:
                fail(cid, "SECTION_UNRESOLVED_OR_INVALID_DECISION", title)
        grammar = row.get("c1_grammar_review")
        if grammar is None and isinstance(custom, dict):
            grammar = custom.get("c1_grammar_review")
        try:
            grammar = parse_json_field(grammar, "c1_grammar_review")
        except ValueError:
            grammar = None
        if not isinstance(grammar, dict) or grammar.get("decision") not in {"VERIFIED", "NOT_APPLICABLE"} or not populated(grammar.get("reason")):
            fail(cid, "GRAMMAR_FORMS_REKTION_NOT_REVIEWED")
    return {"status": "STRUCTURAL_PASS_NOT_STAGE4_5_6_7" if not errors else "BLOCKED",
            "cards_checked": len(rows), "errors": errors, "approved_cards": 0, "mutated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        report = validate(load(args.input))
        report["input_sha256"] = hashlib.sha256(args.input.read_bytes()).hexdigest()
    except (OSError, ValueError, csv.Error) as exc:
        report = {"status": "INPUT_ERROR", "error": str(exc), "approved_cards": 0}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "STRUCTURAL_PASS_NOT_STAGE4_5_6_7" else 2


if __name__ == "__main__":
    sys.exit(main())
