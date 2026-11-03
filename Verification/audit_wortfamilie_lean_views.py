#!/usr/bin/env python3
"""Optional read-only Wortfamilie cross-view diagnostic (NOT a new gate).

One Stage3 decision may have a visible Wortfamilie text list and/or typed
WORD_FAMILY relations. These are not guaranteed to be equivalent: only
resolved target IDs justify graph edges, whereas useful freeform visible
items need not have their own canonical target. Never auto-fabricate edges.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

REQUIRED = {"id", "front", "details", "custom_fields", "related"}
RELATION_FIELDS = ("canonical_relations", "vnext_relations")

def _unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("DUPLICATE_JSON_KEY:" + key)
        obj[key] = value
    return obj

def _decode(text, field):
    try:
        return json.loads(text, object_pairs_hook=_unique_pairs)
    except (ValueError, TypeError) as exc:
        raise ValueError("INVALID_JSON:" + field) from exc

def _items(row):
    sections = _decode(row["details"], "details")
    custom = _decode(row["custom_fields"], "custom_fields")
    related = _decode(row["related"], "related")
    if not isinstance(sections, list) or not isinstance(custom, dict) or not isinstance(related, list):
        raise ValueError("INVALID_CARD_STRUCTURE:" + row["id"])
    visible = []
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError("INVALID_DETAILS_ENTRY:" + row["id"])
        if str(section.get("title", "")).strip().casefold() != "wortfamilie":
            continue
        items = section.get("items", [])
        if not isinstance(items, list):
            raise ValueError("INVALID_WORTFAMILIE_VISIBLE_ITEMS:" + row["id"])
        visible.extend(items)
    relations = []
    for field in RELATION_FIELDS:
        entries = custom.get(field, [])
        if not isinstance(entries, list):
            raise ValueError("INVALID_RELATION_FIELD:" + field)
        for entry in entries:
            if isinstance(entry, dict) and str(entry.get("type", "")).strip().upper() == "WORD_FAMILY":
                relations.append((field, entry))
    for entry in related:
        if isinstance(entry, dict) and str(entry.get("relation_type", "")).strip().upper() == "WORD_FAMILY":
            relations.append(("related", entry))
    return visible, relations

def audit(rows, source_sha256, limit=12):
    if not rows:
        raise ValueError("EMPTY_CARD_UNIVERSE")
    ids = []
    for row in rows:
        if not REQUIRED.issubset(row):
            raise ValueError("MISSING_TSV_COLUMNS")
        cid = row.get("id")
        if not isinstance(cid, str) or not cid.strip() or cid in ids:
            raise ValueError("EMPTY_OR_DUPLICATE_ID")
        ids.append(cid)
    known = set(ids)
    summary = Counter()
    examples = {"relation_without_visible": [], "visible_without_relation": [],
                "target_outside_input": []}
    for row in rows:
        visible, relations = _items(row)
        vid = bool(visible)
        typed = bool(relations)
        summary["cards_total"] += 1
        summary["visible_entries"] += len(visible)
        summary["typed_entries_across_fields"] += len(relations)
        summary["visible_cards"] += bool(vid)
        summary["typed_cards"] += bool(typed)
        summary["both_cards"] += bool(vid and typed)
        summary["visible_only_cards"] += bool(vid and not typed)
        summary["typed_only_cards"] += bool(typed and not vid)
        summary["neither_cards"] += bool(not vid and not typed)
        if typed and not vid and len(examples["relation_without_visible"]) < limit:
            examples["relation_without_visible"].append({"id": row["id"], "front": row["front"]})
        if vid and not typed and len(examples["visible_without_relation"]) < limit:
            examples["visible_without_relation"].append({"id": row["id"], "front": row["front"]})
        for channel, relation in relations:
            target = relation.get("target_id")
            if isinstance(target, str) and target.strip():
                if target in known:
                    summary["references_in_input"] += 1
                else:
                    summary["references_outside_input"] += 1
                    if len(examples["target_outside_input"]) < limit:
                        examples["target_outside_input"].append({
                            "id": row["id"], "target_id": target, "channel": channel})
            else:
                summary["typed_entries_without_target_id"] += 1
    for key in ("cards_total","visible_entries","typed_entries_across_fields",
                "visible_cards","typed_cards","both_cards","visible_only_cards",
                "typed_only_cards","neither_cards","references_in_input",
                "references_outside_input","typed_entries_without_target_id"):
        summary.setdefault(key, 0)
    if summary["both_cards"] + summary["visible_only_cards"] + summary["typed_only_cards"] + summary["neither_cards"] != len(rows):
        raise ValueError("CARD_CLASSIFICATION_MISMATCH")
    return {"schema": "gcpk-lean-wortfamilie-view-audit@1.0",
            "status": "SCOPED_DIAGNOSTIC_NOT_STAGE_ACCEPTANCE",
            "authority_tsv_sha256": source_sha256,
            "counts": dict(summary),
            "review_candidates": examples,
            "interpretation": {
                "relation_without_visible": "Not automatically a bug; Wortnetz graph view and text Details are separate",
                "visible_without_relation": "Not automatically a bug; do not fabricate graph target IDs",
                "typed_entries_across_fields": "May duplicate canonical/vnext projection; NOT unique word-family count",
                "missing_family": "No quantity quota; CLOSED_NO_FORCE valid after one Stage3 review"},
            "changes_to_source": False, "new_mandatory_gate": False}

def read_tsv(raw):
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("INVALID_TSV_ENCODING") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t")
    if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
        raise ValueError("MISSING_TSV_COLUMNS")
    rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("INVALID_TSV_FIELD_COUNT")
    return rows

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--zip-member")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-cards", type=int)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.source.suffix.lower() == ".zip":
            if not args.zip_member:
                raise ValueError("EXACT_ZIP_MEMBER_REQUIRED")
            with zipfile.ZipFile(args.source) as archive:
                if archive.testzip() is not None:
                    raise ValueError("ZIP_CRC_FAILURE")
                raw = archive.read(args.zip_member)
        else:
            if args.zip_member:
                raise ValueError("ZIP_MEMBER_ONLY_FOR_ZIP")
            raw = args.source.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if args.expected_sha256 and digest != args.expected_sha256:
            raise ValueError("SOURCE_SHA256_MISMATCH")
        rows = read_tsv(raw)
        if args.expected_cards is not None and (args.expected_cards < 1 or len(rows) != args.expected_cards):
            raise ValueError("CARD_COUNT_MISMATCH")
        result = audit(rows, digest)
        output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            if args.out.resolve() == args.source.resolve():
                raise ValueError("OUTPUT_SOURCE_COLLISION")
            if args.out.exists():
                raise ValueError("OUTPUT_ALREADY_EXISTS")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding="utf-8")
        print(output, end="")
        return 0
    except (OSError, ValueError, KeyError, UnicodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "BLOCKED_INPUT_INTEGRITY", "error": str(exc)}), file=sys.stderr)
        return 3

if __name__ == "__main__":
    raise SystemExit(main())
