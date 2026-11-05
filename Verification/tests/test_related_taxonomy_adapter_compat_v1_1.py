"""Cross-adapter synthetic contract tests; no registered source or card writes."""
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

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'Verification' / 'related_taxonomy_adapter_bridge_v1_1.py'
spec = importlib.util.spec_from_file_location('related_adapter_v11', SRC)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def canonical_json(doc):
    return json.dumps(doc, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def related(title='Verwandte Wörter', surface='die Beschreibung'):
    return {'title': title, 'items': [surface]}


def tsv_card(profile, *, details=None, custom=None):
    card = {'id': 'case-' + profile, 'front': 'die Beschreibung', 'back': 'توضیح',
            'card_type': 'de-vocabulary', 'category': profile,
            'details': json.dumps(details if details is not None else [related()], ensure_ascii=False),
            'examples': json.dumps([{'text_de': 'Das ist eine Beschreibung.', 'text_fa': 'توضیحی است.'}], ensure_ascii=False),
            'custom_fields': json.dumps(custom if custom is not None else {}, ensure_ascii=False)}
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=card.keys(), delimiter='\t', lineterminator='\n')
    writer.writeheader(); writer.writerow(card)
    return output.getvalue().encode('utf-8')


class AdapterCoverageTests(unittest.TestCase):
    def test_all_six_projected_lexical_workstreams_share_universal_envelope(self):
        for profile in ('Menschen-A1', 'Menschen-A2', 'Menschen-B1',
                        'Verben-mit-Praeposition', 'NVV', 'Vocabulary'):
            with self.subTest(profile=profile):
                raw = tsv_card(profile, details=[related('Verwandt'),
                                               {'title': 'Kombinationen', 'items': ['die Beschreibung']}])
                a, cards, meta = adapter.load_for_audit(raw, 'universal-tsv')
                report = a.audit(cards, hashlib.sha256(raw).hexdigest())
                self.assertEqual(report['related_items_scanned'], 1)
                self.assertIn('RELATED_EXACT_CROSS_SECTION_DUPLICATE', report['counts'])
                self.assertEqual(report['automatic_card_mutations'], 0)
                self.assertFalse(meta['wordnetz_graph_semantics_audited'])

    def test_structured_de_fa_en_pass_through(self):
        data = {'cards': [{'id': 'structured-1', 'front': 'die Beschreibung',
                          'details': [{'title': 'Verwandte Wörter', 'items': [
                              {'de': 'die Erklärung', 'fa': 'توضیح', 'en': 'explanation'}]}],
                          'examples': [], 'custom_fields': {}}]}
        raw = canonical_json(data)
        a, cards, _ = adapter.load_for_audit(raw, 'normalized-json')
        self.assertEqual(a.audit(cards, hashlib.sha256(raw).hexdigest())['related_items_scanned'], 1)

    def test_projected_v411_uses_only_actual_visible_details(self):
        doc = [{'id': 'sense-1', 'cardType': 'de-vocabulary', 'front': 'die Beschreibung',
                'details': [], 'examples': ['Ich habe eine Beschreibung.'],
                'customFields': {'vnext_relations': [{'type': 'RELATED', 'items': [
                    {'label': 'die Erklärung', 'target_id': 'sense-2'}]}]}}]
        before = copy.deepcopy(doc)
        raw = canonical_json(doc)
        a, cards, meta = adapter.load_for_audit(raw, 'v411-projected')
        self.assertEqual(a.audit(cards, hashlib.sha256(raw).hexdigest())['related_items_scanned'], 0)
        self.assertEqual(meta['wordnetz_related_graph_cards_outside_scope'], 1)
        self.assertFalse(meta['wordnetz_graph_semantics_audited'])
        self.assertEqual(doc, before)

    def test_projected_v411_learner_visible_related_is_audited(self):
        doc = [{'id': 'sense-1', 'cardType': 'de-vocabulary', 'front': 'die Beschreibung',
                'details': [related()], 'examples': [], 'customFields': {'vnext_relations': []}}]
        a, cards, _ = adapter.load_for_audit(canonical_json(doc), 'v411-projected')
        self.assertEqual(a.audit(cards, '0'*64)['related_items_scanned'], 1)

    def test_original_auditor_must_reject_raw_v411_projected_array(self):
        raw = canonical_json([{'id': 'c1', 'cardType': 'de-vocabulary', 'front': 'foo',
                               'details': [], 'examples': [], 'customFields': {}}])
        with self.assertRaises(ValueError):
            adapter.load_for_audit(raw, 'normalized-json')

    def test_canonical_schema_requires_original_projector(self):
        src = ROOT / 'Tools' / 'project_v411_vocabulary_cards.py'
        if not src.is_file():
            self.skipTest('Official projector only available in full Git checkout (CI), never mocked')
        canon = {'lexemes': [{'lexeme_id': 'lex1', 'lemma': 'die Beschreibung', 'pos': 'noun',
                              'morphology': {}}],
                 'senses': [{'sense_id': 'sense1', 'lexeme_id': 'lex1',
                             'translations': {'fa': 'توضیح', 'en': 'description'}}],
                 'expressions': [{'expression_id': 'expr1', 'canonical_form': 'eine Beschreibung abgeben',
                                  'translations': {'fa': 'توضیح ارائه کردن', 'en': 'provide a description'},
                                  'expression_type': 'collocation'}], 'relations': [
                                      {'relation_id': 'rel1', 'source_id': 'sense1',
                                       'target_id': 'expr1', 'relation_type': 'RELATED'}], 'sources': []}
        frozen = copy.deepcopy(canon)
        raw = canonical_json(canon)
        a, cards, meta = adapter.load_for_audit(raw, 'v411-canonical')
        self.assertEqual(sorted(c['id'] for c in cards), ['expr1', 'sense1'])
        self.assertEqual(meta['wordnetz_related_graph_cards_outside_scope'], 1)
        self.assertEqual(a.audit(cards, hashlib.sha256(raw).hexdigest())['related_items_scanned'], 0)
        self.assertEqual(canon, frozen)

    def test_raw_onepass_stage3_ledger_rejected_as_not_learner_projection(self):
        doc = {'schema': 'gcpk-stage3-onepass@1.0', 'working_sha256': 'a'*64,
               'cards': [{'id':'x', 'baseline':{}, 'decisions':{'related': {'decision':'HOLD', 'reason':'ambiguous'}}}]}
        with self.assertRaises(ValueError):
            adapter.load_for_audit(canonical_json(doc), 'normalized-json')

    def test_canonical_schema_rejected_when_wrong(self):
        with self.assertRaisesRegex(ValueError, 'NOT_V411_CANONICAL_SCHEMA'):
            adapter.load_for_audit(canonical_json({'cards': []}), 'v411-canonical')

    def test_canonical_duplicate_ids_rejected_before_projection(self):
        doc = {'lexemes': [], 'senses': [{'sense_id': 'same'}, {'sense_id': 'same'}], 'expressions': []}
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_OR_EMPTY_CANONICAL_TARGET_IDS'):
            adapter.load_for_audit(canonical_json(doc), 'v411-canonical')

    def test_projected_duplicate_ids_rejected(self):
        base = {'id': 'x', 'cardType': 'de-vocabulary', 'front': 'x',
                'details': [], 'examples': [], 'customFields': {}}
        with self.assertRaisesRegex(ValueError, 'V411_DUPLICATE_OR_MISSING_CARD_ID'):
            adapter.load_for_audit(canonical_json([base, copy.deepcopy(base)]), 'v411-projected')

    def test_projected_nonvocabulary_card_rejected(self):
        obj = {'id': 'x', 'cardType': 'german-verb', 'front': 'x',
               'details': [], 'examples': [], 'customFields': {}}
        with self.assertRaisesRegex(ValueError, 'NOT_AN_OFFICIAL_V411_LEXICAL_CARD'):
            adapter.load_for_audit(canonical_json([obj]), 'v411-projected')

    def test_canonical_unresolved_is_not_silently_retitled(self):
        with self.assertRaises(ValueError):
            adapter.load_for_audit(canonical_json({'lexemes': [], 'senses': [{'sense_id': None}],
                                                   'expressions': []}), 'v411-canonical')

    def test_source_hash_is_exact_input_and_not_fake_canonical_hash(self):
        raw = tsv_card('Vocabulary')
        a, cards, meta = adapter.load_for_audit(raw, 'universal-tsv')
        report = a.audit(cards, hashlib.sha256(raw).hexdigest())
        self.assertEqual(report['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertFalse(meta['wordnetz_graph_semantics_audited'])

    def test_negative_high_exit_and_nonapproval_with_exclusive_report(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / 'input.tsv'; dst = Path(d) / 'report.json'
            src.write_bytes(tsv_card('NVV', details=[related(surface='opaque-1'),
                                                       {'title':'Kombinationen','items':['opaque-1']}]))
            cp = subprocess.run([sys.executable, str(SRC), str(src), '--source-format', 'universal-tsv',
                                 '--output', str(dst), '--fail-on-high'], capture_output=True, text=True)
            self.assertEqual(cp.returncode, 1, cp.stderr)
            report=json.loads(dst.read_text(encoding='utf-8'))
            self.assertFalse(report['stage4_linguistic_approval'])
            self.assertTrue(report['adapter']['source_mutated'] is False)
            self.assertEqual(src.read_bytes(), tsv_card('NVV', details=[related(surface='opaque-1'),
                                                              {'title':'Kombinationen','items':['opaque-1']}] ))
            cp2 = subprocess.run([sys.executable, str(SRC), str(src), '--source-format', 'universal-tsv',
                                  '--output', str(dst)], capture_output=True, text=True)
            self.assertEqual(cp2.returncode, 2)

    def test_no_output_aliases_source(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / 'x.json'
            src.write_bytes(canonical_json({'cards':[{'id':'x','front':'x','details':[], 'examples':[]}]}))
            before = src.read_bytes()
            cp = subprocess.run([sys.executable, str(SRC), str(src), '--source-format', 'normalized-json',
                                 '--output', str(src)], capture_output=True, text=True)
            self.assertEqual(cp.returncode, 2)
            self.assertEqual(src.read_bytes(), before)

    def test_v411_camel_case_never_fabricates_related_items(self):
        doc=[{'id':'v411','cardType':'de-vocabulary','front':'Wort','details':[],
              'examples':[],'customFields':{'vnext_relations':[{'type':'RELATED',
                'items':[{'label':'Bezug','target_id':'t1'}]}]}}]
        a, cards, meta=adapter.load_for_audit(canonical_json(doc),'v411-projected')
        self.assertEqual(meta['wordnetz_related_graph_cards_outside_scope'], 1)
        self.assertEqual(cards[0]['relations'],[])
        self.assertEqual(a.audit(cards,'1'*64)['related_items_scanned'],0)


if __name__=='__main__':
    unittest.main()
