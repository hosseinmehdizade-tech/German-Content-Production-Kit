#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--workspace', required=True, type=Path)
    ap.add_argument('--zip', required=True, type=Path)
    ap.add_argument('--manifest', required=True, type=Path)
    ap.add_argument('--sha256s', required=True, type=Path)
    ap.add_argument('--postverify', required=True, type=Path)
    ns = ap.parse_args()
    w = ns.workspace

    members = [
        ('DIRECT-IMPORT/MENSCHEN-A2-UNIVERSAL-v2.tsv', w/'05-delivery/MENSCHEN-A2-UNIVERSAL-v2.tsv'),
        ('CANONICAL/CANONICAL-ENRICHED.json', w/'02-canonical/CANONICAL-ENRICHED.json'),
        ('CANONICAL/CANONICAL-VALIDATION.json', w/'02-canonical/CANONICAL-VALIDATION.json'),
        ('CANONICAL/NORMALIZATION-DECISIONS.json', w/'02-canonical/NORMALIZATION-DECISIONS.json'),
        ('SOURCE/SOURCE-MANIFEST.json', w/'00-source/SOURCE-MANIFEST.json'),
        ('SOURCE/SOURCE-INVENTORY.json', w/'01-inventory/SOURCE-INVENTORY.json'),
        ('SOURCE/STABLE-ID-MAP.json', w/'01-inventory/STABLE-ID-MAP.json'),
        ('SOURCE/INVENTORY-QA.json', w/'01-inventory/INVENTORY-QA.json'),
        ('EVIDENCE/EVIDENCE-INDEX.json', w/'03-evidence/EVIDENCE-INDEX.json'),
        ('QA/LINGUISTIC-QA.json', w/'04-qa/LINGUISTIC-QA.json'),
        ('QA/LEXICAL-QUALITY.json', w/'04-qa/LEXICAL-QUALITY.json'),
        ('QA/COVERAGE-REPORT.json', w/'04-qa/COVERAGE-REPORT.json'),
        ('DELIVERY/DELIVERY-VALIDATION.json', w/'05-delivery/DELIVERY-VALIDATION.json'),
        ('DELIVERY/DELIVERY-LOSS-CHECK.json', w/'05-delivery/DELIVERY-LOSS-CHECK.json'),
        ('DELIVERY/BUILD-METADATA.json', w/'05-delivery/BUILD-METADATA.json'),
        ('RUNTIME/RUNTIME-ACCEPTANCE.json', w/'06-runtime/RUNTIME-ACCEPTANCE.json'),
        ('RUNTIME/PRESENTATION-ACCEPTANCE.json', w/'06-runtime/PRESENTATION-ACCEPTANCE.json'),
        ('RUNTIME/STAGE6-PROVENANCE.json', w/'06-runtime/STAGE6-PROVENANCE.json'),
        ('AUDIT/PREVIOUS-PASS-INVALIDATION.json', w/'06-runtime/PREVIOUS-PASS-INVALIDATION.json'),
        ('BUILD/BUILD-METADATA.json', w/'07-release/BUILD-METADATA.json'),
    ]

    missing = [str(p) for _, p in members if not p.exists()]
    if missing:
        raise SystemExit('missing release payload: ' + ', '.join(missing))

    # Hard preconditions: do not package a merely present but failing artifact.
    for rel in [
        '02-canonical/CANONICAL-VALIDATION.json',
        '01-inventory/INVENTORY-QA.json',
        '04-qa/LINGUISTIC-QA.json',
        '04-qa/LEXICAL-QUALITY.json',
        '05-delivery/DELIVERY-VALIDATION.json',
        '05-delivery/DELIVERY-LOSS-CHECK.json',
        '06-runtime/RUNTIME-ACCEPTANCE.json',
        '06-runtime/PRESENTATION-ACCEPTANCE.json',
        '06-runtime/STAGE6-PROVENANCE.json',
    ]:
        obj = json.loads((w/rel).read_text(encoding='utf-8-sig'))
        status = obj.get('status') or obj.get('structural_typed_status')
        if status != 'PASS':
            raise SystemExit(f'gate not PASS: {rel}: {status!r}')
    runtime = json.loads((w/'06-runtime/RUNTIME-ACCEPTANCE.json').read_text(encoding='utf-8'))
    if runtime.get('import_state') != 'IMPORT_VERIFIED' or runtime.get('persistence') != 'reload-survived':
        raise SystemExit('runtime evidence is not IMPORT_VERIFIED + reload-survived')

    payload = [{'path': arc, 'size': p.stat().st_size, 'sha256': sha256(p)} for arc, p in members]
    manifest = {
        'artifact_type': 'gfp-content-release-manifest',
        'manifest_version': '1.1.0',
        'dataset': 'menschen-a2',
        'title': 'Menschen A2',
        'cards': 292,
        'source_rows': 297,
        'runtime': 'German Flashcards Pro v354',
        'runtime_commit': '49a28187e82734e92bc407276eb0d2ee0cbbbd55',
        'runtime_sha256': runtime.get('runtime_sha256'),
        'semantic_contract': 'gfp-german-language-content@3.1.3',
        'delivery_profile': 'flashcards-pro-universal-v2@1.0.1',
        'direct_import_sha256': sha256(w/'05-delivery/MENSCHEN-A2-UNIVERSAL-v2.tsv'),
        'canonical_sha256': sha256(w/'02-canonical/CANONICAL-ENRICHED.json'),
        'stage6_import_state': runtime.get('import_state'),
        'payload': payload,
    }
    ns.manifest.parent.mkdir(parents=True, exist_ok=True)
    ns.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    ns.zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ns.zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for arc, p in members:
            z.write(p, arc)
        z.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        z.writestr('README.txt',
                   'Menschen A2 — German Flashcards Pro v354\n'
                   'Direct import file: DIRECT-IMPORT/MENSCHEN-A2-UNIVERSAL-v2.tsv\n'
                   'Canonical source of truth: CANONICAL/CANONICAL-ENRICHED.json\n'
                   'Runtime acceptance: RUNTIME/RUNTIME-ACCEPTANCE.json\n')

    # First post-package pass. A second independent verifier is mandatory in CI.
    problems = []
    with zipfile.ZipFile(ns.zip, 'r') as z:
        names = set(z.namelist())
        for arc, p in members:
            if arc not in names:
                problems.append(f'missing {arc}')
                continue
            data = z.read(arc)
            if hashlib.sha256(data).hexdigest() != sha256(p):
                problems.append(f'hash mismatch {arc}')
            if len(data) != p.stat().st_size:
                problems.append(f'size mismatch {arc}')
        try:
            embedded = json.loads(z.read('MANIFEST.json').decode('utf-8'))
            if embedded != manifest:
                problems.append('embedded manifest mismatch')
        except Exception as exc:
            problems.append('manifest parse: ' + str(exc))
        tsv_lines = z.read('DIRECT-IMPORT/MENSCHEN-A2-UNIVERSAL-v2.tsv').decode('utf-8-sig').splitlines()
        if len(tsv_lines) - 1 != 292:
            problems.append(f'TSV row count {len(tsv_lines)-1}')
        try:
            can = json.loads(z.read('CANONICAL/CANONICAL-ENRICHED.json').decode('utf-8'))
            if len(can.get('learning_units', [])) != 292:
                problems.append('canonical count mismatch')
        except Exception as exc:
            problems.append('canonical parse: ' + str(exc))

    post = {
        'status': 'PASS' if not problems else 'FAIL',
        'verifier': 'package_release_corrective.py internal post-close verification',
        'zip': ns.zip.name,
        'zip_sha256': sha256(ns.zip),
        'verified_payload_files': len(members),
        'tsv_rows': 292,
        'canonical_units': 292,
        'problems': problems,
    }
    ns.postverify.write_text(json.dumps(post, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sums = [f'{sha256(ns.zip)}  {ns.zip.name}'] + [f"{x['sha256']}  {x['path']}" for x in payload]
    ns.sha256s.write_text('\n'.join(sums) + '\n', encoding='utf-8')
    print(json.dumps(post, ensure_ascii=False, indent=2))
    return 0 if post['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
