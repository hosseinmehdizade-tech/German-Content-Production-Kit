#!/usr/bin/env python3
"""Read-only, source-independent QA for lexical relation sections in JSON/TSV.
Legacy prose is advisory; invalid explicit structured records are blocking.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys
from pathlib import Path

KINDS = {
    'synonyms': 'synonyms', 'synonyme': 'synonyms',
    'antonyms': 'antonyms', 'antonyme': 'antonyms',
    'related_words': 'related_words', 'verwandte wörter': 'related_words',
    'verwandte woerter': 'related_words',
    'wortfamilie': 'word_family', 'word_family': 'word_family'
}
REQUIRED = {'kind', 'term_de', 'translation_fa', 'display_item', 'review_status'}
FA = re.compile(r'[\u0600-\u06ff\u0750-\u077f]')
INLINE_NOTE = re.compile(r'\([^()]{10,}\)\s*[—–]\s*')
OPAQUE_ID = re.compile(r'^(?:ma\dm-lu-|(?:target|sense|expr)_[a-z0-9_-]{8,})', re.I)

def load_rows(path):
    if path.suffix.lower() == '.json':
        root = json.loads(path.read_text(encoding='utf-8-sig'))
        return root.get('cards', []) if isinstance(root, dict) else root
    if path.suffix.lower() == '.tsv':
        with path.open(encoding='utf-8-sig', newline='') as fh:
            return list(csv.DictReader(fh, delimiter='\t'))
    raise ValueError('Expected JSON or TSV projection')

def parsed(value, default):
    if value is None or value == '':
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default

def kind_of(value):
    return KINDS.get(re.sub(r'[\s_-]+', ' ', str(value or '').strip().lower()))

def audit(path, sample_limit=30):
    rows = load_rows(path)
    issues = []
    counts = {'synonyms':0, 'antonyms':0, 'related_words':0, 'word_family':0}
    def flag(code, cid, kind, example='', severity='ADVISORY'):
        issues.append({'code':code, 'severity':severity, 'card_id':cid, 'kind':kind,
                       'example':str(example)[:250]})
    for n, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            flag('CARD_NOT_OBJECT', f'row:{n}', '', severity='BLOCKER')
            continue
        cid = str(row.get('id') or f'row:{n}')
        details = parsed(row.get('details'), [])
        if isinstance(details, dict):
            details = [{'title':k, 'items':v} for k,v in details.items()]
        if not isinstance(details, list):
            details = []
        visible = {}
        for section in details:
            if not isinstance(section, dict):
                continue
            kind = kind_of(section.get('title', ''))
            if kind is None:
                continue
            items = section.get('items', section.get('values', []))
            if not isinstance(items, list):
                items = [items]
            visible.setdefault(kind, [])
            for item in items:
                counts[kind] += 1
                if isinstance(item, dict):
                    flag('TYPED_RECORD_IN_LEGACY_DETAILS', cid, kind, item, 'BLOCKER')
                    continue
                raw = str(item or '').strip()
                visible[kind].append(raw)
                if OPAQUE_ID.search(raw):
                    flag('OPAQUE_RELATION_ID_VISIBLE', cid, kind, raw)
                if INLINE_NOTE.search(raw):
                    flag('LEGACY_INLINE_GERMAN_SENSE_NOTE', cid, kind, raw)
                if FA.search(raw) and not any(sep in raw for sep in ('—', '–')):
                    flag('BILINGUAL_NO_EXPLICIT_SPLIT', cid, kind, raw)
                if not FA.search(raw):
                    flag('PERSIAN_TRANSLATION_NOT_VISIBLE', cid, kind, raw)
        cf = parsed(row.get('customFields', row.get('custom_fields')), {})
        if not isinstance(cf, dict):
            flag('CUSTOM_FIELDS_NOT_OBJECT', cid, '', severity='BLOCKER')
            continue
        sidecar = cf.get('lexical_relations_v1', {})
        if sidecar in (None, {}):
            continue
        if not isinstance(sidecar, dict):
            flag('SIDECAR_NOT_OBJECT', cid, '', sidecar, 'BLOCKER')
            continue
        for kind, records in sidecar.items():
            if kind not in counts:
                flag('UNKNOWN_RELATION_KIND', cid, kind, kind, 'BLOCKER')
                continue
            if not isinstance(records, list):
                flag('SIDECAR_NOT_ARRAY', cid, kind, records, 'BLOCKER')
                continue
            seen = set()
            for record in records:
                if not isinstance(record, dict):
                    flag('RELATION_NOT_OBJECT', cid, kind, record, 'BLOCKER')
                    continue
                missing = [k for k in REQUIRED if not str(record.get(k, '')).strip()]
                if missing:
                    flag('REQUIRED_FIELDS_MISSING', cid, kind, missing, 'BLOCKER')
                    continue
                if record.get('kind') != kind:
                    flag('RELATION_KIND_CONFLICT', cid, kind, record, 'BLOCKER')
                lemma = str(record['term_de']).strip()
                gloss = str(record['translation_fa']).strip()
                display = str(record['display_item']).strip()
                if OPAQUE_ID.search(lemma):
                    flag('TECHNICAL_ID_AS_LEMMA', cid, kind, lemma, 'BLOCKER')
                if not FA.search(gloss):
                    flag('TRANSLATION_NOT_PERSIAN', cid, kind, gloss, 'BLOCKER')
                if any(x in lemma + display for x in '<>'):
                    flag('RAW_HTML_IN_LEXICAL_ITEM', cid, kind, display, 'BLOCKER')
                if lemma not in display or gloss not in display:
                    flag('PROJECTION_MISMATCH', cid, kind, display, 'BLOCKER')
                if visible.get(kind) and display not in visible[kind]:
                    flag('EXACT_DISPLAY_ITEM_NOT_PROJECTED', cid, kind, display, 'BLOCKER')
                identity = (lemma, record.get('sense_key', ''))
                if identity in seen:
                    flag('DUPLICATE_SAME_SENSE', cid, kind, lemma, 'BLOCKER')
                seen.add(identity)
    blockers = sum(i['severity'] == 'BLOCKER' for i in issues)
    advisories = sum(i['severity'] == 'ADVISORY' for i in issues)
    codes = {c:sum(i['code'] == c for i in issues) for c in sorted(set(i['code'] for i in issues))}
    return {
        'schema':'gcpk-global-lexical-relation-audit@1.0.0',
        'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'status':'BLOCKED_STRUCTURAL' if blockers else 'PASS_STRUCTURAL',
        'cards':len(rows), 'relation_entries':sum(counts.values()), 'by_kind':counts,
        'issue_counts':{'BLOCKER':blockers, 'ADVISORY':advisories},
        'issue_codes':codes, 'sample_issues':issues[:sample_limit],
        'scope':'READ_ONLY_NOT_STAGE4_5_6_7',
        'note':'Advisories require source/sense review, never automatic rewrite.'
    }

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('projection', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--strict-legacy', action='store_true')
    args = p.parse_args(argv)
    result = audit(args.projection)
    if args.output:
        if args.output.resolve() == args.projection.resolve():
            raise ValueError('Refusing input overwrite')
        if args.output.exists():
            raise FileExistsError('Output must be write-once')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result['status'] != 'PASS_STRUCTURAL' or (
        args.strict_legacy and result['issue_counts']['ADVISORY']) else 0

if __name__ == '__main__':
    sys.exit(main())
