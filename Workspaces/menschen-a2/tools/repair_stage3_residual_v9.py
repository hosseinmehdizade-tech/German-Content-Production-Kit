#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--patches', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ns = ap.parse_args()

    before_sha = sha256(ns.dataset)
    ds = load(ns.dataset)
    spec = load(ns.patches)
    units = ds.get('learning_units') or []
    by_id = {u.get('id'): u for u in units if isinstance(u, dict)}
    expected_ids = set(spec.get('items', {}))
    if expected_ids != {'ma2-lu-0050', 'ma2-lu-0157', 'ma2-lu-0247'}:
        raise SystemExit(f'unexpected residual patch IDs: {sorted(expected_ids)}')

    changes = []
    for uid, item in spec['items'].items():
        unit = by_id.get(uid)
        if not unit:
            raise SystemExit(f'missing unit {uid}')
        if unit.get('headword') != item.get('headword'):
            raise SystemExit(f'headword mismatch for {uid}: {unit.get("headword")} != {item.get("headword")}')
        examples = unit.setdefault('examples', [])
        before_count = len([x for x in examples if isinstance(x, dict) and str(x.get('text') or '').strip()])
        if before_count >= 4:
            changes.append({'id': uid, 'headword': unit.get('headword'), 'before': before_count, 'after': before_count, 'inserted': []})
            continue
        existing_text = {str(x.get('text') or '').strip() for x in examples if isinstance(x, dict)}
        inserted = []
        for text in item.get('examples', []):
            text = str(text).strip()
            if not text or text in existing_text:
                continue
            if len([x for x in examples if isinstance(x, dict) and str(x.get('text') or '').strip()]) >= 4:
                break
            next_order = max([int(x.get('order', 0)) for x in examples if isinstance(x, dict)] + [0]) + 1
            ex_id = f'{uid}-ex-{next_order:03d}'
            examples.append({'id': ex_id, 'lang': 'de-DE', 'text': text, 'order': next_order, 'translations': []})
            existing_text.add(text)
            inserted.append({'id': ex_id, 'text': text})

        after_count = len([x for x in examples if isinstance(x, dict) and str(x.get('text') or '').strip()])
        if after_count < 4:
            raise SystemExit(f'{uid} still below floor after targeted patch: {after_count}')
        if after_count > 6:
            raise SystemExit(f'{uid} exceeds product maximum after targeted patch: {after_count}')

        sources = unit.setdefault('provenance', {}).setdefault('sources', [])
        source_record = {
            'source_id': item['source_id'],
            'source_kind': item.get('source_kind', 'other'),
            'what_was_verified': ['example_attestation'],
            'verification_status': 'verified',
            'locator': item['locator'],
            'accessed_at': item['accessed_at'],
            'evidence_note': 'Targeted residual Stage 3 repair after durable v8 enrichment. Only exact externally attested German examples needed to close the remaining Product Floor gap were added; no full-source refetch and no generated fallback was used for these units.'
        }
        if not any(isinstance(s, dict) and s.get('source_id') == source_record['source_id'] and s.get('locator') == source_record['locator'] for s in sources):
            sources.append(source_record)
        changes.append({'id': uid, 'headword': unit.get('headword'), 'before': before_count, 'after': after_count, 'inserted': inserted, 'source': item['locator']})

    below = [u.get('id') for u in units if len([x for x in (u.get('examples') or []) if isinstance(x, dict) and str(x.get('text') or '').strip()]) < 4]
    if below:
        raise SystemExit(f'non-target residual units remain below four examples: {below}')

    ns.dataset.write_text(json.dumps(ds, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    after_sha = sha256(ns.dataset)
    report = {
        'status': 'PASS',
        'repair': 'menschen-a2-stage3-residual-v9',
        'policy': 'targeted-only-no-full-refetch',
        'dataset_sha256_before': before_sha,
        'dataset_sha256_after': after_sha,
        'patched_units': changes,
        'all_units_at_or_above_four_examples': True,
        'external_sources': sorted({c.get('source') for c in changes if c.get('source')})
    }
    ns.report.parent.mkdir(parents=True, exist_ok=True)
    ns.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
