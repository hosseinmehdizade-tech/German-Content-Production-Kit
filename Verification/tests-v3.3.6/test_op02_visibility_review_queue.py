"""NONACTIVE Stage5→Stage6 independent PENDING-only review queue tests."""
from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
import build_op02_visibility_review_queue as q
import audit_op02_stage5_source_to_view as core


def fixture(unresolved=True, no_source_id=True):
    items=[
        {'de':'eine Entscheidung treffen','fa':'تصمیم گرفتن','en':'make a decision','kind':'noun_verb'},
        {'de':'eine wichtige Entscheidung','fa':'یک تصمیم مهم','en':'an important decision','kind':'adjective_noun'},
    ]
    if not no_source_id:
        items[0]['item_id']='synthetic-source-item-01'
    visible=[f"{i['de']} — {i['fa']}" for i in items[:1 if unresolved else 2]]
    fields={f:'' for f in core.UNIVERSAL_FIELDS}
    fields.update(id='synthetic-c001',lesson='A1-L01',card_type='de-vocabulary',
                  front='die Entscheidung',details=json.dumps([{'title':'Kombinationen','items':visible}],ensure_ascii=False),
                  custom_fields=json.dumps({'kombinationen_v1':{'visible_section':'Kombinationen','items':items}},ensure_ascii=False))
    mem=io.StringIO(newline='');w=csv.DictWriter(mem,fieldnames=core.UNIVERSAL_FIELDS,delimiter='\t',lineterminator='\n');w.writeheader();w.writerow(fields)
    led=json.dumps({'card_id':fields['id'],'items':items,'lesson':fields['lesson']},ensure_ascii=False)+'\n'
    return mem.getvalue().encode('utf-8'),led.encode('utf-8')


def package(tmp, tsv=None, ledger=None):
    if tsv is None:
        tsv,ledger=fixture()
    p=Path(tmp)/'synthetic-stage5.zip'
    with zipfile.ZipFile(p,'w') as z:
        z.writestr(core.TSV_MEMBER,tsv)
        z.writestr(core.LEDGER_MEMBER,ledger)
    return p,hashlib.sha256(p.read_bytes()).hexdigest()


class TestQueue(unittest.TestCase):
    def test_one_exact_source_anchored_pending_unit(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            a=q.build_queue(p,sha)
            self.assertEqual(a['status'],'BLOCKED_PENDING_INDEPENDENT_ITEM_AND_CURRENT_RUNTIME_EVIDENCE')
            self.assertEqual(a['counts']['unresolved_items'],1)
            x=a['items'][0]
            self.assertEqual(x['card_id'],'synthetic-c001')
            self.assertEqual(x['ordinal'],1)
            self.assertEqual(x['source_item_id'],None)
            self.assertEqual(x['fa'],'یک تصمیم مهم')
            self.assertEqual(x['review_status'],q.PENDING)
            self.assertFalse(x['auto_edit_authorized'])
            self.assertIsNone(x['runtime_evidence'])
            self.assertEqual(len(x['source_unit_sha256']),64)

    def test_fully_visible_source_still_cannot_claim_stage6_pass(self):
        with tempfile.TemporaryDirectory() as d:
            t,l=fixture(unresolved=False)
            p,sha=package(d,t,l)
            a=q.build_queue(p,sha)
            self.assertEqual(a['items'],[])
            self.assertEqual(a['counts']['unresolved_items'],0)
            self.assertEqual(a['status'],'BLOCKED_PENDING_INDEPENDENT_ITEM_AND_CURRENT_RUNTIME_EVIDENCE')
            self.assertEqual(a['runtime']['native_import_study_quick_evidence'],'NOT_RUN')

    def test_queue_deterministic_and_archive_readonly(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            a=q.build_queue(p,sha);b=q.build_queue(p,sha)
            self.assertEqual(q.canonical(a),q.canonical(b))
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),sha)
            self.assertEqual(a['item_list_sha256'],q.digest(q.canonical(a['items'])))

    def test_changed_accepted_translation_changes_source_fingerprint(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            a=q.build_queue(p,sha)
        with tempfile.TemporaryDirectory() as d:
            t,l=fixture()
            import json as _json
            rec=_json.loads(l.decode());rec['items'][1]['fa']='یک تصمیم بسیار مهم'
            row=list(csv.DictReader(io.StringIO(t.decode()),delimiter='\t'))[0]
            cf=_json.loads(row['custom_fields']);cf['kombinationen_v1']['items'][1]['fa']='یک تصمیم بسیار مهم'
            row['custom_fields']=_json.dumps(cf,ensure_ascii=False)
            tsv=io.StringIO(newline='');w=csv.DictWriter(tsv,fieldnames=core.UNIVERSAL_FIELDS,delimiter='\t',lineterminator='\n');w.writeheader();w.writerow(row)
            p,sha=package(d,tsv.getvalue().encode(),(_json.dumps(rec,ensure_ascii=False)+'\n').encode())
            b=q.build_queue(p,sha)
            self.assertNotEqual(a['items'][0]['source_unit_sha256'],b['items'][0]['source_unit_sha256'])

    def test_original_zip_sha_drift_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            with self.assertRaisesRegex(ValueError,'EXACT_ARCHIVE_SHA256_MISMATCH'):
                q.build_queue(p,'0'*64)

    def test_invalid_input_accepted_ledger_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            t,l=fixture()
            v=json.loads(l);v['items'][1]['en']='tampered'
            p,sha=package(d,t,(json.dumps(v,ensure_ascii=False)+'\n').encode())
            with self.assertRaisesRegex(ValueError,'LEDGER_TO_VIEW_BYTE_SEMANTIC_PARITY_FAILED'):
                q.build_queue(p,sha)

    def test_duplicate_explicit_unit_id_rejected_by_source_guard(self):
        with tempfile.TemporaryDirectory() as d:
            t,l=fixture(no_source_id=False)
            rec=json.loads(l);rec['items'][1]['item_id']='synthetic-source-item-01'
            row=list(csv.DictReader(io.StringIO(t.decode()),delimiter='\t'))[0]
            cf=json.loads(row['custom_fields']);cf['kombinationen_v1']['items'][1]['item_id']='synthetic-source-item-01'
            row['custom_fields']=json.dumps(cf,ensure_ascii=False)
            out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=core.UNIVERSAL_FIELDS,delimiter='\t',lineterminator='\n');w.writeheader();w.writerow(row)
            p,sha=package(d,out.getvalue().encode(),(json.dumps(rec,ensure_ascii=False)+'\n').encode())
            with self.assertRaisesRegex(ValueError,'DUPLICATE_EXPLICIT_ITEM_IDS'):
                q.build_queue(p,sha)

    def test_no_runtime_version_fabricated_from_historical_git(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            a=q.build_queue(p,sha)
            self.assertTrue(a['runtime']['resolve_current_fresh_at_validation'])
            self.assertFalse(a['runtime']['exact_current_zip_verified'])
            self.assertNotIn('runtime_version',a['runtime'])
            self.assertTrue(all(x['runtime_evidence'] is None for x in a['items']))

    def test_cli_writes_once_never_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            out=Path(d)/'queue.json'
            out.write_text('immutable user output',encoding='utf8')
            status=q.main(['--zip',str(p),'--sha256',sha,'--output',str(out)])
            self.assertEqual(status,2)
            self.assertEqual(out.read_text(), 'immutable user output')

    def test_cli_cannot_overwrite_source_archive(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            self.assertEqual(q.main(['--zip',str(p),'--sha256',sha,'--output',str(p)]),2)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),sha)

    def test_cli_success_creates_only_pending_queue(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            out=Path(d)/'pending.json'
            status=q.main(['--zip',str(p),'--sha256',sha,'--output',str(out)])
            self.assertEqual(status,2)  # generation succeeded but Stage6 gate stays red
            a=json.loads(out.read_text())
            self.assertEqual(a['status'],'BLOCKED_PENDING_INDEPENDENT_ITEM_AND_CURRENT_RUNTIME_EVIDENCE')
            self.assertEqual(a['counts']['unresolved_items'],1)
            self.assertEqual(q.main(['--zip',str(p),'--sha256',sha,'--output',str(out)]),2)

    def test_stage5_bad_zip_inventory_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            t,l=fixture();p=Path(d)/'synthetic-stage5.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr(core.TSV_MEMBER,t);z.writestr(core.LEDGER_MEMBER,l);z.writestr('../escape.txt',b'bad')
            with self.assertRaisesRegex(ValueError,'UNSAFE_ARCHIVE_MEMBER'):
                q.build_queue(p,hashlib.sha256(p.read_bytes()).hexdigest())

    def test_no_blank_review_fields_claims(self):
        with tempfile.TemporaryDirectory() as d:
            p,sha=package(d)
            a=q.build_queue(p,sha)
            for x in a['items']:
                self.assertEqual(x['review_status'],q.PENDING)
                self.assertIsNone(x['source_semantic_evidence'])
                self.assertIsNone(x['independent_adversarial_evidence'])
            self.assertFalse(a['runtime']['release_final'])


if __name__=='__main__':
    unittest.main()