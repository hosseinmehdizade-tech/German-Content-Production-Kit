#!/usr/bin/env python3
"""Prospective Stage3/Stage4 compatibility and evidence-gate dry run.

This validates metadata/closure, not German linguistic correctness. It does
not edit stage artifacts, accept legacy checkpoints or certify a release.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{64}$")
FACETS = {"identity", "sense", "translations", "examples", "morphosyntax",
          "relations", "combinations", "provenance", "didactics"}
DECISIONS = {"DONE", "NA_WITH_REASON", "HELD"}
BASE = Path(__file__).resolve().parents[1]
MATRIX = "Architecture/Stage3-Stage4-Unification/CONFLICT-DEPENDENCY-MATRIX-v0.1.json"
PRECEDENCE = "Architecture/Stage3-Stage4-Unification/POLICY-PRECEDENCE-ADOPTION-v0.2.json"
SPEC = "Architecture/Stage3-Stage4-Unification/ENRICHMENT-AND-INDEPENDENT-QA-CONTRACT-v0.1.md"
SAMPLES = (
    "Workspaces/menschen-a2-24-lessons-v336/L24-STAGE3C.json",
    "Workspaces/menschen-a2-24-lessons-v336/L24-STAGE4.json",
    "Workspaces/250-verben-mit-praepositionen-kombinationen-repair1-v336/LATEST.json",
    "Workspaces/aber-hallo-listen-tabellen/LATEST.json",
)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value



def validate_dependency_edges(matrix: dict) -> list[str]:
    """Fail closed when graph disagrees with per-conflict requires.

    The matrix is a NONACTIVE compatibility proposal. This never promotes
    a stage, changes user content, or infers implementation approval.
    """
    errors = []
    conflicts = matrix.get("conflicts", [])
    if not isinstance(conflicts, list) or not all(isinstance(c, dict) for c in conflicts):
        return ["invalid conflict records"]
    known = {c.get("id") for c in conflicts if isinstance(c.get("id"), str)}
    expected_list = []
    for c in conflicts:
        child = c.get("id")
        prerequisites = c.get("requires", [])
        if not isinstance(prerequisites, list):
            errors.append(f"invalid requires list: {child}")
            continue
        for parent in prerequisites:
            if not isinstance(parent, str) or parent not in known or parent == child:
                errors.append(f"invalid required predecessor: {parent}->{child}")
                continue
            expected_list.append((parent, child))
    if len(expected_list) != len(set(expected_list)):
        errors.append("duplicate requires relationship")
    expected = set(expected_list)

    edges = matrix.get("dependencies", [])
    if not isinstance(edges, list):
        return errors + ["dependency edges must be a list"]
    seen = set()
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2 or not all(isinstance(x, str) for x in edge):
            errors.append("malformed dependency edge")
            continue
        pair = tuple(edge)
        if pair in seen:
            errors.append(f"duplicate dependency edge: {pair[0]}->{pair[1]}")
        seen.add(pair)
        if pair[0] not in known or pair[1] not in known:
            errors.append(f"unknown graph vertex: {pair[0]}->{pair[1]}")
        elif pair not in expected:
            errors.append(f"undeclared dependency edge: {pair[0]}->{pair[1]}")
    for parent, child in sorted(expected - seen):
        errors.append(f"graph omits required dependency: {parent}->{child}")
    return errors



def validate_precedence_adoption(matrix: dict, adoption: dict) -> list[str]:
    """Guard non-active policy precedence/currentness; not migration approval."""
    errors = []
    if adoption.get("status") != "NONACTIVE_VERSIONED_OPT_IN" or adoption.get("rollout_state") != "PILOT_ONLY_NO_ACTIVE_CHANGE":
        errors.append("policy precedence draft was promoted without authorized migration")
    if adoption.get("framework") != "v3.3.6" or adoption.get("active_prompt") != "Prompt/START-PROMPT-v3.3.6.md":
        errors.append("proposal lost exact active framework/prompt guard")
    conflict_ids = {c.get("id") for c in matrix.get("conflicts", [])}
    ids = adoption.get("preserved_conflicts")
    if not isinstance(ids, list) or len(ids) != len(set(ids)) or set(ids) != conflict_ids:
        errors.append("precedence adoption dropped or invented conflict IDs")
    profiles = adoption.get("applicability")
    if not isinstance(profiles, list) or len(profiles) != 10 or any(
        not isinstance(x, dict) or not x.get("stream") or not x.get("adoption") or not x.get("preserve")
        for x in profiles
    ):
        errors.append("missing ten scoped stream applicability profiles")
    elif len({x["stream"] for x in profiles}) != 10:
        errors.append("duplicate applicability stream")
    compatibility = adoption.get("compatibility", {})
    required = {"stage4": "INDEPENDENT_AI_SEMANTIC_PLUS_FULL_DETERMINISTIC",
                "stage5_6_7": "UNMODIFIED_REQUIRED",
                "ui": "NO_CHANGE", "source": "IMMUTABLE", "locked": "IMMUTABLE"}
    if not isinstance(compatibility, dict) or any(compatibility.get(k) != v for k, v in required.items()):
        errors.append("proposal weakens independent Stage4, Stage5-7, immutable source or UI")
    promotion = adoption.get("promotion_requirements", [])
    expected_promotions = ("explicit user approval", "consumer/schema adapters", "Stage5/6/7")
    if not isinstance(promotion, list) or any(
        not any(token in entry for entry in promotion if isinstance(entry, str))
        for token in expected_promotions
    ):
        errors.append("missing migration approval, writer/consumer or downstream gate")
    resolution = adoption.get("currentness_resolution", {})
    if not isinstance(resolution, dict) or (
        resolution.get("never_assume_version_from_draft") is not True or
        resolution.get("absent_current") != "BLOCKED_FOR_EDIT; no silent downgrade, no content successor in optimization chat" or
        len(resolution.get("selection_order", [])) < 4 or
        "user-established optimization mission" not in resolution.get("user_mission", "")
    ):
        errors.append("stale authority or mission pivot in prospective currentness resolution")
    provenance = adoption.get("dependency_graph_integrity", {})
    expected_edges = sum(len(c.get("requires", [])) for c in matrix.get("conflicts", []))
    if not isinstance(provenance, dict) or (
        provenance.get("source") != MATRIX or
        provenance.get("conflicts") != len(conflict_ids) or
        provenance.get("edges") != expected_edges or
        provenance.get("proposal_only") is not True
    ):
        errors.append("precedence matrix dependency counts or scope drift")
    if isinstance(profiles, list):
        for x in profiles:
            if isinstance(x, dict) and x.get("stream") in (
                "250 Verben mit Praepositionen", "Aber Hallo Listen Tabellen"):
                combined = x.get("adoption", "") + " " + x.get("preserve", "")
                if ("pin WIP33" in combined and "never pin WIP33" not in combined) or "use WIP26" in combined:
                    errors.append("stale historical WIP used as mutable currentness")
    return errors


def validate_matrix(root: Path) -> list[str]:
    errors = []
    matrix = load(root / MATRIX)
    if matrix.get("status") != "PROPOSED_COMPATIBILITY_ONLY_NOT_ACTIVE":
        errors.append("matrix must remain non-active until approved migration")
    if not (root / SPEC).is_file():
        errors.append("missing independent Stage3/4 compatibility contract")
    errors.extend(validate_precedence_adoption(matrix, load(root / PRECEDENCE)))
    conflicts = matrix.get("conflicts", [])
    ids = [x.get("id") for x in conflicts]
    if len(ids) != len(set(ids)) or len(ids) < 10:
        errors.append("invalid conflict ids or missing required coverage")
    graph = {i: [] for i in ids}
    for x in conflicts:
        if not x.get("problem") or not x.get("resolution") or not x.get("compatibility"):
            errors.append(f"incomplete conflict: {x.get('id')}")
        for p in x.get("sources", []):
            if not (root / p).is_file():
                errors.append(f"missing conflict authority: {p}")
        for dep in x.get("requires", []):
            if dep not in graph:
                errors.append(f"unknown dependency: {dep}")
            else:
                graph[dep].append(x.get("id"))
    for p in matrix.get("source_documents", []):
        if not (root / p).is_file():
            errors.append(f"missing source policy: {p}")
    errors.extend(validate_dependency_edges(matrix))
    seen, active = set(), set()

    def walk(n):
        if n in active:
            errors.append(f"dependency cycle: {n}")
            return
        if n in seen:
            return
        active.add(n)
        for m in graph.get(n, []):
            walk(m)
        active.remove(n)
        seen.add(n)
    for key in graph:
        walk(key)
    active_prompt = (root / "Prompt/ACTIVE-PROMPT.txt").read_text(encoding="utf-8").strip()
    if active_prompt != "START-PROMPT-v3.3.6.md":
        errors.append("active prompt has changed: manually re-evaluate compatibility")
    return errors


def legacy_compatibility(root: Path) -> list[str]:
    errors = []
    try:
        s3, s4, verbs, ah = [load(root / p) for p in SAMPLES]
    except (FileNotFoundError, ValueError) as exc:
        return [f"cannot load a representative checkpoint: {exc}"]
    if s3.get("stage") != "3C" or s3.get("stage3c_complete") is not True:
        errors.append("L24 Stage3C legacy key changed")
    if s3.get("stage4_complete") is not False:
        errors.append("L24 Stage3C incorrectly implies downstream Stage4")
    if s4.get("stage") != 4 or s4.get("stage4_complete") is not True:
        errors.append("L24 Stage4 sample status changed")
    if not str(s4.get("status", "")).startswith("PASS_SCOPED"):
        errors.append("L24 Stage4 scope changed; cannot silently promote to full")
    if s4.get("stage5_import_ready") is True or s4.get("stage7_locked") is True:
        errors.append("L24 Stage4 sample would bypass downstream gates")
    if not ("STAGE4" in str(verbs.get("status", "")) and "NOT_FINAL" in str(verbs.get("status", ""))):
        errors.append("250 Verben Stage4 nonfinal authority changed")
    if "STAGE4_OPEN" not in str(ah.get("status", "")):
        errors.append("Aber Hallo Stage4 OPEN authority changed")
    return errors


def validate_candidate(stage3: dict, stage4: dict) -> list[str]:
    """Reject false all-dimensions completion and self-reviewed Stage4 PASS."""
    errors = []
    sha_in, sha_out = stage3.get("input_sha256"), stage3.get("output_sha256")
    if not isinstance(sha_in, str) or not SHA.fullmatch(sha_in):
        errors.append("Stage3 missing exact input_sha256")
    if not isinstance(sha_out, str) or not SHA.fullmatch(sha_out):
        errors.append("Stage3 missing exact output_sha256")
    if not stage3.get("source_authority") or not stage3.get("stage3_method"):
        errors.append("Stage3 missing source authority/authoring method")
    if stage3.get("mutable_bytes_applied") is not True:
        errors.append("Stage3 editorial report is not applied to current working bytes")
    if stage3.get("locked_source_mutated") is not False:
        errors.append("Stage3 must not mutate source or locked history")
    decisions = stage3.get("facets")
    if not isinstance(decisions, dict) or set(decisions) != FACETS:
        errors.append("Stage3 must disposition all nine facets")
    else:
        for name, cell in decisions.items():
            if not isinstance(cell, dict) or cell.get("decision") not in DECISIONS:
                errors.append(f"invalid facet closure: {name}")
                continue
            if cell["decision"] == "NA_WITH_REASON" and not cell.get("reason"):
                errors.append(f"missing not-applicable explanation: {name}")
            if cell["decision"] == "HELD":
                errors.append(f"unresolved facet HOLD: {name}")
        combos = decisions.get("combinations", {})
        if isinstance(combos, dict):
            if combos.get("visible_items") == 0 and combos.get("close") != "CLOSED_NO_FORCE":
                errors.append("zero combinations need CLOSED_NO_FORCE, no forced filler")
            if combos.get("close") == "CLOSED_NO_FORCE" and not combos.get("reason"):
                errors.append("CLOSED_NO_FORCE requires pedagogical reason")
            if combos.get("visible_items", 0) > 0 and not combos.get("teaching_delta_verified"):
                errors.append("visible combinations require teaching_delta verification")
    card_total = stage3.get("lexical_cards_total")
    if type(card_total) is not int or card_total < 1:
        errors.append("Stage3 must count all lexical cards")
    facet_coverage = stage3.get("facet_card_coverage")
    if not isinstance(facet_coverage, dict) or set(facet_coverage) != FACETS:
        errors.append("Stage3 missing per-card nine-facet coverage ledger")
    elif type(card_total) is int and card_total > 0:
        for name, count in facet_coverage.items():
            if type(count) is not int or count != card_total:
                errors.append(f"incomplete card coverage for {name}")
    if stage3.get("source_lineage_receipt") in (None, ""):
        errors.append("Stage3 source-lineage evidence missing")
    if stage3.get("unresolved_holds") != 0:
        errors.append("unresolved Stage3 holds")
    if stage4.get("reviewed_output_sha256") != sha_out:
        errors.append("Stage4 review stale or not bound to Stage3 output SHA")
    if stage4.get("independent_method") == stage3.get("stage3_method") or not stage4.get("independent_method"):
        errors.append("Stage4 lacks independently methoded second pass")
    if stage4.get("review_kind") != "AI_INDEPENDENT_ADVERSARIAL":
        errors.append("Stage4 must label AI review accurately")
    if stage4.get("deterministic_coverage") != "FULL":
        errors.append("Stage4 deterministic scope incomplete")
    if stage4.get("semantic_scope") != "WHOLE_DATASET_RISK_TARGETED_WITH_ADVERSARIAL_SAMPLING":
        errors.append("Stage4 semantic review not broad/risk-targeted enough")
    scanned = stage4.get("deterministic_scanned_units")
    if type(card_total) is not int or type(scanned) is not int or scanned != card_total:
        errors.append("Stage4 deterministic count must cover exact Stage3 card total")
    if type(stage4.get("independent_semantic_challenge_units")) is not int or stage4["independent_semantic_challenge_units"] < 1:
        errors.append("Stage4 requires documented independent semantic adversarial sampling")
    risk_total = stage4.get("risk_queue_total")
    risk_closed = stage4.get("risk_queue_closed")
    if (type(risk_total) is not int or type(risk_closed) is not int or
            risk_total < 0 or risk_closed != risk_total):
        errors.append("Stage4 risk queue needs exact total/closed reconciliation")
    if not stage4.get("adversarial_method_evidence"):
        errors.append("Stage4 independent method evidence missing")
    if stage4.get("risk_queue_open") != 0:
        errors.append("Stage4 risks are still unresolved")
    if stage4.get("source_challenge") is not True:
        errors.append("Stage4 missing independent source challenge")
    if stage4.get("stage4_result") != "PASS":
        errors.append("Stage4 has no full PASS receipt")
    if stage4.get("downstream_stage5_6_7_unmodified") is not True:
        errors.append("Stage5-7 independence not attested")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=BASE)
    parser.add_argument("--stage3", type=Path)
    parser.add_argument("--stage4", type=Path)
    args = parser.parse_args()
    errors = validate_matrix(args.root) + legacy_compatibility(args.root)
    if bool(args.stage3) != bool(args.stage4):
        errors.append("--stage3 and --stage4 must be passed together")
    elif args.stage3 and args.stage4:
        try:
            errors += validate_candidate(load(args.stage3), load(args.stage4))
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    print(json.dumps({"schema": "gcpk-stage3-stage4-compatibility@0.1", "status": "PASS_COMPATIBILITY_ONLY" if not errors else "BLOCKED", "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
