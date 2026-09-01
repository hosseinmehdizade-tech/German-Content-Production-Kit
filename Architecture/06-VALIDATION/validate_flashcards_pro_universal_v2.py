from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

BASE_COLUMNS = [
    'id','card_type','domain','category','source','level','lesson','deck','front','back',
    'front_label','back_label','front_lang','back_lang','typing_target','examples','related',
    'opposites','details','custom_fields','tags','notes','order'
]

SEMANTIC_CONTRACT = 'gfp-german-language-content@3.1.3'
RUNTIME_CONTENT_CONTRACT = 'gfp-german-learning-content@1.0.0'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json_cell(value: str, expected: type, row_no: int, field: str, errors: list[str]) -> Any:
    try:
        obj = json.loads(value or ('{}' if expected is dict else '[]'))
    except Exception as exc:
        errors.append(f'row {row_no}: {field} invalid JSON: {exc}')
        return {} if expected is dict else []
    if not isinstance(obj, expected):
        errors.append(f'row {row_no}: {field} must be {expected.__name__}')
        return {} if expected is dict else []
    return obj


def validate(tsv: Path, canonical: Path | None = None, metadata: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, str]] = []
    seen: set[str] = set()

    with tsv.open('r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh, delimiter='\t')
        header = reader.fieldnames or []
        if header[:23] != BASE_COLUMNS:
            errors.append('header: first 23 columns do not exactly match Universal v2 base envelope')
        if len(header) < 23:
            errors.append(f'header: expected at least 23 columns, got {len(header)}')
        for row_no, row in enumerate(reader, start=2):
            if None in row:
                errors.append(f'row {row_no}: physical column count does not match header')
                continue
            rows.append(row)
            cid = str(row.get('id') or '').strip()
            if not cid:
                errors.append(f'row {row_no}: id is required')
            if cid in seen:
                errors.append(f'row {row_no}: duplicate id {cid}')
            seen.add(cid)
            for key in ('card_type', 'front', 'back'):
                if not str(row.get(key) or '').strip():
                    errors.append(f'row {row_no}: {key} is required')
            for key in BASE_COLUMNS:
                value = str(row.get(key) or '')
                if '\t' in value or '\n' in value or '\r' in value:
                    errors.append(f'row {row_no}: literal tab/newline in {key}')

            examples = load_json_cell(row.get('examples') or '[]', list, row_no, 'examples', errors)
            load_json_cell(row.get('related') or '[]', list, row_no, 'related', errors)
            load_json_cell(row.get('opposites') or '[]', list, row_no, 'opposites', errors)
            load_json_cell(row.get('details') or '[]', list, row_no, 'details', errors)
            custom = load_json_cell(row.get('custom_fields') or '{}', dict, row_no, 'custom_fields', errors)

            if custom:
                if custom.get('learning_unit_id') != cid:
                    errors.append(f'row {row_no}: custom_fields.learning_unit_id must equal id')
                if custom.get('german_learning_contract') != RUNTIME_CONTENT_CONTRACT:
                    errors.append(f'row {row_no}: wrong/missing german_learning_contract')
                if custom.get('semantic_contract') != SEMANTIC_CONTRACT:
                    errors.append(f'row {row_no}: wrong/missing semantic_contract')
                canonical_unit = custom.get('canonical_unit')
                if not isinstance(canonical_unit, dict):
                    errors.append(f'row {row_no}: custom_fields.canonical_unit is required and must be object')
                else:
                    if canonical_unit.get('id') != cid:
                        errors.append(f'row {row_no}: canonical_unit.id mismatch')
                    if str(row.get('front') or '') != str(canonical_unit.get('headword') or ''):
                        errors.append(f'row {row_no}: front/headword parity mismatch')
                    if str(canonical_unit.get('persian_meaning') or '') and str(row.get('back') or '') != str(canonical_unit.get('persian_meaning') or ''):
                        errors.append(f'row {row_no}: back/persian_meaning parity mismatch')
                    if custom.get('canonical_entry_type') != canonical_unit.get('type'):
                        errors.append(f'row {row_no}: canonical entry type parity mismatch')
                    if str(custom.get('german_definition') or '') != str(canonical_unit.get('definition_de') or ''):
                        errors.append(f'row {row_no}: German definition parity mismatch')
                    if str(custom.get('english') or '') != str(canonical_unit.get('english_gloss') or ''):
                        errors.append(f'row {row_no}: English gloss parity mismatch')

            for i, item in enumerate(examples, start=1):
                if not isinstance(item, dict):
                    errors.append(f'row {row_no}: example {i} must be object')
                    continue
                if not str(item.get('text') or '').strip():
                    errors.append(f'row {row_no}: example {i} text required')
                if str(item.get('role') or '') != 'example':
                    errors.append(f'row {row_no}: example {i} role must be example')
                if item.get('order') != i:
                    errors.append(f'row {row_no}: example {i} order must equal {i}')

    if canonical:
        data = json.loads(canonical.read_text(encoding='utf-8'))
        units = data.get('learning_units') or []
        if len(units) != len(rows):
            errors.append(f'row count parity: canonical={len(units)} tsv={len(rows)}')
        by_id = {u.get('id'): u for u in units}
        for i, row in enumerate(rows, start=2):
            cid = row.get('id')
            if cid not in by_id:
                errors.append(f'row {i}: id {cid} missing from canonical dataset')
                continue
            custom = json.loads(row.get('custom_fields') or '{}')
            if custom.get('canonical_unit') != by_id[cid]:
                errors.append(f'row {i}: canonical_unit is not exact deep copy of source unit')

    if metadata:
        meta = json.loads(metadata.read_text(encoding='utf-8'))
        if meta.get('artifact_type') != 'gfp-data-build-metadata':
            errors.append('metadata: artifact_type must be gfp-data-build-metadata')
        if meta.get('schema_profile') != 'universal-v2':
            errors.append('metadata: schema_profile must be universal-v2')
        if meta.get('data_file') != tsv.name:
            errors.append('metadata: data_file does not match TSV filename')
        actual = sha256_file(tsv)
        if str(meta.get('data_sha256') or '').lower() != actual:
            errors.append('metadata: data_sha256 does not match exact TSV bytes')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'transport': 'gfp-universal-card@2.0 / universal-v2',
        'runtime_content_contract': RUNTIME_CONTENT_CONTRACT,
        'semantic_contract': SEMANTIC_CONTRACT,
        'rows': len(rows),
        'errors': errors,
        'warnings': warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('tsv', type=Path)
    ap.add_argument('--canonical', type=Path)
    ap.add_argument('--metadata', type=Path)
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    result = validate(args.tsv, args.canonical, args.metadata)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(text + '\n', encoding='utf-8')
    print(text)
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
