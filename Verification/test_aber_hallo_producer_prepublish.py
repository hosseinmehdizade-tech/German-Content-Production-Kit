"""OP-02 synthetic prepublication role gate; no learner/ZIP writes."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit_aber_hallo_producer_prepublish import assess,parse

BASE="Workspaces/aber-hallo-listen-tabellen/"
A="a"*64
B="b"*64
C="c"*64
D="d"*64


def example():
    zipname="Aber-Hallo-WIP60-20-EXACT-LEXICON.zip"
    portable={"filename":zipname,"sha256":A,"size_bytes":10001,
              "library_file_id":"libfile_synthetic","library_path":"/synthetic/"+zipname,
              "canonical_sha256":B,"import_sha256":C,"stage4":"OPEN"}
    pkg={"name":zipname,"sha256":A,"bytes":10001,
         "member_count":415,"library_file_id":"libfile_synthetic",
         "library_path":"/synthetic/"+zipname,
         "stage4":"OPEN","stage5_6_7":"NOT_RUN","parent_sha256":D}
    receipt_path=BASE+"56-wip60-lexicon-evidence/WIP60-CHECKPOINT.json"
    latest={
        "schema":"gcpk-workstream-latest@1.0.0",
        "workstream":"aber-hallo-listen-tabellen",
        "latest_milestone":"WIP60_SYNTHETIC",
        "latest_receipt_path":receipt_path,
        "authority":{"current_portable":portable},
        "complete_working_content_package":pkg,
        "previous_wip60_source_current":{"portable":{"sha256":D}},
        "progress":{"pending_independent_expert_stage4":True,
                    "independent_expert_unreviewed_units":788,
                    "rektion_independent_external_attested_cumulative":751,
                    "rektion_external_holds_remaining":230},
    }
    receipt={"schema":"gcpk-aber-hallo-wip60-checkpoint@1",
             "status":"PASS_SCOPED_STAGE4_OPEN",
             "parent_sha256":D,"zip":zipname,"zip_sha256":A,
             "library_file_id":"libfile_synthetic",
             "canonical_sha256":B,"import_sha256":C,
             "zip_members":415,"cumulative_attested":751,
             "remaining_holds":230,"learning_units":788,
             "lexical_cards":787,"global_stage4":"OPEN","stage5_to_7":"NOT_RUN"}
    source={"schema":"gcpk-source-manifest@1.1.0",
            "dataset":"aber-hallo-listen-tabellen",
            "source_set":[{"source_id":"s1","source_type":"pdf","sha256":B},
                          {"source_id":"s2","source_type":"pdf","sha256":C}]}
    return latest,receipt,source,receipt_path


class PrepublishGate(unittest.TestCase):
    def evaluate(self,mutation=None,*,candidate_pointer=False):
        a,b,c,path=copy.deepcopy(example())
        if mutation:mutation(a,b,c)
        return assess(a,b,c,a["latest_receipt_path"] if candidate_pointer else path)

    def blocked(self,mutation,code):
        r=self.evaluate(mutation)
        self.assertEqual(r["status"],"BLOCKED_PREPUBLISH",r)
        self.assertIn(code,r["blockers"],r)
        self.never_release(r)

    def never_release(self,result):
        for k in ("authenticated_current_source","authenticated_issuer",
                  "original_zip_bytes_verified","source_pdf_binary_verified",
                  "stage4_semantic_pass","stage5_allowed","stage6_pass",
                  "stage7_release_final","writer_granted","performed_writes"):
            self.assertIs(result[k],False,k)

    def test_exact_known_wip60_role_shape_positive_metadata_only(self):
        r=self.evaluate()
        self.assertEqual(r["status"],
            "PASS_SCOPED_PREPUBLISH_METADATA_ONLY_NOT_AUTHORIZED",r)
        self.never_release(r)

    def test_wip61_stale_complete_package_and_unknown_schema_cannot_pass(self):
        def mutate(a,b,c):
            p=a["authority"]["current_portable"]
            p.update(filename="Aber-Hallo-WIP61-SYNTHETIC.zip",sha256="e"*64)
            a["latest_milestone"]="WIP61_SYNTHETIC"
            a["latest_receipt_path"]=BASE+"57-wip61/WIP61-CHECKPOINT.json"
            a["previous_wip61_source_current"]={"portable":{"sha256":A}}
            b.update(schema="gcpk-wip61-checkpoint@1",
                     zip=p["filename"],zip_sha256=p["sha256"],
                     parent_sha256=A)
        r=self.evaluate(mutate,candidate_pointer=True)
        for code in ("UNREGISTERED_RECEIPT_SCHEMA",
                     "CURRENT_PACKAGE_ROLE_DRIFT:filename",
                     "CURRENT_PACKAGE_ROLE_DRIFT:sha256",
                     "PACKAGE_PREDECESSOR_PARENT_DRIFT"):
            self.assertIn(code,r["blockers"],r)
        self.never_release(r)

    def test_even_fixed_wip61_role_needs_explicit_schema_registration(self):
        def mutate(a,b,c):
            p=a["authority"]["current_portable"]
            p.update(filename="Aber-Hallo-WIP61-SYNTHETIC.zip",sha256="e"*64)
            a["latest_milestone"]="WIP61_SYNTHETIC"
            a["latest_receipt_path"]=BASE+"57-wip61/WIP61-CHECKPOINT.json"
            a["previous_wip61_source_current"]={"portable":{"sha256":A}}
            a["complete_working_content_package"].update(
                name=p["filename"],sha256=p["sha256"],parent_sha256=A)
            b.update(schema="gcpk-wip61-checkpoint@1",zip=p["filename"],
                     zip_sha256=p["sha256"],parent_sha256=A)
        r=self.evaluate(mutate,candidate_pointer=True)
        self.assertEqual(r["blockers"],["UNREGISTERED_RECEIPT_SCHEMA"],r)
        self.never_release(r)

    def test_zip_role_hash_drift(self):
        self.blocked(lambda a,b,c:a["complete_working_content_package"].update(sha256="e"*64),
                     "CURRENT_PACKAGE_ROLE_DRIFT:sha256")

    def test_zip_role_filename_drift(self):
        self.blocked(lambda a,b,c:a["complete_working_content_package"].update(name="WIP59.zip"),
                     "CURRENT_PACKAGE_ROLE_DRIFT:filename")

    def test_parent_readback_drift(self):
        self.blocked(lambda a,b,c:a["complete_working_content_package"].update(parent_sha256="e"*64),
                     "PACKAGE_PREDECESSOR_PARENT_DRIFT")

    def test_parent_receipt_drift(self):
        self.blocked(lambda a,b,c:b.update(parent_sha256="e"*64),
                     "RECEIPT_PREDECESSOR_PARENT_DRIFT")

    def test_portable_canonical_hash_drift(self):
        self.blocked(lambda a,b,c:a["authority"]["current_portable"].update(canonical_sha256="bad"),
                     "CURRENT_HASH_INVALID:canonical_sha256")

    def test_receipt_canonical_hash_drift(self):
        self.blocked(lambda a,b,c:b.update(canonical_sha256="e"*64),
                     "RECEIPT_CURRENT_ROLE_DRIFT:canonical_sha256")

    def test_malformed_source_hash_drift(self):
        self.blocked(lambda a,b,c:c["source_set"][0].update(sha256="bad"),
                     "SOURCE_SET_MALFORMED")

    def test_unregistered_schema_future_blocked(self):
        self.blocked(lambda a,b,c:b.update(schema="future-unknown@1"),
                     "UNREGISTERED_RECEIPT_SCHEMA")

    def test_schema_replay_old_wip60_as_wip61_blocks(self):
        self.blocked(lambda a,b,c:a.update(latest_milestone="WIP61_NEXT"),
                     "RECEIPT_SCHEMA_VERSION_DRIFT")

    def test_receipt_path_switch_blocked(self):
        self.blocked(lambda a,b,c:a.update(latest_receipt_path=BASE+"old.json"),
                     "CURRENT_RECEIPT_PATH_DRIFT")

    def test_stage4_claim_without_review_blocked(self):
        self.blocked(lambda a,b,c:b.update(global_stage4="FINAL"),
                     "FALSE_STAGE4_CLAIM")

    def test_stage5_to7_claim_blocked(self):
        self.blocked(lambda a,b,c:a["complete_working_content_package"].update(stage5_6_7="PASS"),
                     "STAGE4_7_BOUNDARY_INVALID")

    def test_no_independent_review_wrong_claim_blocked(self):
        self.blocked(lambda a,b,c:a["progress"].update(independent_expert_unreviewed_units=0),
                     "STAGE4_REVIEW_NOT_OPEN")

    def test_count_attested_plus_hold_981(self):
        self.blocked(lambda a,b,c:a["progress"].update(rektion_external_holds_remaining=231),
                     "GOVERNED_981_ACCOUNTING_DRIFT")

    def test_receipt_count_drift(self):
        self.blocked(lambda a,b,c:b.update(cumulative_attested=750),
                     "RECEIPT_REKTION_COUNT_DRIFT:cumulative_attested")

    def test_exact_learning_788(self):
        self.blocked(lambda a,b,c:b.update(learning_units=787),
                     "LEARNING_UNIT_COUNT_INVALID")

    def test_exact_lexical_787(self):
        self.blocked(lambda a,b,c:b.update(lexical_cards=788),
                     "LEXICAL_CARD_COUNT_INVALID")

    def test_boolean_counts_not_int(self):
        self.blocked(lambda a,b,c:a["progress"].update(rektion_external_holds_remaining=True),
                     "GOVERNED_981_ACCOUNTING_DRIFT")

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_JSON_KEY"):
            parse(b'{"schema":1,"schema":2}')

    def test_nan_json_rejected(self):
        with self.assertRaisesRegex(ValueError,"NONFINITE_JSON"):
            parse(b'{"x":NaN}')

    def test_cli_strict_blocks_without_writing_files(self):
        a,b,c,path=example()
        b["schema"]="unknown-checkpoint@1"
        with tempfile.TemporaryDirectory() as td:
            tmp=Path(td)
            for key,data in (("latest",a),("receipt",b),("sources",c)):
                (tmp/(key+".json")).write_text(json.dumps(data))
            command=[sys.executable,"-B",str(HERE/"audit_aber_hallo_producer_prepublish.py"),
                     "--latest",str(tmp/"latest.json"),"--receipt",str(tmp/"receipt.json"),
                     "--sources",str(tmp/"sources.json"),"--receipt-relative-path",path,"--strict"]
            result=subprocess.run(command,capture_output=True,text=True,cwd=tmp)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertIn("UNREGISTERED_RECEIPT_SCHEMA",result.stdout)
            self.assertEqual({x.name for x in tmp.iterdir()},
                             {"latest.json","receipt.json","sources.json"})


if __name__=="__main__":
    unittest.main()
