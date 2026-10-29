#!/usr/bin/env python3
"""OP-02 nonactive, read-only mixed Canonical -> lexical Import scope audit.

Deliberately WIP50 format-specific: do not treat a grammatical unit as a
vocabulary card or silently omit one of the 787 true lexical units.
Caller-supplied SHA pins are NOT authenticated CURRENT issuer evidence.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

SCHEMA = "gcpk-op02-wip50-mixed-scope-source-import@1"
SHA = re.compile(r"[0-9a-f]{64}\Z")
VOCABULARY_TYPES = {"verb": "Verb", "adjektiv": "Adjektiv"}
NONLEXICAL_TYPES = {"grammatische_struktur"}
MAX_CANONICAL = 64 * 1024 * 1024
MAX_IMPORT = 64 * 1024 * 1024
HEADER = ("id", "card_type", "domain", "category", "source", "level",
          "lesson", "deck", "front", "back", "front_label", "back_label",
          "front_lang", "back_lang", "typing_target", "examples", "related",
          "opposites", "details", "custom_fields", "tags", "notes", "order")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def object_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY:" + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("NONFINITE_JSON:" + value)


def full_unit_sha(unit: dict) -> str:
    payload = json.dumps(unit, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return sha256(payload)


def result(errors, *, ncanonical=0, nlexical=0, ngrammar=0,
           nimport=0, types=None, excluded=None, pins=None):
    return {
        "schema": SCHEMA,
        "status": ("BLOCKED_INVALID_MIXED_SCOPE" if errors else
                   "PASS_SCOPED_MIXED_ID_AND_BYTE_PARITY_ONLY"),
        "errors": sorted(set(errors)),
        "canonical_units": ncanonical,
        "lexical_units": nlexical,
        "nonlexical_grammar_units": ngrammar,
        "import_cards": nimport,
        "canonical_type_counts": types or {},
        "nonlexical_excluded_unit_proofs": excluded or [],
        "observed_file_sha256": pins or {},
        "import_order_and_identity_match": not bool(errors),
        "stage4_semantic_pass": False,
        "source_fidelity_verified": False,
        "issuer_authenticated": False,
        "production_authorized": False,
        "performed_writes": False,
        "limits": [
            "Only explicit WIP50 type vocabulary verb/adjektiv and grammar structure",
            "Externally supplied SHA256 values do not authenticate CURRENT issuer",
            "Equal IDs/order do not prove semantic fidelity of card fields",
            "No Stage4 review decisions, release rights or Stage5-7 authorization"
        ]
    }


def audit(canonical_raw: bytes, import_raw: bytes,
          expected_canonical_sha256: str, expected_import_sha256: str) -> dict:
    errors = []
    if not isinstance(canonical_raw, bytes) or not 0 < len(canonical_raw) <= MAX_CANONICAL:
        return result(["CANONICAL_BYTES_MISSING_OR_OVERSIZE"])
    if not isinstance(import_raw, bytes) or not 0 < len(import_raw) <= MAX_IMPORT:
        return result(["IMPORT_BYTES_MISSING_OR_OVERSIZE"])
    pins = {"canonical": sha256(canonical_raw), "import_tsv": sha256(import_raw)}
    for key, expected in (("canonical", expected_canonical_sha256),
                          ("import_tsv", expected_import_sha256)):
        if (not isinstance(expected, str) or not SHA.fullmatch(expected)
                or expected == "0" * 64 or pins[key] != expected):
            errors.append("UNTRUSTED_OR_MISMATCHED_PIN:" + key)
    if errors:
        return result(errors, pins=pins)
    try:
        payload = json.loads(canonical_raw.decode("utf-8-sig"),
                             object_pairs_hook=object_unique,
                             parse_constant=reject_constant)
        if not isinstance(payload, dict) or not isinstance(payload.get("learning_units"), list):
            raise ValueError("NOT_LEARNING_UNITS_CANONICAL")
        units = payload["learning_units"]
        if not units:
            raise ValueError("EMPTY_CANONICAL")
        counts = Counter()
        ids = set()
        lex_ids = []
        lex_cat = {}
        excluded = []
        for unit in units:
            if not isinstance(unit, dict):
                raise ValueError("NONOBJECT_CANONICAL_UNIT")
            uid, kind = unit.get("id"), unit.get("type")
            if not isinstance(uid, str) or not uid.strip() or uid in ids:
                raise ValueError("DUPLICATE_OR_INVALID_CANONICAL_ID")
            ids.add(uid)
            if not isinstance(kind, str) or kind not in set(VOCABULARY_TYPES) | NONLEXICAL_TYPES:
                raise ValueError("UNKNOWN_OR_MISSING_CANONICAL_TYPE:" + str(uid))
            counts[kind] += 1
            if kind in VOCABULARY_TYPES:
                lex_ids.append(uid)
                lex_cat[uid] = VOCABULARY_TYPES[kind]
            else:
                excluded.append({"id": uid, "type": kind,
                                 "canonical_unit_sha256": full_unit_sha(unit)})
        if not lex_ids:
            raise ValueError("NO_LEXICAL_UNITS")
        inp = csv.reader(io.StringIO(import_raw.decode("utf-8-sig"), newline=""),
                         delimiter="\t", strict=True)
        header = next(inp)
        if tuple(header) != HEADER:
            raise ValueError("WIP50_TSV_HEADER_MISMATCH")
        rows = list(inp)
        if any(len(row) != len(HEADER) for row in rows):
            raise ValueError("MALFORMED_IMPORT_TSV_ROW")
        id_idx = HEADER.index("id")
        category_idx = HEADER.index("category")
        card_type_idx = HEADER.index("card_type")
        imported_ids = [row[id_idx] for row in rows]
        if len(imported_ids) != len(set(imported_ids)):
            errors.append("DUPLICATE_IMPORTED_LEXICAL_ID")
        if imported_ids != lex_ids:
            errors.append("LEXICAL_ID_ORDER_OR_SET_DIFFERS_FROM_IMPORT")
        for row in rows:
            if row[card_type_idx] != "de-vocabulary":
                errors.append("NON_VOCABULARY_IMPORT_CARD")
            if row[id_idx] not in lex_cat:
                errors.append("IMPORT_REFERENCES_NONLEXICAL_OR_UNKNOWN_ID")
            elif row[category_idx] != lex_cat[row[id_idx]]:
                errors.append("IMPORT_LEXICAL_CATEGORY_MISMATCH")
        if not excluded:
            errors.append("WIP50_EXPECTED_EXPLICIT_NONLEXICAL_UNIT_MISSING")
        # This audit is specifically WIP50: ensure exactly one grammatical
        # structure remains in full Canonical, never in lexical TSV.
        if len(excluded) != 1 or counts["grammatische_struktur"] != 1:
            errors.append("WIP50_NONLEXICAL_SCOPE_UNEXPECTED")
        return result(errors, ncanonical=len(units), nlexical=len(lex_ids),
                      ngrammar=len(excluded), nimport=len(rows),
                      types=dict(sorted(counts.items())), excluded=excluded,
                      pins=pins)
    except (ValueError, TypeError, UnicodeError, csv.Error, StopIteration,
            RecursionError, OverflowError) as exc:
        return result(errors + ["MALFORMED_REAL_SOURCE_OR_TSV:" + str(exc)[:120]],
                      pins=pins)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--import-tsv", type=Path, required=True)
    parser.add_argument("--expected-canonical-sha256", required=True)
    parser.add_argument("--expected-import-sha256", required=True)
    args = parser.parse_args()
    try:
        data = audit(args.canonical.read_bytes(), args.import_tsv.read_bytes(),
                     args.expected_canonical_sha256, args.expected_import_sha256)
    except OSError as exc:
        data = result(["READ_ERROR:" + type(exc).__name__])
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if data["status"].startswith("PASS_SCOPED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
