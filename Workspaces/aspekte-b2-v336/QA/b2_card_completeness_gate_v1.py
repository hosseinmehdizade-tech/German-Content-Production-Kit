#!/usr/bin/env python3
"""Aspekte B2 user-confirmed 2026-11-21 completeness gate. Read-only.

Strict fail-closed verification of declared content coverage. This does not prove
German linguistic naturalness, source attribution, or app import safety.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

FACETS = {
    'synonyms': ['synonyms_de_sense_scoped', 'synonyms_de_proposed'],
    'antonyms': ['antonyms_de_sense_scoped', 'antonyms_de_proposed'],
    'word_family': ['word_family_de_proposed'],
    'related_words': ['related_words_de_proposed'],
    'combinations': ['collocations_de'],
}
CLOSED = {'VERIFIED_PRESENT', 'CLOSED_NO_FORCE', 'NOT_APPLICABLE'}
PLACEHOLDERS = {'', '-', '—', '?', 'n/a', 'none', 'null', 'todo', 'pending'}

def good(value):
    return str(value or '').strip().casefold() not in PLACEHOLDERS

def normal(value):
    return ' '.join(re.findall(r'\w+', str(value).casefold(), re.UNICODE))

def inspect(path):
    raw = Path(path).read_bytes()
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        columns = reader.fieldnames or []
        rows = list(reader)
    errors = Counter()
    samples = []
    ids = set()
    for index, row in enumerate(rows, start=1):
        cid = row.get('unit_id') or row.get('id') or f'row_{index}'
        def flag(key, detail=''):
            errors[key] += 1
            if len(samples) < 40:
                samples.append({'card': cid, 'issue': key, 'detail': detail})
        if not good(cid) or cid in ids:
            flag('MISSING_OR_DUPLICATE_CARD_ID')
        ids.add(cid)
        if not good(row.get('front_de_preview') or row.get('front')):
            flag('MISSING_GERMAN_HEADWORD')
        if not good(row.get('back_fa_preview') or row.get('back')):
            flag('MISSING_PERSIAN_MEANING')
        if not good(row.get('english_gloss')):
            flag('MISSING_ENGLISH_WORD_GLOSS')
        examples = []
        for n in range(1, 5):
            de, fa, en = (row.get(f'example_{n}_{lang}', '') for lang in ('de', 'fa', 'en'))
            if not good(de): flag(f'MISSING_EXAMPLE_{n}_DE')
            if not good(fa): flag(f'MISSING_EXAMPLE_{n}_FA')
            if not good(en): flag(f'MISSING_EXAMPLE_{n}_EN')
            if good(de): examples.append(normal(de))
        if len(examples) != len(set(examples)):
            flag('DUPLICATE_GERMAN_EXAMPLES')
        for facet, source_columns in FACETS.items():
            status = row.get(f'{facet}_review_status', '').strip().upper()
            items = [x.strip() for key in source_columns for x in row.get(key, '').split(';') if good(x)]
            if status not in CLOSED:
                flag('FACET_NOT_REVIEWED', facet)
            elif status == 'VERIFIED_PRESENT' and not items:
                flag('FACET_VERIFIED_BUT_NO_CONTENT', facet)
            elif status != 'VERIFIED_PRESENT':
                if items:
                    flag('FACET_CLOSED_BUT_CONTENT_PRESENT', facet)
                if not good(row.get(f'{facet}_review_reason')):
                    flag('FACET_CLOSURE_REASON_MISSING', facet)
        combos = [c.strip() for c in row.get('collocations_de', '').split(';') if good(c)]
        if combos and row.get('combinations_independence_review', '').strip().upper() != 'CONFIRMED_INDEPENDENT':
            flag('COMBINATIONS_NOT_CONFIRMED_INDEPENDENT_OF_EXAMPLES')
        if len({normal(c) for c in combos}) != len(combos):
            flag('DUPLICATE_COMBINATIONS_ON_CARD')
        for combo in combos:
            if normal(combo) in examples:
                flag('COMBINATION_EQUALS_WHOLE_EXAMPLE', combo)
        # Deliberately DO NOT fail merely because a valid collocation is used
        # as a substring within a legitimate German example sentence.
    if len(rows) != 1719:
        errors['WRONG_CARD_COUNT'] += 1
    return {'contract':'aspekte-b2-user-confirmed-completeness@2026-11-21',
            'status':'PASS' if not errors else 'FAIL',
            'input_sha256':hashlib.sha256(raw).hexdigest(),
            'cards':len(rows),'unique_card_ids':len(ids),
            'expected_examples_per_card':4,
            'required_example_languages':['de','fa','en'],
            'required_word_gloss_language':'en',
            'required_facet_statuses':list(FACETS),
            'errors_by_class':dict(errors),'sample_issues':samples,
            'nonclaims':['NOT_A_LINGUISTIC_SEMANTICS_CERTIFICATION','NOT_APP_IMPORT_VERIFIED']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('master_tsv')
    args = parser.parse_args()
    result = inspect(args.master_tsv)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)