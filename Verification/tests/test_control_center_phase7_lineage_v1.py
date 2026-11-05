"""Adversarial synthetic checks for Phase7 Git-pinned lineage receipt (no binary CI)."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "Tools/verify_control_center_lineage_evidence_v1.py"
spec = importlib.util.spec_from_file_location("control_center_lineage", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class LineageIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=mod.read(mod.INDEX)
        cls.receipt=mod.read(mod.REC)
        cls.historic=mod.read(mod.REG)

    def verify(self, index=None, receipt=None, historic=None):
        return mod.validate(
            copy.deepcopy(self.index if index is None else index),
            copy.deepcopy(self.receipt if receipt is None else receipt),
            copy.deepcopy(self.historic if historic is None else historic))

    def test_git_index_pin_unchanged(self):
        self.assertEqual(mod.validate_repo()["status"],
                         "PASS_GIT_PINNED_LINEAGE_METADATA_ONLY")

    def test_expected_counts_and_zero_stage_certificates(self):
        r=self.verify()
        self.assertEqual(r["historical_proven_links"],15)
        self.assertEqual(r["historical_unproven_links"],5)
        self.assertEqual(r["actual_library_zip_pdf_bytes_rehashed_here"],0)
        self.assertEqual(r["Stage4_to_Stage7_or_CURRENT_FINAL_certificates"],0)

    def test_missing_source_anchor_rejected(self):
        x=copy.deepcopy(self.historic)
        x["records"]=[p for p in x["records"]
                      if p.get("evidence_id")!="aber-hallo-wip92-source-anchored-historical-20261105"]
        with self.assertRaisesRegex(ValueError,"PHASE6_ANCHOR_MISSING"):
            self.verify(historic=x)

    def test_wrong_parent_sha_rejected(self):
        x=copy.deepcopy(self.receipt)
        x["links"][4]["actual_parent_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"BROKEN_PARENT_CHILD_LINK"):
            self.verify(receipt=x)

    def test_missing_intermediate_snapshot_rejected(self):
        x=copy.deepcopy(self.receipt)
        x["snapshots"].pop(7)
        with self.assertRaisesRegex(ValueError,"RECEIPT_MISSING_CONTIGUOUS_SNAPSHOTS"):
            self.verify(receipt=x)

    def test_swapped_source_role_rejected(self):
        x=copy.deepcopy(self.receipt)
        x["source_original_sha256s"]["a1_a2"]=x["source_original_sha256s"]["b1_c2"]
        with self.assertRaisesRegex(ValueError,"RECEIPT_OWNER_OR_SOURCE"):
            self.verify(receipt=x)

    def test_wip82_count_only_not_forged_to_exact_ids(self):
        x=copy.deepcopy(self.receipt)
        x["links"][4]["checkpoint_comparison"]="EXACT_CHANGED_ID_SET"
        with self.assertRaisesRegex(ValueError,"CHANGED_CARD_PROJECTION_DISAGREES"):
            self.verify(receipt=x)

    def test_false_full_chain_promotion_rejected(self):
        x=copy.deepcopy(self.receipt)
        x["claims_boundary"]["not_verified_wip72_to_wip77_edges"]=0
        with self.assertRaisesRegex(ValueError,"FALSE_STAGE_OR_FULL_CHAIN_PROMOTION"):
            self.verify(receipt=x)

    def test_false_semantic_stage4_promotion_rejected(self):
        x=copy.deepcopy(self.receipt)
        x["claims_boundary"]["stage4"]="PASS"
        with self.assertRaisesRegex(ValueError,"FALSE_STAGE_OR_FULL_CHAIN_PROMOTION"):
            self.verify(receipt=x)

    def test_false_current_final_promotion_rejected(self):
        x=copy.deepcopy(self.index)
        x["evidence"][0]["current_or_final"]=True
        with self.assertRaisesRegex(ValueError,"LINEAGE_FAKE_STAGE"):
            self.verify(index=x)

    def test_fake_library_package_sha_rejected(self):
        x=copy.deepcopy(self.receipt)
        x["reproducible_package"]["sha256"]="a"*64
        with self.assertRaisesRegex(ValueError,"REPRODUCIBLE_PACKAGE_PIN_MISMATCH"):
            self.verify(receipt=x)

    def test_fake_changed_card_count_rejected(self):
        x=copy.deepcopy(self.receipt)
        x["links"][0]["changed_canonical_ids_count"]=999
        with self.assertRaisesRegex(ValueError,"CHANGED_CARD_PROJECTION_DISAGREES"):
            self.verify(receipt=x)


if __name__=="__main__":
    unittest.main()
