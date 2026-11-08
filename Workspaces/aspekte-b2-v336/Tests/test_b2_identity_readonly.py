"""Portable, synthetic and negative tests. No real learner data or browser required."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('b2', HERE / 'b2_identity_readonly_preflight.py')
b2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2)
ORDINALS = ['1556','1575','1609','1616','1630','1671','1697']
DECISIONS = [
  'KEEP_STANDALONE_B2', 'HOLD_B1_USAGE_ENRICHMENT_LINK',
  'KEEP_STANDALONE_B2', 'HOLD_A2_ENRICHMENT_OR_B2_FALLBACK',
  'KEEP_NONCARD_CONDITIONAL_B1_REUSE', 'KEEP_STANDALONE_B2', 'KEEP_STANDALONE_B2',
]
REFS = ['', 'mb1m-lu-1040; mb1m-lu-2338', 'mb1m-lu-1880', 'ma2m-lu-0281', 'mb1m-lu-2779', 'AB1P-SRC-0075', '']

class SafeIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        cls.l01 = cls.base / 'synthetic-L01.csv'
        cls.matrix = cls.base / 'synthetic-matrix.csv'
        fields = ['unit_id','source_ordinals','export_importable','linguistic_release_approved']
        with cls.l01.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f,fieldnames=fields)
            w.writeheader()
            for ord_ in range(1549,1709):
                if ord_ in (1630,1660): continue
                w.writerow(dict(unit_id=f'ab2-l01-u-{ord_}',source_ordinals=str(ord_),
                                export_importable='FALSE',linguistic_release_approved='FALSE'))
        cls.expected = b2.sha(cls.l01)
        headers = ['source_ordinal','b2_lemma','b2_current_record_type','b2_current_record_id',
                   'documented_prior_reference_ids','nonmutating_decision','b2_current_source_sha256',
                   'live_app_card_identity_observed','live_srs_snapshot_observed','approved_for_import']
        with cls.matrix.open('w', encoding='utf-8', newline='') as f:
            w=csv.DictWriter(f,fieldnames=headers);w.writeheader()
            for ord_,dec,refs in zip(ORDINALS,DECISIONS,REFS):
                w.writerow(dict(source_ordinal=ord_,b2_lemma='synthetic',
                     b2_current_record_type='NONCARD_REUSE_SIDECAR' if ord_=='1630' else 'CARD_DRAFT',
                     b2_current_record_id=f'ab2-l01-reuse-{ord_}' if ord_=='1630' else f'ab2-l01-u-{ord_}',
                     documented_prior_reference_ids=refs,nonmutating_decision=dec,
                     b2_current_source_sha256=cls.expected,live_app_card_identity_observed='NO',
                     live_srs_snapshot_observed='NO',approved_for_import='NO'))

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def report(self,evidence=None):
        return b2.make_report(self.matrix,self.l01,evidence,self.expected)

    def test_synthetic_count_and_blocked(self):
        r=self.report()
        self.assertEqual(r['summary']['cases'],7)
        self.assertEqual(r['summary']['B2_draft_cases'],6)
        self.assertEqual(r['summary']['conditional_noncard_cases'],1)
        self.assertEqual(r['status'],'BLOCKED_NONIMPORT')
        self.assertEqual(r['summary']['live_accepted_card_IDs_verified'],0)

    def test_does_not_trust_claimed_live_export_or_leak_private_srs(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'user-export.json'
            p.write_text(json.dumps({'kind':'live','cards':[
              {'id':'mb1m-lu-1040','reps':6,'due':123},
              {'id':'ma2m-lu-0281','front':'die Art'},
              {'id':'mb1m-lu-2779','reviews':11},
              {'id':'ab2-l01-u-1575','reviews':12}]}),encoding='utf-8')
            report=self.report(p)
            self.assertEqual(report['summary']['observed_referenced_prior_ids_in_file'],3)
            self.assertEqual(report['summary']['observed_prior_ids_with_SRS_fields_in_file'],2)
            self.assertEqual(report['summary']['live_SRS_identity_verified'],0)
            self.assertEqual(report['summary']['cards_approved_for_import'],0)
            self.assertTrue(all(not r['live_accepted_identity_verified'] for r in report['rows']))
            self.assertNotIn('"due"',json.dumps(report))
            self.assertNotIn('die Art',json.dumps(report))

    def test_forensic_historical_cache_not_live(self):
        archive={'payload':{'localStorage':[['gfp_progress_v8',json.dumps({'cards':{'mb1m-lu-2779':{'reps':5}}})]],
                            'databases':[{'name':'GermanFlashcardsProDB_v6','stores':[]}]}}
        rec,meta=b2.gather_evidence(archive)
        self.assertEqual(rec[0][0],'mb1m-lu-2779')
        self.assertEqual(meta['trust'],'NOT_LIVE_ACTIVE_ATTESTATION')

    def test_unknown_nested_id_rejected_as_unrecognized(self):
        _,meta=b2.gather_evidence({'backups':[{'id':'mb1m-lu-2779','reps':2}]})
        self.assertEqual(meta['parsing'],'UNRECOGNIZED')

    def test_unknown_json_file_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'unknown.json';p.write_text('{"backups": [{"id": "mb1m-lu-2779"}]}')
            with self.assertRaisesRegex(ValueError,'Unsupported export'):
                self.report(p)

    def test_checksum_mismatch_blocks(self):
        with self.assertRaisesRegex(ValueError,'checksum'):
            b2.make_report(self.matrix,self.l01,None,'0'*64)

    def test_seven_case_matrix_tamper_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'matrix.csv';p.write_bytes(self.matrix.read_bytes()+b'\n9999,x\n')
            with self.assertRaises(ValueError):b2.read_matrix(p)

    def test_wrong_matrix_sidecar_or_import_flag_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'matrix.csv';s=self.matrix.read_text().replace('NONCARD_REUSE_SIDECAR','CARD_DRAFT')
            p.write_text(s)
            with self.assertRaises(ValueError):b2.read_matrix(p)
            p.write_text(self.matrix.read_text().replace('NO,NO,NO','NO,NO,YES'))
            with self.assertRaises(ValueError):b2.read_matrix(p)

    def test_duplicate_evidence_ids_unequivocally_unapproved(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'dup.json';p.write_text(json.dumps({'cards':[
                {'id':'mb1m-lu-2779','reviews':2},{'id':'mb1m-lu-2779','reviews':3}]}))
            r=self.report(p)
            self.assertEqual(r['summary']['duplicate_evidence_file_card_ids'],1)
            self.assertEqual(r['summary']['cards_approved_for_import'],0)

    def test_bad_json_safe_failure(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'broken.json';p.write_text('{')
            with self.assertRaises(json.JSONDecodeError):self.report(p)

    def test_l01_source_mutant_safety_flag_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'evil.csv';p.write_bytes(self.l01.read_bytes().replace(b'FALSE',b'TRUE',1))
            m=Path(t)/'matrix.csv'
            m.write_text(self.matrix.read_text().replace(self.expected,b2.sha(p)))
            with self.assertRaisesRegex(ValueError,'NONIMPORT'):
                b2.make_report(m,p,None,b2.sha(p))

    def test_cli_writes_only_to_outdir_returns_nonzero_and_preserves_input(self):
        with tempfile.TemporaryDirectory() as t:
            old1,old2=b2.sha(self.l01),b2.sha(self.matrix)
            result=b2.main(['--matrix',str(self.matrix),'--l01-current',str(self.l01),
                         '--expected-l01-sha256',self.expected,'--out-dir',t])
            self.assertEqual(result,2)
            report=json.loads((Path(t)/'B2-L01-SRS-IDENTITY-READONLY-RESULT.json').read_text())
            self.assertEqual(report['status'],'BLOCKED_NONIMPORT')
            self.assertEqual((b2.sha(self.l01),b2.sha(self.matrix)),(old1,old2))

if __name__=='__main__': unittest.main(verbosity=2)
