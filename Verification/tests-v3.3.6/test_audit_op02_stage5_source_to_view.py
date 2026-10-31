"""NONACTIVE OP-02 source-to-view audit adversarial tests; no production writes."""
import copy
import csv
import hashlib
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile

P = pathlib.Path(__file__).with_name('audit_op02_stage5_source_to_view.py')
spec = importlib.util.spec_from_file_location('view_audit', P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture(view='object', missing=False):
    data = [
        {'de': 'eine Entscheidung treffen', 'fa': 'تصمیم گرفتن', 'en': 'make a decision', 'kind': 'noun_verb'},
        {'de': 'eine wichtige Entscheidung', 'fa': 'یک تصمیم مهم', 'en': 'an important decision', 'kind': 'adjective_noun'},
    ]  # Deliberately lack item IDs, as actual V22 does for many items.
    section = [{'title':'Kombinationen', 'items':[f"{v['de']} — {v['fa']}" for v in data[:1 if missing else 2]]}]
    if view == 'list':
        bridge = data
    elif view == 'object':
        bridge = {'visible_section':'Kombinationen', 'items':data}
    else:
        bridge = {'items':data}
    row = {f:'' for f in m.UNIVERSAL_FIELDS}
    row.update(id='c001', front='die Entscheidung', card_type='de-vocabulary', lesson='A1-L01',
               details=json.dumps(section, ensure_ascii=False),
               custom_fields=json.dumps({'kombinationen_v1':bridge}, ensure_ascii=False))
    ledger = [{'card_id':'c001','items':copy.deepcopy(data),'lesson':'A1-L01'}]
    return [row], ledger


def encode(rows, ledger):
    sio = io.StringIO(newline='')
    writer = csv.DictWriter(sio, fieldnames=m.UNIVERSAL_FIELDS, delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return (sio.getvalue().encode('utf-8'),
            ('\n'.join(json.dumps(x, ensure_ascii=False) for x in ledger)+'\n').encode('utf-8'))


class TestAudit(unittest.TestCase):
    def verify(self, rows=None, ledger=None):
        if rows is None:
            rows, ledger = fixture()
        return m.audit(*encode(rows,ledger))

    def test_positive_two_exact_items(self):
        r = self.verify()
        self.assertEqual(r['counts']['accepted_items'], 2)
        self.assertEqual(r['counts']['physical_matched_items'], 2)
        self.assertEqual(r['counts']['unaccounted_items'], 0)
        self.assertEqual(r['status'], 'PASS_SCOPED_LEDGER_AND_DETAILS_PARITY__NOT_RUNTIME')

    def test_preexisting_partial_section_is_risk_not_silent_pass(self):
        r = self.verify(*fixture(missing=True))
        self.assertEqual(r['status'], 'BLOCKED_VIEW_COVERAGE_REQUIRES_DISPOSITION__LEDGER_PARITY_PASS')
        self.assertEqual(r['counts']['items_EXISTING_PARTIAL_SECTION_CONFLICT'], 1)
        self.assertEqual(r['affected'][0]['unaccounted_items'][0]['ordinal'], 1)

    def test_legacy_list_supported_without_fabricating_ids(self):
        r = self.verify(*fixture(view='list'))
        self.assertEqual(r['counts']['view_envelope_legacy_list'], 1)

    def test_missing_selector_with_nonempty_view_rejected(self):
        with self.assertRaisesRegex(ValueError,'INVALID_VISIBLE_SECTION_SELECTOR'):
            self.verify(*fixture(view='selectorless'))

    def test_wrong_source_ledger_fa_rejected(self):
        rows, ledger=fixture()
        ledger[0]['items'][0]['fa']='معنی غلط'
        with self.assertRaisesRegex(ValueError, 'LEDGER_TO_VIEW_BYTE_SEMANTIC_PARITY_FAILED'):
            self.verify(rows, ledger)

    def test_wrong_source_ledger_en_rejected(self):
        rows, ledger=fixture()
        ledger[0]['items'][0]['en']='wrong meaning'
        with self.assertRaisesRegex(ValueError, 'LEDGER_TO_VIEW_BYTE_SEMANTIC_PARITY_FAILED'):
            self.verify(rows, ledger)

    def test_source_ledger_reordered_rejected(self):
        rows, ledger=fixture()
        ledger[0]['items'].reverse()
        with self.assertRaisesRegex(ValueError, 'LEDGER_TO_VIEW_BYTE_SEMANTIC_PARITY_FAILED'):
            self.verify(rows, ledger)

    def test_duplicate_explicit_item_id_rejected(self):
        rows, ledger=fixture()
        for obj in ledger[0]['items']:obj['id']='duplicate'
        cf=json.loads(rows[0]['custom_fields'])
        for obj in cf['kombinationen_v1']['items']:obj['id']='duplicate'
        rows[0]['custom_fields']=json.dumps(cf)
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_EXPLICIT_ITEM_IDS'):
            self.verify(rows,ledger)

    def test_missing_accepted_translation_rejected(self):
        rows, ledger=fixture()
        for obj in ledger[0]['items']:obj.pop('fa', None)
        cf=json.loads(rows[0]['custom_fields'])
        for obj in cf['kombinationen_v1']['items']:obj.pop('fa',None)
        rows[0]['custom_fields']=json.dumps(cf)
        with self.assertRaisesRegex(ValueError, 'INVALID_ACCEPTED_ITEM_LANGUAGE'):
            self.verify(rows,ledger)

    def test_duplicate_details_section_rejected(self):
        rows,ledger=fixture()
        sections=json.loads(rows[0]['details'])
        sections.append(copy.deepcopy(sections[0]))
        rows[0]['details']=json.dumps(sections)
        with self.assertRaisesRegex(ValueError,'DUPLICATE_KOMBINATIONEN_SECTION'):
            self.verify(rows,ledger)

    def test_duplicate_json_key_fails_closed(self):
        rows,ledger=fixture()
        rows[0]['custom_fields']='{"kombinationen_v1":[], "kombinationen_v1":[]}'
        with self.assertRaisesRegex(ValueError,'DUPLICATE_JSON_KEY'):
            self.verify(rows,ledger)

    def test_duplicated_card_id_rejected(self):
        rows,ledger=fixture()
        rows.append(copy.deepcopy(rows[0]));ledger.append(copy.deepcopy(ledger[0]))
        with self.assertRaisesRegex(ValueError,'DUPLICATE_TSV_CARD_ID'):
            self.verify(rows,ledger)

    def test_malformed_extra_tsv_cell_rejected(self):
        rows,ledger=fixture()
        a,b=encode(rows,ledger)
        with self.assertRaisesRegex(ValueError,'INVALID_UNIVERSAL_ROWS'):
            m.audit(a+b'\tINVALID_EXTRA_CELL\n',b)

    def test_different_ledger_order_rejected(self):
        rows, ledger=fixture()
        r2=copy.deepcopy(rows[0]);r2['id']='c002';rows.append(r2)
        l2=copy.deepcopy(ledger[0]);l2['card_id']='c002';ledger.append(l2)
        ledger.reverse()
        with self.assertRaisesRegex(ValueError,'ROW_LEDGER_ID_OR_ORDER_MISMATCH'):
            self.verify(rows,ledger)

    def test_other_section_text_not_miscounted_as_combination(self):
        rows,ledger=fixture(missing=True)
        de=ledger[0]['items'][1]['de']
        sections=json.loads(rows[0]['details'])
        sections.append({'title':'Verwandte Wörter','items':[de]})
        rows[0]['details']=json.dumps(sections,ensure_ascii=False)
        res=self.verify(rows,ledger)
        self.assertEqual(res['counts']['unaccounted_items'],1)
        self.assertEqual(res['affected'][0]['unaccounted_items'][0]['other_detail_sections_exact_de'],['Verwandte Wörter'])

    def test_bad_external_zip_sha_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'fake.zip';p.write_bytes(b'not-a-valid-zip')
            with self.assertRaisesRegex(ValueError, 'EXACT_ARCHIVE_SHA256_MISMATCH'):
                m.audit_archive(p,'0'*64)

    def test_real_zip_members_roundtrip_synthetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'tiny.zip'
            rows,ledger=fixture()
            t,l=encode(rows,ledger)
            with zipfile.ZipFile(p,'w') as z:
                z.writestr(m.TSV_MEMBER,t)
                z.writestr(m.LEDGER_MEMBER,l)
            result=m.audit_archive(p,hashlib.sha256(p.read_bytes()).hexdigest())
            self.assertEqual(result['counts']['accepted_items'],2)

    def test_cli_review_needed_returns_nonzero_not_green(self):
        rows,ledger=fixture(missing=True)
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'review.zip'
            a,b=encode(rows,ledger)
            with zipfile.ZipFile(p,'w') as z:
                z.writestr(m.TSV_MEMBER,a)
                z.writestr(m.LEDGER_MEMBER,b)
            result=subprocess.run([sys.executable,str(P),'--zip',str(p),'--sha256',hashlib.sha256(p.read_bytes()).hexdigest()],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('BLOCKED_VIEW_COVERAGE',result.stdout)

    def test_cli_all_physical_returns_zero(self):
        rows,ledger=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'pass.zip'
            a,b=encode(rows,ledger)
            with zipfile.ZipFile(p,'w') as z:
                z.writestr(m.TSV_MEMBER,a)
                z.writestr(m.LEDGER_MEMBER,b)
            result=subprocess.run([sys.executable,str(P),'--zip',str(p),'--sha256',hashlib.sha256(p.read_bytes()).hexdigest()],capture_output=True,text=True)
            self.assertEqual(result.returncode,0)
            self.assertIn('PASS_SCOPED_LEDGER_AND_DETAILS_PARITY',result.stdout)

    def test_zero_items_without_visible_selector_is_no_force(self):
        rows,ledger=fixture()
        cf=json.loads(rows[0]['custom_fields']);cf['kombinationen_v1']={'items':[]}
        rows[0]['custom_fields']=json.dumps(cf)
        ledger[0]['items']=[]
        rows[0]['details']='[]'
        res=self.verify(rows,ledger)
        self.assertEqual(res['counts']['accepted_items'],0)


if __name__ == '__main__':
    unittest.main()