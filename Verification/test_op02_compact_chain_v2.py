"""OP02 synthetic 3-ZIP chain regression; no real PDFs, no production writer."""
import hashlib, io, json, sys, tempfile, unittest, csv
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Verification"))
from audit_op02_compact_chain_v2 import (
    audit,CANON,IMPORT,MANIFEST,SUMS,SOURCE,CHECK74,QA74,
    digest,strict_json,leaf_paths,raw_zip)
from test_op02_compact_parent_chain import fixture,pack
def dump(x):return json.dumps(x,sort_keys=True).encode()
def zipped(entries):
    out=io.BytesIO()
    with ZipFile(out,"w",compression=ZIP_DEFLATED) as z:
        for name,raw in entries.items():z.writestr(name,raw)
    return out.getvalue()
def readbin(b):
    with ZipFile(io.BytesIO(b)) as z:return {n:z.read(n) for n in z.namelist()}
def tsv_edit(raw,ids,extra=False):
    data=list(csv.reader(io.StringIO(raw.decode()),delimiter="\t"))
    for r in data[1:]:
        if r[0] in ids:r[19]="WIP74_CHANGED"
    if extra:data[1][20]="UNRELATED_DRIFT"
    o=io.StringIO();w=csv.writer(o,delimiter="\t",lineterminator="\n")
    w.writerows(data)
    return o.getvalue().encode()
def build(variant=None):
    parent,files,summary,sources,prior=fixture()
    w73raw=pack(files,summary,sources,prior)
    z73=readbin(w73raw)
    prior_c=json.loads(z73[CANON])
    # Create revised WIP73 baseline with existing nested rection/translation
    # fields before adding WIP74-only changes.
    units=prior_c["learning_units"]
    for i in range(7):
        if i<5:units[i]["metadata"]={"rection_qa":{"patterns":[{"qa_status":"HOLD"}]}}
        else:
            units[i]["details"]={"kombinationen":[{"text_fa":"old"}]}
            units[i]["examples"]=[{"translations":[{"text":"old"}]}]
    files[CANON]=dump(prior_c)
    updated_c=digest(files[CANON])
    cp73=json.loads(files["06-Checkpoint-State/WIP73-WORKING-CHECKPOINT.json"])
    qa73=json.loads(files["05-Reports/WIP73-SCOPED-QA.json"])
    cp73["canonical_sha256"]=updated_c;qa73["canonical_sha256"]=updated_c
    files["06-Checkpoint-State/WIP73-WORKING-CHECKPOINT.json"]=dump(cp73)
    files["05-Reports/WIP73-SCOPED-QA.json"]=dump(qa73)
    prior["canonical_sha256"]=updated_c
    w73raw=pack(files,summary,sources,prior)
    z73=readbin(w73raw)
    w74c=json.loads(z73[CANON]);units=w74c["learning_units"]
    for i in range(5):
        units[i]["metadata"]["rection_qa"]["patterns"][0]["qa_status"]="ATTESTED_WIP74"
    for i in range(5,7):
        units[i]["details"]["kombinationen"][0]["text_fa"]="new"
        units[i]["examples"][0]["translations"][0]["text"]="new"
    ids=[x["id"] for x in units[:7]]
    w74c=dump(w74c)
    w74t=tsv_edit(z73[IMPORT],ids,variant=="extra_tsv_column")
    hash74c,hash74t=digest(w74c),digest(w74t)
    source_claim=json.loads(z73[SOURCE])["source_pdf_sha256"]
    full_name=prior["parent_name"]
    cp74={"workstream":"aber-hallo-listen-tabellen",
        "state":"CURRENT_WIP74_COMPACT_STAGE4_OPEN","stage4":"OPEN",
        "stage5_to_7":"NOT_RUN","parent_sha256":digest(w73raw),
        "canonical_sha256":hash74c,"import_sha256":hash74t,
        "attested":940,"held":41,
        "immutable_source_parent_sha256":digest(parent)}
    s74={"immutable_parent_full_zip":full_name,
         "full_parent_sha256":digest(parent),
         "parent_wip73_sha256":digest(w73raw),
         "source_pdf_sha256":source_claim,
         "source_pdf_bytes_not_duplicated":True}
    nums={"units":788,"lexical_cards":787,"examples_total":3152,
          "new_independent_exact_rektion":5,"rektion_attested_total":940,
          "rektion_governed_total":981,"rektion_remaining_exact_holds":41,
          "distinct_cards_changed":7,"learner_translation_corrections":4,
          "translation_correction_cards":2,"untouched_import_rows_byte_equal":780}
    qa74={"parent_wip73_sha256":digest(w73raw),
        "immutable_full_parent_wip72_sha256":digest(parent),
        "canonical_sha256":hash74c,"import_sha256":hash74t,
        "counts":dict(nums),
        "scope_boundaries":{
            "stage4_full_semantic_translation_source_adversarial":"OPEN",
            "stage5_6_7":"NOT_RUN"}}
    pack74={
        CANON:w74c,IMPORT:w74t,
        "01-Final-Import/IMPORT.WORKING.tsv.sha256":
            (hash74t+"  IMPORT.WORKING.tsv\n").encode(),
        SOURCE:dump(s74), CHECK74:dump(cp74),QA74:dump(qa74),
        "04-QA-Review/04-LEARNER-TRANSLATION-REPAIRS.jsonl":b'{"a":1}\n'*4,
        "04-QA-Review/05-NEW-INDEPENDENT-CASE-SENSE-EVIDENCE.jsonl":b'{"a":1}\n'*5,
        "04-QA-Review/41-REMAINING-EXACT-HOLDS.jsonl":b'{"a":1}\n'*41,
        "04-QA-Review/46-PARENT-HOLD-QUEUE-DISPOSITIONS.jsonl":b'{"a":1}\n'*46,
        "04-QA-Review/DETERMINISTIC-RISK-FLAGS-NOT-SEMANTIC-PASS.jsonl":b'{"a":1}\n'*3,
        "README-FA-DE.md":b"synthetic compact only",
    }
    if variant=="parent_claim":
        cp74["parent_sha256"]="f"*64
        pack74[CHECK74]=dump(cp74)
    if variant=="stage4_fake":
        cp74["stage4"]="PASS"
        pack74[CHECK74]=dump(cp74)
    if variant=="source_claim":
        s74["source_pdf_sha256"]=[]
        pack74[SOURCE]=dump(s74)
    if variant=="four_translation":
        for i in range(5):
            units[i]["metadata"]["rection_qa"]["patterns"][0]["qa_status"]="HOLD"
        # Make one more translation-only unit instead of a rektion-only one.
        units[4]["details"]={"kombinationen":[{"text_fa":"new"}]}
        units[4]["examples"]=[{"translations":[{"text":"new"}]}]
        pack74[CANON]=dump(w74c)
    if variant=="manifest_count":nums["distinct_cards_changed"]=8
    manifest={"schema":"gcpk-aber-hallo-wip74-compact@1",
              "date":"2026-10-31","counts":nums,"parent_sha256":digest(w73raw),
              "full_source_parent_sha256":digest(parent)}
    manifest["files"]=[{"path":n,"sha256":digest(raw),"size_bytes":len(raw)}
                       for n,raw in pack74.items()]
    pack74[MANIFEST]=dump(manifest)
    pack74[SUMS]="".join(f"{digest(raw)}  {n}\n"
                        for n,raw in pack74.items()).encode()
    w74raw=zipped(pack74)
    ex={"wip74_sha":digest(w74raw),"wip73_sha":digest(w73raw),
        "wip72_sha":digest(parent),"wip74_canonical_sha":hash74c,
        "wip74_import_sha":hash74t,"wip73_canonical_sha":updated_c,
        "wip73_import_sha":prior["import_sha256"],
        "pdf_sha":prior["source_sha256"],"changed_cards":7,
        "rektion_cards":5,"translation_cards":2,"translations":4,
        "new_attested":5,"attested":940,"holds":41}
    return {72:parent,73:w73raw,74:w74raw},ex
def check(variant=None,changed_pin=None,omit=None):
    binary,pins=build(variant)
    if changed_pin:pins.update(changed_pin)
    with tempfile.TemporaryDirectory() as root:
        paths={}
        for v in (72,73,74):
            paths[v]=Path(root)/f"WIP{v}.zip"
            if v!=omit:paths[v].write_bytes(binary[v])
        # Match the independently expected immutable full-parent basename
        # as declared by WIP73 (not WIP73's synthetic placeholder name).
        paths[72].rename(Path(root)/pins.get("parent_name","parent.zip")) if omit!=72 else None
        paths[72]=Path(root)/"parent.zip"
        return audit(paths,pins)
class ThreeHop(unittest.TestCase):
    def hold(self,variant=None,changed_pin=None,omit=None):
        z=check(variant,changed_pin,omit)
        self.assertEqual(z["status"],"BLOCKED",z)
        for field in ("issuer_authenticated","stage4_semantic_pass",
                      "stage5_7_authorized","writer_granted","is_final_release"):
            self.assertFalse(z[field])
    def test_synthetic_happy_path_nonfinal(self):
        z=check()
        self.assertEqual(z["status"],"PASS_SCOPED_THREE_ZIP_RECOVERY_NOT_FINAL",z)
        self.assertEqual(z["verified_archive_count"],3)
        self.assertEqual(z["verified_original_pdfs"],2)
        self.assertEqual(z["rektion_only_units"],5)
        self.assertEqual(z["translation_only_units"],2)
        self.assertFalse(z["is_final_release"])
    def test_parent_missing_blocks(self):self.hold(omit=72)
    def test_middle_compact_missing_blocks(self):self.hold(omit=73)
    def test_self_rehashed_wrong_parent_claim_blocks(self):self.hold("parent_claim")
    def test_self_rehashed_fake_stage4_pass_blocks(self):self.hold("stage4_fake")
    def test_self_rehashed_source_pdf_claim_blocks(self):self.hold("source_claim")
    def test_wrong_external_zip_sha_blocks(self):self.hold(changed_pin={"wip74_sha":"f"*64})
    def test_extra_import_column_change_blocks(self):self.hold("extra_tsv_column")
    def test_manifest_qa_count_disagree_blocks(self):self.hold("manifest_count")
    def test_bad_independent_expected_counts_blocks(self):self.hold(changed_pin={"changed_cards":8})
    def test_leaf_path_classification(self):
        self.assertEqual(leaf_paths({"x":1},{"x":2}),[".x"])
        self.assertEqual(leaf_paths({"x":{"a":3}},{"x":{"a":3}}),[])
if __name__=="__main__":unittest.main()
