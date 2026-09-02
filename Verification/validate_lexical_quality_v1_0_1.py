#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('lexq100', HERE / 'validate_lexical_quality_v1_0_0.py')
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

SOURCE_SENSE_MARKER_RE = re.compile(r'^\s*\[\s*\d+(?:[a-z])?\s*\]\s*', re.I)


def _issue(code, uid, path, message):
    return {'severity': 'error', 'code': code, 'id': uid, 'path': path, 'message': message}


def _finalize(report):
    report['validator_version'] = '1.0.1'
    report['errors'] = sum(x.get('severity') == 'error' for x in report.get('issues', []))
    report['status'] = 'FAIL' if report['errors'] else 'PASS'
    return report


def validate_dataset(ds):
    report = base.validate_dataset(ds)
    units = ds.get('learning_units') if isinstance(ds, dict) else []
    for i, unit in enumerate(units or []):
        if not isinstance(unit, dict):
            continue
        uid = str(unit.get('id') or f'index-{i}')
        details = unit.get('details') if isinstance(unit.get('details'), dict) else {}
        for field in ('synonyms', 'antonyms', 'rection'):
            values = details.get(field)
            if isinstance(values, list):
                for j, value in enumerate(values):
                    if isinstance(value, str) and SOURCE_SENSE_MARKER_RE.search(value):
                        report['issues'].append(_issue(
                            'SOURCE_SENSE_MARKER_LEAK', uid, f'details.{field}[{j}]',
                            'Dictionary/source sense markers such as [1a] are provenance locators, not learner-facing text.'
                        ))
        for j, conn in enumerate(unit.get('connections') or []):
            if not isinstance(conn, dict):
                continue
            text = str(conn.get('text') or '')
            if SOURCE_SENSE_MARKER_RE.search(text):
                report['issues'].append(_issue(
                    'SOURCE_SENSE_MARKER_LEAK', uid, f'connections[{j}].text',
                    'Dictionary/source sense markers such as [1a] are provenance locators, not learner-facing text.'
                ))
    return _finalize(report)


def _canonical_relations(unit):
    details = unit.get('details') if isinstance(unit, dict) and isinstance(unit.get('details'), dict) else {}
    rel = details.get('synonyms') if isinstance(details.get('synonyms'), list) else []
    opp = details.get('antonyms') if isinstance(details.get('antonyms'), list) else []
    return rel, opp


def validate_tsv(path, ds):
    report = base.validate_tsv(path, ds)
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    byid = {u.get('id'): u for u in ds.get('learning_units', []) if isinstance(u, dict)}
    for n, line in enumerate(lines[1:], 2):
        parts = line.split('\t')
        if len(parts) != len(base.HEADERS):
            continue
        row = dict(zip(base.HEADERS, parts))
        uid = row.get('id', f'line-{n}')
        unit = byid.get(uid)
        if not unit:
            continue
        parsed = {}
        for field in ('examples', 'related', 'opposites', 'details', 'custom_fields'):
            raw = row.get(field, '')
            # Universal TSV is raw tab-separated text. RFC4180/CSV quoting around JSON cells is not supported.
            if len(raw) >= 2 and raw.startswith('"') and raw.endswith('"'):
                report['issues'].append(_issue(
                    'TSV_CSV_QUOTING_FORBIDDEN', uid, field,
                    'Universal TSV JSON cells must not be CSV-quoted; write raw JSON between tab delimiters.'
                ))
            try:
                parsed[field] = json.loads(raw)
            except Exception:
                continue
        rel, opp = _canonical_relations(unit)
        if 'related' in parsed and parsed.get('related') != rel:
            report['issues'].append(_issue(
                'TSV_RELATION_PARITY', uid, 'related',
                'TSV related must equal canonical details.synonyms exactly.'
            ))
        if 'opposites' in parsed and parsed.get('opposites') != opp:
            report['issues'].append(_issue(
                'TSV_RELATION_PARITY', uid, 'opposites',
                'TSV opposites must equal canonical details.antonyms exactly.'
            ))
        for field in ('related', 'opposites'):
            values = parsed.get(field)
            if isinstance(values, list):
                for j, value in enumerate(values):
                    if isinstance(value, str) and SOURCE_SENSE_MARKER_RE.search(value):
                        report['issues'].append(_issue(
                            'SOURCE_SENSE_MARKER_LEAK', uid, f'{field}[{j}]',
                            'Dictionary/source sense markers such as [1a] must not enter learner-facing TSV fields.'
                        ))
        if 'details' in parsed and not isinstance(parsed.get('details'), list):
            report['issues'].append(_issue('TSV_DETAILS_SHAPE', uid, 'details', 'Runtime details must be a JSON array.'))
        if 'custom_fields' in parsed and not isinstance(parsed.get('custom_fields'), dict):
            report['issues'].append(_issue('TSV_CUSTOM_FIELDS_SHAPE', uid, 'custom_fields', 'Runtime custom_fields must be a JSON object.'))
    report['errors'] = sum(x.get('severity') == 'error' for x in report.get('issues', []))
    report['status'] = 'FAIL' if report['errors'] else 'PASS'
    report['validator'] = 'gfp-v354-universal-v2-transport'
    report['validator_version'] = '1.0.1'
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dataset')
    ap.add_argument('--tsv')
    ap.add_argument('--output')
    ns = ap.parse_args()
    ds = json.loads(Path(ns.dataset).read_text(encoding='utf-8'))
    quality = validate_dataset(ds)
    report = {'quality': quality}
    if ns.tsv:
        report['transport'] = validate_tsv(ns.tsv, ds)
    report['status'] = 'PASS' if quality['status'] == 'PASS' and report.get('transport', {'status': 'PASS'})['status'] == 'PASS' else 'FAIL'
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    print(text, end='')
    if ns.output:
        Path(ns.output).write_text(text, encoding='utf-8')
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
