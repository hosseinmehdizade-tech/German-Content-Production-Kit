#!/usr/bin/env python3
"""Fail-closed recovery of Menschen A1 legacy enrichment candidates.

This tool intentionally DOES NOT call legacy NVV columns canonical Nomen-Verb-
Verbindungen or collocations. It extracts candidates, resolves legacy identity
against a legacy card/headword source, and emits a review queue. Canonical
mutation is only allowed with an explicit classification/evidence decisions file.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ABSENT = {"", "—", "-", None}
ALLOWED_KINDS = {
    "collocation", "nvv", "pattern", "fixed_expression",
    "prepositional_pattern", "common_combination", "other"
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_headword(text: str) -> str:
    text = (text or "").strip().casefold()
    text = text.replace("jdn.", "jemanden").replace("jdm.", "jemandem").replace("etw.", "etwas")
    text = re.sub(r"\s+", " ", text)
    return text


def parse_legacy_diff(path: Path):
    data = load_json(path)
    by_id = defaultdict(dict)
    for item in data.get("issues", []):
        if item.get("code") != "ALLOWED_CHANGE":
            continue
        card_id = item.get("card_id")
        col = item.get("column")
        val = item.get("new_value")
        if card_id and col and val not in ABSENT:
            by_id[card_id][col] = val
    return by_id


def read_legacy_cards(path: Path):
    """Read a legacy TSV carrying at least id and a headword-bearing column.

    Supported preferred columns: infinitive_display, lemma, german.
    The full legacy file is used for semantic identity only; no row-order mapping.
    """
    out = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            cid = (row.get("id") or "").strip()
            head = (row.get("infinitive_display") or row.get("lemma") or row.get("german") or "").strip()
            if cid and head:
                out[cid] = {"headword_raw": head, "headword_norm": normalize_headword(head)}
    return out


def canonical_index(dataset):
    by_exact = defaultdict(list)
    for unit in dataset.get("learning_units", []):
        by_exact[normalize_headword(unit.get("headword", ""))].append(unit)
    return by_exact


def extract_candidates(diff_paths, legacy_cards, canonical):
    merged = {}
    for p in diff_paths:
        for cid, cols in parse_legacy_diff(p).items():
            merged.setdefault(cid, {}).update(cols)

    cidx = canonical_index(canonical)
    queue = []
    for legacy_id, cols in sorted(merged.items()):
        legacy = legacy_cards.get(legacy_id)
        if not legacy:
            queue.append({
                "legacy_id": legacy_id, "status": "BLOCKED_NO_LEGACY_HEADWORD",
                "candidates": [cols.get(f"NVV{i}") for i in range(1, 7) if cols.get(f"NVV{i}") not in ABSENT]
            })
            continue
        matches = cidx.get(legacy["headword_norm"], [])
        candidates = [cols.get(f"NVV{i}") for i in range(1, 7) if cols.get(f"NVV{i}") not in ABSENT]
        if len(matches) != 1:
            queue.append({
                "legacy_id": legacy_id, "legacy_headword": legacy["headword_raw"],
                "status": "REVIEW_IDENTITY_AMBIGUOUS" if matches else "REVIEW_IDENTITY_NOT_FOUND",
                "canonical_candidates": [u.get("id") for u in matches], "candidates": candidates
            })
            continue
        u = matches[0]
        queue.append({
            "legacy_id": legacy_id, "legacy_headword": legacy["headword_raw"],
            "canonical_id": u.get("id"), "canonical_headword": u.get("headword"),
            "status": "CLASSIFICATION_REQUIRED", "candidates": candidates,
            "legacy_synonyms": [cols.get("synonym1"), cols.get("synonym2")],
            "legacy_antonyms": [cols.get("antonym1"), cols.get("antonym2")]
        })
    return queue


def validate_decisions(queue, decisions):
    qmap = {x.get("canonical_id"): x for x in queue if x.get("canonical_id")}
    errors = []
    for d in decisions:
        cid = d.get("canonical_id")
        if cid not in qmap:
            errors.append(f"Unknown/unresolved canonical_id in decisions: {cid}")
            continue
        for c in d.get("connections", []):
            if c.get("kind") not in ALLOWED_KINDS:
                errors.append(f"{cid}: invalid connection kind {c.get('kind')!r}")
            if not str(c.get("text", "")).strip():
                errors.append(f"{cid}: empty connection text")
            if not c.get("evidence"):
                errors.append(f"{cid}: connection {c.get('text')!r} lacks evidence binding")
    return errors


def apply_decisions(canonical, decisions):
    by_id = {u.get("id"): u for u in canonical.get("learning_units", [])}
    for d in decisions:
        u = by_id[d["canonical_id"]]
        existing = {(x.get("kind"), x.get("text")) for x in u.get("connections", []) if isinstance(x, dict)}
        conns = list(u.get("connections", []))
        for c in d.get("connections", []):
            key = (c["kind"], c["text"])
            if key not in existing:
                conns.append({"kind": c["kind"], "text": c["text"]})
                existing.add(key)
        if conns:
            u["connections"] = conns
        # Evidence is appended as explicit recovery provenance, never rewritten as live dictionary evidence.
        if d.get("connections"):
            sources = u.setdefault("provenance", {}).setdefault("sources", [])
            claims = sorted({"collocation" if c["kind"] == "collocation" else "usage" for c in d["connections"]})
            sources.append({
                "source_id": "legacy_menschen_a1_enrichment_recovery",
                "source_kind": "legacy_audit_artifact",
                "what_was_verified": claims,
                "verification_status": "verified",
                "locator": d.get("evidence_locator", "legacy-recovery://explicit-decision"),
                "evidence_note": "Recovered from legacy enrichment only after semantic identity resolution and explicit current-schema classification."
            })
    return canonical


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", required=True, type=Path)
    ap.add_argument("--legacy-cards", required=True, type=Path)
    ap.add_argument("--legacy-diff", action="append", required=True, type=Path)
    ap.add_argument("--queue", required=True, type=Path)
    ap.add_argument("--decisions", type=Path)
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()

    canonical = load_json(ns.canonical)
    legacy_cards = read_legacy_cards(ns.legacy_cards)
    queue = extract_candidates(ns.legacy_diff, legacy_cards, canonical)
    ns.queue.parent.mkdir(parents=True, exist_ok=True)
    ns.queue.write_text(json.dumps({"status": "REVIEW_REQUIRED", "items": queue}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not ns.decisions:
        print(f"Review queue written: {ns.queue}")
        return 1
    if not ns.output:
        ap.error("--output is required with --decisions")
    decisions_data = load_json(ns.decisions)
    decisions = decisions_data.get("decisions", decisions_data if isinstance(decisions_data, list) else [])
    errors = validate_decisions(queue, decisions)
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
        return 2
    repaired = apply_decisions(canonical, decisions)
    ns.output.write_text(json.dumps(repaired, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Candidate canonical written: {ns.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
