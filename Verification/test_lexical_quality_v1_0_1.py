#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('q', HERE / 'validate_lexical_quality_v1_0_1.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


def base_dataset():
    return {'learning_units': [{
        'id': 'T-1', 'type': 'verb', 'headword': 'hören', 'persian_meaning': 'شنیدن',
        'definition_de': 'mit den Ohren wahrnehmen',
        'core': {'present_3sg': 'hört', 'preterite_3sg': 'hörte', 'perfect': 'hat gehört', 'auxiliary': 'haben', 'reflexive': False, 'separability': 'non_prefixed'},
        'examples': [{'id': 'e1', 'text': 'Ich höre Musik.', 'translations': [{'lang': 'fa-IR', 'text': 'موسیقی گوش می‌دهم.'}, {'lang': 'en-US', 'text': 'I listen to music.'}]}],
        'provenance': {'sources': []}
    }]}


def codes(report):
    return {x.get('code') for x in report.get('issues', [])}


def raw_tsv(row):
    return '\t'.join(q.base.HEADERS) + '\n' + '\t'.join(row) + '\n'


def run():
    d = base_dataset()
    u = d['learning_units'][0]
    u['details'] = {'synonyms': ['[1a] lauschen']}
    u['provenance']['sources'] = [{'verification_status': 'verified', 'what_was_verified': ['synonymy']}]
    r = q.validate_dataset(d)
    assert 'SOURCE_SENSE_MARKER_LEAK' in codes(r), r

    d = base_dataset()
    u = d['learning_units'][0]
    u['details'] = {'synonyms': ['lauschen', 'horchen']}
    u['provenance']['sources'] = [{'verification_status': 'verified', 'what_was_verified': ['synonymy']}]
    r = q.validate_dataset(d)
    assert 'SOURCE_SENSE_MARKER_LEAK' not in codes(r), r

    d = base_dataset()
    u = d['learning_units'][0]
    u['connections'] = [{'kind': 'collocation', 'text': '[2b] Musik hören'}]
    u['provenance']['sources'] = [{'verification_status': 'verified', 'what_was_verified': ['collocation']}]
    r = q.validate_dataset(d)
    assert 'SOURCE_SENSE_MARKER_LEAK' in codes(r), r

    d = base_dataset()
    u = d['learning_units'][0]
    headers = q.base.HEADERS
    canonical = json.dumps({'canonical_unit': u}, ensure_ascii=False, separators=(',', ':'))
    row = ['T-1','de-vocabulary','German','verb','Test','A1','L1','Verben','hören','شنیدن','Deutsch','فارسی','de-DE','fa-IR','front-core',json.dumps(u['examples'],ensure_ascii=False,separators=(',',':')),json.dumps(['[1a] lauschen'],ensure_ascii=False),json.dumps([],ensure_ascii=False),'[]',canonical,'','','1']
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / 'bad.tsv'; p.write_text(raw_tsv(row), encoding='utf-8')
        r = q.validate_tsv(p, d)
        c = codes(r)
        assert 'TSV_RELATION_PARITY' in c and 'SOURCE_SENSE_MARKER_LEAK' in c, r

    # CSV/RFC4180 quoting is not Universal TSV. The runtime parser expects raw JSON cells between tabs.
    d = base_dataset(); u = d['learning_units'][0]
    canonical = json.dumps({'canonical_unit': u}, ensure_ascii=False, separators=(',', ':'))
    quoted_related = '"[""lauschen"",""horchen""]"'
    row = ['T-1','de-vocabulary','German','verb','Test','A1','L1','Verben','hören','شنیدن','Deutsch','فارسی','de-DE','fa-IR','front-core',json.dumps(u['examples'],ensure_ascii=False,separators=(',',':')),quoted_related,'[]','[]',canonical,'','','1']
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / 'csv-quoted.tsv'; p.write_text(raw_tsv(row), encoding='utf-8')
        r = q.validate_tsv(p, d)
        assert 'TSV_CSV_QUOTING_FORBIDDEN' in codes(r), r

    print('PASS lexical-quality v1.0.1 source-marker/TSV regressions')


if __name__ == '__main__':
    run()
