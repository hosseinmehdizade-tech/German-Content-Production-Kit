"""Source-only (not browser/Stage6) forensic route classification adversarial cases."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import audit_op02_source_display_routes as route
import build_op02_visibility_review_queue as q
import audit_op02_stage5_source_to_view as core

DE='eine wichtige Entscheidung'


def fixture(tmp, details=None, examples='', front='die Entscheidung', missing=True):
    original=[
      {'de':'eine Entscheidung treffen','fa':'تصمیم گرفتن','en':'make a decision','kind':'noun_verb'},
      {'de':DE,'fa':'یک تصمیم مهم','en':'an important decision','kind':'adjective_noun'}]
    if details is None:
        details=[{'title':'Kombinationen','items':['eine Entscheidung treffen — تصمیم گرفتن']}]
    if not missing:
        details=[{'title':'Kombinationen','items':[f"{v['de']} — {v['fa']}" for v in original]}]
    row={field:'' for field in core.UNIVERSAL_FIELDS}
    row.update(id='synthetic-c001',lesson='A1-L01',front=front,back='ساختگی',card_type='de-vocabulary',
               details=json.dumps(details,ensure_ascii=False),examples=examples,
               custom_fields=json.dumps({'kombinationen_v1':{'visible_section':'Kombinationen','items':original}},ensure_ascii=False))
    sio=io.StringIO(newline='');writer=csv.DictWriter(sio,delimiter='\t',fieldnames=core.UNIVERSAL_FIELDS,lineterminator='\n')
    writer.writeheader();writer.writerow(row)
    ledger=json.dumps({'card_id':row['id'],'lesson':row['lesson'],'items':original},ensure_ascii=False)+'\n'
    archive=Path(tmp)/'synthetic.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr(core.TSV_MEMBER,sio.getvalue().encode('utf8'))
        z.writestr(core.LEDGER_MEMBER,ledger.encode('utf8'))
    h=hashlib.sha256(archive.read_bytes()).hexdigest()
    return archive,h,q.build_queue(archive,h)

class SourceRoutes(unittest.TestCase):
    def check(self,**kwargs):
        with tempfile.TemporaryDirectory() as d:
            z,sha,pending=fixture(d,**kwargs)
            result=route.classify(z,sha,pending)
            self.assertEqual(result['source_pending_queue_items_sha256'],pending['item_list_sha256'])
            return result

    def test_no_alt_exact_de_is_priority_and_not_pass(self):
        result=self.check()
        self.assertEqual(result['counts']['units'],1)
        self.assertEqual(result['counts']['no_alternative_exact_de_in_scanned_fields'],1)
        self.assertEqual(result['highest_priority'][0]['de'],DE)
        self.assertEqual(result['status'],route.BLOCKED)

    def test_other_detail_exact_de_is_not_runtime_visibility(self):
        d=[{'title':'Kombinationen','items':['eine Entscheidung treffen — تصمیم گرفتن']},
           {'title':'Verwandte Wörter','items':[DE]}]
        r=self.check(details=d)
        self.assertEqual(r['counts']['other_details_exact_de'],1)
        self.assertEqual(r['counts']['no_alternative_exact_de_in_scanned_fields'],0)
        self.assertFalse(r['cases'][0]['bilingual_display_verified'])

    def test_source_example_substring_is_only_a_source_hit(self):
        r=self.check(examples=json.dumps(['Zum Beispiel: '+DE+'!']))
        self.assertEqual(r['counts']['any_other_tsv_text_columns_containing_de'],1)
        self.assertEqual(r['counts']['per_text_column_hits']['examples'],1)
        self.assertFalse(r['cases'][0]['native_current_runtime_verified'])

    def test_both_routes_are_counted_once_for_coverage(self):
        d=[{'title':'Kombinationen','items':['eine Entscheidung treffen — تصمیم گرفتن']},
           {'title':'Verwandte Wörter','items':[DE]}]
        r=self.check(details=d,examples=DE)
        self.assertEqual(r['counts']['overlap_other_details_and_tsv_text'],1)
        self.assertEqual(r['counts']['no_alternative_exact_de_in_scanned_fields'],0)
        self.assertEqual(len(r['cases']),1)

    def test_different_case_not_silently_normalized(self):
        r=self.check(examples=DE.upper())
        self.assertEqual(r['counts']['no_alternative_exact_de_in_scanned_fields'],1)

    def test_english_persian_only_not_a_german_hit(self):
        r=self.check(examples='an important decision یک تصمیم مهم')
        self.assertEqual(r['counts']['any_other_tsv_text_columns_containing_de'],0)

    def test_fully_visible_source_returns_empty_blocked_not_stage6(self):
        r=self.check(missing=False)
        self.assertEqual(r['counts']['units'],0)
        self.assertEqual(r['highest_priority'],[])
        self.assertEqual(r['status'],route.BLOCKED)

    def test_queue_lacks_one_case_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            z,sha,pending=fixture(d)
            pending['items']=[]
            with self.assertRaisesRegex(ValueError,'UNTRUSTED_QUEUE_OR_SOURCE_FINGERPRINT_DRIFT'):
                route.classify(z,sha,pending)

    def test_queue_source_unit_hash_tampering_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            z,sha,pending=fixture(d)
            pending['items'][0]['source_unit_sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'UNTRUSTED_QUEUE_OR_SOURCE_FINGERPRINT_DRIFT'):
                route.classify(z,sha,pending)

    def test_wrong_archive_digest_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            z,sha,pending=fixture(d)
            with self.assertRaisesRegex(ValueError,'EXACT_ARCHIVE_SHA256_MISMATCH'):
                route.classify(z,'0'*64,pending)

    def test_cli_created_report_returns_blocked_exit_two(self):
        with tempfile.TemporaryDirectory() as d:
            z,sha,pending=fixture(d)
            queue=Path(d)/'pending.json';queue.write_text(json.dumps(pending,ensure_ascii=False))
            out=Path(d)/'triage.json'
            cmd=[sys.executable,str(Path(route.__file__)),'--zip',str(z),'--zip-sha256',sha,'--queue',str(queue),'--output',str(out)]
            p=subprocess.run(cmd,capture_output=True,text=True,check=False)
            self.assertEqual(p.returncode,2)
            self.assertTrue(out.exists())
            self.assertEqual(json.loads(out.read_text())['status'],route.BLOCKED)
            self.assertEqual(subprocess.run(cmd,capture_output=True,check=False).returncode,2)

    def test_cli_rejects_overwriting_source_or_queue(self):
        with tempfile.TemporaryDirectory() as d:
            z,sha,pending=fixture(d)
            queue=Path(d)/'pending.json';queue.write_text(json.dumps(pending,ensure_ascii=False))
            for dest in (queue,z):
                old=dest.read_bytes()
                rc=route.main(['--zip',str(z),'--zip-sha256',sha,'--queue',str(queue),'--output',str(dest)])
                self.assertEqual(rc,2)
                self.assertEqual(old,dest.read_bytes())

    def test_report_deterministic_and_no_archive_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            z,sha,pending=fixture(d)
            a=route.classify(z,sha,pending)
            b=route.classify(z,sha,pending)
            self.assertEqual(route.canonical(a),route.canonical(b))
            self.assertEqual(hashlib.sha256(z.read_bytes()).hexdigest(),sha)

if __name__=='__main__':
    unittest.main()