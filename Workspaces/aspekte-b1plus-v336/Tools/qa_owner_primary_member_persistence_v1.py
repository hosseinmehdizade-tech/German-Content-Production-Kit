#!/usr/bin/env python3
"""Fail-closed persistence gate. Compare saved ZIP primary card bytes, never sidecars alone.

This prevents the L04 Phase2 v1 defect: audit sidecars showed 62 changes while the
primary 1571-card learner-data JSONL in the ZIP was byte-identical to its parent.

Usage: python qa_owner_primary_member_persistence_v1.py parent.zip child.zip --lesson L04 --expected-changed 62
"""
import argparse
import hashlib
import json
import sys
import zipfile

MAIN = 'G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP = 'G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'

def sha(value):
    return hashlib.sha256(value).hexdigest()

def verified_members(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None, 'ZIP_CRC_FAIL'
        files = {n: z.read(n) for n in z.namelist() if n != 'SHA256SUMS.txt'}
        manifest = {name: digest for digest, name in (
            row.split('  ', 1) for row in z.read('SHA256SUMS.txt').decode().splitlines() if row
        )}
        assert set(files) == set(manifest), 'ZIP_MEMBER_MANIFEST_MISMATCH'
        assert all(sha(value) == manifest[name] for name, value in files.items()), 'ZIP_HASH_MISMATCH'
        return files

def check(parent, child, lesson, claimed):
    a, b = verified_members(parent), verified_members(child)
    assert a[MAP] == b[MAP], 'SOURCE_MAP_CHANGED'
    old = [json.loads(row) for row in a[MAIN].splitlines()]
    new = [json.loads(row) for row in b[MAIN].splitlines()]
    assert len(old) == len(new) == 1571, 'GLOBAL_CARD_COUNT_CHANGED'
    assert len({c['preview_card_id'] for c in new}) == len(new), 'DUPLICATE_CARD_ID'
    assert [c['preview_card_id'] for c in old] == [c['preview_card_id'] for c in new], 'CARD_IDS_CHANGED'
    assert [c['linked_original_source_ordinals'] for c in old] == [
        c['linked_original_source_ordinals'] for c in new], 'SOURCE_LINKS_CHANGED'
    assert all(x == y for x, y in zip(old, new) if x['lesson'] != lesson), 'NON_LESSON_CARD_CHANGED'
    actual = sum(x != y for x, y in zip(old, new))
    assert actual == claimed, f'CLAIMED_{claimed}_ACTUAL_{actual}'
    if claimed:
        assert a[MAIN] != b[MAIN], 'MAIN_JSONL_WAS_NOT_PERSISTED'
    return {
        'result': 'PASS',
        'lesson': lesson,
        'claimed_changed_cards': claimed,
        'persisted_changed_cards': actual,
        'parent_main_sha256': sha(a[MAIN]),
        'child_main_sha256': sha(b[MAIN]),
        'original_map_sha256': sha(a[MAP]),
        'zip_manifest_and_crc': 'PASS',
        'non_lesson_cards_preserved': True
    }

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('parent')
    p.add_argument('child')
    p.add_argument('--lesson', required=True)
    p.add_argument('--expected-changed', required=True, type=int)
    args = p.parse_args()
    try:
        print(json.dumps(check(args.parent, args.child, args.lesson, args.expected_changed), indent=2))
    except (AssertionError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(json.dumps({'result': 'FAIL', 'error': str(exc)}))
        sys.exit(1)
