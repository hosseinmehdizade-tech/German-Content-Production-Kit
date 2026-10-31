#!/usr/bin/env python3
"""OP-02 read-only, NONACTIVE accepted-source -> TSV -> declared-view visibility audit.

No editing, no inference about learner-visible CURRENT runtime, no Stage5/6/7 approval.
Caller pins the exact whole archive SHA256; archived ledger and imported rows are
bound to the same original ZIP. All 23 Universal columns and IDs are checked.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

SCHEMA = 'gcpk-op02-nonactive-accepted-source-to-view-audit@1'
UNIVERSAL_FIELDS = ('id card_type domain category source level lesson deck front back '
                    'front_label back_label front_lang back_lang typing_target '
                    'examples related opposites details custom_fields tags notes order').split()
TSV_MEMBER = '01-Final-Import/Menschen-A1-V22-CONTENT-IMPORT.tsv'
LEDGER_MEMBER = '04-Enrichment-Work/accepted-combinations.jsonl'
SHA256_PATTERN = __import__('re').compile(r'[0-9a-f]{64}\Z')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_json(text: str):
    def pairs(p):
        out = {}
        for k, v in p:
            if k in out:
                raise ValueError('DUPLICATE_JSON_KEY:' + k)
            out[k] = v
        return out
    def nope(v):
        raise ValueError('NONFINITE_JSON:' + v)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=nope)


def _rows(tsv: bytes):
    reader = csv.DictReader(io.StringIO(tsv.decode('utf-8-sig'), newline=''), delimiter='\t')
    if reader.fieldnames != UNIVERSAL_FIELDS:
        raise ValueError('INVALID_UNIVERSAL_23_COLUMN_HEADER')
    rows = list(reader)
    if not rows or any(set(row) != set(UNIVERSAL_FIELDS) or any(not isinstance(v, str) for v in row.values()) or not row['id'] for row in rows):
        raise ValueError('INVALID_UNIVERSAL_ROWS')
    ids = [r['id'] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError('DUPLICATE_TSV_CARD_ID')
    return rows


def _ledger(data: bytes):
    lines = data.decode('utf-8').splitlines()
    if not lines or any(not ln for ln in lines):
        raise ValueError('EMPTY_OR_BLANK_LEDGER')
    records = [strict_json(ln) for ln in lines]
    if any(not isinstance(v, dict) or set(v) != {'card_id', 'items', 'lesson'} or not isinstance(v['items'], list) or not isinstance(v['card_id'], str) for v in records):
        raise ValueError('INVALID_ACCEPTED_LEDGER_SCHEMA')
    ids = [v['card_id'] for v in records]
    if len(set(ids)) != len(ids):
        raise ValueError('DUPLICATE_LEDGER_ID')
    return records


def _view_item_parts(value):
    if not isinstance(value, dict):
        raise ValueError('INVALID_ACCEPTED_ITEM')
    if not isinstance(value.get('de'), str) or not value['de'].strip() or not isinstance(value.get('fa'), str) or not isinstance(value.get('en'), str):
        raise ValueError('INVALID_ACCEPTED_ITEM_LANGUAGE')
    return value['de'].strip(), value['fa'].strip(), value['en'].strip()


def _matches(item, v):
    de, fa, en = _view_item_parts(item)
    if isinstance(v, dict):
        return v.get('de') == de and v.get('fa') == fa and (not en or v.get('en') == en)
    if isinstance(v, str):
        alternatives = {de, de + ' — ' + fa}
        if fa and en:
            alternatives.add(de + ' — ' + fa + ' — ' + en)
        return v.strip() in alternatives
    raise ValueError('INVALID_DETAIL_ITEM_TYPE')


def _physical(details):
    if not isinstance(details, list) or any(not isinstance(v, dict) or not isinstance(v.get('title'), str) or not isinstance(v.get('items'), list) for v in details):
        raise ValueError('MALFORMED_DETAILS')
    combo_sections = [section for section in details if section['title'] == 'Kombinationen']
    if len(combo_sections) > 1:
        raise ValueError('DUPLICATE_KOMBINATIONEN_SECTION')
    return combo_sections[0]['items'] if combo_sections else [], details


def audit(tsv: bytes, ledger: bytes) -> dict:
    rows, records = _rows(tsv), _ledger(ledger)
    if len(rows) != len(records) or [r['id'] for r in rows] != [rec['card_id'] for rec in records]:
        raise ValueError('ROW_LEDGER_ID_OR_ORDER_MISMATCH')
    counts = collections.Counter()
    affected = []
    for row, rec in zip(rows, records):
        card_id = row['id']
        if rec['lesson'] != row['lesson']:
            raise ValueError('SOURCE_LESSON_DRIFT:' + card_id)
        custom, details = strict_json(row['custom_fields']), strict_json(row['details'])
        if not isinstance(custom, dict) or 'kombinationen_v1' not in custom:
            raise ValueError('MISSING_TYPED_KOMBINATIONEN_VIEW:' + card_id)
        view = custom['kombinationen_v1']
        if isinstance(view, list):
            items = view
            shape = 'legacy_list'
            selector = None
        elif isinstance(view, dict):
            items = view.get('items')
            selector = view.get('visible_section')
            shape = 'object'
            if selector != 'Kombinationen' and (items or selector not in (None, '')):
                raise ValueError('INVALID_VISIBLE_SECTION_SELECTOR:' + card_id)
        else:
            raise ValueError('INVALID_VIEW_ENVELOPE:' + card_id)
        if not isinstance(items, list) or items != rec['items']:
            raise ValueError('LEDGER_TO_VIEW_BYTE_SEMANTIC_PARITY_FAILED:' + card_id)
        ids = [item.get('id', item.get('item_id')) if isinstance(item, dict) else None for item in items]
        nonempty_ids = [v for v in ids if v is not None]
        if any(not isinstance(v, str) or not v.strip() for v in nonempty_ids) or len(set(nonempty_ids)) != len(nonempty_ids):
            raise ValueError('MALFORMED_OR_DUPLICATE_EXPLICIT_ITEM_IDS:' + card_id)
        physical, all_details = _physical(details)
        used = set()
        missing = []
        for ordinal, item in enumerate(items):
            de, fa, en = _view_item_parts(item)
            found = next((i for i, v in enumerate(physical) if i not in used and _matches(item, v)), None)
            if found is not None:
                used.add(found)
                continue
            elsewhere = []
            for section in all_details:
                if section['title'] == 'Kombinationen':
                    continue
                if any((isinstance(v, str) and v.strip() == de) or
                       (isinstance(v, dict) and v.get('de') == de)
                       for v in section['items']):
                    elsewhere.append(section['title'])
            missing.append({'item_id': item.get('id', item.get('item_id')), 'ordinal': ordinal, 'de': de,
                            'fa': fa, 'en': en, 'other_detail_sections_exact_de': sorted(set(elsewhere))})
        counts['cards'] += 1
        counts['accepted_items'] += len(items)
        counts['physical_matched_items'] += len(used)
        counts['view_envelope_' + shape] += 1
        if missing:
            category = 'AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF' if not physical and shape == 'object' else 'EXISTING_PARTIAL_SECTION_CONFLICT'
            if not physical and shape == 'legacy_list':
                category = 'LEGACY_LIST_NO_SECTION_REVIEW'
            counts['items_' + category] += len(missing)
            counts['cards_' + category] += 1
            affected.append({'id': card_id, 'lesson': row['lesson'], 'category': category,
                             'unaccounted_items': missing})
        else:
            counts['cards_ALL_ITEMS_IN_DECLARED_DETAILS'] += 1
    counts['unaccounted_items'] = counts['accepted_items'] - counts['physical_matched_items']
    return {'schema': SCHEMA,
            'status': ('PASS_SCOPED_LEDGER_AND_DETAILS_PARITY__NOT_RUNTIME' if not affected else
                       'PASS_SCOPED_LEDGER_PARITY__VIEW_COVERAGE_REVIEW_REQUIRED__NOT_STAGE6'),
            'counts': dict(sorted(counts.items())), 'affected': affected,
            'not_proven': ['independent Stage4 linguistic approval', 'intent of other detail sections',
                           'real CURRENT v503 Study/Quick rendering', 'full Stage5, Stage6 or Stage7 acceptance']}


def audit_archive(path: Path, expected_archive_sha256: str) -> dict:
    if not SHA256_PATTERN.fullmatch(expected_archive_sha256):
        raise ValueError('EXTERNAL_PIN_NOT_SHA256')
    blob = path.read_bytes()
    if digest(blob) != expected_archive_sha256:
        raise ValueError('EXACT_ARCHIVE_SHA256_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        if len(set(z.namelist())) != len(z.namelist()) or z.testzip() is not None:
            raise ValueError('DUPLICATE_OR_CRC_BAD_ARCHIVE')
        direct, accepted = z.read(TSV_MEMBER), z.read(LEDGER_MEMBER)
    result = audit(direct, accepted)
    result['input_sha256'] = {'archive': digest(blob), 'tsv': digest(direct), 'accepted_ledger': digest(accepted)}
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--zip', required=True, type=Path)
    ap.add_argument('--sha256', required=True)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    try:
        result = audit_archive(args.zip, args.sha256)
        if args.output:
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        print(json.dumps({'status': result['status'], 'counts': result['counts'], 'archive_sha256': result['input_sha256']['archive']}, ensure_ascii=False))
        return 0 if result['status'].startswith('PASS_SCOPED') else 2
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'status':'BLOCKED', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())