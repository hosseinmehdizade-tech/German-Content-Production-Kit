#!/usr/bin/env python3
"""Strict Lesen R3 -> current v505 precompiled runtime transport.

Based on independently verified v1.3.0 compiled-runtime entry layout and
exact fields of the immutable original master; preserves the 65 untouched
runtime entries as dictionary-identical. Not the historical R41 compiler or
fulltext grammar generator. It NEVER writes back to original/Current.
"""
import argparse, copy, hashlib, json, pathlib, zipfile

BASE_SHA = '558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565'
R3_SHA = '2b7e29acb973d34e878f76df5135be740c0819934b457265a1fd281ca97c2a8e'
DIFF = {'LES-PRES-035','LES-PRES-051','LES-PRES-059'}

def sha_bytes(x): return hashlib.sha256(x).hexdigest()
def sortedbytes(obj): return json.dumps(obj, ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
def get(path): return json.loads(path.read_text('utf8'))
def put(path,obj): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def verify_section_mapping(b, e):
    unit=e['unit'];rid='lesen_'+b['id']
    assert e['source_item_id']==b['id'] and unit['reading_unit_id']==rid
    assert unit['title']==b['title_de']
    assert unit['title_translations']=={'fa':b['title_fa'],'en':b['title_en']}
    assert unit['cefr']==b['cefr_target'] and unit['text_type']==b['text_type']
    assert unit['topic_tags']==list(dict.fromkeys(b['topics']))
    assert len(unit['passages'])==len(b['reading']['sections'])
    for sec,p in zip(b['reading']['sections'],unit['passages']):
        assert p['passage_id']==rid+'_'+sec['id']
        assert p['r38']['source_section_id']==sec['id']
        assert p['text_de']==sec['text'] and p['translations']==sec['translations']
        assert p['section_role']==sec['role']
        assert p['sentence_ids']==[s['id'] for s in sec['sentences']]
    assert len(e['exercises'])==len(b['questions'])==5
    assert unit['comprehension_exercise_ids']==[x['exercise_id'] for x in e['exercises']]
    for q,ex in zip(b['questions'],e['exercises']):
        assert ex['exercise_id']==rid+'_'+q['id'] and ex['prompt_de']==q['prompt_de']
        assert ex['answer_spec']['model_answer']==q['answer_de']
        assert ex['answer_spec']['question_type']==q['type']
        assert ex['answer_spec']['answer_hidden_by_default']==q['answer_hidden_by_default']
        assert ex['r38']['question_id']==q['id'] and ex['r38']['difficulty']==q['difficulty']
        assert ex['r38']['evidence_section_ids']==q['evidence_section_ids']
    for key,expected in [('word_count_de',b['reading']['word_count_de']),('estimated_pure_reading_min',b['reading']['estimated_pure_reading_min']),('recommended_study_time_min',b['reading']['recommended_study_time_min']),('grammar',b['grammar']),('vocabulary',b['vocabulary']),('tasks',b['tasks']),('display_recommendation',b['display_recommendation']),('quality',b['quality']),('learning_objectives_de',b['learning_objectives_de'])]:
        assert unit['r38'][key]==expected, (b['id'], key)

def apply_fields(orig, newer, entry):
    e=copy.deepcopy(entry);u=e['unit']
    assert orig['id']==newer['id'] and orig['order']==newer['order']
    assert set(orig)==set(newer)
    assert {k for k in orig if orig[k]!=newer[k]} <= {'reading','grammar','questions','quality'}
    assert len(orig['reading']['sections'])==len(newer['reading']['sections'])
    assert [s['id'] for s in orig['reading']['sections']]==[s['id'] for s in newer['reading']['sections']]
    assert [q['id'] for q in orig['questions']]==[q['id'] for q in newer['questions']]
    assert [v['id'] for v in orig['vocabulary']]==[v['id'] for v in newer['vocabulary']]
    assert orig['title_de']==newer['title_de'] and orig['legacy_source']==newer['legacy_source']
    for sec,p in zip(newer['reading']['sections'],u['passages']):
        assert [t['id'] for t in sec['sentences']]==p['sentence_ids']
        p['text_de']=sec['text']
        p['translations']=copy.deepcopy(sec['translations'])
        p['section_role']=sec['role']
    for q,ex in zip(newer['questions'],e['exercises']):
        ex['prompt_de']=q['prompt_de']
        ex['answer_spec']['model_answer']=q['answer_de']
        ex['answer_spec']['answer_hidden_by_default']=q['answer_hidden_by_default']
        ex['answer_spec']['question_type']=q['type']
        ex['skill_tags']=['reading.'+q['type']]
        ex['r38']['difficulty']=q['difficulty']
        ex['r38']['evidence_section_ids']=copy.deepcopy(q['evidence_section_ids'])
    for key in ['word_count_de','estimated_pure_reading_min','recommended_study_time_min']:
        u['r38'][key]=newer['reading'][key]
    for key in ['grammar','vocabulary','tasks','display_recommendation','quality','learning_objectives_de']:
        u['r38'][key]=copy.deepcopy(newer[key])
    verify_section_mapping(newer,e)
    return e

def main():
    a=argparse.ArgumentParser();a.add_argument('--base-zip',type=pathlib.Path,required=True);a.add_argument('--r3-master',type=pathlib.Path,required=True);a.add_argument('--output',type=pathlib.Path,required=True);a.add_argument('--evidence',type=pathlib.Path,required=True);args=a.parse_args()
    assert sha_bytes(args.base_zip.read_bytes())==BASE_SHA,'baseline ZIP SHA mismatch'
    assert sha_bytes(args.r3_master.read_bytes())==R3_SHA,'R3 master SHA mismatch'
    with zipfile.ZipFile(args.base_zip) as z:
        assert z.testzip() is None
        master_raw=z.read('01-Final-Content/Lesen-Production-Master-v1.3.0.json')
        base=json.loads(master_raw)
        runtime=json.loads(z.read('02-Compiled-Runtime/Lesen-Runtime-Pack-v1.0.0.json'))
    newer=get(args.r3_master)
    assert sha_bytes(master_raw)==runtime['compiled_from']['sha256']
    assert sha_bytes(sortedbytes(runtime['entries']))==runtime['integrity']['entries_sha256'],'old entries hash mismatch'
    assert len(base['items'])==len(newer['items'])==len(runtime['entries'])==68
    assert [x['id'] for x in base['items']]==[x['id'] for x in newer['items']]==[x['source_item_id'] for x in runtime['entries']]
    assert {x['id'] for x,y in zip(base['items'],newer['items']) if x!=y}==DIFF
    # Validate the old runtime against the source master *before* using its transport layout.
    for b,e in zip(base['items'],runtime['entries']):verify_section_mapping(b,e)
    out=copy.deepcopy(runtime)
    for i,(old,new) in enumerate(zip(base['items'],newer['items'])):
        if old['id'] in DIFF:out['entries'][i]=apply_fields(old,new,out['entries'][i])
        else:assert out['entries'][i]==runtime['entries'][i]
    # Verify all 68 entries are exact faithful transports of R3 master.
    for b,e in zip(newer['items'],out['entries']):verify_section_mapping(b,e)
    counts={
        'entries':68,'reading_units':68,
        'passages':sum(len(x['unit']['passages']) for x in out['entries']),
        'exercises':sum(len(x['exercises']) for x in out['entries']),
        'vocabulary_entries':sum(len(x['unit']['r38']['vocabulary']) for x in out['entries']),
        'curated_grammar':sum(len(x['unit']['r38']['grammar']['curated_annotations']) for x in out['entries']),
        'full_text_grammar':sum(len(x['unit']['r38']['grammar']['full_text_occurrences']) for x in out['entries'])}
    assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4620},counts
    out['counts']=counts
    out['compiled_from']={'schema_version':newer['schema_version'],'pack_id':newer['pack_id'],'content_version':newer['content_version'],'sha256':R3_SHA}
    # Not masquerading as historical R41 native compiler: this is a source-aware delta transport.
    out['compiler']={'id':'lesen-r3-source-verified-delta-transport-v1','deterministic':True,'runtime_analysis_required':False,'contract':'historical compiled runtime + exact 3 changed owner units -> v505 import contract', 'note':'Not the historical R41 compiler or fulltext grammar generator.'}
    out['candidate_review']={'status':'PREENTRY_CANDIDATE_ONLY_NOT_RELEASED', 'changed_units':sorted(DIFF),'content_quality':'STAGE4_HOLD_55_TEMPLATE_UNITS_AND_NATIVE_GRAMMAR_ENGINE_NOT_RERUN','native_stage6':'NOT_RUN','original_current':'UNMODIFIED'}
    out['integrity']={'algorithm':'sha256','entries_sha256':sha_bytes(sortedbytes(out['entries']))}
    # Full payload = whole pack WITHOUT integrity to avoid hash self reference.
    out['integrity']['payload_sha256']=sha_bytes(sortedbytes({k:v for k,v in out.items() if k!='integrity'}))
    assert sha_bytes(sortedbytes(out['entries']))==out['integrity']['entries_sha256']
    assert sha_bytes(sortedbytes({k:v for k,v in out.items() if k!='integrity'}))==out['integrity']['payload_sha256']
    put(args.output,out)
    evidence={'schema':'lesen-r3-v505-runtime-delta-transport-evidence@1','current_source_zip_sha256':BASE_SHA,'current_compiled_entries_sha256':runtime['integrity']['entries_sha256'],'r3_source_sha256':R3_SHA,'r3_runtime_sha256':sha_bytes(args.output.read_bytes()),'entries_sha256':out['integrity']['entries_sha256'],'payload_sha256':out['integrity']['payload_sha256'],'canonical_hash':'sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf8"))','payload_hash_scope':'all top-level runtime JSON keys other than integrity','counts':counts,'changed_unit_ids':sorted(DIFF),'unchanged_runtime_entries_identical':65,'all_68_runtime_entries_checked_against_R3_master':True,'original_68_entries_checked_against_original_master':True,'original_compiled_sha_verified':True,'no_native_reading_grammar_rebuild':True,'semantic_stage4':'HOLD','stage5':'CANDIDATE_PREENTRY_ONLY','stage6':'NOT_RUN','stage7':'NOT_RELEASED','user_data_touched':False}
    put(args.evidence,evidence)
    print(json.dumps(evidence,ensure_ascii=False,indent=2))
if __name__=='__main__':main()