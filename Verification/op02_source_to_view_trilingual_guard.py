#!/usr/bin/env python3
"""OP-02 nonactive READ-ONLY Stage5-to-view projection quality guard.

This is a physical-data gate only: NEVER a Stage4 approval, native DOM test,
or a mandate to add/delete/duplicate learner combinations.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path


def strict_json(text):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs)


def classify(entry, physical, envelope):
    if not isinstance(entry, dict) or any(
        not isinstance(entry.get(k), str) or not entry[k].strip()
        for k in ("de", "fa", "en")
    ):
        raise ValueError("missing source DE/FA/EN")
    de, fa, en = (entry[k] for k in ("de", "fa", "en"))
    found = []
    if f"{de} — {fa} — {en}" in physical:
        found.append("PHYSICAL_DE_FA_EN_STRING")
    if f"{de} — {fa}" in physical:
        found.append("PHYSICAL_DE_FA_ONLY")
    object_matches = sum(isinstance(x, dict) and all(x.get(k) == entry[k] for k in
                                      ("de", "fa", "en")) for x in physical)
    if object_matches:
        found.append("PHYSICAL_OBJECT_RENDER_PAIRING_UNPROVEN")
    if len(found) > 1 or object_matches > 1 or sum(x == f"{de} — {fa} — {en}" for x in physical) > 1 or sum(x == f"{de} — {fa}" for x in physical) > 1:
        raise ValueError("ambiguous duplicate representations")
    if found:
        return found[0]
    if physical:
        return "PARTIAL_SECTION_PREEMPTED"
    if isinstance(envelope, dict) and str(envelope.get("visible_section", "")).casefold() == "kombinationen":
        return "BRIDGE_DE_FA_ONLY_DOM_UNPROVEN"
    return "NO_VERIFIED_PROJECTION"


def audit(rows):
    results = []
    ids = set()
    for row in rows:
        if not isinstance(row.get("id"), str) or not row["id"].strip():
            raise ValueError("missing or empty card id")
        if row["id"] in ids:
            raise ValueError("duplicate card id")
        ids.add(row["id"])
        custom = strict_json(row["custom_fields"])
        if not isinstance(custom, dict):
            raise ValueError("custom_fields must be an object")
        envelope = custom.get("kombinationen_v1")
        if isinstance(envelope, dict):
            items = envelope.get("items", [])
        elif isinstance(envelope, list):
            items = envelope
        elif envelope is None:
            continue
        else:
            raise ValueError("invalid combination envelope")
        if not isinstance(items, list):
            raise ValueError("combination items not a list")
        sections = strict_json(row["details"])
        if not isinstance(sections, list):
            raise ValueError("details not a list")
        physical_sections = [x for x in sections if isinstance(x, dict)
                             and str(x.get("title", "")).casefold() == "kombinationen"]
        if len(physical_sections) > 1:
            raise ValueError("ambiguous combination sections")
        physical = physical_sections[0].get("items", []) if physical_sections else []
        if not isinstance(physical, list):
            raise ValueError("physical section not an array")
        source_triplets = set()
        for ordinal, entry in enumerate(items):
            if not isinstance(entry, dict) or any(not isinstance(entry.get(lang), str) or not entry[lang].strip() for lang in ("de", "fa", "en")):
                raise ValueError("invalid source trilingual combination")
            triplet = tuple(entry[lang] for lang in ("de", "fa", "en"))
            if triplet in source_triplets:
                raise ValueError("duplicate exact trilingual source item on card")
            source_triplets.add(triplet)
            results.append({"card_id": row["id"], "ordinal": ordinal,
                            "state": classify(entry, physical, envelope)})
    counts = dict(collections.Counter(x["state"] for x in results))
    unresolved = sum(v for k, v in counts.items() if k != "PHYSICAL_DE_FA_EN_STRING")
    if not results:
        status = "BLOCKED_EMPTY_SOURCE_UNIVERSE"
    else:
        status = "SCOPED_PHYSICAL_ONLY" if unresolved == 0 else "BLOCKED_SOURCE_TO_VIEW_EVIDENCE"
    return {"schema": "op02-readonly-source-to-view@1",
            "status": status, "total_cards": len(ids),
            "total_source_items": len(results), "counts": counts,
            "unresolved_or_unproven": unresolved,
            "native_study_dom": "NOT_TESTED", "native_quick_dom": "NOT_TESTED",
            "stage4_approval": False, "stage6_pass": False, "stage7_pass": False,
            "items": results}


def verify_bytes(raw, expected_sha256):
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError("exact TSV sha256 mismatch")
    return digest


def main(argv=None):
    parser = argparse.ArgumentParser(description="Nonactive read-only physical Stage5-to-view guard; not Stage6")
    parser.add_argument("tsv", type=Path)
    parser.add_argument("--expected-sha256", required=True, help="Exact vetted TSV-byte SHA256")
    parser.add_argument("--expected-cards", type=int, required=True)
    parser.add_argument("--expected-items", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        if args.expected_cards <= 0 or args.expected_items <= 0:
            raise ValueError("expected counts must be positive")
        raw = args.tsv.read_bytes()
        digest = verify_bytes(raw, args.expected_sha256)
        rows = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), delimiter="\t")
        result = audit(rows)
        if result["total_cards"] != args.expected_cards or result["total_source_items"] != args.expected_items:
            raise ValueError("exact source-universe count mismatch")
        result["authority_tsv_sha256"] = digest
    except (ValueError, KeyError, TypeError, UnicodeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"status":"BLOCKED_INTEGRITY", "error":str(error)}), file=__import__("sys").stderr)
        return 3
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "SCOPED_PHYSICAL_ONLY" else 2

if __name__ == "__main__":
    raise SystemExit(main())
