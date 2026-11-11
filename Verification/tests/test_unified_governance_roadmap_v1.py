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
