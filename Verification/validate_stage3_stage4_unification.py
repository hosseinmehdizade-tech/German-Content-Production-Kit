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




def validate_stage56_evidence_chain(boundary: dict, user: dict, readiness: dict) -> list[str]:
    """Keep distinct exact-artifact static, user-observed, release evidence types.

    Verifies the documented 250 Verben v1.7 history, NOT app behavior.
    """
    errors = []
    check = lambda ok, msg: None if ok else errors.append(msg)
    old = boundary.get("exact_authority", {})
    target = user.get("target_identity", {})
    checks = user.get("checked_behaviors", [])
    check(boundary.get("real_stage6", {}).get("overall") == "BLOCKED_NOT_PASS",
          "past agent Stage6 browser attempt cannot be promoted to automated PASS")
    check(boundary.get("content_scoped_checks", {}).get("real_browser") ==
          "BLOCKED_NET_ERR_BLOCKED_BY_ADMINISTRATOR",
          "independent browser environment blocker not preserved")
    check(user.get("evidence_type") == "DIRECT_USER_REPORTED_MANUAL_OBSERVATION" and
          "USER_CONFIRMED" in user.get("status", ""),
          "manual user observation must remain separately labeled")
    check(isinstance(checks, list) and len(checks) == 8 and
          len({x.get("id") for x in checks if isinstance(x, dict)}) == 8 and
          all(isinstance(x, dict) and x.get("reported_result") == "PASS_USER_REPORTED" for x in checks),
          "not exactly eight distinct user-reported checks")
    check(user.get("acceptance", {}).get("independent_browser_automation") ==
          "NOT_RUN_IN_AGENT_ENVIRONMENT",
          "user report must not fabricate independent automated Stage6")
    check(user.get("prior_independent_evidence", {}).get("agent_chromium_localhost") ==
          "BLOCKED_NET_ERR_BLOCKED_BY_ADMINISTRATOR",
          "user report lost provenance of prior environment blocker")
    check(old.get("current_app") == target.get("app_current_runtime") == "v486-R120"
          and old.get("current_app_zip_sha256") == target.get("app_zip_sha256"),
          "Stage6 user and static records target different app CURRENT")
    check(old.get("exact_import_tsv_sha256") ==
          target.get("stage4_stage5_approved_content_tsv_sha256"),
          "Stage5 / Stage6 import dataset identity mismatch")
    check(isinstance(readiness.get("overall"), str) and
          "STAGE6_USER_CONFIRMED_PASS" in readiness["overall"] and
          "STAGE7_PRIVATE_SINGLE_ZIP_PASS" in readiness["overall"] and
          "NO_RUNTIME_PROMOTION" in readiness["overall"],
          "private Stage7/readiness not explicitly distinguished from runtime promotion")
    check(user.get("preservation", {}).get("app_current_unchanged") is True and
          user.get("preservation", {}).get("app_visible_UI_unchanged") is True,
          "user observation incorrectly implies app or UI mutation")
    return errors


def validate_stage5to7_private_lineage(
        stage5: dict, stage7: dict, boundary: dict, user: dict,
        readiness: dict, stage5_outcome: dict, stage7_outcome: dict,
        stage4: dict) -> list[str]:
    """Historical 250-Verben v1.7 *record* parity, NOT ZIP-byte or live app QA.

    Cross-check separately written Stage5/7 checkpoints and outcome receipts
    against the older environment-blocked agent Stage6 evidence, later direct
    user observation, and non-authoritative readiness summary. Never infer a
    general Stage4/5/6/7 promotion, automatic browser PASS or public license.
    """
    errors: list[str] = []
    q = readiness.get("phase3_enrichment_QA", {})
    if not isinstance(q, dict):
        return ["Stage5-7 readiness missing lexical evidence"]
    r5, ra, ru, r7 = (q.get(name) for name in (
        "stage5_content_delivery_v17", "stage6_current_v486_vmp_v17",
        "stage6_user_observed_v17", "stage7_private_release_v17"))
    if not all(isinstance(x, dict) for x in (r5, ra, ru, r7)):
        return ["Stage5-7 missing independently scoped readiness records"]

    def compare(name: str, fields: list[object]) -> None:
        if not all(isinstance(v, str) and SHA.fullmatch(v) for v in fields):
            errors.append(name + ": missing/malformed SHA256")
        elif len(set(fields)) != 1:
            errors.append(name + ": independent evidence hashes disagree")

    def keep(label: str, condition: bool) -> None:
        if not condition:
            errors.append(label)

    workstream = stage5.get("workstream")
    keep("Stage4-7 mismatched source workstream", all(
        x.get("workstream") == workstream for x in
        (stage4, stage7, boundary, user)) and isinstance(workstream, str) and bool(workstream))
    stage4_authority = stage4.get("authority", {})
    stage4_artifact = stage4.get("artifact", {})
    stage4_review = stage4.get("review", {})
    stage4_qa = stage4.get("QA", {})
    stage4_boundaries = stage4.get("boundaries", {})
    if not all(isinstance(x, dict) for x in (
            stage4_authority, stage4_artifact, stage4_review,
            stage4_qa, stage4_boundaries)):
        return errors + ["Stage4 malformed independent linguistic approval"]
    keep("Stage4 review cannot be human-signed, scoped or self-promoting", (
        stage4.get("status") ==
        "PASS_AI_LINGUISTIC_QA_AND_TECHNICAL_GATES_EXACT_OPTIN_SUCCESSOR_ONLY" and
        stage4_qa.get("AI_independent_second_method") ==
        "DOCUMENTED_NOT_HUMAN" and
        stage4_boundaries.get("stage5") == "NOT_RUN" and
        stage4_boundaries.get("stage7") == "NOT_FINAL" and
        stage4_review.get("open_high_or_source_fidelity_holds") == 0))
    l5 = stage5.get("lineage", {})
    a5 = stage5.get("artifact", {})
    a7 = stage7.get("authorities", {})
    release = stage7.get("release", {})
    gate7 = stage7.get("gates", {})
    b7 = stage7.get("boundaries", {})
    old = boundary.get("exact_authority", {})
    target = user.get("target_identity", {})
    protected = user.get("preservation", {})
    if not all(isinstance(v, dict) for v in
               (l5, a5, a7, release, gate7, b7, old, target, protected)):
        return errors + ["Stage5-7 malformed lineage/authority records"]

    compare("Stage4 approved ZIP to Stage5", [
        stage4_artifact.get("zip_sha256"),
        l5.get("approved_stage4_zip_sha256"),
        q.get("stage4_final_v17", {}).get("zip_sha256"),
    ])
    compare("Stage5 package", [
        a5.get("sha256"), old.get("content_stage5_sha256"),
        target.get("stage5_content_zip_sha256"),
        a7.get("original_stage5_content_zip_sha256"),
        r5.get("zip_sha256"), ru.get("stage5_zip_sha256"),
        r7.get("content_stage5_source_zip_sha256"),
        stage5_outcome.get("persistence", {}).get("package_sha256"),
    ])
    compare("Stage4-approved import TSV to Stage7", [
        stage4_authority.get("v17_exact_tsv_sha256"),
        l5.get("approved_stage4_tsv_sha256"),
        l5.get("current_stage5_import_tsv_sha256"),
        old.get("exact_import_tsv_sha256"),
        target.get("stage4_stage5_approved_content_tsv_sha256"),
        a7.get("source_stage4_stage5_v17_tsv_sha256"),
        r5.get("import_tsv_sha256"), ra.get("content_tsv_sha256"),
        ru.get("exact_import_tsv_sha256"), r7.get("content_v17_tsv_sha256"),
    ])
    compare("preserved production WIP27", [
        stage4_authority.get("original_production_WIP27_zip_sha256"),
        l5.get("existing_wip27_production_zip_sha256"),
        old.get("production_WIP27_sha256"),
        protected.get("production_WIP27_zip_sha256"),
        a7.get("original_WIP27_zip_sha256"),
        r5.get("source_wip27_zip_sha256"),
    ])
    compare("registered original PDF provenance", [
        stage4_authority.get("original_pdf_sha256"),
        l5.get("registered_source_pdf_sha256"),
        a7.get("original_source_pdf_sha256"),
        r7.get("original_pdf_external_sha256"),
    ])
    compare("registered canonical source provenance", [
        stage4_authority.get("canonical_source_member_sha256"),
        l5.get("registered_canonical_source_sha256"),
        a7.get("canonical_source_sha256"),
    ])
    compare("same exact historical app ZIP", [
        old.get("current_app_zip_sha256"), target.get("app_zip_sha256"),
        a7.get("original_current_app_zip_sha256"),
        ra.get("runtime_zip_sha256"), ru.get("app_zip_sha256"),
        r7.get("current_app_zip_sha256"),
    ])
    keep("Stage5-7 historical app version mismatch", (
        old.get("current_app") == target.get("app_current_runtime") ==
        a7.get("original_current_app_version") == ra.get("current_runtime") ==
        ru.get("app_current") == r7.get("current_runtime") == "v486-R120"))
    compare("private Stage7 release ZIP", [
        release.get("sha256"), r7.get("exact_final_zip_sha256"),
        stage7_outcome.get("persistence", {}).get("release_zip_sha256"),
    ])
    keep("Stage5-7 outcome receipts cannot certify wrong milestones", (
        stage5_outcome.get("milestone", {}).get("state") == "PASS" and
        stage7_outcome.get("milestone", {}).get("state") == "PASS" and
        stage5_outcome.get("persistence", {}).get("resume_pointer") ==
        r5.get("checkpoint") and
        stage7_outcome.get("persistence", {}).get("resume_pointer") ==
        r7.get("checkpoint")))
    keep("Stage5/7 package inventory counts disagree", (
        a5.get("files") == r5.get("package_file_count") == 46 and
        a5.get("manifest_entries") == r5.get("manifest_verified") == 45 and
        release.get("zip_member_count") == r7.get("package_files") == 184 and
        release.get("manifest_entries") == r7.get("manifest_verified") == 183))
    keep("Stage7 independent-browser evidence must stay USER REPORTED", (
        user.get("evidence_type") == "DIRECT_USER_REPORTED_MANUAL_OBSERVATION" and
        user.get("acceptance", {}).get("independent_browser_automation") ==
        "NOT_RUN_IN_AGENT_ENVIRONMENT" and
        "USER_REPORTED" in gate7.get("stage6", "") and
        "NOT_AUTOMATED" in gate7.get("stage6", "") and
        r7.get("stage6") ==
        "PASS_DIRECT_USER_REPORTED_8_CHECKS__INDEPENDENT_BROWSER_NOT_RUN" and
        r7.get("original_workstream_PRODUCTION_WIP27_latest_unchanged") is True))
    keep("Stage7 private-only licensing/source PDF boundary weakened", (
        b7.get("source_pdf_in_final_zip") is False and
        b7.get("source_pdf_remains_available_in_user_private_stage5_archive") is True and
        "NOT_ESTABLISHED" in b7.get("source_rights", "") and
        r7.get("original_pdf_included") is False and
        "PRIVATE_" in r7.get("license", "") and
        "NOT_ESTABLISHED" in r7.get("license", "") and
        stage7_outcome.get("boundaries", {}).get("public_redistribution_rights") ==
        "NOT_ESTABLISHED"))
    keep("Stage5-7 mutation or runtime promotion scope inflated", (
        a5.get("app_runtime_included") is False and
        r5.get("production_LATEST_modified") is False and
        stage7.get("boundaries", {}).get("app_current_pointer_modified") is False and
        stage7.get("boundaries", {}).get("main_content_WIP27_modified") is False and
        stage7.get("coverage", {}).get("visible_UI_changed") is False and
        stage7.get("coverage", {}).get("content_sha_changed") is False and
        stage7.get("coverage", {}).get("runtime_sha_changed") is False and
        b7.get("artifact_purpose") ==
        "PRIVATE_USER_CONTENT_INTEGRATION_DISTRIBUTION__NOT_GLOBAL_APP_RUNTIME_VERSION_PROMOTION"))
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
    # OP-01 active user-approved linguistic policy requires an explicit
    # reasoned disposition for EVERY lexical unit. Aggregate coverage and a
    # nonempty adversarial sample cannot substitute for a complete ledger.
    # This remains NONACTIVE metadata preflight, not linguistic signoff.
    unit_pins = stage3.get("unit_sha256_by_id")
    valid_pins = (
        isinstance(unit_pins, dict) and type(card_total) is int and
        len(unit_pins) == card_total and card_total > 0 and
        all(isinstance(uid, str) and bool(uid.strip()) and
            isinstance(sha, str) and SHA.fullmatch(sha) is not None
            for uid, sha in unit_pins.items())
    )
    if not valid_pins:
        errors.append("Stage3 must pin every lexical unit ID to exact SHA256")
    reviews = stage4.get("unit_dispositions")
    allowed = {"KEEP_WITH_REASON", "CLOSED_NO_FORCE_WITH_REASON",
               "CORRECT_WITH_BEFORE_AFTER", "HOLD_WITH_SPECIFIC_EVIDENCE"}
    if not isinstance(reviews, list) or type(card_total) is not int or len(reviews) != card_total:
        errors.append("Stage4 per-unit disposition ledger must cover exact lexical total")
    else:
        seen = set()
        for i, review in enumerate(reviews):
            if not isinstance(review, dict) or set(review) != {
                    "unit_id", "unit_sha256", "disposition", "reason",
                    "evidence_ref", "source_locator"}:
                errors.append(f"Stage4 malformed unit disposition: {i}")
                continue
            uid = review["unit_id"]
            if not isinstance(uid, str) or not uid or uid in seen:
                errors.append(f"Stage4 duplicate/invalid unit disposition ID: {i}")
                continue
            seen.add(uid)
            if not valid_pins or uid not in unit_pins or review["unit_sha256"] != unit_pins[uid]:
                errors.append(f"Stage4 per-unit disposition stale/unknown SHA: {uid}")
            if review["disposition"] not in allowed:
                errors.append(f"Stage4 unknown per-unit disposition: {uid}")
            elif review["disposition"] in {"HOLD_WITH_SPECIFIC_EVIDENCE", "CORRECT_WITH_BEFORE_AFTER"}:
                # A final pass cannot treat a held item as closed, or claim
                # a correction solely on self-reported pre/post metadata.
                errors.append(f"Stage4 hold/correction requires separate closure and byte proof: {uid}")
            for field in ("reason", "evidence_ref", "source_locator"):
                value = review[field]
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"Stage4 unit disposition missing {field}: {uid}")
        if valid_pins and seen != set(unit_pins):
            errors.append("Stage4 unit disposition ID set differs from Stage3 snapshot")
    control = stage4.get("seeded_negative_control")
    if not isinstance(control, dict) or set(control) != {
            "unit_id", "expected_fault", "detected_fault", "result",
            "evidence_ref"}:
        errors.append("Stage4 seeded negative control receipt missing/malformed")
    elif (not valid_pins or
          not isinstance(control["unit_id"], str) or
          control["unit_id"] not in unit_pins or
          not isinstance(control["expected_fault"], str) or
          not control["expected_fault"].strip() or
          control["detected_fault"] != control["expected_fault"] or
          control["result"] != "DETECTED" or
          not isinstance(control["evidence_ref"], str) or
          not control["evidence_ref"].strip()):
        errors.append("Stage4 seeded negative control not detected/bound to unit evidence")
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
    stage56_paths = (
        "Architecture/Stage3-Stage4-Unification/250-VERBEN-STAGE6-V486-R120-BOUNDARY-v1.7.json",
        "Architecture/Stage3-Stage4-Unification/250-VERBEN-STAGE6-USER-CONFIRMED-v1.7-2026-10-29.json",
        "Architecture/Stage3-Stage4-Unification/PHASE-2-3-4-READINESS-v0.1.json",
    )
    errors += validate_stage56_evidence_chain(*(load(args.root / name) for name in stage56_paths))
    historical = "Architecture/Stage3-Stage4-Unification/"
    errors += validate_stage5to7_private_lineage(
        load(args.root / (historical + "250-VERBEN-STAGE5-CONTENT-DELIVERY-v1.7.json")),
        load(args.root / (historical + "250-VERBEN-STAGE7-PRIVATE-RELEASE-v1.7.json")),
        load(args.root / stage56_paths[0]), load(args.root / stage56_paths[1]),
        load(args.root / stage56_paths[2]),
        load(args.root / (historical + "250-VERBEN-STAGE5-OUTCOME-v1.7.json")),
        load(args.root / (historical + "250-VERBEN-STAGE7-OUTCOME-v1.7.json")),
        load(args.root / (historical + "250-VERBEN-STAGE4-AI-PASS-v1.7.json")),
    )
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
