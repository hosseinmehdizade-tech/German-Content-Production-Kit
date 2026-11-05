"""Independent remote Git main+separate Library-copy byte parity for governed P1.

All tests use simulated GitHub REST responses and SYNTHETIC generated source
fixtures. They never assert authenticated real Library provenance or CURRENT.
"""
from __future__ import annotations

import base64
import copy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"Verification/verify_remote_policy_adoption_v1.py"
spec=importlib.util.spec_from_file_location("gfp_opt_remote",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAMILY="family:250-verben-mit-praepositionen"
WORKSPACE="workspace:250-verben-mit-praepositionen-lexical-enrichment-v1"
WORKDIR="Workspaces/250-verben-mit-praepositionen-lexical-enrichment-v1"
LIBPATH="/Flasch kart/German-Content-Production-Kit/Content/250-Verben-mit-Praepositionen/TEST/TEST-STAGE5-DELIVERY.zip"
LIBID="libfile_testnotproviderproof"
FILEID="file_testnotproviderproof"

def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def native_tsv():
    out=io.StringIO(newline="")
    fields=("id","front","back","card_type","category","details","custom_fields","source")
    w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n")
    w.writeheader()
    for n in range(2):
        w.writerow({
            "id":"c-"+str(n),"front":"kommen","back":"آمدن",
            "card_type":"de-vocabulary","category":"Verb",
            "details":json.dumps([{"title":"Bedeutung","items":["kommen"]}]),
            "custom_fields":json.dumps({"presentation_contract":"gfp-vocabulary-neutral@1"}),
            "source":"Synthetic P1 producer fixture"
        })
    return out.getvalue().encode("utf-8")

class FakeGithub:
    def __init__(self,pointer:dict):
        self.pointer=copy.deepcopy(pointer)
        self.head="a"*40
        self.moves_on_second_ref=False
        self.bad_blob=False
        self.bad_path=False
        self.bad_size=False
        self.refs=0

    def __call__(self,url):
        if url==m.API+"/git/ref/heads/main":
            self.refs+=1
            return {"object":{"type":"commit","sha":
                 ("b"*40 if self.moves_on_second_ref and self.refs>1 else self.head)}}
        if url.startswith(m.API+"/contents/"+WORKDIR+"/LATEST.json?ref="):
            data=(json.dumps(self.pointer,ensure_ascii=False,sort_keys=True)+"\n").encode("utf-8")
            return {
                "type":"file","path":("another/LATEST.json" if self.bad_path else WORKDIR+"/LATEST.json"),
                "encoding":"base64","content":base64.b64encode(data).decode("ascii"),
                "sha":("c"*40 if self.bad_blob else git_blob(data)),
                "size":len(data)+(1 if self.bad_size else 0)
            }
        raise AssertionError("FAKE_GITHUB_REJECTS_UNEXPECTED_URL:"+url)

class RemotePolicyReadbackTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.home=Path(t.name)
        self.src=self.home/"src"
        self.src.mkdir()
        for name,data in {
            "TEST-IMPORT.tsv":native_tsv(),
            "TEST-CANONICAL.json":b'{"cards":[]}',
            "TEST-SOURCE-OUTPUT-MAP.tsv":b"id\tsource\n",
            "TEST-VERIFICATION.json":b'{"qa":"synthetic"}'
        }.items():
            (self.src/name).write_bytes(data)
        self.out=self.home/"TEST-STAGE5-DELIVERY.zip"
        self.receipt=self.home/"native-receipt.json"
        self.native=m.local.governed.run(self.src,self.out,self.receipt)
        self.library=self.home/"separate-library-materialization"/self.out.name
        self.library.parent.mkdir()
        shutil.copyfile(self.out,self.library)
        self.pointer={
            "schema":"gcpk-workstream-latest@1.0.0",
            "workstream":WORKDIR.split("/")[-1],
            "status":"PASS_STAGE5_GOVERNED_CONTRACT__NOT_STAGE6",
            "artifact":{
                "filename":self.out.name,
                "bytes":self.out.stat().st_size,
                "sha256":self.native["output_zip_sha256"],
                "library_file_id":LIBID,
                "library_path":LIBPATH
            }
        }
        self.github=FakeGithub(self.pointer)

    def run_remote(self,**updates):
        kwargs={
            "family_id":FAMILY,
            "workspace_id":WORKSPACE,
            "source_dir":self.src,
            "archive":self.out,
            "native_receipt":self.receipt,
            "library_copy":self.library,
            "library_file_id":FILEID,
            "library_record_id":LIBID,
            "library_path":LIBPATH,
            "fetch":self.github
        }
        kwargs.update(updates)
        return m.verify(**kwargs)

    def test_exact_e2e_github_main_and_materialized_copy_but_no_adoption(self):
        result=self.run_remote()
        self.assertEqual(result["status"],
             "PASS_LIVE_GITHUB_MAIN_AND_SEPARATE_LIBRARY_COPY_BYTE_PARITY__ADOPTION_HELD")
        self.assertEqual(result["actual_native_cards"],2)
        self.assertTrue(result["remote_main_checked_twice_without_movement"])
        self.assertEqual(result["github_main_commit_sha"],"a"*40)
        self.assertEqual(result["actual_governed_zip_sha256"],self.native["output_zip_sha256"])
        self.assertIn("HELD_PENDING_AUTHENTICATED_LIBRARY_PROVENANCE",
                      result["formal_source_level_policy_adoption"])
        self.assertFalse(result["all_21_families_adopted"])
        self.assertEqual(self.github.refs,2)

    def test_lib_materialization_is_not_automatically_provider_authenticated(self):
        result=self.run_remote()
        self.assertEqual(
             result["library_copy_proof"]["library_provider_authentication_by_this_script"],
             "NOT_AVAILABLE__COPY_AND_IDS_OPERATOR_SUPPLIED")

    def test_correct_live_github_blob_matches_exact_pointer(self):
        _,sha,blob=m.github_pointer(WORKDIR,self.github)
        self.assertEqual(sha,"a"*40)
        body=(json.dumps(self.pointer,ensure_ascii=False,sort_keys=True)+"\n").encode()
        self.assertEqual(blob,git_blob(body))

    def test_remote_main_moves_while_build_replay_is_running(self):
        self.github.moves_on_second_ref=True
        with self.assertRaisesRegex(ValueError,"GITHUB_MAIN_MOVED_DURING_READBACK"):
            self.run_remote()

    def test_github_pointer_sha_forgery_is_blocked(self):
        self.github.bad_blob=True
        with self.assertRaisesRegex(ValueError,"GITHUB_POINTER_BLOB_MISMATCH"):
            self.run_remote()

    def test_github_pointer_path_substitution_blocked(self):
        self.github.bad_path=True
        with self.assertRaisesRegex(ValueError,"GITHUB_CONTENTS_NOT_EXACT_MAIN_FILE"):
            self.run_remote()

    def test_github_pointer_truncated_size_is_blocked(self):
        self.github.bad_size=True
        with self.assertRaisesRegex(ValueError,"GITHUB_POINTER_SIZE_MISMATCH"):
            self.run_remote()

    def test_github_api_not_main_ref_blocked(self):
        with self.assertRaisesRegex(ValueError,"GITHUB_MAIN_HEAD_INVALID"):
            m.github_pointer(WORKDIR,lambda url:{"object":{"sha":"a"*40,
                                                           "type":"tag"}})

    def test_wrong_library_record_id_rejected(self):
        with self.assertRaisesRegex(ValueError,"REMOTE_GITHUB_LIBRARY_ID_OR_PATH_MISMATCH"):
            self.run_remote(library_record_id="libfile_wrong")

    def test_wrong_materialized_library_file_digest_rejected(self):
        self.library.write_bytes(self.library.read_bytes()+b"edited")
        with self.assertRaisesRegex(ValueError,"LIBRARY_BYTE_LENGTH_MISMATCH"):
            self.run_remote()

    def test_same_archive_path_masquerading_as_second_provider_copy_refused(self):
        with self.assertRaisesRegex(ValueError,"LIBRARY_COPY_NOT_INDEPENDENT_FILE"):
            self.run_remote(library_copy=self.out)

    def test_missing_library_copy_fails(self):
        self.library.unlink()
        with self.assertRaisesRegex(ValueError,"LIBRARY_OR_SOURCE_COPY_NOT_REGULAR"):
            self.run_remote()

    def test_github_latest_not_matching_actual_archive_fails(self):
        self.github.pointer["artifact"]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"LATEST_ACTUAL_ZIP_DOES_NOT_MATCH"):
            self.run_remote()

    def test_github_latest_wrong_workspace_owner_fails(self):
        self.github.pointer["workstream"]="other-workstream"
        with self.assertRaisesRegex(ValueError,"LATEST_REFERENCES_DIFFERENT_WORKSTREAM"):
            self.run_remote()

    def test_no_governed_native_receipt_never_adopt(self):
        self.receipt.unlink()
        with self.assertRaisesRegex(ValueError,"NO_NEW_GOVERNED_RECEIPT"):
            self.run_remote()

    def test_grammar_source_not_forced_to_vocabulary_schema(self):
        with self.assertRaisesRegex(ValueError,"WORKSPACE_WRONG_FAMILY_OR_NONLEXICAL_ADAPTER"):
            self.run_remote(family_id="family:grammatik-aktiv-a1-b1")

    def test_malicious_workspace_path_blocked_before_network(self):
        with self.assertRaisesRegex(ValueError,"UNSAFE_GITHUB_WORKSPACE"):
            m.github_pointer("../steal",self.github)

    def test_file_id_is_not_equal_to_library_record_id(self):
        with self.assertRaisesRegex(ValueError,"LIBRARY_REF_OR_PATH_INVALID"):
            self.run_remote(library_file_id=LIBID)

    def test_only_read_operations_never_modify_source_or_user_zip(self):
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.src.iterdir()}
        origin=hashlib.sha256(self.out.read_bytes()).hexdigest()
        self.run_remote()
        self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in self.src.iterdir()})
        self.assertEqual(origin,hashlib.sha256(self.out.read_bytes()).hexdigest())

    def test_stage4_and_stage6_not_claimed_even_with_real_byte_parity(self):
        x=self.run_remote()
        self.assertEqual(x["linguistic_stage4"],"NOT_CERTIFIED_BY_THIS_TOOL")
        self.assertEqual(x["stage6_browser"],"NOT_RUN")
        self.assertEqual(x["stage7_final"],"NOT_RUN")
        self.assertEqual(x["more_recent_explicit_user_artifact"],
                         "MUST_BE_CHECKED_SEPARATELY_BEFORE_CURRENT_CLAIM")

if __name__=="__main__":
    unittest.main()
