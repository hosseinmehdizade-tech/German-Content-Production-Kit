"""OP02 synthetic compact / exact parent lineage safety regression, no user data."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Verification"))
from audit_op02_compact_parent_chain import audit, CANON,IMPORT,CHECKPOINT,SOURCE,QA,MANIFEST,SUMS,PARENT_PDFS

def h(x):return hashlib.sha256(x).hexdigest()
def dump(x):return json.dumps(x,ensure_ascii=False,sort_keys=True).encode()
def zipdata(files):
    bio=io.BytesIO()
    with ZipFile(bio,"w",ZIP_DEFLATED) as z:
        for k,v in files.items():z.writestr(k,v)
    return bio.getvalue()
def tsv(changed):
    b=io.StringIO()
    w=csv.writer(b,delimiter="\t",lineterminator="\n")
    w.writerow(["id","card_type"]+["field"+str(i) for i in range(21)])
    for i in range(1,788):
        row=[f"ahl-lu-{i:04d}","vocab"]+[""]*21
        if i<=changed:row[19]="wip73"
        w.writerow(row)
    return b.getvalue().encode()
def fixture(changed=6):
    pdfs=[b"%PDF-1.4\nsynthetic source A",b"%PDF-1.4\nsynthetic source B"]
    sources=[{"id":name,"sha256":h(raw)} for name,raw in
             zip(("A1-A2","B1-C2"),pdfs)]
    original={"learning_units":[{"id":f"ahl-lu-{i:04d}","rektion":"parent"} for i in range(1,789)]}
    current={"learning_units":[
        {"id":f"ahl-lu-{i:04d}","rektion":"wip73" if i<=changed else "parent"}
        for i in range(1,789)]}
    parent_files={CANON:dump(original),IMPORT:tsv(0),**dict(zip(PARENT_PDFS,pdfs))}
    parent=zipdata(parent_files)
    expected={"compact_sha256":"","parent_sha256":h(parent),
        "canonical_sha256":h(dump(current)),"import_sha256":h(tsv(changed)),
        "parent_name":"parent.zip","source_sha256":list(map(h,pdfs)),
        "member_count":13,"changed_cards":6,"parent_holds":52,
        "new_attested":6,"current_attested":935,"remaining_holds":46}
    p=expected["parent_sha256"];cs=expected["canonical_sha256"];is_=expected["import_sha256"]
    summary={"changed_distinct_cards":6,"new_exact_attestations":6,
             "wip72_hold_queue_input":52,"carried_holds":46,
             "cumulative_attested":935,"portable_kind":
                "COMPACT_CURRENT_WORKING_SNAPSHOT_WITH_EXACT_PARENT",
             "stage4":"OPEN","stage5_6_7":"NOT_RUN"}
    cp={"schema":"gcpk-wip73-compact-working@1",
        "status":"CURRENT_WIP73_COMPACT_935_ATTESTED_46_HOLDS_STAGE4_OPEN",
        "parent_sha256":p,"canonical_sha256":cs,"import_sha256":is_,
        "full_source_and_history_parent":"parent.zip",
        "source_sha256":sources,"new_attested":6,
        "remaining_holds":46,"stage4":"OPEN","stage5_6_7":"NOT_RUN"}
    qa={"parent_sha256":p,"canonical_sha256":cs,"import_sha256":is_,
        "source_sha256":sources,"counts":dict(summary)}
    src={"parent_full_zip":"parent.zip","parent_sha256":p,
         "source_pdf_sha256":sources,"source_pdf_bytes_not_duplicated":True}
    files={CANON:dump(current),IMPORT:tsv(changed),CHECKPOINT:dump(cp),
           SOURCE:dump(src),QA:dump(qa),
           "01-Final-Import/IMPORT.WORKING.tsv.sha256":(is_+"  IMPORT.WORKING.tsv\n").encode(),
           "04-QA-Review/06-EXACT-INDEPENDENT-EVIDENCE.jsonl":b'{"a":1}\n',
           "04-QA-Review/09-ADVERSARIAL-NEGATIVE-CONTROLS.json":b"[]",
           "04-QA-Review/46-CURRENT-EXTERNAL-HOLDS.jsonl":b'{"a":1}\n',
           "04-QA-Review/52-PARENT-QUEUE-WIP73-DISPOSITIONS.jsonl":b'{"a":1}\n',
           "README-FA-DE.md":b"synthetic",
           }
    return parent,files,summary,sources,expected

def pack(files,summary,sources,expected, *, modify_manifest=None):
    fields=[{"path":k,"size_bytes":len(v),"sha256":h(v)} for k,v in files.items()]
    manifest={"schema":"gcpk-aber-hallo-wip73-compact-current-working@1",
              "workstream":"aber-hallo-listen-tabellen","summary":summary,
              "parent_full_zip":{"name":expected["parent_name"],"sha256":expected["parent_sha256"]},
              "original_source_pdf_sha256":sources,"files":fields,
              "file_count_excluding_manifest_and_checksums":len(files)}
    if modify_manifest:modify_manifest(manifest)
    allfiles=dict(files)
    allfiles[MANIFEST]=dump(manifest)
    allfiles[SUMS]="".join(f"{h(v)}  {n}\n" for n,v in allfiles.items()).encode()
    blob=zipdata(allfiles)
    expected["compact_sha256"]=h(blob)
    return blob

def run(changer=None, changed=6, missing_parent=False, manifest_change=None):
    parent,files,summary,sources,expected=fixture(changed)
    if changer:changer(files,summary,sources,expected)
    compact=pack(files,summary,sources,expected,modify_manifest=manifest_change)
    with tempfile.TemporaryDirectory() as d:
        a=Path(d)/"compact.zip";p=Path(d)/"parent.zip"
        a.write_bytes(compact)
        if not missing_parent:p.write_bytes(parent)
        return audit(a,p,expected)

def edit_json(files,name,key,value):
    x=json.loads(files[name]);x[key]=value;files[name]=dump(x)

class CompactParentGate(unittest.TestCase):
    def blocked(self,change=None,token=None,**kw):
        result=run(change,**kw)
        self.assertEqual(result["status"],"BLOCKED",result)
        if token:self.assertTrue(any(token in e for e in result["errors"]),result)
        self.assertFalse(result["issuer_authenticated"])
        self.assertFalse(result["stage4_semantic_pass"])
        self.assertFalse(result["stage5_7_authorized"])

    def test_valid_compact_only_recovers_not_final(self):
        v=run()
        self.assertEqual(v["status"],"PASS_SCOPED_COMPACT_PARENT_RECOVERY_NOT_FINAL",v)
        self.assertTrue(v["manifest_checksum_valid"],v)
        self.assertEqual(v["parent_original_pdfs_verified"],2)
        self.assertEqual(v["changed_canonical_units"],6)
        self.assertEqual(v["changed_import_rows"],6)
        self.assertFalse(v["issuer_authenticated"])
        self.assertFalse(v["compact_is_final_release"])
        self.assertFalse(v["writer_granted"])

    def test_wrong_parent_original_bytes(self):
        def bad(f,s,q,e):e["parent_sha256"]="f"*64
        self.blocked(bad,"PARENT_OUTER_SHA_MISMATCH")

    def test_parent_missing_must_block(self):
        self.blocked(missing_parent=True,token="PARENT_FILE_MISSING")

    def test_wrong_expected_compact_hash(self):
        def bad(f,s,q,e): e["canonical_sha256"]="f"*64
        self.blocked(bad,"EXTERNALLY_PINNED_canonical_sha256_DRIFT")

    def test_more_than_declared_six_rows(self):
        self.blocked(changed=7,token="IMPORT_CHANGED_ROW_COUNT_DRIFT")

    def test_more_than_declared_six_canonical_units(self):
        self.blocked(changed=7,token="CANONICAL_UNITS_OR_ID_LINEAGE_DRIFT")

    def test_fully_rehashed_wrong_checkpoint_parent(self):
        self.blocked(lambda f,s,q,e:edit_json(f,CHECKPOINT,"parent_sha256","f"*64),
                     "CHECKPOINT_PARENT_HASH_DRIFT")

    def test_fully_rehashed_wrong_source_parent(self):
        self.blocked(lambda f,s,q,e:edit_json(f,SOURCE,"parent_sha256","f"*64),
                     "SOURCE_PARENT_HASH_DRIFT")

    def test_stale_canonical_checkpoint(self):
        self.blocked(lambda f,s,q,e:edit_json(f,CHECKPOINT,"canonical_sha256","f"*64),
                     "COMPACT_CHECKPOINT_canonical_sha256_DRIFT")

    def test_stale_import_qa(self):
        self.blocked(lambda f,s,q,e:edit_json(f,QA,"import_sha256","f"*64),
                     "COMPACT_QA_import_sha256_DRIFT")

    def test_mismatched_original_source_claim(self):
        def bad(f,s,q,e):
            edit_json(f,SOURCE,"source_pdf_sha256",[])
        self.blocked(bad,"SOURCE_HASH_DECLARATION_DRIFT")

    def test_rehashed_ambiguous_stage4_pass_claim(self):
        def bad(f,s,q,e):s["stage4"]="PASS"
        self.blocked(bad,"COMPACT_NOT_EXPLICITLY_NONFINAL")

    def test_rehashed_stage5_pass_claim(self):
        def bad(f,s,q,e):edit_json(f,CHECKPOINT,"stage5_6_7","PASS")
        self.blocked(bad,"COMPACT_ACTIVE_SCOPE_OR_STAGE_CLAIM_DRIFT")

    def test_duplicate_json_field(self):
        def bad(f,s,q,e):f[CHECKPOINT]=f[CHECKPOINT][:-1]+b', "parent_sha256":"f"}'
        self.blocked(bad,"COMPACT_PARSE_OR_SCHEMA_ValueError")

    def test_manifest_member_digest_tampered_then_rehashed_checksums(self):
        def bad(m):m["files"][0]["sha256"]="f"*64
        self.blocked(manifest_change=bad,token="COMPACT_MANIFEST_MEMBER_HASH_DRIFT")

    def test_declared_progress_mismatch(self):
        def bad(f,s,q,e):s["carried_holds"]=45
        self.blocked(bad,"COMPACT_QA_COUNT_DRIFT")

    def test_no_source_pdf_payload_in_compact_does_not_claim_pdfs_present(self):
        result=run()
        self.assertEqual(result["parent_original_pdfs_verified"],2)
        self.assertTrue(result["parent_required"])

if __name__=="__main__":unittest.main()
