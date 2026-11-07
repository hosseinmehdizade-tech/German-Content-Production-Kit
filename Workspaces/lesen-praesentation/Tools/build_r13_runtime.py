#!/usr/bin/env python3
"""Transport exactly 16 R13 p04 section edits from v505-proven R12 runtime. No browser/user data."""
import json,copy,hashlib,pathlib,importlib.util
P=pathlib.Path('/mnt/data/lesen_r13_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r12_20261107/Lesen-Production-Master-v1.3.0-R12-10P04-TRILINGUAL-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r12_20261107/Lesen-R12-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R13-16P04-TRILINGUAL-CANDIDATE.json'
OUT=P/'Lesen-R13-v505-16P04-RUNTIME-PREENTRY-CANDIDATE.json'
EVIDENCE=P/'LESEN-R13-RUNTIME-TRANSPORT-EVIDENCE.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(OLDM.read_bytes())=='a41224ae7a054a959c942afb0b13fcb7d686c76fc27131ec813a9272dad6e7d2'
assert sha(OLDR.read_bytes())=='e08844a19137a1edece8deb9f39e036df7b4777de2e54db4312e0ab14c3bcd86'
spec=importlib.util.spec_from_file_location('lesen_mapper','/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py')
mapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(mapper)
a=json.loads(OLDM.read_text());b=json.loads(OLDR.read_text());c=json.loads(NEWM.read_text());d=copy.deepcopy(b)
assert len(a['items'])==len(c['items'])==len(b['entries'])==68
assert sha(canon(b['entries']))==b['integrity']['entries_sha256']
assert sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
expected=set(range(52,59))|set(range(60,69));changed=[]
for i,(old,new,e) in enumerate(zip(a['items'],c['items'],b['entries'])):
 n=i+1;assert old['id']==new['id']==e['source_item_id']
 mapper.verify_section_mapping(old,e)
 diffs={k for k in old if old[k]!=new[k]}
 if n in expected:
  assert diffs=={'reading','grammar','quality'},(n,diffs)
  assert old['reading']['sections'][:3]==new['reading']['sections'][:3]
  assert old['reading']['sections'][4:]==new['reading']['sections'][4:]
  assert old['reading']['sections'][3]['sentences'][1]==new['reading']['sections'][3]['sentences'][1]
  assert old['questions']==new['questions'] and old['vocabulary']==new['vocabulary']
  d['entries'][i]=mapper.apply_fields(old,new,e);changed.append(new['id'])
 else:
  assert diffs==set(),(n,diffs)
  assert e==d['entries'][i]
 mapper.verify_section_mapping(new,d['entries'][i])
assert changed==[f'LES-PRES-{n:03d}' for n in sorted(expected)]
assert a['items'][50]==c['items'][50] and a['items'][58]==c['items'][58]
counts={'entries':68,'reading_units':68,
 'passages':sum(len(x['unit']['passages']) for x in d['entries']),
 'exercises':sum(len(x['exercises']) for x in d['entries']),
 'vocabulary_entries':sum(len(x['unit']['r38']['vocabulary']) for x in d['entries']),
 'curated_grammar':sum(len(x['unit']['r38']['grammar']['curated_annotations']) for x in d['entries']),
 'full_text_grammar':sum(len(x['unit']['r38']['grammar']['full_text_occurrences']) for x in d['entries'])}
assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4345},counts
d['counts']=counts
d['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(NEWM.read_bytes())}
d['compiler']={'id':'lesen-r13-16p04-scoped-trilingual-delta-v1','deterministic':True,'runtime_analysis_required':False,
 'contract':'Byte-verified R12 v505 preentry runtime plus 16 exact p04 DE/FA/EN and scoped grammar edits',
 'note':'NOT native full nine-lens grammar generator; NOT actual browser/IndexedDB Stage6 or Stage7 release.'}
d['candidate_review']={'status':'R13_PREENTRY_ONLY_STAGE4_6_7_HOLD','changed_unit_ids':changed,'preserved_prior_edits':['LES-PRES-051','LES-PRES-059'],
 'changed_section_ids':['p04'],'changed_sentences_per_unit':['p04-s01','p04-s03'],
 'unchanged_original_middle_sentences':16,'semantic_stage4':'HOLD','full_nine_lens_grammar_rerun':False,
 'browser_indexeddb_stage6':'NOT_RUN','curated_current':'UNCHANGED','fulltext_grammar_count_after':4345,
 'parent_r12_runtime_sha256':sha(OLDR.read_bytes())}
d['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(d['entries']))}
d['integrity']['payload_sha256']=sha(canon({k:v for k,v in d.items() if k!='integrity'}))
write(OUT,d)
rec={'schema':'lesen-r13-v505-preentry-transport@1.0.0','date':'2026-11-07',
 'parent_content_sha256':sha(OLDM.read_bytes()),'parent_runtime_sha256':sha(OLDR.read_bytes()),
 'r13_content_sha256':sha(NEWM.read_bytes()),'r13_runtime_sha256':sha(OUT.read_bytes()),
 'r13_runtime_bytes':OUT.stat().st_size,'counts':counts,'unchanged_exact_entries':52,
 'changed_unit_ids':changed,'previously_approved_051_059_preserved':True,
 'integrity_entries_sha256':d['integrity']['entries_sha256'],'integrity_payload_sha256':d['integrity']['payload_sha256'],
 'v505_source_validator':'SEPARATE_REQUIRED','stage4':'HOLD','native_browser_stage6':'NOT_RUN',
 'full_nine_lens_engine':'NOT_RERUN','curated_current':'UNCHANGED','app_ui_or_srs_fsrs_modified':False}
write(EVIDENCE,rec)
print(json.dumps(rec,ensure_ascii=False,indent=2))