#!/usr/bin/env python3
"""Independent synthetic cases for the global relation quality gate."""
import importlib.util, json, pathlib, tempfile, unittest

SRC=pathlib.Path(__file__).resolve().parents[1]/'audit_lexical_relation_fields_v1.py'
spec=importlib.util.spec_from_file_location('lexrel',SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LexicalRelationAuditTest(unittest.TestCase):
    def check(self,cards):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'source.json'
            p.write_text(json.dumps({'cards':cards},ensure_ascii=False),encoding='utf-8')
            original=p.read_bytes()
            result=m.audit(p)
            self.assertEqual(p.read_bytes(),original,'audit must never mutate source')
            return result
    def test_simple_legacy(self):
        r=self.check([{'id':'x','details':[{'title':'Synonyme','items':['existieren — وجود داشتن']}]}])
        self.assertEqual(r['status'],'PASS_STRUCTURAL')
        self.assertEqual(r['relation_entries'],1)
        self.assertEqual(r['issue_counts']['ADVISORY'],0)
    def test_context_note_advisory_not_deleted(self):
        r=self.check([{'id':'x','details':[{'title':'Synonyme','items':['fortbestehen (nur bei Regelungen; nicht Prüfung bestehen) — ادامه داشتن']}]}])
        self.assertEqual(r['status'],'PASS_STRUCTURAL')
        self.assertIn('LEGACY_INLINE_GERMAN_SENSE_NOTE',r['issue_codes'])
    def test_mixed_script_warning(self):
        r=self.check([{'id':'x','details':[{'title':'Antonyme','items':['schweigen سکوت کردن']}]}])
        self.assertIn('BILINGUAL_NO_EXPLICIT_SPLIT',r['issue_codes'])
    def test_opaque_lexical_id_warning(self):
        r=self.check([{'id':'x','details':[{'title':'Verwandte Wörter','items':['ma1m-lu-1222']}]}])
        self.assertIn('OPAQUE_RELATION_ID_VISIBLE',r['issue_codes'])
    def test_typed_record_pass(self):
        entry={'kind':'synonyms','term_de':'existieren','translation_fa':'وجود داشتن','display_item':'existieren — وجود داشتن','review_status':'KEEP_WITH_REASON'}
        r=self.check([{'id':'x','details':[{'title':'Synonyme','items':['existieren — وجود داشتن']}],'customFields':{'lexical_relations_v1':{'synonyms':[entry]}}}])
        self.assertEqual(r['status'],'PASS_STRUCTURAL')
    def test_typed_missing_fields_blocked(self):
        r=self.check([{'id':'x','customFields':{'lexical_relations_v1':{'synonyms':[{'term_de':'existieren'}]}}}])
        self.assertEqual(r['status'],'BLOCKED_STRUCTURAL')
    def test_typed_projection_mismatch_blocked(self):
        entry={'kind':'synonyms','term_de':'existieren','translation_fa':'وجود داشتن','display_item':'existieren — وجود داشتن','review_status':'KEEP_WITH_REASON'}
        r=self.check([{'id':'x','details':[{'title':'Synonyme','items':['anderes — چیز دیگری']}],'customFields':{'lexical_relations_v1':{'synonyms':[entry]}}}])
        self.assertEqual(r['status'],'BLOCKED_STRUCTURAL')
    def test_html_blocked(self):
        entry={'kind':'synonyms','term_de':'<img>','translation_fa':'وجود داشتن','display_item':'<img> — وجود داشتن','review_status':'KEEP_WITH_REASON'}
        r=self.check([{'id':'x','details':[{'title':'Synonyme','items':['<img> — وجود داشتن']}],'customFields':{'lexical_relations_v1':{'synonyms':[entry]}}}])
        self.assertIn('RAW_HTML_IN_LEXICAL_ITEM',r['issue_codes'])
if __name__=='__main__':unittest.main()
