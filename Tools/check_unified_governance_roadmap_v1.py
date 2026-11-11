#!/usr/bin/env python3
"""Fail-closed strategy/startup routing check, NOT proof that producers adopted policies.

The checked baseline is a declared historical inventory. All producer-level
acceptance requires separate real-output parity and stage-specific receipts.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

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
    check(management.get("active_phase") == "MGMT_G0_G5_CONTROL_PLANE_COMPLETED_WITH_EXPLICIT_HOLDS__NO_NATIVE_WRITES",
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
    # G1 live Git evidence guard: a routed family is not a released producer.
    # Verify the same 21 IDs and exact Git-file blobs recorded in the existing
    # management roadmap, without contacting private Library or reading cards.
    family_matrix = management.get("family_management_matrix_20261111", {})
    family_rows = family_matrix.get("families", [])
    check(isinstance(family_rows, list) and len(family_rows) == 21,
          "G1_INCOMPLETE_FAMILY_MATRIX")
    family_ids = [entry.get("family_id") for entry in family_rows]
    catalog_ids = [entry.get("id") for entry in catalog.get("families", [])]
    check(len(set(family_ids)) == 21 and set(family_ids) == set(catalog_ids),
          "G1_FAMILY_IDENTITIES_DRIFT")
    router_path = "Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
    check(family_matrix.get("router_path") == router_path,
          "G1_FAMILY_ROUTER_WRONG")
    router_file = ROOT / router_path
    # Git tree objects are authoritative; Windows checkout may transform LF
    # to CRLF, so hashing working-tree bytes causes false failures.
    def git_head_blob(path: str) -> str:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD:" + path], cwd=ROOT,
            text=True, encoding="utf-8").strip()
    check(git_head_blob(router_path) == family_matrix.get("router_blob"),
          "G1_FAMILY_ROUTER_CHANGED")
    router = json.loads(router_file.read_text(encoding="utf-8"))
    by_family = {item["family_id"]: item for item in router["families"]}
    check(set(by_family) == set(family_ids), "G1_ROUTER_FAMILY_MISMATCH")
    examined = 0
    kinds = {"OWNER_POINTER_RECORDED": 0,
             "RELEASE_AUTHORITY_UNATTESTED": 0,
             "LIBRARY_ONLY_CATALOG": 0}
    for entry in family_rows:
        fam_id = entry["family_id"]
        authority = by_family[fam_id]
        kind = entry.get("management_class")
        check(kind in kinds, "G1_UNSUPPORTED_CLASS:" + fam_id)
        kinds[kind] += 1
        check(entry.get("canonical_git_workspace") ==
              authority.get("canonical_git_workspace") and
              entry.get("canonical_library_root") ==
              authority.get("canonical_library_root"),
              "G1_FAMILY_ROUTE_CHANGED:" + fam_id)
        expected_kind = (
            "OWNER_POINTER_RECORDED" if
            "USER_ACCEPTED_CURATED_OWNER_PIN" in authority.get("route_state", "")
            else "LIBRARY_ONLY_CATALOG" if
            "LIBRARY_CANONICAL_ONLY" in authority.get("route_state", "")
            else "RELEASE_AUTHORITY_UNATTESTED")
        check(kind == expected_kind, "G1_FAMILY_AUTHORITY_PROMOTION:" + fam_id)
        doc = entry.get("source_status_document")
        blob = entry.get("source_status_git_blob")
        if kind == "LIBRARY_ONLY_CATALOG":
            check(doc is None and blob is None and
                  entry.get("release_authority", "").startswith("HOLD_"),
                  "G1_LIBRARY_ONLY_FALSE_PROOF:" + fam_id)
            continue
        check(isinstance(doc, str) and
              doc.startswith(authority["canonical_git_workspace"] + "/") and
              ".." not in Path(doc).parts and
              isinstance(blob, str) and len(blob) == 40,
              "G1_STATUS_SOURCE_UNSAFE:" + fam_id)
        if kind == "OWNER_POINTER_RECORDED":
            check(doc == authority.get("canonical_source_owner_document"),
                  "G1_OWNER_POINTER_CHANGED:" + fam_id)
        else:
            check(entry.get("release_authority") == "HOLD_RELEASE_AUTHORITY_UNATTESTED",
                  "G1_UNATTESTED_RELEASE_FALSE_PROMOTION:" + fam_id)
        source_file = ROOT / doc
        check(source_file.is_file() and not source_file.is_symlink() and
              git_head_blob(doc) == blob,
              "G1_SOURCE_DOCUMENT_BLOB_CHANGED:" + fam_id)
        examined += 1
    check(kinds == {"OWNER_POINTER_RECORDED": 10,
                    "RELEASE_AUTHORITY_UNATTESTED": 6,
                    "LIBRARY_ONLY_CATALOG": 5} and examined == 16 and
          family_matrix.get("source_status_documents_checked_from_live_git") == 16 and
          family_matrix.get("no_new_native_producer_adoptions") is True,
          "G1_FAMILY_COUNTS_OR_RELEASE_CLAIM")

    # G2: the EXISTING policy-impact planner supplies all 462 source-specific
    # classifications. Verify typed producer lanes and actual Git-pinned
    # candidate gates; do not infer native adoption from routing metadata.
    g2 = management.get("g2_policy_to_native_producer_20261111", {})
    g2_sources = g2.get("source_of_truth", {})
    expected_sources = {
        "registry_path": "Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json",
        "source_profile_path":
            "Optimization-Program/Control-Center/Profiles/P1-ALL-FAMILY-APPLICABILITY-v1.json",
        "planner_path": "Tools/plan_central_policy_impact_v1.py",
    }
    for key, path in expected_sources.items():
        check(g2_sources.get(key) == path and
              g2_sources.get(key.replace("_path", "_git_blob")) ==
              git_head_blob(path),
              "G2_SOURCE_PIN_DRIFT:" + key)
    planner_path = ROOT / expected_sources["planner_path"]
    spec = importlib.util.spec_from_file_location(
        "gfp_existing_policy_planner_for_management", planner_path)
    check(spec is not None and spec.loader is not None,
          "G2_PLANNER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source_profile = json.loads(
        (ROOT / expected_sources["source_profile_path"]).read_text(encoding="utf-8"))
    profiles = source_profile.get("families", [])
    check(len(profiles) == 21 and
          {row.get("id") for row in profiles} == set(family_ids),
          "G2_PROFILE_COVERAGE_CHANGED")
    declared_domains = {f["id"]: f for f in profiles}
    g2_bindings = g2.get("policy_bindings", {})
    bindings = registry.get("policy_bindings", {})
    check(isinstance(g2_bindings, dict) and
          set(g2_bindings) == set(bindings) and len(bindings) == 22,
          "G2_POLICY_BINDING_SET_DRIFT")
    for key, policy_binding in bindings.items():
        expected = {
            "scope": policy_binding["scope"],
            "stages": policy_binding["stages"],
            "path": policy_binding["path"],
            "git_blob": policy_binding["blob_sha"]
        }
        check(g2_bindings[key] == expected,
              "G2_POLICY_BINDING_CHANGED:" + key)
    gates = g2.get("tested_existing_entrypoints", [])
    expected_gate_roles = {
        "NEW_AUTHORIZED_LEXICAL_STAGE5_CANDIDATE_ONLY":
            "Tools/build_quality_gated_lexical_candidate_v1.py",
        "OPTIONAL_SOURCE_ATTESTED_FRONT_TRANSPORT":
            "Tools/build_quality_gated_front_stage5_v1.py",
        "LEXICAL_STAGE4_SOURCE_AND_CROSS_TILE_GUARD":
            "Verification/guard_lexical_rule_coverage_v1.py",
        "LEXICAL_CANONICAL_FAMILY_SCOPE_CHECK":
            "Verification/verify_lexical_family_release_route_v1.py"
    }
    check(isinstance(gates, list) and len(gates) == 4 and
          {g.get("role") for g in gates} == set(expected_gate_roles),
          "G2_MISSING_CANDIDATE_FAIL_CLOSED_GATE")
    for gate in gates:
        role = gate["role"]
        path = expected_gate_roles[role]
        check(gate.get("path") == path and
              gate.get("git_blob") == git_head_blob(path) and
              gate.get("adoption") not in ("ADOPTED", "FINAL", "STAGE5_PASS"),
              "G2_GATE_BLOB_OR_FALSE_ADOPTION:" + role)
    g2_rows = g2.get("families", [])
    check(isinstance(g2_rows, list) and len(g2_rows) == 21,
          "G2_FAMILY_COVERAGE_INCOMPLETE")
    g2_ids = [item.get("family_id") for item in g2_rows]
    check(len(set(g2_ids)) == 21 and set(g2_ids) == set(family_ids),
          "G2_FAMILY_ID_DRIFT")
    g1_by_id = {item["family_id"]: item for item in family_rows}
    exact_lanes = {
      "LEXICAL_SOURCE_CANDIDATE": (
       "CANDIDATE_CENTRAL_LEXICAL_FAIL_CLOSED_GATE_NOT_NATIVE_ADOPTED",
       "HOLD_LEXICAL_SOURCE_OWNER_AND_RELEASE_AUTHORIZATION"),
      "MIXED_SOURCE_NEEDS_OUTPUT_SPLIT":
       "HOLD_FIELD_LEVEL_SPLIT_AND_NATIVE_ADAPTER",
      "VISUAL_MEDIA_NEEDS_PROFILE": "HOLD_VISUAL_SOURCE_NATIVE_ADAPTER",
      "GRAMMAR_NEEDS_PROFILE": "HOLD_GRAMMAR_SOURCE_NATIVE_ADAPTER",
      "READING_SKILLS_NEEDS_PROFILE": "HOLD_READING_SOURCE_NATIVE_ADAPTER",
      "WRITING_SKILLS_NEEDS_PROFILE": "HOLD_WRITING_SOURCE_NATIVE_ADAPTER",
      "GENERIC_IMPORT_NATIVE_OUTPUT_UNRESOLVED":
       "HOLD_GENERIC_NATIVE_OUTPUT_AND_SOURCE_OWNER"
    }
    total_cells = 0
    for item in g2_rows:
        fid = item["family_id"]
        prof = declared_domains[fid]
        src = g1_by_id[fid]
        domain = prof["declared_domain"]
        check(item.get("declared_domain") == domain and
              item.get("management_class") == src["management_class"] and
              item.get("owner_status_git_blob") ==
              src.get("source_status_git_blob"),
              "G2_FAMILY_SOURCE_AUTHORITY_DRIFT:" + fid)
        lane = item.get("producer_lane", {})
        status = lane.get("status")
        klass = src["management_class"]
        if klass == "LIBRARY_ONLY_CATALOG":
            expected_lane = "HOLD_LIBRARY_OWNER_AND_EXACT_CURRENT_BYTES"
        elif domain == "LEXICAL_SOURCE_CANDIDATE":
            expected_lane = exact_lanes[domain][
                0 if klass == "OWNER_POINTER_RECORDED" else 1]
        else:
            expected_lane = exact_lanes[domain]
        check(status == expected_lane and
              isinstance(lane.get("required"), str) and
              bool(lane["required"]) and
              lane.get("central_entrypoint") == (
                  "Tools/build_quality_gated_lexical_candidate_v1.py"
                  if domain == "LEXICAL_SOURCE_CANDIDATE"
                  and klass != "LIBRARY_ONLY_CATALOG" else None),
              "G2_NATIVE_LANE_UNSAFE:" + fid)
        check(item.get("native_producer_adopted") is False and
              item.get("stage5_accepted_by_this_matrix") is False,
              "G2_FALSE_NATIVE_ADOPTION:" + fid)
        policies = item.get("policy_impact", {})
        check(isinstance(policies, dict) and set(policies) == set(bindings),
              "G2_FAMILY_POLICY_COVERAGE:" + fid)
        for binding_id, binding in bindings.items():
            expected_impact = module.family_decision(prof, binding)
            check(policies[binding_id] == expected_impact,
                  "G2_RULE_SOURCE_TYPE_MISCLASSIFIED:" + fid + ":" + binding_id)
            total_cells += 1
    totals = g2.get("totals", {})
    check(total_cells == 462 and totals.get("families") == 21
          and totals.get("bindings") == 22
          and totals.get("expected_policy_family_cells") == total_cells
          and totals.get("new_formal_native_adoption_count") == 0
          and totals.get("prospective_routes_only") is True,
          "G2_POLICY_MATRIX_FALSE_COMPLETION")
    check(g2.get("completion") ==
          "MANAGEMENT_FIELD_AND_GATE_MAPPING_ONLY__SOURCE_SPECIFIC_IMPLEMENTATION_AND_TESTED_ADOPTION_HOLD",
          "G2_IMPROPER_RELEASE_CLAIM")

    # G3: classify all family source-writer admission as DENY by default;
    # a PR rule is NOT an atomic lock across Git, Library or app runtime.
    g3 = management.get("g3_parallel_writer_isolation_20261111", {})
    g3_auth = g3.get("authority", {})
    expected_g3_paths = {
        "writer_allowlist_path": "Optimization-Program/WRITER-SCOPES.json",
        "tracked_writer_implementation_path":
            "Verification/persist_verified_git_edit.py",
        "synthetic_writer_negative_test_path":
            "Verification/test_persist_verified_git_edit.py",
        "canonical_router_path":
            "Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
    }
    for key, path in expected_g3_paths.items():
        check(g3_auth.get(key) == path and
              g3_auth.get(key.replace("_path", "_git_blob")) ==
              git_head_blob(path),
              "G3_WRITER_TRUST_ROOT_GIT_DRIFT:" + key)
    scopes_path = ROOT / expected_g3_paths["writer_allowlist_path"]
    scopes = json.loads(scopes_path.read_text(encoding="utf-8"))
    check(scopes.get("schema") == "gcpk-remote-git-writer-scopes@1"
          and scopes.get("status") == "DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL"
          and scopes.get("scopes") == []
          and g3_auth.get("writer_allowlist_state") == scopes["status"]
          and g3_auth.get("approved_scopes") == 0,
          "G3_WRITER_SCOPE_DENY_ALL_BROKEN")
    required_checks = g3_auth.get("independent_required_status_check_sources")
    check(g3_auth.get("main_ruleset_id") == 27024820
          and g3_auth.get("enforcement") == "active"
          and g3_auth.get("bypass_actor_count") == 0
          and required_checks == [
              {"name": "GFP-Required-Governance-Gate", "app_id": 15368},
              {"name": "Mergify Merge Protections", "app_id": 10562}],
          "G3_REQUIRED_CHECK_TRUST_ORIGIN_CHANGED")
    claims = g3.get("actual_enforcement_verified", {})
    required_true = (
        "content_kit_main_pull_request_required",
        "content_kit_main_no_bypass_actors",
        "merge_check_two_apps_required",
        "writer_scope_changes_mergify_blocked",
        "opt_in_direct_contents_writer_denies_all_without_scoped_grant",
        "synthetic_preimage_parent_cas_and_postwrite_readback_existing"
    )
    required_false = (
        "per_family_native_writer_permission_proven",
        "automatic_single_writer_lock_all_sources",
        "github_and_library_atomic_cross_provider_transaction",
        "app_repository_matching_ruleset_proven",
        "source_stage4_5_6_7_or_current_acceptance_from_this_stage"
    )
    check(all(claims.get(key) is True for key in required_true)
          and all(claims.get(key) is False for key in required_false),
          "G3_FALSE_UNIVERSAL_WRITER_ENFORCEMENT")
    family_routes = g3.get("family_routes", [])
    check(isinstance(family_routes, list) and len(family_routes) == 21,
          "G3_FAMILY_WRITER_MATRIX_INCOMPLETE")
    route_ids = [item.get("family_id") for item in family_routes]
    check(len(set(route_ids)) == 21 and set(route_ids) == set(family_ids),
          "G3_WRITER_IDENTITY_COVERAGE_DRIFT")
    g1_index = {item["family_id"]: item for item in family_rows}
    g2_index = {item["family_id"]: item for item in g2_rows}
    for item in family_routes:
        fid = item["family_id"]
        existing = g1_index[fid]
        domain = g2_index[fid]["declared_domain"]
        klass = existing["management_class"]
        check(item.get("source_domain") == domain
              and item.get("management_class") == klass
              and item.get("canonical_git_workspace") ==
              existing["canonical_git_workspace"]
              and item.get("source_status_document") ==
              existing["source_status_document"]
              and item.get("source_status_git_blob") ==
              existing["source_status_git_blob"],
              "G3_WRITER_CROSSES_SOURCE_FAMILY:" + fid)
        if klass == "LIBRARY_ONLY_CATALOG":
            expected_route = "NO_TRACKED_CANONICAL_GIT_WRITER"
            expected_admission = "HOLD_LIBRARY_CURRENT_AUTHORITY_AND_NATIVE_OWNER"
        elif klass == "RELEASE_AUTHORITY_UNATTESTED":
            expected_route = "ONE_DECLARED_CANONICAL_WORKSPACE_NOT_AN_ACTIVE_WRITER"
            expected_admission = "HOLD_SOURCE_OWNER_AND_STAGE_RELEASE_AUTHORIZATION"
        else:
            expected_route = "CANONICAL_GIT_WORKSPACE_FOR_PROPOSED_OWNER_CONTROLLED_PR"
            expected_admission = "HOLD_NO_EXACT_APPROVED_WRITER_SCOPE_OR_VALID_NEW_MUTABLE_DELTA"
        check(item.get("write_route_status") == expected_route
              and item.get("admission_status") == expected_admission,
              "G3_FAMILY_ADMISSION_NOT_HELD:" + fid)
        check(item.get("approved_git_writer_grants") == 0
              and item.get("grant_authority") == "WRITER-SCOPES_DENY_ALL"
              and item.get("parallel_writers_allowed") == 0
              and item.get("approved_grant_ref") is None
              and item.get("expected_current_parent_blob") is None
              and item.get("expected_portable_artifact_sha256") is None
              and item.get("mutable_target") ==
              "UNSELECTED_NO_OWNER_AUTHORIZED_PATH"
              and item.get("source_content_write_started") is False
              and item.get("stage5_or_current_promotion") is False,
              "G3_UNAUTHORIZED_FAMILY_WRITE_CLAIM:" + fid)
        check(isinstance(item.get("gate_before_any_future_write"), str)
              and "READBACK" in item["gate_before_any_future_write"]
              and ("CAS" in item["gate_before_any_future_write"] or
                   "EXACT_PARENT" in item["gate_before_any_future_write"]),
              "G3_MISSING_WRITER_CAS_GATE:" + fid)
    g3_totals = g3.get("totals", {})
    check(g3_totals.get("families") == 21
          and g3_totals.get("owner_pointers_recorded") == 10
          and g3_totals.get("release_authority_unattested") == 6
          and g3_totals.get("library_only") == 5
          and g3_totals.get("authorized_active_writer_grants") == 0
          and g3_totals.get("actively_admitted_family_writers") == 0
          and g3_totals.get("management_routed_family_holds") == 21
          and g3_totals.get("content_stage5_proofs_from_G3") == 0
          and g3.get("completion") ==
              "G3_MANAGEMENT_DISPOSITION_PASS_WITH_21_DEFAULT_DENY_HOLDS__NOT_UNIVERSAL_PRODUCTION_ENFORCEMENT",
          "G3_FALSE_FAMILY_WRITER_COMPLETION")
    check(len(g3.get("unavoidable_limits", [])) >= 5
          and "FRESH_BRANCH" in g3.get("admission_contract", {}).get("branch", "")
          and "PROTECTED_MAIN_PR" in g3.get("admission_contract", {}).get("pr", "")
          and "EXPECTED_GIT_BLOB" in g3.get("admission_contract", {}).get("compare_and_swap", "")
          and "EXACT_PORTABLE_PARENT_SHA" in g3.get("admission_contract", {}).get("compare_and_swap", ""),
          "G3_WRITER_RISK_CONTRACT_REMOVED")

    # G4: keep external security observations honest. CI checks the exact
    # tracked evidence and fail-closed claims, NOT remote GitHub/Drive live state.
    g4 = management.get("g4_security_retention_provider_boundaries_20261111", {})
    git_sec = g4.get("git_hard_boundary", {})
    expected_sec = [
        {"context": "GFP-Required-Governance-Gate", "integration_id": 15368},
        {"context": "Mergify Merge Protections", "integration_id": 10562},
    ]
    check(git_sec.get("main_ruleset_id") == 27024820
          and git_sec.get("main_ruleset_enforcement") == "active"
          and git_sec.get("main_protected") is True
          and git_sec.get("bypass_actors") == 0
          and git_sec.get("main_pr_rule_required") is True
          and git_sec.get("required_review_count") == 0
          and git_sec.get("strict_required_checks_policy") is False
          and git_sec.get("required_checks") == expected_sec
          and git_sec.get("external_freeze_config_path") == ".mergify.yml"
          and git_sec.get("external_freeze_config_git_blob") ==
              git_head_blob(".mergify.yml")
          and git_sec.get("external_negative_pr") ==
              {"pr": 183, "merged": False,
               "mergeable_state": "blocked", "closed": True}
          and git_sec.get("no_claim_of_atomic_cross_provider_security") is True
          and "HOLD" in git_sec.get("check_origin_issuer_for_content_current_separately", ""),
          "G4_CONTENT_MAIN_SECURITY_OR_ISSUER_CLAIM_CHANGED")
    app_sec = g4.get("application_boundary", {})
    check(app_sec.get("repo") == "hosseinmehdizade-tech/German-Flashcards-Pro"
          and app_sec.get("main_protected_flag_from_provider") is False
          and app_sec.get("rulesets_api_status") ==
              "FORBIDDEN_403__UPGRADE_PRO_OR_PUBLIC_REQUIRED"
          and app_sec.get("app_main_security") ==
              "UNPROTECTED_OR_UNATTESTED__NO_DEPLOYMENT_ISSUER_APPROVAL"
          and app_sec.get("current_runtime") ==
              "v505-R141 WORDLINKS_FRONTBACK_R3"
          and app_sec.get("current_runtime_release_final") is False
          and app_sec.get("current_main_is_exact_current_runtime") is False
          and app_sec.get("current_source_mirror_file_count") == 169
          and app_sec.get("no_live_app_import_or_srs_certification") is True,
          "G4_APP_MAIN_UNPROTECTED_OR_NONFINAL_BOUNDARY_REMOVED")
    retention = g4.get("provider_retention", {})
    known_git_paths = {
       "source_owner_contract_path":
          "Optimization-Program/Control-Center/DYNAMIC-CONTENT-PORTFOLIO-CONTRACT-v1.md",
       "curated_portfolio_path":
          "Optimization-Program/Control-Center/DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json",
       "library_dashboard_pointer_path":
          "Optimization-Program/Control-Center/Dashboard/DASHBOARD-LATEST.json"
    }
    for attr, path in known_git_paths.items():
        check(retention.get(attr) == path and
              retention.get(attr.replace("_path", "_git_blob")) ==
              git_head_blob(path),
              "G4_RETENTION_TRUSTED_POINTER_DRIFT:" + attr)
    check(retention.get("curated_portfolio_entries_10_snapshot_not_all_families") is True
          and retention.get("current_raw_library_rehash_of_all_21_completed") is False
          and retention.get("verified_reclaimable_duplicate_bytes") == 0
          and retention.get("op05_cleanup_status") ==
              "ON_HOLD_INDEPENDENT_LIBRARY_COPY_SHA_UNAVAILABLE"
          and retention.get("op05_confirmed_duplicate_groups") == 0
          and retention.get("op05_deleted_files_in_program") == 0
          and retention.get("matching_filenames_or_sizes_not_duplicate_proof") is True
          and retention.get("preserve_original_source_pdfs_and_audio") is True
          and retention.get("preserve_locked_final_current_and_protected_history") is True
          and retention.get("no_cleanup_or_trash_in_this_campaign") is True
          and retention.get("no_rewrite_accepted_source_zip") is True
          and retention.get("immutable_library_files_natively_checked_in_this_work") is False,
          "G4_FALSE_PROVIDER_DEDUP_OR_RELEASE_CLAIM")
    check("SHA256" in retention.get("deletion_requires", "")
          and "EXPLICIT_USER_SCOPE" in retention.get("deletion_requires", ""),
          "G4_DELETION_GUARD_REMOVED")
    program_op05 = next((pkg for pkg in state.get("work_packages", [])
                         if pkg.get("id") == "OP-05"), {})
    check(program_op05.get("status") ==
          retention["op05_cleanup_status"],
          "G4_OP05_STORAGE_HOLD_UNSYNCED")
    drive = g4.get("new_direct_drive_metadata_observations", [])
    check(len(drive) == 2
          and {v.get("family_id") for v in drive} ==
          {"family:menschen-a1", "family:menschen-a1-verben"}
          and all(v.get("status") ==
                  "METADATA_ID_NAME_SIZE_EXISTS__NO_NEW_RAW_SHA256"
                  and type(v.get("bytes")) is int and v["bytes"] > 0
                  for v in drive),
          "G4_DRIVE_METADATA_MISLABELED_RAW_HASH")
    curated = json.loads(
        (ROOT / known_git_paths["curated_portfolio_path"]).read_text(encoding="utf-8"))
    curated_by_id = {z["id"]: z for z in curated.get("items", [])}
    check(len(curated_by_id) == 10,
          "G4_CURATED_PORTFOLIO_OBSERVATION_COUNT_DRIFT")
    g4_rows = g4.get("per_family_preservation", [])
    check(len(g4_rows) == 21
          and {z.get("family_id") for z in g4_rows} == set(family_ids),
          "G4_FAMILY_RETENTION_COVERAGE_MISSING")
    g1_index = {z["family_id"]: z for z in family_rows}
    for row in g4_rows:
        fid = row["family_id"]
        owner = g1_index[fid]
        entry = row.get("accepted_portfolio_observation")
        historical = curated_by_id.get(fid)
        check(row.get("management_class") == owner["management_class"]
              and row.get("owner_document") ==
              owner["source_status_document"]
              and row.get("current_provider_raw_bytes_verified_by_this_g4") is False
              and row.get("current_content_promotion_by_this_g4") is False
              and row.get("can_delete_source_or_archive") is False
              and row.get("operation_before_verified_source") ==
              "READ_ONLY_MANAGEMENT_INTAKE"
              and isinstance(row.get("blocker"), str)
              and row["blocker"].startswith("HOLD_"),
              "G4_UNSAFE_FAMILY_RETENTION_OR_PROMOTION:" + fid)
        if historical is None:
            check(entry is None, "G4_UNATTESTED_HISTORICAL_ARTIFACT:" + fid)
        else:
            check(entry is not None and
                  entry.get("artifact_name") ==
                  historical["active_baseline"]["artifact_name"] and
                  entry.get("prior_observed_artifact_sha256") ==
                  historical["active_baseline"]["artifact_sha256"] and
                  entry.get("historical_provider_evidence") ==
                  historical["active_baseline"]["byte_reverification_this_registry_pass"] and
                  entry.get("source_registry_as_of_snapshot") is True,
                  "G4_HISTORICAL_PORTFOLIO_SOURCE_DRIFT:" + fid)
    check(g4.get("management_completion") ==
          "G4_SAFE_RETENTION_AND_SECURITY_HOLDS_DECLARED_FOR_ALL_21__APP_MAIN_NOT_PROTECTED__NO_AUTO_RELEASE",
          "G4_FALSE_MANAGEMENT_SECURITY_CLAIM")

    # G5: the single campaign is a conditional, read-only intake for ALL 21
    # families, not a covert writer grant, stage advance or mass ZIP release.
    g5 = management.get("g5_coordinated_portfolio_kickoff_20261111", {})
    check(g5.get("launch_state") ==
          "COORDINATED_PORTFOLIO_INTAKE_ROUTED_WITH_EXPLICIT_OWNER_RELEASE_HOLDS__NO_CONTENT_PRODUCTION"
          and g5.get("all_families_in_one_plan") is True
          and g5.get("all_21_simultaneous_writing") is False
          and g5.get("all_21_simultaneous_stage5_release") is False
          and g5.get("original_accepted_sources_immutable") is True
          and g5.get("formal_native_adoption_count") == 0,
          "G5_FALSE_PORTFOLIO_GO_LIVE_CLAIM")
    kickoff_rows = g5.get("stage_matrix", [])
    check(isinstance(kickoff_rows, list)
          and len(kickoff_rows) == 21
          and len({z.get("family_id") for z in kickoff_rows}) == 21
          and {z.get("family_id") for z in kickoff_rows} == set(family_ids),
          "G5_MISSING_FAMILY_KICKOFF")
    stage_names = {"stage" + str(n) for n in range(1, 8)}
    for row in kickoff_rows:
        fid = row["family_id"]
        owner = g1_index[fid]
        class_ = owner["management_class"]
        stage = row.get("stage_disposition", {})
        expected_first = (
            "CONDITIONAL_READ_ONLY_OWNER_INTAKE__NEW_WRITE_NOT_AUTHORIZED"
            if class_ == "OWNER_POINTER_RECORDED"
            else "HOLD_SOURCE_RELEASE_OWNER__READ_ONLY_TRIAGE"
            if class_ == "RELEASE_AUTHORITY_UNATTESTED"
            else "HOLD_LIBRARY_CURRENT_SOURCE_OWNER_AND_GIT_ROUTE__READ_ONLY_TRIAGE")
        check(row.get("source_management_class") == class_
              and row.get("canonical_git_workspace") ==
              owner["canonical_git_workspace"]
              and row.get("owner_status_document") ==
              owner["source_status_document"]
              and row.get("owner_status_git_blob") ==
              owner["source_status_git_blob"]
              and row.get("common_portfolio_intake") ==
              "INCLUDED_IN_SINGLE_COORDINATED_CAMPAIGN",
              "G5_FAMILY_SOURCE_ROUTE_WRONG:" + fid)
        check(isinstance(stage, dict) and set(stage) == stage_names
              and stage.get("stage1") == expected_first
              and all(isinstance(stage["stage" + str(n)], str)
                      and stage["stage" + str(n)].startswith("HOLD_")
                      for n in range(2, 8)),
              "G5_UNAUTHORIZED_STAGE_GO:" + fid)
        check(all(row.get(key) is val for key, val in (
             ("no_learner_card_mutation", True),
             ("no_new_stage5", True),
             ("no_automatic_zip", True),
             ("no_app_current_promotion", True),
             ("new_native_adoption_claim", False),
             ("source_current_provider_raw_approval", False)))
             and row.get("requires_preflight") ==
             next(v["blocker"] for v in g4_rows if v["family_id"] == fid),
             "G5_FALSE_FAMILY_RELEASE_PERMISSION:" + fid)
    blockers = g5.get("blocker_types", {})
    check(blockers.get("conditional_read_only_intake") == 10
          and blockers.get("existing_git_authority_hold") == 6
          and blockers.get("library_only_hold") == 5
          and blockers.get("total_writer_grants") == 0
          and blockers.get("op05_library_cleanup_hold") is True
          and blockers.get("app_main_unprotected") is True
          and blockers.get("publisher_current_issuer_hold") is True
          and g5.get("management_decision") ==
              "MANAGEMENT_FRAMEWORK_BOUNDARIES_CLOSED_AND_21_FAMILY_CONDITIONAL_INTAKE_MATRIX_ATTESTED__OPERATIONAL_RELEASES_NOT_READY",
          "G5_FALSE_MANAGEMENT_COMPLETION")
    manager_close = state.get("management_first_sequencing_20261111", {})
    close_report = manager_close.get("g4_g5_scoped_closeout_20261111", {})
    check(close_report.get("management_status") ==
          "SCOPE_COMPLETE_WITH_UNRESOLVED_EXTERNAL_HOLDS"
          and close_report.get("security_content_main_pass") is True
          and close_report.get("security_app_main_protected") is False
          and close_report.get("op05_library_cleanup_hold") is True
          and close_report.get("all_families_in_campaign") == 21
          and close_report.get("all_stages_mapped") == 147
          and close_report.get("direct_write_grants") == 0
          and close_report.get("new_content_or_release") is False,
          "G5_STATE_FALSE_PREMATURE_SOURCE_EXECUTION")

    # Live source intake: source-owned currentness overrides historical
    # management routing; no content write or producer acceptance is implied.
    intake = management.get("coordinated_source_intake_20261111", {})
    check(intake.get("status") ==
          "ONE_21_FAMILY_LIVE_STATUS_INTAKE_RECORDED__NO_CONTENT_WRITES"
          and intake.get("source_git_status_documents_live_readback_verified") == 16
          and intake.get("source_git_status_documents_matching_previous_G1_sha") == 16
          and intake.get("library_only_canonical_root_inventory_completed") == 5
          and intake.get("global_source_production_authorized_by_this_intake") is False
          and intake.get("source_provider_current_raw_bytes_reverified_by_this_intake") == 0,
          "G5_INTAKE_FALSE_SOURCE_PROOF")
    override = intake.get("actual_currentness_override", {})
    check(override.get("family_id") == "family:aspekte-b2"
          and override.get("preferred_authority") ==
              "Workspaces/aspekte-b2-v336/RUN-CONTROL.json"
          and override.get("git_blob") ==
              git_head_blob("Workspaces/aspekte-b2-v336/RUN-CONTROL.json")
          and override.get("master_version") == "7"
          and override.get("next_lesson") == "L06"
          and override.get("next_phase") == 2
          and override.get("lesson_cards") == 141
          and override.get("already_final_stage4_cards") == 864
          and override.get("total_unique_cards") == 1719
          and override.get("old_owner_LATEST_and_CHECKPOINT_outdated_for_operational_progress") is True
          and override.get("release_status") == "NONIMPORT"
          and override.get("no_source_mutation_by_this_intake") is True,
          "G5_B2_LIVE_CURRENTNESS_DOWNGRADED")
    actual_b2 = json.loads((ROOT / override["preferred_authority"]).read_text(encoding="utf-8"))
    check(actual_b2.get("next_task", {}).get("master_version") ==
          override["master_version"]
          and actual_b2["next_task"].get("authority_sha256") ==
          override.get("master_sha256")
          and actual_b2["next_task"].get("semantic_completed_total") ==
          override["already_final_stage4_cards"]
          and actual_b2["next_task"].get("current_lesson") ==
          override["next_lesson"]
          and actual_b2["next_task"].get("lesson_phase") ==
          override["next_phase"],
          "G5_B2_RUN_CONTROL_RECONCILIATION_BROKEN")
    inventory = intake.get("source_specific_paths", [])
    check(isinstance(inventory, list) and len(inventory) == 21
          and {f.get("family_id") for f in inventory} == set(family_ids)
          and len({f.get("family_id") for f in inventory}) == 21,
          "G5_INTAKE_FAMILY_COVERAGE_INCOMPLETE")
    previous_g1 = {f["family_id"]: f for f in family_rows}
    library_count = 0
    for item in inventory:
        fid = item["family_id"]
        source = previous_g1[fid]
        check(item.get("current_source_management_class") ==
              source["management_class"]
              and item.get("source_status_document") ==
              source["source_status_document"]
              and item.get("source_status_git_blob_verified_in_read_only_intake") ==
              source["source_status_git_blob"]
              and item.get("canonical_git_workspace") ==
              source["canonical_git_workspace"]
              and isinstance(item.get("read_only_action"), str)
              and bool(item["read_only_action"])
              and item.get("current_raw_source_bytes_verified_this_intake") is False
              and item.get("writer_approved_by_this_intake") is False
              and item.get("native_stage5_adopted_by_this_intake") is False,
              "G5_INTAKE_OWNER_OR_WRITE_AUTHORITY_FALSE:" + fid)
        if source["source_status_document"]:
            check(git_head_blob(source["source_status_document"]) ==
                  item["source_status_git_blob_verified_in_read_only_intake"],
                  "G5_INTAKE_OWNER_GIT_BLOB_DRIFT:" + fid)
        else:
            library_count += 1
            check(item.get("library_observation", {}).get("current_exact_source")
                  is False,
                  "G5_INTAKE_LIBRARY_CURRENT_FALSE_CLAIM:" + fid)
    check(library_count == 5 and
          intake.get("canonical_owner_counts") ==
          {"accepted_owner_pointer": 10,
           "release_owner_unattested": 6,
           "library_only_no_current": 5}
          and intake.get("safety", {}).get("no_new_adopter_or_stage5") is True
          and intake.get("safety", {}).get("originals_and_final_portables_unchanged") is True,
          "G5_INTAKE_NO_MASS_SOURCE_PROMOTION")

    # Prospective all-family Stage6 split (2026-11-12). Do not regress to
    # mandatory per-source blocked browser loops or waive true app safety.
    split = management.get("central_content_runtime_split_20261112", {})
    policy_split = registry.get("stage6_content_app_separation_20261112", {})
    req_pins = {
        "normative_seven_stage_path": "seven_stages",
        "content_delivery_policy_path": "stage5_delivery",
    }
    check(split.get("status") ==
          "GLOBAL_SCOPED_POLICY_ACTIVE_FOR_FUTURE_SOURCE_WORK__NOT_NATIVE_ADOPTION"
          and split.get("source_family_coverage") == 21
          and set(split.get("family_ids", [])) == set(family_ids)
          and len(split.get("family_ids", [])) == 21
          and policy_split.get("scope") == "ALL_21_CANONICAL_CONTENT_FAMILIES",
          "GLOBAL_RUNTIME_SPLIT_NOT_ALL_FAMILIES")
    check(split.get("active_policy_registry_path") == REGISTRY
          and split.get("active_policy_registry_git_blob") ==
          git_head_blob(REGISTRY),
          "RUNTIME_SPLIT_REGISTRY_NOT_PINNED")
    for attr, binding_id in req_pins.items():
        binding = registry["policy_bindings"][binding_id]
        path = binding.get("path")
        blob = binding.get("blob_sha")
        check(split.get(attr) == path
              and split.get(attr.replace("_path", "_git_blob")) == blob
              and policy_split.get(
                  "normative_source" if binding_id == "seven_stages"
                  else "vocabulary_delivery_policy") == path
              and policy_split.get(
                  "normative_source_blob" if binding_id == "seven_stages"
                  else "vocabulary_delivery_policy_blob") == blob
              and git_head_blob(path) == blob,
              "RUNTIME_SPLIT_POLICY_ACTIVE_BLOB_MISMATCH:" + binding_id)
    check(split.get("source_owner_content_handoff") ==
          "STAGE1_5_QA_PLUS_CONTENT_ONLY_STAGE7_PACKAGE_VERIFICATION"
          and split.get("app_owned_stage6") ==
          "GERMAN_FLASHCARDS_PRO_RUNTIME_ACCEPTANCE__NOT_PER_SOURCE_BROWSER_REPLAY"
          and split.get("content_only_stage7_may_pass_while_stage6_blocked") is True
          and policy_split.get("content_only_stage7_requires_real_app_stage6") is False
          and split.get("app_integrated_stage7_must_not_pass_unless_stage6_real_pass") is True
          and policy_split.get("app_integrated_stage7_requires_real_app_stage6") is True,
          "RUNTIME_SPLIT_FALSE_DELIVERY_SCOPE")
    check(split.get("runtime_browser_block") ==
          "BLOCKED_WITH_RECORDED_ENVIRONMENT_FINGERPRINT"
          and split.get("repeat_same_blocked_browser_attempt") is False
          and policy_split.get("retry_same_blocked_environment_and_same_app_contents") is False
          and policy_split.get("runtime_browser_block_state") == "BLOCKED"
          and policy_split.get("historical_seven_stage_enums_unchanged") is True
          and policy_split.get("native_srs_fsrs_acceptance_cannot_be_inferred") is True
          and policy_split.get("no_lock_or_content_current_mutation") is True,
          "RUNTIME_SPLIT_BLOCKED_BROWSER_RETRY_OR_FALSE_PASS")
    check(split.get("previously_accepted_source_content_immutable") is True
          and split.get("source_owner_stage4_and_stage5_required_for_new_content") is True
          and split.get("all_new_producers_formally_adopted") == 0
          and split.get("active_source_writers") == 0
          and split.get("native_stage6_reports_run_by_this_change") == 0
          and split.get("control_center_no_reruns_or_new_zip") is True
          and all(registry.get("protected_invariants", {}).get(k) is True
                  for k in (
                      "content_only_package_not_blocked_by_unrunnable_app_browser",
                      "app_integrated_release_requires_real_native_stage6",
                      "blocked_browser_tests_deduplicated_when_environment_unchanged")),
          "RUNTIME_SPLIT_UNAUTHORIZED_SOURCE_OR_APP_PROMOTION")
    # Check exact normative documents, not merely a matrix label.
    pipeline = (ROOT / registry["policy_bindings"]["seven_stages"]["path"]).read_text(
        encoding="utf-8")
    delivery = read_json(ROOT, registry["policy_bindings"]["stage5_delivery"]["path"])
    for marker in (
        "CONTENT_ONLY: 1 → 2 → 3 → 4 → 5 → 7",
        "APP_INTEGRATED: 1 → 2 → 3 → 4 → 5 → 6",
        "ERR_BLOCKED_BY_ADMINISTRATOR",
        "does **not** block",
        "APP_INTEGRATED",
        "convert synthetic/parser QA into native PASS",
    ):
        check(marker in pipeline, "RUNTIME_SPLIT_MISSING_NORMATIVE_TEXT:" + marker)
    ds = delivery.get("runtime_acceptance_separation_20261112", {})
    check(ds.get("policy") ==
          "CENTRAL_ALL_21_CONTENT_FAMILIES__PROSPECTIVE_AND_NON_DESTRUCTIVE"
          and ds.get("requires_app_stage6_for_content_only") is False
          and ds.get("requires_app_stage6_for_app_integrated") is True
          and ds.get("blocked_runtime_state") == "BLOCKED"
          and ds.get("blocked_browser_once_per_unchanged_environment") is True
          and ds.get("no_full_rebuild_from_stage6_block") is True
          and ds.get("preserve_accepted_outputs") is True
          and ds.get("no_new_app_release_or_content_acceptance_inferred_from_policy_change") is True,
          "RUNTIME_SPLIT_CONTENT_DELIVERY_INVARIANT")
    state_split = state.get("management_first_sequencing_20261111", {}).get(
        "global_content_runtime_split_20261112", {})
    check(state_split.get("source_families") == 21
          and state_split.get("stage6_central_app_owner") is True
          and state_split.get("content_only_stage7_no_runtime_gate") is True
          and state_split.get("app_integrated_needs_native_stage6_pass") is True
          and state_split.get("repeat_unchanged_blocked_browser") is False
          and state_split.get("native_adoptions_new") == 0
          and state_split.get("source_content_mutations") == 0,
          "RUNTIME_SPLIT_STATE_SYNC_MISSING")

    rollout = management.get("rollout_after_management", {})
    check(rollout.get("activate_all_families_in_common_plan") is True
          and rollout.get("simultaneous_content_edit_or_release") is False
          and rollout.get("no_new_artifacts_or_zip_until_source_authorized") is True,
          "MANAGEMENT_ROLLOUT_UNSAFE")
    manager_state = state.get("management_first_sequencing_20261111", {})
    check(manager_state.get("status") == "MANAGEMENT_G0_G5_SCOPED_COMPLETED_WITH_HOLDS__COORDINATED_INTAKE_ONLY"
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
        "management_family_routes_verified": 21,
        "management_git_status_document_blobs_verified": 16,
        "management_release_authority_or_library_holds": 11,
        "management_policy_family_classifications_verified": 462,
        "management_source_type_native_gates_pinned": 4,
        "management_writer_family_holds_verified": 21,
        "active_writer_grants_verified": 0,
        "cross_provider_atomic_writer_locks_proven": False,
        "management_g4_family_retention_holds_verified": 21,
        "management_g5_kickoff_families_verified": 21,
        "management_g5_stage_dispositions_verified": 147,
        "coordinated_readonly_intake_families": 21,
        "runtime_split_policy_applies_to_families": 21,
        "content_only_stage7_requires_real_browser": False,
        "app_integrated_stage7_requires_real_browser": True,
        "repeat_identical_blocked_browser_attempt": False,
        "b2_live_stage4_completed_cards": 864,
        "app_main_branch_protected_claimed": False,
        "independent_content_provider_sha256_rehashed_by_this_test": 0,
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
