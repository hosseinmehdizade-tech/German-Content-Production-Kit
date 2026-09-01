import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[2]


def import_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / relative)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


BUILDER = import_module('gfp_delivery_builder_v313', '06-VALIDATION/build_flashcards_pro_universal_v2.py')
DELIVERY_VALIDATOR = import_module('gfp_delivery_validator_v313', '06-VALIDATION/validate_flashcards_pro_universal_v2.py')


def load(relative):
    return json.loads((PACKAGE / relative).read_text(encoding='utf-8'))


class V313DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.dataset = load('05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json')
        self.profile = load('03-PROFILES/ARCHITECTURE-PROOF.json')

    def build(self, folder: Path):
        tsv = folder / 'sample.tsv'
        meta = folder / 'BUILD-METADATA.json'
        BUILDER.write_tsv(self.dataset, self.profile, tsv)
        BUILDER.write_metadata(tsv, meta, 'test-v313')
        return tsv, meta

    def test_exact_universal_v2_header_and_row_count(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, _ = self.build(Path(td))
            with tsv.open('r', encoding='utf-8-sig', newline='') as fh:
                rows = list(csv.reader(fh, delimiter='\t'))
            self.assertEqual(BUILDER.BASE_COLUMNS, rows[0])
            self.assertEqual(len(self.dataset['learning_units']), len(rows) - 1)

    def test_lossless_canonical_unit_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, meta = self.build(Path(td))
            report = DELIVERY_VALIDATOR.validate(tsv, None, meta)
            self.assertEqual('PASS', report['status'], report['errors'])
            with tsv.open('r', encoding='utf-8-sig', newline='') as fh:
                rows = list(csv.DictReader(fh, delimiter='\t'))
            by_id = {u['id']: u for u in self.dataset['learning_units']}
            for row in rows:
                custom = json.loads(row['custom_fields'])
                self.assertEqual(by_id[row['id']], custom['canonical_unit'])

    def test_nvv_and_collocation_remain_distinct(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, _ = self.build(Path(td))
            with tsv.open('r', encoding='utf-8-sig', newline='') as fh:
                rows = list(csv.DictReader(fh, delimiter='\t'))
            noun = next(r for r in rows if r['front'] == 'Entscheidung')
            custom = json.loads(noun['custom_fields'])
            kinds = {x['kind'] for x in custom['canonical_unit']['connections']}
            self.assertIn('nvv', kinds)
            self.assertIn('collocation', kinds)
            details = json.loads(noun['details'])
            titles = {section['title'] for section in details}
            self.assertIn('NVV', titles)
            self.assertIn('Kollokationen', titles)

    def test_build_metadata_hash_matches_exact_tsv(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, meta = self.build(Path(td))
            metadata = json.loads(meta.read_text(encoding='utf-8'))
            self.assertEqual(BUILDER.sha256_file(tsv), metadata['data_sha256'])
            self.assertEqual('universal-v2', metadata['schema_profile'])

    def test_deep_parity_validator_with_canonical_source(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            tsv, meta = self.build(folder)
            canonical = folder / 'canonical.json'
            canonical.write_text(json.dumps(self.dataset, ensure_ascii=False, indent=2), encoding='utf-8')
            report = DELIVERY_VALIDATOR.validate(tsv, canonical, meta)
            self.assertEqual('PASS', report['status'], report['errors'])
            self.assertEqual([], report['warnings'])

    def test_current_prompt_keeps_delivery_and_runtime_claims_separate(self):
        prompt = (PACKAGE / '01-CORE/CONTENT-GENERATION-MASTER-PROMPT-v3.1.5.md').read_text(encoding='utf-8')
        self.assertIn('TRANSPORT_VALIDATED', prompt)
        self.assertIn('APP_COMPATIBLE', prompt)
        self.assertIn('RUNTIME_BLOCKED', prompt)
        self.assertIn('IMPORT_VERIFIED', prompt)
        self.assertIn('BUILD-METADATA.json', prompt)


if __name__ == '__main__':
    unittest.main()
