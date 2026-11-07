#!/usr/bin/env python3
"""Independent, read-only verifier for Lesen R3 -> v505 candidate transport."""
import collections, hashlib, json, pathlib, sys, zipfile
p=pathlib.Path('/mnt/data');w=p/'lesen_r4_workspace';
src=p/'Lesen-Praesentation-B2-C1-v1.3.0-CONTENT-PRODUCTION-DELIVERY.zip';master=p/'lesen_r3_20261107/Lesen-Production-Master-v1.3.0-R3-3UNIT-GRAMMAR-CANDIDATE.json';cand=w/'Lesen-R3-v505-PREENTRY-RUNTIME-CANDIDATE.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
old_zip=src.read_bytes();new_master=master.read_bytes();new_runtime=cand.read_bytes()
assert sha(old_zip)=='558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565'
assert sha(new_master)=='2b7e29acb973d34e878f76df5135be740c0819934b457265a1fd281ca97c2a8e'
with zipfile.ZipFile(src) as z:
 assert z.testzip() is None
 base=json.loads(z.read('02-Compiled-Runtime/Lesen-Runtime-Pack-v1.0.0.json'))
 original=json.loads(z.read('01-Final-Content/Lesen-Production-Master-v1.3.0.json'))
r3=json.loads(new_master);pack=json.loads(new_runtime)
assert pack['schema_version']==base['schema_version']=='lesen.runtime.v1.0.0'
assert pack['compiled_from']['sha256']==sha(new_master)
assert pack['integrity']['entries_sha256']==sha(canon(pack['entries']))
assert pack['integrity']['payload_sha256']==sha(canon({k:v for k,v in pack.items() if k!='integrity'}))
assert len(pack['entries'])==len(base['entries'])==68
assert pack['counts']['full_text_grammar']==4620
assert set(x['id'] for x in original['items'])==set(x['id'] for x in r3['items'])
changed={'LES-PRES-035','LES-PRES-051','LES-PRES-059'}
checks=collections.Counter();changed_real=[]
for old,new,prev,e in zip(original['items'],r3['items'],base['entries'],pack['entries']):
 id=old['id'];u=e['unit'];p=u['passages'];assert new['id']==prev['source_item_id']==id==e['source_item_id'];assert e['order']==new['order']
 if id not in changed:
  assert e==prev
  checks['retained_entire_runtime_unit_exact']+=1
 else:
  assert e!=prev;changed_real.append(id)
  assert e['unit']['provenance']==prev['unit']['provenance'];checks['changed_unit_provenance_preserved']+=1
  assert e['unit']['r38']['vocabulary']==prev['unit']['r38']['vocabulary'];checks['changed_unit_lexical_entries_preserved']+=1
  assert e['unit']['r38']['grammar']==new['grammar'];checks['changed_unit_grammar_exact_new_master']+=1
 assert len(p)==len(new['reading']['sections']);assert len(e['exercises'])==len(new['questions'])==5
 assert e['unit']['comprehension_exercise_ids']==[q['exercise_id'] for q in e['exercises']]
 for ps,ms in zip(p,new['reading']['sections']):
  assert ps['r38']['source_section_id']==ms['id']
  assert ps['text_de']==ms['text'] and ps['translations']==ms['translations']
  assert ps['sentence_ids']==[s['id'] for s in ms['sentences']]
  assert ps['translations']['fa'].strip() and ps['translations']['en'].strip()
  checks['text_translation_and_sentence_transport']+=1
 for re,q in zip(e['exercises'],new['questions']):
  assert re['r38']['question_id']==q['id']
  assert re['prompt_de']==q['prompt_de']
  assert re['answer_spec']['model_answer']==q['answer_de']
  assert re['r38']['evidence_section_ids']==q['evidence_section_ids']
  checks['question_answer_evidence_transport']+=1
 sections={x['id']:x for x in new['reading']['sections']}
 for occ in u['r38']['grammar']['full_text_occurrences']:
  txt=sections[occ['section_id']]['text'];st=occ['start'];en=occ['end'];assert type(st) is int and type(en) is int and 0<=st<en<=len(txt) and txt[st:en]==occ['target_text']
  assert occ['sentence_id'] in {s['id'] for s in sections[occ['section_id']]['sentences']}
  checks['exact_grammar_offset_and_sentence']+=1
 assert all(not z.get('target_id') for z in new['vocabulary']) # lexical target IDs historically remain absent
checks['same_340_ids']=340
assert changed_real==sorted(changed)
assert checks['retained_entire_runtime_unit_exact']==65
assert checks['text_translation_and_sentence_transport']==478
assert checks['question_answer_evidence_transport']==340
assert checks['exact_grammar_offset_and_sentence']==4620
native=json.loads((w/'LESEN-R3-v505-EXACT-SOURCE-VALIDATOR-QA.json').read_text())
assert native['checks']['candidate_pack_status']=='PASS'
assert native['checks']['all_6_negative_rejected']
assert native['checks']['actual_native_counts']['entries']==68
assert native['checks']['in_memory_projection']['units']==68
assert native['checks']['actual_db_transaction']=='NOT_RUN'
rep={'schema':'lesen-r3-v505-independent-transport-verification@1', 'date':'2026-11-07', 'runtime_sha256':sha(new_runtime),'runtime_bytes':len(new_runtime),'source_r3_master_sha256':sha(new_master), 'source_immutable_zip_sha256':sha(old_zip), 'checks':dict(checks), 'candidate_changed_units':changed_real,'candidate_current_promotion':False, 'v505_exact_source_validation':'PASS', 'six_negative_controls':'6/6 REJECTED','in_memory_record_projection':'PASS', 'full_browser_import':'NOT_RUN', 'whole_content_semantic_stage4':'HOLD_55_REMAINING', 'original_nine_lens_grammar_generator':'NOT_RERUN','source_mutation':False,'user_SRS_FSRS_mutation':False,'status':'PASS_INDEPENDENT_SOURCE_TO_RUNTIME_TRANSPORT_ONLY__NOT_RELEASED'}
out=w/'LESEN-R3-v505-INDEPENDENT-CROSSCHECK.json';out.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n',encoding='utf8');print(json.dumps(rep,ensure_ascii=False,indent=2))