"""New accepted source claims cannot use an old format-only Stage5 ZIP as proof."""
from __future__ import annotations
import hashlib,json,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Verification"))
from check_new_lexical_stage5_claims_v1 import release_check,promoted,sha,json_obj

class NewClaimProofTests(unittest.TestCase):
    def setUp(self):
        self.owner="Workspaces/menschen-a1-verben-wortfamilie-v336"
        route=json.loads((ROOT/"Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json").read_text())
        self.route=route
        family=next(f for f in route["families"] if f["family_id"]=="family:menschen-a1-verben")
        self.family=family
        self.receipt_path=self.owner+"/Stage5/LEXICAL-QUALITY-CURRENT.json"
        self.zip_sha="e"*64
        self.report={"schema":"gcpk-lexical-quality-gated-stage5-candidate@1.0.0",
           "status":"PASS_STAGE5_CANDIDATE_WITH_EXACT_SOURCE_STAGE4_AND_RULE_COVERAGE",
           "family_authority":{"family_id":family["family_id"],
              "canonical_git_workspace":self.owner,"parent_sha256":family["active_content_sha256"]},
           "quality_gate":{"status":"PASS_FOR_GOVERNED_STAGE5_CANDIDATE_ONLY",
              "source_tsv_sha256":"1"*64,"blockers":[]},
           "governed_format_build":{"status":"PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY",
              "source_role_sha256":{"direct-import-tsv":"1"*64},
              "output_zip_sha256":self.zip_sha,"linguistic_stage4":"NOT_CERTIFIED"},
           "exact_stage4_receipt_sha256":"2"*64,
           "exact_cross_tile_review_sha256":"3"*64}
    def raw(self):
        return json.dumps(self.report,sort_keys=True).encode("utf-8")
    def path(self):
        return self.owner+"/STAGE5-NEW-ACCEPTANCE.json"
    def claim(self):
        return {"status":"PASS_STAGE5_CONTENT_DELIVERY","artifact":{"sha256":self.zip_sha},
          "release_quality_receipt":{"path":self.receipt_path,"sha256":sha(self.raw())}}
    def check(self,claim=None):
        return release_check(self.path(),claim or self.claim(),None,lambda p:self.raw(),self.route)
    def test_valid_complete_new_release_proof(self):
        x=self.check()
        self.assertEqual(x["status"],"PASS_EXACT_SOURCE_LEXICAL_STAGE5_CLAIM_RECEIPT_BOUND")
        self.assertEqual(x["family"],self.family["family_id"])
    def test_new_release_without_receipt_blocked(self):
        c=self.claim();c.pop("release_quality_receipt")
        with self.assertRaisesRegex(ValueError,"RELEASE_QUALITY_RECEIPT_REQUIRED"):
            self.check(c)
    def test_wrong_receipt_hash_blocked(self):
        c=self.claim();c["release_quality_receipt"]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"BYTES_MISMATCH"):self.check(c)
    def test_receipt_different_workstream_blocked(self):
        c=self.claim();c["release_quality_receipt"]["path"]="Workspaces/aspekte-b2-v336/quality.json"
        with self.assertRaisesRegex(ValueError,"WRONG_OWNER"):self.check(c)
    def test_bad_current_parent_blocked(self):
        self.report["family_authority"]["parent_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"CURRENTNESS_MISMATCH"):self.check()
    def test_forged_stage4_pass_on_format_wrapper_blocked(self):
        self.report["governed_format_build"]["linguistic_stage4"]="PASS"
        with self.assertRaisesRegex(ValueError,"FAKES_STAGE4"):self.check()
    def test_stage4_proof_missing_blocked(self):
        self.report.pop("exact_stage4_receipt_sha256")
        with self.assertRaisesRegex(ValueError,"STAGE4_OR_CROSS_TILE_PROOF_MISSING"):self.check()
    def test_cross_tile_proof_missing_blocked(self):
        self.report.pop("exact_cross_tile_review_sha256")
        with self.assertRaisesRegex(ValueError,"STAGE4_OR_CROSS_TILE_PROOF_MISSING"):self.check()
    def test_source_tsv_mismatch_blocked(self):
        self.report["governed_format_build"]["source_role_sha256"]["direct-import-tsv"]="0"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_TSV_HASH_MISMATCH"):self.check()
    def test_format_only_report_without_quality_gate_blocked(self):
        self.report["quality_gate"]["status"]="BLOCKED"
        with self.assertRaisesRegex(ValueError,"CONTENT_QA_OR_NATIVE_FORMAT_GATE_NOT_PASS"):self.check()
    def test_wrong_zip_in_acceptance_claim_blocked(self):
        c=self.claim();c["artifact"]["sha256"]="a"*64
        with self.assertRaisesRegex(ValueError,"NOT_QUALITY_GATED_ZIP"):self.check(c)
    def test_old_accepted_unchanged_status_not_retroactive(self):
        c=self.claim();self.assertFalse(promoted(c,c,self.path()))
    def test_new_nonimport_draft_not_promotion(self):
        self.assertFalse(promoted({"status":"EDITORIAL_DRAFT_NONIMPORT"},None,self.path()))
    def test_new_stage3_receipt_not_promotion(self):
        self.assertFalse(promoted({"status":"PASS_STAGE3"},None,self.owner+"/STAGE3.json"))
    def test_import_ready_new_latest_is_promotion(self):
        p=self.owner+"/LATEST.json"
        self.assertTrue(promoted({"import_ready":True},{"import_ready":False},p))
    def test_latest_draft_not_promotion(self):
        p=self.owner+"/LATEST.json"
        self.assertFalse(promoted({"import_ready":False},{"import_ready":False},p))
    def test_duplicate_proof_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_JSON_KEY"):
            json_obj(b'{"status":"PASS","status":"BLOCKED"}')

if __name__=="__main__":unittest.main()
