#!/usr/bin/env python3
"""Pre-status evidence gate: never confuse newest observed working with accepted baseline.

This tool validates supplied provider observations; it does NOT crawl private providers.
A passing gate means the claim matches the byte-checked observed candidates, not
that unlisted files are impossible. Run only after enumerating live provider files.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = 'gcpk-status-currentness-evidence@1'
PROVIDERS = ('conversation', 'library', 'google_drive', 'github')
HEX64 = re.compile(r'^[0-9a-f]{64}$')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as file:
        for block in iter(lambda: file.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def evaluate(doc, base):
    errors, holds, warnings = [], [], []
    if doc.get('schema') != SCHEMA or not doc.get('workstream'):
        errors.append('SCHEMA_OR_WORKSTREAM_INVALID')
    observations = doc.get('provider_observations', {})
    for name in PROVIDERS:
        entry = observations.get(name)
        if not isinstance(entry, dict) or entry.get('status') not in ('checked', 'unavailable'):
            holds.append('PROVIDER_NOT_RECONCILED:' + name)
        elif entry.get('status') == 'unavailable':
            if not entry.get('reason'):
                errors.append('UNAVAILABLE_WITHOUT_REASON:' + name)
            holds.append('PROVIDER_UNAVAILABLE:' + name)
        elif not entry.get('locator'):
            holds.append('PROVIDER_CHECK_UNGROUNDED:' + name)
    artifacts = doc.get('artifacts')
    if not isinstance(artifacts, list) or not artifacts:
        errors.append('NO_ARTIFACT_CANDIDATES')
        artifacts = []
    ids, inspected = set(), {}
    for a in artifacts:
        if not isinstance(a, dict):
            errors.append('INVALID_ARTIFACT_RECORD')
            continue
        aid, role = a.get('id'), a.get('role')
        if not isinstance(aid, str) or not aid or aid in ids:
            errors.append('DUPLICATE_OR_MISSING_ARTIFACT_ID:' + str(aid))
            continue
        ids.add(aid)
        if role not in ('working', 'accepted', 'historical'):
            errors.append('INVALID_ROLE:' + aid)
        if not a.get('locator') or not a.get('provider'):
            holds.append('MISSING_ARTIFACT_PROVENANCE:' + aid)
        expected = str(a.get('sha256', ''))
        if not HEX64.fullmatch(expected):
            errors.append('INVALID_SHA256:' + aid)
            continue
        p = a.get('path')
        if p:
            path = Path(p)
            if not path.is_absolute():
                path = (base / path).resolve()
            if not path.is_file():
                holds.append('BYTE_SOURCE_UNAVAILABLE:' + aid)
                continue
            got = sha256(path)
            if got != expected:
                errors.append('BYTE_HASH_MISMATCH:' + aid)
                continue
            expected_cards = a.get('expected_cards')
            if expected_cards is not None:
                try:
                    data = json.loads(path.read_text(encoding='utf-8-sig'))
                    cards = data if isinstance(data, list) else data.get('cards')
                    if not isinstance(cards, list) or len(cards) != expected_cards:
                        errors.append('CARD_COUNT_MISMATCH:' + aid)
                    elif len({c.get('id') for c in cards}) != len(cards):
                        errors.append('DUPLICATE_CARD_IDS:' + aid)
                except (ValueError, TypeError, UnicodeError, AttributeError):
                    errors.append('CARD_JSON_INVALID:' + aid)
            inspected[aid] = 'BYTE_VERIFIED'
        else:
            inspected[aid] = 'METADATA_ONLY'
            if role == 'working':
                holds.append('WORKING_CANDIDATE_NOT_BYTE_VERIFIED:' + aid)
    claims = doc.get('claims', {})
    chosen = {}
    for role, claim_key in (('working', 'current_working_id'), ('accepted', 'accepted_baseline_id')):
        items = [a for a in artifacts if isinstance(a, dict) and a.get('role') == role]
        active = [a for a in items if a.get('active') is True]
        if len(active) != 1:
            holds.append('AMBIGUOUS_' + role.upper() + '_SELECTION')
        else:
            selected = active[0]['id']
            if role == 'working':
                for candidate in items:
                    if candidate.get('id') != selected and candidate.get('superseded_by') != selected:
                        holds.append('UNRESOLVED_COMPETING_WORKING:' + str(candidate.get('id')))
            chosen[role] = selected
            if claims.get(claim_key) != selected:
                errors.append('STALE_' + claim_key.upper() + ':claimed=' + str(claims.get(claim_key)) + ':observed=' + selected)
            if role == 'working' and inspected.get(selected) != 'BYTE_VERIFIED':
                holds.append('ACTIVE_WORKING_NOT_BYTE_VERIFIED:' + selected)
            if role == 'accepted' and inspected.get(selected) != 'BYTE_VERIFIED':
                warnings.append('ACCEPTED_BASELINE_PRIOR_RECEIPT_ONLY:' + selected)
    status = 'FAIL_STALE_OR_CORRUPT' if errors else 'HOLD_INCOMPLETE_EVIDENCE' if holds else 'PASS_OBSERVED_STATUS_CLAIM'
    return {'schema': 'gcpk-status-currentness-gate-result@1', 'workstream': doc.get('workstream'),
            'status': status, 'selected': chosen, 'byte_evidence': inspected,
            'errors': errors, 'holds': holds, 'warnings': warnings,
            'scope_limit': 'Observed artifacts only; no private provider discovery is performed by this script.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest', type=Path)
    args = ap.parse_args()
    result = evaluate(json.loads(args.manifest.read_text(encoding='utf-8')), args.manifest.parent)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS_OBSERVED_STATUS_CLAIM' else 2


if __name__ == '__main__':
    sys.exit(main())
