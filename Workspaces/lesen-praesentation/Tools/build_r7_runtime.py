#!/usr/bin/env python3
"""Produce source-aware R7 v505 PREENTRY runtime from byte-pinned R6 runtime.
Only question prompt+model answer fields change; no browser/IndexedDB/app modifications.
"""
import copy,hashlib,json,pathlib
P=pathlib.Path('/mnt/data/lesen_r7_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r6_20261107/Lesen-Production-Master-v1.3.0-R6-20UNIT-Q123-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r6_20261107/Lesen-R6-v505-20UNIT-Q123-RUNTIME-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R7-20UNIT-Q123-CANDIDATE.json'
OUT=P/'Lesen-R7-v505-20UNIT-Q123-RUNTIME-CANDIDATE.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
assert sha(OLDM.read_bytes())=='3a727fc2575b5c041808803b6a97d2a77239aa3089f6bf88570c39e959d26f5c'
assert sha(OLDR.read_bytes())=='3843634a8300f16a14e192c3ecef04b3e83b7dcad9631a84162495ce307ea625'
a=json.loads(OLDM.read_text());b=json.loads(OLDR.read_text());c=json.loads(NEWM.read_text());out=copy.deepcopy(b)
assert len(a['items'])==len(c['items'])==len(b['entries'])==len(out['entries'])==68
assert sha(canon(b['entries']))==b['integrity']['entries_sha256']
assert sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
changed=[];prompt_count=0;answer_count=0
for old,new,prev,run in zip(a['items'],c['items'],b['entries'],out['entries']):
 assert old['id']==new['id']==prev['source_item_id']==run['source_item_id']
 assert {key for key in old if old[key]!=new[key]}<={'questions'}
 if old['questions']!=new['questions']:
  changed.append(new['id']); assert new['id'] in [f'LES-PRES-{i:03}' for i in range(31,51)]
  for k,(x,y,e) in enumerate(zip(old['questions'],new['questions'],run['exercises'])):
   assert x['id']==y['id']==e['r38']['question_id']
   assert {key for key in x if x[key]!=y[key]}<={'prompt_de','answer_de'}
   if k<3:
    if x['prompt_de']!=y['prompt_de']: e['prompt_de']=y['prompt_de'];prompt_count+=1
    if x['answer_de']!=y['answer_de']: e['answer_spec']['model_answer']=y['answer_de'];answer_count+=1
   else:assert x==y
 else:assert prev==run
 assert prev['unit']==run['unit']
 assert all(e['prompt_de']==q['prompt_de'] and e['answer_spec']['model_answer']==q['answer_de'] for q,e in zip(new['questions'],run['exercises']))
assert changed==[f'LES-PRES-{i:03}' for i in range(31,51)]
assert (prompt_count,answer_count)==(58,57)
assert sum(x==y for x,y in zip(b['entries'],out['entries']))==48
out['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(NEWM.read_bytes())}
out['compiler']={'id':'lesen-r7-20unit-q123-delta-transport-v1','deterministic':True,'runtime_analysis_required':False,'contract':'R6 v505 preentry + changed q01/q02/q03 prompts+answers on 031..050 only; q02/q03 035 preserved, 043 q03 answer preserved','note':'Not native full compiler; no browser/IndexedDB writes or Stage6 claim.'}
out['candidate_review']={'status':'PREENTRY_CANDIDATE_NOT_STAGE4_6_7','changed_unit_ids':changed,'revised_prompt_count':prompt_count,'revised_answer_count':answer_count,'all_passages_and_grammar_untouched':True,'parent_r6_runtime_sha256':sha(OLDR.read_bytes()),'native_stage6':'NOT_RUN','semantic_stage4':'NOT_FULLY_PERFORMED'}
out['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(out['entries']))}
out['integrity']['payload_sha256']=sha(canon({k:v for k,v in out.items() if k!='integrity'}))
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'runtime_sha256':sha(OUT.read_bytes()),'bytes':OUT.stat().st_size,'changed_units':len(changed),'prompt_count':prompt_count,'answer_count':answer_count,'entries_sha256':out['integrity']['entries_sha256'],'payload_sha256':out['integrity']['payload_sha256']},indent=2))