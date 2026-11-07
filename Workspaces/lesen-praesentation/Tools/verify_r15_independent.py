#!/usr/bin/env python3
"""Independent read-only verification of R15 against R14 master/runtime and editorial ledger.
No authoring module import. This intentionally does not certify full semantic Stage4.
"""
import json,pathlib,hashlib,collections,copy,re
P=pathlib.Path('/mnt/data/lesen_r15_20261107');P14=pathlib.Path('/mnt/data/lesen_r14_20261107')
paths=[P14/'Lesen-Production-Master-v1.3.0-R14-14P03-TRILINGUAL-CANDIDATE.json',P14/'Lesen-R14-v505-14P03-RUNTIME-PREENTRY-CANDIDATE.json',P/'Lesen-Production-Master-v1.3.0-R15-25CONCLUSIONS-TRILINGUAL-CANDIDATE.json',P/'Lesen-R15-v505-25CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json',P/'LESEN-R15-25CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json']
a,b,c,d,ledger=[json.loads(z.read_text()) for z in paths]
sha=lambda x:hashlib.sha256(x).hexdigest();canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
checks=collections.Counter();errors=[]
def ck(k,flag):
 checks[k]+=1
 if not flag:errors.append(k)
ck('R14_master_SHA',sha(paths[0].read_bytes())=='40f4eee25d4ea541d33f91f327bc88243ec5e2971419927ae43c2f0035af2568')
ck('R14_runtime_SHA',sha(paths[1].read_bytes())=='84b4e1aa8ad6f9299545eb52b2a730474dfc91e635be5cbd843d8e2bca4ea4f3')
ck('R15_ledger_SHA',sha(paths[2].read_bytes())==ledger['r15_content_sha256'])
ck('R15_runtime_sha',sha(paths[2].read_bytes())==d['compiled_from']['sha256'])
ck('runtime_entries_integrity',sha(canon(d['entries']))==d['integrity']['entries_sha256'])
ck('runtime_payload_integrity',sha(canon({k:v for k,v in d.items() if k!='integrity'}))==d['integrity']['payload_sha256'])
ck('counts68',len(a['items'])==len(b['entries'])==len(c['items'])==len(d['entries'])==68)
ck('schema_consistency',d['schema_version']==b['schema_version']=='lesen.runtime.v1.0.0')
expected={(f'LES-PRES-{n:03d}',sid) for n in range(11,25) for sid in ('p02','p03') if (sid=='p02' or n not in (13,17,21))}
ck('expected25',len(expected)==25)
ck('changed_ledger_keys',{(r['unit_id'],r['section_id']) for r in ledger['before_after']}==expected)
ck('curated_retargets',ledger['curated_relative_clause_samples_retargeted']==9)
ck('no_added_grammar',ledger['new_grammar_extractions']==0)
ck('stale_markers_removed',ledger['old_context_invalidations']==78)
ck('original_generic_tail_remaining',ledger['remaining_exact_generic_p02_s03']==41 and ledger['remaining_exact_generic_p03_s03']==30)
changed_units=[];old_retired=[];newcur=0
for old,new,ore,nre in zip(a['items'],c['items'],b['entries'],d['entries']):
 n=int(old['id'].split('-')[-1]);is_edit=11<=n<=24
 ck('unit_id_source_runtime',old['id']==new['id']==ore['source_item_id']==nre['source_item_id'])
 ck('unit_title_order',(old['title_de'],old['order'])==(new['title_de'],new['order']))
 ck('questions_unchanged',old['questions']==new['questions'])
 ck('vocab_unchanged',old['vocabulary']==new['vocabulary'])
 ck('legacy_source_unchanged',old['legacy_source']==new['legacy_source'])
 ck('grammartasks_unchanged',old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks'])
 ck('auto_lens_unchanged',old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets'])
 ck('stable_curated_ids',[r['id'] for r in old['grammar']['curated_annotations']]==[r['id'] for r in new['grammar']['curated_annotations']])
 ck('entry_exercise_count',len(nre['exercises'])==len(new['questions'])==5)
 ck('original_exercises_runtime_unchanged',ore['exercises']==nre['exercises'])
 ck('runtime_unit_grammar_match',new['grammar']==nre['unit']['r38']['grammar'])
 ck('runtime_unit_quality_match',new['quality']==nre['unit']['r38']['quality'])
 ck('runtime_word_count_match',new['reading']['word_count_de']==nre['unit']['r38']['word_count_de'])
 ck('stable_section_ids',[s['id'] for s in old['reading']['sections']]==[s['id'] for s in new['reading']['sections']])
 if not is_edit:
  ck('unchanged_master_unit',old==new)
  ck('unchanged_runtime_entry',ore==nre)
 else:
  changed_units.append(new['id'])
  ck('edited_unit_fields',{k for k in old if old[k]!=new[k]}=={'reading','grammar','quality'})
  ck('old_non_p02_p03_untouched',all(old['reading']['sections'][j]==new['reading']['sections'][j] for j in range(7) if j not in (1,2)))
  for sid in ('p02','p03'):
   os=next(s for s in old['reading']['sections'] if s['id']==sid)
   ns=next(s for s in new['reading']['sections'] if s['id']==sid)
   edit=(new['id'],sid) in expected
   if not edit:
    ck('unedited_p02_p03_section',os==ns)
    continue
   ck('first_two_de_exact',os['sentences'][:2]==ns['sentences'][:2])
   ck('tail_de_changed',os['sentences'][2]['text']!=ns['sentences'][2]['text'])
   ck('p02_p03_join',ns['text']==' '.join(s['text'] for s in ns['sentences']))
   ck('long_specific_DE_sentence',len(ns['sentences'][2]['text'])>65 and 'Nutzen entstehen' not in ns['sentences'][2]['text'] and 'Vorteil auf der einen Seite' not in ns['sentences'][2]['text'])
   for lang in ('fa','en'):
    po=re.split(r'(?<=[.!?؟])\s+',os['translations'][lang]);pn=re.split(r'(?<=[.!?؟])\s+',ns['translations'][lang])
    ck('three_translation_sentences',len(po)==len(pn)==3)
    if len(po)==len(pn)==3:
     ck('first_two_translation_sentences_same',po[:2]==pn[:2])
     ck('third_translation_sentence_changed',po[-1]!=pn[-1])
     ck('third_translation_sentence_length',len(pn[-1])>45)
   ck('new_wordcount_exact',new['reading']['word_count_de']==len(' '.join(z['text'] for z in new['reading']['sections']).split()))
   before=[r for r in old['grammar']['full_text_occurrences'] if r['section_id']==sid and r['sentence_id']==sid+'-s03']
   after=[r for r in new['grammar']['full_text_occurrences'] if r['section_id']==sid and r['sentence_id']==sid+'-s03']
   old_retired.extend((new['id'],z['id']) for z in before)
   ck('removed_only_old_last_grammar',len(before)==(4 if sid=='p02' else 2) and not after)
  ck('remaining_old_grammar_metadata_exact',all(z in old['grammar']['full_text_occurrences'] for z in new['grammar']['full_text_occurrences']))
  for oo,nn in zip(old['grammar']['curated_annotations'],new['grammar']['curated_annotations']):
   if oo!=nn:
    newcur+=1
    ck('curated_relative_clause_label',oo['grammar_key']==nn['grammar_key']=='relative_clause' and oo['section_id']==nn['section_id']=='p02' and nn['sentence_id']=='p02-s03')
    ck('curated_retarget_provenance',nn.get('annotation_source')=='editorial_verified_relative_clause_r15' and 'not_native_engine' in nn.get('derivation_method',''))
    ck('real_relative_clause_present',any(tok in nn['target_text'] for tok in (', die ',', der ',', das ',', denen ',', in denen ')))
 for sec,pa in zip(new['reading']['sections'],nre['unit']['passages']):
  ck('runtime_de_section_equal',sec['text']==pa['text_de'])
  ck('runtime_translations_equal',sec['translations']==pa['translations'])
  ck('runtime_sentence_ids_equal',[s['id'] for s in sec['sentences']]==pa['sentence_ids'])
  ck('trilingual_nonempty',bool(sec['text']) and bool(sec['translations']['fa']) and bool(sec['translations']['en']))
 for q,ex in zip(new['questions'],nre['exercises']):
  ck('question_runtime_text',q['prompt_de']==ex['prompt_de'])
  ck('question_runtime_answer',q['answer_de']==ex['answer_spec']['model_answer'])
  ck('question_runtime_evidence',q['evidence_section_ids']==ex['r38']['evidence_section_ids'])
 for occ in new['grammar']['full_text_occurrences']:
  sec=next(s for s in new['reading']['sections'] if s['id']==occ['section_id'])
  sent=next(s for s in sec['sentences'] if s['id']==occ['sentence_id'])
  ck('fulltext_target_offset_exact',sec['text'][occ['start']:occ['end']]==occ['target_text'])
  ck('fulltext_target_sentence_containment',occ['target_text'] in sent['text'])
 ck('unique_fulltext_ids',len({z['id'] for z in new['grammar']['full_text_occurrences']})==len(new['grammar']['full_text_occurrences']))
ck('retired78',len(old_retired)==78 and len(set(old_retired))==78)
ck('curated_nine',newcur==9)
ck('14_changed',[f'LES-PRES-{n:03d}' for n in range(11,25)]==changed_units)
ck('count_integrity',d['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4220})
ck('fulltext_qa_count',c['full_text_grammar_qa']['occurrences']==c['full_text_grammar_qa']['offset_exact_matches']==4220)
ck('fulltext_total',sum(len(u['grammar']['full_text_occurrences']) for u in c['items'])==4220)
ck('p02_unchanged_generic_count',sum(u['reading']['sections'][1]['sentences'][-1]['text']==a['items'][10]['reading']['sections'][1]['sentences'][-1]['text'] for u in c['items'])==41)
ck('p03_unchanged_generic_count',sum(u['reading']['sections'][2]['sentences'][-1]['text']==a['items'][10]['reading']['sections'][2]['sentences'][-1]['text'] for u in c['items'])==30)
probes=[]
def neg(name,mutate,predicate):
 obj=copy.deepcopy(c);mutate(obj);fail=not predicate(obj);probes.append({'name':name,'rejected':fail});ck('neg_'+name,fail)
neg('empty_de_last',lambda z:z['items'][10]['reading']['sections'][1]['sentences'][2].update(text=''),lambda z:len(z['items'][10]['reading']['sections'][1]['sentences'][2]['text'])>65)
neg('overwrite_untouched_item',lambda z:z['items'][1].update(title_de='bad'),lambda z:z['items'][1]==a['items'][1])
neg('break_fa',lambda z:z['items'][11]['reading']['sections'][1]['translations'].update(fa=''),lambda z:bool(z['items'][11]['reading']['sections'][1]['translations']['fa']))
neg('break_en',lambda z:z['items'][11]['reading']['sections'][1]['translations'].update(en=''),lambda z:bool(z['items'][11]['reading']['sections'][1]['translations']['en']))
neg('bad_old_offset',lambda z:z['items'][11]['grammar']['full_text_occurrences'][0].update(start=100000),lambda z:all(s['text'][q['start']:q['end']]==q['target_text'] for u in z['items'][:13] for q in u['grammar']['full_text_occurrences'] for s in u['reading']['sections'] if s['id']==q['section_id']))
neg('remove_curated',lambda z:z['items'][11]['grammar']['curated_annotations'].pop(),lambda z:sum(len(u['grammar']['curated_annotations']) for u in z['items'])==669)
neg('destroy_question',lambda z:z['items'][10]['questions'][0].update(prompt_de='bad'),lambda z:z['items'][10]['questions']==a['items'][10]['questions'])
neg('bad_lens_count',lambda z:z['full_text_grammar_qa'].update(occurrences=100),lambda z:z['full_text_grammar_qa']['occurrences']==4220)
neg('edit_source_prefix',lambda z:z['items'][11]['reading']['sections'][1]['sentences'][0].update(text='bad'),lambda z:z['items'][11]['reading']['sections'][1]['sentences'][0]==a['items'][11]['reading']['sections'][1]['sentences'][0])
status='PASS_SCOPED_SOURCE_STRUCTURE_NOT_SEMANTIC_STAGE4' if not errors and all(x['rejected'] for x in probes) else 'FAIL'
result={'schema':'lesen-r15-independent-readonly-source-runtime-qa@1.0.0','date':'2026-11-07','parent_r14_master_sha256':sha(paths[0].read_bytes()),
'parent_r14_runtime_sha256':sha(paths[1].read_bytes()),'r15_master_sha256':sha(paths[2].read_bytes()),'r15_runtime_sha256':sha(paths[3].read_bytes()),
'checks_by_type':dict(checks),'checks_total':sum(checks.values()),'errors_count':len(errors),'errors':errors[:50],
'adversarial_negative_cases':probes,'changed_units':changed_units,'edited_sections':25,'unchanged_units':54,
'old_generic_occurrences_retired':len(old_retired),'curated_examples_retargeted':newcur,'grammar_total':4220,
'remaining_generic_p02':41,'remaining_generic_p03':30,
'formal_independent_semantic_stage4':'HOLD','original_native_grammar_rederivation':False,'real_browser_indexeddb_stage6':'NOT_RUN',
'stage7':'NOT_RELEASED','status':status}
(P/'LESEN-R15-INDEPENDENT-STRUCTURAL-QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='checks_by_type'},ensure_ascii=False,indent=2))
if status=='FAIL':raise SystemExit(1)