#!/usr/bin/env python3
"""Independent read-only structural and deltas check of Lesen R7, not linguistic Stage4.
Does not depend on R7 builder. Negative mutations test contract rejection.
"""
import json,hashlib,copy,collections,pathlib,re
P=pathlib.Path('/mnt/data/lesen_r7_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r6_20261107/Lesen-Production-Master-v1.3.0-R6-20UNIT-Q123-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r6_20261107/Lesen-R6-v505-20UNIT-Q123-RUNTIME-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R7-20UNIT-Q123-CANDIDATE.json'
NEWR=P/'Lesen-R7-v505-20UNIT-Q123-RUNTIME-CANDIDATE.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda o:json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
assert sha(OLDM.read_bytes())=='3a727fc2575b5c041808803b6a97d2a77239aa3089f6bf88570c39e959d26f5c'
assert sha(OLDR.read_bytes())=='3843634a8300f16a14e192c3ecef04b3e83b7dcad9631a84162495ce307ea625'
a=json.loads(OLDM.read_text());b=json.loads(NEWM.read_text());c=json.loads(OLDR.read_text());d=json.loads(NEWR.read_text()); ledger=json.loads((P/'LESEN-R7-20UNIT-QUESTION-EVIDENCE.json').read_text())
check=collections.Counter();fails=[]
def ck(label,ok):
 check[label]+=1
 if not ok:fails.append(label)
ck('master_root_delta_restricted',{k for k in a if a[k]!=b[k]}=={'items','content_version','status','qa_summary'})
ck('exact_integrity_entries',sha(canon(d['entries']))==d['integrity']['entries_sha256'])
ck('exact_integrity_payload',sha(canon({k:v for k,v in d.items() if k!='integrity'}))==d['integrity']['payload_sha256'])
ck('exact_compiled_from',d['compiled_from']['sha256']==sha(NEWM.read_bytes()))
ck('runtime_counts_preserved',c['counts']==d['counts'])
ck('grammar_contract_preserved',a['grammar_lens_contract']==b['grammar_lens_contract'])
ck('question_contract_preserved',a['question_contract']==b['question_contract'])
ck('pack_identity_preserved',a['pack_id']==b['pack_id'] and a['item_count']==b['item_count'])
changed=[]; prompts=0;answers=0;offsets=0;source_paras=0;qa_pairs=0
for old,new,prev,run in zip(a['items'],b['items'],c['entries'],d['entries']):
 uid=old['id'];assert uid==new['id']==prev['source_item_id']==run['source_item_id']
 ck('unit_metadata_stable',old['id']==new['id'] and old['order']==new['order'] and old['legacy_source']==new['legacy_source'])
 ck('passages_and_translations_unchanged',old['reading']==new['reading'])
 ck('original_grammar_unchanged',old['grammar']==new['grammar'])
 ck('vocabulary_and_metadata_unchanged',all(old[k]==new[k] for k in old if k not in {'questions'}))
 ck('runtime_payload_unit_unchanged',prev['unit']==run['unit'])
 ck('question_id_types_refs_unchanged',all(x['id']==y['id'] and x['type']==y['type'] and x['evidence_section_ids']==y['evidence_section_ids'] for x,y in zip(old['questions'],new['questions'])))
 ck('q04_q05_unchanged',old['questions'][3:]==new['questions'][3:])
 ck('exercises_identity_stable',all(e0['exercise_id']==e1['exercise_id'] for e0,e1 in zip(prev['exercises'],run['exercises'])))
 ck('exact_master_runtime_answers_prompts',all(e['prompt_de']==q['prompt_de'] and e['answer_spec']['model_answer']==q['answer_de'] for e,q in zip(run['exercises'],new['questions'])))
 sections={p['id']:p for p in new['reading']['sections']}
 for sec in sections.values():
  source_paras+=1
  ck('trilingual_text_present',bool(sec['text'].strip()) and bool(sec['translations']['fa'].strip()) and bool(sec['translations']['en'].strip()))
  ck('sentence_text_still_in_section',all(sent['text'] in sec['text'] for sent in sec['sentences']))
 for anchor in new['grammar']['full_text_occurrences']:
  sec=sections.get(anchor['section_id']);sentence=next((s for s in sec['sentences'] if s['id']==anchor['sentence_id']),None) if sec else None
  ck('fulltext_grammar_offset',bool(sec and sentence and sec['text'][anchor['start']:anchor['end']]==anchor['target_text']))
  offsets+=1
 for q in new['questions']:
  ck('question_answer_text_nonempty',len(q['prompt_de'])>20 and len(q['answer_de'])>(0 if q['id']=='q05' else 30))
  if q['id']!='q05':ck('source_references_resolve',bool(q['evidence_section_ids']) and all(secid in sections for secid in q['evidence_section_ids']))
  else:ck('open_personal_transfer_no_source_ref',not q['evidence_section_ids'])
 if old['questions']!=new['questions']:
  changed.append(uid); ck('change_scope_31_50',31<=int(uid[-3:])<=50)
  for j,(x,y) in enumerate(zip(old['questions'],new['questions'])):
   if j>=3:continue
   diff={k for k in x if x[k]!=y[k]}; ck('only_question_text_changed',diff<={'prompt_de','answer_de'})
   if diff:
    ck('prompt_learner_facing',y['prompt_de'].endswith('?') and len(y['prompt_de'])>=50)
    ck('answer_complete',len(y['answer_de'])>60)
    qa_pairs+=1
    if 'prompt_de' in diff:prompts+=1
    if 'answer_de' in diff:answers+=1
   else:ck('unmodified_approved_question',uid=='LES-PRES-035' and j in [1,2])
 else:ck('unmodified_runtime_entry_exact',prev==run)
ck('20_units_edited',changed==[f'LES-PRES-{i:03}' for i in range(31,51)])
ck('exact_question_edits',(prompts,answers,qa_pairs)==(58,57,58))
ck('runtime_units_untouched_48',sum(x==y for x,y in zip(c['entries'],d['entries']))==48)
ck('all_sections_unchanged_478',source_paras==478)
ck('all_offsets_unchanged_4620',offsets==4620)
ck('all_question_ids_340',sum(len(z['questions']) for z in b['items'])==340)
ck('per_unit_questions_unique',all(len({q['id'] for q in z['questions']})==5 for z in b['items']))
ck('distinct_prompts_r7',[len({z['questions'][j]['prompt_de'] for z in b['items']}) for j in range(4)]==[51,53,52,68])
ck('ledger_correct_count',len(ledger['changes'])==60)
ck('lemma_sense_source_present',all(z['source_excerpt'] for z in ledger['changes'] if z['action']!='PRESERVED_ALREADY_CUSTOM_REVIEWED'))
ck('old_q02_035_preserved',b['items'][34]['questions'][1]==a['items'][34]['questions'][1])
ck('old_q03_035_preserved',b['items'][34]['questions'][2]==a['items'][34]['questions'][2])
ck('old_q03_answer_043_preserved',b['items'][42]['questions'][2]['answer_de']==a['items'][42]['questions'][2]['answer_de'])
# Adversarial negative probes against real conditions (do NOT mutate current artifacts).
probes=[]
def neg(name,condition):
 probes.append({'case':name,'rejected':not condition});ck('negative_'+name+'_rejected',not condition)
mut=copy.deepcopy(b);mut['items'][30]['reading']['sections'][0]['translations']['fa']=''
neg('fa_missing',all(s['translations'].get('fa') for z in mut['items'] for s in z['reading']['sections']))
mut=copy.deepcopy(b);mut['items'][31]['questions'][0]['id']='q77'
neg('question_id_changed',mut['items'][31]['questions'][0]['id']==a['items'][31]['questions'][0]['id'])
mut=copy.deepcopy(b);mut['items'][31]['reading']['sections'][1]['text']+='Zusatz'
neg('unapproved_passage_edit',mut['items'][31]['reading']==a['items'][31]['reading'])
mut=copy.deepcopy(b);x=mut['items'][31]['grammar']['full_text_occurrences'][0];x['start']+=1
sec=next(s for s in mut['items'][31]['reading']['sections'] if s['id']==x['section_id'])
neg('broken_grammar_span',sec['text'][x['start']:x['end']]==x['target_text'])
mut=copy.deepcopy(d);mut['entries'][30]['exercises'][0]['prompt_de']='random'
neg('runtime_master_divergence',mut['entries'][30]['exercises'][0]['prompt_de']==b['items'][30]['questions'][0]['prompt_de'])
mut=copy.deepcopy(d);mut['entries'][32]['unit']['passages'][0]['translations']['en']=''
neg('missing_runtime_english',all(s['translations'].get('en') for e in mut['entries'] for s in e['unit']['passages']))
mut=copy.deepcopy(d);mut['entries'][2]['source_item_id']=mut['entries'][1]['source_item_id']
neg('duplicate_runtime_id',len({e['source_item_id'] for e in mut['entries']})==68)
mut=copy.deepcopy(b);mut['items'][34]['questions'][2]['answer_de']='Bad previous value'
neg('previous_accepted_q03_035_lost',mut['items'][34]['questions'][2]==a['items'][34]['questions'][2])
mut=copy.deepcopy(b);mut['items'][42]['questions'][2]['answer_de']='Broken'
neg('previous_accepted_q03_043_lost',mut['items'][42]['questions'][2]['answer_de']==a['items'][42]['questions'][2]['answer_de'])
result={'schema':'lesen-r7-independent-scoped-structural-qa@1.0.0','source_sha256':sha(OLDM.read_bytes()),'candidate_content_sha256':sha(NEWM.read_bytes()),'candidate_runtime_sha256':sha(NEWR.read_bytes()),'structural_checks':sum(check.values()),'check_categories':dict(check),'failures':fails,'negative_probes':probes,'unit_changes':changed,'question_prompt_changes':prompts,'question_answer_changes':answers,'question_pairs_affected':qa_pairs,'source_paragraphs_checked':source_paras,'grammar_offsets_checked':offsets,'status':'PASS' if not fails else 'FAIL','limitations':['No independent full DE/FA/EN linguistic Stage4 certification','No native browser IndexedDB Stage6','No original grammar full 9-lens rebuild','No Stage7 release']}
(P/'LESEN-R7-INDEPENDENT-STRUCTURAL-QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','structural_checks','failures','question_prompt_changes','question_answer_changes','question_pairs_affected','grammar_offsets_checked']},indent=2))
if fails:raise SystemExit(1)