"""Source-neutral synthetic negative controls. No real card or locked source writes."""
import copy
import csv
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'audit_related_sections_taxonomy_v1_1.py'
spec = importlib.util.spec_from_file_location('related_v1_1', MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def section(title, *items):
    return {'title': title, 'items': list(items)}


def card(cid='demo-1', front='die Beschreibung', details=None, **kwargs):
    return {'id': cid, 'front': front, 'details': details if details is not None else [],
            'examples': [], **kwargs}


def scan(cards):
    return m.audit(m.load_cards(json.dumps({'cards': cards}).encode('utf-8'), '.json'), '0' * 64)


class TaxonomyContractTests(unittest.TestCase):
    def codes(self, *cards):
        return [x['code'] for x in scan(list(cards))['findings']]

    def test_role_aliases(self):
        self.assertEqual(m.ROLE_ALIASES['Verwandt'], 'RELATED')
        self.assertEqual(m.ROLE_ALIASES['Verwandte Wörter'], 'RELATED')

    def test_no_quota_for_empty_related(self):
        self.assertEqual(self.codes(card()), [])

    def test_genuine_related_without_target_stays_no_force(self):
        self.assertEqual(self.codes(card(details=[section('Verwandte Wörter', 'der Unterricht')])), [])

    def test_description_duplicate_with_combination(self):
        c = card(details=[section('Verwandte Wörter', 'allgemeine Beschreibung'),
                          section('Kombinationen', 'allgemeine Beschreibung')])
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(c))

    def test_backend_combinations_v1(self):
        c = card(details=[section('Verwandt', 'eine Beschreibung verfassen')],
                 custom_fields={'kombinationen_v1': {'items': [{'de': 'eine Beschreibung verfassen', 'fa': '...', 'en': '...'}]}})
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(c))

    def test_backend_combinations_v336(self):
        c = card(details=[section('Verwandt', 'eine Beschreibung verfassen')],
                 custom_fields={'kombinationen_v336': {'items': [{'de': 'eine Beschreibung verfassen'}]}})
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(c))

    def test_full_sentence_in_examples_exact_but_not_reclassified(self):
        c = card(details=[section('Verwandte Wörter', 'Bitte senden Sie uns eine Beschreibung.')],
                 examples=[{'text_de': 'Bitte senden Sie uns eine Beschreibung.', 'text_fa': '...', 'text_en': '...'}])
        got = self.codes(c)
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', got)
        self.assertIn('SENTENCE_OR_REDEMITTEL_ROLE_REVIEW', got)

    def test_separate_redemittel_target_not_auto_example(self):
        a = card(details=[section('Verwandte Wörter', 'Bitte senden Sie uns eine Beschreibung.')],
                 canonical_relations=[{'target_id': 'demo-2', 'relation_type': 'RELATED'}])
        b = card('demo-2', 'Bitte senden Sie uns eine Beschreibung.')
        self.assertNotIn('PRETYPED_TARGET_IN_RELATED', self.codes(a, b))
        self.assertIn('SENTENCE_OR_REDEMITTEL_ROLE_REVIEW', self.codes(a, b))

    def test_actual_typed_family_candidate(self):
        a = card('demo-1', 'beschreiben', [section('Verwandt', 'die Beschreibung')],
                 canonical_relations=[{'target_id': 'demo-2', 'relation_type': 'WORD_FAMILY'}])
        b = card('demo-2', 'die Beschreibung')
        self.assertIn('PRETYPED_TARGET_IN_RELATED', self.codes(a, b))

    def test_pretyped_synonym_candidate(self):
        a = card('demo-1', 'der Nachtisch', [section('Verwandt', 'die Nachspeise')],
                 canonical_relations=[{'target_id': 'demo-2', 'relation_type': 'SYNONYM'}])
        self.assertIn('PRETYPED_TARGET_IN_RELATED', self.codes(a, card('demo-2', 'die Nachspeise')))

    def test_pretyped_antonym_candidate(self):
        a = card('demo-1', 'groß', [section('Verwandt', 'klein')],
                 canonical_relations=[{'target_id': 'demo-2', 'relation_type': 'ANTONYM'}])
        self.assertIn('PRETYPED_TARGET_IN_RELATED', self.codes(a, card('demo-2', 'klein')))

    def test_typed_target_does_not_assert_semantic_truth(self):
        report = scan([card('demo-1', 'gut', [section('Verwandt', 'schlecht')],
                            canonical_relations=[{'target_id': 'demo-2', 'relation_type': 'WORD_FAMILY'}]),
                       card('demo-2', 'schlecht')])
        self.assertFalse(report['stage4_linguistic_approval'])

    def test_mismatched_surface_not_promoted(self):
        a = card('demo-1', 'gut', [section('Verwandt', 'ziemlich schlecht')],
                 canonical_relations=[{'target_id': 'demo-2', 'relation_type': 'ANTONYM'}])
        self.assertNotIn('PRETYPED_TARGET_IN_RELATED', self.codes(a, card('demo-2', 'schlecht')))

    def test_unresolved_target_id_never_promoted(self):
        a = card(details=[section('Verwandt', 'klein')],
                 canonical_relations=[{'target_id': 'missing-target', 'relation_type': 'ANTONYM'}])
        self.assertNotIn('PRETYPED_TARGET_IN_RELATED', self.codes(a))

    def test_conflicting_relationships_go_high_hold(self):
        rels = [{'target_id': 'demo-2', 'relation_type': 'SYNONYM'},
                {'target_id': 'demo-2', 'relation_type': 'WORD_FAMILY'}]
        a = card('demo-1', 'Freizeit', [section('Verwandt', 'freie Zeit')], canonical_relations=rels)
        got = self.codes(a, card('demo-2', 'freie Zeit'))
        self.assertIn('CONFLICTING_TYPED_TARGET', got)
        self.assertNotIn('PRETYPED_TARGET_IN_RELATED', got)

    def test_related_and_synonym_conflict(self):
        a = card('demo-1', 'Gruß', [section('Verwandt', 'Begrüßung')],
                 canonical_relations=[{'target_id':'demo-2','type':'RELATED'},
                                      {'target_id':'demo-2','type':'SYNONYM'}])
        self.assertIn('CONFLICTING_TYPED_TARGET', self.codes(a, card('demo-2', 'Begrüßung')))

    def test_same_surface_in_synonyms(self):
        a = card(details=[section('Verwandt', 'Nachspeise'), section('Synonyme', 'Nachspeise')])
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_same_surface_in_word_family(self):
        a = card(details=[section('Verwandte Wörter', 'beschreiben'), section('Wortfamilie', 'beschreiben')])
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_same_surface_in_antonyms(self):
        a = card(details=[section('Verwandt', 'klein'), section('Antonyme', 'klein')])
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_duplicate_within_legacy_and_new_related(self):
        a = card(details=[section('Verwandt', 'der Beruf'), section('Verwandte Wörter', 'der Beruf')])
        self.assertIn('DUPLICATE_WITHIN_RELATED', self.codes(a))

    def test_no_duplicate_when_only_semantic_overlap(self):
        a = card(details=[section('Verwandt', 'die Beschreibung'),
                          section('Kombinationen', 'eine Beschreibung verfassen')])
        self.assertNotIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_no_confusion_rektion_with_combination(self):
        a = card(details=[section('Verwandt', 'an der Arbeit'),
                          section('Rektion', 'arbeiten an + Dativ')])
        self.assertNotIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_german_eszet_casefold_not_safe(self):
        a = card(details=[section('Verwandt', 'Maße'), section('Kombinationen', 'Masse')])
        self.assertNotIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_case_difference_not_auto_delete(self):
        a = card(details=[section('Verwandt', 'Weg'), section('Kombinationen', 'weg')])
        self.assertNotIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_punctuation_difference_not_auto_delete(self):
        a = card(details=[section('Verwandt', 'Na ja!'), section('Synonyme', 'Na ja')])
        self.assertNotIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_nfc_and_space_exact(self):
        a = card(details=[section('Verwandt', '  eine  Beschreibung\t verfassen  '),
                          section('Kombinationen', 'eine Beschreibung verfassen')])
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_opaque_real_source_id(self):
        a = card(details=[section('Verwandte Wörter', 'ma1m-lu-0898')])
        self.assertIn('OPAQUE_TARGET_ID_IN_RELATED', self.codes(a))

    def test_opaque_dynamic_target_id(self):
        a = card('card.001', details=[section('Verwandt', 'card.002')])
        self.assertIn('OPAQUE_TARGET_ID_IN_RELATED', self.codes(a, card('card.002', 'gut')))

    def test_self_reference(self):
        a = card('demo-1', details=[section('Verwandt', 'demo-1')])
        self.assertIn('OPAQUE_TARGET_ID_IN_RELATED', self.codes(a))

    def test_invisible_format_control(self):
        a = card(details=[section('Verwandt', 'die\u200b Beschreibung')])
        self.assertIn('INVISIBLE_FORMAT_CONTROL', self.codes(a))

    def test_short_greeting_not_sentence_gate(self):
        a = card(details=[section('Verwandt', 'Guten Morgen!')])
        self.assertNotIn('SENTENCE_OR_REDEMITTEL_ROLE_REVIEW', self.codes(a))

    def test_long_sentence_goes_to_review_not_examples(self):
        a = card(details=[section('Verwandt', 'Ich komme heute leider etwas später.')])
        self.assertIn('SENTENCE_OR_REDEMITTEL_ROLE_REVIEW', self.codes(a))

    def test_non_german_examples_do_not_false_match(self):
        a = card(details=[section('Verwandt', 'Hallo')], examples=[{'lang':'fa','text':'Hallo'}])
        self.assertNotIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_structured_trilingual_detail_preserves_de(self):
        a = card(details=[section('Verwandt', {'de':'Nachspeise','fa':'دسر','en':'dessert'}),
                          section('Synonyme', 'Nachspeise')])
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', self.codes(a))

    def test_does_not_mutate_input(self):
        cards = [card(details=[section('Verwandt', 'Hallo'), section('Synonyme', 'Hallo')])]
        old = copy.deepcopy(cards)
        scan(cards)
        self.assertEqual(cards, old)

    def test_input_hash_and_flags(self):
        raw = json.dumps({'cards': [card(details=[section('Verwandt', 'Wetter')])]}).encode()
        report = m.audit(m.load_cards(raw, '.json'), hashlib.sha256(raw).hexdigest())
        self.assertEqual(report['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertFalse(report['stage4_linguistic_approval'])
        self.assertEqual(report['automatic_card_mutations'], 0)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            m.load_cards(b'{"id":"x","id":"y"}', '.json')

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            m.load_cards(json.dumps({'cards':[card(),card()]}).encode(), '.json')

    def test_invalid_details_rejected(self):
        with self.assertRaises(ValueError):
            m.load_cards(json.dumps(card(details='not-json-array')).encode(), '.json')

    def test_invalid_custom_fields_rejected(self):
        with self.assertRaises(ValueError):
            m.load_cards(json.dumps(card(custom_fields='{{invalid')).encode(), '.json')

    def test_bad_language_item_rejected(self):
        with self.assertRaises(ValueError):
            scan([card(details=[section('Verwandt', {'fa':'سلام'})])])

    def test_tsv_compatibility(self):
        data = io.StringIO()
        w = csv.DictWriter(data, ['id','front','details','examples','custom_fields'], delimiter='\t')
        w.writeheader()
        w.writerow({'id':'x','front':'Beschreiben','details':json.dumps([section('Verwandt','ein Beispiel')]),
                    'examples':json.dumps([{'text_de':'ein Beispiel'}]),'custom_fields':json.dumps({})})
        report = m.audit(m.load_cards(data.getvalue().encode('utf-8'), '.tsv'), '1'*64)
        self.assertEqual(report['cards_scanned'], 1)
        self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', [x['code'] for x in report['findings']])

    def test_tsv_column_mismatch_rejected(self):
        raw = b'id\tfront\tdetails\texamples\na\tx\t[]\t[]\textra\n'
        with self.assertRaises(ValueError):
            m.load_cards(raw, '.tsv')

    def test_cli_report_and_default_advisory_exit(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d)/'input.json'; dst = Path(d)/'report.json'
            src.write_text(json.dumps({'cards':[card(details=[section('Verwandt','Hallo'),section('Synonyme','Hallo')])]}),encoding='utf8')
            result = subprocess.run([sys.executable,str(MODULE),str(src),'--output',str(dst)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(dst.read_text())['status'],'ADVISORY_READ_ONLY_NOT_STAGE4_ACCEPTANCE')
            strict = subprocess.run([sys.executable,str(MODULE),str(src),'--fail-on-high'],capture_output=True,text=True)
            self.assertEqual(strict.returncode,1)

    def test_cli_invalid_exit_2(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'bad.json';p.write_text('{}')
            r = subprocess.run([sys.executable,str(MODULE),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,2)

    def test_multi_corpus_schema_neutral(self):
        for prefix in ('menschen-a1', 'menschen-a2', 'menschen-b1', 'verben', 'nvv', 'vocabulary'):
            c = card(prefix+'-1', prefix, [section('Verwandte Wörter','verwandtes Stichwort')])
            self.assertEqual(self.codes(c),[])


if __name__ == '__main__':
    unittest.main()
