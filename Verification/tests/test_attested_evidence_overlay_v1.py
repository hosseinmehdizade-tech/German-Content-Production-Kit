"""Adversarial cross-project exact historical evidence overlay tests."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "Tools/build_attested_evidence_overlay_v1.py"
spec = importlib.util.spec_from_file_location("attested_evidence_overlay", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AttestedEvidenceOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.idx = mod.graph.index_blobs()
        cls.cat = mod.graph.source_json(mod.graph.CATALOG, cls.idx)
        cls.reg = mod.graph.source_json(mod.REGISTRY, cls.idx)
        cls.receipts = {r["receipt_path"]: mod.graph.source_json(r["receipt_path"], cls.idx)
                        for r in cls.reg["records"]}
        cls.receipts.update({r["profile_path"]: mod.graph.source_json(r["profile_path"], cls.idx)
                             for r in cls.reg["records"]})
        for record in cls.reg["records"]:
            if record.get("latest_path"):
                cls.receipts[record["latest_path"]] = mod.graph.source_json(
                    record["latest_path"], cls.idx)

    def outcome(self, reg=None, cat=None, idx=None, docs=None):
        reg = copy.deepcopy(self.reg if reg is None else reg)
        cat = copy.deepcopy(self.cat if cat is None else cat)
        idx = dict(self.idx if idx is None else idx)
        docs = copy.deepcopy(self.receipts if docs is None else docs)
        return mod.build(reg, cat, idx, lambda path: docs.get(path))

    def test_exact_git_receipts_and_profiles_match_in_current_index(self):
        result = self.outcome()
        self.assertEqual(result["counts"]["historical_byte_receipts_git_workspaces"], 1)
        self.assertEqual(result["counts"]["historical_byte_receipts_root_workstreams"], 1)
        self.assertEqual(result["counts"]["unattested_git_workspaces"], 33)

    def test_two_historical_receipts_have_independent_family_ids(self):
        result = self.outcome()
        self.assertEqual({e["parent_family_id"] for e in result["evidence"]},
                         {"family:250-verben-mit-praepositionen", "family:nomen-verb-verbindungen"})

    def test_nv_root_workstream_not_faked_as_git_workspace(self):
        result = self.outcome()
        nvv = next(x for x in result["evidence"] if x["target_id"] == "root:nomen_verb_verbindungen")
        self.assertEqual(nvv["git_pointer_relation"], "NO_NATIVE_GIT_LATEST__ROOT_SUMMARY_NOT_PORTABLE_CURRENT")
        self.assertFalse(nvv["current_user_source_automatically_resolved"])

    def test_no_stage_approval_is_issued_from_bytes(self):
        result = self.outcome()
        self.assertEqual(result["counts"]["current_or_final_stage_certificates"], 0)
        self.assertTrue(all(e["stage5_final"] == "NOT_ATTESTED_BY_OVERLAY" for e in result["evidence"]))
        self.assertTrue(all(not x["current_or_stage_verified"] for x in result["workspace_evidence"]))

    def test_zero_fresh_readback_from_git_ci_is_explicit(self):
        result = self.outcome()
        self.assertEqual(result["counts"]["fresh_pdf_zip_bytes_rehashed_by_github_ci"], 0)
        self.assertTrue(all(not x["source_bytes_freshly_read_in_github_runner"] for x in result["evidence"]))

    def test_profile_blob_tamper_blocks(self):
        idx = dict(self.idx)
        idx[self.reg["records"][0]["profile_path"]] = "a" * 40
        with self.assertRaisesRegex(ValueError, "EVIDENCE_GIT_PIN_DRIFT:profile_path"):
            self.outcome(idx=idx)

    def test_receipt_blob_tamper_blocks(self):
        idx = dict(self.idx)
        idx[self.reg["records"][1]["receipt_path"]] = "f" * 40
        with self.assertRaisesRegex(ValueError, "EVIDENCE_GIT_PIN_DRIFT:receipt_path"):
            self.outcome(idx=idx)

    def test_receipt_source_sha_change_blocks(self):
        docs = copy.deepcopy(self.receipts)
        p = self.reg["records"][1]["receipt_path"]
        docs[p]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "RECEIPT_SHA_MISMATCH:source_sha256"):
            self.outcome(docs=docs)

    def test_profile_artifact_sha_change_blocks(self):
        docs = copy.deepcopy(self.receipts)
        p = self.reg["records"][0]["profile_path"]
        docs[p]["artifact_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "PROFILE_SHA_MISMATCH:artifact_sha256"):
            self.outcome(docs=docs)

    def test_unsafe_evidence_relative_path_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][0]["receipt_path"] = "../outside.json"
        with self.assertRaisesRegex(ValueError, "UNSAFE_EVIDENCE_PATH"):
            self.outcome(reg=reg)

    def test_forged_nv_git_workspace_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][1]["target_type"] = "GIT_WORKSPACE"
        reg["records"][1]["target_id"] = "workspace:nomen-verb-verbindungen"
        with self.assertRaisesRegex(ValueError, "UNREGISTERED_GIT_WORKSPACE_TARGET"):
            self.outcome(reg=reg)

    def test_wrong_family_or_parent_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][0]["parent_family_id"] = "family:nomen-verb-verbindungen"
        with self.assertRaisesRegex(ValueError, "TARGET_FAMILY_MISMATCH"):
            self.outcome(reg=reg)

    def test_duplicate_target_fails_closed(self):
        reg = copy.deepcopy(self.reg)
        reg["records"].append(copy.deepcopy(reg["records"][0]))
        reg["records"][2]["evidence_id"] = "third-duplicate-report-20261105"
        with self.assertRaisesRegex(ValueError, "MULTIPLE_RECEIPTS_FOR_SAME_TARGET"):
            self.outcome(reg=reg)

    def test_hidden_stage5_pass_in_nvv_receipt_blocks(self):
        docs = copy.deepcopy(self.receipts)
        docs[self.reg["records"][1]["receipt_path"]]["official_stage5"] = "PASS"
        with self.assertRaisesRegex(ValueError, "NVV_FALSE_STAGE_PROMOTION"):
            self.outcome(docs=docs)

    def test_missing_b1_attestation_remains_unverified(self):
        result = self.outcome()
        b1 = next(x for x in result["workspace_evidence"]
                  if x["target_id"] == "workspace:menschen-b1-24-lessons-v336")
        self.assertEqual(b1["evidence_status"], mod.NONE)
        self.assertFalse(b1["current_or_stage_verified"])

    def test_changed_workstream_latest_is_historical_supersession_not_full_pass(self):
        idx = dict(self.idx)
        idx[self.reg["records"][0]["latest_path"]] = "3" * 40
        result = self.outcome(idx=idx)
        old = next(x for x in result["evidence"] if x["target_id"] ==
                   "workspace:250-verben-mit-praepositionen-lexical-enrichment-v1")
        self.assertIn("REVERIFY_BEFORE_RESUME", old["git_pointer_relation"])
        self.assertEqual(result["counts"]["current_or_final_stage_certificates"], 0)

    def test_changed_latest_artifact_without_pointer_pin_change_blocks(self):
        docs = copy.deepcopy(self.receipts)
        p = self.reg["records"][0]["latest_path"]
        docs[p]["artifact"]["sha256"] = "5" * 64
        with self.assertRaisesRegex(ValueError, "LATEST_ARTIFACT_DISAGREES_WITH_RECEIPT"):
            self.outcome(docs=docs)

    def test_markdown_is_deterministic_and_does_not_mutate_snapshot(self):
        result = self.outcome()
        old = copy.deepcopy(result)
        text = mod.markdown(result)
        self.assertEqual(result, old)
        self.assertIn("not CURRENT", text.lower().replace("not current", "not CURRENT"))
        self.assertIn("Nomen-Verb-Verbindungen", text)

    def test_real_cli_output_never_writes_into_checkout(self):
        root = ROOT / "Workspaces" / "forbidden-evidence-overlay"
        run = subprocess.run([sys.executable, str(FILE), "--output-dir", str(root)],
                             cwd=ROOT, capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 2)
        self.assertIn("GIT_WORKTREE_OUTPUT_FORBIDDEN", run.stderr)
        self.assertFalse(root.exists())

    def test_real_cli_builds_two_reports_outside_git(self):
        with tempfile.TemporaryDirectory(prefix="evidence-overlay-v1-") as td:
            run = subprocess.run([sys.executable, str(FILE), "--check", "--output-dir", td],
                                 cwd=ROOT, capture_output=True, text=True, timeout=120)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            self.assertTrue((Path(td) / "ATTESTED-EVIDENCE.json").exists())
            self.assertTrue((Path(td) / "ATTESTED-EVIDENCE.md").exists())


if __name__ == "__main__":
    unittest.main()
