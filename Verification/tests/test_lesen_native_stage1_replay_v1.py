"""Actual Lesen native Stage1 source order and QA replay, including hostile mutations.

Tests never load copyrighted PDF bytes or rewrite a content workstream.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"Verification/replay_lesen_stage1_native_v1.py"
spec=importlib.util.spec_from_file_location("gfp_lesen_native_stage1",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class RealReadingSourceInventoryReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roles=m.git_index_bytes()
        cls.docs={key:value["document"] for key,value in cls.roles.items()}
        cls.hashes={key:value["sha256"] for key,value in cls.roles.items()}
        cls.blobs={key:value["blob"] for key,value in cls.roles.items()}
        cls.actual=m.execute()

    def replay(self,mutate=None):
        docs=copy.deepcopy(self.docs)
        hashes=copy.deepcopy(self.hashes)
        if mutate:mutate(docs,hashes)
        return m.check(docs,hashes,self.blobs)

    def test_full_real_git_stage1_replay_and_no_source_current_claim(self):
        self.assertEqual(self.actual["schema"],m.SCHEMA)
        self.assertEqual(self.actual["status"],
            "PASS_ACTUAL_GIT_READING_STAGE1_DERIVED_BYTES_AND_STRUCTURE_REPLAY_ONLY")
        self.assertEqual(self.actual["replayed_counts"],
           {"topics":68,"pages":76,"continuations":6,"blanks":1,
            "duplicate_occurrences":1,"unnumbered_topics":1})
        self.assertFalse(self.actual["actual_independent_stage1_source_pdf_bytes_revalidated"])
        self.assertEqual(self.actual["new_policy_adoption"],"NOT_ADOPTED")
        self.assertEqual(self.actual["linguistic_stage4"],"NOT_RUN")

    def test_actual_derived_sha_bytes_match_recorded_qa_receipt(self):
        report=self.actual["actual_git_derived_evidence"]
        for role in ("manifest","inventory","ids","qa","checkpoint"):
            self.assertEqual(report[role]["git_blob"],self.blobs[role])
            self.assertEqual(report[role]["sha256"],self.hashes[role])
        evidence=self.docs["qa"]["evidence"]
        self.assertEqual(evidence["source_inventory_sha256"],self.hashes["inventory"])
        self.assertEqual(evidence["stable_id_map_sha256"],self.hashes["ids"])

    def test_68_topics_76_pdf_pages_one_each(self):
        inv=self.docs["inventory"]
        self.assertEqual(len(inv["topics"]),68)
        self.assertEqual([x["page"] for x in inv["page_accounting"]],list(range(1,77)))
        self.assertEqual(inv["special_cases"]["unnumbered_topic_start_pages"],[35])

    def test_real_source_number_tokens_are_not_forced_unique(self):
        t=self.docs["inventory"]["topics"]
        self.assertEqual(t[4]["source_number_token"],"06")
        self.assertEqual(t[5]["source_number_token"],"06")
        self.replay()

    def test_fake_stage4_or_stage2_pass_not_promoted(self):
        def change(d,h): d["checkpoint"]["stages"][1]["state"]="PASS"
        with self.assertRaisesRegex(ValueError,"READING_STAGE_BOUNDS_CHANGED"):
            self.replay(change)

    def test_relabel_stable_id_map_fails(self):
        def change(d,h): d["ids"]["mappings"][3]["label_text_nfc"]="INVENTED"
        with self.assertRaisesRegex(ValueError,"ACTUAL_NATIVE_ID_MAP_NOT_SAME_SOURCE_ORDER"):
            self.replay(change)

    def test_reorder_topic_ids_fails(self):
        def change(d,h): d["inventory"]["topics"][0]["stable_id"]="lesen-praes-0099"
        with self.assertRaisesRegex(ValueError,"READING_STABLE_ID_ORDER_INVALID"):
            self.replay(change)

    def test_duplicate_stable_id_fails(self):
        def change(d,h): d["inventory"]["topics"][5]["stable_id"]="lesen-praes-0001"
        with self.assertRaisesRegex(ValueError,"READING_STABLE_ID_ORDER_INVALID"):
            self.replay(change)

    def test_missing_page_number_fails(self):
        def change(d,h): d["inventory"]["page_accounting"][1]["page"]=1
        with self.assertRaisesRegex(ValueError,"MISSING_DUPLICATE_OR_OUT_OF_ORDER_PDF_PAGE"):
            self.replay(change)

    def test_forged_page_classification_fails(self):
        def change(d,h): d["inventory"]["page_accounting"][2]["classification"]="topic_start"
        with self.assertRaisesRegex(ValueError,"PAGE_CLASSIFICATION_CONSERVATION_FAILED"):
            self.replay(change)

    def test_continuation_wrong_origin_fails(self):
        def change(d,h):
            next(x for x in d["inventory"]["page_accounting"] if x["page"]==18)["continues_page"]=16
        with self.assertRaisesRegex(ValueError,"PAGE_SPECIAL_ORIGIN_DRIFT"):
            self.replay(change)

    def test_duplicate_page_69_wrong_topic_fails(self):
        def change(d,h):
            next(x for x in d["inventory"]["page_accounting"] if x["page"]==69)["topic_id"]="lesen-praes-0001"
        with self.assertRaisesRegex(ValueError,"TOPIC_SPECIAL_PAGE_MEMBERSHIP_DRIFT"):
            self.replay(change)

    def test_missing_special_blank_fails(self):
        def change(d,h):d["inventory"]["special_cases"]["blank_pages"]=[]
        with self.assertRaisesRegex(ValueError,"SPECIAL_PAGES_NOT_RECONCILED"):
            self.replay(change)

    def test_wrong_source_manifest_domain_fails(self):
        def change(d,h):d["manifest"]["domain"]="vocabulary"
        with self.assertRaisesRegex(ValueError,"READING_SOURCE_DOMAIN_OR_DELIVERY_BOUNDARY_CHANGED"):
            self.replay(change)

    def test_source_registry_identity_drift_fails(self):
        def change(d,h):
            next(x for x in d["registry"]["sources"]
                 if x["source_id"]==m.SOURCE_ID)["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"CROSS_ROLE_READING_SOURCE_ID_OR_HASH_DRIFT"):
            self.replay(change)

    def test_unsigned_qa_or_false_quality_flag_fails(self):
        def change(d,h): d["qa"]["checks"]["stable_ids_unique"]=False
        with self.assertRaisesRegex(ValueError,"SOURCE_RECORDED_QA_IS_NOT_PASS"):
            self.replay(change)

    def test_qa_stale_source_inventory_actual_sha_fails(self):
        def change(d,h): h["inventory"]="b"*64
        with self.assertRaisesRegex(ValueError,"ACTUAL_NATIVE_INVENTORY_ID_BYTES_NOT_QA_PINNED"):
            self.replay(change)

    def test_qa_stale_stable_id_actual_sha_fails(self):
        def change(d,h): h["ids"]="b"*64
        with self.assertRaisesRegex(ValueError,"ACTUAL_NATIVE_INVENTORY_ID_BYTES_NOT_QA_PINNED"):
            self.replay(change)

    def test_unicode_nfc_heading_tamper_fails(self):
        def change(d,h):d["inventory"]["topics"][1]["source_heading_nfc"]="Perso\u0308nlichkeit"
        with self.assertRaisesRegex(ValueError,"HEADING_OR_LABEL_NFC_DRIFT"):
            self.replay(change)

    def test_dropped_unnumbered_topic_fails(self):
        def change(d,h):d["inventory"]["special_cases"]["unnumbered_topic_start_pages"]=[]
        with self.assertRaisesRegex(ValueError,"UNNUMBERED_READING_PROMPT_NOT_RECONCILED"):
            self.replay(change)

    def test_bad_source_delivery_policy_fails(self):
        def change(d,h):d["manifest"]["production_policy"]["runtime_reproduction"]="copy_pdf_verbatim"
        with self.assertRaisesRegex(ValueError,"READING_SOURCE_DOMAIN_OR_DELIVERY_BOUNDARY_CHANGED"):
            self.replay(change)

    def test_fake_page_count_fails(self):
        def change(d,h):d["inventory"]["counts"]["pdf_pages"]=75
        with self.assertRaisesRegex(ValueError,"SOURCE_COUNT_OR_RECORDED_QA_SUMMARY_DRIFT"):
            self.replay(change)

    def test_duplicate_json_keys_and_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_JSON_KEY"):
            m.strict_json(b'{"a":1,"a":2}')
        with self.assertRaisesRegex(ValueError,"NONFINITE_JSON"):
            m.strict_json(b'{"a":NaN}')

    def test_source_role_is_actual_readonly_git_blob(self):
        a=m.git_index_bytes()
        self.assertEqual(self.blobs,{k:r["blob"] for k,r in a.items()})
        self.assertTrue(all(r["path"]==m.FILES[k] for k,r in a.items()))
        self.assertEqual(self.actual["any_card_source_locked_or_app_mutation"],False)

    def test_cli_write_once_to_safe_external_report(self):
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/"reading-qa.json"
            cmd=[sys.executable,"-B",str(SCRIPT),"--new-report",str(dest),"--summary"]
            a=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(a.returncode,0,a.stderr)
            self.assertEqual(json.loads(dest.read_text())["replayed_counts"]["topics"],68)
            b=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(b.returncode,2)
            self.assertIn("REPORT_NOT_EXCLUSIVE",b.stderr)

if __name__=="__main__":
    unittest.main()
