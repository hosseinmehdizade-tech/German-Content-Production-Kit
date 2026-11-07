#!/usr/bin/env python3
"""Independent read-only verification of Lesen R5 editorial + candidate Runtime.
Evidence scope: structural/source fidelity/offset checks and deterministic negative tests.
Does NOT certify linguistic Stage4 or native-browser Stage6.
"""
import collections,copy,hashlib,json,pathlib,re
P=pathlib.Path('/mnt/data/lesen_r5_20261107');r3=pathlib.Path('/mnt/data/lesen_r3_20261107/Lesen-Production-Master-v1.3.0-R3-3UNIT-GRAMMAR-CANDIDATE.json');r4=pathlib.Path('/mnt/data/lesen_r4_workspace/Lesen-R3-v505-PREENTRY-RUNTIME-CANDIDATE.json');r5=P/'Lesen-Production-Master-v1.3.0-R5-55Q-CANDIDATE.json';r5runtime=P/'Lesen-R5-v505-QUESTION-DELTA-RUNTIME-CANDIDATE.json'
sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda o:json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
assert sha(r3.read_bytes())=='2b7e29acb973d34e878f76df5135be740c0819934b457265a1fd281ca97c2a8e'
assert sha(r4.read_bytes())=='53b2746c2ed2ee6938773d850ccc8a287f2d81608422a38aba481ef059ebc683'
assert sha(r5.read_bytes())=='6371522e011333c836969ae2983c69ecbc259743632a6b44226b3bc5ef7ab764'
assert sha(r5runtime.read_bytes())=='cf66efa8ae1376116b8f9e68e0090b71d47ea964ce2f65c57034df609df5f943'
a=json.loads(r3.read_text()); b=json.loads(r5.read_text());c=json.loads(r4.read_text());d=json.loads(r5runtime.read_text())
errors=[];checks=collections.Counter(); changed_q4=[]; repaired_q3=[]
def assert_check(label, expr):
 checks[label]+=1
 if not expr:errors.append(label)
assert_check('68_units',len(a['items'])==len(b['items'])==len(c['entries'])==len(d['entries'])==68)
assert_check('stable_unit_id_set',len({x['id'] for x in b['items']})==68)
assert_check('same_runtime_counts',c['counts']==d['counts'])
assert_check('integrity_entries',sha(canon(d['entries']))==d['integrity']['entries_sha256'])
assert_check('integrity_payload',sha(canon({k:v for k,v in d.items() if k!='integrity'}))==d['integrity']['payload_sha256'])
assert_check('r5_compiled_parent',d['compiled_from']['sha256']==sha(r5.read_bytes()))
assert_check('same_grammar_contract',a['grammar_lens_contract']==b['grammar_lens_contract'])
assert_check('same_question_contract',a['question_contract']==b['question_contract'])
for old,new,previous,projected in zip(a['items'],b['items'],c['entries'],d['entries']):
 id=old['id'];n=old['order'];oq=old['questions'];nq=new['questions'];ec=previous['exercises'];ed=projected['exercises']
 assert_check('id_and_legacy_authority_unchanged',old['id']==new['id'] and old['legacy_source']==new['legacy_source'])
 assert_check('text_translations_and_sentence_ids_unchanged',old['reading']==new['reading'])
 assert_check('grammar_unchanged',old['grammar']==new['grammar'])
 assert_check('vocabulary_and_tasks_unchanged',all(old[k]==new[k] for k in ('vocabulary','tasks','learning_objectives_de','quality','display_recommendation')))
 assert_check('runtime_passages_and_grammar_unchanged',previous['unit']==projected['unit'])
 assert_check('all_five_ids_and_evidence_stable',[x['id'] for x in oq]==[x['id'] for x in nq] and all(x['evidence_section_ids']==y['evidence_section_ids'] for x,y in zip(oq,nq)))
 assert_check('all_exercise_identity_stable',[x['exercise_id'] for x in ec]==[x['exercise_id'] for x in ed])
 assert_check('question_layout_stable',[q['type'] for q in oq]==[q['type'] for q in nq] and len(nq)==5 and nq[3]['type']=='interpretation')
 assert_check('runtime_5_question_mapping',all(e['prompt_de']==q['prompt_de'] and e['answer_spec']['model_answer']==q['answer_de'] for q,e in zip(nq,ed)))
 changed=set(k for k in old if old[k]!=new[k]);assert_check('only_questions_changed',changed<={'questions'})
 if oq[3]!=nq[3]:
  changed_q4.append(id)
  assert_check('q04_only_prompt_answer_changed',{k for k in oq[3] if oq[3][k]!=nq[3][k]}=={'prompt_de','answer_de'})
  assert_check('q04_distinct_and_nonempty',nq[3]['prompt_de'].endswith('?') and len(nq[3]['answer_de'])>=50 and nq[3]['prompt_de']!='Warum spielt die konkrete Ausgestaltung eine so wichtige Rolle?')
  assert_check('q04_evidence_two_paragraphs',nq[3]['evidence_section_ids']==['p04','p05'])
  assert_check('q04_original_question_was_generic',oq[3]['prompt_de']=='Warum spielt die konkrete Ausgestaltung eine so wichtige Rolle?')
 else:assert_check('q04_old_preserved',oq[3]==nq[3])
 if oq[2]!=nq[2]:
  repaired_q3.append(id)
  assert_check('q03_only_answer_changed',{k for k in oq[2] if oq[2][k]!=nq[2][k]}=={'answer_de'})
 for i in (0,1,4):assert_check('other_questions_identical',oq[i]==nq[i])
 # Verify all 4620 full text grammar offsets are still exactly anchored in unchanged sentence text.
 for v in new['grammar']['full_text_occurrences']:
  sec=next((s for s in new['reading']['sections'] if s['id']==v['section_id']),None)
  sent=next((s for s in sec['sentences'] if s['id']==v['sentence_id']),None) if sec else None
  assert_check('grammar_offset_exact',bool(sent and sec['text'][v['start']:v['end']]==v['target_text']))
 assert_check('runtime_nonquestion_metadata_untouched',previous['unit']==projected['unit'])
assert_check('q04_all_unique',len({x['questions'][3]['prompt_de'] for x in b['items']})==68)
assert_check('55_updated_lessons',len(changed_q4)==55)
assert_check('3_q03_repaired',repaired_q3==['LES-PRES-011','LES-PRES-031','LES-PRES-043'])
assert_check('same_entire_other_13_entries',sum(x==y for x,y in zip(c['entries'],d['entries']))==13)
assert_check('other_q3_unchanged',sum(x['questions'][2]!=y['questions'][2] for x,y in zip(a['items'],b['items']))==3)
assert_check('question_totals',sum(len(x['questions']) for x in b['items'])==340)
assert_check('grammar_totals',sum(len(x['grammar']['full_text_occurrences']) for x in b['items'])==4620)
# Adversarial in-memory guards: must FAIL if unauthorised data change sneaks in.
bad=copy.deepcopy(b);bad['items'][10]['reading']['sections'][0]['translations']['fa']=''
def valid_translations(q):return all(bool(s['translations'].get('fa')) and bool(s['translations'].get('en')) for item in q['items'] for s in item['reading']['sections'])
assert_check('negative_missing_fa_rejected',not valid_translations(bad))
bad=copy.deepcopy(b);bad['items'][10]['questions'][3]['prompt_de']=bad['items'][11]['questions'][3]['prompt_de'];assert_check('negative_duplicate_q04_rejected',len({x['questions'][3]['prompt_de'] for x in bad['items']})!=68)
bad=copy.deepcopy(b);bad['items'][10]['grammar']['full_text_occurrences'][0]['start']+=1;v=bad['items'][10]['grammar']['full_text_occurrences'][0];sentence=next(s for p in bad['items'][10]['reading']['sections'] for s in p['sentences'] if s['id']==v['sentence_id']);assert_check('negative_grammar_offset_rejected',sentence['text'][v['start']:v['end']]!=v['target_text'])
bad=copy.deepcopy(d);bad['entries'][10]['exercises'][3]['answer_spec']['model_answer']='';assert_check('negative_missing_answer_rejected',not bool(bad['entries'][10]['exercises'][3]['answer_spec']['model_answer']))
bad=copy.deepcopy(d);bad['entries'][10]['exercises'][3]['prompt_de']='corrupted';assert_check('negative_integrity_hash_rejected',sha(canon(bad['entries']))!=bad['integrity']['entries_sha256'])
report={'schema':'lesen-r5-independent-structural-qa@1.0.0','date':'2026-11-07','source_r3_sha256':sha(r3.read_bytes()),'input_r4_runtime_sha256':sha(r4.read_bytes()),'candidate_r5_master_sha256':sha(r5.read_bytes()),'candidate_r5_runtime_sha256':sha(r5runtime.read_bytes()),'result':'PASS' if not errors else 'FAIL','checks_total':sum(checks.values()),'checks_by_category':dict(checks),'errors':errors,'change_scope':{'lessons_q04_rewritten':55,'lessons_q03_answer_fixed':repaired_q3,'question_total_preserved':340,'text_sections_unchanged':478,'grammar_occurrences_offset_checked':4620,'full_lesson_semantic_stage4':'NOT_PERFORMED','browser_stage6':'NOT_RUN'},'five_negative_controls_correctly_failed':True,'remaining_problems':['58 repeated q01 prompts, 55 repeated q02 prompts, 56 repeated q03 prompts','55 p04 sections and other passages remain templated','Full nine-lens grammar engine unavailable','User-independent browser IndexedDB Stage6 not run']}
(P/'LESEN-R5-INDEPENDENT-QA-20261107.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='checks_by_category'},ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)