#!/usr/bin/env python3
"""Fail-closed regression tests for central 21-family currentness visibility."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "Tools" / "reconcile_cop_family_currentness_v1.py"
spec = importlib.util.spec_from_file_location("cop_currentness", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class FamilyCurrentnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.catalog = {"families": []}
        self.portfolio = {"items": []}
        self.routing = {"families": []}
        self.evidence = {"schema": m.SCHEMA, "date": "2026-11-23",
                         "data_edit_authorized": False, "items": []}
        self.legacy_sha = "a" * 64
        self.work_sha = "b" * 64
        for i in range(21):
            fid = "family:test-" + str(i)
            workspace = "Workspaces/source-" + str(i)
            libpath = "/Flasch kart/Content/Source-" + str(i)
            self.catalog["families"].append({"id": fid, "library_path": libpath})
            route = {"family_id": fid, "canonical_library_root": libpath,
                     "canonical_git_workspace": workspace, "canonical_source_owner_document": None,
                     "active_content_sha256": None}
            if i < 10:
                ownerpath = workspace + "/LATEST.json"
                sha = self.legacy_sha if i == 0 else hex(i)[2:].zfill(64)
                ownerdoc = {"selected": {"sha256": sha}}
                raw = (json.dumps(ownerdoc, sort_keys=True) + "\n").encode()
                self.raw(ownerpath, raw)
                route["canonical_source_owner_document"] = ownerpath
                route["active_content_sha256"] = sha
                self.portfolio["items"].append({
                    "id": fid,
                    "owner_locator": {"path": ownerpath, "git_blob_observed": m.git_blob(raw),
                                      "artifact_sha_json_pointer": "/selected/sha256"},
                    "active_baseline": {"artifact_sha256": sha}})
            self.routing["families"].append(route)
        self.write(m.CATALOG, self.catalog)
        self.write(m.PORTFOLIO, self.portfolio)
        self.write(m.ROUTING, self.routing)
        self.add_observation(0, self.legacy_sha)
        self.add_observation(1, self.work_sha)
        self.write(m.OBSERVATIONS, self.evidence)

    def raw(self, rel, content):
        f = self.root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)

    def write(self, rel, j):
        self.raw(rel, (json.dumps(j, sort_keys=True) + "\n").encode())

    def add_observation(self, i, sha, kind="working", accepted=False):
        fid = "family:test-" + str(i)
        evidence_path = "Workspaces/source-" + str(i) + "/CURRENT-RECEIPT.json"
        self.write(evidence_path, {"content": {"zip_sha256": sha}})
        obs = {"family_id": fid, "kind": kind, "provider": "google_drive",
               "observed_as_of": "2026-11-22", "name": "source-" + str(i) + ".zip",
               "sha256": sha, "locator": "https://drive.google.com/file/d/example/view",
               "evidence_path": evidence_path, "evidence_json_pointer": "/content/zip_sha256",
               "accepted_successor_decision": accepted}
        if accepted:
            obs["approval_receipt"] = "Workspaces/source-" + str(i) + "/approval.json"
        self.evidence["items"] = [o for o in self.evidence["items"] if o["family_id"] != fid] + [obs]

    def test_all_21_covered_and_unknown_not_certified(self):
        report = m.inspect(self.root)
        self.assertEqual(report["total_catalog_families"], 21)
        self.assertEqual(report["selected_accepted_baselines"], 10)
        self.assertEqual(report["recorded_as_of_families"], 2)
        self.assertEqual(report["counts"]["GIT_MATCH"], 10)
        self.assertEqual(report["counts"]["NO_SELECTED_BASELINE"], 11)
        self.assertEqual(report["counts"]["CURRENT_NOT_VERIFIED"], 19)
        self.assertEqual(report["counts"]["WORKING_DIFFERS_ACCEPTED__NO_AUTO_PROMOTION"], 1)
        self.assertFalse(report["all_21_live_current_verified"])
        self.assertEqual(report["status"], "GIT_POINTERS_MATCH__LIVE_PROVIDER_CURRENTNESS_INCOMPLETE")
        self.assertEqual(report["blocking_families"], [])

    def test_b1_style_newer_working_not_forced_to_accepted(self):
        row = next(x for x in m.inspect(self.root)["families"] if x["family_id"] == "family:test-1")
        self.assertEqual(row["working_status"], "WORKING_DIFFERS_ACCEPTED__NO_AUTO_PROMOTION")
        self.assertNotEqual(row["working_observed_sha256"], row["accepted_baseline_sha256"])
        self.assertEqual(row["git_sync"], "GIT_MATCH")

    def test_stale_owner_without_registry_change_is_failing_hold(self):
        self.write("Workspaces/source-0/LATEST.json", {"selected": {"sha256": self.work_sha}})
        result = m.inspect(self.root)
        row = next(x for x in result["families"] if x["family_id"] == "family:test-0")
        self.assertIn("SELECTED_OWNER_SHA_DRIFT", row["findings"])
        self.assertIn("SELECTED_OWNER_BLOB_DRIFT", row["findings"])
        self.assertEqual(result["status"], "CURRENTNESS_HOLD_GIT_OR_RECORDED_ACCEPTANCE_DRIFT")

    def test_route_pin_drift_is_failing_hold(self):
        self.routing["families"][0]["active_content_sha256"] = self.work_sha
        self.write(m.ROUTING, self.routing)
        self.assertIn("CANONICAL_ARTIFACT_PIN_DRIFT", m.inspect(self.root)["families"][0]["findings"])

    def test_source_claim_must_be_backed_by_exact_receipt(self):
        self.evidence["items"][0]["sha256"] = self.work_sha
        self.write(m.OBSERVATIONS, self.evidence)
        report = m.inspect(self.root)
        self.assertIn("WORKING_SOURCE_RECEIPT_MISMATCH", report["families"][0]["findings"])

    def test_recognized_accepted_successor_is_review_hold_not_auto_promotion(self):
        self.add_observation(0, self.work_sha, kind="accepted_successor", accepted=True)
        self.write(m.OBSERVATIONS, self.evidence)
        report = m.inspect(self.root)
        self.assertEqual(report["families"][0]["working_status"], "ACCEPTED_SUCCESSOR_NOT_SYNCED_HOLD")
        self.assertIn("family:test-0", report["blocking_families"])
        self.assertEqual(self.portfolio["items"][0]["active_baseline"]["artifact_sha256"], self.legacy_sha)

    def test_fake_accepted_successor_without_explicit_decision_rejected(self):
        self.add_observation(0, self.work_sha, kind="accepted_successor", accepted=False)
        self.write(m.OBSERVATIONS, self.evidence)
        with self.assertRaises(ValueError):
            m.inspect(self.root)

    def test_duplicate_or_unmapped_family_evidence_rejected(self):
        self.evidence["items"].append(copy.deepcopy(self.evidence["items"][0]))
        self.write(m.OBSERVATIONS, self.evidence)
        with self.assertRaises(ValueError):
            m.inspect(self.root)

    def test_external_reports_readonly_and_no_in_repo_output(self):
        self.root.joinpath("reference.lock").write_bytes(b"immutable")
        before = (self.root / m.PORTFOLIO).read_bytes()
        out = self.root.parent / "outside"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.main(["--repo-root", str(self.root), "--fail-on-drift",
                                     "--out-dir", str(out)]), 0)
        self.assertTrue((out / "COP-CURRENTNESS-21-FAMILY.json").exists())
        self.assertEqual((self.root / m.PORTFOLIO).read_bytes(), before)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.main(["--repo-root", str(self.root),
                                     "--out-dir", str(self.root / "bad")]), 2)
        self.assertFalse((self.root / "bad").exists())

    def test_parent_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            m.source_path(self.root, "Workspaces/../secrets")
        with self.assertRaises(ValueError):
            m.source_path(self.root, "/etc/passwd")
        with self.assertRaises(ValueError):
            m.source_path(self.root, "Workspaces\\bad")

if __name__ == "__main__":
    unittest.main()
