"""Root checkpoint evidence: five genuine owner branches, not false CURRENT.

Mocks live GitHub REST for adversarial tests; production workflow separately
uses authenticated actual GitHub main/branch head and immutable blob reads.
"""
from __future__ import annotations
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"Verification/reconcile_live_root_checkpoints_v1.py"
spec=importlib.util.spec_from_file_location("gfp_root_branches",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class FakeGitHub:
    def __init__(self,candidates):
        self.candidates=copy.deepcopy(candidates)
        self.main="a"*40
        self.roots={}
        self.branches={}
        self.refs={self.main:None}
        self.calls={}
        self.moved_branch=None
        self.moved_main=False
        self.bad_git_blob_for=None
        self.bad_path_for=None
        self.main_now_exists=False
        self.missing_branch_for=None
        self.invalid_json_for=None
        for x in self.candidates["checkpoint_slots"]:
            cand=x["branch_candidate"]
            if cand is None:continue
            branch=cand["branch"]
            sha=hashlib.sha1(branch.encode()).hexdigest()
            payload={cand["owner_field"]:cand["owner_value"]}
            if cand.get("status_selector"):
                payload["stages"]={"7_release_post_package_verification":{
                    "state":cand["observed_source_checkpoint_status"]}}
            else:
                payload["status"]=cand["observed_source_checkpoint_status"]
            data=json.dumps(payload,sort_keys=True).encode()
            cand["checkpoint_blob"]=m.git_blob(data)
            self.branches[branch]=sha
            self.roots[(sha,x["main_declared_checkpoint"])]=data
        self.first_main=self.main

    def __call__(self,url):
        self.calls[url]=self.calls.get(url,0)+1
        if url.startswith(m.API+"/git/ref/heads/"):
            branch=unquote(url.split("/git/ref/heads/",1)[1])
            if branch=="main":
                sha=self.main
                if self.moved_main and self.calls[url]>1:sha="b"*40
            else:
                sha=self.branches.get(branch)
                if self.moved_branch==branch and self.calls[url]>1:
                    sha="c"*40
            return {"object":{"type":"commit","sha":sha}} if sha else None
        if url.startswith(m.API+"/contents/"):
            right=url.split("/contents/",1)[1]
            rel,sha=right.split("?ref=",1)
            path=unquote(rel)
            if sha==self.main:
                if not self.main_now_exists:return None
                data=b'{"status":"POSSIBLE_NEW_CHECKPOINT"}'
            else:
                if self.missing_branch_for==path:return None
                data=self.roots.get((sha,path))
                if data is None:return None
            if self.invalid_json_for==path:data=b'{"a":1,"a":2}'
            return {
              "type":"file","path":("other/"+path if self.bad_path_for==path else path),
              "encoding":"base64","content":base64.b64encode(data).decode(),
              "size":len(data),"sha":("f"*40 if self.bad_git_blob_for==path
                                  else m.git_blob(data))
            }
        raise AssertionError("UNEXPECTED_FAKE_GITHUB_URL:"+url)

class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog,cls.cat_blob=m.indexed_json(m.CATALOG)
        cls.routes,cls.route_blob=m.indexed_json(m.ROUTES)
        cls.record,_=m.indexed_json(m.CANDIDATES)

    def setup_fixture(self):
        fake=FakeGitHub(self.record)
        return fake.candidates,fake

    def replay(self,manifest,fetch):
        return m.live_report(manifest,self.catalog,self.routes,
                             self.cat_blob,self.route_blob,fetch)

    def test_all_five_real_root_labels_exact_source_authority(self):
        m.validate_sources(self.record,self.catalog,self.routes,
                           self.cat_blob,self.route_blob)
        self.assertEqual({x["root_key"] for x in self.record["checkpoint_slots"]},
                         m.EXPECTED_ISSUES)

    def test_branch_qualified_five_locator_mock_success_never_adopt(self):
        manifest,api=self.setup_fixture()
        data=self.replay(manifest,api)
        self.assertEqual(data["status"],
             "PASS_FIVE_LIVE_BRANCH_LOCATORS__ZERO_SOURCE_PROMOTION")
        self.assertEqual(data["counts"]["exact_live_branch_blob_locs"],5)
        self.assertEqual(data["counts"]["still_missing_on_main"],5)
        self.assertEqual(data["counts"]["source_current_confirmed"],0)
        self.assertEqual(data["counts"]["formal_new_policy_adoptions"],0)
        self.assertEqual(data["counts"]["root_checkpoint_files_created"],0)
        self.assertTrue(all(x["policy_adopted"] is False for x in data["roots"]))

    def test_all_five_side_branch_qualified_paths_preserved(self):
        manifest,api=self.setup_fixture()
        data=self.replay(manifest,api)
        for x in data["roots"]:
            loc=x["branch_locator"]
            self.assertIsNotNone(loc)
            self.assertTrue(loc["qualified_path"].endswith(
                             x["declared_main_path"]))
            self.assertEqual(loc["first_branch_commit"],loc["second_branch_commit"])
            self.assertEqual(x["status"],
                             "PASS_BRANCH_QUALIFIED_CHECKPOINT_BLOB_EXISTS__NOT_CURRENT")

    def test_nvv_library_newer_candidate_never_assumed_current(self):
        manifest,api=self.setup_fixture()
        r=self.replay(manifest,api)
        nvv=next(x for x in r["roots"] if x["root_key"]=="nomen_verb_verbindungen")
        self.assertIn("OLDER_BRANCH_RECORD",nvv["separate_library_newer_candidate"]["source_currentness_conflict"])
        self.assertTrue(nvv["separate_library_newer_candidate"][
                        "observation_is_provider_listing_metadata_not_content_validation"])

    def test_branch_changed_after_first_ref_is_not_accepted(self):
        manifest,api=self.setup_fixture()
        api.moved_branch="nvv-production"
        data=self.replay(manifest,api)
        nvv=next(x for x in data["roots"] if x["root_key"]=="nomen_verb_verbindungen")
        self.assertEqual(nvv["status"],"BRANCH_MOVED_DURING_READBACK__RETRY")
        self.assertEqual(data["counts"]["exact_live_branch_blob_locs"],4)
        self.assertTrue(data["status"].startswith("SOURCE_BRANCH_DRIFT"))

    def test_main_moved_during_readback_blocks_all(self):
        manifest,api=self.setup_fixture()
        api.moved_main=True
        with self.assertRaisesRegex(ValueError,"MAIN_MOVED_DURING_ROOT_RECOVERY_READBACK"):
            self.replay(manifest,api)

    def test_wrong_git_blob_cannot_pass_source_identity(self):
        manifest,api=self.setup_fixture()
        target=manifest["checkpoint_slots"][0]["main_declared_checkpoint"]
        api.bad_git_blob_for=target
        with self.assertRaisesRegex(ValueError,"GITHUB_CHECKPOINT_GIT_BLOB_INVALID"):
            self.replay(manifest,api)

    def test_valid_new_main_checkpoint_must_force_review(self):
        manifest,api=self.setup_fixture()
        api.main_now_exists=True
        result=self.replay(manifest,api)
        self.assertEqual(result["counts"]["still_missing_on_main"],0)
        self.assertEqual(result["counts"]["exact_live_branch_blob_locs"],0)
        self.assertTrue(all(x["status"]==
           "MAIN_PATH_NOW_PRESENT__ROOT_ROUTE_TRIAGE_REVIEW_REQUIRED"
           for x in result["roots"]))

    def test_branch_missing_path_cannot_pass(self):
        manifest,api=self.setup_fixture()
        path=manifest["checkpoint_slots"][0]["main_declared_checkpoint"]
        api.missing_branch_for=path
        result=self.replay(manifest,api)
        self.assertEqual(result["counts"]["exact_live_branch_blob_locs"],4)

    def test_owner_changed_but_blob_ref_is_pinned(self):
        manifest,api=self.setup_fixture()
        slot=manifest["checkpoint_slots"][0]
        slot["branch_candidate"]["owner_value"]="wrong-owner"
        result=self.replay(manifest,api)
        row=result["roots"][0]
        self.assertEqual(row["status"],"BRANCH_CHECKPOINT_OWNER_OR_STATUS_DRIFT__SOURCE_OWNER_REVIEW")

    def test_edited_observed_expected_blob_prevents_false_pass(self):
        manifest,api=self.setup_fixture()
        manifest["checkpoint_slots"][0]["branch_candidate"]["checkpoint_blob"]="a"*40
        result=self.replay(manifest,api)
        self.assertEqual(result["counts"]["exact_live_branch_blob_locs"],3)

    def test_grammar_must_use_pinned_native_status_selector(self):
        manifest,api=self.setup_fixture()
        row=next(x for x in manifest["checkpoint_slots"]
                 if x["root_key"]=="grammar_aktiv_a1_c1")
        row["branch_candidate"].pop("status_selector")
        with self.assertRaisesRegex(ValueError,"GRAMMAR_NATIVE_CHECKPOINT_SELECTOR_REQUIRED"):
            self.replay(manifest,api)

    def test_grammar_wrong_nested_stage7_never_passes(self):
        manifest,api=self.setup_fixture()
        row=next(x for x in manifest["checkpoint_slots"]
                 if x["root_key"]=="grammar_aktiv_a1_c1")
        original=row["branch_candidate"]["observed_source_checkpoint_status"]
        row["branch_candidate"]["observed_source_checkpoint_status"]="FINAL"
        result=self.replay(manifest,api)
        grammar=next(x for x in result["roots"]
                     if x["root_key"]=="grammar_aktiv_a1_c1")
        self.assertEqual(grammar["status"],
                         "BRANCH_CHECKPOINT_OWNER_OR_STATUS_DRIFT__SOURCE_OWNER_REVIEW")
        self.assertEqual(result["counts"]["exact_live_branch_blob_locs"],4)
        self.assertEqual(original,"PASS_WITH_ENVIRONMENT_BOUNDARY")

    def test_nongrammar_cannot_inject_native_status_selector(self):
        manifest,api=self.setup_fixture()
        manifest["checkpoint_slots"][0]["branch_candidate"]["status_selector"]=(
            "stages.7_release_post_package_verification.state")
        with self.assertRaisesRegex(ValueError,
                "NON_GRAMMAR_CHECKPOINT_SELECTOR_NOT_ALLOWED"):
            self.replay(manifest,api)

    def test_wrong_root_to_family_mapping_fails(self):
        manifest,api=self.setup_fixture()
        manifest["checkpoint_slots"][0]["family_id"]="family:schreiben"
        with self.assertRaisesRegex(ValueError,"ROOT_ROUTE_OWNER_OR_MISSING_MAIN_PATH"):
            self.replay(manifest,api)

    def test_root_route_catalog_version_drift_fails(self):
        manifest,api=self.setup_fixture()
        manifest["root_route_authority"]["git_blob"]="a"*40
        with self.assertRaisesRegex(ValueError,"ROOT_RECOVERY_BASELINE_PIN_DRIFT"):
            self.replay(manifest,api)

    def test_refuses_disabled_locked_guard(self):
        manifest,api=self.setup_fixture()
        manifest["safety"]["do_not_mutate_locked_sources"]=False
        with self.assertRaisesRegex(ValueError,"ROOT_RECOVERY_SAFETY_DISABLED"):
            self.replay(manifest,api)

    def test_provider_listing_not_promoted_to_current(self):
        manifest,api=self.setup_fixture()
        row=next(x for x in manifest["checkpoint_slots"]
                 if x["root_key"]=="nomen_verb_verbindungen")
        row["library_newer_candidate_observation"]["is_current_or_accepted"]="PASS"
        with self.assertRaisesRegex(ValueError,"NVV_LIBRARY_METADATA_FALSIFIED_AS_CURRENT"):
            self.replay(manifest,api)

    def test_branch_name_cannot_contain_path_or_ref_injection(self):
        manifest,api=self.setup_fixture()
        manifest["checkpoint_slots"][0]["branch_candidate"]["branch"]="../evil"
        with self.assertRaisesRegex(ValueError,"MALFORMED_BRANCH_EVIDENCE"):
            self.replay(manifest,api)

    def test_source_json_duplicate_key_fails(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_JSON_FIELD"):
            m.strict_json(b'{"status":"PASS","status":"FAKE"}')

    def test_github_claims_wrong_response_path_fails(self):
        manifest,api=self.setup_fixture()
        api.bad_path_for=manifest["checkpoint_slots"][0]["main_declared_checkpoint"]
        with self.assertRaisesRegex(ValueError,"GITHUB_UNEXPECTED_CHECKPOINT_CONTENTS"):
            self.replay(manifest,api)

    def test_source_branch_ref_bad_type_fails(self):
        manifest,api=self.setup_fixture()
        def fake(url):
            if url.endswith("/git/ref/heads/main"):
                return {"object":{"type":"tag","sha":"a"*40}}
            return api(url)
        with self.assertRaisesRegex(ValueError,"GITHUB_BRANCH_HEAD_UNAVAILABLE"):
            self.replay(manifest,fake)

if __name__=="__main__":
    unittest.main()
