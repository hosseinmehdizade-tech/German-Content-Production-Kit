"""Cross-project lexical release-gate regression tests; synthetic fixtures only."""
from __future__ import annotations
import csv,io,json,tempfile,sys,hashlib,unittest
from pathlib import Path
from unittest.mock import patch
import types

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Verification"))
from guard_lexical_rule_coverage_v1 import native_rows,review_signals,evaluate,pinned,blob,sha

EXAMPLES=[
 {"lang":"de-DE","text":"Das Haus wird morgen versteigert."},
 {"lang":"de-DE","text":"Sie versteigern alte Möbel."},
 {"lang":"de-DE","text":"Das Bild wurde öffentlich versteigert."},
 {"lang":"de-DE","text":"Wir möchten die Sammlung versteigern."}]
COMBOS=[
 "ein Haus versteigern — یک خانه را به مزایده گذاشتن",
 "alte Möbel versteigern — اثاثیه قدیمی را به مزایده گذاشتن",
 "ein Bild versteigern — تابلویی را به مزایده گذاشتن",
 "eine Sammlung versteigern — مجموعه‌ای را به مزایده گذاشتن",
 "etwas öffentlich versteigern — مزایده عمومی کردن",
 "etwas an den Meistbietenden versteigern — به بالاترین پیشنهاددهنده فروختن"]

def data(combos=None,examples=None,ids=("c1",)):
    if combos is None:combos=COMBOS
    if examples is None:examples=EXAMPLES
    out=io.StringIO(newline="")
    columns=["id","front","back","card_type","category","details","examples","custom_fields","source"]
    w=csv.DictWriter(out,fieldnames=columns,delimiter="\t",lineterminator="\n")
    w.writeheader()
    for cid in ids:
        w.writerow({"id":cid,"front":"versteigern","back":"حراج کردن",
          "card_type":"de-vocabulary","category":"Verb","source":"synthetic",
          "details":json.dumps([{"title":"Kombinationen","items":combos}],ensure_ascii=False),
          "examples":json.dumps(examples,ensure_ascii=False),"custom_fields":"{}"})
    return out.getvalue().encode("utf-8")

class SemanticSignalTests(unittest.TestCase):
    def test_screenshot_five_from_six(self):
        r=review_signals(native_rows(data()))
        flagged={x["combination"] for x in r["issues"]}
        self.assertEqual(len(flagged),5)
        self.assertNotIn("etwas an den Meistbietenden versteigern",str(flagged))
        self.assertEqual(r["examples"],4)
        self.assertEqual(r["combinations"],6)
    def test_exact_clone_is_high(self):
        r=review_signals(native_rows(data(combos=["Sie versteigern alte Möbel. — الف"])))
        self.assertEqual(r["issues"][0]["severity"],"HIGH")
        self.assertEqual(r["issues"][0]["code"],"EXACT_EXAMPLE_CLONE")
    def test_duplicate_combinations_high(self):
        r=review_signals(native_rows(data(combos=["ein Haus versteigern — الف","ein Haus versteigern — ب"])))
        self.assertTrue(any(x["code"]=="EXACT_COMBO_DUPLICATE" for x in r["issues"]))
    def test_no_quota_zero_combinations(self):
        self.assertEqual(review_signals(native_rows(data(combos=[],examples=[])))["issues"],[])
    def test_malformed_details_fail_closed(self):
        rows=native_rows(data())
        rows[0]["details"]='"not sections"'
        with self.assertRaises(ValueError):review_signals(rows)
    def test_duplicate_card_ids_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_CARD_IDS"):
            native_rows(data(ids=("c1","c1")))
    def test_schema_missing_examples_rejected(self):
        with self.assertRaises(ValueError):native_rows(b"id\tfront\tdetails\nc1\tx\t[]\n")
    def test_flagged_identity_stable(self):
        a=review_signals(native_rows(data()))
        b=review_signals(native_rows(data()))
        self.assertEqual(a,b)
    def test_active_registry_all_pins(self):
        p=pinned(ROOT)
        self.assertGreaterEqual(p["bindings_checked"],8)
    def test_registry_pin_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"Prompt").mkdir()
            original=json.loads((ROOT/"Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json").read_text())
            (root/"Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json").write_text(json.dumps(original))
            with self.assertRaisesRegex(ValueError,"MISSING_POLICY_FILE"):
                pinned(root)

class ReleaseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.directory=Path(self.tmp.name)
        self.input=self.directory/"current.tsv";self.input.write_bytes(data())
    def test_missing_evidence_blocks(self):
        r=evaluate(self.input,root=ROOT,policy_checks=False)
        self.assertEqual(r["status"],"BLOCKED")
        self.assertIn("INDEPENDENT_STAGE4_EVIDENCE_MISSING",r["blockers"])
        self.assertIn("SAME_CARD_CROSS_TILE_REVIEW_MISSING",r["blockers"])
    def test_input_unchanged_by_gate(self):
        before=self.input.read_bytes()
        evaluate(self.input,root=ROOT,policy_checks=False)
        self.assertEqual(self.input.read_bytes(),before)
    def fake_review(self,source_sha=None,with_ids=True):
        stage4=self.directory/"stage4.json";stage4.write_text("{}")
        items=review_signals(native_rows(self.input.read_bytes()))["issues"]
        review=self.directory/"review.json"
        review.write_text(json.dumps({"schema":"gcpk-lexical-cross-tile-acceptance@1.0.0",
            "source_tsv_sha256":source_sha or sha(self.input.read_bytes()),
            "workstream":"SYNTHETIC_ONLY",
            "curated_current_parent_sha256":"1"*64,
            "stage4_receipt_sha256":sha(stage4.read_bytes()),
            "flagged_card_ids":sorted({v["card_id"] for v in items}) if with_ids else [],
            "risk_based_independent_review":True,"high_decisions":[]}))
        return stage4,review
    def test_false_source_hash_rejected(self):
        stage,review=self.fake_review(source_sha="0"*64)
        fake=types.SimpleNamespace(accept_existing_stage4=lambda *a:{"status":"PASS_SYNTHETIC_MOCK","blockers":[]})
        with patch.dict(sys.modules,{"audit_kombinationen_lean_v1_1":fake}):
            r=evaluate(self.input,stage,review,root=ROOT,policy_checks=False)
        self.assertIn("CROSS_TILE_REVIEW_SOURCE_MISMATCH",r["blockers"])
    def test_missing_review_scope_rejected(self):
        stage,review=self.fake_review(with_ids=False)
        fake=types.SimpleNamespace(accept_existing_stage4=lambda *a:{"status":"PASS_SYNTHETIC_MOCK","blockers":[]})
        with patch.dict(sys.modules,{"audit_kombinationen_lean_v1_1":fake}):
            r=evaluate(self.input,stage,review,root=ROOT,policy_checks=False)
        self.assertIn("CROSS_TILE_SCOPE_MISSING_CARDS",r["blockers"])
    def test_exact_high_needs_individual_reason(self):
        self.input.write_bytes(data(combos=["Sie versteigern alte Möbel. — ..."]))
        stage,review=self.fake_review()
        fake=types.SimpleNamespace(accept_existing_stage4=lambda *a:{"status":"PASS_SYNTHETIC_MOCK","blockers":[]})
        with patch.dict(sys.modules,{"audit_kombinationen_lean_v1_1":fake}):
            r=evaluate(self.input,stage,review,root=ROOT,policy_checks=False)
        self.assertTrue(any(x.startswith("HIGH_UNRESOLVED:") for x in r["blockers"]))
    def test_valid_synthetic_evidence_mock_does_not_prove_real_stage4(self):
        stage,review=self.fake_review()
        fake=types.SimpleNamespace(accept_existing_stage4=lambda *a:{"status":"PASS_SYNTHETIC_MOCK","blockers":[]})
        with patch.dict(sys.modules,{"audit_kombinationen_lean_v1_1":fake}):
            r=evaluate(self.input,stage,review,root=ROOT,policy_checks=False)
        self.assertEqual(r["status"],"PASS_FOR_GOVERNED_STAGE5_CANDIDATE_ONLY")
        self.assertIn("NATIVE_APP_STAGE6",r["does_not_prove"])
    def test_actual_candidate_builder_refuses_without_policy_evidence(self):
        import subprocess
        src=self.directory/"four-roles";src.mkdir()
        (src/"TEST-IMPORT.tsv").write_bytes(self.input.read_bytes())
        (src/"TEST-CANONICAL.json").write_text('{"cards":[]}\n')
        (src/"TEST-SOURCE-OUTPUT-MAP.tsv").write_text("id\tsource\n")
        (src/"TEST-VERIFICATION.json").write_text('{"status":"synthetic"}\n')
        out=self.directory/"candidate.zip"
        receipt=self.directory/"governed.json"
        policy=self.directory/"policy.json"
        cmd=[sys.executable,str(ROOT/"Tools/build_quality_gated_lexical_candidate_v1.py"),
             str(src),str(out),"--receipt",str(receipt),"--policy-report",str(policy),
             "--stage4-receipt",str(self.directory/"MISSING-stage4.json"),
             "--cross-tile-review",str(self.directory/"MISSING-review.json")]
        run=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8")
        self.assertEqual(run.returncode,2,run.stderr)
        self.assertFalse(out.exists())
        self.assertFalse(receipt.exists())
        self.assertFalse(policy.exists())

    def test_stage4_failure_not_overridden_by_review(self):
        stage,review=self.fake_review()
        fake=types.SimpleNamespace(accept_existing_stage4=lambda *a:{"status":"BLOCKED","blockers":["HOLD"]})
        with patch.dict(sys.modules,{"audit_kombinationen_lean_v1_1":fake}):
            r=evaluate(self.input,stage,review,root=ROOT,policy_checks=False)
        self.assertIn("EXACT_SOURCE_OFFICIAL_STAGE4_FAILED",r["blockers"])

if __name__=="__main__":unittest.main()
