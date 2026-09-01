#!/usr/bin/env python3
"""Fail-closed preflight for Menschen A1 v3.1.10 legacy recovery inputs.

This script does not repair content. It verifies that the complete legacy artifacts
needed by recover_legacy_enrichment.py are present as repository/workspace bytes
and match the independently discovered historical invariants.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

EXPECTED_DIFFS = {
    "part1": {
        "rows": 141,
        "changed_rows": 141,
        "changed_columns": {"NVV1": 141, "NVV2": 141, "NVV3": 118},
        "expected_first_id": "MEN-A1-0001",
    },
    "part2": {
        "rows": 135,
        "changed_rows": 135,
        "changed_columns": {"NVV1": 135, "NVV2": 135, "NVV3": 135},
        "expected_first_id": "MEN-A1-0142",
    },
}

HEADWORD_COLUMNS = ("infinitive_display", "lemma", "german")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_diff(path: Path, spec: dict, label: str):
    errors = []
    if not path.is_file():
        return [f"{label}: missing file: {path}"]
    try:
        data = load_json(path)
    except Exception as exc:
        return [f"{label}: invalid JSON: {exc}"]

    if data.get("mode") != "diff" or data.get("phase") != 4:
        errors.append(f"{label}: expected mode=diff and phase=4")
    if data.get("data_rows") != spec["rows"]:
        errors.append(f"{label}: data_rows={data.get('data_rows')!r}, expected {spec['rows']}")
    if data.get("changed_rows") != spec["changed_rows"]:
        errors.append(f"{label}: changed_rows={data.get('changed_rows')!r}, expected {spec['changed_rows']}")

    changed = data.get("changed_columns") or {}
    for key, expected in spec["changed_columns"].items():
        if changed.get(key) != expected:
            errors.append(f"{label}: changed_columns[{key}]={changed.get(key)!r}, expected {expected}")

    issues = data.get("issues")
    if not isinstance(issues, list) or not issues:
        errors.append(f"{label}: issues must be a non-empty list")
    else:
        allowed = [x for x in issues if x.get("code") == "ALLOWED_CHANGE"]
        if not allowed:
            errors.append(f"{label}: no ALLOWED_CHANGE records found")
        first_ids = [x.get("card_id") for x in allowed if x.get("card_id")]
        if first_ids and spec.get("expected_first_id") not in first_ids:
            errors.append(f"{label}: expected evidence for {spec['expected_first_id']} not found")
        for x in allowed:
            if x.get("column") in {"NVV1", "NVV2", "NVV3", "NVV4", "NVV5", "NVV6"}:
                if not str(x.get("new_value", "")).strip() or x.get("new_value") == "—":
                    errors.append(f"{label}: empty/absent NVV ALLOWED_CHANGE for {x.get('card_id')}")
                    break
    return errors


def verify_legacy_cards(path: Path):
    errors = []
    metrics = {}
    if not path.is_file():
        return [f"legacy-cards: missing file: {path}"], metrics
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            header = reader.fieldnames or []
            if "id" not in header:
                errors.append("legacy-cards: missing id column")
            head_col = next((c for c in HEADWORD_COLUMNS if c in header), None)
            if not head_col:
                errors.append(f"legacy-cards: needs one headword column from {HEADWORD_COLUMNS}")
            ids = []
            nonempty_headwords = 0
            duplicate_ids = set()
            seen = set()
            for row in reader:
                cid = (row.get("id") or "").strip()
                if not cid:
                    errors.append("legacy-cards: empty id encountered")
                    continue
                if cid in seen:
                    duplicate_ids.add(cid)
                seen.add(cid)
                ids.append(cid)
                if head_col and (row.get(head_col) or "").strip():
                    nonempty_headwords += 1
            metrics = {
                "rows": len(ids),
                "unique_ids": len(seen),
                "duplicate_ids": sorted(duplicate_ids),
                "headword_column": head_col,
                "nonempty_headwords": nonempty_headwords,
            }
            if len(ids) != 276:
                errors.append(f"legacy-cards: expected 276 rows, found {len(ids)}")
            if len(seen) != 276:
                errors.append(f"legacy-cards: expected 276 unique IDs, found {len(seen)}")
            if duplicate_ids:
                errors.append(f"legacy-cards: duplicate IDs: {sorted(duplicate_ids)[:10]}")
            if head_col and nonempty_headwords != 276:
                errors.append(f"legacy-cards: expected 276 non-empty {head_col} values, found {nonempty_headwords}")
    except Exception as exc:
        errors.append(f"legacy-cards: unreadable TSV: {exc}")
    return errors, metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part1", required=True, type=Path)
    ap.add_argument("--part2", required=True, type=Path)
    ap.add_argument("--legacy-cards", required=True, type=Path)
    ap.add_argument("--report", type=Path)
    ns = ap.parse_args()

    errors = []
    errors += verify_diff(ns.part1, EXPECTED_DIFFS["part1"], "part1")
    errors += verify_diff(ns.part2, EXPECTED_DIFFS["part2"], "part2")
    legacy_errors, legacy_metrics = verify_legacy_cards(ns.legacy_cards)
    errors += legacy_errors

    report = {
        "gate": "MENSCHEN_A1_V3_1_10_RECOVERY_INPUT_PREFLIGHT",
        "status": "PASS" if not errors else "FAIL",
        "inputs": {
            "part1": str(ns.part1),
            "part2": str(ns.part2),
            "legacy_cards": str(ns.legacy_cards),
        },
        "expected": EXPECTED_DIFFS,
        "legacy_metrics": legacy_metrics,
        "errors": errors,
        "next_action": "Run recover_legacy_enrichment.py only after PASS." if not errors else "Do not run canonical mutation; supply/fix complete recovery inputs.",
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if ns.report:
        ns.report.parent.mkdir(parents=True, exist_ok=True)
        ns.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
