#!/usr/bin/env python3
"""R8 question-only source aware delta transport against pinned R7 v505 runtime.
Explicitly not the app's full native compiler, not actual browser Stage6.
"""
import hashlib,json,copy,pathlib
P=pathlib.Path('/mnt/data/lesen_r8_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r7_20261107/Lesen-Production-Master-v1.3.0-R7-20UNIT-Q123-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r7_20261107/Lesen-R7-v505-20UNIT-Q123-RUNTIME-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R8-18UNIT-Q123-CANDIDATE.json'
OUT=P/'Lesen-R8-v505-18UNIT-Q123-RUNTIME-CANDIDATE.json'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
canon=lambda o:json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
assert sha(OLDM.read_bytes())=='f472a6260b29f7112bfdf71894f1004957ade61d8ec9bc842992f5a6e4c718d9'
assert sha(OLDR.read_bytes())=='043126b22cc256a911ec9697888b5f944a4520ddb3e22ef74de423abc3c9c6b3'
a=json.loads(OLDM.read_text());b=json.loads(OLDR.read_text());c=json.loads(NEWM.read_text());out=copy.deepcopy(b)
assert sha(canon(b['entries']))==b['integrity']['entries_sha256']
assert sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
changed=[];prompts=answers=0
for old,new,prev,run in zip(a['items'],c['items'],b['entries'],out['entries']):
 uid=old['id'];assert uid==new['id']==prev['source_item_id']==run['source_item_id']
 assert {k for k in old if old[k]!=new[k]}<={'questions'}
 assert prev['unit']==run['unit']
 if old['questions']!=new['questions']:
  changed.append(uid);assert 51<=int(uid[-3:])<=68
  for k,(x,y,e) in enumerate(zip(old['questions'],new['questions'],run['exercises'])):
   assert x['id']==y['id']==e['r38']['question_id']
   assert {key for key in x if x[key]!=y[key]}<={'prompt_de','answer_de'}
   if k<3:
    if x['prompt_de']!=y['prompt_de']:e['prompt_de']=y['prompt_de'];prompts+=1
    if x['answer_de']!=y['answer_de']:e['answer_spec']['model_answer']=y['answer_de'];answers+=1
   else:assert x==y
 else:assert prev==run
 assert all(e['prompt_de']==q['prompt_de'] and e['answer_spec']['model_answer']==q['answer_de'] for q,e in zip(new['questions'],run['exercises']))
assert changed==[f'LES-PRES-{i:03d}' for i in range(51,69)]
assert (prompts,answers)==(50,50)
assert sum(old==new for old,new in zip(b['entries'],out['entries']))==50
out['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(NEWM.read_bytes())}
out['compiler']={'id':'lesen-r8-18unit-q123-delta-transport-v1','deterministic':True,'runtime_analysis_required':False,'contract':'R7 v505 preentry + edited q01..03 in 051..068; already reviewed q02 and q03 of 051/059 preserved','note':'Source-aware bounded question delta only, not native full compiler. No browser/IndexedDB writes or Stage6 claim.'}
out['candidate_review']={'status':'PREENTRY_CANDIDATE_NOT_STAGE4_6_7','changed_unit_ids':changed,'revised_prompt_count':prompts,'revised_answer_count':answers,'preserved_previous_questions':['LES-PRES-051.q02','LES-PRES-051.q03','LES-PRES-059.q02','LES-PRES-059.q03'],'all_passages_and_grammar_untouched':True,'parent_r7_runtime_sha256':sha(OLDR.read_bytes()),'native_stage6':'NOT_RUN','semantic_stage4':'NOT_FULLY_PERFORMED'}
out['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(out['entries']))}
out['integrity']['payload_sha256']=sha(canon({k:v for k,v in out.items() if k!='integrity'}))
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'runtime_sha256':sha(OUT.read_bytes()),'bytes':OUT.stat().st_size,'changed_units':len(changed),'prompts':prompts,'answers':answers,'entries_sha256':out['integrity']['entries_sha256'],'payload_sha256':out['integrity']['payload_sha256']},ensure_ascii=False,indent=2))