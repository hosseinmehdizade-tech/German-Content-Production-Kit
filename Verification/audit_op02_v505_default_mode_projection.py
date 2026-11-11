#!/usr/bin/env python3
"""Nonactive v505 source-pinned Study/Quick default-mode projection audit.

Models only the currently verified static projector and declared default ordering.
Never claims actual imported browser/DOM visibility or user override state.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import pathlib
import zipfile
from build_op02_visibility_review_queue import build_queue

CURRENT_APP_SHA = '0b7358d2755a80d1563e5b4791f62ec72c6a42279914739d551aef1f4d2a0ea5'
CURRENT_PROJECTOR_SHA = '51645e4cfafabcd0370d2659ca75ef5b83bc3ad53049a262a396ba397bcfc378'
ORIGINAL_ZIP_SHA = '74cdbf5b6d0121421fac8235124e738929b9764f3696db532cc54f9509f5757d'
ORIGINAL_TSV_SHA = '024ee77efbb3675a0720491af1da2286e2186bd00bc83bcbb9dfef22b0656c9a'
TSV_MEMBER = '01-Final-Import/Menschen-A1-V22-CONTENT-IMPORT.tsv'
DEFAULT_ORDER = ('english', 'features', 'combinations', 'grammar', 'forms', 'variants', 'rection', 'structure', 'synonyms', 'antonyms', 'word_family', 'collocations', 'function', 'register', 'notes', 'custom')
SHA256 = lambda b: hashlib.sha256(b).hexdigest()


def canonical_unit_parseable(custom):
    # v505 parseCanonicalUnitCandidateV348 requires an object with examples array.
    c = custom.get('canonical_unit') or custom.get('canonicalUnit')
    if isinstance(c, str):
        try:c=json.loads(c)
        except json.JSONDecodeError:return False
    if isinstance(c, dict) and isinstance(c.get('examples'), list):return True
    for name in ('german_content_v313', 'german_content_v312'):
        env=custom.get(name)
        if isinstance(env,dict) and isinstance(env.get('unit'),dict) and isinstance(env['unit'].get('examples'),list):return True
    return False


def classify_case(row, item, category):
    custom=json.loads(row['custom_fields']);sections=json.loads(row['details'])
    kv=custom.get('kombinationen_v1')
    if not isinstance(kv,dict) or str(kv.get('visible_section','')).strip().casefold()!='kombinationen':
        raise ValueError('UNEXPECTED_CURRENT_BRIDGE_SCHEMA:'+row['id'])
    combo=[s for s in sections if s['title']=='Kombinationen']
    if len(combo)>1:raise ValueError('DUPLICATE_SECTION:'+row['id'])
    if not isinstance(kv.get('items'),list):raise ValueError('MISSING_BRIDGE_ITEMS:'+row['id'])
    if category=='AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF':
        if combo and combo[0]['items']:raise ValueError('EXPECTED_EMPTY_KOMBINATIONEN:'+row['id'])
        # v505 presentationProjectedDetailsV459 generates a section from kv.items.
        status='DEFAULT_SOURCE_MODEL_BRIDGE_GENERATED_NOT_DOM_VERIFIED'
    elif category=='EXISTING_PARTIAL_SECTION_CONFLICT':
        if not combo or not combo[0]['items']:raise ValueError('EXPECTED_PARTIAL_SECTION:'+row['id'])
        # v505 early return if existing section has any items, ignores missing kv items.
        status='DEFAULT_SOURCE_MODEL_MISSING_FROM_COMBINATIONS'
    else:raise ValueError('UNKNOWN_CATEGORY:'+category)
    return status


def audit(zip_path, queue_path):
    zbytes=pathlib.Path(zip_path).read_bytes()
    if SHA256(zbytes)!=ORIGINAL_ZIP_SHA:raise ValueError('EXACT_V22_ARCHIVE_SHA_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        if z.testzip() is not None:raise ValueError('ARCHIVE_CRC_BAD')
        tsv=z.read(TSV_MEMBER)
    if SHA256(tsv)!=ORIGINAL_TSV_SHA:raise ValueError('EXACT_V22_TSV_SHA_MISMATCH')
    rows=list(csv.DictReader(io.StringIO(tsv.decode('utf-8-sig'),newline=''),delimiter='\t'))
    byid={r['id']:r for r in rows}
    if len(rows)!=2997 or len(byid)!=len(rows):raise ValueError('ORIGINAL_CARD_COUNT_DRIFT')
    q=json.loads(pathlib.Path(queue_path).read_text(encoding='utf8'))
    # Reject a swapped or fabricated pending-case file even with plausible top-level counts.
    regenerated=build_queue(pathlib.Path(zip_path),ORIGINAL_ZIP_SHA)
    if q!=regenerated:raise ValueError('PENDING_QUEUE_NOT_SOURCE_EXACT_REGENERATED')
    if q.get('source',{}).get('stage5_zip_sha256')!=ORIGINAL_ZIP_SHA or q.get('counts',{}).get('unresolved_items')!=105:
        raise ValueError('QUEUE_IDENTITY_MISMATCH')
    items=q.get('items')
    if not isinstance(items,list) or len(items)!=105:raise ValueError('QUEUE_LENGTH_MISMATCH')
    if len({v.get('source_unit_sha256') for v in items})!=105:raise ValueError('QUEUE_DUPLICATE_SOURCE_UNITS')
    summary=collections.Counter();cases=[]
    for case in items:
        cid=case['card_id'];row=byid.get(cid)
        if row is None or row['lesson']!=case['lesson']:raise ValueError('SOURCE_CARD_MISSING_OR_LESSON_DRIFT:'+cid)
        category=case['review_category'];status=classify_case(row,case,category)
        summary[status]+=1
        cases.append({'card_id':cid,'lesson':case['lesson'],'source_unit_sha256':case['source_unit_sha256'],'ordinal':case['ordinal'],
                      'de':case['de'],'class':category,'source_model':status,'default_study_section':'combinations',
                      'default_quick_section':'combinations' if status=='DEFAULT_SOURCE_MODEL_BRIDGE_GENERATED_NOT_DOM_VERIFIED' else 'partial_combinations_only',
                      'native_dom':'NOT_RUN','user_presentation_overrides':'UNKNOWN','editorial_disposition':'PENDING'})
    legacy=collections.Counter();example_legacy=[]
    for r in rows:
        c=json.loads(r['custom_fields']);kv=c.get('kombinationen_v1')
        if not isinstance(kv,list) or not kv:continue
        legacy['nonempty_legacy_list_cards']+=1;legacy['nonempty_legacy_list_items']+=len(kv)
        if canonical_unit_parseable(c):
            legacy['canonical_unit_with_valid_examples']+=1
            example_legacy.append(r['id'])
        else: legacy['canonical_unit_incomplete_generic_fallback_candidates']+=1
    if summary['DEFAULT_SOURCE_MODEL_BRIDGE_GENERATED_NOT_DOM_VERIFIED']!=57 or summary['DEFAULT_SOURCE_MODEL_MISSING_FROM_COMBINATIONS']!=48:
        raise ValueError('UNEXPECTED_V22_PROJECTOR_CLASSIFICATION_COUNTS')
    if legacy['nonempty_legacy_list_cards']!=119 or legacy['nonempty_legacy_list_items']!=302:
        raise ValueError('LEGACY_COHORT_COUNT_DRIFT')
    return {'schema':'gfp-op02-v505-default-mode-static-audit@1','status':'PASS_SCOPED_EXACT_V505_DEFAULT_SOURCE_ROUTE__NATIVE_STAGE6_BLOCKED',
            'authority':{'app_component_sha256':CURRENT_APP_SHA,'projector_function_sha256':CURRENT_PROJECTOR_SHA,
                         'stage5_source_zip_sha256':ORIGINAL_ZIP_SHA,'stage5_tsv_sha256':ORIGINAL_TSV_SHA},
            'default_contract':{'ranked_first_three':list(DEFAULT_ORDER[:3]),'quick_details':'collapsed:first_three','study_details':'full',
                                'hidden_sections':'not supplied by embedded contract; possible user override','source':['verified-v505-app-blob','embeddedPresentationContractV339','presentationDetailSectionsV339','presentationProjectedDetailsV459']},
            'counts':{'cases':len(cases),**dict(summary),**dict(legacy)},'legacy_parseable_canonical_cards':example_legacy,
            'conditional':{'bridge_57':'Available in default Study and Quick model when user overrides do not hide the combinations section; not DOM proof',
                            'partial_48':'Missing specific source items from projected Kombinationen section; other card sections/UI remain separate question',
                            'legacy_302':'Legacy list is not automatically invisible; original canonical_unit requires an examples array to override physical Details and that condition is tested independently'},
            'not_proven':['whole original v505 ZIP SHA recomputation','actual browser/DOM and user settings','correct semantic/editorial grouping','formal full Stage5','Stage6','Stage7','release FINAL'],
            'cases':cases}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zip',required=True);ap.add_argument('--queue',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();target=pathlib.Path(a.output)
    if target.exists() or target.resolve() in (pathlib.Path(a.zip).resolve(),pathlib.Path(a.queue).resolve()):
        raise SystemExit('BLOCKED_WRITE_ONCE')
    try:r=audit(a.zip,a.queue)
    except Exception as e:print(json.dumps({'status':'BLOCKED','error':str(e)}));return 2
    target.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'status':r['status'],'counts':r['counts']},ensure_ascii=False))
    return 2  # Prevent process result being confused with native Stage6 PASS.

if __name__=='__main__':raise SystemExit(main())