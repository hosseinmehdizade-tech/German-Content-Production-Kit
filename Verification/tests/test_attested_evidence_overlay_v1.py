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
            if record.get("phase4_receipt_path"):
                cls.receipts[record["phase4_receipt_path"]] = mod.graph.source_json(
                    record["phase4_receipt_path"], cls.idx)
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
        self.assertEqual(result["counts"]["source_anchored_historical_git_workspaces"], 1)

    def test_three_typed_historical_receipts_have_independent_family_ids(self):
        result = self.outcome()
        self.assertEqual({e["parent_family_id"] for e in result["evidence"]},
                         {"family:250-verben-mit-praepositionen", "family:nomen-verb-verbindungen",
                          "family:aber-hallo-listen-tabellen"})

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

    def test_historical_nvv_root_receipt_cannot_be_relabelled_as_new_git_workspace(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][1]["target_type"] = "GIT_WORKSPACE"
        reg["records"][1]["target_id"] = "workspace:nomen-verb-verbindungen"
        with self.assertRaisesRegex(ValueError, "WRONG_WORKSPACE_LATEST"):
            self.outcome(reg=reg)

    def test_wrong_family_or_parent_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][0]["parent_family_id"] = "family:nomen-verb-verbindungen"
        with self.assertRaisesRegex(ValueError, "TARGET_FAMILY_MISMATCH"):
            self.outcome(reg=reg)

    def test_duplicate_target_fails_closed(self):
        reg = copy.deepcopy(self.reg)
        reg["records"].append(copy.deepcopy(reg["records"][0]))
        reg["records"][-1]["evidence_id"] = "third-duplicate-report-20261105"
        with self.assertRaisesRegex(ValueError, "MULTIPLE_RECEIPTS_FOR_SAME_TARGET"):
            self.outcome(reg=reg)

    def test_hidden_stage5_pass_in_nvv_receipt_blocks(self):
        docs = copy.deepcopy(self.receipts)
        docs[self.reg["records"][1]["receipt_path"]]["official_stage5"] = "PASS"
        with self.assertRaisesRegex(ValueError, "NVV_FALSE_STAGE_PROMOTION"):
            self.outcome(docs=docs)

    def anchor(self, result):
        return next(e for e in result["evidence"] if
                    e["target_id"] == "workspace:aber-hallo-listen-tabellen")

    def test_aber_hallo_source_anchor_not_full_or_stage_accepted(self):
        result = self.outcome()
        row = self.anchor(result)
        self.assertEqual(row["historical_evidence_status"], mod.ANCHOR_HISTORICAL)
        self.assertFalse(row["intermediate_versions_replayed"])
        self.assertFalse(row["source_to_card_semantics_certified"])
        self.assertEqual(row["stage4_risk_gate"], "OPEN__NOT_STAGE4_PASS")
        self.assertEqual(result["counts"]["historical_byte_receipts_git_workspaces"], 1)
        self.assertEqual(result["counts"]["source_anchored_historical_git_workspaces"], 1)
        self.assertEqual(result["counts"]["current_or_final_stage_certificates"], 0)
        family = next(x for x in result["families"] if
                      x["family_id"] == "family:aber-hallo-listen-tabellen")
        self.assertEqual(len(family["source_anchor_only_receipt_ids"]), 1)
        self.assertFalse(family["family_current_certified"])

    def test_aber_hallo_phase4_git_blob_tamper_blocks(self):
        idx = dict(self.idx)
        reg = self.reg["records"][-1]
        idx[reg["phase4_receipt_path"]] = "0" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_GIT_PIN_DRIFT:phase4_receipt_path"):
            self.outcome(idx=idx)

    def test_aber_hallo_phase5_git_blob_tamper_blocks(self):
        idx = dict(self.idx)
        reg = self.reg["records"][-1]
        idx[reg["receipt_path"]] = "0" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_GIT_PIN_DRIFT:receipt_path"):
            self.outcome(idx=idx)

    def test_aber_hallo_profile_git_blob_tamper_blocks(self):
        idx = dict(self.idx)
        reg = self.reg["records"][-1]
        idx[reg["profile_path"]] = "0" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_GIT_PIN_DRIFT:profile_path"):
            self.outcome(idx=idx)

    def test_aber_hallo_missing_phase4_path_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][-1]["phase4_receipt_path"] = (
            "Optimization-Program/Verification/PHASE4-ABER-HALLO-WIP92-SCOPED-BYTE-ATTESTATION-20261105.json")
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_GIT_PIN_DRIFT:phase4_receipt_path"):
            self.outcome(reg=reg)

    def test_aber_hallo_forged_family_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][-1]["parent_family_id"] = "family:menschen-a2"
        with self.assertRaisesRegex(ValueError, "TARGET_FAMILY_MISMATCH"):
            self.outcome(reg=reg)

    def test_aber_hallo_forged_source_digest_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][-1]["source_sha256s"]["b1_c2"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_SOURCE_MISMATCH:b1_c2"):
            self.outcome(reg=reg)

    def test_aber_hallo_recovery_digest_change_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][-1]["recovery_zip_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_ARCHIVE_SHA_MISMATCH:recovery_wip77"):
            self.outcome(reg=reg)

    def test_aber_hallo_wip72_parent_digest_change_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][-1]["immutable_wip72_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_ARCHIVE_SHA_MISMATCH:embedded_immutable_wip72"):
            self.outcome(reg=reg)

    def test_aber_hallo_semantic_stage4_fake_promotion_blocks(self):
        docs = copy.deepcopy(self.receipts)
        p = self.reg["records"][-1]["receipt_path"]
        docs[p]["explicit_limits"]["linguistic_stage4"] = "PASS"
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_FALSE_STAGE_OR_LINEAGE_PROMOTION"):
            self.outcome(docs=docs)

    def test_aber_hallo_intermediate_lineage_false_promotion_blocks(self):
        docs = copy.deepcopy(self.receipts)
        p = self.reg["records"][-1]["receipt_path"]
        docs[p]["explicit_limits"]["all_wip73_to_wip91_intermediate_artifact_bytes_replayed"] = True
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_FALSE_STAGE_OR_LINEAGE_PROMOTION"):
            self.outcome(docs=docs)

    def test_aber_hallo_source_to_card_false_promotion_blocks(self):
        reg = copy.deepcopy(self.reg)
        reg["records"][-1]["source_to_card_semantics_certified"] = True
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_FALSE_STAGE_OR_LINEAGE_PROMOTION"):
            self.outcome(reg=reg)

    def test_aber_hallo_phase4_source_mismatch_blocks(self):
        docs = copy.deepcopy(self.receipts)
        p = self.reg["records"][-1]["phase4_receipt_path"]
        docs[p]["sources"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_SOURCE_MISMATCH:a1_a2"):
            self.outcome(docs=docs)

    def test_aber_hallo_latest_pointer_drift_is_not_current(self):
        idx = dict(self.idx)
        idx[self.reg["records"][-1]["latest_path"]] = "f" * 40
        row = self.anchor(self.outcome(idx=idx))
        self.assertIn("REVERIFY_BEFORE_RESUME", row["git_pointer_relation"])
        self.assertFalse(row["current_user_source_automatically_resolved"])

    def test_aber_hallo_same_git_blob_but_wrong_latest_zip_blocks(self):
        docs = copy.deepcopy(self.receipts)
        record = self.reg["records"][-1]
        p = record["latest_path"]
        docs[p]["authority"]["current_portable"]["sha256"] = "0" * 64
        if self.idx.get(p) == record["latest_git_blob_at_readback"]:
            with self.assertRaisesRegex(ValueError, "SOURCE_ANCHOR_LATEST_ARTIFACT_DISAGREES_WITH_RECEIPT"):
                self.outcome(docs=docs)
        else:
            # A newer real workstream LATEST supersedes this dated WIP92 receipt.
            # Never fetch/promote stale WIP92 as CURRENT, even with a forged copy.
            result = self.outcome(docs=docs)
            row = self.anchor(result)
            self.assertIn("REVERIFY_BEFORE_RESUME", row["git_pointer_relation"])
            self.assertFalse(row["current_user_source_automatically_resolved"])

    def test_aber_hallo_no_binary_reread_in_ci(self):
        row = self.anchor(self.outcome())
        self.assertFalse(row["source_bytes_freshly_read_in_github_runner"])
        self.assertFalse(row["current_user_source_automatically_resolved"])

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
        record = self.reg["records"][0]
        p = record["latest_path"]
        docs[p]["artifact"]["sha256"] = "5" * 64
        if self.idx.get(p) == record["latest_git_blob_at_readback"]:
            with self.assertRaisesRegex(ValueError, "LATEST_ARTIFACT_DISAGREES_WITH_RECEIPT"):
                self.outcome(docs=docs)
        else:
            # Stale historical LATEST is not authoritative and must not be fetched
            # or promoted merely because this synthetic copy changed.
            row = next(r for r in self.outcome(docs=docs)["evidence"]
                       if r["target_id"] == record["target_id"])
            self.assertIn("REVERIFY_BEFORE_RESUME", row["git_pointer_relation"])

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
