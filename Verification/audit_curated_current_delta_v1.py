#!/usr/bin/env python3
"""Read-only current-vs-immediate-curated-parent delta audit; never compares to raw textbook.

Only structural/decision evidence. It does NOT certify linguistic Stage4, importer
Stage5, browser Stage6, release Stage7, source authenticity or user authorization.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

MAX_BYTES = 50_000_000
APPROVED = {"USER_APPROVED", "REVIEWED_CURATED"}


class DeltaError(ValueError):
    pass


def strict_object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DeltaError("DUPLICATE_JSON_KEY:" + key)
        result[key] = value
    return result


def read_blob(path):
    p = Path(path)
    if not p.is_file() or p.is_symlink():
        raise DeltaError("CURRENT_OR_PARENT_UNREADABLE")
    if p.stat().st_size > MAX_BYTES:
        raise DeltaError("INPUT_TOO_LARGE_FOR_SCOPED_TOOL")
    return p.read_bytes()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def records(blob, suffix, id_column="id"):
    try:
        data = blob.decode("utf-8-sig")
    except UnicodeError as exc:
        raise DeltaError("NON_UTF8_INPUT") from exc
    if suffix.lower() == ".json":
        obj = json.loads(data, object_pairs_hook=strict_object_pairs)
        rows = obj.get("cards") if isinstance(obj, dict) else obj
        if not isinstance(rows, list):
            raise DeltaError("JSON_MUST_HAVE_CARDS_LIST")
    elif suffix.lower() in (".tsv", ".csv"):
        sep = "\t" if suffix.lower() == ".tsv" else ","
        f = io.StringIO(data, newline="")
        rd = csv.DictReader(f, delimiter=sep, strict=True)
        cols = rd.fieldnames
        if not cols or not all(cols) or len(set(cols)) != len(cols):
            raise DeltaError("INVALID_OR_DUPLICATE_HEADER")
        if id_column not in cols:
            raise DeltaError("MISSING_ID_COLUMN")
        rows = list(rd)
        if any(None in row or any(key is None for key in row) for row in rows):
            raise DeltaError("MALFORMED_TABULAR_ROW")
    else:
        raise DeltaError("UNSUPPORTED_FORMAT_EXPECT_JSON_CSV_TSV")
    index = {}
    for row in rows:
        if not isinstance(row, dict):
            raise DeltaError("NONOBJECT_ROW")
        idval = row.get(id_column)
        if not isinstance(idval, str) or not idval.strip() or idval != idval.strip():
            raise DeltaError("EMPTY_OR_UNSTABLE_ID")
        if idval in index:
            raise DeltaError("DUPLICATE_ID:" + idval)
        index[idval] = row
    return index


def decisions_from_bytes(blob):
    obj = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object_pairs)
    if not isinstance(obj, dict) or not isinstance(obj.get("decisions"), dict):
        raise DeltaError("DECISIONS_MUST_BE_OBJECT")
    return obj["decisions"]


def analyze(current, predecessor=None, decisions=None):
    """Operate on **already parsed verified** owner-local curated records."""
    if predecessor is None:
        return {"status": "BASELINE_STRUCTURAL_PASS_NOT_SEMANTIC", "current_count": len(current),
                "added": [], "removed": [], "modified": [], "unchanged": len(current),
                "decision_holds": [], "review_scope": [],
                "original_book_row_equality_required": False}
    before, after = set(predecessor), set(current)
    added = sorted(after - before)
    removed = sorted(before - after)
    modified = sorted(i for i in (before & after) if current[i] != predecessor[i])
    unchanged = len(before & after) - len(modified)
    d = decisions or {}
    holds = []
    for card_id in removed:
        item = d.get(card_id)
        if not (isinstance(item, dict) and item.get("operation") == "REMOVED"
                and item.get("disposition") in APPROVED
                and isinstance(item.get("reason"), str) and item["reason"].strip()):
            holds.append(card_id)
    return {"status": "HOLD_REMOVAL_DECISION" if holds else "DELTA_STRUCTURAL_PASS_NOT_SEMANTIC",
            "current_count": len(current), "previous_count": len(predecessor),
            "added": added, "removed": removed, "modified": modified,
            "unchanged": unchanged, "decision_holds": holds,
            "review_scope": sorted(set(added + modified + removed)),
            "original_book_row_equality_required": False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--current", required=True)
    p.add_argument("--expected-current-sha256", required=True)
    p.add_argument("--previous-curated", help="immediate accepted predecessor, NEVER raw textbook")
    p.add_argument("--expected-previous-sha256")
    p.add_argument("--decisions", help="optional JSON {decisions:{id:{operation,disposition,reason}}}")
    p.add_argument("--id-column", default="id")
    a = p.parse_args(argv)
    try:
        if bool(a.previous_curated) != bool(a.expected_previous_sha256):
            raise DeltaError("PREVIOUS_PATH_AND_SHA_REQUIRED_TOGETHER")
        cdata = read_blob(a.current)
        if digest(cdata) != a.expected_current_sha256:
            raise DeltaError("CURRENT_HASH_MISMATCH")
        current = records(cdata, Path(a.current).suffix, a.id_column)
        prev = None
        if a.previous_curated:
            if Path(a.current).resolve() == Path(a.previous_curated).resolve():
                raise DeltaError("CURRENT_AND_PREVIOUS_SAME_FILE")
            pdata = read_blob(a.previous_curated)
            if digest(pdata) != a.expected_previous_sha256:
                raise DeltaError("PREVIOUS_HASH_MISMATCH")
            prev = records(pdata, Path(a.previous_curated).suffix, a.id_column)
        decisions = decisions_from_bytes(read_blob(a.decisions)) if a.decisions else {}
        result = analyze(current, prev, decisions)
        result.update({"current_sha256": digest(cdata),
                       "predecessor_sha256": digest(pdata) if prev is not None else None,
                       "source_mode": "CURATED_BASELINE_ONLY" if prev is None
                           else "CURRENT_VS_IMMEDIATE_CURATED_PARENT",
                       "full_language_qa_stage4": "NOT_EVALUATED",
                       "runtime_stage6": "NOT_EVALUATED"})
        print(json.dumps(result, ensure_ascii=False))
        return 2 if result["decision_holds"] else 0
    except (DeltaError, ValueError, csv.Error, UnicodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
