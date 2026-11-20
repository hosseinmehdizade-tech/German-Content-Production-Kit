#!/usr/bin/env python3
"""Synthetic-only QA: no user or copyrighted data needed in CI."""
import unittest,json
from validate_typing_core_alias_coverage import validate
def mk(core='anschreiben',aliases=None):
    c={'typingCore':core}
    if aliases is not None:
        c['acceptedAnswersFull']=aliases;c['acceptedAnswersStandard']=aliases
    return {'id':'synthetic','custom_fields':json.dumps(c,ensure_ascii=False)}
class GuardTest(unittest.TestCase):
    def test_without_override(self):self.assertEqual(validate([mk()])['status'],'PASS')
    def test_core_accepted(self):self.assertEqual(validate([mk(aliases=['anschreiben'])])['status'],'PASS')
    def test_variants_preserved(self):self.assertEqual(validate([mk(aliases=['anschreiben','schreibt an'])])['status'],'PASS')
    def test_core_missing_from_both(self):self.assertEqual(validate([mk(aliases=['schreibt an'])])['error_count'],2)
    def test_core_metadata_missing(self):self.assertEqual(validate([mk('', ['anschreiben'])])['errors'][0]['code'],'TYPING_CORE_MISSING')
    def test_invalid_override_shape(self):self.assertEqual(validate([mk(aliases='anschreiben')])['status'],'FAIL')
    def test_blank_alias(self):self.assertEqual(validate([mk(aliases=['anschreiben',''])])['status'],'FAIL')
    def test_corrupt_json(self):self.assertEqual(validate([{'id':'bad','custom_fields':'{wrong'}])['status'],'FAIL')
    def test_one_mode_missing(self):
        r=mk(aliases=['anschreiben']);c=json.loads(r['custom_fields']);c['acceptedAnswersFull']=['schreibt an'];r['custom_fields']=json.dumps(c)
        self.assertEqual(validate([r])['error_count'],1)
    def test_counting(self):
        r=validate([mk(),mk(aliases=['anschreiben']),mk(aliases=['schreibt an'])])
        self.assertEqual((r['cards'],r['override_cards'],r['covered_override_cards'],r['error_count']),(3,2,1,2))
if __name__=='__main__':unittest.main()
