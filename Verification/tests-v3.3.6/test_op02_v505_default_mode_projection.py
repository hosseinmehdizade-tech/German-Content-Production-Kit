"""Synthetic fail-closed tests for static v505 default Study/Quick diagnostic.
No user ZIP, actual browser or release status is mocked as successful.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('v505_mode',ROOT/'audit_op02_v505_default_mode_projection.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def make_row(existing=False,visible='Kombinationen'):
    kv={'visible_section':visible,'items':[{'de':'arbeiten mit jemandem','fa':'با کسی کار کردن','en':'work with someone'}]}
    details=[{'title':'English','items':['work']},{'title':'Formen','items':['arbeitet']}]
    if existing:details.append({'title':'Kombinationen','items':['etwas anderes — چیزی دیگر']})
    return {'id':'c001','lesson':'A1-L01','custom_fields':json.dumps({'kombinationen_v1':kv},ensure_ascii=False),
            'details':json.dumps(details,ensure_ascii=False)}


class TestV505Modes(unittest.TestCase):
    def test_embedded_order_places_combinations_third(self):
        self.assertEqual(m.DEFAULT_ORDER.index('combinations'),2)

    def test_default_quick_three_sections_contains_combinations(self):
        self.assertIn('combinations',m.DEFAULT_ORDER[:3])

    def test_default_study_bridge_needs_actual_dom(self):
        self.assertEqual(m.classify_case(make_row(),{},'AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF'),
                         'DEFAULT_SOURCE_MODEL_BRIDGE_GENERATED_NOT_DOM_VERIFIED')

    def test_existing_partial_section_is_not_repaired(self):
        self.assertEqual(m.classify_case(make_row(existing=True),{},'EXISTING_PARTIAL_SECTION_CONFLICT'),
                         'DEFAULT_SOURCE_MODEL_MISSING_FROM_COMBINATIONS')

    def test_wrong_selector_rejected(self):
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_CURRENT_BRIDGE_SCHEMA'):
            m.classify_case(make_row(visible='Verwandte Wörter'),{},'AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF')

    def test_bridged_card_cannot_have_nonempty_physical_combo(self):
        with self.assertRaisesRegex(ValueError,'EXPECTED_EMPTY_KOMBINATIONEN'):
            m.classify_case(make_row(existing=True),{},'AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF')

    def test_partial_card_requires_nonempty_physical_combo(self):
        with self.assertRaisesRegex(ValueError,'EXPECTED_PARTIAL_SECTION'):
            m.classify_case(make_row(),{},'EXISTING_PARTIAL_SECTION_CONFLICT')

    def test_two_same_sections_rejected(self):
        r=make_row(existing=True);d=json.loads(r['details']);d.append(copy.deepcopy(d[-1]));r['details']=json.dumps(d)
        with self.assertRaisesRegex(ValueError,'DUPLICATE_SECTION'):
            m.classify_case(r,{},'EXISTING_PARTIAL_SECTION_CONFLICT')

    def test_unknown_review_category_rejected(self):
        with self.assertRaisesRegex(ValueError,'UNKNOWN_CATEGORY'):
            m.classify_case(make_row(),{},'GLOBALLY_APPROVED')

    def test_legacy_canonical_without_examples_is_not_new_architecture(self):
        self.assertFalse(m.canonical_unit_parseable({'canonical_unit':{'type':'noun','core':{},'details':{}}}))

    def test_legacy_canonical_with_examples_is_parseable(self):
        self.assertTrue(m.canonical_unit_parseable({'canonical_unit':{'examples':[]}}))

    def test_old_format_full_envelope_recognized(self):
        self.assertTrue(m.canonical_unit_parseable({'german_content_v312':{'unit':{'examples':[]}}}))

    def test_unparseable_canonical_string_not_full_unit(self):
        self.assertFalse(m.canonical_unit_parseable({'canonical_unit':'{broken-json'}))

    def test_no_source_zip_cannot_false_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):m.audit(Path(tmp)/'missing.zip',Path(tmp)/'missing.json')

    def test_fake_zip_sha_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            z=Path(tmp)/'fake.zip';z.write_bytes(b'not-the-V22-original')
            with self.assertRaisesRegex(ValueError,'EXACT_V22_ARCHIVE_SHA_MISMATCH'):
                m.audit(z,Path(tmp)/'queue.json')

if __name__=='__main__':unittest.main()