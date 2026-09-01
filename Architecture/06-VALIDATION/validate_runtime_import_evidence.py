#!/usr/bin/env python3
"""Validate GFP runtime import evidence for Master Prompt v3.1.4."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

PACKAGE = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PACKAGE / '02-SCHEMAS' / 'RUNTIME-IMPORT-EVIDENCE-SCHEMA.json'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate(data: dict[str, Any], artifact_path: Path | None = None) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    validator = Draft202012Validator(schema)
    errors = [f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))]
    warnings: list[str] = []

    pre = data.get('preflight') or {}
    commit = data.get('commit') or {}
    reload = data.get('reload') or {}
    artifact_status = data.get('artifact_status')
    runtime_status = data.get('runtime_status')
    mode = data.get('verification_mode')

    if runtime_status in {'RUNTIME_PREFLIGHT_PASS', 'RUNTIME_BLOCKED', 'IMPORT_VERIFIED'} and not pre.get('checked'):
        errors.append('preflight.checked must be true for a claim about the current runtime')

    if runtime_status == 'RUNTIME_PREFLIGHT_PASS':
        if pre.get('pending_unverified_commit') is True:
            errors.append('RUNTIME_PREFLIGHT_PASS forbidden while pending_unverified_commit=true')
        if pre.get('existing_library_count') is None:
            errors.append('RUNTIME_PREFLIGHT_PASS requires existing_library_count evidence')

    if runtime_status == 'RUNTIME_BLOCKED':
        blocked_signals = [
            pre.get('writes_blocked') is True,
            pre.get('can_write') is False,
            pre.get('writer_authority') is False,
            pre.get('unresolved_recovery') is True,
            pre.get('pending_unverified_commit') is True,
            pre.get('runtime_mode') not in {None, 'READY'},
        ]
        if not any(blocked_signals):
            errors.append('RUNTIME_BLOCKED requires at least one concrete blocking signal')

    if runtime_status == 'IMPORT_VERIFIED':
        if artifact_status != 'APP_COMPATIBLE':
            errors.append('IMPORT_VERIFIED requires artifact_status=APP_COMPATIBLE')
        if commit.get('pre_count') is None or commit.get('post_count') is None or commit.get('expected_post_count') is None:
            errors.append('IMPORT_VERIFIED requires pre_count, post_count and expected_post_count')
        elif commit.get('post_count') != commit.get('expected_post_count'):
            errors.append('IMPORT_VERIFIED post_count must equal expected_post_count')
        if reload.get('post_reload_count') is None:
            errors.append('IMPORT_VERIFIED requires post_reload_count')
        elif commit.get('post_count') is not None and reload.get('post_reload_count') != commit.get('post_count'):
            errors.append('IMPORT_VERIFIED post_reload_count must equal committed post_count')

    if mode == 'isolated-runtime' and runtime_status != 'CURRENT_RUNTIME_NOT_VERIFIED':
        errors.append('isolated-runtime evidence cannot claim a current-runtime status')

    if artifact_path is not None:
        if not artifact_path.is_file():
            errors.append(f'artifact path does not exist: {artifact_path}')
        else:
            expected = str((data.get('artifact') or {}).get('sha256') or '').lower()
            actual = sha256_file(artifact_path)
            if expected != actual:
                errors.append(f'artifact SHA-256 mismatch: evidence={expected} actual={actual}')

    scenario_names = {s.get('name'): s for s in data.get('scenarios', []) if isinstance(s, dict)}
    if artifact_status == 'APP_COMPATIBLE':
        for name in ('ready-existing-library', 'write-blocked-fail-closed', 'reload-durability'):
            if not scenario_names.get(name, {}).get('passed'):
                errors.append(f'APP_COMPATIBLE requires passed scenario: {name}')
        if not scenario_names.get('recovery-resolved-ready-import', {}).get('passed'):
            warnings.append('APP_COMPATIBLE evidence does not include recovery-resolved-ready-import; current-runtime recovery claims remain prohibited')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'warnings': warnings,
        'artifact_status': artifact_status,
        'runtime_status': runtime_status,
        'verification_mode': mode,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('evidence', type=Path)
    ap.add_argument('--artifact', type=Path)
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    data = json.loads(args.evidence.read_text(encoding='utf-8'))
    report = validate(data, args.artifact)
    out = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(out + '\n', encoding='utf-8')
    print(out)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
