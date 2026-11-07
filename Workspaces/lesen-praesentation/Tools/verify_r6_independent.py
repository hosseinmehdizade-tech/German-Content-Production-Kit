#!/usr/bin/env python3
"""Independent structural/source-local QA of R6 20-unit 60-Q rewrite; never Stage4/6.
Checks all reading content and grammar positions, with explicit negative data mutations.
"""
import json,collections,hashlib,copy,re,pathlib
P=pathlib.Path('/mnt/data/lesen_r6_20261107')
M5=pathlib.Path('/mnt/data/lesen_r5_20261107/Lesen-Production-Master-v1.3.0-R5-55Q-CANDIDATE.json')
R5=pathlib.Path('/mnt/data/lesen_r5_20261107/Lesen-R5-v505-QUESTION-DELTA-RUNTIME-CANDIDATE.json')
M6=P/'Lesen-Production-Master-v1.3.0-R6-20UNIT-Q123-CANDIDATE.json';R6=P/'Lesen-R6-v505-20UNIT-Q123-RUNTIME-CANDIDATE.json'
sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda o:json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
assert sha(M5.read_bytes())=='6371522e011333c836969ae2983c69ecbc259743632a6b44226b3bc5ef7ab764'
assert sha(R5.read_bytes())=='cf66efa8ae1376116b8f9e68e0090b71d47ea964ce2f65c57034df609df5f943'
a=json.loads(M5.read_text());b=json.loads(M6.read_text());c=json.loads(R5.read_text());d=json.loads(R6.read_text());assert len(b['items'])==len(d['entries'])==68
counts=collections.Counter();fails=[]
def ck(label,condition):
 counts[label]+=1
 if not condition:fails.append(label)
ck('master_field_delta_allowed',{k for k in a if a[k]!=b[k]}=={'items','content_version','status','qa_summary'})
ck('runtime_integrity_entries',sha(canon(d['entries']))==d['integrity']['entries_sha256'])
ck('runtime_integrity_payload',sha(canon({k:v for k,v in d.items() if k!='integrity'}))==d['integrity']['payload_sha256'])
ck('runtime_compiled_from_exact_master',d['compiled_from']['sha256']==sha(M6.read_bytes()))
ck('runtime_count_totals_unchanged',c['counts']==d['counts'])
ck('original_question_contract_kept',a['question_contract']==b['question_contract'])
ck('original_grammar_lens_kept',a['grammar_lens_contract']==b['grammar_lens_contract'])
changed=[];pairs=0;offsets=0;byid={}
for p,q,cr,dr in zip(a['items'],b['items'],c['entries'],d['entries']):
 id=p['id'];byid[id]=q
 ck('unit_id_and_metadata_stable',id==q['id']==cr['source_item_id']==dr['source_item_id'] and p['legacy_source']==q['legacy_source'])
 ck('reading_text_sentences_translations_identical',p['reading']==q['reading'])
 ck('grammar_same',p['grammar']==q['grammar'])
 ck('other_lexical_content_unchanged',all(p[k]==q[k] for k in ('vocabulary','tasks','learning_objectives_de','quality','display_recommendation','title_de','title_fa','title_en')))
 ck('only_questions_in_changed_unit',{k for k in p if p[k]!=q[k]}<={'questions'})
 ck('runtime_nonquestion_unit_exact',cr['unit']==dr['unit'])
 ck('question_ids_types_evidence_preserved',all(pq['id']==nq['id'] and pq['type']==nq['type'] and pq['evidence_section_ids']==nq['evidence_section_ids'] for pq,nq in zip(p['questions'],q['questions'])))
 ck('runtime_question_identity_preserved',[e['exercise_id'] for e in cr['exercises']]==[e['exercise_id'] for e in dr['exercises']])
 ck('master_runtime_q_a_pairs',all(e['prompt_de']==ques['prompt_de'] and e['answer_spec']['model_answer']==ques['answer_de'] for e,ques in zip(dr['exercises'],q['questions'])))
 ck('q04_q05_untouched',all(p['questions'][j]==q['questions'][j] for j in [3,4]))
 sections={s['id']:s for s in q['reading']['sections']}
 for sec in sections.values():ck('trilingual_paragraph_present',bool(sec['text'].strip()) and bool(sec['translations']['fa'].strip()) and bool(sec['translations']['en'].strip()))
 for g in q['grammar']['full_text_occurrences']:
  sec=sections.get(g['section_id'])
  sent=next((x for x in sec['sentences'] if x['id']==g['sentence_id']),None) if sec else None
  ck('exact_fulltext_grammar_offset',bool(sec and sent and sec['text'][g['start']:g['end']]==g['target_text']))
  offsets+=1
 for qn in q['questions']:
  if qn['id']=='q05':
   # q05 is the preexisting open-ended OPINION exercise, intentionally has no source evidence and may have a concise model hint.
   ck('q05_open_opinion_evidence_exception_preserved',qn==p['questions'][4] and not qn['evidence_section_ids'])
  else:
   ck('source_evidence_for_q01_q04_valid',bool(qn['evidence_section_ids']) and all(v in sections for v in qn['evidence_section_ids']))
   ck('source_question_and_answer_nonempty',len(qn['prompt_de'])>20 and len(qn['answer_de'])>30)
 if p['questions']!=q['questions']:
  changed.append(id)
  for j,(pq,nq) in enumerate(zip(p['questions'],q['questions'])):
   if j<3:
    ck('changed_question_only_prompt_answer',{k for k in pq if pq[k]!=nq[k]}=={'prompt_de','answer_de'})
    ck('prompt_is_question_and_has_source_terms',nq['prompt_de'].endswith('?') and len(nq['prompt_de'].split())>=5)
    ck('answer_has_two_clause_or_complete_sentence',len(nq['answer_de'])>85)
    ck('evidence_role_correct',nq['evidence_section_ids']==(['p01','p06'] if j==0 else ['p02'] if j==1 else ['p03']))
    pairs+=1
   else:ck('original_last_two_questions_kept',pq==nq)
 else:ck('untouched_entries_equal',cr==dr)
ck('edited_units_exact_20',changed==[f'LES-PRES-{i:03d}' for i in range(11,31)])
ck('edited_qa_pairs_exact_60',pairs==60)
ck('unchanged_runtime_entries_exact_48',sum(aa==bb for aa,bb in zip(c['entries'],d['entries']))==48)
ck('grammar_count_4620',offsets==4620)
ck('all_question_ids_total_340',sum(len(x['questions']) for x in b['items'])==340)
uniq={f'q0{j}':len({item['questions'][j-1]['prompt_de'] for item in b['items']}) for j in range(1,5)}
ck('question_unique_stats',uniq=={'q01':31,'q02':34,'q03':33,'q04':68})
# Deterministic negative mutation probes, each fails independent exact invariant.
negative=[]
def neg(label,condition):
 negative.append({'test':label,'rejected':not condition});ck('negative_'+label+'_rejected',not condition)
bad=copy.deepcopy(b);bad['items'][11]['reading']['sections'][0]['translations']['fa']=''
neg('missing_persian',all(sec['translations'].get('fa') for item in bad['items'] for sec in item['reading']['sections']))
bad=copy.deepcopy(b);bad['items'][11]['grammar']['full_text_occurrences'][0]['start']+=1
g=bad['items'][11]['grammar']['full_text_occurrences'][0];sec=next(s for s in bad['items'][11]['reading']['sections'] if s['id']==g['section_id'])
neg('broken_grammar_offset',sec['text'][g['start']:g['end']]==g['target_text'])
bad=copy.deepcopy(b);bad['items'][11]['questions'][0]['id']='q99'
neg('wrong_question_identity',bad['items'][11]['questions'][0]['id']==a['items'][11]['questions'][0]['id'])
bad=copy.deepcopy(b);bad['items'][11]['questions'][1]['evidence_section_ids']=['p99']
neg('invalid_evidence',all(x in {s['id'] for s in bad['items'][11]['reading']['sections']} for x in bad['items'][11]['questions'][1]['evidence_section_ids']))
bad=copy.deepcopy(d);bad['entries'][11]['exercises'][0]['prompt_de']='Tampered'
neg('tampered_runtime_integrity',sha(canon(bad['entries']))==bad['integrity']['entries_sha256'])
bad=copy.deepcopy(d);bad['entries'][11]['exercises'][2]['answer_spec']['model_answer']=''
neg('missing_runtime_answer',all(e['answer_spec']['model_answer'] for e in bad['entries'][11]['exercises']))
bad=copy.deepcopy(d);bad['entries'][11]['unit']['passages'][0]['translations']['en']=''
neg('changed_runtime_passage',bad['entries'][11]['unit']==c['entries'][11]['unit'])
report={'schema':'lesen-r6-independent-structural-qa@1.0.0','date':'2026-11-07','result':'PASS' if not fails else 'FAIL','checks_total':sum(counts.values()),'counts_by_category':dict(counts),'failures':fails,'negative_mutations':negative,'exact_r5_master_sha256':sha(M5.read_bytes()),'exact_r6_master_sha256':sha(M6.read_bytes()),'exact_r5_runtime_sha256':sha(R5.read_bytes()),'exact_r6_runtime_sha256':sha(R6.read_bytes()),'changed_units':changed,'changed_question_answer_pairs':pairs,'unique_prompts':uniq,'fulltext_grammar_offsets_verified':offsets,'release_boundaries':{'semantic_linguistic_stage4':'NOT_INDEPENDENTLY_COMPLETED','v505_preentry':'SEPARATE_NATIVE_TEST_REQUIRED','native_chrome_indexeddb_stage6':'NOT_RUN','stage7':'NOT_RELEASED'},'note':'Passing checks prove scope/identity/transport, not the accuracy or naturalness of all reading questions.'}
(P/'LESEN-R6-INDEPENDENT-STRUCTURAL-QA-20261107.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='counts_by_category'},ensure_ascii=False,indent=2))
if fails:raise SystemExit('QA failed: '+','.join(fails[:10]))