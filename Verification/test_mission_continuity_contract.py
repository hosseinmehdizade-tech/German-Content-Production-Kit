"""Regression guard for user-defined chat mission vs project workstream drift.

This checks durable policy/document coherence, not the private behavior of an AI.
Run with: python -B -m unittest discover -s Verification -p test_mission_continuity_contract.py
"""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MissionContinuityContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads((ROOT / "EXECUTION-OUTCOME-EFFICIENCY-POLICY.json").read_text(encoding="utf-8"))
        cls.state = json.loads((ROOT / "Optimization-Program/STATE.json").read_text(encoding="utf-8"))
        cls.bootstrap = (ROOT / "PROJECT-BOOTSTRAP.md").read_text(encoding="utf-8")
        cls.readme = (ROOT / "Optimization-Program/README.md").read_text(encoding="utf-8")

    def test_unqualified_continue_retains_user_mission(self):
        rule = self.policy["mission_continuity"]
        self.assertTrue(rule["status"].startswith("ACTIVE_USER_CORRECTION"))
        self.assertIn("continue", rule["continue_without_subject"])
        self.assertIn("same user-established mission", rule["continue_without_subject"])
        self.assertIn("Tampermonkey", self.bootstrap)
        self.assertIn("not", rule["continue_without_subject"].lower())

    def test_assistant_handoff_is_not_user_permission(self):
        rule = self.policy["mission_continuity"]
        self.assertIn("explicit user", rule["scope_transition"].lower())
        self.assertIn("explicit user", rule["mutation_gate"].lower())
        self.assertIn("assistant", rule["mutation_gate"].lower())
        self.assertIn("USER-MISSION CONTINUITY", self.bootstrap)
        self.assertIn("Only a new explicit user request", self.bootstrap)

    def test_optimization_mission_is_not_silently_closed(self):
        self.assertEqual(self.state["active_priority"], "OP-01_OP-02")
        self.assertTrue(self.state["state"].startswith("ACTIVE_OPTIMIZATION_MISSION"))
        self.assertTrue(self.state["mission_continuity"]["require_explicit_user_switch"])
        statuses = {w["id"]: w["status"] for w in self.state["work_packages"]}
        self.assertTrue(statuses["OP-01"].startswith("ACTIVE"))
        self.assertTrue(statuses["OP-02"].startswith("ACTIVE"))

    def test_old_misrouting_instruction_explicitly_superseded(self):
        self.assertIn("## Mission and continuation invariants", self.readme)
        self.assertIn("SUPERSEDED HISTORICAL HANDOFF", self.readme)
        self.assertNotIn("Otherwise proceed with actual German content production", self.readme)
        self.assertNotIn("return ordinary ChatGPT `ادامه بده` work to the user's active German learning content", self.readme)
        self.assertIn("OP-01/OP-02", self.readme)
        self.assertIn("Never silently edit", self.readme)

    def test_content_write_is_not_implicit_regardless_of_checkpoint(self):
        mission = self.state["mission_continuity"]
        prohibited = " ".join(mission["prohibited_without_user_request"]).lower()
        self.assertIn("create learner flashcards", prohibited)
        self.assertIn("content successor zip", prohibited)
        self.assertIn("content workstream latest", prohibited)
        self.assertIn("import to user srs", prohibited)
        self.assertIn("explicit user", self.policy["mission_continuity"]["safe_exception"].lower())
        self.assertIn("explicit user", self.readme.lower())


if __name__ == "__main__":
    unittest.main()
