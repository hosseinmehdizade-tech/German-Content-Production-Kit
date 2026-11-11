#!/usr/bin/env python3
"""Fail-closed strategy/startup routing check, NOT proof that producers adopted policies.

The checked baseline is a declared historical inventory. All producer-level
acceptance requires separate real-output parity and stage-specific receipts.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = "Optimization-Program/CONTROL-CENTER-UNIFIED-GOVERNANCE-ROADMAP-v1.0.0.json"
MARKDOWN = ROUTE.removesuffix(".json") + ".md"
PROGRAM_STATE = "Optimization-Program/STATE.json"
CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
REGISTRY = "Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
REQUIRED_STARTUPS = (
    "PROJECT-BOOTSTRAP.md",
    "Prompt/START-PROMPT-v3.3.6.md",
    "Optimization-Program/README.md",
)

def check(condition: bool, name: str) -> None:
    if not condition:
        raise ValueError(name)

def read_json(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))

def verify_roadmap(r: dict, state: dict, catalog: dict, registry: dict, routes: dict[str, str], md: str) -> dict:
    check(r.get("schema") == "gfp-opt-unified-governance-roadmap@1.0.0", "ROADMAP_SCHEMA_INVALID")
    check(r.get("program_id") == state.get("program_id") == "GFP-OPT-2026", "PROGRAM_ID_MISMATCH")
    check(r.get("program_name") == "German Flashcards — Continuous Optimization Program", "PROGRAM_NAME_MISMATCH")
    check(r.get("component_name") == "Project Control Center", "CONTROL_CENTER_NAME_MISMATCH")
    check(r.get("authority") == "USER_DIRECTED_CROSS_REPOSITORY_OPTIMIZATION_MISSION__PROSPECTIVE_ONLY", "ROADMAP_WRONG_AUTHORITY")
    check(r.get("status") == "ACTIVE_ROADMAP__NOT_GLOBAL_ADOPTION_OR_END_TO_END_EXECUTION_PASS", "ROADMAP_FALSE_GLOBAL_PASS")
    check(r.get("canonical_document") == MARKDOWN, "ROADMAP_MD_POINTER")
    check(r.get("scope", {}).get("repos") == [
        "hosseinmehdizade-tech/German-Content-Production-Kit",
        "hosseinmehdizade-tech/German-Flashcards-Pro"], "CROSS_REPO_SCOPE_MISMATCH")
    observed = dict(library_content_families=len(catalog.get("families", [])),
                    git_workspaces=len(catalog.get("workspaces", [])),
                    root_workstreams=len(catalog.get("root_workstreams", [])),
                    active_pinned_policy_bindings=len(registry.get("policy_bindings", {})))
    # v1 historical inventory is a dated baseline; new centrally approved
    # policies do NOT invalidate old catalog history or justify rereading books.
    # Compare identities against that baseline but validate active policy count
    # against the exact current registry instead of demanding the old count.
    baseline=r.get("scope", {}).get("project_inventory_baseline", {})
    historical={k:baseline.get(k) for k in
                ("library_content_families","git_workspaces","root_workstreams")}
    today={k:observed[k] for k in historical}
    # The original 21/35/17 inventory remains historical. Only a separately
    # reviewed, exact R164 identity addition permits the current 36th directory.
    reconciliation=r.get("scope",{}).get("inventory_reconciliation_20261107",{})
    current_workspace_ok=(
        today["git_workspaces"]==historical["git_workspaces"]
        or (
            historical["git_workspaces"]==35
            and today["git_workspaces"]==36
            and reconciliation.get("previous_catalog_count_before_r164")==35
            and reconciliation.get("live_catalog_git_workspace_count")==36
            and reconciliation.get("last_added_git_dir")==
                "Workspaces/menschen-a2-verben-r164-front-back-successor-v336"
        )
    )
    check(today["library_content_families"]==historical["library_content_families"]
          and today["root_workstreams"]==historical["root_workstreams"]
          and current_workspace_ok
          and isinstance(baseline.get("active_pinned_policy_bindings"), int)
          and observed["active_pinned_policy_bindings"] >= baseline["active_pinned_policy_bindings"],
          "INVENTORY_BASELINE_DRIFT_REVIEW_REQUIRED")
    check("curated_current_delta_qa" in registry.get("policy_bindings",{}),
          "CURATED_CURRENT_ACTIVE_ROUTING_MISSING")
    check(r.get("scope", {}).get("baseline_type") ==
          "HISTORICAL_CATALOG_AND_REGISTRY_COUNTS__NOT_ALL_PRODUCERS_ADOPTED", "BASELINE_WRONG_CONFIDENCE")
    check(registry.get("schema") == "gcpk-global-policy-registry@1.0.0"
          and registry.get("status") is not None, "POLICY_REGISTRY_NOT_ACTIVE")
    steps = r.get("roadmap")
    check(isinstance(steps, list) and [x.get("id") for x in steps] ==
          ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]
          and [x.get("priority") for x in steps] == list(range(7)), "ROADMAP_PRIORITY_DRIFT")
    check(steps[1].get("status") == "OPEN_NEXT" and
          "policy" in steps[1].get("title", "").lower(), "P1_EXECUTION_NOT_NEXT")
    check("P1" in r.get("immediate_next_action", "") and
          "not another Aber Hallo" in r.get("immediate_next_action", ""), "UNRELATED_MICRO_AUDIT_REINTRODUCED")
    policy = r.get("global_behavior_contract", {})
    expectations = {
        "single_instruction_governs_applicable_future_runs": True,
        "changes_cross_chat_live_without_resume": False,
        "source_profile_needed_for_real_semantic_differences": True,
        "auto_modify_locked_content": False,
        "auto_modify_existing_current_content_without_scope": False,
        "auto_promote_stage4_to_7_or_current": False,
        "cross_source_output_parity_must_be_verified_with_real_producer_artifacts": True,
        "policy_text_only_is_not_producer_adoption": True,
    }
    for k, v in expectations.items():
        check(policy.get(k) is v, "FALSE_PRODUCER_OR_ADOPTION_CLAIM:" + k)
    check("OP-01/OP-02" in policy.get("dispatch_in_optimizer_chat", ""),
          "OPTIMIZER_MISSION_CONTINUITY_BROKEN")

    # 2026-11-11 user's management-first campaign is a stricter order of work
    # inside the unchanged OP-01/OP-02 optimization mission, not producer
    # admission or an invitation to release content.
    management = r.get("management_first_campaign_20261111", {})
    check(management.get("active_phase") == "MGMT_READINESS_G0_TO_G5__NOT_COMPLETE",
          "MANAGEMENT_FIRST_NOT_ACTIVE")
    gate_ids = [item.get("id") for item in management.get("management_gates", [])]
    check(gate_ids == ["G0", "G1", "G2", "G3", "G4", "G5"],
          "MANAGEMENT_GATE_ORDER_OR_COVERAGE_CHANGED")
    baseline = management.get("baseline_provenance", {})
    check(baseline.get("families_total") == 21
          and baseline.get("family_authority_classes", {}).get("accepted_owner_pointer_present") == 10
          and baseline.get("family_authority_classes", {}).get("stage_release_authority_unattested") == 6
          and baseline.get("family_authority_classes", {}).get("library_only_no_git_workspace") == 5
          and baseline.get("registered_policy_bindings") == len(registry.get("policy_bindings", {}))
          and baseline.get("formally_adopted_native_producers") == 0,
          "MANAGEMENT_BASELINE_FALSE_COVERAGE")
    rollout = management.get("rollout_after_management", {})
    check(rollout.get("activate_all_families_in_common_plan") is True
          and rollout.get("simultaneous_content_edit_or_release") is False
          and rollout.get("no_new_artifacts_or_zip_until_source_authorized") is True,
          "MANAGEMENT_ROLLOUT_UNSAFE")
    manager_state = state.get("management_first_sequencing_20261111", {})
    check(manager_state.get("status") == "ACTIVE_MANAGEMENT_ONLY__G0_G5_OPEN__NOT_COMPLETE"
          and manager_state.get("roadmap_path") == ROUTE
          and manager_state.get("all_family_scope") == 21
          and manager_state.get("native_producers_formally_adopted") == 0
          and manager_state.get("no_stage5_source_execution_during_management") is True,
          "MANAGEMENT_STATE_UNSYNCED")
    check("MANAGEMENT-FIRST" in policy.get("dispatch_in_optimizer_chat", "")
          and "MANAGEMENT-FIRST" in r.get("immediate_next_action", "")
          and "MANAGEMENT-FIRST" in state.get("next_exact_action", ""),
          "MANAGEMENT_FIRST_PRIORITY_DRIFT")
    statuses = r.get("roll_out_states", [])
    check(statuses == ["NOT_ROUTED", "ROUTED_ONLY", "ADAPTER_IMPLEMENTED_SYNTHETIC",
                       "REAL_OUTPUT_PARITY_VERIFIED", "QA_GATE_ENFORCED_AT_ELIGIBLE_BOUNDARY",
                       "BLOCKED_CONFLICT_OR_SOURCE", "NOT_APPLICABLE"],
          "ADOPTION_TYPES_CHANGED")
    check(len(r.get("required_evidence_per_policy_rollout", [])) >= 7,
          "REAL_PRODUCER_ACCEPTANCE_EVIDENCE_MISSING")
    snapshot = state.get("control_center_unified_governance_roadmap_20261105", {})
    check(snapshot.get("roadmap_json") == ROUTE and snapshot.get("roadmap_markdown") == MARKDOWN
          and snapshot.get("program_id") == r["program_id"], "PROGRAM_STATE_NOT_ROUTED")
    check(snapshot.get("immediate_next", "").startswith("P1:") and
          snapshot.get("authority_boundaries", {}).get("no_global_34_workspace_adoption_claim") is True
          and snapshot.get("authority_boundaries", {}).get("no_original_or_locked_or_card_edit") is True,
          "PROGRAM_STATE_FALSE_COMPLETION")
    for path in REQUIRED_STARTUPS:
        s = routes.get(path)
        check(isinstance(s, str) and ROUTE in s and "GFP-OPT-2026" in s,
              "ROADMAP_NOT_IN_STARTUP:" + path)
    check("CONTROL-CENTER-UNIFIED-GOVERNANCE-ROADMAP-v1.0.0.json" in md and
          "P1" in md and "P2" in md and "P3" in md and
          "LOCKED" in md and "not" in md.lower(),
          "ROADMAP_DOCUMENT_DISAGREES")
    return {
        "result": "PASS_ROADMAP_AND_CONTENT_KIT_STARTUP_ROUTING_ONLY",
        "program": r["program_id"],
        "component": r["component_name"],
        "roadmap_priorities": len(steps),
        "content_repo_startup_files_checked": len(REQUIRED_STARTUPS),
        "inventory": observed,
        "policy_bundles_routed": observed["active_pinned_policy_bindings"],
        "real_producer_adoption_proven_by_this_test": 0,
        "learner_card_edits_authorized_by_this_test": 0,
        "Stage4_5_6_7_or_CURRENT_FINAL_certificates": 0,
        "cross_repo_app_bootstrap_readby_this_test": False,
    }

def main() -> None:
    import sys
    root = ROOT
    try:
        r = read_json(root, ROUTE)
        state = read_json(root, PROGRAM_STATE)
        catalog = read_json(root, CATALOG)
        registry = read_json(root, REGISTRY)
        routes = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED_STARTUPS}
        md = (root / MARKDOWN).read_text(encoding="utf-8")
        result = verify_roadmap(r, state, catalog, registry, routes, md)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("ROADMAP_ROUTING_FAIL: " + str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
