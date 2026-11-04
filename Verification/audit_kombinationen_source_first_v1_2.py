#!/usr/bin/env python3
"""Advisory, read-only source-first combination / Rektion overlap diagnostic.

Not a Stage4 signature or a correctness/idiomaticity judge. JSON input:
{"card_id":"...","headword":"...", "examples":[{"de":"..."}],
 "combinations":[{"de":"...","fa":"...","en":"...", "kind":"...",
   "origin":"REGISTERED_SOURCE", "evidence":[{"source_id":"...","locator":"...","access_status":"VERIFIED_EXACT_ENTRY"}],
   "teaching_delta":"PATTERN"}], "rection":[{"de":"..."}]}

Usage: python Verification/audit_kombinationen_source_first_v1_2.py input.json \
         [--registered-sources Architecture/03-SOURCES/SOURCE-REGISTRY.json] [--output report.json]
Returns 0 for successful *diagnostic execution* (even if findings exist), 2 on invalid input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

TECHNICAL_MARKERS = {"context", "pattern", "adjective_noun", "noun_verb", "verb_object", "collocation", "nvv", "fixed_expression"}
SUPPORTED_ORIGINS = {"REGISTERED_SOURCE", "PARENT_GENERATED_EXAMPLE", "PARENT_CANONICAL_RELATION", "CURATED_PEDAGOGICAL"}


def clean(value):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or "")).casefold()).strip(" .!?·;,:\t\r\n")


def diagnostic(card, registered_sources=None):
    if not isinstance(card, dict) or not isinstance(card.get("combinations", []), list):
        raise ValueError("expected card object with combinations list")
    card_id = card.get("card_id") or "UNSPECIFIED"
    combos = card.get("combinations", [])
    examples = card.get("examples", [])
    rection = card.get("rection", [])
    if not isinstance(examples, list) or not isinstance(rection, list):
        raise ValueError("examples and rection must be lists")
    example_de = [clean(ex.get("de") if isinstance(ex, dict) else ex) for ex in examples]
    rection_de = [clean(rec.get("de") if isinstance(rec, dict) else rec) for rec in rection]
    issues = []
    seen = set()
    kinds = set()

    def add(code, severity, item_index=None, detail=""):
        issues.append({"code": code, "severity": severity, "item_index": item_index, "detail": detail})

    for i, item in enumerate(combos):
        if not isinstance(item, dict) or not isinstance(item.get("de"), str):
            add("STRUCTURED_ITEM_REQUIRED", "HIGH", i, "Expected one object with de/fa/en/kind metadata")
            continue
        de = item["de"].strip()
        norm = clean(de)
        if not norm:
            add("EMPTY_COMBINATION", "HIGH", i)
            continue
        if norm in seen:
            add("DUPLICATE_COMBINATION", "HIGH", i, de)
        seen.add(norm)
        if norm in TECHNICAL_MARKERS:
            add("TECHNICAL_KIND_LEAK", "HIGH", i, de)
        if norm in example_de:
            add("EXACT_EXAMPLE_CLONE", "MEDIUM", i, de)
        elif len(norm) >= 12 and any(norm in ex for ex in example_de if ex):
            add("EXAMPLE_FRAGMENT_OVERLAP", "LOW_ADVISORY", i, de)
        if norm in rection_de:
            add("EXACT_REKTION_DUPLICATE", "HIGH", i, de)
        if isinstance(item.get("kind"), str) and item["kind"]:
            kinds.add(item["kind"])
        else:
            add("MISSING_PATTERN_KIND", "MEDIUM", i, de)
        if not item.get("teaching_delta"):
            add("MISSING_TEACHING_DELTA", "MEDIUM", i, de)
        if not item.get("fa"):
            add("MISSING_FA", "HIGH", i, de)
        if card.get("require_en", True) and not item.get("en"):
            add("MISSING_EN", "HIGH", i, de)
        origin = item.get("origin")
        if origin not in SUPPORTED_ORIGINS:
            add("MISSING_OR_UNRECOGNIZED_ORIGIN", "HIGH", i, de)
        if origin == "PARENT_GENERATED_EXAMPLE":
            add("EXAMPLES_USED_AS_SOURCE", "LOW_ADVISORY", i, "Need independently justified teaching delta")
        if origin == "REGISTERED_SOURCE":
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                add("MISSING_REGISTERED_SOURCE_EVIDENCE", "HIGH", i, de)
            else:
                for ev in evidence:
                    if not isinstance(ev, dict) or not ev.get("source_id") or not ev.get("locator"):
                        add("INCOMPLETE_SOURCE_EVIDENCE", "HIGH", i, de)
                        continue
                    if registered_sources is not None and ev["source_id"] not in registered_sources:
                        add("UNKNOWN_REGISTERED_SOURCE", "HIGH", i, str(ev["source_id"]))
                    if ev.get("access_status") != "VERIFIED_EXACT_ENTRY":
                        add("UNVERIFIED_SOURCE_CLAIM", "MEDIUM", i, str(ev["source_id"]))
        if origin == "CURATED_PEDAGOGICAL" and item.get("source_claim") == "REGISTERED_SOURCE":
            add("FALSE_SOURCE_PROMOTION", "HIGH", i, de)
    # Check abstract rection too; a prepositional phrase is not necessarily an argument-valency rule.
    for i, item in enumerate(rection):
        if not isinstance(item, (str, dict)):
            add("INVALID_REKTION", "MEDIUM", i)
            continue
        rec = item if isinstance(item, dict) else {"de": item}
        if not rec.get("de"):
            add("EMPTY_REKTION", "MEDIUM", i)
        elif isinstance(item, dict) and item.get("teaching_delta") is None:
            add("REKTION_NO_INDEPENDENT_TEACHING_DELTA", "LOW_ADVISORY", i, str(rec.get("de")))
    if len(seen) >= 3 and len(kinds) == 1:
        add("SINGLE_PATTERN_FAMILY", "LOW_ADVISORY", None, "Consider variety from different attested syntactic families; never force quota")
    return {"schema": "gcpk-source-first-combination-diagnostic@1.2.0", "card_id": card_id,
            "diagnostic_only_not_stage4_acceptance": True, "original_card_untouched": True,
            "combinations_checked": len(combos), "distinct_kinds": sorted(kinds),
            "issues": issues, "counts_by_code": {code: sum(x["code"] == code for x in issues) for code in sorted({x["code"] for x in issues})}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--registered-sources", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        card = json.loads(args.input.read_text(encoding="utf-8"))
        registry = None
        if args.registered_sources:
            registry = {x["source_id"] for x in json.loads(args.registered_sources.read_text(encoding="utf-8"))["sources"] if x.get("approval_status") == "approved"}
        report = diagnostic(card, registry)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())