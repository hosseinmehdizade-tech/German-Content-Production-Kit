#!/usr/bin/env python3
"""R10->R11 deterministic reading-specific candidate transport, no app/browser/user state changes."""
import json,copy,hashlib,pathlib,importlib.util,collections
P=pathlib.Path('/mnt/data/lesen_r11_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r10_20261107/Lesen-Production-Master-v1.3.0-R10-10P04-TRILINGUAL-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r10_20261107/Lesen-R10-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R11-9P04-TRILINGUAL-CANDIDATE.json'
OUT=P/'Lesen-R11-v505-9P04-RUNTIME-PREENTRY-CANDIDATE.json'
EVIDENCE=P/'LESEN-R11-RUNTIME-TRANSPORT-EVIDENCE.json'
OLDM_SHA='4be5bf368b23a1a46bae2d28686b3d4f9336ac01d98c2c1449ab19df81b9509a'
OLDR_SHA='e2e5d395679f772f7ec4cf845da4af2aadb148f3362b3ed3955ed76d280e9aa3'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(OLDM.read_bytes())==OLDM_SHA and sha(OLDR.read_bytes())==OLDR_SHA
mpspec=importlib.util.spec_from_file_location('lesen_mapper','/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py')
mapper=importlib.util.module_from_spec(mpspec);mpspec.loader.exec_module(mapper)
a=json.loads(OLDM.read_text());b=json.loads(OLDR.read_text());c=json.loads(NEWM.read_text());d=copy.deepcopy(b)
assert len(a['items'])==len(c['items'])==len(b['entries'])==68
assert sha(canon(b['entries']))==b['integrity']['entries_sha256']
assert sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
expected={31,32,33,34,36,37,38,39,40};changed=[]
for i,(old,new,e) in enumerate(zip(a['items'],c['items'],b['entries'])):
    n=i+1
    assert old['id']==new['id']==e['source_item_id']
    mapper.verify_section_mapping(old,e)
    diffs={k for k in old if old[k]!=new[k]}
    if n in expected:
        assert diffs=={'reading','grammar','quality'},(n,diffs)
        assert old['reading']['sections'][:3]==new['reading']['sections'][:3]
        assert old['reading']['sections'][4:]==new['reading']['sections'][4:]
        assert old['reading']['sections'][3]['sentences'][1]==new['reading']['sections'][3]['sentences'][1]
        assert old['questions']==new['questions'] and old['vocabulary']==new['vocabulary']
        d['entries'][i]=mapper.apply_fields(old,new,e)
        changed.append(new['id'])
    else:
        assert diffs==set(),(n,diffs)
        assert e==d['entries'][i]
    mapper.verify_section_mapping(new,d['entries'][i])
assert changed==[f'LES-PRES-{n:03d}' for n in sorted(expected)]
assert a['items'][34]==c['items'][34] and b['entries'][34]==d['entries'][34]
counts={'entries':68,'reading_units':68,
 'passages':sum(len(x['unit']['passages']) for x in d['entries']),
 'exercises':sum(len(x['exercises']) for x in d['entries']),
 'vocabulary_entries':sum(len(x['unit']['r38']['vocabulary']) for x in d['entries']),
 'curated_grammar':sum(len(x['unit']['r38']['grammar']['curated_annotations']) for x in d['entries']),
 'full_text_grammar':sum(len(x['unit']['r38']['grammar']['full_text_occurrences']) for x in d['entries'])}
assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4475},counts
d['counts']=counts
d['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(NEWM.read_bytes())}
d['compiler']={'id':'lesen-r11-9p04-scoped-trilingual-delta-v1','deterministic':True,'runtime_analysis_required':False,
 'contract':'R10 verified v505 preentry runtime plus 9 editorial p04 source sections with FA/EN and scoped grammar anchors',
 'note':'NOT the native nine-lens grammar source producer; NOT browser/IndexedDB Stage6 or Stage7.'}
d['candidate_review']={'status':'R11_PREENTRY_ONLY_STAGE4_6_7_HOLD','changed_unit_ids':changed,'preserved_previously_revised_unit':'LES-PRES-035',
 'changed_section_ids':['p04'],'changed_sentences_per_unit':['p04-s01','p04-s03'],
 'preserved_original_p04_s02_in_all_nine':True,'semantic_stage4':'HOLD','full_nine_lens_grammar_rerun':False,
 'browser_indexeddb_stage6':'NOT_RUN','curated_current':'UNCHANGED',
 'fulltext_grammar_count_after':4475,'parent_r10_runtime_sha256':OLDR_SHA}
d['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(d['entries']))}
d['integrity']['payload_sha256']=sha(canon({k:v for k,v in d.items() if k!='integrity'}))
write(OUT,d)
rec={'schema':'lesen-r11-v505-preentry-transport@1.0.0','date':'2026-11-07',
 'parent_content_sha256':OLDM_SHA,'parent_runtime_sha256':OLDR_SHA,
 'r11_content_sha256':sha(NEWM.read_bytes()),'r11_runtime_sha256':sha(OUT.read_bytes()),
 'r11_runtime_bytes':OUT.stat().st_size,'counts':counts,'unchanged_exact_entries':59,
 'changed_unit_ids':changed,'previously_revised_035_preserved':True,
 'integrity_entries_sha256':d['integrity']['entries_sha256'],'integrity_payload_sha256':d['integrity']['payload_sha256'],
 'v505_source_validator':'SEPARATE_REQUIRED','stage4':'HOLD','native_browser_stage6':'NOT_RUN',
 'full_9_lens_engine':'NOT_RERUN','curated_current':'UNCHANGED','app_ui_or_srs_fsrs_modified':False}
write(EVIDENCE,rec);print(json.dumps(rec,ensure_ascii=False,indent=2))