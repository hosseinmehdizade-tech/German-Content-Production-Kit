#!/usr/bin/env python3
"""Read-only adapter compatibility for the related taxonomy v1.1 auditor.

Supported explicit boundaries:
  --source-format universal-tsv : normal projected direct-import TSV
  --source-format normalized-json : normalized {"cards":[...]} or single card
  --source-format v411-projected : official v411 projector output JSON array
  --source-format v411-canonical : official v411 canonical JSON (via exact project())

This tool audits ONLY learner-visible details; vnext_relations/Wortnetz are
intentionally not transformed into fake learner details or graph edges.
No Stage4 approval or content writes occur. Report creation is exclusive.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load_module(path: Path, name: str):
    if not path.is_file():
        raise ValueError('MISSING_REGISTERED_PROJECTOR:' + str(path.name))
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ValueError('INVALID_PROJECTOR_MODULE')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def duplicate_safe_json(raw: bytes):
    auditor = load_module(HERE / 'audit_related_sections_taxonomy_v1_1.py', 'related_taxonomy_v11')
    return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=auditor.unique_json_keys)


def projected_to_normalized(doc):
    if not isinstance(doc, list) or not doc:
        raise ValueError('V411_PROJECTED_MUST_BE_NONEMPTY_ARRAY')
    cards = []
    ids = set()
    graph_only = 0
    for c in doc:
        if not isinstance(c, dict) or c.get('cardType') != 'de-vocabulary':
            raise ValueError('NOT_AN_OFFICIAL_V411_LEXICAL_CARD')
        if not all(k in c for k in ('id', 'front', 'details', 'examples', 'customFields')):
            raise ValueError('INCOMPLETE_V411_PROJECTED_CARD')
        cid = c['id']
        if not isinstance(cid, str) or not cid.strip() or cid in ids:
            raise ValueError('V411_DUPLICATE_OR_MISSING_CARD_ID')
        ids.add(cid)
        cf = c['customFields']
        if not isinstance(cf, dict):
            raise ValueError('V411_CUSTOM_FIELDS_NOT_OBJECT')
        if not isinstance(c['details'], list):
            raise ValueError('V411_DETAILS_NOT_LIST')
        if not isinstance(c['examples'], list):
            raise ValueError('V411_EXAMPLES_NOT_LIST')
        graph = cf.get('vnext_relations', [])
        if not isinstance(graph, list):
            raise ValueError('V411_RELATION_GROUPS_NOT_LIST')
        if any(not isinstance(g, dict) for g in graph):
            raise ValueError('V411_RELATION_GROUP_INVALID')
        if any(g.get('type') == 'RELATED' and g.get('items') for g in graph):
            graph_only += 1
        cards.append({'id': cid, 'front': c['front'], 'details': c['details'],
                      'examples': c['examples'], 'custom_fields': cf})
    return {'cards': cards}, graph_only


def load_for_audit(raw: bytes, mode: str):
    auditor = load_module(HERE / 'audit_related_sections_taxonomy_v1_1.py', 'related_taxonomy_adapter_auditor')
    if mode in ('universal-tsv', 'normalized-json'):
        suffix = '.tsv' if mode == 'universal-tsv' else '.json'
        cards = auditor.load_cards(raw, suffix)
        return auditor, cards, {'projection': 'DIRECT_EXISTING_PRESENTATION',
                                'wordnetz_graph_semantics_audited': False,
                                'coverage': 'LEARNER_VISIBLE_DETAILS_ONLY'}
    source = duplicate_safe_json(raw)
    if mode == 'v411-canonical':
        if not isinstance(source, dict) or not all(k in source for k in ('lexemes', 'senses', 'expressions')):
            raise ValueError('NOT_V411_CANONICAL_SCHEMA')
        if not isinstance(source['senses'], list) or not isinstance(source['expressions'], list):
            raise ValueError('INVALID_CANONICAL_TARGET_LIST')
        expected = [x.get('sense_id') for x in source['senses']] + [x.get('expression_id') for x in source['expressions']]
        if not expected or any(not isinstance(x, str) or not x for x in expected) or len(expected) != len(set(expected)):
            raise ValueError('DUPLICATE_OR_EMPTY_CANONICAL_TARGET_IDS')
        projector = load_module(ROOT / 'Tools' / 'project_v411_vocabulary_cards.py', 'registered_v411_projector')
        try:
            projected = projector.project(source)
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError('REGISTERED_PROJECTOR_FAILED') from exc
        if sorted(c.get('id') for c in projected) != sorted(expected):
            raise ValueError('CANONICAL_PROJECTOR_ID_PARITY_FAILURE')
    elif mode == 'v411-projected':
        projected = source
    else:
        raise ValueError('UNSUPPORTED_EXPLICIT_FORMAT')
    normalized, graph_only = projected_to_normalized(projected)
    cards = auditor.load_cards(json.dumps(normalized, ensure_ascii=False).encode('utf-8'), '.json')
    if len(cards) != len(projected):
        raise ValueError('PROJECTION_CARD_COUNT_MISMATCH')
    return auditor, cards, {'projection': 'OFFICIAL_V411_TO_READONLY_DETAILS_ADAPTER',
                            'wordnetz_graph_semantics_audited': False,
                            'wordnetz_related_graph_cards_outside_scope': graph_only,
                            'coverage': 'VISIBLE_DETAILS_ONLY_GRAPH_NOT_REINTERPRETED'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--source-format', required=True,
                        choices=['universal-tsv', 'normalized-json', 'v411-projected', 'v411-canonical'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--fail-on-high', action='store_true')
    args = parser.parse_args(argv)
    try:
        raw = args.input.read_bytes()
        auditor, cards, metadata = load_for_audit(raw, args.source_format)
        result = auditor.audit(cards, hashlib.sha256(raw).hexdigest())
        result['adapter'] = {'source_format': args.source_format, **metadata,
                             'declared_pass': False, 'source_mutated': False}
        if args.output:
            if args.output.resolve() == args.input.resolve():
                raise ValueError('OUTPUT_ALIASES_INPUT')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'status': result['status'], 'cards': len(cards),
                          'related_items': result['related_items_scanned'],
                          'issues': result['severity_counts'], 'adapter': metadata['projection']},
                         ensure_ascii=False))
        return 1 if args.fail_on_high and result['severity_counts'].get('HIGH', 0) else 0
    except (OSError, ValueError, UnicodeError) as exc:
        print('INVALID_INPUT:' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
