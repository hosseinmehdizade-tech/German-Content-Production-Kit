#!/usr/bin/env python3
"""Independent read-only structural/transport QA for Lesen R9->R10.
Not a human/native independent Stage4 translation evaluation or browser Stage6.
"""
import collections, copy, hashlib, json, pathlib
P=pathlib.Path('/mnt/data/lesen_r10_20261107')
A_PATH=pathlib.Path('/mnt/data/lesen_r9_20261107/Lesen-Production-Master-v1.3.0-R9-10P04-TRILINGUAL-CANDIDATE.json')
C_PATH=pathlib.Path('/mnt/data/lesen_r9_20261107/Lesen-R9-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json')
B_PATH=P/'Lesen-Production-Master-v1.3.0-R10-10P04-TRILINGUAL-CANDIDATE.json'
D_PATH=P/'Lesen-R10-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json'
LEDGER=P/'LESEN-R10-10P04-TRILINGUAL-GRAMMAR-LEDGER.json'
OUT=P/'LESEN-R10-INDEPENDENT-STRUCTURAL-QA.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda obj:json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
assert sha(A_PATH.read_bytes())=='52667254d47987e5f4c4146078fd2c8204e80152de3268cd0eb599fc0c2f8171'
assert sha(C_PATH.read_bytes())=='115a988c339f6fa392091727a7aab10f4456d6b7e04e7678492867e785e5aa59'
A=json.loads(A_PATH.read_text());B=json.loads(B_PATH.read_text());C=json.loads(C_PATH.read_text());D=json.loads(D_PATH.read_text());L=json.loads(LEDGER.read_text())
checks=collections.Counter();fail=[]
def ck(name,v):
 checks[name]+=1
 if not v:fail.append(name)
ck('68_entries',len(A['items'])==len(B['items'])==len(C['entries'])==len(D['entries'])==68)
ck('root_pack_id',A['pack_id']==B['pack_id'] and D['pack_id']==C['pack_id']==A['pack_id']+'-runtime-v1')
ck('runtime_entries_hash',sha(canonical(D['entries']))==D['integrity']['entries_sha256'])
ck('runtime_payload_hash',sha(canonical({k:v for k,v in D.items() if k!='integrity'}))==D['integrity']['payload_sha256'])
ck('runtime_compiled_from_exact',D['compiled_from']['sha256']==sha(B_PATH.read_bytes()))
ck('ledger_exact_sha',L['candidate_sha256']==sha(B_PATH.read_bytes()))
ck('parent_entries_hash',sha(canonical(C['entries']))==C['integrity']['entries_sha256'])
changed=[];old_invalid=[];new_added=[];retarget=[]; shifted=0; retained=0
for a,b,c,d in zip(A['items'],B['items'],C['entries'],D['entries']):
 n=int(b['id'].split('-')[-1]);target=21<=n<=30
 ck('same_id_and_order',a['id']==b['id']==c['source_item_id']==d['source_item_id'] and a['order']==b['order'])
 ck('same_title',a['title_de']==b['title_de'])
 ck('same_question_body',a['questions']==b['questions'])
 ck('same_vocabulary',a['vocabulary']==b['vocabulary'])
 ck('same_legacy_provenance',a['legacy_source']==b['legacy_source'])
 ck('same_grammar_tasks',a['grammar']['grammar_tasks']==b['grammar']['grammar_tasks'])
 ck('same_auto_lens_targets',a['grammar']['auto_lens_targets']==b['grammar']['auto_lens_targets'])
 ck('same_question_ids',[q['id'] for q in a['questions']]==[q['id'] for q in b['questions']])
 ck('same_section_ids',[s['id'] for s in a['reading']['sections']]==[s['id'] for s in b['reading']['sections']])
 ck('same_non_p04_sections',a['reading']['sections'][:3]==b['reading']['sections'][:3] and a['reading']['sections'][4:]==b['reading']['sections'][4:])
 ck('same_runtime_exercises',c['exercises']==d['exercises'])
 ck('runtime_word_count',b['reading']['word_count_de']==d['unit']['r38']['word_count_de'])
 ck('runtime_grammar',d['unit']['r38']['grammar']==b['grammar'])
 ck('runtime_quality',d['unit']['r38']['quality']==b['quality'])
 if not target:
  ck('unchanged_58_master_exact',a==b)
  ck('unchanged_58_runtime_exact',c==d)
 else:
  changed.append(b['id']);sa=a['reading']['sections'][3];sb=b['reading']['sections'][3]
  ck('allowed_fields_only',{k for k in a if a[k]!=b[k]}=={'reading','grammar','quality'})
  ck('old_uses_generic_p04',sa['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.'))
  ck('new_no_generic_p04',not sb['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.'))
  ck('middle_sentence_identical',sa['sentences'][1]==sb['sentences'][1])
  ck('s01_s03_both_revised',sa['sentences'][0]!=sb['sentences'][0] and sa['sentences'][2]!=sb['sentences'][2])
  ck('passage_reassembled',sb['text']==' '.join(x['text'] for x in sb['sentences']))
  ck('translations_changed_nonempty',sa['translations']!=sb['translations'] and all(len(sb['translations'][k])>150 for k in ['fa','en']))
  ck('new_word_count',b['reading']['word_count_de']==len(' '.join(s['text'] for s in b['reading']['sections']).split()))
  ck('new_quality_content_hash',b['quality']['content_hash']==sha(' '.join(s['text'] for s in b['reading']['sections']).encode())[:16])
  ck('runtime_p04_exact',d['unit']['passages'][3]['text_de']==sb['text'] and d['unit']['passages'][3]['translations']==sb['translations'])
  ck('runtime_non_p04_unchanged',all(c['unit']['passages'][i]==d['unit']['passages'][i] for i in list(range(3))+list(range(4,7))))
  po={(x['id'],x['sentence_id']):x for x in a['grammar']['full_text_occurrences'] if x['section_id']=='p04'}
  pn=[x for x in b['grammar']['full_text_occurrences'] if x['section_id']=='p04']
  for x in po.values():
   if x['sentence_id']!='p04-s02':old_invalid.append((b['id'],x['id']))
  for x in pn:
   if x['id'].startswith('ftg-r10-'):
    new_added.append((b['id'],x['id']))
    ck('new_explicit_form',x['grammar_key']=='konjunktiv_ii' and x['annotation_source']=='editorial_scoped_r10' and x['target_text']=='sollten' and x['sentence_id']=='p04-s03')
   else:
    ck('retained_only_s02',x['sentence_id']=='p04-s02' and (x['id'],'p04-s02') in po)
    old=po[(x['id'],'p04-s02')]
    ck('retained_metadata_exact',all(x.get(k)==old.get(k) for k in x if k not in ('start','end')))
    ck('reanchor_correct',x['start']==len(sb['sentences'][0]['text'])+1+sb['sentences'][1]['text'].index(x['target_text']))
    retained+=1;shifted+=int(x['start']!=old['start'])
  for g in b['grammar']['curated_annotations']:
   if g['section_id']=='p04' and g['sentence_id']=='p04-s03':
    retarget.append((b['id'],g['id']))
    ck('curated_old_retarget',g['annotation_source']=='editorial_retarget_r10' and g['target_text']==sb['sentences'][2]['text'])
 for s,p in zip(b['reading']['sections'],d['unit']['passages']):
  ck('all_section_content_exact',s['text']==p['text_de'] and s['translations']==p['translations'])
  ck('all_section_translation_present',all(s['translations'][k].strip() for k in ['fa','en']))
  ck('all_sentence_ids_exact',[x['id'] for x in s['sentences']]==p['sentence_ids'])
 for q,e in zip(b['questions'],d['exercises']):
  ck('all_questions_exact',q['prompt_de']==e['prompt_de'])
  ck('all_answers_exact',q['answer_de']==e['answer_spec']['model_answer'])
  ck('all_question_evidence',q['evidence_section_ids']==e['r38']['evidence_section_ids'])
 for g in b['grammar']['curated_annotations']:
  sec=next(s for s in b['reading']['sections'] if s['id']==g['section_id'])
  sent=next(s for s in sec['sentences'] if s['id']==g['sentence_id'])
  ck('all_curated_grammar_exact',g['target_text'] in sent['text'])
 for g in b['grammar']['full_text_occurrences']:
  sec=next(s for s in b['reading']['sections'] if s['id']==g['section_id'])
  sent=next(s for s in sec['sentences'] if s['id']==g['sentence_id'])
  ck('all_grammar_offsets_exact',sec['text'][g['start']:g['end']]==g['target_text'])
  ck('all_grammar_sentence_membership',g['target_text'] in sent['text'])
 ids=[g['id'] for g in b['grammar']['full_text_occurrences']]
 ck('unique_grammar_ids_per_unit',len(set(ids))==len(ids))
ck('changed_units_exact',changed==[f'LES-PRES-{k:03d}' for k in range(21,31)])
ck('grammar_old_invalidated_count',len(old_invalid)==60)
ck('grammar_new_scoped_count',len(new_added)==10)
ck('grammar_curated_retarget_count',len(retarget)==6)
ck('grammar_shifted_matches_ledger',shifted==L['p04_s02_reanchored'])
ck('grammar_retained_count',retained==sum(e['retained_p04_s02'] for e in L['before_after']))
ck('grammar_total_exact',sum(len(u['grammar']['full_text_occurrences']) for u in B['items'])==D['counts']['full_text_grammar']==B['full_text_grammar_qa']['occurrences']==4520)
ck('curated_total',sum(len(u['grammar']['curated_annotations']) for u in B['items'])==669)
ck('runtime_expected_counts',D['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4520})
ck('question_4_unique',len({u['questions'][3]['prompt_de'] for u in B['items']})==68)
ck('generic_p04_remaining',sum(u['reading']['sections'][3]['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.') for u in B['items'])==35)
negative=[]
def probe(name,change,predicate):
 x=copy.deepcopy(B);change(x);rej=not predicate(x);negative.append({'name':name,'rejected':rej});ck('negative_'+name,rej)
probe('changed_middle_sentence',lambda x:x['items'][20]['reading']['sections'][3]['sentences'][1].update(text='falsified'),lambda x:x['items'][20]['reading']['sections'][3]['sentences'][1]==A['items'][20]['reading']['sections'][3]['sentences'][1])
probe('wrong_question_id',lambda x:x['items'][20]['questions'][0].update(id='wrong'),lambda x:x['items'][20]['questions']==A['items'][20]['questions'])
probe('missing_farsi',lambda x:x['items'][20]['reading']['sections'][3]['translations'].update(fa=''),lambda x:bool(x['items'][20]['reading']['sections'][3]['translations']['fa']))
probe('bad_grammar_start',lambda x:x['items'][20]['grammar']['full_text_occurrences'][-1].update(start=999999),lambda x:all(s['text'][g['start']:g['end']]==g['target_text'] for u in x['items'] for s in u['reading']['sections'] for g in u['grammar']['full_text_occurrences'] if g['section_id']==s['id']))
probe('corrupted_unchanged_unit',lambda x:x['items'][0].update(title_de='corrupted'),lambda x:x['items'][0]==A['items'][0])
probe('wrong_grammar_qa',lambda x:x['full_text_grammar_qa'].update(occurrences=123),lambda x:x['full_text_grammar_qa']['occurrences']==4520)
probe('resurrected_deleted_span',lambda x:x['items'][20]['grammar']['full_text_occurrences'].append(copy.deepcopy(next(g for g in A['items'][20]['grammar']['full_text_occurrences'] if g['section_id']=='p04' and g['sentence_id']=='p04-s01'))),lambda x:len(x['items'][20]['grammar']['full_text_occurrences'])==len(B['items'][20]['grammar']['full_text_occurrences']))
probe('rewritten_answer_without_approval',lambda x:x['items'][21]['questions'][1].update(answer_de='corrupted'),lambda x:x['items'][21]['questions']==A['items'][21]['questions'])
probe('missing_new_k2',lambda x:x['items'][20]['grammar']['full_text_occurrences'].pop(),lambda x:any(g['id']=='ftg-r10-021-p04-k2-advice' for g in x['items'][20]['grammar']['full_text_occurrences']))
qa={'schema':'lesen-r10-independent-static-qa@1.0.0','date':'2026-11-07',
    'parent_content_sha256':sha(A_PATH.read_bytes()),'parent_runtime_sha256':sha(C_PATH.read_bytes()),
    'candidate_content_sha256':sha(B_PATH.read_bytes()),'candidate_runtime_sha256':sha(D_PATH.read_bytes()),
    'checks_total':sum(checks.values()),'failed_count':len(fail),'failed':fail[:20],
    'check_groups':dict(checks),'negative_tests':negative,'all_negative_rejected':all(x['rejected'] for x in negative),
    'changed_lessons':changed,'unchanged_unit_count':58,'changed_p04_sentences':20,
    'old_grammar_invalidated':len(old_invalid),'new_scoped_grammar':len(new_added),
    'curated_retargets':len(retarget),'p04_s02_reanchors':shifted,'fulltext_grammar_total':4520,
    'actual_runtime_source_fidelity':'PASS_IF_ZERO_FAILURES','farsi_english_review':'AI_EDITORIAL_NOT_INDEPENDENT_HUMAN_STAGE4',
    'native_9_lens_grammar':'NOT_RERUN','native_browser_stage6':'NOT_RUN',
    'status':'PASS_SCOPED_STRUCTURE_ONLY_IF_NO_ERRORS__STAGE4_6_7_HOLD'}
OUT.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in qa.items() if k!='check_groups'},ensure_ascii=False,indent=2))
if fail or not qa['all_negative_rejected']:raise SystemExit(1)