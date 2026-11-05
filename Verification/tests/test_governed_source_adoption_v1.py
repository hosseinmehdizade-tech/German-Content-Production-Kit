"""P1 adoption proof: end-to-end native builder fixtures + hostile receipts/pointers.

GitHub CI here produces SYNTHETIC source packages and simulated local LATEST.
No private Library archive and no live GitHub-main remote readback is performed.
"""
from __future__ import annotations
import copy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"Verification/verify_governed_source_adoption_v1.py"
spec=importlib.util.spec_from_file_location("gfp_opt_p1_adoption",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAMILY="family:250-verben-mit-praepositionen"
WORKSPACE="workspace:250-verben-mit-praepositionen-lexical-enrichment-v1"
WORKDIR="Workspaces/250-verben-mit-praepositionen-lexical-enrichment-v1"

def typed_tsv():
    s=io.StringIO(newline="")
    fields=["id","front","back","card_type","category","details","custom_fields","source"]
    w=csv.DictWriter(s,fieldnames=fields,delimiter="\t",lineterminator="\n")
    w.writeheader()
    for n in range(2):
        w.writerow({
            "id":"source-00"+str(n),"front":"kommen","back":"آمدن",
            "card_type":"de-vocabulary","category":"Verb",
            "details":json.dumps([{"title":"Deutsch","items":["kommen"]}]),
            "custom_fields":json.dumps({"presentation_contract":"gfp-vocabulary-neutral@1"}),
            "source":"Synthetic source -- not authorized real family content"
        })
    return s.getvalue().encode("utf-8")

def blob_sha(content:bytes):
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()

class ExactSourceAdoptionTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.home=Path(t.name)
        self.source=self.home/"source"
        self.source.mkdir()
        self.files={
            "SOURCE-IMPORT.tsv":typed_tsv(),
            "SOURCE-CANONICAL.json":b'{"cards":[]}\n',
            "SOURCE-SOURCE-OUTPUT-MAP.tsv":b"id\tsource\n",
            "SOURCE-VERIFICATION.json":b'{"qa":"synthetic-only"}\n'
        }
        for path,contents in self.files.items():
            (self.source/path).write_bytes(contents)
        self.archive=self.home/"STAGE5-NATIVE-DELIVERY.zip"
        self.native=self.home/"STAGE5-NATIVE-RECEIPT.json"
        self.checkout=self.home/"checkout"
        self.latest=self.checkout/WORKDIR/"LATEST.json"
        self.latest.parent.mkdir(parents=True)
        self.report=self.home/"P1-ADOPTION-CANDIDATE.json"

    def build(self):
        native=m.governed.run(self.source,self.archive,self.native)
        pointer={
            "schema":"gcpk-workstream-latest@1.0.0",
            "workstream":WORKDIR.split("/")[-1],
            "status":"PASS_STAGE5_CLEAN_CONTENT_DELIVERY__NOT_STAGE6",
            "artifact":{
                "filename":self.archive.name,
                "sha256":native["output_zip_sha256"],
                "bytes":self.archive.stat().st_size
            }
        }
        self.write_latest(pointer)
        return native

    def write_latest(self,document):
        self.latest.write_text(json.dumps(document,sort_keys=True)+"\n",encoding="utf-8")
        return blob_sha(self.latest.read_bytes())

    def verify(self,**overrides):
        fields={
            "family_id":FAMILY,"workspace_id":WORKSPACE,
            "latest_blob":blob_sha(self.latest.read_bytes()),
            "workspace_root":self.checkout,
            "source":self.source,"archive":self.archive,
            "native_receipt":self.native
        }
        fields.update(overrides)
        return m.verify(**fields)

    def test_strict_real_catalog_and_lexical_owner(self):
        self.assertEqual(m.resolve_owner(FAMILY,WORKSPACE),WORKDIR)
        self.assertEqual(len(m.catalog_authority()[0]["families"]),21)

    def test_official_builder_receipt_and_pinned_latest_replayed_end_to_end(self):
        self.build()
        out=self.verify()
        self.assertEqual(out["status"],
            "PASS_SCOPED_LOCAL_CURRENT_POINTER_AND_GOVERNED_ZIP_PARITY__REMOTE_ADOPTION_OPEN")
        self.assertEqual(out["verified_cards"],2)
        self.assertEqual(out["source_input_sha256"]["direct-import-tsv"],
                         hashlib.sha256(typed_tsv()).hexdigest())
        self.assertEqual(out["formal_real_producer_adoption"],
            "NOT_GRANTED__INDEPENDENT_REMOTE_MAIN_AND_LIBRARY_READBACK_REQUIRED")
        self.assertFalse(out["automatic_other_source_propagation"])

    def test_real_input_bytes_unchanged_after_independent_replay(self):
        self.build()
        before={x.name:hashlib.sha256(x.read_bytes()).hexdigest()
                for x in self.source.iterdir()}
        self.verify()
        self.assertEqual(before,{x.name:hashlib.sha256(x.read_bytes()).hexdigest()
                                 for x in self.source.iterdir()})

    def test_no_receipt_means_legacy_archive_cannot_masquerade_as_adopted(self):
        self.build()
        self.native.unlink()
        with self.assertRaisesRegex(ValueError,
                   "NO_ACTUAL_GOVERNED_RECEIPT__LEGACY_ARCHIVE_NOT_ADOPTED"):
            self.verify()

    def test_wrong_family_to_workspace_mapping_refused(self):
        self.build()
        with self.assertRaisesRegex(ValueError,"WORKSPACE_WRONG_FAMILY"):
            self.verify(family_id="family:menschen-a1-verben")

    def test_grammar_family_cannot_be_forced_into_vocabulary_adapter(self):
        with self.assertRaisesRegex(ValueError,"WORKSPACE_WRONG_FAMILY_OR_NONLEXICAL_ADAPTER"):
            m.resolve_owner("family:grammatik-aktiv-a1-b1",
                            "workspace:250-verben-mit-praepositionen-lexical-enrichment-v1")

    def test_unknown_source_owner_fails(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_SOURCE_OWNER"):
            m.resolve_owner("family:invented",WORKSPACE)

    def test_changed_actual_source_tsv_refuses_old_receipt(self):
        self.build()
        (self.source/"SOURCE-IMPORT.tsv").write_bytes(typed_tsv()+b"\n")
        with self.assertRaisesRegex(ValueError,"ACTUAL_SOURCE_ROLES_CHANGED_OR_FORGED"):
            self.verify()

    def test_changed_native_output_fails_closed(self):
        self.build()
        self.archive.write_bytes(self.archive.read_bytes()+b"\x00")
        with self.assertRaisesRegex(ValueError,
                    "ACTUAL_GOVERNED_ZIP_NOT_IN_RECEIPT"):
            self.verify()

    def test_wrong_latest_git_blob_fails_closed(self):
        self.build()
        with self.assertRaisesRegex(ValueError,"LATEST_GIT_BLOB_CHANGED"):
            self.verify(latest_blob="a"*40)

    def test_latest_points_to_another_zip_fails(self):
        self.build()
        data=json.loads(self.latest.read_text())
        data["artifact"]["sha256"]="0"*64
        self.write_latest(data)
        with self.assertRaisesRegex(ValueError,"LATEST_ACTUAL_ZIP_DOES_NOT_MATCH"):
            self.verify()

    def test_latest_wrong_byte_size_fails(self):
        self.build()
        data=json.loads(self.latest.read_text())
        data["artifact"]["bytes"]+=1
        self.write_latest(data)
        with self.assertRaisesRegex(ValueError,"LATEST_ACTUAL_ZIP_SIZE_MISMATCH"):
            self.verify()

    def test_wrong_workspace_pointer_fails(self):
        self.build()
        data=json.loads(self.latest.read_text())
        data["workstream"]="another-workspace"
        self.write_latest(data)
        with self.assertRaisesRegex(ValueError,"LATEST_REFERENCES_DIFFERENT_WORKSTREAM"):
            self.verify()

    def test_stage4_only_latest_cannot_be_stage5_adopted(self):
        self.build()
        data=json.loads(self.latest.read_text())
        data["status"]="STAGE4_OPEN_WIP"
        self.write_latest(data)
        with self.assertRaisesRegex(ValueError,"LATEST_NOT_STAGE5_ELIGIBLE"):
            self.verify()

    def test_forged_formal_stage5_claim_is_rejected(self):
        self.build()
        doc=json.loads(self.native.read_text(encoding="utf-8"))
        doc["stage5_content_acceptance"]="PASS_FINAL"
        self.native.write_text(json.dumps(doc),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"FORGED_NATIVE_RECEIPT_PASS_OR_MUTATION"):
            self.verify()

    def test_forged_policy_sha_is_rejected(self):
        self.build()
        doc=json.loads(self.native.read_text(encoding="utf-8"))
        doc["active_policy"]["validator_git_blob"]="f"*40
        self.native.write_text(json.dumps(doc),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"CURRENT_PINNED_POLICY_NOT_IN_RECEIPT"):
            self.verify()

    def test_forged_output_role_hash_is_rejected(self):
        self.build()
        doc=json.loads(self.native.read_text(encoding="utf-8"))
        doc["source_role_sha256"]["direct-import-tsv"]="b"*64
        self.native.write_text(json.dumps(doc),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"ACTUAL_SOURCE_ROLES_CHANGED_OR_FORGED"):
            self.verify()

    def test_unregistered_checkout_latest_schema_fails(self):
        self.build()
        data=json.loads(self.latest.read_text())
        data["schema"]="custom-latest"
        self.write_latest(data)
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_WORKSTREAM_LATEST_SCHEMA"):
            self.verify()

    def test_cli_report_is_exclusive_and_non_authoritative(self):
        self.build()
        args=[
          sys.executable,str(SCRIPT),
          "--family-id",FAMILY,"--workspace-id",WORKSPACE,
          "--latest-git-blob",blob_sha(self.latest.read_bytes()),
          "--workspace-root",str(self.checkout),
          "--source-dir",str(self.source),
          "--archive",str(self.archive),
          "--native-receipt",str(self.native),
          "--new-report",str(self.report)
        ]
        a=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,encoding="utf-8")
        self.assertEqual(a.returncode,0,a.stderr)
        report=json.loads(self.report.read_text(encoding="utf-8"))
        self.assertFalse(report["github_ci_private_source_rehash"])
        self.assertIn("REMOTE_ADOPTION_OPEN",report["status"])
        old=self.report.read_bytes()
        b=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,encoding="utf-8")
        self.assertEqual(b.returncode,2)
        self.assertEqual(old,self.report.read_bytes())

    def test_missing_pointer_blocks_adoption(self):
        self.build()
        self.latest.unlink()
        with self.assertRaisesRegex(ValueError,"SOURCE_LATEST_MISSING_OR_SYMLINK"):
            self.verify(latest_blob="a"*40)

if __name__=="__main__":
    unittest.main()
