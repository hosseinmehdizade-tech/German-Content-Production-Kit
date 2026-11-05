"""Metadata-only Phase8 adversarial Git-pinned lineage tests for both OS runners."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/"Tools/verify_control_center_phase8_lineage_v1.py"
spec=importlib.util.spec_from_file_location("phase8_lineage_metadata",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class Phase8LedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.idx=mod.p7.read(mod.INDEX)
        cls.rec=mod.p7.read(mod.RECEIPT)
        cls.prev=mod.p7.read(mod.P7_RECEIPT)
    def validate(self,i=None,r=None,p=None):
        return mod.validate(copy.deepcopy(self.idx if i is None else i),
                            copy.deepcopy(self.rec if r is None else r),
                            copy.deepcopy(self.prev if p is None else p))

    def test_actual_git_index_pins(self):
        self.assertEqual(mod.validate_repo()["status"],
                         "PASS_PINNED_PHASE8_METADATA_ONLY__NO_REAL_BINARY_CI")

    def test_counts_and_zero_stage(self):
        result=self.validate()
        self.assertEqual(result["verified_historical_edges_WIP77_to_WIP95"],18)
        self.assertEqual(result["unverified_earlier_edges"],5)
        self.assertEqual(result["native_or_release_certificates"],0)
        self.assertEqual(result["ci_real_pdf_or_library_zip_rereads"],0)

    def test_duplicate_or_missing_lineage_records_blocks(self):
        x=copy.deepcopy(self.idx)
        x["evidence"].pop(0)
        with self.assertRaisesRegex(ValueError,"PHASE8_INDEX_RECORD_COUNT"):
            self.validate(i=x)

    def test_false_complete_chain_promotion_blocks(self):
        x=copy.deepcopy(self.rec)
        x["explicit_limits"]["fully_contiguous_wip72_to_wip95"]=True
        with self.assertRaisesRegex(ValueError,"PHASE8_FALSE_STAGE_OR_CONTIGUITY"):
            self.validate(r=x)

    def test_fake_full_stage4_blocks(self):
        x=copy.deepcopy(self.idx)
        x["evidence"][1]["full_stage4"]=True
        with self.assertRaisesRegex(ValueError,"PHASE8_FALSE_STAGE_PROMOTION"):
            self.validate(i=x)

    def test_wrong_parent_receipt_sha_blocks(self):
        x=copy.deepcopy(self.rec)
        x["parent_evidence"]["git_blob_sha"]="a"*40
        with self.assertRaisesRegex(ValueError,"PHASE8_PARENT_LINEAGE_BREAK"):
            self.validate(r=x)

    def test_wip93_nonmetadata_exception_not_hidden(self):
        x=copy.deepcopy(self.rec)
        x["edges"][0]["only_metadata_changes"]=True
        with self.assertRaisesRegex(ValueError,"PHASE8_WIP93_NON_METADATA_EXCEPTION_HIDDEN"):
            self.validate(r=x)

    def test_wrong_qa_mismatch_count_blocks(self):
        x=copy.deepcopy(self.rec)
        x["snapshots"][3]["rection_qa_mismatched_ids"]=["ahl-lu-0278"]
        with self.assertRaisesRegex(ValueError,"PHASE8_RECTION_MIRROR_CLAIM_CHANGED"):
            self.validate(r=x)

    def test_fake_94_95_parent_link_blocks(self):
        x=copy.deepcopy(self.rec)
        x["edges"][2]["child"]=94
        with self.assertRaisesRegex(ValueError,"PHASE8_MISSING_OR_WRONG_EDGES"):
            self.validate(r=x)

    def test_wrong_manifest_members_blocks(self):
        x=copy.deepcopy(self.rec)
        x["snapshots"][1]["zip_members"]=109
        with self.assertRaisesRegex(ValueError,"PHASE8_MANIFEST_COUNTS"):
            self.validate(r=x)

    def test_wrong_library_attestation_blocks(self):
        x=copy.deepcopy(self.rec)
        x["locally_verified_package"]["library_sync"]="PASS_EXACT_READBACK"
        with self.assertRaisesRegex(ValueError,"PHASE8_PACKAGE_OR_LIBRARY_ATTESTATION_NOT_GROUNDED"):
            self.validate(r=x)

    def test_false_browsed_ui_pass_blocks(self):
        x=copy.deepcopy(self.rec)
        x["cross_snapshot_constraints"]["wip95_browser_render_and_downstream_hidden_field_effects"]="PASS"
        with self.assertRaisesRegex(ValueError,"PHASE8_COUNTS_OR_DISPLAY_BOUNDARY_CHANGED"):
            self.validate(r=x)

    def test_fake_source_hash_blocks(self):
        x=copy.deepcopy(self.rec)
        x["actual_original_pdf_sha256s"]["b1_c2"]="0"*64
        with self.assertRaisesRegex(ValueError,"PHASE8_ORIGINAL_SOURCE_DRIFT"):
            self.validate(r=x)

    def test_parent_phase7_history_cannot_change(self):
        x=copy.deepcopy(self.prev)
        x["snapshots"][-1]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"PHASE8_PARENT_LINEAGE_BREAK"):
            self.validate(p=x)

    def test_package_sha_tamper_rejected(self):
        x=copy.deepcopy(self.rec)
        x["locally_verified_package"]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"PHASE8_PACKAGE_OR_LIBRARY_ATTESTATION_NOT_GROUNDED"):
            self.validate(r=x)

if __name__=="__main__":unittest.main()
