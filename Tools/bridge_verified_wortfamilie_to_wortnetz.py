#!/usr/bin/env python3
"""Reuse VERIFIED Stage3 Wortfamilie decisions to author canonical WORD_FAMILY graph edges.

The normal v411 projector already maps canonical relations to vnext_relations,
and Wortnetz already consumes WORD_FAMILY. This opt-in writer creates a NEW
canonical successor, never edits historical source, learner cards or the app.
Unresolved text remains text; no fuzzy lookup or invented reverse edge.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

LEDGER_SCHEMA = "gcpk-stage3-onepass@1.0"
HASH = re.compile(r"[0-9a-f]{64}\Z")
GERMAN_ARTICLE = re.compile(r"^(?:der|die|das)\s+", re.I)
ALLOWED_TARGETS = ("senses", "expressions")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("DUPLICATE_JSON_KEY:" + key)
        obj[key] = value
    return obj


def load_json(data: bytes, description: str):
    try:
        return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_pairs)
    except (UnicodeError, ValueError, TypeError) as exc:
        raise ValueError("INVALID_JSON:" + description) from exc


def lexical_surface(value) -> str:
    if not isinstance(value, str):
        return ""
    normalized = " ".join(value.strip().casefold().replace("ß", "ss").split())
    return GERMAN_ARTICLE.sub("", normalized)


def target_registry(registry):
    if not isinstance(registry, dict):
        raise ValueError("CANONICAL_NOT_OBJECT")
    lexemes = registry.get("lexemes", [])
    if not isinstance(lexemes, list):
        raise ValueError("INVALID_LEXEMES")
    lexicon = {}
    for item in lexemes:
        if not isinstance(item, dict) or not isinstance(item.get("lexeme_id"), str):
            raise ValueError("INVALID_LEXEME")
        if item["lexeme_id"] in lexicon:
            raise ValueError("DUPLICATE_LEXEME_ID")
        lexicon[item["lexeme_id"]] = item

    targets = {}
    for collection, key, typ in (("senses", "sense_id", "sense"), 
                                 ("expressions", "expression_id", "expression")):
        rows = registry.get(collection, [])
        if not isinstance(rows, list):
            raise ValueError("INVALID_TARGET_COLLECTION:" + collection)
        for item in rows:
            if not isinstance(item, dict) or not isinstance(item.get(key), str) or not item[key]:
                raise ValueError("INVALID_TARGET_ID:" + collection)
            tid = item[key]
            if tid in targets:
                raise ValueError("DUPLICATE_CANONICAL_TARGET_ID:" + tid)
            if typ == "sense":
                lemma = lexicon.get(item.get("lexeme_id"), {}).get("lemma", "")
            else:
                lemma = item.get("canonical_form", "")
            if not isinstance(lemma, str) or not lemma.strip():
                raise ValueError("MISSING_CANONICAL_TARGET_LEMMA:" + tid)
            targets[tid] = {"type": typ, "de": lemma,
                            "fa": (item.get("translations") or {}).get("fa", "")}
    sources = registry.get("sources", [])
    if not isinstance(sources, list) or any(
            not isinstance(src, dict) or not isinstance(src.get("source_id"), str)
            for src in sources):
        raise ValueError("INVALID_CANONICAL_SOURCES")
    source_ids = [src["source_id"] for src in sources]
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("DUPLICATE_SOURCE_ID")
    relations = registry.get("relations", [])
    if not isinstance(relations, list):
        raise ValueError("INVALID_CANONICAL_RELATIONS")
    used_ids = {}
    existing_pairs = set()
    for relation in relations:
        if not isinstance(relation, dict):
            raise ValueError("INVALID_CANONICAL_RELATION")
        rid = relation.get("relation_id")
        if not isinstance(rid, str) or not rid or rid in used_ids:
            raise ValueError("EMPTY_OR_DUPLICATE_RELATION_ID")
        used_ids[rid] = relation
        if relation.get("relation_type") == "WORD_FAMILY":
            existing_pairs.add((relation.get("source_id"), relation.get("target_id")))
    return targets, set(source_ids), used_ids, existing_pairs


def apply_bridge(canonical: dict, ledger: dict, canonical_bytes: bytes):
    if not isinstance(ledger, dict) or ledger.get("schema") != LEDGER_SCHEMA:
        raise ValueError("UNSUPPORTED_STAGE3_LEDGER")
    if ledger.get("working_sha256") != digest(canonical_bytes):
        raise ValueError("EXACT_WORKING_CANONICAL_SHA_MISMATCH")
    source_hash = ledger.get("registered_source_sha256")
    if not isinstance(source_hash, str) or not HASH.fullmatch(source_hash):
        raise ValueError("STAGE3_SOURCE_AUTHORITY_NOT_PINNED")
    if not isinstance(ledger.get("cards"), list) or not ledger["cards"]:
        raise ValueError("EMPTY_STAGE3_LEDGER")
    targets, sources, used_ids, pairs = target_registry(canonical)
    new = copy.deepcopy(canonical)
    new.setdefault("relations", [])
    count = {"decisions_seen": 0, "candidate_members": 0, "edges_added": 0,
             "existing_edges_reused": 0, "unresolved_target": 0,
             "unreviewed_member": 0, "no_registered_evidence": 0,
             "unmatched_german_target": 0, "self_link_rejected": 0,
             "nonverified_family_decisions": 0}
    seen = set()
    for card in ledger["cards"]:
        if not isinstance(card, dict) or not isinstance(card.get("id"), str) or not card["id"]:
            raise ValueError("INVALID_STAGE3_CARD")
        uid = card["id"]
        if uid in seen:
            raise ValueError("DUPLICATE_STAGE3_CARD:" + uid)
        seen.add(uid)
        if uid not in targets:
            raise ValueError("STAGE3_SOURCE_NOT_IN_CANONICAL:" + uid)
        decisions = card.get("decisions", {})
        if not isinstance(decisions, dict):
            raise ValueError("INVALID_STAGE3_DECISIONS:" + uid)
        decision = decisions.get("word_family", decisions.get("wortfamilie"))
        if decision is None:
            continue
        if not isinstance(decision, dict):
            raise ValueError("INVALID_FAMILY_DECISION:" + uid)
        count["decisions_seen"] += 1
        if decision.get("decision") != "VERIFIED_PRESENT":
            count["nonverified_family_decisions"] += 1
            continue
        members = decision.get("members", [])
        if not isinstance(members, list):
            raise ValueError("INVALID_FAMILY_MEMBERS:" + uid)
        for member in members:
            count["candidate_members"] += 1
            if not isinstance(member, dict):
                raise ValueError("INVALID_FAMILY_MEMBER:" + uid)
            if member.get("decision", "VERIFIED_PRESENT") != "VERIFIED_PRESENT":
                count["unreviewed_member"] += 1
                continue
            tid = member.get("target_id")
            if not isinstance(tid, str) or tid not in targets:
                count["unresolved_target"] += 1
                continue
            if tid == uid:
                count["self_link_rejected"] += 1
                continue
            surface = member.get("de")
            if not lexical_surface(surface) or lexical_surface(surface) != lexical_surface(targets[tid]["de"]):
                count["unmatched_german_target"] += 1
                continue
            evidence = member.get("provenance", decision.get("provenance"))
            refs = evidence.get("source_refs") if isinstance(evidence, dict) else None
            if not isinstance(refs, list) or not refs or any(
                    not isinstance(x, dict) or
                    not isinstance(x.get("source_id"), str) or
                    x["source_id"] not in sources
                    for x in refs):
                count["no_registered_evidence"] += 1
                continue
            pair = (uid, tid)
            if pair in pairs:
                count["existing_edges_reused"] += 1
                continue
            rid = "wf-" + hashlib.sha256((uid + "\x00" + tid).encode()).hexdigest()[:24]
            if rid in used_ids:
                raise ValueError("DETERMINISTIC_RELATION_ID_COLLISION:" + rid)
            relation = {"relation_id": rid, "relation_type": "WORD_FAMILY",
                        "source_type": targets[uid]["type"], "source_id": uid,
                        "target_type": targets[tid]["type"], "target_id": tid,
                        "value": {"text": targets[tid]["de"],
                                  "meaning": targets[tid]["fa"]},
                        "provenance": copy.deepcopy(evidence)}
            new["relations"].append(relation)
            used_ids[rid] = relation
            pairs.add(pair)
            count["edges_added"] += 1
    return new, {"schema": "gcpk-stage3-wortfamilie-wortnetz-bridge@1.0",
                 "status": "SOURCE_BOUND_SUCCESSOR_PROPOSAL_NOT_STAGE4_OR_STAGE6_PASS",
                 "canonical_parent_sha256": digest(canonical_bytes),
                 "registered_source_sha256": source_hash,
                 "counts": count,
                 "no_runtime_or_existing_library_mutation": True,
                 "no_mandatory_new_gate": True}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--canonical", required=True, type=Path)
    p.add_argument("--onepass", required=True, type=Path)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--output", type=Path, help="New canonical successor only, never in place")
    p.add_argument("--report", type=Path)
    p.add_argument("--apply", action="store_true", help="Write new successor; default is read-only")
    args = p.parse_args(argv)
    try:
        if not HASH.fullmatch(args.expected_sha256):
            raise ValueError("INVALID_EXPECTED_SHA256")
        raw = args.canonical.read_bytes()
        if digest(raw) != args.expected_sha256:
            raise ValueError("CALLER_EXPECTED_SHA256_MISMATCH")
        original = load_json(raw, "canonical")
        ledger = load_json(args.onepass.read_bytes(), "stage3")
        updated, report = apply_bridge(original, ledger, raw)
        if args.apply:
            if args.output is None:
                raise ValueError("OUTPUT_REQUIRED_FOR_APPLY")
            if args.output.resolve() in {args.canonical.resolve(), args.onepass.resolve()}:
                raise ValueError("OVERWRITE_OF_INPUT_FORBIDDEN")
            if args.output.exists():
                raise ValueError("OUTPUT_EXISTS")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            out = (json.dumps(updated, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            args.output.write_bytes(out)
            report["successor_sha256"] = digest(out)
            report["status"] = "SUCCESSOR_WRITTEN_NOT_STAGE4_OR_STAGE6_PASS"
        if args.report:
            if args.report.resolve() in {args.canonical.resolve(), args.onepass.resolve(), 
                                         args.output.resolve() if args.output else args.canonical.resolve()}:
                raise ValueError("REPORT_OVERWRITES_DATA")
            if args.report.exists():
                raise ValueError("REPORT_EXISTS")
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "BLOCKED_INPUT_OR_AUTHORITY",
                          "reason": str(exc)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
