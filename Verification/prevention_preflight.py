#!/usr/bin/env python3
"""Read-only early gates. Never repairs content or claims runtime acceptance."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from validate_unified_vocabulary_projection_v1_1_0 import load_rows, parse_custom, validate

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def coordination_errors(state, sync):
    errors = []
    budget = sync["turn_budget"]["ordinary_turn_git_sync_attempts_max"]
    configured = state.get("git_sync_policy", {})
    for key, expected in {"mode": sync["mode"], "ordinary_turn_sync_attempts_max": budget,
                          "coalesce_intermediate_states": sync["coalescing_rule"]["enabled"]}.items():
        if (key in configured or state.get("project") == "German-Content-Production-Kit") and configured.get(key) != expected:
            errors.append(f"STALE_SYNC_COORDINATION: {key}")
    if state.get("operating_mode", {}).get("git_retry_budget_per_normal_turn") != budget:
        errors.append("STALE_SYNC_COORDINATION: operating_mode retry budget")
    return errors


def memory_errors(memory, root):
    errors = []
    decisions = memory.get("decisions", [])
    ids = [d.get("id") for d in decisions]
    if not ids or len(ids) != len(set(ids)):
        errors.append("MEMORY_IDS_EMPTY_OR_DUPLICATED")
    by_id = {d.get("id"): d for d in decisions}
    for d in decisions:
        mid = d.get("id")
        if d.get("status") not in {"ACTIVE", "SUPERSEDED", "HISTORICAL"}:
            errors.append(f"{mid}: INVALID_STATUS")
        integrity = d.get("decision_integrity", {})
        fields = integrity.get("fields", [])
        if not fields or digest({k: d.get(k) for k in fields}) != integrity.get("sha256"):
            errors.append(f"{mid}: PRESERVED_DECISION_CHANGED")
        for old in d.get("supersedes", []):
            if old not in by_id:
                if old not in memory.get("external_supersession_ids", []):
                    errors.append(f"{mid}: UNKNOWN_SUPERSESSION {old}")
            elif by_id[old].get("status") != "SUPERSEDED" or mid not in by_id[old].get("superseded_by", []):
                errors.append(f"{mid}: BROKEN_SUPERSESSION {old}")
        for successor in d.get("superseded_by", []):
            if successor not in by_id or mid not in by_id[successor].get("supersedes", []):
                errors.append(f"{mid}: BROKEN_SUCCESSOR {successor}")
        lesson = d.get("prevention", {})
        if d.get("status") == "ACTIVE":
            required = {"scope", "severity", "root_cause", "impact", "wrong_path", "correct_method", "rule", "gate", "evidence", "affected_workstreams", "time_cost"}
            if required - lesson.keys():
                errors.append(f"{mid}: INCOMPLETE_LIFECYCLE")
            if any(not lesson.get(k) for k in required):
                errors.append(f"{mid}: EMPTY_LIFECYCLE_FIELD")
            if lesson.get("severity") not in {"S1", "S2", "S3", "S4"}:
                errors.append(f"{mid}: INVALID_SEVERITY")
            gate = lesson.get("gate", {})
            if not gate.get("kinds") or set(gate.get("kinds", [])) - set("ABCDEFGH"):
                errors.append(f"{mid}: INVALID_GATE_CLASSIFICATION")
            if gate.get("status") not in {"MANUAL", "IMPLEMENTED", "PORTABLE_AUTHORITY_REQUIRED", "PARTIAL"}:
                errors.append(f"{mid}: INVALID_GATE_STATUS")
            if not gate.get("limits"):
                errors.append(f"{mid}: MISSING_GATE_LIMITS")
            refs = lesson.get("evidence", [])
            if not refs:
                errors.append(f"{mid}: NO_EVIDENCE")
            for ref in refs:
                file = ref.split("#", 1)[0]
                target = (root / file).resolve()
                if not target.is_relative_to(root.resolve()) or not target.is_file():
                    errors.append(f"{mid}: MISSING_LOCAL_EVIDENCE {ref}")
            for tool in gate.get("tools", []):
                if not (root / tool).is_file():
                    errors.append(f"{mid}: MISSING_GATE_TOOL {tool}")
    return errors


def projection_errors(rows):
    errors = [f"ENVELOPE: {x}" for x in validate(rows)["errors"]]
    ids = [str(r.get("id") or "").strip() for r in rows]
    if not rows or any(not cid for cid in ids):
        errors.append("EMPTY_PROJECTION_OR_ID")
    for cid, count in Counter(ids).items():
        if count > 1:
            errors.append(f"{cid}: DUPLICATE_CANONICAL_ID")
    for row in rows:
        cid = row.get("id")
        cf, custom_error = parse_custom(row)
        if custom_error:
            continue
        unit = cf.get("canonical_unit") or {}
        definitions = [cf.get("germanDefinition"), cf.get("vnext_definition_de"), unit.get("definition_de")]
        note = str(row.get("notes") or "").strip()
        if note and note in {str(v).strip() for v in definitions if v}:
            errors.append(f"{cid}: DUPLICATE_DEFINITION_NOTE")
        if str(cf.get("vnext_pos") or row.get("category") or "").lower() == "verb":
            morphology = cf.get("vnext_morphology") or {}
            core = unit.get("core") or {}
            aliases = {"present": ("present_3sg", "present"), "preterite": ("preterite_3sg", "preterite"), "perfect": ("perfect",)}
            for slot, keys in aliases.items():
                source = next((morphology[k] for k in keys if morphology.get(k)), None)
                bridge = next((core[k] for k in keys if core.get(k)), None) or cf.get(slot) or row.get(slot)
                if source and not bridge:
                    errors.append(f"{cid}: MISSING_MORPHOLOGY_BRIDGE {slot}")
        # Scan explicit learner fields only. Semantic/provenance enums remain valid.
        surface = [row.get("front"), row.get("back"), row.get("notes"), row.get("details"), unit.get("details"), unit.get("connections")]
        blob = json.dumps(surface, ensure_ascii=False)
        if re.search(r"\bREKTION\b", blob):
            errors.append(f"{cid}: LITERAL_REKTION_IN_LEARNER_FIELD")
        # Exact known enum spellings; no fuzzy word blacklist or POS inference.
        if re.search(r"\b(?:non_prefixed|verb_core|accusative_object|dative_object)\b", blob):
            errors.append(f"{cid}: INTERNAL_ENUM_IN_LEARNER_FIELD")
        related = row.get("related") or []
        if isinstance(related, str):
            try:
                related = json.loads(related)
            except ValueError:
                related = []  # Unstructured text needs runtime/linguistic review.
        for item in related if isinstance(related, list) else []:
            if isinstance(item, dict) and item.get("relation_type", item.get("type", "SYNONYM")).upper() != "SYNONYM":
                errors.append(f"{cid}: NON_SYNONYM_IN_SYNONYM_TRANSPORT")
    return errors


def lineage_errors(rows, baseline):
    """Successor projection vs an explicitly resolved immutable parent envelope.

    Canonical semantics may be enriched. This checks survival of authority
    payloads and known parent metadata, without treating book names as IDs.
    """
    errors = projection_errors(rows)
    parents = {str(r.get("id")): r for r in baseline}
    if not parents or set(parents) != {str(r.get("id")) for r in rows}:
        errors.append("LINEAGE_IDENTITY_SET_CHANGED_REVIEW_REQUIRED")
    for row in rows:
        cid = str(row.get("id"))
        parent = parents.get(cid)
        if parent is None:
            continue
        cf, _ = parse_custom(row)
        prior, _ = parse_custom(parent)
        if not isinstance(cf.get("canonical_unit"), dict) or not cf.get("canonical_unit"):
            errors.append(f"{cid}: MISSING_CANONICAL_UNIT")
        if not isinstance(cf.get("canonical_relations"), list):
            errors.append(f"{cid}: MISSING_CANONICAL_RELATIONS")
        for key in ["source_audio_refs", "course_memberships"]:
            if key in prior and cf.get(key) != prior[key]:
                errors.append(f"{cid}: PARENT_LINEAGE_LOST {key}")
        for key in ["source", "lesson", "deck", "order"]:
            if key in parent and str(row.get(key, "")) != str(parent[key]):
                errors.append(f"{cid}: PARENT_SEED_OR_ORDER_CHANGED_REVIEW_REQUIRED {key}")
    return errors


def package_errors(path):
    errors = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        for name, count in Counter(names).items():
            if count > 1:
                errors.append(f"DUPLICATE_ZIP_MEMBER: {name}")
        for name in names:
            parts = PurePosixPath(name.replace("\\", "/")).parts
            if ".." in parts or name.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", name):
                errors.append(f"UNSAFE_ZIP_PATH: {name}")
            if any(p.lower() in {"__pycache__", ".pytest_cache", ".git"} for p in parts) or name.lower().endswith((".pyc", ".pyo")):
                errors.append(f"PACKAGE_CONTAMINATION: {name}")
        bad = archive.testzip()
        if bad:
            errors.append(f"CRC_FAILURE: {bad}")
    return errors


def checkpoint_errors(data, memory=None):
    errors = []
    for key, expected in {"project_memory": "PROJECT-MEMORY.json", "git_sync_policy": "GIT-SYNC-POLICY.json"}.items():
        if data.get(key) != expected:
            errors.append(f"MISSING_OR_INVALID_CHECKPOINT_POINTER: {key}")
    if not data.get("next_action"):
        errors.append("MISSING_NEXT_ACTION")
    if memory is not None:
        known = {d["id"] for d in memory["decisions"]}
        for ref in data.get("prevention_refs", []):
            if ref not in known:
                errors.append(f"UNKNOWN_PREVENTION_REFERENCE: {ref}")
    # Identity formats vary by workstream; do not invent a universal authority schema.
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["memory", "projection", "lineage", "package", "checkpoint"])
    ap.add_argument("input", nargs="?")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--baseline", type=Path, help="Resolved immutable parent projection for lineage mode; never inferred from a filename")
    args = ap.parse_args()
    try:
        path = Path(args.input) if args.input else args.root / "PROJECT-MEMORY.json"
        if args.mode == "memory":
            errors = memory_errors(json.loads(path.read_text(encoding="utf-8-sig")), args.root)
            errors += coordination_errors(
                json.loads((args.root / "PROJECT-STATE.json").read_text(encoding="utf-8-sig")),
                json.loads((args.root / "GIT-SYNC-POLICY.json").read_text(encoding="utf-8-sig")))
        elif not args.input:
            raise ValueError("input is required")
        elif args.mode == "projection":
            errors = projection_errors(load_rows(path))
        elif args.mode == "lineage":
            if not args.baseline:
                raise ValueError("lineage mode requires --baseline from resolved parent authority")
            errors = lineage_errors(load_rows(path), load_rows(args.baseline))
        elif args.mode == "package":
            errors = package_errors(path)
        else:
            errors = checkpoint_errors(json.loads(path.read_text(encoding="utf-8-sig")),
                                       json.loads((args.root / "PROJECT-MEMORY.json").read_text(encoding="utf-8-sig")))
        print(json.dumps({"status": "FAIL" if errors else "PASS", "gate": args.mode, "errors": errors}, ensure_ascii=False, indent=2))
        return bool(errors)
    except (ValueError, OSError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "INPUT_ERROR", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
