#!/usr/bin/env python3
"""Read-only, fail-closed Aspekte B2 cross-level identity preflight.

Analyses local, user-provided JSON export or v471 forensic archive. NEVER writes to
an application profile, IndexedDB, localStorage, or an input file. Forensic/legacy
records are observations, not a current active runtime attestation.

This script deliberately never approves or imports B2 learner cards.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import pathlib
import re
import sys
from collections import Counter

SCHEMA = 'aspekte-b2-readonly-srs-id-preflight@1.0.0'
KNOWN_TYPES = {'KEEP_STANDALONE_B2', 'HOLD_B1_USAGE_ENRICHMENT_LINK',
               'HOLD_A2_ENRICHMENT_OR_B2_FALLBACK', 'KEEP_NONCARD_CONDITIONAL_B1_REUSE'}
ID_PATTERN = re.compile(r'^(?:mb1m-lu-\d+|ma2m-lu-\d+|ab2-l\d+-u-\d+)$')
MAX_JSON_BYTES = 150 * 1024 * 1024


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def json_file(path: pathlib.Path):
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError('Evidence exceeds 150MiB safety ceiling')
    with path.open(encoding='utf-8-sig') as f:
        return json.load(f)


def extract_records(obj):
    """Return claimed IDs and whether SRS state is present in the given payload.

    Do not traverse arbitrary nested JSON (avoids mistaking historical/deleted
    backups for the active card collection).
    """
    rows = []
    if not isinstance(obj, dict):
        return rows, 'UNRECOGNIZED'
    cards = obj.get('cards')
    if isinstance(cards, list):
        for c in cards:
            if isinstance(c, dict) and isinstance(c.get('id'), str):
                rows.append((c['id'], c, 'EXPORT_CARDS_LIST'))
        return rows, 'CARDS_LIST' if rows else 'EMPTY_CARDS_LIST'
    if isinstance(cards, dict):
        for key, val in cards.items():
            if isinstance(key, str) and isinstance(val, dict):
                rows.append((key, val, 'PROGRESS_CARDS_MAP'))
        return rows, 'PROGRESS_MAP' if rows else 'EMPTY_PROGRESS_MAP'
    store = obj.get('store')
    if isinstance(store, dict):
        return extract_records(store)
    return [], 'UNRECOGNIZED'


def gather_evidence(obj):
    """Fail-closed inventory. Forensic archive contains ALL browser stores,
    including obsolete/recovery data. Only gfp_progress_v8 is inspected and is
    marked as a LEGACY_PROGRESS_CACHE, never current accepted-card proof.
    """
    if not isinstance(obj, dict):
        raise ValueError('Evidence must be a JSON object')
    if isinstance(obj.get('payload'), dict) and ('databases' in obj['payload'] or 'localStorage' in obj['payload']):
        payload = obj['payload']
        cache = None
        loc = payload.get('localStorage', [])
        if isinstance(loc, list):
            for row in loc:
                if isinstance(row, (list, tuple)) and len(row) == 2 and row[0] == 'gfp_progress_v8' and isinstance(row[1], str):
                    try:
                        cache = json.loads(row[1])
                    except (ValueError, TypeError):
                        pass
        records, parse = extract_records(cache)
        return records, {
            'format': 'GFP_V471_FORENSIC_ARCHIVE', 'record_source': 'LEGACY_LOCALSTORAGE_PROGRESS_CACHE',
            'parsing': parse, 'trust': 'NOT_LIVE_ACTIVE_ATTESTATION',
            'idb_databases_present': len(payload.get('databases', [])) if isinstance(payload.get('databases'), list) else None,
            'idb_not_interpreted_without_ACTIVE_GENERATION_PROOF': True,
            'caution': 'Forensic payload may preserve orphaned, deleted or historical cards.'
        }
    recs, parse = extract_records(obj)
    return recs, {
        'format': 'USER_PROVIDED_CARD_OR_STATE_JSON', 'record_source': parse,
        'parsing': parse, 'trust': 'UNAUTHENTICATED_FILE_SNAPSHOT_NOT_LIVE_APP_PROOF',
        'idb_not_interpreted_without_ACTIVE_GENERATION_PROOF': True,
        'caution': 'File existence does not establish active/current browser identity.'
    }


def looks_like_srs(record):
    # Presence-only, intentionally never reveal raw review history or due dates.
    return any(key in record for key in ('reviews', 'reps', 'lapses', 'stability', 'difficulty', 'due', 'dueDate', 'lastReview', 'history'))


def read_matrix(path: pathlib.Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if len(rows) != 7 or len(set(x.get('source_ordinal', '') for x in rows)) != 7:
        raise ValueError('Expected the exact seven reviewed L01 crosslevel entries')
    if any(x['nonmutating_decision'] not in KNOWN_TYPES for x in rows):
        raise ValueError('Unexpected editorial decision; source review is required')
    if sum(x['b2_current_record_type'] == 'NONCARD_REUSE_SIDECAR' for x in rows) != 1:
        raise ValueError('Expected one noncard conditional B1 reuse sidecar')
    expected_ordinals = {'1556','1575','1609','1616','1630','1671','1697'}
    if {x['source_ordinal'] for x in rows} != expected_ordinals:
        raise ValueError('Unexpected lesson-one crosslevel source ordinals')
    if any(r.get('approved_for_import') != 'NO' or
           r.get('live_app_card_identity_observed') != 'NO' or
           r.get('live_srs_snapshot_observed') != 'NO' for r in rows):
        raise ValueError('Crosslevel matrix must remain NONIMPORT and unverified')
    return rows


def make_report(matrix: pathlib.Path, l01: pathlib.Path, evidence: pathlib.Path | None, expected_sha: str):
    source_sha = sha(l01)
    if expected_sha and source_sha != expected_sha:
        raise ValueError('Current L01 file checksum does not match pinned GitHub RUN-CONTROL')
    rows = read_matrix(matrix)
    if any(r.get('b2_current_source_sha256') != source_sha for r in rows):
        raise ValueError('Crosslevel review matrix refers to different L01 file bytes')
    with l01.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {'unit_id','source_ordinals','export_importable','linguistic_release_approved'} <= set(reader.fieldnames):
            raise ValueError('L01 is not the expected curated learner draft schema')
        cards = list(reader)
    if len(cards) != 158:
        raise ValueError('L01 158-card source row count has drifted')
    units = [r['unit_id'] for r in cards]
    if len(set(units)) != 158 or any(r['export_importable'].upper() != 'FALSE' or
                                    r['linguistic_release_approved'].upper() != 'FALSE' for r in cards):
        raise ValueError('L01 ID uniqueness or NONIMPORT safety gate violated')
    by_id = {r['unit_id']:r for r in cards}
    for r in rows:
        ident = r['b2_current_record_id']
        if r['b2_current_record_type'] == 'CARD_DRAFT':
            if ident not in by_id or r['source_ordinal'] not in by_id[ident]['source_ordinals'].split(';'):
                raise ValueError('Crosslevel draft does not match current L01 ID and source ordinal: '+ident)
        elif r['b2_current_record_type'] == 'NONCARD_REUSE_SIDECAR':
            if ident in by_id:
                raise ValueError('NONCARD reuse ID appears as an importable L01 draft: '+ident)
    recs, evidence_context = ([], {'format':'NO_USER_EVIDENCE', 'record_source':'NONE',
                                   'trust':'NONE', 'caution':'No user/browser export was provided.'})
    e_sha = None
    if evidence:
        if evidence.resolve() in (l01.resolve(), matrix.resolve()):
            raise ValueError('Evidence input must not be source CSV')
        e_sha = sha(evidence)
        recs, evidence_context = gather_evidence(json_file(evidence))
        if evidence_context['parsing'] == 'UNRECOGNIZED':
            raise ValueError('Unsupported export structure; cannot infer card absence from this file')
    counter = Counter(k for k, _, _ in recs)
    unique_id_set = set(counter)
    duplicates = sorted(k for k,v in counter.items() if v > 1)
    observations = {}
    for ident, card, src in recs:
        if ident not in observations:
            observations[ident] = {'srs_fields_present': looks_like_srs(card), 'source_type': src}
        else:
            observations[ident]['srs_fields_present'] |= looks_like_srs(card)
    output=[]
    for row in rows:
        refs = [q.strip() for q in row.get('documented_prior_reference_ids','').split(';') if q.strip()]
        supported_refs = [q for q in refs if ID_PATTERN.fullmatch(q)]
        observed=[ident for ident in supported_refs if ident in unique_id_set]
        present_srs=[ident for ident in observed if observations[ident]['srs_fields_present']]
        observed_b2 = row.get('b2_current_record_id') in unique_id_set
        output.append({
            'source_ordinal':row['source_ordinal'], 'lemma':row['b2_lemma'],
            'b2_record_type':row['b2_current_record_type'],
            'b2_draft_id':row['b2_current_record_id'],
            'editorial_decision_unchanged':row['nonmutating_decision'],
            'documented_prior_reference_ids':refs,
            'prior_IDs_observed_in_supplied_file':observed,
            'prior_IDs_with_SRS_fields_in_supplied_file':present_srs,
            'b2_draft_ID_observed_in_supplied_file':observed_b2,
            'live_accepted_identity_verified':False,
            'live_SRS_state_verified':False,
            'provisional_category':('EVIDENCE_FILE_CONTAINS_CANDIDATE_IDS__NATIVE_PROOF_PENDING'
                if observed else 'NO_SAME_ID_EVIDENCE_IN_PROVIDED_FILE'),
            'publication_approval':'BLOCKED_NONIMPORT'
        })
    summary={
        'cases':len(output), 'B2_draft_cases':sum(x['b2_record_type']=='CARD_DRAFT' for x in output),
        'conditional_noncard_cases':sum(x['b2_record_type']=='NONCARD_REUSE_SIDECAR' for x in output),
        'observed_referenced_prior_ids_in_file':len(set(y for x in output for y in x['prior_IDs_observed_in_supplied_file'])),
        'observed_prior_ids_with_SRS_fields_in_file':len(set(y for x in output for y in x['prior_IDs_with_SRS_fields_in_supplied_file'])),
        'duplicate_evidence_file_card_ids':len(duplicates),
        'live_accepted_card_IDs_verified':0,
        'live_SRS_identity_verified':0,
        'cards_approved_for_import':0,
        'SRS_mutations':0,
        'source_card_mutations':0
    }
    report={
        'schema':SCHEMA, 'operation':'READ_ONLY_LOCAL_FILE_PREFLIGHT',
        'source_sha256':source_sha, 'source_filename':l01.name,
        'matrix_sha256':sha(matrix), 'evidence_file_sha256':e_sha,
        'evidence':evidence_context, 'summary':summary,
        'rows':output,
        'external_gates':{'independent_DE_FA_linguistic_signoff':False,
            'browser_current_active_generation_attested':False,
            'native_import_persistence_and_rollback_verified':False},
        'status':'BLOCKED_NONIMPORT',
        'privacy':'No raw SRS values, card text, browser URLs or raw evidence payload emitted.',
        'limitations':['An offline input cannot prove current active browser generation by itself.',
            'GFP v471 forensic archives contain recovery and historical stores: presence is not acceptance.',
            'A prior B1/A2 word occurrence is not same card identity or same learning sense.',
            'No automatic ID reuse, deletion, merge, or import is authorized.']
    }
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix', type=pathlib.Path, required=True)
    parser.add_argument('--l01-current', type=pathlib.Path, required=True)
    parser.add_argument('--expected-l01-sha256', default='')
    parser.add_argument('--evidence-json',type=pathlib.Path,help='Optional user-exported JSON/forensic archive; never uploads it')
    parser.add_argument('--out-dir',type=pathlib.Path,required=True)
    args=parser.parse_args(argv)
    try:
        result=make_report(args.matrix,args.l01_current,args.evidence_json,args.expected_l01_sha256)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print('SAFE_FAIL: '+str(exc),file=sys.stderr)
        return 3
    args.out_dir.mkdir(parents=True,exist_ok=True)
    dst=args.out_dir/'B2-L01-SRS-IDENTITY-READONLY-RESULT.json'
    dst.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    csvfile=args.out_dir/'B2-L01-SRS-IDENTITY-READONLY-RESULT.csv'
    with csvfile.open('w',encoding='utf-8-sig',newline='') as f:
        columns=['source_ordinal','lemma','b2_record_type','editorial_decision_unchanged',
                 'documented_prior_reference_ids','prior_IDs_observed_in_supplied_file',
                 'prior_IDs_with_SRS_fields_in_supplied_file','live_accepted_identity_verified','publication_approval']
        writer=csv.DictWriter(f,columns,extrasaction='ignore')
        writer.writeheader()
        for row in result['rows']:
            item=dict(row)
            for k in ('documented_prior_reference_ids','prior_IDs_observed_in_supplied_file',
                       'prior_IDs_with_SRS_fields_in_supplied_file'):
                item[k]='; '.join(item[k])
            writer.writerow(item)
    print('SAFE_REPORT_WRITTEN '+str(dst))
    print('STATUS BLOCKED_NONIMPORT; NO SRS MUTATIONS')
    return 2  # a nonzero status deliberately prevents any accidental release gate

if __name__=='__main__':
    sys.exit(main())
