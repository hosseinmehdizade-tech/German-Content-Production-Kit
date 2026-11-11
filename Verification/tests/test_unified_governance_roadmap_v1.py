"""Adversarial checks: roadmap must not authorize invisible/global content migrations."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "Tools/check_unified_governance_roadmap_v1.py"
spec = importlib.util.spec_from_file_location("gfp_roadmap", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RoadmapContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roadmap = mod.read_json(ROOT, mod.ROUTE)
        cls.state = mod.read_json(ROOT, mod.PROGRAM_STATE)
        cls.catalog = mod.read_json(ROOT, mod.CATALOG)
        cls.registry = mod.read_json(ROOT, mod.REGISTRY)
        cls.routes = {path: (ROOT / path).read_text(encoding="utf-8")
                      for path in mod.REQUIRED_STARTUPS}
        cls.markdown = (ROOT / mod.MARKDOWN).read_text(encoding="utf-8")

    def check(self, roadmap=None, state=None, catalog=None, registry=None,
              routes=None, markdown=None):
        return mod.verify_roadmap(
            copy.deepcopy(self.roadmap if roadmap is None else roadmap),
            copy.deepcopy(self.state if state is None else state),
            copy.deepcopy(self.catalog if catalog is None else catalog),
            copy.deepcopy(self.registry if registry is None else registry),
            copy.deepcopy(self.routes if routes is None else routes),
            self.markdown if markdown is None else markdown)

    def test_management_first_campaign_is_live_and_all_families_in_scope(self):
        out = self.check()
        self.assertEqual(out["real_producer_adoption_proven_by_this_test"], 0)
        mg = self.roadmap["management_first_campaign_20261111"]
        self.assertEqual([g["id"] for g in mg["management_gates"]],
                         ["G0", "G1", "G2", "G3", "G4", "G5"])
        self.assertEqual(mg["baseline_provenance"]["families_total"], 21)

    def test_unqualified_optimizer_continuation_cannot_skip_management(self):
        wrong = copy.deepcopy(self.roadmap)
        wrong["management_first_campaign_20261111"]["active_phase"] = "ALL_DONE"
        with self.assertRaisesRegex(ValueError, "MANAGEMENT_FIRST_NOT_ACTIVE"):
            self.check(roadmap=wrong)

    def test_mass_release_cannot_be_mistaken_for_one_portfolio_campaign(self):
        wrong = copy.deepcopy(self.roadmap)
        wrong["management_first_campaign_20261111"]["rollout_after_management"]["simultaneous_content_edit_or_release"] = True
        with self.assertRaisesRegex(ValueError, "MANAGEMENT_ROLLOUT_UNSAFE"):
            self.check(roadmap=wrong)

    def test_manager_status_cannot_claim_new_adopted_producers_without_evidence(self):
        wrong = copy.deepcopy(self.state)
        wrong["management_first_sequencing_20261111"]["native_producers_formally_adopted"] = 21
        with self.assertRaisesRegex(ValueError, "MANAGEMENT_STATE_UNSYNCED"):
            self.check(state=wrong)

    def test_g1_all_family_paths_and_git_blobs_attested_without_release(self):
        out = self.check()
        self.assertEqual(out["management_family_routes_verified"], 21)
        self.assertEqual(out["management_git_status_document_blobs_verified"], 16)
        self.assertEqual(out["management_release_authority_or_library_holds"], 11)
        self.assertEqual(out["real_producer_adoption_proven_by_this_test"], 0)

    def test_g1_detects_forged_owner_git_blob(self):
        wrong = copy.deepcopy(self.roadmap)
        row = wrong["management_first_campaign_20261111"]["family_management_matrix_20261111"]["families"][0]
        row["source_status_git_blob"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "G1_SOURCE_DOCUMENT_BLOB_CHANGED"):
            self.check(roadmap=wrong)

    def test_g1_cannot_drop_library_only_families(self):
        wrong = copy.deepcopy(self.roadmap)
        wrong["management_first_campaign_20261111"]["family_management_matrix_20261111"]["families"].pop()
        with self.assertRaisesRegex(ValueError, "G1_INCOMPLETE_FAMILY_MATRIX"):
            self.check(roadmap=wrong)

    def test_g1_library_only_fake_owner_promotion_fails(self):
        wrong = copy.deepcopy(self.roadmap)
        fams = wrong["management_first_campaign_20261111"]["family_management_matrix_20261111"]["families"]
        row = next(x for x in fams if x["family_id"] == "family:vocabulary-sonstige")
        row["management_class"] = "OWNER_POINTER_RECORDED"
        with self.assertRaisesRegex(ValueError, "G1_FAMILY_AUTHORITY_PROMOTION"):
            self.check(roadmap=wrong)

    def test_g2_matrix_covers_every_family_and_policy_without_adoption(self):
        result = self.check()
        self.assertEqual(result["management_policy_family_classifications_verified"], 462)
        self.assertEqual(result["management_source_type_native_gates_pinned"], 4)
        self.assertEqual(result["real_producer_adoption_proven_by_this_test"], 0)

    def test_g2_wrong_lexical_rule_scope_is_rejected(self):
        wrong = copy.deepcopy(self.roadmap)
        row = wrong["management_first_campaign_20261111"]["g2_policy_to_native_producer_20261111"]["families"][0]
        row["policy_impact"]["kombinationen_source_first"] = "ROUTED_PROSPECTIVE_NO_EXECUTION_PROOF"
        with self.assertRaisesRegex(ValueError, "G2_RULE_SOURCE_TYPE_MISCLASSIFIED"):
            self.check(roadmap=wrong)

    def test_g2_missing_rule_one_family_is_rejected(self):
        wrong = copy.deepcopy(self.roadmap)
        row = wrong["management_first_campaign_20261111"]["g2_policy_to_native_producer_20261111"]["families"][0]
        row["policy_impact"].pop("curated_current_delta_qa")
        with self.assertRaisesRegex(ValueError, "G2_FAMILY_POLICY_COVERAGE"):
            self.check(roadmap=wrong)

    def test_g2_unapproved_family_cannot_claim_native_adoption(self):
        wrong = copy.deepcopy(self.roadmap)
        row = wrong["management_first_campaign_20261111"]["g2_policy_to_native_producer_20261111"]["families"][0]
        row["native_producer_adopted"] = True
        with self.assertRaisesRegex(ValueError, "G2_FALSE_NATIVE_ADOPTION"):
            self.check(roadmap=wrong)

    def test_g2_library_only_domain_cannot_use_lexical_gate(self):
        wrong = copy.deepcopy(self.roadmap)
        rows = wrong["management_first_campaign_20261111"]["g2_policy_to_native_producer_20261111"]["families"]
        row = next(x for x in rows if x["family_id"] == "family:schreiben")
        row["producer_lane"]["central_entrypoint"] = "Tools/build_quality_gated_lexical_candidate_v1.py"
        with self.assertRaisesRegex(ValueError, "G2_NATIVE_LANE_UNSAFE"):
            self.check(roadmap=wrong)

    def test_g2_cannot_fake_central_gate_git_blob(self):
        wrong = copy.deepcopy(self.roadmap)
        rows = wrong["management_first_campaign_20261111"]["g2_policy_to_native_producer_20261111"]["tested_existing_entrypoints"]
        rows[0]["git_blob"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "G2_GATE_BLOB_OR_FALSE_ADOPTION"):
            self.check(roadmap=wrong)

    def test_g3_default_deny_all_family_writer_admissions(self):
        out = self.check()
        self.assertEqual(out["management_writer_family_holds_verified"], 21)
        self.assertEqual(out["active_writer_grants_verified"], 0)
        self.assertFalse(out["cross_provider_atomic_writer_locks_proven"])

    def test_g3_fake_active_family_writer_is_rejected(self):
        wrong = copy.deepcopy(self.roadmap)
        row = wrong["management_first_campaign_20261111"]["g3_parallel_writer_isolation_20261111"]["family_routes"][0]
        row["approved_git_writer_grants"] = 1
        with self.assertRaisesRegex(ValueError, "G3_UNAUTHORIZED_FAMILY_WRITE_CLAIM"):
            self.check(roadmap=wrong)

    def test_g3_default_deny_git_writer_registry_must_not_be_forged(self):
        wrong = copy.deepcopy(self.roadmap)
        auth = wrong["management_first_campaign_20261111"]["g3_parallel_writer_isolation_20261111"]["authority"]
        auth["writer_allowlist_state"] = "ACTIVE_SCOPED_GRANTS"
        with self.assertRaisesRegex(ValueError, "G3_WRITER_SCOPE_DENY_ALL_BROKEN"):
            self.check(roadmap=wrong)

    def test_g3_cannot_swap_family_writer_workspace(self):
        wrong = copy.deepcopy(self.roadmap)
        row = wrong["management_first_campaign_20261111"]["g3_parallel_writer_isolation_20261111"]["family_routes"][0]
        row["canonical_git_workspace"] = "Workspaces/aspekte-b2-v336"
        with self.assertRaisesRegex(ValueError, "G3_WRITER_CROSSES_SOURCE_FAMILY"):
            self.check(roadmap=wrong)

    def test_g3_cannot_skip_library_only_family(self):
        wrong = copy.deepcopy(self.roadmap)
        rows = wrong["management_first_campaign_20261111"]["g3_parallel_writer_isolation_20261111"]["family_routes"]
        rows.pop()
        with self.assertRaisesRegex(ValueError, "G3_FAMILY_WRITER_MATRIX_INCOMPLETE"):
            self.check(roadmap=wrong)

    def test_g3_no_fake_atomic_github_library_lock(self):
        wrong = copy.deepcopy(self.roadmap)
        claims = wrong["management_first_campaign_20261111"]["g3_parallel_writer_isolation_20261111"]["actual_enforcement_verified"]
        claims["github_and_library_atomic_cross_provider_transaction"] = True
        with self.assertRaisesRegex(ValueError, "G3_FALSE_UNIVERSAL_WRITER_ENFORCEMENT"):
            self.check(roadmap=wrong)

    def test_g3_no_fake_external_writer_issuer(self):
        wrong = copy.deepcopy(self.roadmap)
        auth = wrong["management_first_campaign_20261111"]["g3_parallel_writer_isolation_20261111"]["authority"]
        auth["independent_required_status_check_sources"][1]["app_id"] = 15368
        with self.assertRaisesRegex(ValueError, "G3_REQUIRED_CHECK_TRUST_ORIGIN_CHANGED"):
            self.check(roadmap=wrong)

    def test_g4_g5_complete_management_without_source_adoption(self):
        result = self.check()
        self.assertEqual(result["management_g4_family_retention_holds_verified"], 21)
        self.assertEqual(result["management_g5_kickoff_families_verified"], 21)
        self.assertEqual(result["management_g5_stage_dispositions_verified"], 147)
        self.assertEqual(result["independent_content_provider_sha256_rehashed_by_this_test"], 0)
        self.assertFalse(result["app_main_branch_protected_claimed"])
        self.assertEqual(result["real_producer_adoption_proven_by_this_test"], 0)

    def test_g4_app_main_unprotected_cannot_be_misreported(self):
        wrong = copy.deepcopy(self.roadmap)
        app = wrong["management_first_campaign_20261111"]["g4_security_retention_provider_boundaries_20261111"]["application_boundary"]
        app["main_protected_flag_from_provider"] = True
        with self.assertRaisesRegex(ValueError, "G4_APP_MAIN_UNPROTECTED_OR_NONFINAL_BOUNDARY_REMOVED"):
            self.check(roadmap=wrong)

    def test_g4_never_claim_library_duplicate_without_bytes(self):
        wrong = copy.deepcopy(self.roadmap)
        record = wrong["management_first_campaign_20261111"]["g4_security_retention_provider_boundaries_20261111"]["provider_retention"]
        record["verified_reclaimable_duplicate_bytes"] = 213216245
        with self.assertRaisesRegex(ValueError, "G4_FALSE_PROVIDER_DEDUP_OR_RELEASE_CLAIM"):
            self.check(roadmap=wrong)

    def test_g4_no_source_archive_delete_permission(self):
        wrong = copy.deepcopy(self.roadmap)
        rows = wrong["management_first_campaign_20261111"]["g4_security_retention_provider_boundaries_20261111"]["per_family_preservation"]
        rows[0]["can_delete_source_or_archive"] = True
        with self.assertRaisesRegex(ValueError, "G4_UNSAFE_FAMILY_RETENTION_OR_PROMOTION"):
            self.check(roadmap=wrong)

    def test_g4_drive_metadata_not_raw_sha(self):
        wrong = copy.deepcopy(self.roadmap)
        docs = wrong["management_first_campaign_20261111"]["g4_security_retention_provider_boundaries_20261111"]["new_direct_drive_metadata_observations"]
        docs[0]["status"] = "PASS_DIRECT_SHA256"
        with self.assertRaisesRegex(ValueError, "G4_DRIVE_METADATA_MISLABELED_RAW_HASH"):
            self.check(roadmap=wrong)

    def test_g5_single_campaign_cannot_auto_edit_all_families(self):
        wrong = copy.deepcopy(self.roadmap)
        decision = wrong["management_first_campaign_20261111"]["g5_coordinated_portfolio_kickoff_20261111"]
        decision["all_21_simultaneous_writing"] = True
        with self.assertRaisesRegex(ValueError, "G5_FALSE_PORTFOLIO_GO_LIVE_CLAIM"):
            self.check(roadmap=wrong)

    def test_g5_cannot_promote_a_family_stage5_without_real_owner_qa(self):
        wrong = copy.deepcopy(self.roadmap)
        rows = wrong["management_first_campaign_20261111"]["g5_coordinated_portfolio_kickoff_20261111"]["stage_matrix"]
        rows[0]["stage_disposition"]["stage5"] = "GO_AUTOMATIC"
        with self.assertRaisesRegex(ValueError, "G5_UNAUTHORIZED_STAGE_GO"):
            self.check(roadmap=wrong)

    def test_g5_cannot_omit_an_unready_library_family(self):
        wrong = copy.deepcopy(self.roadmap)
        rows = wrong["management_first_campaign_20261111"]["g5_coordinated_portfolio_kickoff_20261111"]["stage_matrix"]
        rows.pop()
        with self.assertRaisesRegex(ValueError, "G5_MISSING_FAMILY_KICKOFF"):
            self.check(roadmap=wrong)

    def test_g5_no_fake_writer_grants_in_state(self):
        wrong = copy.deepcopy(self.state)
        record = wrong["management_first_sequencing_20261111"]["g4_g5_scoped_closeout_20261111"]
        record["direct_write_grants"] = 21
        with self.assertRaisesRegex(ValueError, "G5_STATE_FALSE_PREMATURE_SOURCE_EXECUTION"):
            self.check(state=wrong)

    def test_g5_live_source_intake_21_not_released(self):
        result = self.check()
        self.assertEqual(result["coordinated_readonly_intake_families"], 21)
        self.assertEqual(result["b2_live_stage4_completed_cards"], 864)
        self.assertEqual(result["real_producer_adoption_proven_by_this_test"], 0)

    def test_g5_b2_run_control_not_downgraded_to_old_l05(self):
        wrong = copy.deepcopy(self.roadmap)
        latest = wrong["management_first_campaign_20261111"]["coordinated_source_intake_20261111"]["actual_currentness_override"]
        latest["next_lesson"] = "L05"
        latest["already_final_stage4_cards"] = 637
        with self.assertRaisesRegex(ValueError, "G5_B2_LIVE_CURRENTNESS_DOWNGRADED"):
            self.check(roadmap=wrong)

    def test_g5_intake_cannot_enable_source_writer(self):
        wrong = copy.deepcopy(self.roadmap)
        row = wrong["management_first_campaign_20261111"]["coordinated_source_intake_20261111"]["source_specific_paths"][0]
        row["writer_approved_by_this_intake"] = True
        with self.assertRaisesRegex(ValueError, "G5_INTAKE_OWNER_OR_WRITE_AUTHORITY_FALSE"):
            self.check(roadmap=wrong)

    def test_g5_intake_cannot_claim_library_source_without_bytes(self):
        wrong = copy.deepcopy(self.roadmap)
        rows = wrong["management_first_campaign_20261111"]["coordinated_source_intake_20261111"]["source_specific_paths"]
        row = next(x for x in rows if x["family_id"] == "family:schreiben")
        row["library_observation"]["current_exact_source"] = True
        with self.assertRaisesRegex(ValueError, "G5_INTAKE_LIBRARY_CURRENT_FALSE_CLAIM"):
            self.check(roadmap=wrong)

    def test_real_cli_has_explicit_zero_adoption_claim(self):
        run = subprocess.run([sys.executable, str(FILE)], cwd=ROOT, capture_output=True,
                             text=True, timeout=60, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        result = json.loads(run.stdout)
        self.assertEqual(result["real_producer_adoption_proven_by_this_test"], 0)
        self.assertEqual(result["Stage4_5_6_7_or_CURRENT_FINAL_certificates"], 0)
        self.assertFalse(result["cross_repo_app_bootstrap_readby_this_test"])

    def test_one_program_and_seven_priorities(self):
        out = self.check()
        self.assertEqual(out["program"], "GFP-OPT-2026")
        self.assertEqual(out["roadmap_priorities"], 7)
        self.assertEqual(out["inventory"]["git_workspaces"], 36)
        self.assertEqual(out["policy_bundles_routed"], len(self.registry["policy_bindings"]))

    def test_fake_all_workspaces_adopted_is_rejected(self):
        obj = copy.deepcopy(self.roadmap)
        obj["status"] = "ALL_34_ADOPTED"
        with self.assertRaisesRegex(ValueError, "ROADMAP_FALSE_GLOBAL_PASS"):
            self.check(roadmap=obj)

    def test_auto_locked_mutation_is_rejected(self):
        obj = copy.deepcopy(self.roadmap)
        obj["global_behavior_contract"]["auto_modify_locked_content"] = True
        with self.assertRaisesRegex(ValueError, "FALSE_PRODUCER_OR_ADOPTION_CLAIM"):
            self.check(roadmap=obj)

    def test_disabling_real_producer_parity_is_rejected(self):
        obj = copy.deepcopy(self.roadmap)
        obj["global_behavior_contract"]["cross_source_output_parity_must_be_verified_with_real_producer_artifacts"] = False
        with self.assertRaisesRegex(ValueError, "FALSE_PRODUCER_OR_ADOPTION_CLAIM"):
            self.check(roadmap=obj)

    def test_fake_immediate_live_sync_is_rejected(self):
        obj = copy.deepcopy(self.roadmap)
        obj["global_behavior_contract"]["changes_cross_chat_live_without_resume"] = True
        with self.assertRaisesRegex(ValueError, "FALSE_PRODUCER_OR_ADOPTION_CLAIM"):
            self.check(roadmap=obj)

    def test_switching_priority_back_to_aber_audit_is_rejected(self):
        obj = copy.deepcopy(self.roadmap)
        obj["immediate_next_action"] = "Start another Aber Hallo lineage audit"
        with self.assertRaisesRegex(ValueError, "UNRELATED_MICRO_AUDIT_REINTRODUCED"):
            self.check(roadmap=obj)

    def test_priority_order_cannot_silently_change(self):
        obj = copy.deepcopy(self.roadmap)
        obj["roadmap"][0], obj["roadmap"][1] = obj["roadmap"][1], obj["roadmap"][0]
        with self.assertRaisesRegex(ValueError, "ROADMAP_PRIORITY_DRIFT"):
            self.check(roadmap=obj)

    def test_incomplete_start_prompt_blocks(self):
        routes = copy.deepcopy(self.routes)
        routes["Prompt/START-PROMPT-v3.3.6.md"] = "A previous ungoverned source prompt"
        with self.assertRaisesRegex(ValueError, "ROADMAP_NOT_IN_STARTUP"):
            self.check(routes=routes)

    def test_incomplete_root_bootstrap_blocks(self):
        routes = copy.deepcopy(self.routes)
        routes["PROJECT-BOOTSTRAP.md"] = "Go edit Aber Hallo cards"
        with self.assertRaisesRegex(ValueError, "ROADMAP_NOT_IN_STARTUP"):
            self.check(routes=routes)

    def test_disabling_negative_evidence_rejected(self):
        obj = copy.deepcopy(self.roadmap)
        obj["required_evidence_per_policy_rollout"] = ["Synthetic PASS"]
        with self.assertRaisesRegex(ValueError, "REAL_PRODUCER_ACCEPTANCE_EVIDENCE_MISSING"):
            self.check(roadmap=obj)

    def test_source_profile_guard_required(self):
        obj = copy.deepcopy(self.roadmap)
        obj["global_behavior_contract"]["source_profile_needed_for_real_semantic_differences"] = False
        with self.assertRaisesRegex(ValueError, "FALSE_PRODUCER_OR_ADOPTION_CLAIM"):
            self.check(roadmap=obj)

    def test_fake_stage4_approval_rejected(self):
        obj = copy.deepcopy(self.roadmap)
        obj["global_behavior_contract"]["auto_promote_stage4_to_7_or_current"] = True
        with self.assertRaisesRegex(ValueError, "FALSE_PRODUCER_OR_ADOPTION_CLAIM"):
            self.check(roadmap=obj)

    def test_incorrect_project_identity_fails(self):
        obj = copy.deepcopy(self.roadmap)
        obj["component_name"] = "Aber Hallo"
        with self.assertRaisesRegex(ValueError, "CONTROL_CENTER_NAME_MISMATCH"):
            self.check(roadmap=obj)

    def test_stale_registry_inventory_requires_review(self):
        obj = copy.deepcopy(self.roadmap)
        obj["scope"]["project_inventory_baseline"]["git_workspaces"] = 100
        with self.assertRaisesRegex(ValueError, "INVENTORY_BASELINE_DRIFT_REVIEW_REQUIRED"):
            self.check(roadmap=obj)

    def test_historical_15_rule_baseline_does_not_override_active_rule_registry(self):
        out=self.check()
        self.assertEqual(self.roadmap["scope"]["project_inventory_baseline"]
                         ["active_pinned_policy_bindings"], 15)
        self.assertGreaterEqual(out["policy_bundles_routed"],22)
        self.assertIn("curated_current_delta_qa",self.registry["policy_bindings"])

    def test_missing_current_curated_policy_must_fail(self):
        reg=copy.deepcopy(self.registry)
        reg["policy_bindings"].pop("curated_current_delta_qa")
        with self.assertRaisesRegex(ValueError,"CURATED_CURRENT_ACTIVE_ROUTING_MISSING"):
            self.check(registry=reg)

    def test_forged_state_completion_fails(self):
        obj = copy.deepcopy(self.state)
        obj["control_center_unified_governance_roadmap_20261105"]["authority_boundaries"]["no_global_34_workspace_adoption_claim"] = False
        with self.assertRaisesRegex(ValueError, "PROGRAM_STATE_FALSE_COMPLETION"):
            self.check(state=obj)


if __name__ == "__main__":
    unittest.main()
