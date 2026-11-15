"""Regression tests for the evidence-bound status guard. Run with unittest discover."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
from status_currentness_gate_v1 import evaluate, SCHEMA, PROVIDERS


class CurrentnessGateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.raw = self.base / 'latest.json'
        self.raw.write_text(json.dumps({'cards': [{'id': '1'}, {'id': '2'}]}), encoding='utf-8')
        digest = hashlib.sha256(self.raw.read_bytes()).hexdigest()
        self.doc = {
            'schema': SCHEMA,
            'workstream': 'menschen-a1-verben',
            'provider_observations': {
                p: {'status': 'checked', 'locator': 'evidence://' + p} for p in PROVIDERS
            },
            'artifacts': [
                {'id': 'R10', 'role': 'accepted', 'active': True,
                 'sha256': 'a' * 64, 'provider': 'google_drive',
                 'locator': 'previously validated acceptance receipt'},
                {'id': 'R16-P19', 'role': 'working', 'active': True,
                 'sha256': digest, 'path': str(self.raw), 'expected_cards': 2,
                 'provider': 'google_drive', 'locator': 'actual master readback'}
            ],
            'claims': {'current_working_id': 'R16-P19', 'accepted_baseline_id': 'R10'}
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_stale_r10_current_working_claim_rejected(self):
        self.doc['claims']['current_working_id'] = 'R10'
        result = evaluate(self.doc, self.base)
        self.assertEqual(result['status'], 'FAIL_STALE_OR_CORRUPT')
        self.assertTrue(any('STALE_CURRENT_WORKING_ID' in x for x in result['errors']))

    def test_new_working_and_old_accepted_are_both_visible(self):
        result = evaluate(self.doc, self.base)
        self.assertEqual(result['status'], 'PASS_OBSERVED_STATUS_CLAIM')
        self.assertEqual(result['selected'], {'working': 'R16-P19', 'accepted': 'R10'})
        self.assertIn('R10', result['byte_evidence'])
        self.assertTrue(result['warnings'])

    def test_missing_working_file_holds(self):
        self.raw.unlink()
        self.assertEqual(evaluate(self.doc, self.base)['status'], 'HOLD_INCOMPLETE_EVIDENCE')

    def test_missing_library_discovery_holds(self):
        del self.doc['provider_observations']['library']
        self.assertEqual(evaluate(self.doc, self.base)['status'], 'HOLD_INCOMPLETE_EVIDENCE')

    def test_hash_mismatch_fails(self):
        self.raw.write_text('changed', encoding='utf-8')
        self.assertEqual(evaluate(self.doc, self.base)['status'], 'FAIL_STALE_OR_CORRUPT')

    def test_two_active_working_artifacts_hold(self):
        self.doc['artifacts'].append(dict(self.doc['artifacts'][1], id='R16-P20', active=True))
        self.assertEqual(evaluate(self.doc, self.base)['status'], 'HOLD_INCOMPLETE_EVIDENCE')

    def test_unresolved_competing_working_artifact_holds(self):
        self.doc['artifacts'].append(dict(self.doc['artifacts'][1], id='R16-P20', active=False))
        self.assertEqual(evaluate(self.doc, self.base)['status'], 'HOLD_INCOMPLETE_EVIDENCE')

    def test_no_status_claim_fails(self):
        self.doc['claims'] = {}
        self.assertEqual(evaluate(self.doc, self.base)['status'], 'FAIL_STALE_OR_CORRUPT')


if __name__ == '__main__':
    unittest.main()
