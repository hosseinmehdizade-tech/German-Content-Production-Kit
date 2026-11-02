#!/usr/bin/env python3
"""OP-02 nonactive READ-ONLY Stage5-to-view projection quality guard.

This is a physical-data gate only: NEVER a Stage4 approval, native DOM test,
or a mandate to add/delete/duplicate learner combinations.
"""
import argparse
import collections
import csv
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
    if any(isinstance(x, dict) and all(x.get(k) == entry[k] for k in
                                      ("de", "fa", "en")) for x in physical):
        found.append("PHYSICAL_OBJECT_RENDER_PAIRING_UNPROVEN")
    if len(found) > 1:
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
        if row["id"] in ids:
            raise ValueError("duplicate card id")
        ids.add(row["id"])
        custom = strict_json(row["custom_fields"])
        envelope = custom.get("kombinationen_v1")
        if isinstance(envelope, dict):
            items = envelope.get("items") or []
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
        for ordinal, entry in enumerate(items):
            results.append({"card_id": row["id"], "ordinal": ordinal,
                            "state": classify(entry, physical, envelope)})
    counts = dict(collections.Counter(x["state"] for x in results))
    unresolved = sum(v for k, v in counts.items() if k != "PHYSICAL_DE_FA_EN_STRING")
    return {"schema": "op02-readonly-source-to-view@1",
            "status": "SCOPED_PHYSICAL_ONLY" if unresolved == 0 else "BLOCKED_SOURCE_TO_VIEW_EVIDENCE",
            "total_source_items": len(results), "counts": counts,
            "unresolved_or_unproven": unresolved,
            "native_study_dom": "NOT_TESTED", "native_quick_dom": "NOT_TESTED",
            "stage4_approval": False, "stage6_pass": False, "stage7_pass": False,
            "items": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tsv", type=Path)
    args = parser.parse_args()
    with args.tsv.open(encoding="utf-8-sig", newline="") as handle:
        result = audit(csv.DictReader(handle, delimiter="\t"))
    print(json.dumps(result, ensure_ascii=False))
    return 2 if result["unresolved_or_unproven"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
