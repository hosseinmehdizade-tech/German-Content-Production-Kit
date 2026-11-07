"""Regression guard for the Aspekte resume / Library-roadmap retry loop.

Offline, read-only: tests repository control-plane contracts and stable release
blockers. Never contacts or mutates private Library and never approves cards.
Run: python -B -m unittest discover -s Verification/tests -p
     'test_aspekte_sync_loop_guard_v1.py' -v
"""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "Prompt" / "ASPEKTE-RESUME-SYNC-CIRCUIT-BREAKER-v1.0.0.md"
B1 = ROOT / "Workspaces" / "aspekte-b1plus-v336"
B2 = ROOT / "Workspaces" / "aspekte-b2-v336"
C1 = ROOT / "Workspaces" / "aspekte-c1-v336"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path):
    return path.read_text(encoding="utf-8")


class AspekteAntiLoop(unittest.TestCase):
    def test_one_central_circuit_breaker_and_three_owner_routes(self):
        contract = load_text(P)
        self.assertIn("No further automatic overwrite/update/reconciliation", contract)
        self.assertIn("LIBRARY_ROADMAP_HISTORICAL_NONBLOCKING", contract)
        self.assertIn("STOP THAT DESTINATION", contract)
        self.assertIn("Kaffeeservice", contract)
        for folder in (B1, B2, C1):
            head = load_text(folder / "README.md")[:2200]
            self.assertIn(P.name, head, folder.name)
            self.assertIn("Library", head, folder.name)
        self.assertIn(P.name, load_text(ROOT / "AGENTS.md"))
        self.assertIn(P.name, load_text(ROOT / "Prompt" / "GLOBAL-POLICY-SYNCHRONIZATION-v1.0.0.md"))

    def test_b1_library_roadmap_is_not_a_resume_gate(self):
        latest = load_json(B1 / "LATEST.json")
        checkpoint = load_json(B1 / "CHECKPOINT.json")
        roadmap = load_text(B1 / "ROADMAP-TEMP.md")
        self.assertIn("**Version:** 0.15", roadmap)
        self.assertIn("Never overwrite or reconcile", roadmap)
        for obj in (latest, checkpoint):
            guard = obj["aspekte_sync_guard"]
            self.assertTrue(guard["no_library_roadmap_overwrite"])
            self.assertTrue(guard["no_resume_block_from_library_roadmap_lag"])
            self.assertEqual(guard["control_plane"], "GitHub_workstream_files")
            self.assertEqual(obj["temporary_roadmap"]["version"], "0.15")
            self.assertTrue(obj["temporary_roadmap"]["library_roadmap_historical_snapshot"])
            self.assertNotIn("verified_sha256", obj["temporary_roadmap"])
            self.assertFalse(obj["latest_G2_lexical_layer"]["import_ready"])
            self.assertEqual(obj["latest_G2_lexical_layer"]["full_card_QA_approved"], 0)
            self.assertEqual(obj["latest_G2_lexical_layer"]["cumulative_checked"],
                             latest["latest_G2_lexical_layer"]["cumulative_checked"])
        self.assertEqual(latest["aspekte_sync_guard"]["library_roadmap_last_observed_version"], 11)

    def test_b2_existing_lesson_guard_not_overridden(self):
        run = load_json(B2 / "RUN-CONTROL.json")
        guard = run["aspekte_sync_guard"]
        self.assertTrue(guard["no_library_roadmap_overwrite"])
        self.assertTrue(guard["preserve_existing_three_pass_exit_guard"])
        self.assertEqual(guard["source_of_next_action"], "RUN-CONTROL.json#next_task")
        self.assertEqual(guard["sync_attempts_max_per_destination_per_turn"], 1)
        self.assertIn("EXECUTION-EXIT-GUARD-v1.0.0.md", load_text(B2 / "README.md"))

    def test_c1_portable_curated_stage1_not_replaced(self):
        latest = load_json(C1 / "LATEST.json")
        checkpoint = load_json(C1 / "CHECKPOINT.json")
        for obj in (latest, checkpoint):
            guard = obj["aspekte_sync_guard"]
            self.assertTrue(guard["no_library_roadmap_overwrite"])
            self.assertTrue(guard["preserve_C1_curated_data_and_accepted_semantic_dispositions"])
            self.assertTrue(guard["no_raw_pdf_reingestion_for_old_source_fidelity"])
            self.assertFalse(bool(obj.get("crosslevel_semantic_final")))
        self.assertEqual(latest["stage1"], "IN_PROGRESS")


if __name__ == "__main__":
    unittest.main()
