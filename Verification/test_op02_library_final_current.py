"""OP02 guarded Library-final admission: exact Aber Hallo active metadata only.

Synthetic ZIP fixtures simulate external off-repo builders that bypass
guarded_zip; no user content or Library files ever changed.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
from library_publish_preflight import audit
from test_op02_guarded_aber_current import parts, PTR,WORK,MAN,CANON,IMP

def make(tmp, files=None, *,filename="candidate.zip"):
    src=parts() if files is None else files
    p=Path(tmp)/filename
    with ZipFile(p,"w",compression=ZIP_DEFLATED) as z:
        for n,raw in src.items():z.writestr(n,raw)
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    receipt=Path(tmp)/"quality.json"
    receipt.write_text(json.dumps({
        "status":"PASS","stage7":"PASS","archive_sha256":sha,
    }),encoding="utf-8")
    return p,receipt,sha

def invoke(tmp, files=None, *,workstream="aber-hallo-listen-tabellen",
           purpose="final_delivery",filename="candidate.zip",evidence_mode=True):
    p,receipt,sha=make(tmp,files,filename=filename)
    if purpose=="required_recovery":
        receipt.write_text(json.dumps({"archive_sha256":sha,
            "recovery_gap":"raw replay needed"}),encoding="utf-8")
    cat={"complete":True,"scope":"workstream","workstream":workstream,
         "entries":[]}
    return audit(p,purpose=purpose,
        destination="/German-Content-Production-Kit/Final/"+p.name,
        workstream=workstream,catalog=cat,
        evidence=receipt if evidence_mode else None,
        user_request="user explicitly requested checkpoint" if purpose=="explicit_user_checkpoint" else None)

def mod_json(files,name,field,value):
    doc=json.loads(files[name])
    doc[field]=value
    files[name]=json.dumps(doc).encode()

class LibraryFinalCurrent(unittest.TestCase):
    def evaluate(self,fn=None,**options):
        with tempfile.TemporaryDirectory() as d:
            files=parts()
            if fn:fn(files)
            return invoke(d,files,**options)

    def fails(self,fn,reason="ABER_HALLO_FINAL_CURRENT_METADATA_STALE",**options):
        x=self.evaluate(fn,**options)
        self.assertEqual(x["decision"],"BLOCK",x)
        self.assertEqual(x["reason"],reason,x)
        return x

    def test_fully_coherent_final_admitted_only_as_library_preflight(self):
        x=self.evaluate()
        self.assertEqual(x["decision"],"ALLOW",x)
        self.assertEqual(x["reason"],"PURPOSE_HASH_AND_CATALOG_VERIFIED",x)

    def test_future_version_75(self):
        def future(f):
            newer=parts(75)
            f.clear();f.update(newer)
        x=self.evaluate(future)
        self.assertEqual(x["decision"],"ALLOW",x)

    def test_wip66_parent_pointer_copied_to_wip70_rejected(self):
        self.fails(lambda f:mod_json(f,PTR,"current","WIP66_STALE"))

    def test_wip70_pointer_main_canonical_correct_but_working_hash_stale(self):
        self.fails(lambda f:mod_json(f,PTR,"working_canonical_sha256","f"*64))

    def test_wip70_pointer_main_import_correct_but_working_hash_stale(self):
        self.fails(lambda f:mod_json(f,PTR,"working_import_sha256","f"*64))

    def test_wip65_working_state_status_reused_blocks(self):
        self.fails(lambda f:mod_json(f,WORK,"status","WORKING_WIP65_OLD"))

    def test_wip65_working_state_legacy_canonical_hash_blocks(self):
        self.fails(lambda f:mod_json(f,WORK,"canonical_sha256","f"*64))

    def test_wrong_manifest_summary_version_blocks(self):
        def change(f):
            j=json.loads(f[MAN]);j["summary"]["status"]="CURRENT_WIP69_OLD"
            f[MAN]=json.dumps(j).encode()
        self.fails(change)

    def test_missing_pointer_blocks(self):
        self.fails(lambda f:f.pop(PTR))

    def test_missing_working_state_blocks(self):
        self.fails(lambda f:f.pop(WORK))

    def test_malformed_pointer_blocks(self):
        self.fails(lambda f:f.update({PTR:b'{"current":NaN}'}))

    def test_duplicate_pointer_key_blocks(self):
        self.fails(lambda f:f.update({PTR:f[PTR][:-1]+b', "current":"WIP70_DUP"}'}))

    def test_same_malformed_candidate_validated_major_blocks(self):
        self.fails(lambda f:mod_json(f,PTR,"current","WIP69_STALE"),
                   purpose="validated_major_checkpoint")

    def test_other_workstream_unchanged(self):
        x=self.evaluate(lambda f:mod_json(f,PTR,"current","WIP66_STALE"),
                        workstream="menschen-b1-24-lessons-v336")
        self.assertEqual(x["decision"],"ALLOW",x)

    def test_recovery_damaged_current_still_retains_scoped_recovery_route(self):
        x=self.evaluate(lambda f:mod_json(f,PTR,"current","WIP66_STALE"),
                        purpose="required_recovery")
        self.assertEqual(x["decision"],"ALLOW",x)
        self.assertEqual(x["workstream"],"aber-hallo-listen-tabellen")

    def test_explicit_checkpoint_keeps_raw_recovery_route(self):
        x=self.evaluate(lambda f:mod_json(f,PTR,"current","WIP66_STALE"),
                        purpose="explicit_user_checkpoint")
        self.assertEqual(x["decision"],"ALLOW",x)

    def test_final_without_stage7_evidence_stays_hold(self):
        x=self.evaluate(evidence_mode=False)
        self.assertEqual(x["decision"],"HOLD",x)
        self.assertEqual(x["reason"],"QUALITY_OR_RECOVERY_EVIDENCE_MISSING")

    def test_fake_archive_with_named_aber_workstream_but_no_active_roles_blocks(self):
        def generic(f):
            f.clear()
            f["cards.tsv"]=b"id\n"
        self.fails(generic,reason="ABER_HALLO_FINAL_ACTIVE_CONTRACT_MISSING")

    def test_active_metadata_cannot_be_claimed_by_foreign_manifest(self):
        self.fails(lambda f:mod_json(f,MAN,"workstream","menschen-a2"))

    def test_wip_filename_still_blocked_before_final_stage(self):
        x=self.evaluate(filename="aber-hallo-WIP70.zip")
        self.assertEqual(x["decision"],"BLOCK",x)
        self.assertEqual(x["reason"],"ROUTINE_WIP_ZIP")

if __name__=="__main__":
    unittest.main()
