#!/usr/bin/env python3
"""Source-neutral, read-only advisory QA of learner-visible related sections.

Inputs:
  TSV: id, front, details(JSON), examples(JSON), optional custom_fields(JSON).
  JSON: {"cards": [{"id", "front", "details", "examples", "canonical_relations"?}]}
        or one card object; custom_fields may contain canonical_relations,
        canonical_unit, kombinationen_v1/v336.

No source/content mutation; findings are NOT linguistic Stage4 acceptance.
Invalid data -> exit 2. Findings -> exit 0 (or exit 1 with --fail-on-high).
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

SCHEMA = 'gcpk-related-taxonomy-audit@1.1.0'
RELATED = {'Verwandt', 'Verwandte Wörter'}
ROLE_ALIASES = {
    'Verwandt': 'RELATED', 'Verwandte Wörter': 'RELATED',
    'Wortfamilie': 'WORD_FAMILY', 'Synonyme': 'SYNONYM',
    'Antonyme': 'ANTONYM', 'Kombinationen': 'COMBINATION',
    'Kollokationen': 'COMBINATION', 'Beispiele': 'EXAMPLE',
    'Redemittel': 'REDEMITTEL', 'Rektion': 'REKTION'
}
TYPED_ROUTING = {'WORD_FAMILY', 'SYNONYM', 'ANTONYM'}
OPAQUE_ID = re.compile(r'^(?:ma\dm?-?lu-\d{3,}|ma\d[a-z]*-lu-\d{3,}|gfp:[\w.:-]+)$', re.I)
SENTENCE_END = re.compile(r'[.!?…][\"\'»”)]*$')
SEVERITY_ORDER = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2, 'INFO': 3}


def unique_json_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('DUPLICATE_JSON_KEY:' + key)
        out[key] = value
    return out


def load_json(value, name):
    if isinstance(value, str):
        try:
            return json.loads(value, object_pairs_hook=unique_json_keys)
        except (ValueError, TypeError) as exc:
            raise ValueError('INVALID_JSON_' + name) from exc
    return value


def exact(value):
    """NFC/whitespace only. NO case, ß, punctuation, inflection or fuzzy folding."""
    return ' '.join(unicodedata.normalize('NFC', value).split())


def de_text(value):
    if isinstance(value, dict):
        return value.get('de', value.get('text_de', value.get('text', '')))
    if isinstance(value, str):
        # Existing learner-facing serialized bilingual details use spaced em dash.
        return value.split(' — ', 1)[0]
    return None


def content_text(value, field):
    out = de_text(value)
    if not isinstance(out, str) or not out.strip():
        raise ValueError('EMPTY_OR_INVALID_GERMAN_ITEM:' + field)
    return exact(out)


def examples_de(source):
    entries = load_json(source, 'EXAMPLES') if source is not None else []
    if not isinstance(entries, list):
        raise ValueError('EXAMPLES_NOT_LIST')
    result = []
    for entry in entries:
        if isinstance(entry, dict):
            lang = entry.get('lang', entry.get('language', 'de'))
            if lang and not str(lang).lower().startswith('de'):
                continue
        if isinstance(entry, dict):
            de = entry.get('text_de', entry.get('de', entry.get('text', '')))
        else:
            de = entry
        if isinstance(de, str) and de.strip():
            result.append(exact(de))
        elif de is not None:
            raise ValueError('EXAMPLE_GERMAN_NOT_STRING')
    return result


def normalize_card(card):
    if not isinstance(card, dict):
        raise ValueError('CARD_NOT_OBJECT')
    cid = card.get('id', card.get('card_id'))
    if not isinstance(cid, str) or not cid.strip():
        raise ValueError('MISSING_CARD_ID')
    front = card.get('front', card.get('headword', ''))
    if not isinstance(front, str):
        raise ValueError('INVALID_FRONT')
    ds = load_json(card.get('details', []), 'DETAILS')
    if not isinstance(ds, list):
        raise ValueError('DETAILS_NOT_LIST')
    cf = load_json(card.get('custom_fields', {}), 'CUSTOM_FIELDS')
    if not isinstance(cf, dict):
        raise ValueError('CUSTOM_FIELDS_NOT_OBJECT')
    rels = card.get('canonical_relations', cf.get('canonical_relations', []))
    if not isinstance(rels, list):
        raise ValueError('RELATIONS_NOT_LIST')
    for rel in rels:
        if not isinstance(rel, dict):
            raise ValueError('RELATION_NOT_OBJECT')
    cu = cf.get('canonical_unit', {})
    if not isinstance(cu, dict):
        raise ValueError('CANONICAL_UNIT_NOT_OBJECT')
    headword = cu.get('headword', front)
    if not isinstance(headword, str):
        headword = front
    combo = []
    for key in ('kombinationen_v1', 'kombinationen_v336'):
        val = cf.get(key, [])
        if isinstance(val, dict):
            val = val.get('items', [])
        if not isinstance(val, list):
            raise ValueError('INVALID_BACKEND_COMBINATIONS:' + key)
        combo.extend(content_text(v, key) for v in val)
    return {
        'id': cid, 'front': front, 'headword': headword,
        'details': ds, 'examples': examples_de(card.get('examples', [])),
        'backend_combos': combo, 'relations': rels,
    }


def load_cards(raw, suffix):
    if suffix == '.tsv':
        rdr = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''), delimiter='\t')
        fields = {'id', 'front', 'details', 'examples'}
        if not rdr.fieldnames or not fields.issubset(rdr.fieldnames):
            raise ValueError('INCOMPATIBLE_TSV_HEADER')
        cards = list(rdr)
        for row in cards:
            if None in row:
                raise ValueError('TSV_TOO_MANY_COLUMNS')
            if any(v is None for v in row.values()):
                raise ValueError('TSV_TOO_FEW_COLUMNS')
    elif suffix == '.json':
        doc = load_json(raw.decode('utf-8-sig'), 'INPUT')
        cards = doc.get('cards') if isinstance(doc, dict) and 'cards' in doc else [doc]
        if not isinstance(cards, list):
            raise ValueError('CARDS_NOT_LIST')
    else:
        raise ValueError('UNSUPPORTED_INPUT_EXTENSION')
    if not cards:
        raise ValueError('EMPTY_INPUT')
    parsed = [normalize_card(c) for c in cards]
    ids = [r['id'] for r in parsed]
    if len(ids) != len(set(ids)):
        raise ValueError('DUPLICATE_CARD_ID')
    return parsed


def audit(cards, sha256):
    """Pure deterministic diagnostic; no operation can mutate cards or source bytes."""
    byid = {card['id']: card for card in cards}
    findings = []
    related_count = 0

    def add(card_id, code, severity, value='', *, section='Verwandte Wörter', reason='', target_id=None):
        x = {'card_id': card_id, 'code': code, 'severity': severity,
             'section': section, 'value': value, 'disposition': 'REVIEW_ONLY_NO_AUTOMATIC_EDIT'}
        if reason:
            x['reason'] = reason
        if target_id:
            x['target_id'] = target_id
        findings.append(x)

    for card in cards:
        cid = card['id']
        roles = collections.defaultdict(list)
        related = []
        for section in card['details']:
            if not isinstance(section, dict):
                raise ValueError('DETAIL_SECTION_NOT_OBJECT:' + cid)
            title = section.get('title', '')
            items = section.get('items', [])
            if not isinstance(title, str) or not isinstance(items, list):
                raise ValueError('INVALID_DETAIL_SECTION:' + cid)
            role = ROLE_ALIASES.get(title)
            if not role:
                continue
            for i, item in enumerate(items):
                value = content_text(item, title)
                if role == 'RELATED':
                    related.append((title, i, value))
                roles[role].append(value)
        all_combos = {exact(x) for x in card['backend_combos']}
        all_combos.update(roles['COMBINATION'])
        example_set = set(card['examples']) | set(roles['EXAMPLE'])
        for _,_, value in related:
            related_count += 1
            if value == cid or value in byid or OPAQUE_ID.fullmatch(value):
                add(cid, 'OPAQUE_TARGET_ID_IN_RELATED', 'HIGH', value,
                    reason='Raw internal identifier cannot be learner-facing German')
                continue
            if any(ch in value for ch in ('\u200b', '\ufeff')):
                add(cid, 'INVISIBLE_FORMAT_CONTROL', 'HIGH', value)
            matches = []
            for edge in card['relations']:
                tid = edge.get('target_id')
                target = byid.get(tid)
                if not target or tid == cid:
                    continue
                typ = edge.get('relation_type', edge.get('type'))
                if typ not in TYPED_ROUTING and typ != 'RELATED':
                    continue
                if value not in {exact(target['front']), exact(target['headword'])}:
                    continue
                matches.append((typ, tid))
            kinds = {r[0] for r in matches}
            if len(kinds) > 1:
                add(cid, 'CONFLICTING_TYPED_TARGET', 'HIGH', value,
                    reason='Multiple pre-existing relationship types for exact surface; needs source/sense review')
            elif kinds and next(iter(kinds)) in TYPED_ROUTING:
                typ, tid = sorted(matches)[0]
                add(cid, 'PRETYPED_TARGET_IN_RELATED', 'MEDIUM', value,
                    reason='Candidate for existing typed section only after source/sense verification', target_id=tid)
            other = sorted(role for role in ('WORD_FAMILY', 'SYNONYM', 'ANTONYM', 'REDEMITTEL', 'REKTION')
                           if value in roles[role])
            if value in all_combos:
                other.append('COMBINATION')
            if value in example_set:
                other.append('EXAMPLE')
            if other:
                add(cid, 'RELATED_EXACT_CROSS_SECTION_DUPLICATE', 'HIGH', value,
                    reason='Same German surface in ' + ','.join(other) + '; human-approved teaching delta may allow roles')
            if len(value.split()) >= 5 and SENTENCE_END.search(value):
                add(cid, 'SENTENCE_OR_REDEMITTEL_ROLE_REVIEW', 'MEDIUM', value,
                    reason='Sentence-like surface is not sufficient to create/overwrite an example')
        counts = collections.Counter(roles['RELATED'])
        for val, n in sorted(counts.items()):
            if n > 1:
                add(cid, 'DUPLICATE_WITHIN_RELATED', 'HIGH', val,
                    reason='Same surface repeated in related sections')
        # Different German strings/cases/punctuation are not automatically the same.
    findings.sort(key=lambda x: (x['card_id'], SEVERITY_ORDER[x['severity']], x['code'], x['value']))
    return {
        'schema': SCHEMA, 'status': 'ADVISORY_READ_ONLY_NOT_STAGE4_ACCEPTANCE',
        'source_sha256': sha256, 'cards_scanned': len(cards),
        'related_items_scanned': related_count,
        'counts': dict(sorted(collections.Counter(f['code'] for f in findings).items())),
        'severity_counts': dict(sorted(collections.Counter(f['severity'] for f in findings).items())),
        'findings': findings, 'automatic_card_mutations': 0,
        'stage4_linguistic_approval': False, 'stage5_6_7_approval': False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path, help='Unchanged TSV or JSON file for read-only diagnostic')
    p.add_argument('--output', type=Path, help='Optional JSON advisory report, NOT a content file')
    p.add_argument('--fail-on-high', action='store_true', help='Optional targeted CI gate; NOT Stage4 PASS')
    a = p.parse_args(argv)
    try:
        raw = a.input.read_bytes()
        cards = load_cards(raw, a.input.suffix.lower())
        result = audit(cards, hashlib.sha256(raw).hexdigest())
        if a.output:
            a.output.parent.mkdir(parents=True, exist_ok=True)
            a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'schema': SCHEMA, 'cards': len(cards),
                          'related_items': result['related_items_scanned'],
                          'issues': result['severity_counts'],
                          'status': result['status']}, ensure_ascii=False))
        return 1 if a.fail_on_high and result['severity_counts'].get('HIGH', 0) else 0
    except (OSError, ValueError, UnicodeError) as e:
        print('INVALID_INPUT:' + str(e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
