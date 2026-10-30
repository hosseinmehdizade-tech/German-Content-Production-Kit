"""OP02 scoped active ZIP guard: no learner/source modifications or release."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
from content_package_guard import guarded_zip,PackageGuardError,check_aber_hallo_active_pointer

CANON="02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json"
IMP="01-Final-Import/IMPORT.WORKING.tsv"
PTR="07-Checkpoint-State/CURRENT-WORKSTREAM-POINTER.json"
WORK="07-Checkpoint-State/WORKING-STATE.json"
MAN="MANIFEST.json"

def hh(raw):
    return hashlib.sha256(raw).hexdigest()

def parts(n=70):
    canon=b'{"learning_units":[]}'
    imp=b'id\tcard_type\n'
    digestc,digesti=hh(canon),hh(imp)
    return {
       CANON:canon,IMP:imp,
       PTR:json.dumps({
         "schema":"aber-hallo-portable-working-authority@1.0.0",
         "workstream":"aber-hallo-listen-tabellen",
         "current":f"WIP{n}_SCOPED_VALID",
         "canonical_sha256":digestc,"import_sha256":digesti,
         "working_canonical_sha256":digestc,"working_import_sha256":digesti,
         "previous_wip14_zip_sha256":"a"*64,
       }).encode(),
       WORK:json.dumps({
         "schema":"aber-hallo-working-content-lean-repair@1.0.0",
         "status":f"WORKING_WIP{n}_SCOPED_STAGE4_OPEN",
         "working_canonical_sha256":digestc,"working_import_sha256":digesti,
         "canonical_sha256":digestc,"import_sha256":digesti,
         "parent_wip14_zip_sha256":"b"*64,
       }).encode(),
       MAN:json.dumps({
         "workstream":"aber-hallo-listen-tabellen",
         "summary":{"status":f"CURRENT_WIP{n}_SCOPED_STAGE4_OPEN",
                    "canonical_sha256":digestc,"import_sha256":digesti},
       }).encode(),
    }

def produce(path,values,*,purpose="final_delivery"):
    with guarded_zip(path,purpose=purpose) as z:
        for name,data in values.items():
            z.writestr(name,data)

def mutate_json(values,name,field,value):
    obj=json.loads(values[name])
    obj[field]=value
    values[name]=json.dumps(obj).encode()

class GuardedCurrent(unittest.TestCase):
    def blocked(self,change,fragment):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"candidate.zip"
            v=parts()
            change(v)
            with self.assertRaisesRegex(PackageGuardError,fragment):
                produce(path,v)
            self.assertFalse(path.exists())
            self.assertFalse((Path(d)/".content-package-index.json").exists())
            self.assertFalse(list(Path(d).glob(".content-zip-*.tmp")))

    def test_producer_v70_valid_current_can_publish_only_scoped_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"scoped.zip"
            produce(p,parts())
            with zipfile.ZipFile(p,"r") as z:
                self.assertTrue(check_aber_hallo_active_pointer(z))
            self.assertTrue(p.is_file())

    def test_producer_v71_without_per_wip_schema_changes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"scoped.zip"
            produce(p,parts(71))
            self.assertTrue(p.is_file())

    def test_stale_parent_pointer_rejected_before_publish(self):
        def change(v):
            mutate_json(v,PTR,"current","WIP69_STALE")
        self.blocked(change,"CURRENT pointer version stale")

    def test_stale_parent_canonical_digest_rejected(self):
        def change(v):
            mutate_json(v,PTR,"canonical_sha256","f"*64)
        self.blocked(change,"CURRENT pointer canonical_sha256 stale")

    def test_stale_parent_working_import_digest_rejected(self):
        def change(v):
            mutate_json(v,PTR,"working_import_sha256","f"*64)
        self.blocked(change,"CURRENT pointer working_import_sha256 stale")

    def test_stale_working_state_status_rejected(self):
        def change(v):
            mutate_json(v,WORK,"status","WORKING_WIP65_OLD")
        self.blocked(change,"WORKING-STATE active status/version stale")

    def test_stale_working_state_hash_rejected(self):
        def change(v):
            mutate_json(v,WORK,"working_canonical_sha256","f"*64)
        self.blocked(change,"WORKING-STATE working_canonical_sha256 stale")

    def test_manifest_has_wrong_canonical_sha_rejected(self):
        def change(v):
            m=json.loads(v[MAN]);m["summary"]["canonical_sha256"]="f"*64
            v[MAN]=json.dumps(m).encode()
        self.blocked(change,"MANIFEST active canonical_sha256 is stale")

    def test_manifest_wrong_workstream_rejected(self):
        def change(v):
            mutate_json(v,MAN,"workstream","lesen-praesentation")
        self.blocked(change,"foreign or malformed MANIFEST workstream")

    def test_missing_pointer_rejected(self):
        self.blocked(lambda v:v.pop(PTR),"missing active CURRENT role")

    def test_missing_working_state_rejected(self):
        self.blocked(lambda v:v.pop(WORK),"missing active CURRENT role")

    def test_missing_manifest_rejected(self):
        self.blocked(lambda v:v.pop(MAN),"lacks MANIFEST")

    def test_duplicate_json_key_rejected(self):
        def change(v):
            v[PTR]=v[PTR][:-1]+b', "current":"WIP70_DUPLICATE"}'
        self.blocked(change,"duplicate active JSON key")

    def test_foreign_generic_zip_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"generic.zip"
            produce(out,{"cards.tsv":b"row","manifest.json":b'{"version":1}'})
            self.assertTrue(out.is_file())

    def test_cli_accepts_scoped_good_without_granting_release(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"good.zip"
            produce(out,parts())
            c=subprocess.run([sys.executable,str(ROOT/"Tools/prepublish_aber_hallo_guard.py"),
                              str(out),"--expected-milestone","WIP70_REQUESTED",
                              "--expected-sha256",hh(out.read_bytes())],
                             capture_output=True,text=True)
            self.assertEqual(c.returncode,0,c.stdout+c.stderr)
            j=json.loads(c.stdout)
            self.assertEqual(j["status"],"PASS_SCOPED_METADATA_COHERENCE_ONLY")
            self.assertFalse(j["publisher_authenticated"])
            self.assertFalse(j["stage4_semantic_pass"])
            self.assertFalse(j["performed_writes"])

    def test_cli_wrong_external_version_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"good.zip"
            produce(out,parts())
            c=subprocess.run([sys.executable,str(ROOT/"Tools/prepublish_aber_hallo_guard.py"),
                              str(out),"--expected-milestone","WIP69_WRONG"],
                             capture_output=True,text=True)
            self.assertEqual(c.returncode,2,c.stdout+c.stderr)
            self.assertIn("MANIFEST_VS_EXPECTED_MILESTONE_DRIFT",c.stdout)

    def test_cli_wrong_external_zip_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"good.zip"
            produce(out,parts())
            c=subprocess.run([sys.executable,str(ROOT/"Tools/prepublish_aber_hallo_guard.py"),
                              str(out),"--expected-milestone","WIP70_GOOD",
                              "--expected-sha256","f"*64],
                             capture_output=True,text=True)
            self.assertEqual(c.returncode,2,c.stdout+c.stderr)
            self.assertIn("EXTERNAL_ZIP_SHA_DRIFT",c.stdout)

    def test_cli_missing_binary_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"absent.zip"
            c=subprocess.run([sys.executable,str(ROOT/"Tools/prepublish_aber_hallo_guard.py"),
                              str(path),"--expected-milestone","WIP70_GOOD"],
                             capture_output=True,text=True)
            self.assertEqual(c.returncode,2,c.stdout+c.stderr)
            self.assertFalse(path.exists())

if __name__=="__main__":
    unittest.main()
