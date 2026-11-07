#!/usr/bin/env python3
"""Exact R5 runtime -> R6 runtime 20-unit question-only delta transport (v505 PREENTRY only)."""
import copy,hashlib,importlib.util,json,pathlib
P=pathlib.Path('/mnt/data/lesen_r6_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r5_20261107/Lesen-Production-Master-v1.3.0-R5-55Q-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r5_20261107/Lesen-R5-v505-QUESTION-DELTA-RUNTIME-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R6-20UNIT-Q123-CANDIDATE.json'
OUT=P/'Lesen-R6-v505-20UNIT-Q123-RUNTIME-CANDIDATE.json'
sha=lambda b: hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
assert sha(OLDM.read_bytes())=='6371522e011333c836969ae2983c69ecbc259743632a6b44226b3bc5ef7ab764'
assert sha(OLDR.read_bytes())=='cf66efa8ae1376116b8f9e68e0090b71d47ea964ce2f65c57034df609df5f943'
a=json.loads(OLDM.read_text());b=json.loads(OLDR.read_text());c=json.loads(NEWM.read_text());out=copy.deepcopy(b)
assert b['schema_version']=='lesen.runtime.v1.0.0' and len(out['entries'])==68
assert sha(canon(b['entries']))==b['integrity']['entries_sha256']
assert sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
changed=[]
for i,(old,new,prev,runtime) in enumerate(zip(a['items'],c['items'],b['entries'],out['entries'])):
 assert old['id']==new['id']==prev['source_item_id']==runtime['source_item_id']
 assert {key for key in old if old[key]!=new[key]}<={'questions'}
 if old['questions']!=new['questions']:
  changed.append(new['id'])
  assert new['id'] in [f'LES-PRES-{i:03d}' for i in range(11,31)]
  for index,(q0,q1,e) in enumerate(zip(old['questions'],new['questions'],runtime['exercises'])):
   assert q0['id']==q1['id']==e['r38']['question_id']
   assert {k for k in q0 if q0[k]!=q1[k]}<={'prompt_de','answer_de'}
   if index<3:
    e['prompt_de']=q1['prompt_de']; e['answer_spec']['model_answer']=q1['answer_de']
   else:assert q0==q1
 else: assert prev==runtime
 assert prev['unit']==runtime['unit']
 assert all(e['prompt_de']==q['prompt_de'] and e['answer_spec']['model_answer']==q['answer_de'] for q,e in zip(new['questions'],runtime['exercises']))
assert changed==[f'LES-PRES-{i:03d}' for i in range(11,31)]
assert sum(x==y for x,y in zip(b['entries'],out['entries']))==48
out['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(NEWM.read_bytes())}
out['compiler']={'id':'lesen-r6-20unit-q123-delta-transport-v1','deterministic':True,'runtime_analysis_required':False,'contract':'R5 v505 validated preentry + edited question prompt/answer only on q01/q02/q03 units 011..030','note':'Not original native full compiler; no user profile, browser or FSRS writes.'}
out['candidate_review']={'status':'PREENTRY_CANDIDATE_NOT_STAGE4_6_7','changed_unit_ids':changed,'revised_question_prompt_answer_pairs':60,'all_passages_and_grammar_untouched':True,'previous_r5_runtime_sha256':sha(OLDR.read_bytes()),'native_stage6':'NOT_RUN','semantic_stage4':'NOT_FULLY_PERFORMED'}
out['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(out['entries']))}
out['integrity']['payload_sha256']=sha(canon({k:v for k,v in out.items() if k!='integrity'}))
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'r6_content_sha256':sha(NEWM.read_bytes()),'r6_runtime_sha256':sha(OUT.read_bytes()),'runtime_bytes':OUT.stat().st_size,'changed_entries':len(changed),'unchanged_entries':48,'entries_sha256':out['integrity']['entries_sha256'],'payload_sha256':out['integrity']['payload_sha256']},indent=2))