#!/usr/bin/env python3
"""Standalone, synthetic-only tests; the 1918-card source corpus stays out of Git."""
import copy
import json
import unittest
from validate_learner_visible_lexical_front_v1_1_0 import validate

def row(front, core=None, head=None, vm=None):
    u = {'type': 'noun', 'core': core or {}}
    if head is not None:
        u['headword'] = head
    cf = {'canonical_unit': u}
    if vm is not None:
        cf['vnext_morphology'] = vm
    return {'id': 'synthetic-legacy', 'category': 'Noun', 'front': front,
            'custom_fields': json.dumps(cf, ensure_ascii=False)}

def codes(r):
    return [e['error'] for e in validate([r])['errors']]

class LegacyNounFrontTest(unittest.TestCase):
    def test_legacy_complete_headword(self):
        r = row('der Wald, Wälder', {'article': 'der', 'plural': 'Wälder'},
                'der Wald, Wälder')
        original = copy.deepcopy(r)
        self.assertEqual(codes(r), [])
        self.assertEqual(r, original)

    def test_missing_alias_but_exact_morphology(self):
        r = row('das Konzert, Konzerte', vm={'article': 'das', 'plural': 'Konzerte'})
        self.assertEqual(codes(r), [])

    def test_spaces_in_legacy_plural(self):
        r = row('der Grund, Gründe (bei der Bedeutung „reason“)',
                vm={'article': 'der',
                    'plural': 'Gründe (bei der Bedeutung „reason“) '})
        self.assertEqual(codes(r), [])

    def test_normal_noun_unaffected(self):
        self.assertEqual(codes(row('die Birne, Birnen',
                                   {'article': 'die', 'plural': 'Birnen'},
                                   'Birne')), [])

    def test_noun_without_plural_stays_fail(self):
        self.assertIn('NOUN_PLURAL_METADATA_MISSING',
                      codes(row('das Gemüse', {'article': 'das'}, 'das Gemüse')))

    def test_wrong_plural_stays_fail(self):
        self.assertIn('NOUN_FRONT_NOT_CANONICAL_DISPLAY',
                      codes(row('der Wald, WRONG', {'article': 'der',
                                                   'plural': 'Wälder'},
                                'der Wald, Wälder')))

    def test_wrong_article_stays_fail(self):
        self.assertIn('NOUN_FRONT_NOT_CANONICAL_DISPLAY',
                      codes(row('das Wald, Wälder', {'article': 'der',
                                                    'plural': 'Wälder'},
                                'der Wald, Wälder')))

    def test_conflicting_metadata_stays_fail(self):
        self.assertIn('NOUN_FRONT_NOT_CANONICAL_DISPLAY',
                      codes(row('die Menge, Mengen',
                                {'article': 'der', 'plural': 'Mengen'},
                                'die Menge, Mengen')))

    def test_unverified_complex_shapes_not_normalized(self):
        r = row('der Wald, Wälder', {'article': 'der', 'plural': 'Wälder',
                                    'singular_forms': ['die Wald']},
                'der Wald, Wälder')
        self.assertIn('NOUN_FRONT_NOT_CANONICAL_DISPLAY', codes(r))

    def test_wrong_alias_rejected(self):
        r = row('die Ausstellung, Ausstellungen',
                vm={'article': 'die', 'plural': 'WRONG'})
        self.assertIn('NOUN_ARTICLE_METADATA_MISSING', codes(r))

if __name__ == '__main__':
    unittest.main()
