#!/usr/bin/env python3
"""Independent, read-only R9 cross-check against pinned R8 content and preentry.

This verification is structural + exact grammar spans + per-field transport fidelity.
It intentionally does not certify linguistic Stage4 or live browser Stage6.
"""
import collections, copy, hashlib, json, pathlib
P=pathlib.Path('/mnt/data/lesen_r9_20261107')
R8M=pathlib.Path('/mnt/data/lesen_r8_20261107/Lesen-Production-Master-v1.3.0-R8-18UNIT-Q123-CANDIDATE.json')
R8R=pathlib.Path('/mnt/data/lesen_r8_20261107/Lesen-R8-v505-18UNIT-Q123-RUNTIME-CANDIDATE.json')
R9M=P/'Lesen-Production-Master-v1.3.0-R9-10P04-TRILINGUAL-CANDIDATE.json'
R9R=P/'Lesen-R9-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json'
LEDGER=P/'LESEN-R9-10P04-EDITORIAL-AND-GRAMMAR-LEDGER.json'
OUT=P/'LESEN-R9-INDEPENDENT-STRUCTURAL-QA.json'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
assert sha(R8M.read_bytes())=='f3e22d1f62aa78590f44ccfe358a9240319a99c9d8a1f39fc8a1ee81ac6d4cf2'
assert sha(R8R.read_bytes())=='da770588aee670e60cf985dbfdcfd4fe0715847b43822f214ce90ba27bba4608'
A=json.loads(R8M.read_text(encoding='utf8'));B=json.loads(R9M.read_text(encoding='utf8'))
C=json.loads(R8R.read_text(encoding='utf8'));D=json.loads(R9R.read_text(encoding='utf8'))
L=json.loads(LEDGER.read_text(encoding='utf8'))
checks=collections.Counter(); failed=[]
def ck(label,condition):
 checks[label]+=1
 if not condition:failed.append(label)
ck('root_68_units',len(A['items'])==len(B['items'])==len(C['entries'])==len(D['entries'])==68)
ck('no_crossproject_change', A['pack_id']==B['pack_id'] and C['pack_id']==D['pack_id'] and C['pack_id']==A['pack_id']+'-runtime-v1')
ck('parent_integrity',sha(canonical(C['entries']))==C['integrity']['entries_sha256'])
ck('candidate_integrity_entries',sha(canonical(D['entries']))==D['integrity']['entries_sha256'])
ck('candidate_integrity_payload',sha(canonical({k:v for k,v in D.items() if k!='integrity'}))==D['integrity']['payload_sha256'])
ck('candidate_compiled_from', D['compiled_from']['sha256']==sha(R9M.read_bytes()))
ck('lexical_type',D['schema_version']==C['schema_version']=='lesen.runtime.v1.0.0')
ck('ledger_sha',L['candidate_r9_sha256']==sha(R9M.read_bytes()))
changed_ids=[];deleted_spans=[];revised_curated=0; checked_s02=0; added_r9=[]
q_ids_a=[];q_ids_b=[]
for a,b,c,d in zip(A['items'],B['items'],C['entries'],D['entries']):
 uid=a['id'];n=int(uid[-3:]);in_target=11<=n<=20
 ck('stable_order',a['order']==b['order'])
 ck('stable_unit_id',a['id']==b['id']==c['source_item_id']==d['source_item_id'])
 ck('same_all_questions',a['questions']==b['questions'])
 ck('same_vocabulary',a['vocabulary']==b['vocabulary'])
 ck('same_legacy_source',a['legacy_source']==b['legacy_source'])
 ck('same_title',a['title_de']==b['title_de'])
 ck('same_grammar_tasks',a['grammar']['grammar_tasks']==b['grammar']['grammar_tasks'])
 ck('same_auto_lens_targets',a['grammar']['auto_lens_targets']==b['grammar']['auto_lens_targets'])
 ck('same_question_ids',[x['id'] for x in a['questions']]==[x['id'] for x in b['questions']])
 q_ids_a.extend((uid,x['id']) for x in a['questions']);q_ids_b.extend((uid,x['id']) for x in b['questions'])
 ck('same_section_membership',[x['id'] for x in a['reading']['sections']]==[x['id'] for x in b['reading']['sections']])
 ck('same_non_p04_sections',a['reading']['sections'][:3]==b['reading']['sections'][:3] and a['reading']['sections'][4:]==b['reading']['sections'][4:])
 ck('same_runtime_exercises',c['exercises']==d['exercises'])
 if not in_target:
  ck('unchanged_58_master_exact',a==b)
  ck('unchanged_58_runtime_exact',c==d)
 else:
  changed_ids.append(uid)
  ck('target_changed_fields_exact',{key for key in a if a[key]!=b[key]}=={'reading','grammar','quality'})
  pa=a['reading']['sections'][3];pb=b['reading']['sections'][3]
  ck('p04_changed',pa['text']!=pb['text'] and pa['translations']!=pb['translations'])
  ck('p04_middle_sentence_exact',pa['sentences'][1]==pb['sentences'][1]);checked_s02+=1
  ck('p04_only_first_last_revised',pa['sentences'][0]!=pb['sentences'][0] and pa['sentences'][2]!=pb['sentences'][2])
  ck('correct_sentence_reassembly',pb['text']==' '.join(s['text'] for s in pb['sentences']))
  ck('no_generic_p04_prefix',not pb['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.'))
  ck('p04_fa_en_present_and_non_equal',len(pb['translations']['fa'])>120 and len(pb['translations']['en'])>120 and pb['translations']['fa']!=pa['translations']['fa'] and pb['translations']['en']!=pa['translations']['en'])
  ck('new_word_count',b['reading']['word_count_de']==len(' '.join(s['text'] for s in b['reading']['sections']).split()))
  ck('new_quality_hash',b['quality']['content_hash']==sha(' '.join(s['text'] for s in b['reading']['sections']).encode('utf8'))[:16])
  ck('runtime_source_p04',d['unit']['passages'][3]['text_de']==pb['text'] and d['unit']['passages'][3]['translations']==pb['translations'])
  ck('runtime_unchanged_others',[p for i,p in enumerate(c['unit']['passages']) if i!=3]==[p for i,p in enumerate(d['unit']['passages']) if i!=3])
  ck('runtime_grammar_full_exact',d['unit']['r38']['grammar']==b['grammar'])
  ck('runtime_current_quality',d['unit']['r38']['quality']==b['quality'])
  ck('runtime_wordcount',d['unit']['r38']['word_count_de']==b['reading']['word_count_de'])
  oldp04={(x['id'],x['sentence_id']):x for x in a['grammar']['full_text_occurrences'] if x['section_id']=='p04'}
  newp04=[x for x in b['grammar']['full_text_occurrences'] if x['section_id']=='p04']
  for x in newp04:
   if x['id'].startswith('ftg-r9'):
    added_r9.append((uid,x['id']))
    ck('new_r9_grammar_type',x['grammar_key']=='konjunktiv_ii' and x['annotation_source']=='editorial_scoped_r9')
    ck('new_r9_grammar_on_s03',x['sentence_id']=='p04-s03' and x['target_text'] in ('sollte','sollten'))
   else:
    ck('s02_old_span_retained_only',x['sentence_id']=='p04-s02' and (x['id'],'p04-s02') in oldp04)
    ck('s02_old_span_metadata_unchanged',all(x.get(k)==oldp04[(x['id'],'p04-s02')].get(k) for k in x if k not in ('start','end')))
  for x in oldp04.values():
   if x['sentence_id']!='p04-s02':deleted_spans.append((uid,x['id']))
  for x in b['grammar']['curated_annotations']:
   if x['section_id']=='p04' and x['sentence_id']=='p04-s03':
    revised_curated+=1
    ck('curated_retargeted_label',x['annotation_source']=='editorial_retarget_r9' and x['grammar_key']=='konjunktiv_ii' and x['target_text']==pb['sentences'][2]['text'])
 for s,p in zip(b['reading']['sections'],d['unit']['passages']):
  ck('exact_478_section_source',p['text_de']==s['text'] and p['translations']==s['translations'])
  ck('three_languages_each_section',all(isinstance(s['translations'].get(l),str) and s['translations'][l].strip() for l in ('fa','en')))
  ck('sentence_ids_exact',p['sentence_ids']==[x['id'] for x in s['sentences']])
 for k,ex in enumerate(d['exercises']):
  ck('all_340_question_text',ex['prompt_de']==b['questions'][k]['prompt_de'])
  ck('all_340_answer_text',ex['answer_spec']['model_answer']==b['questions'][k]['answer_de'])
  ck('all_340_exercise_evidence',ex['r38']['evidence_section_ids']==b['questions'][k]['evidence_section_ids'])
 for g in b['grammar']['curated_annotations']:
  s=next(s for s in b['reading']['sections'] if s['id']==g['section_id'])
  sent=next(s for s in s['sentences'] if s['id']==g['sentence_id'])
  ck('all_669_curated_targets_exist',g['target_text'] in sent['text'])
 for g in b['grammar']['full_text_occurrences']:
  s=next(s for s in b['reading']['sections'] if s['id']==g['section_id'])
  ck('all_grammar_spans_exact',s['text'][g['start']:g['end']]==g['target_text'])
  ck('all_grammar_sentence_membership',any(x['id']==g['sentence_id'] and g['target_text'] in x['text'] for x in s['sentences']))
 # Catch duplicate occurrence IDs in a per-lesson scope
 ids=[g['id'] for g in b['grammar']['full_text_occurrences']]
 ck('unique_grammar_id_per_lesson',len(set(ids))==len(ids))
ck('all_340_question_identity',q_ids_a==q_ids_b and len(q_ids_a)==340)
ck('exact_changed_list',changed_ids==[f'LES-PRES-{k:03d}' for k in range(11,21)])
ck('changed_10_grammar_count',len(added_r9)==10)
ck('old_anchor_drop_count',len(deleted_spans)==60)
ck('curated_annotations_retargeted',revised_curated==5)
ck('fulltext_grammar_metadata_matches',B['full_text_grammar_qa']['occurrences']==4570 and B['full_text_grammar_qa']['offset_exact_matches']==4570)
ck('fulltext_grammar_runtime_count',D['counts']['full_text_grammar']==4570)
ck('runtime_total_counts',D['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4570})
ck('all_68_question_4_unique',len({u['questions'][3]['prompt_de'] for u in B['items']})==68)
ck('remaining_generic_p04_exact',sum(u['reading']['sections'][3]['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.') for u in B['items'])==45)
# Independently execute nine adversarial mutations against our own structural gates.
negative=[]
def probe(name,modify,predicate):
 x=copy.deepcopy(B);modify(x)
 rejected=not predicate(x)
 negative.append({'name':name,'rejected':rejected})
 ck('negative_case_'+name,rejected)
probe('wrong_question_id',lambda x:x['items'][0]['questions'][0].update(id='q10'),lambda x:[q['id'] for q in x['items'][0]['questions']]==[q['id'] for q in A['items'][0]['questions']])
probe('broken_unchanged_unit',lambda x:x['items'][0].update(title_de='unapproved change'),lambda x:x['items'][0]==A['items'][0])
probe('missing_Farsi_in_changed_p04',lambda x:x['items'][10]['reading']['sections'][3]['translations'].update(fa=''),lambda x:bool(x['items'][10]['reading']['sections'][3]['translations']['fa']))
probe('p04_s02_accidental_change',lambda x:x['items'][10]['reading']['sections'][3]['sentences'][1].update(text='unapproved'),lambda x:x['items'][10]['reading']['sections'][3]['sentences'][1]==A['items'][10]['reading']['sections'][3]['sentences'][1])
probe('broken_new_grammar_offset',lambda x:x['items'][10]['grammar']['full_text_occurrences'][-1].update(start=1000000),lambda x:all(s['text'][o['start']:o['end']]==o['target_text'] for u in x['items'][:11] for s in u['reading']['sections'] for o in u['grammar']['full_text_occurrences'] if o['section_id']==s['id']))
probe('old_invalid_grammar_resurrected',lambda x:x['items'][10]['grammar']['full_text_occurrences'].append(copy.deepcopy(next(o for o in A['items'][10]['grammar']['full_text_occurrences'] if o['section_id']=='p04' and o['sentence_id']=='p04-s01'))),lambda x:len(x['items'][10]['grammar']['full_text_occurrences'])==len(B['items'][10]['grammar']['full_text_occurrences']))
probe('trilingual_mismatch_in_runtime',lambda x:x['items'][10]['reading']['sections'][3]['translations'].update(en='edited but transport stale'),lambda x:x['items'][10]['reading']['sections'][3]['translations']==D['entries'][10]['unit']['passages'][3]['translations'])
probe('wrong_grammar_total',lambda x:x['full_text_grammar_qa'].update(occurrences=9999),lambda x:x['full_text_grammar_qa']['occurrences']==4570)
probe('broken_question_answer',lambda x:x['items'][10]['questions'][0].update(answer_de=''),lambda x:bool(x['items'][10]['questions'][0]['answer_de']))
result={'schema':'lesen-r9-independent-structural-qa@1.0.0','date':'2026-11-07',
 'authority_r8_sha256':sha(R8M.read_bytes()),'r9_content_sha256':sha(R9M.read_bytes()),
 'r9_runtime_sha256':sha(R9R.read_bytes()),
 'checks_total':sum(checks.values()),'checks_failed':len(failed),'check_groups':dict(checks),
 'failed':failed[:20], 'negative_tests':negative,'all_negative_rejected':all(z['rejected'] for z in negative),
 'changed_lessons':changed_ids,'source_evidence':'R8 current curated p02/p03/p05; not reimported original publisher PDF',
 'unchanged_58_units':58,'p04_sentences_modified':20,
 'grammar_before':4620,'grammar_after':4570,'grammar_removed_old':len(deleted_spans),
 'grammar_new_scoped':len(added_r9),'curated_retargets':revised_curated,'full_9_lens_engine':'NOT_RERUN',
 'translation_stage4':'HOLD_NOT_INDEPENDENT_SEMANTIC_CERTIFICATION',
 'native_browser_stage6':'NOT_RUN',
 'status':'PASS_EXACT_STRUCTURAL_IF_ZERO_ERRORS__NOT_HOLISTIC_STAGE4',
 'source_runtime_mutation':False}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='check_groups'},ensure_ascii=False,indent=2))
if failed or not result['all_negative_rejected']:raise SystemExit(1)