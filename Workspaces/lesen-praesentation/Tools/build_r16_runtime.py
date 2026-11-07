#!/usr/bin/env python3
"""Exact R15 v505 pre-entry runtime plus only 13 changed lesson projections."""
import pathlib,json,copy,hashlib,importlib.util
P=pathlib.Path('/mnt/data/lesen_r16_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r15_20261107/Lesen-Production-Master-v1.3.0-R15-25CONCLUSIONS-TRILINGUAL-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r15_20261107/Lesen-R15-v505-25CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R16-22CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
OUT=P/'Lesen-R16-v505-22CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'
EVD=P/'LESEN-R16-V505-TRANSPORT-EVIDENCE.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sham='efa0fa9ece712f3a045ef47c802efe9230fe1baa366cb43e7f3ba5a8573e4c67';shar='52b0d807bf1c9ab6dbc80011ddb98d131594ebdb4544981a8d0a1c9c22489e33'
assert sha(OLDM.read_bytes())==sham and sha(OLDR.read_bytes())==shar
spec=importlib.util.spec_from_file_location('v505_exact_runtime_map','/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py')
map=importlib.util.module_from_spec(spec);spec.loader.exec_module(map)
a=json.loads(OLDM.read_text());b=json.loads(OLDR.read_text());c=json.loads(NEWM.read_text());d=copy.deepcopy(b)
assert sha(canon(b['entries']))==b['integrity']['entries_sha256'] and sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
changed=[]
for i,(old,new,ent) in enumerate(zip(a['items'],c['items'],b['entries'])):
 assert old['id']==new['id']==ent['source_item_id']
 map.verify_section_mapping(old,ent)
 diff={k for k in old if old[k]!=new[k]}
 if old!=new:
  assert 25<=i+1<=38 and i+1!=35 and diff=={'reading','grammar','quality'},(old['id'],diff)
  assert old['questions']==new['questions'] and old['vocabulary']==new['vocabulary']
  assert old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets']
  assert old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks']
  d['entries'][i]=map.apply_fields(old,new,ent);changed.append(old['id'])
 else:assert d['entries'][i]==ent
 map.verify_section_mapping(new,d['entries'][i])
assert len(changed)==13
counts={'entries':len(d['entries']),'reading_units':len(d['entries']),
'passages':sum(len(e['unit']['passages']) for e in d['entries']),
'exercises':sum(len(e['exercises']) for e in d['entries']),
'vocabulary_entries':sum(len(e['unit']['r38']['vocabulary']) for e in d['entries']),
'curated_grammar':sum(len(e['unit']['r38']['grammar']['curated_annotations']) for e in d['entries']),
'full_text_grammar':sum(len(e['unit']['r38']['grammar']['full_text_occurrences']) for e in d['entries'])}
assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4160},counts
d['counts']=counts
d['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(NEWM.read_bytes())}
d['compiler']={'id':'lesen-r16-source-aligned-conclusions-v505-delta-v1','deterministic':True,'runtime_analysis_required':False,
'contract':'R15 exact v505 preentry runtime plus only 13 source-mapped edited units covering 22 generic conclusions.',
'note':'Not the historical full compiler, complete grammar engine, native browser import, or released content.'}
d['candidate_review']={'status':'R16_SOURCE_BOUND_CANDIDATE_STAGE4_6_7_HOLD','changed_unit_ids':changed,
'changed_section_ids':['p02','p03'],'changed_sentence_ids':['p02-s03','p03-s03'],
'old_generic_grammar_retired':70,'new_manual_relative_grammar':10,'curated_relative_retargets':10,
'full_semantic_stage4':'HOLD','browser_indexeddb_stage6':'NOT_RUN','original_current':'UNCHANGED',
'grammar_total':4160,'remaining_exact_generic_p02_s03':28,'remaining_exact_generic_p03_s03':21}
d['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(d['entries']))};d['integrity']['payload_sha256']=sha(canon({k:v for k,v in d.items() if k!='integrity'}))
write(OUT,d)
evidence={'schema':'lesen-r16-source-aware-v505-preentry-transport@1.0.0','date':'2026-11-07',
'parent_master_sha256':sham,'parent_runtime_sha256':shar,'candidate_master_sha256':sha(NEWM.read_bytes()),
'candidate_runtime_sha256':sha(OUT.read_bytes()),'candidate_runtime_bytes':OUT.stat().st_size,
'counts':counts,'changed_units':changed,'unchanged_entries':55,'changed_conclusion_sections':22,
'parent_entries_integrity_verified':True,'new_entries_integrity':d['integrity']['entries_sha256'],
'new_payload_integrity':d['integrity']['payload_sha256'],'mapping_verified':68,
'complete_independent_semantic_stage4':'HOLD','native_browser_stage6':'NOT_RUN','stage7':'NOT_RELEASED'}
write(EVD,evidence);print(json.dumps(evidence,ensure_ascii=False,indent=2))