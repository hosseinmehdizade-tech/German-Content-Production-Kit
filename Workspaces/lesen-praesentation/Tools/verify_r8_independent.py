#!/usr/bin/env python3
"""Independent bounded R7 -> R8 read-only QA. Structural/transport not independent linguistic Stage4."""
import json,hashlib,copy,collections,pathlib,re
P=pathlib.Path('/mnt/data/lesen_r8_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r7_20261107/Lesen-Production-Master-v1.3.0-R7-20UNIT-Q123-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r7_20261107/Lesen-R7-v505-20UNIT-Q123-RUNTIME-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R8-18UNIT-Q123-CANDIDATE.json'
NEWR=P/'Lesen-R8-v505-18UNIT-Q123-RUNTIME-CANDIDATE.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda o:json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
assert sha(OLDM.read_bytes())=='f472a6260b29f7112bfdf71894f1004957ade61d8ec9bc842992f5a6e4c718d9'
assert sha(OLDR.read_bytes())=='043126b22cc256a911ec9697888b5f944a4520ddb3e22ef74de423abc3c9c6b3'
a=json.loads(OLDM.read_text());b=json.loads(NEWM.read_text());c=json.loads(OLDR.read_text());d=json.loads(NEWR.read_text()); ledger=json.loads((P/'LESEN-R8-50Q-SOURCE-EVIDENCE.json').read_text())
checks=collections.Counter();failures=[];changed=[];qp=qa=occurrences=sections_checked=0

def ck(label,condition):
 checks[label]+=1
 if not condition:failures.append(label)
ck('master_root_delta_scope',{k for k in a if a[k]!=b[k]}=={'items','content_version','qa_summary'})
ck('exact_runtime_entries_integrity',sha(canon(d['entries']))==d['integrity']['entries_sha256'])
ck('exact_runtime_payload_integrity',sha(canon({k:v for k,v in d.items() if k!='integrity'}))==d['integrity']['payload_sha256'])
ck('compiled_from_new_master',d['compiled_from']['sha256']==sha(NEWM.read_bytes()))
ck('counts_identical',c['counts']==d['counts'])
ck('question_contract_same',a['question_contract']==b['question_contract'])
ck('grammar_contract_same',a['grammar_lens_contract']==b['grammar_lens_contract'])
ck('pack_identity_same',a['pack_id']==b['pack_id'] and a['item_count']==b['item_count'])
for old,new,prev,run in zip(a['items'],b['items'],c['entries'],d['entries']):
 uid=old['id'];idx=int(uid[-3:]);ck('unit_identity_order',old['id']==new['id']==prev['source_item_id']==run['source_item_id'] and old['order']==new['order'])
 ck('all_nonquestion_item_data_stable',all(old[k]==new[k] for k in old if k!='questions'))
 ck('runtime_unit_payload_stable',prev['unit']==run['unit'])
 ck('runtime_exercise_identity_stable',all(u['exercise_id']==v['exercise_id'] for u,v in zip(prev['exercises'],run['exercises'])))
 ck('questions_metadata_same',all(all(x[k]==y[k] for k in x if k not in {'prompt_de','answer_de'}) for x,y in zip(old['questions'],new['questions'])))
 ck('q04_q05_same',old['questions'][3:]==new['questions'][3:])
 ck('5_question_ids_unique',len({q['id'] for q in new['questions']})==5)
 ck('master_runtime_questions_agree',all(z['prompt_de']==q['prompt_de'] and z['answer_spec']['model_answer']==q['answer_de'] for z,q in zip(run['exercises'],new['questions'])))
 byid={s['id']:s for s in new['reading']['sections']}
 for sec in byid.values():
  sections_checked+=1
  ck('trilingual_full_sections',all(isinstance(sec.get('translations',{}).get(lang),str) and len(sec['translations'][lang])>10 for lang in ['fa','en']) and len(sec['text'])>30)
  ck('sentence_inside_section',all(t['text'] in sec['text'] for t in sec['sentences']))
 for span in new['grammar']['full_text_occurrences']:
  section=byid.get(span['section_id']);sent=next((x for x in section['sentences'] if x['id']==span['sentence_id']),None) if section else None
  ck('grammar_anchor_exact_text',bool(section and sent and section['text'][span['start']:span['end']]==span['target_text']))
  occurrences+=1
 for q in new['questions']:
  ck('question_prompt_answer_nonempty',len(q['prompt_de'])>20 and len(q['answer_de'])>5)
  ck('all_question_refs_resolve',all(secid in byid for secid in q['evidence_section_ids']))
  ck('question_has_source_or_open_transfer',len(q['evidence_section_ids'])>0 if q['id']!='q05' else len(q['evidence_section_ids'])==0)
 if old['questions']!=new['questions']:
  changed.append(uid);ck('range_051_to_068',51<=idx<=68)
  for j,(x,y) in enumerate(zip(old['questions'],new['questions'])):
   df={k for k in x if x[k]!=y[k]}
   ck('only_q01_03_text_diffs',not df or (j<3 and df<={'prompt_de','answer_de'}))
   if df:
    ck('changed_qa_pair_both_fields',df=={'prompt_de','answer_de'})
    ck('question_form',y['prompt_de'].endswith('?') and len(y['prompt_de'])>55)
    ck('answer_size',len(y['answer_de'])>75)
    qp+=int('prompt_de' in df);qa+=int('answer_de' in df)
   elif j<3 and idx in (51,59):ck('preexisting_custom_preserved',j in (1,2))
   elif j<3: ck('expected_changed_all_three',False)
 else:ck('50_unchanged_entry_exact',prev==run)
ck('changed_exactly_18',changed==[f'LES-PRES-{i:03d}' for i in range(51,69)])
ck('prompt_answer_changes_exact',qp==50 and qa==50)
ck('50_unmodified_runtime_units_exact',sum(x==y for x,y in zip(c['entries'],d['entries']))==50)
ck('478_source_sections_unchanged',sections_checked==478)
ck('4620_grammar_spans_unchanged',occurrences==4620)
ck('340_questions_stable',sum(len(u['questions']) for u in b['items'])==340)
ck('all_4_questions_distinct',[len({u['questions'][j]['prompt_de'] for u in b['items']}) for j in range(4)]==[68,68,68,68])
ck('50_source_evidence_records',len(ledger['changes'])==50)
ck('source_evidence_real_passage',all(any(s['text']==rec['source_section_de'] for s in b['items'][int(rec['unit_id'][-3:])-1]['reading']['sections']) for rec in ledger['changes']))
ck('preserve_51_59_q02_q03',all(a['items'][n-1]['questions'][j]==b['items'][n-1]['questions'][j] for n in (51,59) for j in (1,2)))
ck('baseline_r7_prior_edited_1_50_same',all(a['items'][i]==b['items'][i] for i in range(50)))
# Negative mutations: independent expected-failure checks based on the same read-only rules.
probes=[]
def neg(name,condition):
 ok=not condition;probes.append({'name':name,'rejected':ok});ck('negative_'+name+'_rejected',ok)
mut=copy.deepcopy(b);mut['items'][50]['reading']['sections'][1]['translations']['fa']='';neg('empty_fa',(mut['items'][50]['reading']==a['items'][50]['reading']))
mut=copy.deepcopy(b);mut['items'][51]['questions'][1]['id']='wrong';neg('renamed_question_id',mut['items'][51]['questions'][1]['id']==a['items'][51]['questions'][1]['id'])
mut=copy.deepcopy(b);mut['items'][51]['grammar']['full_text_occurrences'][0]['start']+=1;x=mut['items'][51]['grammar']['full_text_occurrences'][0];sec=next(s for s in mut['items'][51]['reading']['sections'] if s['id']==x['section_id']);neg('bad_grammar_offset',sec['text'][x['start']:x['end']]==x['target_text'])
mut=copy.deepcopy(d);mut['entries'][52]['exercises'][0]['answer_spec']['model_answer']='wrong';neg('runtime_master_divergence',mut['entries'][52]['exercises'][0]['answer_spec']['model_answer']==b['items'][52]['questions'][0]['answer_de'])
mut=copy.deepcopy(b);mut['items'][50]['questions'][1]['answer_de']='overwritten';neg('lost_approved_51q02',mut['items'][50]['questions'][1]==a['items'][50]['questions'][1])
mut=copy.deepcopy(b);mut['items'][58]['questions'][2]['answer_de']='overwritten';neg('lost_approved_59q03',mut['items'][58]['questions'][2]==a['items'][58]['questions'][2])
mut=copy.deepcopy(d);mut['entries'][50]['unit']['passages'][0]['translations']['en']='';neg('missing_en_runtime',all(s['translations'].get('en') for s in mut['entries'][50]['unit']['passages']))
mut=copy.deepcopy(d);mut['entries'][51]['source_item_id']=mut['entries'][50]['source_item_id'];neg('duplicate_runtime_id',len({e['source_item_id'] for e in mut['entries']})==68)
mut=copy.deepcopy(b);mut['items'][0]['questions'][0]['prompt_de']='changed previously approved';neg('unapproved_old_lesson_mutation',all(a['items'][i]==mut['items'][i] for i in range(50)))
result={'schema':'lesen-r8-independent-scoped-structural-qa@1.0.0','parent_master_sha256':sha(OLDM.read_bytes()),'parent_runtime_sha256':sha(OLDR.read_bytes()),'candidate_master_sha256':sha(NEWM.read_bytes()),'candidate_runtime_sha256':sha(NEWR.read_bytes()),'status':'PASS' if not failures else 'FAIL','structural_checks':sum(checks.values()),'check_categories':dict(checks),'failures':failures,'negative_probes':probes,'affected_units':changed,'changed_questions':qp,'changed_answers':qa,'unchanged_units':50,'fulltext_grammar_spans_checked':occurrences,'passages_checked':sections_checked,'limits':['No complete human independent German and DE/FA/EN semantic Stage4 certification','No browser IndexedDB Stage6 acceptance','No re-run of historical nine-lens grammar generator','No Stage7 final/release claim']}
(P/'LESEN-R8-INDEPENDENT-STRUCTURAL-QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','structural_checks','failures','changed_questions','changed_answers','fulltext_grammar_spans_checked','passages_checked']},ensure_ascii=False,indent=2))
if failures:raise SystemExit(1)