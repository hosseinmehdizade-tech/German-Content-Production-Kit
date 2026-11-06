"""Read-only B2 L02 current draft subset safety; no private card content in Git."""
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
SPEC=importlib.util.spec_from_file_location(
    "l02subset",ROOT/"Verification/verify_aspekte_b2_l02_curated_subset_v1.py")
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def encode_csv(rows,header):
    f=io.StringIO(newline="")
    w=csv.DictWriter(f,fieldnames=header,lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return f.getvalue().encode("utf-8")


class CuratedL02Subset(unittest.TestCase):
    def setUp(self):
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root=Path(td.name)
        self.parent=root/"STAGE2-L02-R14-108-ROW-SOURCE-BOUND-OVERLAY.jsonl"
        self.draft=root/"L02-R15-FIRST-12-CURATED-UNIT-PREVIEW-NONIMPORT.csv"
        self.parents=[{"source_csv_ordinal":i,"source_row_id":f"ab2-src-{i:06d}",
                       "source_headword_de_raw":"synthetic source marker"}
                      for i in range(1709,1817)]
        self.cards=[]
        for i in range(1709,1721):
            self.cards.append({
                "unit_id":f"ab2-l02-u-{i}","source_ordinal":str(i),
                "source_id":f"ab2-src-{i:06d}",
                "front_de_preview":"das Wort","back_fa_preview":"کلمه",
                "example_1_de":"Das ist ein Wort.",
                "example_1_fa":"این یک واژه است.",
                "example_2_de":"Dieses Wort ist neu.",
                "example_2_fa":"این واژه جدید است.",
                "editorial_parent_overlay":"L02_R14",
                "qa_status":"SINGLE_AI_EDITORIAL_DRAFT_NOT_INDEPENDENT",
                "export_importable":"FALSE",
                "linguistic_release_approved":"FALSE",
                "note":"SYNTHETIC"
            })
        self.scope={
            "label":"L02_R15_FIRST_12_CURATED_DRAFT_UNITS_NONIMPORT",
            "lesson":2,"project_id":"aspekte-b2",
            "source_rows":108,"source_ordinal_range":[1709,1816],
            "parent_overlay_path":"/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Current/"+self.parent.name,
            "current_draft_path":"/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Current/"+self.draft.name,
            "accepted_editorial_parent":"R14_108_SOURCE_BOUND_OVERLAY",
            "parent_overlay_sha256":"","current_draft_sha256":"",
            "current_draft_rows":12,"bilingual_example_pairs":24,
            "remaining_parent_records_not_yet_curated_to_units":96,
            "next_ordinal_to_curate":1721,"source_rows_unchanged":True,
            "original_source_membership_reaudited":False,
            "prior_user_cards_modified":False,"importable":False,
            "stage2_approved":False,"formal_stage4_qa_approved":False,
            "stage3_to_stage7":"NOT_STARTED"
        }
        self.refresh()

    def refresh(self):
        raw="\n".join(json.dumps(row,ensure_ascii=False) for row in self.parents)+"\n"
        self.parent.write_text(raw,encoding="utf8")
        self.scope["parent_overlay_sha256"]=hashlib.sha256(self.parent.read_bytes()).hexdigest()
        bytes_draft=encode_csv(self.cards,list(self.cards[0]))
        self.draft.write_bytes(bytes_draft)
        self.scope["current_draft_sha256"]=hashlib.sha256(bytes_draft).hexdigest()

    def check(self):
        return m.audit({"latest_l02_scoped_audit":self.scope},self.parent,self.draft)

    def test_first_12_of_108_are_current_not_the_old_raw_book(self):
        r=self.check()
        self.assertEqual((r["parent_rows"],r["projected_draft_units"],
                          r["unprojected_parent_units"],r["next_ordinal"]),(108,12,96,1721))
        self.assertEqual(r["source_compared"],"NONE__CURATED_PARENT_R14_ONLY")

    def test_wrong_current_hash_denied(self):
        self.cards[0]["back_fa_preview"]="untrusted"
        self.draft.write_bytes(encode_csv(self.cards,list(self.cards[0])))
        with self.assertRaisesRegex(m.B2L02Failure,"CURATED_SHA256_MISMATCH"):
            self.check()

    def test_false_release_bit_denied(self):
        self.cards[0]["export_importable"]="TRUE"
        self.refresh()
        with self.assertRaisesRegex(m.B2L02Failure,"UNAPPROVED_DRAFT_MARKED_FINAL"):
            self.check()

    def test_unverified_source_identity_denied(self):
        self.cards[0]["source_id"]="old-raw-fake-id"
        self.refresh()
        with self.assertRaisesRegex(m.B2L02Failure,"PROPOSED_CARD_NOT_IN_CURATED_PARENT"):
            self.check()

    def test_missing_bilingual_pair_denied(self):
        self.cards[0]["example_2_fa"]=""
        self.refresh()
        with self.assertRaisesRegex(m.B2L02Failure,"MISSING_BILINGUAL_CONTENT"):
            self.check()

    def test_duplicate_id_denied(self):
        self.cards[1]["unit_id"]=self.cards[0]["unit_id"]
        self.refresh()
        with self.assertRaisesRegex(m.B2L02Failure,"DUPLICATE_OR_UNSTABLE_DRAFT_ID"):
            self.check()

    def test_false_full_chapter_claim_denied(self):
        self.scope["current_draft_rows"]=108
        with self.assertRaisesRegex(m.B2L02Failure,"SCOPED_PARENT_OR_DRAFT_ROW_COUNT_CHANGED"):
            self.check()

    def test_historical_raw_authority_denied(self):
        self.scope["parent_overlay_path"]="/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Source/original.csv"
        with self.assertRaisesRegex(m.B2L02Failure,"NONOWNER_OR_OLD_RAW_SOURCE_PATH"):
            self.check()

    def test_modifying_old_parent_without_repin_denied(self):
        self.parents[0]["source_row_id"]="tampered"
        self.parent.write_text("\n".join(json.dumps(x) for x in self.parents)+"\n",encoding="utf8")
        with self.assertRaisesRegex(m.B2L02Failure,"CURATED_SHA256_MISMATCH"):
            self.check()

    def test_no_file_writer(self):
        before=[p.read_bytes() for p in (self.parent,self.draft)]
        self.check()
        self.assertEqual(before,[p.read_bytes() for p in (self.parent,self.draft)])

    def test_real_git_pointer_does_not_reset_l01_or_approve_l02(self):
        latest=json.loads((ROOT/"Workspaces/aspekte-b2-v336/LATEST.json").read_text(encoding="utf8"))
        l02=m.scope(latest)
        self.assertEqual(l02["current_draft_rows"],12)
        self.assertEqual(l02["next_ordinal_to_curate"],1721)
        self.assertFalse(l02["importable"])
        self.assertTrue(latest["latest_scoped_audit"]["label"].startswith("L01_R"))


if __name__=="__main__":
    unittest.main()
