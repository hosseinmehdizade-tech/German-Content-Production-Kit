#!/usr/bin/env python3
"""Create exact pre-entry v505 reading runtime candidate from R4 runtime + R5 question-only editorial delta.
NEVER invokes installed browser/IndexedDB or touches CURRENT. Native full compiler NOT claimed.
"""
import copy,hashlib,json,pathlib,importlib.util
P=pathlib.Path('/mnt/data/lesen_r5_20261107')
R3PATH=pathlib.Path('/mnt/data/lesen_r3_20261107/Lesen-Production-Master-v1.3.0-R3-3UNIT-GRAMMAR-CANDIDATE.json')
R4PATH=pathlib.Path('/mnt/data/lesen_r4_workspace/Lesen-R3-v505-PREENTRY-RUNTIME-CANDIDATE.json')
R5PATH=P/'Lesen-Production-Master-v1.3.0-R5-55Q-CANDIDATE.json'
OUT=P/'Lesen-R5-v505-QUESTION-DELTA-RUNTIME-CANDIDATE.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
assert sha(R3PATH.read_bytes())=='2b7e29acb973d34e878f76df5135be740c0819934b457265a1fd281ca97c2a8e'
assert sha(R4PATH.read_bytes())=='53b2746c2ed2ee6938773d850ccc8a287f2d81608422a38aba481ef059ebc683'
assert sha(R5PATH.read_bytes())=='6371522e011333c836969ae2983c69ecbc259743632a6b44226b3bc5ef7ab764'
modpath=pathlib.Path('/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py')
spec=importlib.util.spec_from_file_location('lesen_source_map',modpath);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
R3=json.loads(R3PATH.read_text());R4=json.loads(R4PATH.read_text());R5=json.loads(R5PATH.read_text());out=copy.deepcopy(R4)
assert len(R3['items'])==len(R5['items'])==len(R4['entries'])==68
assert sha(canonical(R4['entries']))==R4['integrity']['entries_sha256']
assert sha(canonical({k:v for k,v in R4.items() if k!='integrity'}))==R4['integrity']['payload_sha256']
modified=[]
for idx,(old,new,entry) in enumerate(zip(R3['items'],R5['items'],R4['entries'])):
 assert old['id']==new['id']==entry['source_item_id']
 mod.verify_section_mapping(old,entry)
 assert {k for k in old if old[k]!=new[k]}<= {'questions'}
 assert old['reading']==new['reading'] and old['grammar']==new['grammar']
 if old['questions']!=new['questions']:
  modified.append(old['id'])
  oe=out['entries'][idx]
  for qold,qnew,ex in zip(old['questions'],new['questions'],oe['exercises']):
   assert qold['id']==qnew['id'] and ex['r38']['question_id']==qold['id']
   assert {k for k in qold if qold[k]!=qnew[k]} <= {'prompt_de','answer_de'},(old['id'],qold['id'])
   ex['prompt_de']=qnew['prompt_de']
   ex['answer_spec']['model_answer']=qnew['answer_de']
  assert oe['unit']==entry['unit']
 else:assert out['entries'][idx]==entry
 mod.verify_section_mapping(new,out['entries'][idx])
assert len(modified)==55, len(modified)
assert sum(x['unit']==y['unit'] for x,y in zip(R4['entries'],out['entries']))==68
assert sum(x==y for x,y in zip(R4['entries'],out['entries']))==13
assert R4['counts']==out['counts']
out['compiled_from']={'schema_version':R5['schema_version'],'pack_id':R5['pack_id'],'content_version':R5['content_version'],'sha256':sha(R5PATH.read_bytes())}
out['compiler']={'id':'lesen-r5-question-only-delta-transport-v1','deterministic':True,'runtime_analysis_required':False,'contract':'exact R4 preentry runtime + 55 source-owner revised q04 prompt/answer + 3 q03 answer repairs','note':'Not the historical native full compiler; preserves all passage/grammar units exactly.'}
out['candidate_review']={'status':'PREENTRY_ONLY__NOT_STAGE4_6_7','changed_unit_ids':modified,'q04_replacements':55,'q03_grammar_repairs':3,'reading_text_and_fulltext_grammar_changed':False,'other_questions_untouched':True,'original_current':'UNMODIFIED','native_stage6':'NOT_RUN','semantic_stage4':'NOT_FULLY_PERFORMED'}
out['integrity']={'algorithm':'sha256','entries_sha256':sha(canonical(out['entries']))}
out['integrity']['payload_sha256']=sha(canonical({k:v for k,v in out.items() if k!='integrity'}))
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(canonical(json.loads(OUT.read_text())['entries']))==out['integrity']['entries_sha256']
receipt={'schema':'lesen-r5-v505-preentry-transport-evidence@1.0.0','date':'2026-11-07','r3_content_sha256':sha(R3PATH.read_bytes()),'r4_runtime_sha256':sha(R4PATH.read_bytes()),'r5_content_sha256':sha(R5PATH.read_bytes()),'r5_runtime_sha256':sha(OUT.read_bytes()),'r5_runtime_entries_hash':out['integrity']['entries_sha256'],'r5_runtime_payload_hash':out['integrity']['payload_sha256'],'exact_unchanged_unit_content':68,'exact_unchanged_entry_count':13,'question_updated_entry_count':55,'question_replacements_q04':55,'question_repairs_q03':3,'total_questions':340,'fulltext_grammar_exact_unchanged':4620,'proof':'Each of 68 v505 entries projected exactly from R5 master via source-bound mapping; full record unit bytes equal to R4; IDs untouched; no browser import','stage4':'HOLD','stage5':'CANDIDATE_PREENTRY','stage6':'NOT_RUN','stage7':'NOT_RELEASED'}
(P/'LESEN-R5-TRANSPORT-EVIDENCE-20261107.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))