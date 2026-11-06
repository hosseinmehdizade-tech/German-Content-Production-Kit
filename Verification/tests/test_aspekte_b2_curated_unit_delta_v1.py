"""Native B2 current-vs-immediate-curated-parent test with synthetic 160-row lineage.

This does not embed private flashcards or certify human semantic quality.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"Verification/verify_aspekte_b2_curated_unit_delta_v1.py"
spec=importlib.util.spec_from_file_location("b2_native_curated_delta",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

HEADER=(
    "unit_id","source_ordinals","source_ids","front_de_preview",
    "back_fa_preview","example_1_de","example_1_fa","example_2_de",
    "example_2_fa","POS_or_unit_type","unit_policy","prior_card_link",
    "qa_status","export_importable","linguistic_release_approved",
    "source_example_count_in_original_R42","r43_new_example_sentence_count","note"
)
NONCARD=(
    "source_ordinal","source_id","object_id","type","linked_learner_unit",
    "source_de_immutable","source_fa_immutable","front_de_current",
    "back_fa_current","example_1_de","example_1_fa","example_2_de",
    "example_2_fa","next_gate","importable","release_approved"
)


def encode(rows,fields):
    f=io.StringIO(newline="")
    w=csv.DictWriter(f,fieldnames=fields,delimiter=",",lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return f.getvalue().encode("utf-8")


def sample():
    units=[]
    for ordinal in range(1549,1709):
        if ordinal in (1630,1660,1641):
            continue
        r={
            "unit_id":f"ab2-l01-u-{ordinal}",
            "source_ordinals":"1640;1641" if ordinal==1640 else str(ordinal),
            "source_ids":f"src-{ordinal}",
            "front_de_preview":"Beispiel",
            "back_fa_preview":"مثال",
            "example_1_de":"Das ist ein Beispiel.",
            "example_1_fa":"این یک مثال است.",
            "example_2_de":"Hier steht ein Beispiel.",
            "example_2_fa":"اینجا یک مثال آمده است.",
            "POS_or_unit_type":"SOURCE_LEARNER_UNIT",
            "unit_policy":"KEEP_DISTINCT",
            "prior_card_link":"",
            "qa_status":"AI_EDITORIAL_PREVIEW_NOT_INDEPENDENT",
            "export_importable":"FALSE",
            "linguistic_release_approved":"FALSE",
            "source_example_count_in_original_R42":"0",
            "r43_new_example_sentence_count":"0",
            "note":"synthetic only"
        }
        units.append(r)
    extra=copy.deepcopy(next(x for x in units if x["source_ordinals"]=="1586"))
    extra["unit_id"]="ab2-l01-u-1586-split"
    units.append(extra)
    assert len(units)==158
    noncard=[]
    for ordinal in (1630,1660):
        noncard.append({
            "source_ordinal":str(ordinal),"source_id":f"src-{ordinal}",
            "object_id":f"nc-{ordinal}","type":"NONCARD",
            "linked_learner_unit":"","source_de_immutable":"Wort",
            "source_fa_immutable":"کلمه","front_de_current":"Wort",
            "back_fa_current":"کلمه","example_1_de":"Ein Beispiel.",
            "example_1_fa":"یک مثال.","example_2_de":"Noch ein Beispiel.",
            "example_2_fa":"مثالی دیگر.","next_gate":"NOT_APPROVED",
            "importable":"FALSE","release_approved":"FALSE"
        })
    return units,noncard


class NativeB2Delta(unittest.TestCase):
    def setUp(self):
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root=Path(td.name)
        self.old=root/"L01-CURRENT-158-UNIT-REVIEW-R46-NONIMPORT.csv"
        self.new=root/"L01-CURRENT-158-UNIT-REVIEW-R47-NONIMPORT.csv"
        self.nc=root/"L01-CURRENT-2-NONCARD-OBJECTS-R45-NONIMPORT.csv"
        self.before,self.noncard=sample()
        self.after=copy.deepcopy(self.before)
        self.after[0]["back_fa_preview"]="نمونه؛ مثال"
        self.latest={"latest_scoped_audit":{
            "label":"L01_R47_1_UNIT_1_FIELD_NONIMPORT",
            "parent_R46_158_current_sha256":"",
            "current_158_draft_preview_path":"/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Current/"+self.new.name,
            "current_158_draft_preview_sha256":"",
            "noncard_2_current_path":"/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Current/"+self.nc.name,
            "noncard_2_current_sha256":"",
            "source_rows_coverage":160,"draft_unique_ids":158,
            "R44_legacy_HOLDs":17,"identity_or_target_HOLDs":[1575,1616,1630,1660],
            "modified_unit_count":1,"modified_field_count":1,
            "unchanged_unit_count":157,"stage2_approved":False,
            "importable":False,"imported_cards":0,
            "stage3_to_stage7":"NOT_STARTED",
            "global_portable_project_checkpoint":"L05_R25_UNCHANGED"}}
        self.rewrite()

    def rewrite(self):
        for file,data,fields,key in (
            (self.old,self.before,HEADER,"parent_R46_158_current_sha256"),
            (self.new,self.after,HEADER,"current_158_draft_preview_sha256"),
            (self.nc,self.noncard,NONCARD,"noncard_2_current_sha256")
        ):
            raw=encode(data,fields)
            file.write_bytes(raw)
            self.latest["latest_scoped_audit"][key]=hashlib.sha256(raw).hexdigest()

    def check(self):
        return m.audit(self.latest,self.old,self.new,self.nc)

    def test_realistic_160_source_to_158_draft_delta_and_no_original(self):
        out=self.check()
        self.assertEqual((out["changed_units"],out["changed_fields"],
                          out["unchanged_units"]),(1,1,157))
        self.assertEqual((out["covered_source_ordinals"],
                          out["noncard_supplementary_objects"]),(160,2))
        self.assertEqual(out["source_comparison"],
                         "NONE__USER_CURATED_PARENT_ONLY")
        self.assertFalse(out["formal_stage2_approval"])

    def test_changed_current_content_without_repin_fails(self):
        self.after[0]["back_fa_preview"]="ویرایش بی‌سند"
        self.new.write_bytes(encode(self.after,HEADER))
        with self.assertRaisesRegex(m.CuratedB2Error,"SHA256_MISMATCH"):
            self.check()

    def test_missing_immediate_parent_pin_fails(self):
        del self.latest["latest_scoped_audit"]["parent_R46_158_current_sha256"]
        with self.assertRaisesRegex(m.CuratedB2Error,
                                    "MISSING_IMMEDIATE_ACCEPTED_CURATED_PARENT_PIN"):
            self.check()

    def test_unapproved_import_bit_fails_even_when_hash_recomputed(self):
        self.after[0]["export_importable"]="TRUE"
        self.rewrite()
        with self.assertRaisesRegex(m.CuratedB2Error,"UNAPPROVED_CARD_MARKED_IMPORTABLE"):
            self.check()

    def test_lost_existing_persian_translation_fails(self):
        self.after[0]["back_fa_preview"]=""
        self.rewrite()
        with self.assertRaisesRegex(m.CuratedB2Error,"CURATED_BILINGUAL_CONTENT_BLANKED"):
            self.check()

    def test_source_identity_change_fails(self):
        self.after[0]["source_ordinals"]="1548"
        self.rewrite()
        with self.assertRaisesRegex(m.CuratedB2Error,"CURATED_IDENTITY_OR_PROVENANCE_CHANGED"):
            self.check()

    def test_extra_old_book_row_cannot_be_reintroduced(self):
        self.after.append(dict(self.after[0],unit_id="raw-source-resurrected"))
        self.rewrite()
        with self.assertRaisesRegex(m.CuratedB2Error,
                                    "PROVISIONAL_UNIT_IDS_OR_CARD_COUNT_CHANGED"):
            self.check()

    def test_fake_delta_scope_count_fails(self):
        self.latest["latest_scoped_audit"]["modified_field_count"]=15
        with self.assertRaisesRegex(m.CuratedB2Error,"DELTA_COUNTS_DISAGREE"):
            self.check()

    def test_noncard_source_object_cannot_be_dropped(self):
        self.noncard.pop()
        self.rewrite()
        with self.assertRaisesRegex(m.CuratedB2Error,"NONCARD_CONTENT_OBJECTS_DROPPED"):
            self.check()

    def test_new_rev_number_must_match_immediate_parent(self):
        self.latest["latest_scoped_audit"]["label"]="L01_R48_NEW_DRAFT"
        with self.assertRaisesRegex(m.CuratedB2Error,
                                    "MISSING_IMMEDIATE_ACCEPTED_CURATED_PARENT_PIN"):
            self.check()

    def test_parent_and_new_inputs_not_written(self):
        oldhash=hashlib.sha256(self.old.read_bytes()).hexdigest()
        currenthash=hashlib.sha256(self.new.read_bytes()).hexdigest()
        self.check()
        self.assertEqual(hashlib.sha256(self.old.read_bytes()).hexdigest(),oldhash)
        self.assertEqual(hashlib.sha256(self.new.read_bytes()).hexdigest(),currenthash)

    def test_real_git_latest_is_current_revision_nonimport_not_final(self):
        latest=json.loads((ROOT/"Workspaces/aspekte-b2-v336/LATEST.json").read_text(encoding="utf8"))
        scope,_rev,_sha=m.scope_contract(latest)
        self.assertTrue(scope["current_158_draft_preview_path"].endswith("-NONIMPORT.csv"))
        self.assertFalse(scope["stage2_approved"])
        self.assertEqual(scope["imported_cards"],0)


if __name__=="__main__":
    unittest.main()
