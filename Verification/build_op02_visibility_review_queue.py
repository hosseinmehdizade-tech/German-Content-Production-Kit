#!/usr/bin/env python3
"""NONACTIVE OP-02: derive exact, PENDING-only Stage5->Stage6 reviewer queue.

Reads immutable Stage5 ZIP once through the existing fail-closed Stage5 source
scanner; does not alter learner content, import, or decide semantic correctness.
No stage acceptance, runtime validation, trusted reviewer signoff or writer grant.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

from audit_op02_stage5_source_to_view import (
    audit_archive, digest, _ledger, _rows, TSV_MEMBER, LEDGER_MEMBER,
)

SCHEMA = 'gcpk-op02-stage6-visibility-handoff-queue@1'
PENDING = 'PENDING_SEMANTIC_AND_EXACT_CURRENT_RUNTIME_REVIEW'
CATEGORIES = {
    'AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF': 'STAGE6_CONSUMER_BRIDGE_REQUIRED',
    'EXISTING_PARTIAL_SECTION_CONFLICT': 'STAGE5_SOURCE_BOUND_PLACEMENT_AND_STAGE6_REQUIRED',
    'LEGACY_LIST_NO_SECTION_REVIEW': 'STAGE5_LEGACY_PLACEMENT_AND_STAGE6_REQUIRED',
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def build_queue(zip_path: Path, exact_sha256: str):
    scanned = audit_archive(zip_path, exact_sha256)
    if scanned['status'] not in {
        'BLOCKED_VIEW_COVERAGE_REQUIRES_DISPOSITION__LEDGER_PARITY_PASS',
        'PASS_SCOPED_LEDGER_AND_DETAILS_PARITY__NOT_RUNTIME',
    }:
        raise ValueError('UNEXPECTED_STAGE5_AUDIT_STATUS')
    with zipfile.ZipFile(zip_path) as z:
        tsv_bytes = z.read(TSV_MEMBER)
        ledger_bytes = z.read(LEDGER_MEMBER)
    rows = _rows(tsv_bytes)
    records = _ledger(ledger_bytes)
    if len(rows) != len(records):
        raise ValueError('ROW_LEDGER_LENGTH_MISMATCH')
    accepted = {r['card_id']: r for r in records}
    rawrows = {r['id']: r for r in rows}
    units = []
    unique = set()
    for group in scanned['affected']:
        cid,lesson,category=group['id'],group['lesson'],group['category']
        if category not in CATEGORIES:
            raise ValueError('UNRECOGNIZED_REVIEW_CATEGORY:' + category)
        if cid not in accepted or cid not in rawrows:
            raise ValueError('AUDIT_REFERENCES_UNKNOWN_CARD:' + cid)
        raw = rawrows[cid]
        if lesson != accepted[cid]['lesson'] or lesson != raw['lesson']:
            raise ValueError('AUDIT_LESSON_DRIFT:' + cid)
        for item in group['unaccounted_items']:
            ordinal = item['ordinal']
            originals = accepted[cid]['items']
            if type(ordinal) is not int or ordinal < 0 or ordinal >= len(originals):
                raise ValueError('AUDIT_ITEM_ORDINAL_INVALID:' + cid)
            origin = originals[ordinal]
            if any(origin.get(lang) != item[lang] for lang in ('de','fa','en')):
                raise ValueError('AUDIT_ITEM_TEXT_NOT_BOUND:' + cid)
            key = (cid,ordinal)
            if key in unique:
                raise ValueError('DUPLICATE_AUDIT_UNIT:' + cid)
            unique.add(key)
            source = {'card_id':cid,'lesson':lesson,'ordinal':ordinal,'accepted_item':origin}
            units.append({
                'card_id':cid,
                'lesson':lesson,
                'ordinal':ordinal,
                'source_item_id':item.get('item_id'),  # null where historical source has no ID
                'source_unit_sha256':digest(canonical(source)),
                'de':item['de'],'fa':item['fa'],'en':item['en'],
                'expected_bilingual_text':item['de'].strip()+' — '+item['fa'].strip(),
                'review_category':category,
                'review_priority':1 if category=='EXISTING_PARTIAL_SECTION_CONFLICT' else 2,
                'other_detail_sections_exact_de':item['other_detail_sections_exact_de'],
                'review_status':PENDING,
                'runtime_evidence':None,
                'source_semantic_evidence':None,
                'independent_adversarial_evidence':None,
                'auto_edit_authorized':False,
            })
    # Keep original scanner's source/card order. Do not change UI-order claims.
    if len(units) != scanned['counts']['unaccounted_items']:
        raise ValueError('AUDIT_UNACCOUNTED_UNIT_TOTAL_MISMATCH')
    if len({x['card_id'] for x in units}) != len(scanned['affected']):
        raise ValueError('AUDIT_AFFECTED_CARD_TOTAL_MISMATCH')
    if len(units)+scanned['counts']['physical_matched_items']!=scanned['counts']['accepted_items']:
        raise ValueError('AUDIT_COVERAGE_SUM_MISMATCH')
    # Output is a work queue, NEVER a PASS/approval receipt. Runtime authority
    # is deliberately not hard-coded; CURRENT must be re-resolved live at Stage6.
    return {
        'schema':SCHEMA,
        'status':'BLOCKED_PENDING_INDEPENDENT_ITEM_AND_CURRENT_RUNTIME_EVIDENCE',
        'scope':'NONACTIVE_DIAGNOSTIC_NOT_STAGE5_6_7_ACCEPTANCE',
        'source':{
            'stage5_zip_sha256':exact_sha256,
            'stage5_import_tsv_sha256':digest(tsv_bytes),
            'accepted_ledger_sha256':digest(ledger_bytes),
            'stage5_scanner_status':scanned['status'],
        },
        'runtime':{
            'current_authority':'German-Flashcards-Pro/RUNTIME-AUTHORITY-PIN.json',
            'resolve_current_fresh_at_validation':True,
            'exact_current_zip_verified':False,
            'native_import_study_quick_evidence':'NOT_RUN',
            'release_final':False,
        },
        'counts':{
            'cards':len(rows),
            'accepted_items':scanned['counts']['accepted_items'],
            'physical_details_matched_items':scanned['counts']['physical_matched_items'],
            'unresolved_cards':len(scanned['affected']),
            'unresolved_items':len(units),
            'bridge_candidate_items':sum(x['review_category']=='AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF' for x in units),
            'partial_section_conflict_items':sum(x['review_category']=='EXISTING_PARTIAL_SECTION_CONFLICT' for x in units),
            'legacy_list_review_items':sum(x['review_category']=='LEGACY_LIST_NO_SECTION_REVIEW' for x in units),
        },
        'required_evidence_before_any_promotion':[
            'Re-resolve newest CURRENT app version, full ZIP and index.html exact SHA256',
            'Exact source-item SHA and original source/Stage4 reviewer rationale where ambiguity exists',
            'Native import and Study/Quick actual display on exact CURRENT isolated profile',
            'Document intended section or deliberate omission with distinct cited source/method',
            'Independent adversarial verification of source+runtime disposition',
            'Re-run full formal Stage5 and separate Stage6/7 gates, no implied PASS',
        ],
        'item_list_sha256':digest(canonical(units)),
        'items':units,
    }


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip',required=True,type=Path)
    p.add_argument('--sha256',required=True)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args(argv)
    if args.output.resolve()==args.zip.resolve():
        print(json.dumps({'status':'BLOCKED','error':'OUTPUT_CANNOT_OVERWRITE_SOURCE'}))
        return 2
    if args.output.exists():
        print(json.dumps({'status':'BLOCKED','error':'OUTPUT_ALREADY_EXISTS_WRITE_ONCE'}))
        return 2
    try:
        result=build_queue(args.zip,args.sha256)
        payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        # Exclusive create, no overwrites, never touch the source ZIP.
        with args.output.open('x',encoding='utf-8') as f:
            f.write(payload)
        print(json.dumps({'status':result['status'],'unresolved':result['counts']['unresolved_items'],
                          'queue_sha256':digest(payload.encode('utf-8'))},ensure_ascii=False))
        return 2  # generated queue is NOT Stage6 PASS; fail closed if reused as a gate
    except (ValueError,TypeError,KeyError,OSError,zipfile.BadZipFile,UnicodeError) as exc:
        print(json.dumps({'status':'BLOCKED','error':str(exc)},ensure_ascii=False))
        return 2

if __name__=='__main__':
    raise SystemExit(main())