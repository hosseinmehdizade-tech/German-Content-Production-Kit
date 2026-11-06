#!/usr/bin/env python3
"""Read-only audit of learner-visible morphology detail titles.

Only details[].title is governed. canonical_unit.morphology is allowed.
No source, card, or user study state mutation.
"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import sys
import zipfile
from collections import Counter

FORBIDDEN = {"morphologie", "morphology"}


def read_cards(source, member=None):
    file = pathlib.Path(source)
    raw = file.read_bytes()
    selected = None
    if file.suffix.lower() == ".zip":
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError("ZIP CRC failure: " + bad)
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError("duplicate ZIP member paths")
            if member:
                if member not in names:
                    raise ValueError("missing ZIP member " + member)
                selected = member
            else:
                eligible = [name for name in names if (name.startswith("01-Content/") or "/" not in name)
                            and name.lower().endswith((".tsv", ".csv"))]
                matches = [name for name in eligible if name.lower().endswith(("cards.tsv", "cards.csv"))]
                if len(matches) != 1:
                    raise ValueError("ambiguous card file; provide --member")
                selected = matches[0]
            raw = archive.read(selected)
    elif member:
        raise ValueError("--member is only valid with ZIP")
    delim = "\t" if (selected or file.name).lower().endswith(".tsv") else ","
    cards = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter=delim))
    if not cards or not {"id", "details"}.issubset(cards[0]):
        raise ValueError("missing card id/details")
    return cards, hashlib.sha256(raw).hexdigest(), selected


def audit(cards):
    result = {"cards": len(cards), "visible_morphologie_sections": 0,
              "affected_card_ids": [], "standard_formen_sections": 0,
              "internal_morphology_metadata_cards": 0, "invalid_details_ids": [],
              "full_front_formen_exact_duplicate_advisories": []}
    ids = set()
    titles = Counter()
    for row in cards:
        card_id = row.get("id", "")
        if not card_id or card_id in ids:
            raise ValueError("empty or duplicate card ID: " + card_id)
        ids.add(card_id)
        try:
            details = json.loads(row.get("details") or "[]")
        except ValueError:
            details = None
        if not isinstance(details, list):
            result["invalid_details_ids"].append(card_id)
            continue
        for section in details:
            if not isinstance(section, dict) or not isinstance(section.get("title"), str) or not isinstance(section.get("items"), list):
                result["invalid_details_ids"].append(card_id)
                continue
            label = " ".join(section["title"].casefold().split())
            titles[label] += 1
            if label in FORBIDDEN:
                result["visible_morphologie_sections"] += 1
                result["affected_card_ids"].append(card_id)
            if label == "formen":
                result["standard_formen_sections"] += 1
                if any(isinstance(item, str) and " ".join(item.split()) == " ".join((row.get("front") or "").split()) for item in section["items"]):
                    result["full_front_formen_exact_duplicate_advisories"].append(card_id)
        try:
            custom = json.loads(row.get("custom_fields") or "{}")
        except ValueError:
            custom = {}
        unit = custom.get("canonical_unit") if isinstance(custom, dict) else None
        if isinstance(unit, dict) and any(key in unit for key in ("morphology", "forms")):
            result["internal_morphology_metadata_cards"] += 1
    result["affected_card_ids"] = sorted(set(result["affected_card_ids"]))
    result["invalid_details_ids"] = sorted(set(result["invalid_details_ids"]))
    result["full_front_formen_exact_duplicate_advisories"] = sorted(set(result["full_front_formen_exact_duplicate_advisories"]))
    result["title_counts"] = dict(sorted(titles.items()))
    result["status"] = "HOLD_VISIBLE_MORPHOLOGIE" if result["visible_morphologie_sections"] else "PASS_NO_STANDALONE_MORPHOLOGIE"
    return result


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--member")
    p.add_argument("--fail-on-morphologie", action="store_true")
    p.add_argument("--output")
    args = p.parse_args(argv)
    try:
        cards, digest, member = read_cards(args.file, args.member)
        report = audit(cards)
        report["selected_card_payload_sha256"] = digest
        report["selected_member"] = member
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            out = pathlib.Path(args.output)
            if out.exists():
                raise ValueError("refuse to overwrite report " + str(out))
            out.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        if report["invalid_details_ids"]:
            return 2
        return 1 if args.fail_on_morphologie and report["visible_morphologie_sections"] else 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
        print("MORPHOLOGY_AUDIT_ERROR: " + str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
