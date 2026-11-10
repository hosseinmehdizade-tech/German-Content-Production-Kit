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
    def test_filename_only_artifact_is_not_byte_identity_proof(self):
        c=self.claim();c["artifact"]="UNVERIFIED-CONTENT.zip"
        with self.assertRaisesRegex(ValueError,"RELEASE_ARTIFACT_SHA256_REQUIRED"):
            self.check(c)

    def test_empty_artifact_object_has_no_exact_zip_pin(self):
        c=self.claim();c["artifact"]={"filename":"no-digest.zip"}
        with self.assertRaisesRegex(ValueError,"RELEASE_ARTIFACT_SHA256_REQUIRED"):
            self.check(c)

    def test_malformed_artifact_digest_is_rejected(self):
        c=self.claim();c["artifact"]["sha256"]="not-sha256"
        with self.assertRaisesRegex(ValueError,"RELEASE_ARTIFACT_SHA256_MALFORMED"):
            self.check(c)

    def test_missing_quality_gate_output_zip_digest_blocks_claim(self):
        self.report["governed_format_build"].pop("output_zip_sha256")
        with self.assertRaisesRegex(ValueError,"QUALITY_GATE_OUTPUT_SHA256_MISSING"):
            self.check()

    def test_quality_gate_output_must_be_sha256(self):
        self.report["governed_format_build"]["output_zip_sha256"]="short"
        with self.assertRaisesRegex(ValueError,"QUALITY_GATE_OUTPUT_SHA256_MISSING"):
            self.check()

    def test_contradictory_zip_pointers_must_not_pass(self):
        c=self.claim();c["latest_archive_sha256"]="a"*64
        with self.assertRaisesRegex(ValueError,"RELEASE_ARTIFACT_NOT_QUALITY_GATED_ZIP"):
            self.check(c)

    def test_wrong_explicit_source_tsv_pin_must_not_pass(self):
        c=self.claim();c["content_tsv_sha256"]="9"*64
        with self.assertRaisesRegex(ValueError,"RELEASE_POINTER_TSV_HASH_MISMATCH"):
            self.check(c)

    def test_quality_report_source_digest_must_be_sha256(self):
        self.report["quality_gate"]["source_tsv_sha256"]="invalid"
        self.report["governed_format_build"]["source_role_sha256"]["direct-import-tsv"]="invalid"
        with self.assertRaisesRegex(ValueError,"RELEASE_SOURCE_TSV_SHA256_INVALID"):
            self.check()

    def test_explicit_latest_archive_sha_alternative_is_valid(self):
        c=self.claim();c["artifact"]="SAME-CONTENT.zip"
        c["latest_archive_sha256"]=self.zip_sha
        x=self.check(c)
        self.assertEqual(x["release_zip_sha256"],self.zip_sha)
        self.assertEqual(x["bound_artifact_pointers"],["latest_archive_sha256"])

    def test_nested_stage5_sha_alternative_is_valid(self):
        c=self.claim();c.pop("artifact")
        c["stage5"]={"status":"PASS", "output_zip_sha256":self.zip_sha}
        x=self.check(c)
        self.assertEqual(x["bound_artifact_pointers"],["stage5.output_zip_sha256"])

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


class FullGitRangeRegressionTests(unittest.TestCase):
    def setUp(self):
        import subprocess
        self.subprocess=subprocess
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.repo=Path(tmp.name)/"repo"
        self.repo.mkdir()
        self.g("init","-q")
        self.g("config","user.email","ci@example.invalid")
        self.g("config","user.name","Synthetic CI")
        path=self.repo/"Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
        path.parent.mkdir(parents=True)
        ref=ROOT/"Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
        path.write_bytes(ref.read_bytes())
        (self.repo/"README").write_text("baseline")
        self.g("add",".")
        self.g("commit","-qm","synthetic base")
        self.base=self.g("rev-parse","HEAD").strip()
    def g(self,*args):
        return self.subprocess.run(["git",*args],cwd=self.repo,check=True,
            capture_output=True,text=True,encoding="utf-8").stdout
    def commit(self,path,content):
        p=self.repo/path
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(content,encoding="utf-8")
        self.g("add",str(path))
        self.g("commit","-qm","synthetic change")
        return self.g("rev-parse","HEAD").strip()
    def test_full_pr_base_detects_claim_hidden_in_earlier_commit(self):
        from check_new_lexical_stage5_claims_v1 import run
        stage="Workspaces/menschen-a1-verben-wortfamilie-v336/STAGE5-TEST.json"
        self.commit(stage,json.dumps({"status":"PASS_STAGE5_CONTENT_DELIVERY",
            "artifact":{"sha256":"a"*64}}))
        previous=self.g("rev-parse","HEAD").strip()
        head=self.commit("Workspaces/menschen-a1-verben-wortfamilie-v336/notes.txt",
                        "separate later commit")
        self.assertEqual(run(previous,head,self.repo)["new_claims_verified"],0)
        with self.assertRaisesRegex(ValueError,"RELEASE_QUALITY_RECEIPT_REQUIRED"):
            run(self.base,head,self.repo)
    def test_new_latest_promotion_requires_quality_proof(self):
        from check_new_lexical_stage5_claims_v1 import run
        path="Workspaces/menschen-a1-verben-wortfamilie-v336/LATEST.json"
        self.commit(path,json.dumps({"status":"STAGE4_PENDING","import_ready":False}))
        baseline=self.g("rev-parse","HEAD").strip()
        latest=self.commit(path,json.dumps({"status":"PASS_STAGE5","import_ready":True,
            "source_sha256":"1"*64}))
        with self.assertRaisesRegex(ValueError,"RELEASE_QUALITY_RECEIPT_REQUIRED"):
            run(baseline,latest,self.repo)
    def test_approved_latest_repointed_to_different_zip_requires_proof(self):
        from check_new_lexical_stage5_claims_v1 import run
        path="Workspaces/menschen-a1-verben-wortfamilie-v336/LATEST.json"
        self.commit(path,json.dumps({"status":"PASS_STAGE5","import_ready":True,
            "artifact":{"sha256":"1"*64}}))
        baseline=self.g("rev-parse","HEAD").strip()
        latest=self.commit(path,json.dumps({"status":"PASS_STAGE5","import_ready":True,
            "artifact":{"sha256":"2"*64}}))
        with self.assertRaisesRegex(ValueError,"RELEASE_QUALITY_RECEIPT_REQUIRED"):
            run(baseline,latest,self.repo)
    def test_unchanged_accepted_pointer_metadata_edit_not_release(self):
        from check_new_lexical_stage5_claims_v1 import run
        path="Workspaces/menschen-a1-verben-wortfamilie-v336/LATEST.json"
        self.commit(path,json.dumps({"status":"PASS_STAGE5","import_ready":True,
            "artifact":{"sha256":"1"*64},"date":"2026-11-01"}))
        base=self.g("rev-parse","HEAD").strip()
        head=self.commit(path,json.dumps({"status":"PASS_STAGE5","import_ready":True,
            "artifact":{"sha256":"1"*64},"date":"2026-11-08"}))
        self.assertEqual(run(base,head,self.repo)["new_claims_verified"],0)
    def test_unrelated_workspace_json_array_not_a_release(self):
        from check_new_lexical_stage5_claims_v1 import run
        head=self.commit("Workspaces/menschen-a1-verben-wortfamilie-v336/QA-DATA.json",
                         '[{"term":"sprechen"},{"term":"hören"}]')
        self.assertEqual(run(self.base,head,self.repo)["new_claims_verified"],0)
    def test_real_workflow_uses_event_name_and_full_before_sha(self):
        y=(ROOT/".github/workflows/gfp-lexical-stage5-claim-guard.yml").read_text()
        self.assertIn("EVENT_NAME: "+"${{ github.event_name }}",y)
        self.assertIn("PUSH_BEFORE: "+"${{ github.event.before }}",y)
        self.assertIn('BASE="$PUSH_BEFORE"',y)
        self.assertIn('BASE="$PR_BASE"',y)
        self.assertNotIn("BAD_${{ github.event_name }}",y)

if __name__=="__main__":unittest.main()
