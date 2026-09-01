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


RUNTIME_VALIDATOR = import_module('runtime_evidence_v314', '06-VALIDATION/validate_runtime_import_evidence.py')


def base_evidence():
    return {
        'evidence_version': '1.0',
        'target_runtime': {'product': 'German Flashcards Pro', 'version': 'v343'},
        'verification_mode': 'isolated-runtime',
        'artifact': {'file': 'sample.tsv', 'sha256': '0' * 64, 'schema_profile': 'universal-v2', 'row_count': 30},
        'import_mode': 'add',
        'artifact_status': 'APP_COMPATIBLE',
        'runtime_status': 'CURRENT_RUNTIME_NOT_VERIFIED',
        'scenarios': [
            {'name': 'ready-empty-library', 'passed': True, 'pre_count': 0, 'post_count': 30},
            {'name': 'ready-existing-library', 'passed': True, 'pre_count': 100, 'post_count': 130},
            {'name': 'write-blocked-fail-closed', 'passed': True, 'pre_count': 100, 'post_count': 100},
            {'name': 'recovery-resolved-ready-import', 'passed': True, 'pre_count': 100, 'post_count': 130},
            {'name': 'reload-durability', 'passed': True, 'post_count': 130},
            {'name': 'roundtrip-export', 'passed': True},
            {'name': 'writer-concurrency-guard', 'passed': True}
        ],
        'preflight': {'checked': False, 'runtime_mode': None, 'writes_blocked': None, 'can_write': None, 'writer_authority': None, 'unresolved_recovery': None, 'pending_unverified_commit': None, 'existing_library_count': None, 'library_fingerprint': None, 'block_reason': None},
        'commit': {'attempted': False, 'persistent_commit': None, 'verified': None, 'pre_count': None, 'post_count': None, 'expected_post_count': None, 'rollback_preserved_previous': None, 'error': None},
        'reload': {'performed': False, 'persistence_verified': None, 'post_reload_count': None, 'post_reload_fingerprint': None},
        'notes': []
    }


class V314RuntimeStateGateTests(unittest.TestCase):
    def test_prompt_separates_artifact_and_current_runtime(self):
        prompt = (PACKAGE / '01-CORE/CONTENT-GENERATION-MASTER-PROMPT-v3.1.5.md').read_text(encoding='utf-8')
        for token in ('APP_COMPATIBLE', 'CURRENT_RUNTIME_NOT_VERIFIED', 'RUNTIME_PREFLIGHT_PASS', 'RUNTIME_BLOCKED', 'IMPORT_VERIFIED'):
            self.assertIn(token, prompt)
        self.assertIn('IMPORT_READY` از v3.1.4 **ممنوع/Deprecated**', prompt)
        self.assertIn('existing non-empty library', prompt)
        self.assertIn('WRITE-BLOCKED / DEGRADED / RECOVERY', prompt)
        self.assertIn('reload/reopen durability', prompt)
        self.assertIn('هیچ Reset/Clear/Delete database', prompt)

    def test_valid_isolated_app_compatible_cannot_claim_current_runtime(self):
        ev = base_evidence()
        report = RUNTIME_VALIDATOR.validate(ev)
        self.assertEqual('PASS', report['status'], report['errors'])
        ev['runtime_status'] = 'IMPORT_VERIFIED'
        report = RUNTIME_VALIDATOR.validate(ev)
        self.assertEqual('FAIL', report['status'])
        self.assertTrue(any('isolated-runtime' in e or 'actual-user-runtime' in e for e in report['errors']))

    def test_blocked_live_runtime_is_valid_blocked_evidence_not_import_success(self):
        ev = base_evidence()
        ev['verification_mode'] = 'actual-user-runtime'
        ev['runtime_status'] = 'RUNTIME_BLOCKED'
        ev['preflight'] = {
            'checked': True,
            'runtime_mode': 'DEGRADED_READ_ONLY',
            'writes_blocked': True,
            'can_write': False,
            'writer_authority': True,
            'unresolved_recovery': True,
            'pending_unverified_commit': False,
            'existing_library_count': 1124,
            'library_fingerprint': 'fixture-before',
            'block_reason': 'database recovery not complete'
        }
        report = RUNTIME_VALIDATOR.validate(ev)
        self.assertEqual('PASS', report['status'], report['errors'])

    def test_preflight_pass_rejects_write_block(self):
        ev = base_evidence()
        ev['verification_mode'] = 'actual-user-runtime'
        ev['runtime_status'] = 'RUNTIME_PREFLIGHT_PASS'
        ev['preflight'] = {
            'checked': True,
            'runtime_mode': 'READY',
            'writes_blocked': True,
            'can_write': True,
            'writer_authority': True,
            'unresolved_recovery': False,
            'pending_unverified_commit': False,
            'existing_library_count': 1124,
            'library_fingerprint': 'fixture-before',
            'block_reason': None
        }
        report = RUNTIME_VALIDATOR.validate(ev)
        self.assertEqual('FAIL', report['status'])

    def test_import_verified_requires_commit_and_reload(self):
        ev = base_evidence()
        ev['verification_mode'] = 'actual-user-runtime'
        ev['runtime_status'] = 'IMPORT_VERIFIED'
        ev['preflight'] = {
            'checked': True,
            'runtime_mode': 'READY',
            'writes_blocked': False,
            'can_write': True,
            'writer_authority': True,
            'unresolved_recovery': False,
            'pending_unverified_commit': False,
            'existing_library_count': 1124,
            'library_fingerprint': 'before',
            'block_reason': None
        }
        ev['commit'] = {
            'attempted': True,
            'persistent_commit': True,
            'verified': True,
            'pre_count': 1124,
            'post_count': 1154,
            'expected_post_count': 1154,
            'rollback_preserved_previous': True,
            'error': None
        }
        ev['reload'] = {
            'performed': True,
            'persistence_verified': True,
            'post_reload_count': 1154,
            'post_reload_fingerprint': 'after'
        }
        report = RUNTIME_VALIDATOR.validate(ev)
        self.assertEqual('PASS', report['status'], report['errors'])
        ev['reload']['persistence_verified'] = False
        report = RUNTIME_VALIDATOR.validate(ev)
        self.assertEqual('FAIL', report['status'])

    def test_app_compatible_requires_existing_library_and_fail_closed_scenarios(self):
        ev = base_evidence()
        ev['scenarios'] = [s for s in ev['scenarios'] if s['name'] != 'ready-existing-library']
        report = RUNTIME_VALIDATOR.validate(ev)
        self.assertEqual('FAIL', report['status'])
        self.assertTrue(any('ready-existing-library' in e for e in report['errors']))

    def test_artifact_sha_can_be_bound_to_exact_file(self):
        ev = base_evidence()
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / 'sample.tsv'
            f.write_bytes(b'id\tfront\n1\ttest\n')
            ev['artifact']['sha256'] = RUNTIME_VALIDATOR.sha256_file(f)
            report = RUNTIME_VALIDATOR.validate(ev, f)
            self.assertEqual('PASS', report['status'], report['errors'])
            f.write_bytes(b'changed')
            report = RUNTIME_VALIDATOR.validate(ev, f)
            self.assertEqual('FAIL', report['status'])


if __name__ == '__main__':
    unittest.main()
