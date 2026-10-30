"""Synthetic parent/current original-ZIP byte lineage and publisher guards."""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile,ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Verification"))
from audit_op02_parent_pointer_lineage import audit, digest, no_duplicate_json, POINTER, CANON, IMPORT

def artifact(version, *, parent_pointer=None, mutate_pointer=None, bad_manifest=False):
    canonical=json.dumps({"units":[{"id":version}]}).encode()
    imp=f"id\tcard_type\nahl-lu-{version:04}\tvocab\n".encode()
    pointer={
        "workstream":"aber-hallo-listen-tabellen",
        "current":f"WIP{version}_SYNTHETIC",
        "canonical_sha256":digest(canonical),
        "import_sha256":digest(imp),
        "working_canonical_sha256":digest(canonical),
        "working_import_sha256":digest(imp),
    }
    if parent_pointer is not None:
        pointer=copy.deepcopy(parent_pointer)
    if mutate_pointer:mutate_pointer(pointer)
    manifest={"summary":{
        "status":f"CURRENT_WIP{version}_SYNTHETIC",
        "canonical_sha256":digest(canonical),
        "import_sha256":digest(imp) if not bad_manifest else "f"*64,
    }}
    streams={
        POINTER:json.dumps(pointer,sort_keys=True).encode(),
        CANON:canonical,IMPORT:imp,
        "MANIFEST.json":json.dumps(manifest,sort_keys=True).encode()
    }
    with io.BytesIO() as buff:
        with ZipFile(buff,"w",compression=ZIP_DEFLATED) as z:
            for name,data in streams.items():z.writestr(name,data)
        return buff.getvalue(),pointer

def evaluate(child_mutate=None,parent_mutate=None,prior_pointer=False,
             current_version=68,parent_version=67,
             current_data=None,parent_data=None,snapshot_change=None):
    parent,ptr=artifact(parent_version,mutate_pointer=parent_mutate)
    child,_=artifact(current_version,parent_pointer=ptr if prior_pointer else None,
                     mutate_pointer=child_mutate)
    if current_data is not None:child=current_data
    if parent_data is not None:parent=parent_data
    spec={"workstream":"aber-hallo-listen-tabellen",
          "current_sha256":digest(child),"parent_sha256":digest(parent),
          "current_milestone":f"WIP{current_version}_SYNTHETIC",
          "parent_version":parent_version}
    if snapshot_change:snapshot_change(spec)
    with tempfile.TemporaryDirectory() as d:
        a=Path(d)/"new.zip";b=Path(d)/"parent.zip"
        a.write_bytes(child);b.write_bytes(parent)
        return audit(a,b,spec)

class PointerLineage(unittest.TestCase):
    def denied(self,result):
        for key in ("issuer_authenticated","stage4_semantic_pass",
                    "stage5_7_authorized","release_authorized",
                    "writer_granted","performed_writes"):
            self.assertIs(result[key],False)

    def blocked(self,result,reason):
        self.assertEqual(result["status"],"BLOCKED",result)
        self.assertIn(reason,result["errors"],result)
        self.denied(result)

    def test_honest_parent_current_scoped_only(self):
        r=evaluate()
        self.assertEqual(r["status"],
            "PASS_SCOPED_ORIGINAL_POINTER_LINEAGE_ONLY_NOT_RELEASE",r)
        self.assertFalse(r["same_pointer_bytes"])
        self.denied(r)

    def test_future_versions_reuse_same_contract(self):
        r=evaluate(current_version=104,parent_version=103)
        self.assertEqual(r["status"],
            "PASS_SCOPED_ORIGINAL_POINTER_LINEAGE_ONLY_NOT_RELEASE",r)
        self.denied(r)

    def test_wip67_exact_byte_copy_of_wip66_pointer_is_rejected(self):
        r=evaluate(current_version=67,parent_version=66,prior_pointer=True)
        self.blocked(r,"EXACT_PARENT_POINTER_REUSED")
        self.assertIn("CURRENT_POINTER_VERSION_STALE",r["errors"])
        self.assertIn("current",r["required_producer_repairs"])
        for key in ("canonical_sha256","import_sha256",
                    "working_canonical_sha256","working_import_sha256"):
            self.assertIn(key,r["required_producer_repairs"])
        self.assertEqual(r["current_pointer_sha256"],r["parent_pointer_sha256"])

    def test_selfconsistent_zip_hash_does_not_hide_parent_copy(self):
        r=evaluate(prior_pointer=True)
        self.blocked(r,"EXACT_PARENT_POINTER_REUSED")

    def test_current_version_changed_but_old_digest_still_blocks(self):
        def partial(p):
            c,_=artifact(67)
            with ZipFile(io.BytesIO(c)) as z:
                old=json.loads(z.read(POINTER))
            p["canonical_sha256"]=old["canonical_sha256"]
            p["working_canonical_sha256"]=old["working_canonical_sha256"]
        r=evaluate(child_mutate=partial)
        self.blocked(r,"CURRENT_POINTER_DIGEST_STALE:canonical_sha256")

    def test_working_hash_stale_even_if_main_hashs_good(self):
        r=evaluate(child_mutate=lambda p:p.update(working_import_sha256="f"*64))
        self.blocked(r,"CURRENT_POINTER_DIGEST_STALE:working_import_sha256")

    def test_parent_hash_mismatch_detected(self):
        r=evaluate(snapshot_change=lambda s:s.update(parent_sha256="f"*64))
        self.blocked(r,"PARENT_ZIP_SHA256_DRIFT")

    def test_current_hash_mismatch_detected(self):
        r=evaluate(snapshot_change=lambda s:s.update(current_sha256="f"*64))
        self.blocked(r,"CURRENT_ZIP_SHA256_DRIFT")

    def test_parent_version_gap_blocks(self):
        r=evaluate(snapshot_change=lambda s:s.update(parent_version=65))
        self.blocked(r,"PARENT_CURRENT_VERSION_GAP")

    def test_parent_version_forged_blocks(self):
        r=evaluate(parent_mutate=lambda p:p.update(current="WIP65_FAKE"))
        self.blocked(r,"PARENT_POINTER_VERSION_STALE")

    def test_manifest_mismatch_blocks(self):
        p,_=artifact(67,bad_manifest=True)
        r=evaluate(parent_data=p)
        self.blocked(r,"PARENT_MANIFEST_VERSION_OR_DIGEST_DRIFT")

    def test_workstream_forgery_blocks(self):
        r=evaluate(child_mutate=lambda p:p.update(workstream="other"))
        self.blocked(r,"CURRENT_POINTER_WORKSTREAM_INVALID")

    def test_parent_hash_and_pointer_same_version_forgery_blocks(self):
        r=evaluate(child_mutate=lambda p:p.update(current="WIP67_FAKE"))
        self.blocked(r,"CURRENT_POINTER_VERSION_STALE")

    def test_no_source_raw_zip_blocks(self):
        r=evaluate(current_data=b"not a zip")
        self.blocked(r,"CURRENT_ZIP_PARSE_FAILURE_BadZipFile")

    def test_snapshot_foreign_workstream_blocks(self):
        r=evaluate(snapshot_change=lambda s:s.update(workstream="other"))
        self.blocked(r,"INDEPENDENT_SNAPSHOT_SHAPE_INVALID")

    def test_snapshot_unrecognized_issuer_field_blocks(self):
        r=evaluate(snapshot_change=lambda s:s.update(issuer="APPROVED"))
        self.blocked(r,"INDEPENDENT_SNAPSHOT_SHAPE_INVALID")

    def test_snapshot_bool_version_blocks(self):
        r=evaluate(snapshot_change=lambda s:s.update(parent_version=True))
        self.blocked(r,"INDEPENDENT_SNAPSHOT_SHAPE_INVALID")

    def test_snapshot_same_current_and_parent_digest_blocks(self):
        def mutate(s):s["parent_sha256"]=s["current_sha256"]
        r=evaluate(snapshot_change=mutate)
        self.blocked(r,"INDEPENDENT_SNAPSHOT_SHAPE_INVALID")

    def test_duplicate_json_before_audit_blocks(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_JSON_FIELD"):
            no_duplicate_json(b'{"schema":"a","schema":"b"}')

    def test_nonfinite_json_before_audit_blocks(self):
        with self.assertRaisesRegex(ValueError,"NONFINITE_JSON"):
            no_duplicate_json(b'{"count":NaN}')

    def test_missing_original_parent_archive_blocks(self):
        child,_=artifact(68)
        parent,_=artifact(67)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"child.zip";p.write_bytes(child)
            missing=Path(d)/"missing.zip"
            spec={"workstream":"aber-hallo-listen-tabellen",
                  "current_sha256":digest(child),"parent_sha256":digest(parent),
                  "current_milestone":"WIP68_CANDIDATE","parent_version":67}
            result=audit(p,missing,spec)
            self.blocked(result,"PARENT_RAW_FILE_MISSING_OR_SYMLINK")

    def test_input_zip_not_modified(self):
        child,_=artifact(68);parent,_=artifact(67)
        with tempfile.TemporaryDirectory() as d:
            c=Path(d)/"child.zip";p=Path(d)/"parent.zip"
            c.write_bytes(child);p.write_bytes(parent)
            before=(digest(c.read_bytes()),digest(p.read_bytes()))
            spec={"workstream":"aber-hallo-listen-tabellen",
                  "current_sha256":before[0],"parent_sha256":before[1],
                  "current_milestone":"WIP68_SYNTHETIC","parent_version":67}
            audit(c,p,spec)
            self.assertEqual(before,(digest(c.read_bytes()),digest(p.read_bytes())))

if __name__=="__main__":
    unittest.main()
