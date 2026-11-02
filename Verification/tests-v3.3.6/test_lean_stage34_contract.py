"""Nonactive structural regression for the user-approved Lean Stage3/4 policy.

This checks references and safeguards, NOT actual editorial quality or schema migration.
No content, checkpoint, runtime or filesystem writes.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class LeanOperatingCompatibility(unittest.TestCase):
    def setUp(self):
        self.pointer = json.loads(read("Prompt/KOMBINATIONEN-ACTIVE-POLICY.json"))
        self.mode = read("Prompt/LEAN-STAGE3-4-OPERATING-MODE-v1.0.0.md")
        self.didactic = read("Prompt/KOMBINATIONEN-DIDACTIC-MEHRWERT-GATE-v1.1.0.md")
        self.start = read("Prompt/START-PROMPT-v3.3.6.md")
        self.risk = json.loads(read("STAGE4-RISK-BASED-ACCEPTANCE-POLICY-v1.0.1.json"))

    def test_pointer_has_only_new_review_gate(self):
        self.assertEqual(self.pointer["didactic_delta_gate"]["policy"],
            "Prompt/KOMBINATIONEN-DIDACTIC-MEHRWERT-GATE-v1.1.0.md")
        self.assertTrue(self.pointer["didactic_delta_gate"]["no_extra_review_gate"])

    def test_legacy_scanner_not_silently_claimed_migrated(self):
        self.assertIn("HISTORICAL_SCANNER_NOT_MIGRATED", self.pointer["didactic_delta_gate"]["legacy_portable_kit_status"])
        self.assertIn("not modified here", self.didactic)

    def test_single_pass_but_legacy_outputs_still_required(self):
        self.assertIn("single working pass", self.mode)
        self.assertIn("3A/3B/3C", self.mode)
        self.assertIn("legacy-compatible", self.start)

    def test_stage4_risk_policy_is_reused(self):
        self.assertIn("STAGE4-RISK-BASED-ACCEPTANCE-POLICY-v1.0.1.json", self.didactic)
        self.assertEqual(self.risk["acceptance"]["require_100_percent_mechanical"], "YES")

    def test_high_risks_still_individual(self):
        self.assertEqual(self.risk["risk"]["family_group_closure"]["all_critical_high"], "ALWAYS_INDIVIDUAL")
        self.assertIn("CRITICAL/HIGH", self.didactic)

    def test_group_review_is_evidence_bound(self):
        self.assertEqual(self.risk["risk"]["family_group_closure"]["affected_ids"], "REQUIRED_ALL_EXACT")
        self.assertEqual(self.risk["risk"]["family_group_closure"]["independent_challenge"], "REQUIRED")

    def test_advisory_flag_not_error(self):
        self.assertTrue(self.risk["risk"]["scanner_alert_is_not_error"])
        self.assertIn("not an automatic error", self.didactic)

    def test_no_density_quota(self):
        self.assertTrue(self.pointer["no_hard_quota"])
        self.assertIn("No quantity target", self.didactic)

    def test_empty_combo_closure_with_reason(self):
        self.assertTrue(self.pointer["closed_no_force_allowed"])
        self.assertIn("NO_ADDITIONAL_TEACHING_VALUE", self.didactic)

    def test_no_fabricated_source_or_lineage_change(self):
        self.assertIn("no-fabrication", self.mode)
        self.assertIn("honest", self.didactic)

    def test_no_editorial_reaudit_of_unchanged_history(self):
        self.assertTrue(self.pointer["didactic_delta_gate"]["no_retroactive_content_reopen_without_change_or_systemic_error"])
        self.assertIn("No routine historic re-audit", self.didactic)

    def test_no_fake_stage4_or_runtime_promotion(self):
        self.assertTrue(self.risk["acceptance"]["stage5_6_7_always_separate"])
        self.assertIn("no retroactive Stage4 PASS", self.mode)

    def test_no_routine_extra_gate(self):
        self.assertTrue(self.pointer["didactic_delta_gate"]["no_extra_review_gate"])
        self.assertIn("not a second mandatory approval", read("README.md"))

    def test_no_forced_manual_nine_facets(self):
        self.assertIn("no forced repeated nine-facet prose checklists", self.mode)

    def test_immutable_source_and_ui_srs(self):
        self.assertIn("LOCKED", self.mode)
        self.assertIn("UI, SRS", self.mode)

    def test_start_prompt_points_to_new_contract(self):
        self.assertIn("LEAN-STAGE3-4-OPERATING-MODE-v1.0.0.md", self.start)
        self.assertIn("didactic overlay v1.1.0", self.start)


if __name__ == "__main__":
    unittest.main()
