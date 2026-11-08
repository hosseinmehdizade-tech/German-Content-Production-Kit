"""Cross-project lexical release-gate regression tests; synthetic fixtures only."""
from __future__ import annotations
import csv,io,json,tempfile,sys,hashlib,unittest
from pathlib import Path
from unittest.mock import patch
import types

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Verification"))
from guard_lexical_rule_coverage_v1 import native_rows,review_signals,evaluate,pinned,blob,sha,high_taxonomy_signals,review_high_findings

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

def data(combos=None,examples=None,ids=("c1",),backend=None):
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
          "examples":json.dumps(examples,ensure_ascii=False),"custom_fields":json.dumps(backend if backend is not None else {},ensure_ascii=False)})
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
    def test_accepted_250_verben_native_string_examples_scan_without_rewriting(self):
        # Real source shape: v1.8 official direct-import TSV stores 4 German examples
        # as JSON strings rather than v336 language-tagged example objects.
        ex=["Es hängt von dir ab, was wir machen.",
            "Das Ergebnis hängt von der Vorbereitung ab.",
            "Ob wir fahren, hängt vom Wetter ab.",
            "Viele Studierende hängen finanziell von ihren Eltern ab."]
        ts=native_rows(data(combos=["von etwas abhängen — به چیزی بستگی داشتن"],examples=ex))
        out=review_signals(ts)
        self.assertEqual(out["examples"],4)
        self.assertEqual(out["combinations"],1)
        self.assertFalse(any(x["code"]=="EXACT_EXAMPLE_CLONE" for x in out["issues"]))

    def test_native_string_example_exact_clone_is_high(self):
        ex=["Es hängt von dir ab, was wir machen."]
        out=review_signals(native_rows(data(combos=[ex[0]+" — بستگی دارد"],examples=ex)))
        self.assertEqual(out["examples"],1)
        self.assertEqual(out["issues"][0]["code"],"EXACT_EXAMPLE_CLONE")
        self.assertEqual(out["issues"][0]["severity"],"HIGH")

    def test_native_string_examples_and_structured_examples_both_count(self):
        ex=["Das Ergebnis hängt von der Vorbereitung ab.",
            {"lang":"de-DE","text":"Es hängt von dir ab."},
            {"lang":"fa-IR","text":"این به تو بستگی دارد."}]
        out=review_signals(native_rows(data(combos=[],examples=ex)))
        self.assertEqual(out["examples"],2)
        self.assertEqual(out["issues"],[])

    def test_lean_advisory_scans_native_string_examples_not_zero(self):
        from audit_kombinationen_lean_v1_1 import german_examples,analyze_rows
        ex=["Es hängt von dir ab, was wir machen.",
            "Das Ergebnis hängt von der Vorbereitung ab."]
        rows=native_rows(data(combos=["hängt von dir ab — به تو بستگی دارد"],examples=ex))
        self.assertEqual(list(german_examples(rows[0])),ex)
        diag=analyze_rows(rows,"real-v18-shape.tsv","0"*64)
        self.assertEqual(diag["cards"],1)
        self.assertTrue(any(x["rule"]=="LITERAL_EXAMPLE_SUBSPAN" for x in diag["flags"]))

    def test_lean_advisory_rejects_invalid_native_example_type(self):
        from audit_kombinationen_lean_v1_1 import german_examples
        rows=native_rows(data(combos=[],examples=[123]))
        with self.assertRaisesRegex(ValueError,"UNKNOWN_EXAMPLE_FORMAT"):
            list(german_examples(rows[0]))

    def test_native_empty_string_examples_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"EMPTY_GERMAN_EXAMPLE"):
            review_signals(native_rows(data(combos=[],examples=[" "])))

    def test_native_nonstring_nonobject_examples_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_EXAMPLE_FORMAT"):
            review_signals(native_rows(data(combos=[],examples=[12])))

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

class BackendCombinationCoverageTests(unittest.TestCase):
    """Future mutable source projections must not hide structured collocations."""
    def scan(self,backend,visible=None,examples=None):
        return review_signals(native_rows(data(combos=visible if visible is not None else [],
                                               examples=examples,backend=backend)))
    def test_backend_v1_only_exact_example_clone_is_high(self):
        combo="Sie versteigern alte Möbel."
        out=self.scan({"kombinationen_v1":{"visible_section":"Kombinationen",
                  "items":[{"de":combo,"fa":"وسایل قدیمی را به مزایده می‌گذارند","en":"auction old furniture",
                            "kind":"collocation"}]}},examples=EXAMPLES)
        self.assertEqual(out["combinations"],1)
        self.assertEqual([(x["code"],x["severity"]) for x in out["issues"]],
                         [("EXACT_EXAMPLE_CLONE","HIGH")])

    def test_backend_v336_only_is_not_silently_ignored(self):
        out=self.scan({"kombinationen_v336":{"items":["Sie versteigern alte Möbel. — مزایده"]}},
                      examples=EXAMPLES)
        self.assertEqual(out["combinations"],1)
        self.assertEqual(out["issues"][0]["code"],"EXACT_EXAMPLE_CLONE")

    def test_structured_and_visible_mirrors_count_only_one_learner_item(self):
        term="etwas an den Meistbietenden versteigern"
        backend={"kombinationen_v1":{"visible_section":"Kombinationen",
                     "items":[{"de":term,"fa":"به بالاترین پیشنهاددهنده فروختن"}]},
                 "kombinationen_v336":{"items":[{"de":term,"fa":"به بالاترین پیشنهاددهنده فروختن"}]}}
        out=self.scan(backend,visible=[term+" — به بالاترین پیشنهاددهنده فروختن"],examples=EXAMPLES)
        self.assertEqual(out["combinations"],1)
        self.assertEqual(out["issues"],[])

    def test_shortened_display_source_needs_review_not_automatic_deletion(self):
        surface="über + Akkusativ abstimmen; worüber?"
        full=surface+" – darüber (Pronominaladverb)"
        out=self.scan({"kombinationen_v1":{"items":[{"de":full,"fa":"دربارهٔ چیزی رأی دادن"}]}},
                      visible=[surface+" — دربارهٔ چیزی رأی دادن"],examples=[])
        self.assertEqual(out["combinations"],2)
        self.assertEqual([(x["code"],x["severity"]) for x in out["issues"]],
                         [("BACKEND_VISIBLE_SURFACE_DIVERGENCE_REVIEW","MEDIUM")])

    def test_r16_setzen_and_sitzen_short_display_detected_as_review(self):
        short="sich auf / neben + Akkusativ setzen (wohin?)"
        full=short+" – auf / neben + Dativ sitzen (wo?)"
        out=self.scan({"kombinationen_v1":{"items":[{"de":full,"fa":"نشستن در یک مکان"}]}},
                      visible=[short+" — جایی نشستن"],examples=[])
        self.assertEqual(out["issues"][0]["code"],"BACKEND_VISIBLE_SURFACE_DIVERGENCE_REVIEW")
        self.assertEqual(out["issues"][0]["severity"],"MEDIUM")

    def test_exact_r16_abstimmen_en_dash_is_not_a_display_divergence(self):
        de="über + Akkusativ abstimmen; worüber? – darüber (Pronominaladverb)"
        tr="دربارهٔ چیزی رأی دادن؛ پرسش worüber و ضمیر اشارهٔ darüber"
        out=self.scan({"kombinationen_v1":{"items":[{"de":de,"fa":tr}]}},
                      visible=[de+" — "+tr],examples=[])
        self.assertEqual(out["combinations"],1)
        self.assertFalse(any(x["code"]=="BACKEND_VISIBLE_SURFACE_DIVERGENCE_REVIEW"
                             for x in out["issues"]))

    def test_exact_r16_setzen_en_dash_is_not_a_display_divergence(self):
        de="sich auf / neben + Akkusativ setzen (wohin?) – auf / neben + Dativ sitzen (wo?)"
        tr="نشستن به سمت یک مکان با آکوزاتیو؛ در حالت نشسته بودن مکان با داتیو"
        out=self.scan({"kombinationen_v1":{"items":[{"de":de,"fa":tr}]}},
                      visible=[de+" — "+tr],examples=[])
        self.assertEqual(out["combinations"],1)
        self.assertEqual(out["issues"],[])

    def test_lean_advisory_preserves_en_dash_before_persian_translation(self):
        from audit_kombinationen_lean_v1_1 import combos
        full="sich auf + Akkusativ setzen (wohin?) – auf + Dativ sitzen (wo?)"
        row={"details":json.dumps([{"title":"Kombinationen",
                        "items":[full+" — حرکت به مکان", "auf dem Weg – در راه"]}],ensure_ascii=False)}
        self.assertEqual(list(combos(row)),[full,"auf dem Weg"])

    def test_lean_advisory_keeps_entire_real_r16_abstimmen_grammar(self):
        from audit_kombinationen_lean_v1_1 import combos
        full="über + Akkusativ abstimmen; worüber? – darüber (Pronominaladverb)"
        row={"details":json.dumps([{"title":"Kombinationen",
                        "items":[full+" — رأی دادن"]}],ensure_ascii=False)}
        self.assertEqual(list(combos(row)),[full])

    def test_backend_distinct_from_visible_is_still_checked(self):
        out=self.scan({"kombinationen_v1":{"items":[{"de":"Sie versteigern alte Möbel.",
                                                         "fa":"وسایل قدیمی را حراج می‌کنند"}]}},
                      visible=["etwas an den Meistbietenden versteigern — حراج‌کردن"],
                      examples=EXAMPLES)
        self.assertEqual(out["combinations"],2)
        self.assertIn("BACKEND_VISIBLE_SURFACE_DIVERGENCE_REVIEW",
                      {x["code"] for x in out["issues"]})
        self.assertIn("EXACT_EXAMPLE_CLONE",
                      {x["code"] for x in out["issues"]})

    def test_backend_duplicate_within_one_source_is_high(self):
        term="etwas an den Meistbietenden versteigern"
        out=self.scan({"kombinationen_v1":{"items":[{"de":term,"fa":"فروختن"},
                                                       {"de":term,"fa":"به مزایده گذاشتن"}]}},
                      examples=EXAMPLES)
        self.assertEqual(out["combinations"],1)
        self.assertTrue(any(x["code"]=="EXACT_COMBO_DUPLICATE"
                            and x["severity"]=="HIGH" for x in out["issues"]))

    def test_backend_malformed_list_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"INVALID_BACKEND_COMBINATION_ITEMS"):
            self.scan({"kombinationen_v336":{"visible_section":"Kombinationen"}},examples=EXAMPLES)

    def test_backend_missing_german_surface_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"EMPTY_COMBO"):
            self.scan({"kombinationen_v1":{"items":[{"fa":"فقط فارسی"}]}},examples=EXAMPLES)

    def test_conflicting_camel_and_snake_custom_fields_fail_closed(self):
        raw=data(combos=[],backend={"kombinationen_v1":{"items":[{"de":"Satz A"}]}})
        reader=csv.DictReader(io.StringIO(raw.decode("utf-8")),delimiter="\t")
        rows=list(reader)
        cols=reader.fieldnames+["customFields"]
        rows[0]["customFields"]=json.dumps({"kombinationen_v1":{"items":[{"de":"Satz B"}]}})
        out=io.StringIO(newline="")
        writer=csv.DictWriter(out,fieldnames=cols,delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
        with self.assertRaisesRegex(ValueError,"CONFLICTING_CUSTOM_FIELDS_ALIASES"):
            review_signals(native_rows(out.getvalue().encode("utf-8")))

    def test_camel_custom_fields_only_supported(self):
        raw=data(combos=[],backend={})
        reader=csv.DictReader(io.StringIO(raw.decode("utf-8")),delimiter="\t")
        rows=list(reader)
        cols=reader.fieldnames+["customFields"]
        rows[0]["customFields"]=json.dumps({"kombinationen_v1":{"items":[{"de":"Sie versteigern alte Möbel."}]}})
        out=io.StringIO(newline="")
        writer=csv.DictWriter(out,fieldnames=cols,delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
        scan=review_signals(native_rows(out.getvalue().encode("utf-8")))
        self.assertEqual(scan["combinations"],1)
        self.assertTrue(any(x["code"]=="EXACT_EXAMPLE_CLONE" for x in scan["issues"]))

    def test_eszett_is_not_folded_to_ss_for_exact_backend_duplicate(self):
        out=self.scan({"kombinationen_v1":{"items":[
            {"de":"Maße nehmen","fa":"اندازه گرفتن"},
            {"de":"Masse nehmen","fa":"جرم گرفتن"}]}},examples=[])
        self.assertEqual(out["combinations"],2)
        self.assertFalse(any(x["code"]=="EXACT_COMBO_DUPLICATE" for x in out["issues"]))

    def test_eszett_vs_ss_is_not_suppressed_as_backend_display_mirror(self):
        out=self.scan({"kombinationen_v1":{"items":[{"de":"die Masse bestimmen","fa":"جرم را تعیین کردن"}]}},
                      visible=["die Maße bestimmen — اندازه‌ها را تعیین کردن"],examples=[])
        self.assertEqual(out["combinations"],2)
        self.assertEqual(out["issues"][0]["code"],"BACKEND_VISIBLE_SURFACE_DIVERGENCE_REVIEW")
        self.assertEqual(out["issues"][0]["severity"],"MEDIUM")

    def test_no_forced_combinations_when_backend_empty(self):
        out=self.scan({"kombinationen_v1":{"items":[]},"kombinationen_v336":{"items":[]}},
                      examples=EXAMPLES)
        self.assertEqual(out["combinations"],0)
        self.assertEqual(out["issues"],[])

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


class RightSideCrossSectionSafetyTests(unittest.TestCase):
    """Real taxonomy diagnostic + release-review decision contract, no card writes."""
    def taxonomy(self, details):
        from audit_related_sections_taxonomy_v1_1 import audit,load_cards
        rows=native_rows(data(combos=[],examples=[]))
        rows[0]["details"]=json.dumps(details,ensure_ascii=False)
        raw=data(combos=[],examples=[])
        # The taxonomy parser runs on the exact same projected card representation.
        return high_taxonomy_signals(audit(load_cards(
            json.dumps({"cards":rows},ensure_ascii=False).encode("utf-8"),".json"),
            sha(raw)),sha(raw))

    def evidence(self, issues, high, decisions=()):
        return {"flagged_card_ids":sorted({x["card_id"] for x in issues["issues"]+high}),
                "risk_based_independent_review":True,"high_decisions":list(decisions)}

    def test_real_related_synonym_duplicate_requires_independent_disposition(self):
        high=self.taxonomy([
            {"title":"Verwandte Wörter","items":["Möbel — مبلمان"]},
            {"title":"Synonyme","items":["Möbel — مبلمان"]}])
        self.assertEqual(len(high),1)
        self.assertEqual(high[0]["code"],"RELATED_EXACT_CROSS_SECTION_DUPLICATE")
        scan={"issues":[]}
        b=review_high_findings(scan,high,self.evidence(scan,high))
        self.assertTrue(any(x.startswith("HIGH_UNRESOLVED:") for x in b))
        decision={"id":high[0]["id"],"decision":"KEEP_WITH_SPECIFIC_TEACHING_DELTA",
                  "reason":"Distinct contextual usage independently checked in the approved Stage4 review"}
        self.assertEqual(review_high_findings(scan,high,self.evidence(scan,high,[decision])),[])

    def test_kombination_repeated_as_verwandt_cannot_pass_unreviewed(self):
        high=self.taxonomy([
            {"title":"Kombinationen","items":["alte Möbel versteigern — اثاثیه را به مزایده گذاشتن"]},
            {"title":"Verwandte Wörter","items":["alte Möbel versteigern — اثاثیه را به مزایده گذاشتن"]}])
        self.assertEqual([x["code"] for x in high],["RELATED_EXACT_CROSS_SECTION_DUPLICATE"])
        scan={"issues":[]}
        blockers=review_high_findings(scan,high,self.evidence(scan,high))
        self.assertTrue(any(x.startswith("HIGH_UNRESOLVED:") for x in blockers))

    def test_opaque_internal_id_cannot_be_excused_by_keep(self):
        high=self.taxonomy([{"title":"Verwandte Wörter","items":["ma1m-lu-0001"]}])
        self.assertEqual(high[0]["code"],"OPAQUE_TARGET_ID_IN_RELATED")
        scan={"issues":[]}
        keep={"id":high[0]["id"],"decision":"KEEP_WITH_SPECIFIC_TEACHING_DELTA",
              "reason":"Purported exception"}
        blockers=review_high_findings(scan,high,self.evidence(scan,high,[keep]))
        self.assertTrue(any(x.startswith("RELATED_STRUCTURAL_HIGH_REQUIRES_CORRECTION:") for x in blockers))

    def test_exact_example_clone_not_cured_by_claiming_source_corrected(self):
        scan=review_signals(native_rows(data(combos=["Sie versteigern alte Möbel. — ..."])))
        high=[x for x in scan["issues"] if x["severity"]=="HIGH"]
        self.assertEqual(high[0]["code"],"EXACT_EXAMPLE_CLONE")
        record={"id":high[0]["id"],"decision":"CORRECTED_IN_EXACT_SOURCE",
                "reason":"Marked corrected despite unchanged projected TSV"}
        blockers=review_high_findings(scan,[],self.evidence(scan,[],[record]))
        self.assertTrue(any(x.startswith("CORRECTION_STILL_PRESENT_IN_EXACT_SOURCE:") for x in blockers))

    def test_stale_finding_decision_cannot_be_reused_after_source_changes(self):
        scan=review_signals(native_rows(data(combos=["etwas an den Meistbietenden versteigern — ..."])))
        self.assertEqual(scan["issues"],[])
        record={"id":"1"*64,"decision":"KEEP_WITH_SPECIFIC_TEACHING_DELTA","reason":"Stale"}
        blockers=review_high_findings(scan,[],self.evidence(scan,[],[record]))
        self.assertTrue(any(x.startswith("STALE_OR_UNKNOWN_HIGH_DECISION:") for x in blockers))

    def test_duplicate_review_record_rejected(self):
        scan=review_signals(native_rows(data(combos=["Sie versteigern alte Möbel. — ..."])))
        record={"id":scan["issues"][0]["id"],"decision":"KEEP_WITH_SPECIFIC_TEACHING_DELTA",
                "reason":"Example is explicitly scoped to a separate teaching objective"}
        blockers=review_high_findings(scan,[],self.evidence(scan,[],[record,record]))
        self.assertTrue(any(x.startswith("DUPLICATE_HIGH_DECISION:") for x in blockers))

    def test_no_quota_and_clean_right_side_pass(self):
        scan={"issues":[]}
        self.assertEqual(review_high_findings(scan,[],self.evidence(scan,[])),[])

if __name__=="__main__":unittest.main()
