#!/usr/bin/env python3
"""Read-only independent R17->R18 original-generic-26 conclusions source/runtime QA.
Strict structural/data fidelity and adversarial probes; NOT independent semantic Stage4.
"""
import pathlib,json,hashlib,collections,copy,re
P=pathlib.Path('/mnt/data/lesen_r18_20261107')
files=[pathlib.Path('/mnt/data/lesen_r17_20261107/Lesen-Production-Master-v1.3.0-R17-23CONCLUSIONS-TRILINGUAL-CANDIDATE.json'),
pathlib.Path('/mnt/data/lesen_r17_20261107/Lesen-R17-v505-23CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'),
P/'Lesen-Production-Master-v1.3.0-R18-26CONCLUSIONS-TRILINGUAL-CANDIDATE.json',
P/'Lesen-R18-v505-26CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json',
P/'LESEN-R18-26CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json']
a,b,c,d,l=[json.loads(f.read_text()) for f in files]
sha=lambda v:hashlib.sha256(v).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
checks=collections.Counter();errors=[]
def ck(label,condition):
 checks[label]+=1
 if not condition:errors.append(label)
G={'p02':'Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.',
   'p03':'Ein Vorteil auf der einen Seite kann also durchaus neue Probleme auf der anderen Seite erzeugen.'}
expected={(q['lesson_id'],q['section_id']) for q in l['changes']}
changed_ids={f'LES-PRES-{n:03d}' for n in l['changed_units']}
ct={(q['lesson_id'],q['section_id']):q for q in l['changes']}
ck('parent_hashes',sha(files[0].read_bytes())=='593deb6e5ec7cdba2d95f7445589ae5bf6cf17750eb0f8cdbb9c3f4f1a605ad7' and sha(files[1].read_bytes())=='b6258670d91951c05fdc409886c538558388889f3ea0217533aa08c5dd7d1ccd')
ck('candidate_ledger_hash',l['candidate_sha256']==sha(files[2].read_bytes()))
ck('candidate_runtime_source_hash',d['compiled_from']['sha256']==sha(files[2].read_bytes()))
ck('candidate_runtime_entry_hash',d['integrity']['entries_sha256']==sha(canon(d['entries'])))
ck('candidate_runtime_payload_hash',d['integrity']['payload_sha256']==sha(canon({k:v for k,v in d.items() if k!='integrity'})))
ck('runtime_declared_counts',d['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4041})
ck('exact_26_unique_edited_sections',len(expected)==len(l['changes'])==26)
ck('exact_15_changed_units',len(changed_ids)==15 and len(l['changed_units'])==15)
ck('no_edit_059',a['items'][58]==c['items'][58])
ck('no_edit_051',a['items'][50]==c['items'][50])
ck('no_edit_035',a['items'][34]==c['items'][34])
ck('specific_7_preserved_and_19_revised',l['preserved_specific_fa_en_tail_pairs']==7 and l['revised_fa_en_tail_pairs']==19)
revised=0;removed=0;new_markers=0;cur_retarget=0;translated=0;preserved=0
for orig,upd,oldd,newd in zip(a['items'],c['items'],b['entries'],d['entries']):
 uid=orig['id'];changed=uid in changed_ids
 ck('lesson_id_preserved',uid==upd['id']==oldd['source_item_id']==newd['source_item_id'])
 ck('title_order_provenance_preserved',(orig['title_de'],orig['title_fa'],orig['title_en'],orig['order'],orig['legacy_source'])==(upd['title_de'],upd['title_fa'],upd['title_en'],upd['order'],upd['legacy_source']))
 ck('all_questions_exact',orig['questions']==upd['questions'])
 ck('all_vocabulary_exact',orig['vocabulary']==upd['vocabulary'])
 ck('auto_grammar_and_tasks_exact',orig['grammar']['auto_lens_targets']==upd['grammar']['auto_lens_targets'] and orig['grammar']['grammar_tasks']==upd['grammar']['grammar_tasks'])
 ck('stable_curated_grammar_identifiers',[g['id'] for g in orig['grammar']['curated_annotations']]==[g['id'] for g in upd['grammar']['curated_annotations']])
 ck('runtime_master_grammar_exact',upd['grammar']==newd['unit']['r38']['grammar'])
 ck('runtime_master_quality_exact',upd['quality']==newd['unit']['r38']['quality'])
 ck('runtime_master_word_count_exact',upd['reading']['word_count_de']==newd['unit']['r38']['word_count_de'])
 ck('runtime_original_exercise_exact',oldd['exercises']==newd['exercises'])
 ck('runtime_original_vocab_exact',oldd['unit']['r38']['vocabulary']==newd['unit']['r38']['vocabulary'])
 if not changed:
  ck('unaffected_source_object_exact',orig==upd)
  ck('unaffected_runtime_object_exact',oldd==newd)
 else:
  revised+=1
  ck('changed_fields_narrow',{k for k in orig if orig[k]!=upd[k]}=={'reading','grammar','quality'})
  ck('changed_wordcount_exact',upd['reading']['word_count_de']==len(' '.join(s['text'] for s in upd['reading']['sections']).split()))
  for os,ns in zip(orig['reading']['sections'],upd['reading']['sections']):
   key=(uid,ns['id']);changedsec=key in expected
   ck('section_sentence_ids_preserved',os['id']==ns['id'] and [z['id'] for z in os['sentences']]==[z['id'] for z in ns['sentences']])
   if not changedsec:
    ck('unaffected_reading_section_exact',os==ns)
   else:
    q=ct[key]
    ck('actual_old_generic_tail',os['sentences'][-1]['text']==G[ns['id']])
    ck('after_not_generic_and_topic_length',ns['sentences'][-1]['text']!=G[ns['id']] and len(ns['sentences'][-1]['text'])>85)
    ck('editorial_before_after_exact',q['before_de']==os['sentences'][-1]['text'] and q['after_de']==ns['sentences'][-1]['text'])
    ck('original_first_two_sentences_preserved',os['sentences'][:2]==ns['sentences'][:2])
    ck('section_fulltext_equals_sentences',ns['text']==' '.join(z['text'] for z in ns['sentences']))
    ck('section_other_metadata_unchanged',{k for k in os if k not in ('text','sentences','translations')}=={k for k in ns if k not in ('text','sentences','translations')})
    oldspans=[g for g in orig['grammar']['full_text_occurrences'] if g['section_id']==ns['id'] and g['sentence_id']==ns['id']+'-s03']
    removed+=len(oldspans)
    ck('old_generic_span_count',len(oldspans)==(4 if ns['id']=='p02' else 2))
    ck('old_context_markers_removed',not {g['id'] for g in oldspans}&{g['id'] for g in upd['grammar']['full_text_occurrences']})
    for lang in ('fa','en'):
     op=re.split(r'(?<=[.!?؟])\s+',os['translations'][lang]);np=re.split(r'(?<=[.!?؟])\s+',ns['translations'][lang]);
     ck('full_translation_sentence_count',len(op)==len(np)==3)
     ck('translation_original_first_two_preserved',op[:2]==np[:2])
     ck('translation_tail_matches_ledger',q['before_'+lang+'_tail']==op[-1] and q['after_'+lang+'_tail']==np[-1])
     ck('translation_nonempty',all(z.strip() for z in np))
    if os['translations']==ns['translations']:
     preserved+=1;ck('ledger_records_preserved_translation',q['translation_action']=='PRESERVE_ALREADY_SPECIFIC')
    else:
     translated+=1;ck('pair_of_languages_changed',all(os['translations'][lang]!=ns['translations'][lang] for lang in ('fa','en')))
     ck('ledger_records_revised_translation',q['translation_action']=='REVISE_BOTH_FA_EN_TO_MATCH_DE')
  for oann,nann in zip(orig['grammar']['curated_annotations'],upd['grammar']['curated_annotations']):
   if oann!=nann:
    cur_retarget+=1
    ck('curated_retarget_is_original_relative_g06',oann['id']==nann['id']=='g06' and oann['grammar_key']==nann['grammar_key']=='relative_clause' and nann['section_id']=='p02' and nann['sentence_id']=='p02-s03')
    ck('curated_relative_retarget_exact',nann['target_text']==next(s for s in upd['reading']['sections'] if s['id']=='p02')['sentences'][-1]['text'])
    ck('curated_retarget_editorial_provenance',nann.get('annotation_source')=='editorial_source_aligned_relative_clause_r18')
  oldids={g['id'] for g in orig['grammar']['full_text_occurrences']}
  for g in upd['grammar']['full_text_occurrences']:
   if g['id'] not in oldids:
    new_markers+=1
    ck('new_markers_exact_id_prefix',g['id'].startswith('ftg-r18-') and g['annotation_source']=='manual_scoped_r18')
    ck('one_anchor_per_changed_conclusion',(uid,g['section_id']) in expected and g['sentence_id']==g['section_id']+'-s03')
    ck('expected_target_attested_in_ledger',g['target_text']==ct[(uid,g['section_id'])]['new_scoped_grammar_target'] and g['grammar_key']==ct[(uid,g['section_id'])]['new_manually_attested_grammar_key'])
  ck('unchanged_old_offsets_and_payloads_exact',all(g in orig['grammar']['full_text_occurrences'] for g in upd['grammar']['full_text_occurrences'] if g['id'] in oldids))
 for section,passage in zip(upd['reading']['sections'],newd['unit']['passages']):
  ck('v505_full_german_passage_exact',section['text']==passage['text_de'])
  ck('v505_full_fa_en_exact',section['translations']==passage['translations'])
  ck('v505_original_sentence_ids_exact',[s['id'] for s in section['sentences']]==passage['sentence_ids'])
  ck('all_three_languages_present',bool(section['text'] and section['translations']['fa'] and section['translations']['en']))
 for q,ex in zip(upd['questions'],newd['exercises']):
  ck('v505_question_prompt_exact',q['prompt_de']==ex['prompt_de'])
  ck('v505_hidden_answer_exact',q['answer_de']==ex['answer_spec']['model_answer'])
  ck('v505_evidence_section_ids_exact',q['evidence_section_ids']==ex['r38']['evidence_section_ids'])
 for g in upd['grammar']['full_text_occurrences']:
  section=next(s for s in upd['reading']['sections'] if s['id']==g['section_id'])
  sentence=next(s for s in section['sentences'] if s['id']==g['sentence_id'])
  ck('all_4041_grammar_exact_character_offsets',section['text'][g['start']:g['end']]==g['target_text'])
  ck('all_4041_grammar_sentence_scope',g['target_text'] in sentence['text'])
 ck('per_lesson_grammar_ids_unique',len({g['id'] for g in upd['grammar']['full_text_occurrences']})==len(upd['grammar']['full_text_occurrences']))
ck('exact_modified_unit_count',revised==15)
ck('retired_82_previous_generic_anchors',removed==82)
ck('new_26_exact_manual_grammar',new_markers==26)
ck('retarget_11_existing_curated_relative_clauses',cur_retarget==11)
ck('translation_pairs_19_revised_7_preserved',translated==19 and preserved==7)
ck('global_original_generic_p02_zero',sum(next(s for s in u['reading']['sections'] if s['id']=='p02')['sentences'][-1]['text']==G['p02'] for u in c['items'])==0)
ck('global_original_generic_p03_zero',sum(next(s for s in u['reading']['sections'] if s['id']=='p03')['sentences'][-1]['text']==G['p03'] for u in c['items'])==0)
ck('fulltext_grammar_total_4041',sum(len(u['grammar']['full_text_occurrences']) for u in c['items'])==4041)
ck('global_declared_fulltext_total_exact',c['full_text_grammar_qa']['occurrences']==c['full_text_grammar_qa']['offset_exact_matches']==4041)
ck('global_fulltext_lens_count_exact',c['full_text_grammar_qa']['counts']==dict(collections.Counter(g['grammar_key'] for u in c['items'] for g in u['grammar']['full_text_occurrences'])))
ck('original_unmodified_r17_current_pointer',a['pack_id']==c['pack_id'])
# Adversarial tests guard that validation actually rejects plausible mistakes.
neg=[]
def probe(label,mutator,predicate):
 x=copy.deepcopy(c);mutator(x);rejected=not predicate(x);neg.append({'case':label,'rejected':rejected});ck('negative_'+label,rejected)
probe('change_preserved_lesson_059',lambda x:x['items'][58].update(title_de='BAD'),lambda x:x['items'][58]==a['items'][58])
probe('empty_fa_translation',lambda x:x['items'][52]['reading']['sections'][1]['translations'].update(fa=''),lambda x:bool(x['items'][52]['reading']['sections'][1]['translations']['fa']))
probe('empty_en_translation',lambda x:x['items'][52]['reading']['sections'][1]['translations'].update(en=''),lambda x:bool(x['items'][52]['reading']['sections'][1]['translations']['en']))
probe('remove_question',lambda x:x['items'][52]['questions'].pop(),lambda x:len(x['items'][52]['questions'])==5)
probe('corrupt_new_manual_grammar_offset',lambda x:next(g for g in x['items'][52]['grammar']['full_text_occurrences'] if g['id']=='ftg-r18-053-p02-scoped').update(start=99999),lambda x:all(s['text'][g['start']:g['end']]==g['target_text'] for u in x['items'][52:53] for g in u['grammar']['full_text_occurrences'] for s in u['reading']['sections'] if s['id']==g['section_id']))
probe('fake_curated_relative_target',lambda x:next(g for g in x['items'][52]['grammar']['curated_annotations'] if g['id']=='g06').update(target_text='BAD'),lambda x:all(g['target_text'] in next(ss['text'] for s in x['items'][52]['reading']['sections'] for ss in s['sentences'] if ss['id']==g['sentence_id']) for g in x['items'][52]['grammar']['curated_annotations']))
probe('alter_declared_fulltext_total',lambda x:x['full_text_grammar_qa'].update(occurrences=1),lambda x:x['full_text_grammar_qa']['occurrences']==4041)
probe('restore_generic_p02',lambda x:x['items'][52]['reading']['sections'][1]['sentences'][-1].update(text=G['p02']),lambda x:x['items'][52]['reading']['sections'][1]['sentences'][-1]['text']!=G['p02'])
probe('alter_preserved_middle_sentence',lambda x:x['items'][52]['reading']['sections'][1]['sentences'][1].update(text='BAD'),lambda x:x['items'][52]['reading']['sections'][1]['sentences'][1]==a['items'][52]['reading']['sections'][1]['sentences'][1])
status='PASS_SOURCE_STRUCTURE_NOT_FORMAL_SEMANTIC_STAGE4' if not errors and all(z['rejected'] for z in neg) else 'FAIL'
report={'schema':'lesen-r18-independent-source-runtime-QA@1','date':'2026-11-07','parent_sha256':sha(files[0].read_bytes()),'r18_content_sha256':sha(files[2].read_bytes()),'r18_runtime_sha256':sha(files[3].read_bytes()),
'checks_by_type':dict(checks),'checks_total':sum(checks.values()),'error_count':len(errors),'errors':errors[:50],
'negative_cases':neg,'all_negative_cases_rejected':all(z['rejected'] for z in neg),'changed_units':revised,'changed_sections':len(expected),'unaffected_units':53,'retired_old_grammar':removed,'new_attested_scoped_grammar':new_markers,'curated_relative_retargets':cur_retarget,'translation_pairs_revised':translated,'translation_pairs_preserved':preserved,'fulltext_grammar_total':4041,'remaining_original_generic_p02':0,'remaining_original_generic_p03':0,'full_semantic_stage4':'HOLD','native_browser_stage6':'NOT_RUN','stage7':'NOT_RELEASED','status':status}
(P/'LESEN-R18-INDEPENDENT-SOURCE-QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='checks_by_type'},ensure_ascii=False,indent=2))
if status=='FAIL':raise SystemExit(1)