#!/usr/bin/env python3
"""OP-02: read-only, source-pinned triage of Stage5->Stage6 PENDING items.

Checks exact German-text occurrences in pre-existing detail sections and selected
source TSV text columns. A text hit is NOT evidence of learner-visible bilingual
rendering or an authorized editorial disposition. No content/runtime mutation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

from audit_op02_stage5_source_to_view import digest, TSV_MEMBER
from build_op02_visibility_review_queue import build_queue, canonical

SCHEMA = 'gcpk-op02-source-display-route-triage@1'
TEXT_COLUMNS = ('front', 'back', 'examples', 'related', 'opposites', 'notes')
BLOCKED = 'BLOCKED_SOURCE_ONLY_ROUTE_TRIAGE_NOT_NATIVE_STAGE6'


def classify(original_archive: Path, expected_archive_sha256: str, queue: dict) -> dict:
    source_queue = build_queue(original_archive, expected_archive_sha256)
    if canonical(queue) != canonical(source_queue):
        raise ValueError('UNTRUSTED_QUEUE_OR_SOURCE_FINGERPRINT_DRIFT')
    with zipfile.ZipFile(original_archive) as z:
        rows = list(csv.DictReader(io.StringIO(z.read(TSV_MEMBER).decode('utf-8-sig'), newline=''), delimiter='\t'))
    if len(rows) != source_queue['counts']['cards']:
        raise ValueError('SOURCE_ROW_COUNT_DRIFT')
    by_id = {row['id']: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError('DUPLICATE_SOURCE_CARD_ID')
    cases = []
    route_hits = {name: 0 for name in TEXT_COLUMNS}
    other_section_hits = 0
    any_text_hits = 0
    both_hits = 0
    no_alternative = 0
    for item in source_queue['items']:
        card_id, de = item['card_id'], item['de']
        if card_id not in by_id:
            raise ValueError('UNRESOLVED_CARD_ABSENT_FROM_SOURCE:' + card_id)
        row = by_id[card_id]
        text_hits = [name for name in TEXT_COLUMNS if de in row.get(name, '')]
        other_hits = item['other_detail_sections_exact_de']
        if not isinstance(other_hits, list):
            raise ValueError('INVALID_PREEXISTING_DETAIL_SECTIONS')
        for name in text_hits:
            route_hits[name] += 1
        other_section_hits += bool(other_hits)
        any_text_hits += bool(text_hits)
        both_hits += bool(other_hits) and bool(text_hits)
        if not other_hits and not text_hits:
            route = 'PRIORITY_EXACT_DE_NOT_IN_ALTERNATE_SCANNED_FIELDS'
            no_alternative += 1
        elif other_hits and text_hits:
            route = 'EXACT_DE_IN_OTHER_DETAILS_AND_OTHER_TEXT'
        elif other_hits:
            route = 'EXACT_DE_IN_OTHER_DETAILS_ONLY'
        else:
            route = 'EXACT_DE_IN_OTHER_TEXT_ONLY'
        cases.append({
            'card_id': card_id,
            'lesson': item['lesson'],
            'ordinal': item['ordinal'],
            'source_unit_sha256': item['source_unit_sha256'],
            'source_item_id': item['source_item_id'],
            'de': de,
            'fa': item['fa'],
            'en': item['en'],
            'unresolved_category': item['review_category'],
            'source_only_route': route,
            'other_details_exact_de': other_hits,
            'other_tsv_text_columns_containing_de': text_hits,
            'native_current_runtime_verified': False,
            'bilingual_display_verified': False,
            'editorial_intent_verified': False,
        })
    if len(cases) != source_queue['counts']['unresolved_items']:
        raise ValueError('TRIAGE_LOST_PENDING_UNITS')
    if (other_section_hits + any_text_hits - both_hits + no_alternative) != len(cases):
        raise ValueError('NONDISJOINT_ROUTE_COUNTS')
    return {
        'schema': SCHEMA,
        'status': BLOCKED,
        'scope': 'READ_ONLY_SOURCE_TEXT_OCCURRENCE_NOT_STAGE5_6_7_APPROVAL',
        'source': source_queue['source'],
        'source_pending_queue_items_sha256': source_queue['item_list_sha256'],
        'counts': {
            'units': len(cases),
            'affected_cards': len({c['card_id'] for c in cases}),
            'other_details_exact_de': other_section_hits,
            'any_other_tsv_text_columns_containing_de': any_text_hits,
            'overlap_other_details_and_tsv_text': both_hits,
            'no_alternative_exact_de_in_scanned_fields': no_alternative,
            'per_text_column_hits': route_hits,
            'partial_conflict_no_alternative': sum(c['unresolved_category']=='EXISTING_PARTIAL_SECTION_CONFLICT' and
                                                   c['source_only_route'].startswith('PRIORITY_') for c in cases),
            'bridge_candidate_no_alternative': sum(c['unresolved_category']=='AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF' and
                                                   c['source_only_route'].startswith('PRIORITY_') for c in cases),
        },
        'highest_priority': [c for c in cases if c['source_only_route'].startswith('PRIORITY_')],
        'cases_sha256': digest(canonical(cases)),
        'cases': cases,
        'limitations': [
            'A source-column substring match or other-details DE match is NOT bilingual or runtime visibility proof',
            'Only selected textual columns are scanned; inflection/aliases/semantically equivalent expressions are not inferred',
            'Original V22 card content remains immutable; no disposition assigned to any of 105 units',
            'Exact CURRENT runtime ZIP, isolated native import, Study/Quick DOM, independent semantic review remain pending',
            'This does not approve Stage5/Stage6/Stage7, release, a new writer scope or UI changes',
        ],
    }


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip', type=Path, required=True)
    p.add_argument('--zip-sha256', required=True)
    p.add_argument('--queue', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a=p.parse_args(argv)
    if a.output.resolve() in {a.zip.resolve(),a.queue.resolve()} or a.output.exists():
        print(json.dumps({'status':'BLOCKED','error':'WRITE_ONCE_OUTPUT_NOT_ALLOWED'}))
        return 2
    try:
        queue=json.loads(a.queue.read_text('utf8'))
        result=classify(a.zip,a.zip_sha256,queue)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x',encoding='utf8') as f:
            f.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'status':BLOCKED,'counts':result['counts'],'output_sha256':digest(a.output.read_bytes())},ensure_ascii=False))
        return 2   # Valid report, but no Stage6 evidence: always fail-closed
    except (ValueError,TypeError,KeyError,OSError,zipfile.BadZipFile,UnicodeError) as exc:
        print(json.dumps({'status':'BLOCKED','error':str(exc)},ensure_ascii=False))
        return 2

if __name__=='__main__':
    sys.exit(main())