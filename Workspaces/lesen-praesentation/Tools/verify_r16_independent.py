#!/usr/bin/env python3
"""Independent read-only R15->R16 source/runtime regression and adversarial probes.
Validates source boundaries and target offsets, not holistic language Stage4.
"""
import json,pathlib,collections,hashlib,copy,re
P=pathlib.Path('/mnt/data/lesen_r16_20261107')
ps=[pathlib.Path('/mnt/data/lesen_r15_20261107/Lesen-Production-Master-v1.3.0-R15-25CONCLUSIONS-TRILINGUAL-CANDIDATE.json'),
pathlib.Path('/mnt/data/lesen_r15_20261107/Lesen-R15-v505-25CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'),
P/'Lesen-Production-Master-v1.3.0-R16-22CONCLUSIONS-TRILINGUAL-CANDIDATE.json',
P/'Lesen-R16-v505-22CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json',
P/'LESEN-R16-22CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json']
a,b,c,d,l=[json.loads(p.read_text()) for p in ps]
sha=lambda x:hashlib.sha256(x).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
assert sha(ps[0].read_bytes())=='efa0fa9ece712f3a045ef47c802efe9230fe1baa366cb43e7f3ba5a8573e4c67'
assert sha(ps[1].read_bytes())=='52b0d807bf1c9ab6dbc80011ddb98d131594ebdb4544981a8d0a1c9c22489e33'
checks=collections.Counter();errors=[]
def ck(name,test):
 checks[name]+=1
 if not test:errors.append(name)
ck('r16_parent_master',l['parent_r15_sha256']==sha(ps[0].read_bytes()))
ck('r16_ledger_sha',l['candidate_sha256']==sha(ps[2].read_bytes()))
ck('r16_compiled_source',d['compiled_from']['sha256']==sha(ps[2].read_bytes()))
ck('r16_integrity_entries',d['integrity']['entries_sha256']==sha(canon(d['entries'])))
ck('r16_integrity_payload',d['integrity']['payload_sha256']==sha(canon({k:v for k,v in d.items() if k!='integrity'})))
ck('schema_master',c['schema_version']==a['schema_version'])
ck('counts_and_integrity',d['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4160})
expected={(f'LES-PRES-{n:03d}',sid) for n in range(25,39) if n!=35 for sid in (('p02','p03') if n in (26,27,28,30,31,32,34,36,38) else ('p02',))}
ck('expected_22_sections',len(expected)==22)
ck('ledger_ids_exact',{(q['id'],q['section_id']) for q in l['changes']}==expected)
ck('strict_legacy_removal',l['obsolete_context_grammar_retired']==70)
ck('manual_relative_count',l['new_exact_manual_relative_occurrences']==10)
ck('translation_preservation',l['preserved_specific_fa_en_translations']==44)
ck('remaining_generic_counts',l['remaining_identical_generic_p02']==28 and l['remaining_identical_generic_p03']==21)
ck('old_R15_untouched_baseline',c['items'][34]==a['items'][34])
ck('source_native_counts',len(c['items'])==len(a['items'])==len(d['entries'])==68)
num_changed=0;old_grammar_retired=0;new_grammar=0;cur_retargets=0
GENERIC={'p02':'Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.','p03':'Ein Vorteil auf der einen Seite kann also durchaus neue Probleme auf der anderen Seite erzeugen.'}
for old,new,oe,ne in zip(a['items'],c['items'],b['entries'],d['entries']):
 n=int(old['id'].split('-')[-1]);edited=25<=n<=38 and n!=35
 ck('identity_preserved',old['id']==new['id']==oe['source_item_id']==ne['source_item_id'])
 ck('item_order_title_unchanged',(old['order'],old['title_de'])==(new['order'],new['title_de']))
 ck('immutable_question_list',old['questions']==new['questions'])
 ck('immutable_vocabulary_list',old['vocabulary']==new['vocabulary'])
 ck('immutable_original_source',old['legacy_source']==new['legacy_source'])
 ck('immutable_grammar_task',old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks'])
 ck('immutable_auto_lenses',old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets'])
 ck('immutable_curated_ids',[z['id'] for z in old['grammar']['curated_annotations']]==[z['id'] for z in new['grammar']['curated_annotations']])
 ck('runtime_exercise_preservation',oe['exercises']==ne['exercises'])
 ck('runtime_grammar_match',new['grammar']==ne['unit']['r38']['grammar'])
 ck('runtime_quality_match',new['quality']==ne['unit']['r38']['quality'])
 ck('runtime_wordcount_match',new['reading']['word_count_de']==ne['unit']['r38']['word_count_de'])
 ck('section_ids_preserved',[s['id'] for s in old['reading']['sections']]==[s['id'] for s in new['reading']['sections']])
 if not edited:
  ck('unchanged_lesson_exact',old==new)
  ck('unchanged_v505_entry_exact',oe==ne)
 else:
  num_changed+=1
  ck('narrow_editorial_field_scope',{k for k in old if old[k]!=new[k]}=={'reading','grammar','quality'})
  ck('all_except_two_passages_untouched',all(os==ns for os,ns in zip(old['reading']['sections'],new['reading']['sections']) if os['id'] not in ('p02','p03')))
  ck('word_count_exact',new['reading']['word_count_de']==len(' '.join(s['text'] for s in new['reading']['sections']).split()))
  for sid in ('p02','p03'):
   os=next(s for s in old['reading']['sections'] if s['id']==sid)
   ns=next(s for s in new['reading']['sections'] if s['id']==sid)
   should=(old['id'],sid) in expected
   if should:
    ck('generic_prior_only',os['sentences'][2]['text']==GENERIC[sid])
    ck('first_two_DE_exact',os['sentences'][:2]==ns['sentences'][:2])
    ck('FA_EN_full_byte_identical',os['translations']==ns['translations'])
    ck('nonempty_specific_new_ending',ns['sentences'][2]['text']!=GENERIC[sid] and len(ns['sentences'][2]['text'])>65)
    ck('new_section_join_exact',ns['text']==' '.join(s['text'] for s in ns['sentences']))
    for lang in ('fa','en'):
     pts=re.split(r'(?<=[.!?؟])\s+',ns['translations'][lang]);ck('three_valid_translation_sentences',len(pts)==3 and len(pts[-1])>=35)
    old_occ=[g for g in old['grammar']['full_text_occurrences'] if g['sentence_id']==sid+'-s03' and g['section_id']==sid]
    new_occ=[g for g in new['grammar']['full_text_occurrences'] if g['sentence_id']==sid+'-s03' and g['section_id']==sid]
    old_grammar_retired+=len(old_occ)
    ck('old_grammar_count',(sid=='p02' and len(old_occ)==4) or (sid=='p03' and len(old_occ)==2))
    ck('old_grammar_ids_retired',not {g['id'] for g in old_occ}&{g['id'] for g in new_occ})
    ck('manual_occurrence_count',len(new_occ)==int(bool([z for z in new['grammar']['curated_annotations'] if z['section_id']==sid and z['sentence_id']==sid+'-s03'])))
    new_grammar+=len(new_occ)
    for g in new_occ:
     ck('actual_relative_clause',g['grammar_key']=='relative_clauses_all' and bool(re.search(r'\b(die|der|das|denen)\b',g['target_text'])))
     ck('provenance_manual',g.get('annotation_source')=='manual_scoped_verified_r16')
   else:ck('nonedited_section_byte_identical',os==ns)
  ck('older_fulltext_all_survive_except_last',all(g in old['grammar']['full_text_occurrences'] for g in new['grammar']['full_text_occurrences'] if not g['id'].startswith('ftg-r16-')))
  for x,y in zip(old['grammar']['curated_annotations'],new['grammar']['curated_annotations']):
   if x!=y:
    cur_retargets+=1
    ck('curated_legitimate_relative',x['grammar_key']==y['grammar_key']=='relative_clause' and x['section_id']==y['section_id']=='p02' and y['sentence_id']=='p02-s03')
    ck('curated_relative_attested',', die ' in y['target_text'] or ', der ' in y['target_text'])
    ck('curated_source_provenance',y.get('annotation_source')=='editorial_reviewed_relative_clause_r16')
 for sec,passage in zip(new['reading']['sections'],ne['unit']['passages']):
  ck('runtime_passage_DE_exact',sec['text']==passage['text_de'])
  ck('runtime_passage_translations_exact',sec['translations']==passage['translations'])
  ck('runtime_passage_sentences_exact',[s['id'] for s in sec['sentences']]==passage['sentence_ids'])
  ck('trilingual_nonempty',bool(sec['text']) and bool(sec['translations']['fa']) and bool(sec['translations']['en']))
 for q,ex in zip(new['questions'],ne['exercises']):
  ck('runtime_question_exact',q['prompt_de']==ex['prompt_de'])
  ck('runtime_answer_exact',q['answer_de']==ex['answer_spec']['model_answer'])
  ck('runtime_question_evidence',q['evidence_section_ids']==ex['r38']['evidence_section_ids'])
 for g in new['grammar']['full_text_occurrences']:
  sec=next(z for z in new['reading']['sections'] if z['id']==g['section_id']);sent=next(z for z in sec['sentences'] if z['id']==g['sentence_id'])
  ck('grammar_offset_exact',sec['text'][g['start']:g['end']]==g['target_text'])
  ck('grammar_sentence_ownership',g['target_text'] in sent['text'])
 ck('unique_grammar_ids_per_lesson',len({x['id'] for x in new['grammar']['full_text_occurrences']})==len(new['grammar']['full_text_occurrences']))
ck('changed13',num_changed==13)
ck('retired70',old_grammar_retired==70)
ck('manual10',new_grammar==10)
ck('retarget10',cur_retargets==10)
ck('grammar_total4160',sum(len(z['grammar']['full_text_occurrences']) for z in c['items'])==4160)
ck('master_qa_count4160',c['full_text_grammar_qa']['occurrences']==c['full_text_grammar_qa']['offset_exact_matches']==4160)
ck('remaining_p02_generic28',sum(next(s for s in x['reading']['sections'] if s['id']=='p02')['sentences'][-1]['text']==GENERIC['p02'] for x in c['items'])==28)
ck('remaining_p03_generic21',sum(next(s for s in x['reading']['sections'] if s['id']=='p03')['sentences'][-1]['text']==GENERIC['p03'] for x in c['items'])==21)
probes=[]
def probe(label,mutation,predicate):
 x=copy.deepcopy(c);mutation(x);rejected=not predicate(x)
 probes.append({'case':label,'rejected':rejected});ck('adversarial_'+label,rejected)
probe('overwrite_untouched_lesson',lambda x:x['items'][34].update(title_de='INVALID'),lambda x:x['items'][34]==a['items'][34])
probe('destroy_Persian_translation',lambda x:x['items'][25]['reading']['sections'][1]['translations'].update(fa=''),lambda x:bool(x['items'][25]['reading']['sections'][1]['translations']['fa']))
probe('destroy_English_translation',lambda x:x['items'][25]['reading']['sections'][1]['translations'].update(en=''),lambda x:bool(x['items'][25]['reading']['sections'][1]['translations']['en']))
probe('remove_question',lambda x:x['items'][25]['questions'].pop(),lambda x:len(x['items'][25]['questions'])==5)
probe('invalid_grammar_offset',lambda x:x['items'][24]['grammar']['full_text_occurrences'][0].update(start=999999),lambda x:all(z['text'][g['start']:g['end']]==g['target_text'] for u in x['items'][24:25] for g in u['grammar']['full_text_occurrences'] for z in u['reading']['sections'] if z['id']==g['section_id']))
probe('destroy_curated_relative',lambda x:x['items'][24]['grammar']['curated_annotations'][-1].update(target_text='FAKE'),lambda x:all(q['target_text'] in next(t for s in x['items'][24]['reading']['sections'] if s['id']==q['section_id'] for t in [next(v['text'] for v in s['sentences'] if v['id']==q['sentence_id'])]) for q in x['items'][24]['grammar']['curated_annotations']))
probe('bad_declared_grammar',lambda x:x['full_text_grammar_qa'].update(occurrences=2),lambda x:x['full_text_grammar_qa']['occurrences']==4160)
probe('generic_tail_restored',lambda x:x['items'][25]['reading']['sections'][1]['sentences'][2].update(text=GENERIC['p02']),lambda x:x['items'][25]['reading']['sections'][1]['sentences'][2]['text']!=GENERIC['p02'])
probe('changed_source_first_sentence',lambda x:x['items'][25]['reading']['sections'][1]['sentences'][0].update(text='bad'),lambda x:x['items'][25]['reading']['sections'][1]['sentences'][0]==a['items'][25]['reading']['sections'][1]['sentences'][0])
status='PASS_SCOPED_INDEPENDENT_STRUCTURE_NOT_HOLISTIC_STAGE4' if not errors and all(x['rejected'] for x in probes) else 'FAIL'
result={'schema':'lesen-r16-independent-source-runtime-QA@1.0.0','date':'2026-11-07',
'parent_master_sha256':sha(ps[0].read_bytes()),'parent_runtime_sha256':sha(ps[1].read_bytes()),
'r16_master_sha256':sha(ps[2].read_bytes()),'r16_runtime_sha256':sha(ps[3].read_bytes()),
'checks_by_type':dict(checks),'checks_total':sum(checks.values()),'errors':errors[:40],'error_count':len(errors),
'negative_cases':probes,'all_adversarial_rejected':all(x['rejected'] for x in probes),
'changed_units':num_changed,'changed_conclusions':len(expected),'untouched_units':55,
'retired_grammar':old_grammar_retired,'scoped_new_relative':new_grammar,'curated_retargets':cur_retargets,'grammar_total':4160,
'remaining_generic_p02':28,'remaining_generic_p03':21,
'independent_holistic_stage4':'HOLD','full_ninelens_rerun':False,'browser_stage6':'NOT_RUN','stage7':'NOT_RELEASED','status':status}
(P/'LESEN-R16-INDEPENDENT-SOURCE-QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='checks_by_type'},ensure_ascii=False,indent=2))
if status=='FAIL':raise SystemExit(1)