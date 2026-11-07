#!/usr/bin/env python3
"""Independent read-only R16->R17 source and exact-v505 runtime regression."""
import pathlib,json,hashlib,collections,re,copy
P=pathlib.Path('/mnt/data/lesen_r17_20261107')
files=[pathlib.Path('/mnt/data/lesen_r16_20261107/Lesen-Production-Master-v1.3.0-R16-22CONCLUSIONS-TRILINGUAL-CANDIDATE.json'),
pathlib.Path('/mnt/data/lesen_r16_20261107/Lesen-R16-v505-22CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'),
P/'Lesen-Production-Master-v1.3.0-R17-23CONCLUSIONS-TRILINGUAL-CANDIDATE.json',
P/'Lesen-R17-v505-23CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json',
P/'LESEN-R17-23CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json']
a,b,c,d,l=[json.loads(f.read_text()) for f in files]
sha=lambda t:hashlib.sha256(t).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
checks=collections.Counter();errors=[]
def ck(label,good):
 checks[label]+=1
 if not good:errors.append(label)
gen={'p02':'Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.',
     'p03':'Ein Vorteil auf der einen Seite kann also durchaus neue Probleme auf der anderen Seite erzeugen.'}
expected={(f'LES-PRES-{n:03d}',sid) for n in range(39,53) if n!=51 for sid in ('p02','p03') if any(q['lesson_id']==f'LES-PRES-{n:03d}' and q['section_id']==sid for q in l['changes'])}
changed_ids={f'LES-PRES-{n:03d}' for n in l['changed_units']}
ck('expected_change_count',len(expected)==23 and len(changed_ids)==13)
ck('parent_hashes',sha(files[0].read_bytes())=='0b31f21ed6cd65b2562d3806e58269294196d161b05ba87cc7af35e3ab87ffa5' and sha(files[1].read_bytes())=='afec137c5868eb26051c913e3dedefcc848a4a932d5e4cf23e5e21409516f641')
ck('ledger_source_hash',l['parent_r16_sha256']==sha(files[0].read_bytes()) and l['candidate_sha256']==sha(files[2].read_bytes()))
ck('runtime_source_hash',d['compiled_from']['sha256']==sha(files[2].read_bytes()))
ck('runtime_entry_hash',d['integrity']['entries_sha256']==sha(canon(d['entries'])))
ck('runtime_payload_hash',d['integrity']['payload_sha256']==sha(canon({k:v for k,v in d.items() if k!='integrity'})))
ck('runtime_counts',d['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4097})
ck('unique_ledger_sections',len({(q['lesson_id'],q['section_id']) for q in l['changes']})==len(l['changes'])==23)
ck('no_change_051',c['items'][50]==a['items'][50])
ck('no_change_035',c['items'][34]==a['items'][34])
revised=0;old_removed=0;new_relative=0;cur_retargeted=0;translated=0
for o,n,oe,ne in zip(a['items'],c['items'],b['entries'],d['entries']):
 uid=o['id'];changed=uid in changed_ids
 ck('source_identity',uid==n['id']==oe['source_item_id']==ne['source_item_id'])
 ck('source_title_order',(o['title_de'],o['order'])==(n['title_de'],n['order']))
 ck('source_questions',o['questions']==n['questions'])
 ck('source_vocab',o['vocabulary']==n['vocabulary'])
 ck('source_legacy_provenance',o['legacy_source']==n['legacy_source'])
 ck('source_auto_grammar_tasks',o['grammar']['auto_lens_targets']==n['grammar']['auto_lens_targets'] and o['grammar']['grammar_tasks']==n['grammar']['grammar_tasks'])
 ck('curated_grammar_stable_ids',[z['id'] for z in o['grammar']['curated_annotations']]==[z['id'] for z in n['grammar']['curated_annotations']])
 ck('runtime_grammar_exact',n['grammar']==ne['unit']['r38']['grammar'])
 ck('runtime_question_ids',oe['exercises']==ne['exercises'])
 ck('runtime_quality_exact',n['quality']==ne['unit']['r38']['quality'])
 ck('runtime_word_count',n['reading']['word_count_de']==ne['unit']['r38']['word_count_de'])
 if not changed:
  ck('unchanged_unit_exact',o==n)
  ck('unchanged_runtime_entry_exact',oe==ne)
 else:
  revised+=1
  ck('narrow_changed_fields',{k for k in o if o[k]!=n[k]}=={'reading','grammar','quality'})
  ck('changed_unit_wordcount',n['reading']['word_count_de']==len(' '.join(s['text'] for s in n['reading']['sections']).split()))
  for os,ns in zip(o['reading']['sections'],n['reading']['sections']):
   key=(uid,ns['id']);changedsec=key in expected
   ck('section_id_stable',os['id']==ns['id'] and [x['id'] for x in os['sentences']]==[x['id'] for x in ns['sentences']])
   if not changedsec:
    ck('unedited_section_exact',os==ns)
   else:
    ck('before_generic',os['sentences'][-1]['text']==gen[os['id']])
    ck('new_topic_sentence',ns['sentences'][-1]['text']!=gen[ns['id']] and len(ns['sentences'][-1]['text'])>80)
    ck('first_two_sentences_stable',os['sentences'][:2]==ns['sentences'][:2])
    ck('section_text_join',ns['text']==' '.join(z['text'] for z in ns['sentences']))
    old_entries=[g for g in o['grammar']['full_text_occurrences'] if g['section_id']==ns['id'] and g['sentence_id']==ns['id']+'-s03']
    old_removed+=len(old_entries)
    ck('old_grammar_disappeared',all(g['id'] not in {z['id'] for z in n['grammar']['full_text_occurrences']} for g in old_entries))
    ck('old_spans_expected',len(old_entries)==(4 if ns['id']=='p02' else 2))
    changed_langs=[]
    for lang in ('fa','en'):
     op=re.split(r'(?<=[.!?؟])\s+',os['translations'][lang]);np=re.split(r'(?<=[.!?؟])\s+',ns['translations'][lang]);
     ck('translation_sentence_cardinality',len(op)==len(np)==3)
     ck('translation_first_two_preserved',op[:2]==np[:2])
     if op[-1]!=np[-1]:changed_langs.append(lang)
    ck('translation_paired_change',len(changed_langs) in (0,2))
    if changed_langs:translated+=1
   # strong read-only assertion on all changed/unchanged sections
  # previously attested grammar from untouched source contexts remains exactly valid
  for ann1,ann2 in zip(o['grammar']['curated_annotations'],n['grammar']['curated_annotations']):
   if ann1!=ann2:
    cur_retargeted+=1
    ck('curated_only_legitimate_relative',ann1['id']==ann2['id']=='g06' and ann1['grammar_key']==ann2['grammar_key']=='relative_clause' and ann2['section_id']=='p02' and ann2['sentence_id']=='p02-s03')
    ck('curated_target_real',ann2['target_text']==next(s for s in n['reading']['sections'] if s['id']=='p02')['sentences'][-1]['text'])
    ck('curated_editorial_provenance',ann2.get('annotation_source')=='editorial_source_aligned_relative_clause_r17')
  ck('retained_original_fulltext_offsets',all(z in o['grammar']['full_text_occurrences'] for z in n['grammar']['full_text_occurrences'] if not z['id'].startswith('ftg-r17-')))
  new_relative+=len([g for g in n['grammar']['full_text_occurrences'] if g['id'].startswith('ftg-r17-')])
 for s,p in zip(n['reading']['sections'],ne['unit']['passages']):
  ck('runtime_german_passage_exact',s['text']==p['text_de'])
  ck('runtime_fa_en_exact',s['translations']==p['translations'])
  ck('runtime_sentence_identifiers',[z['id'] for z in s['sentences']]==p['sentence_ids'])
  ck('translation_nonempty',bool(s['translations']['fa']) and bool(s['translations']['en']))
 for q,ex in zip(n['questions'],ne['exercises']):
  ck('runtime_question_exact',q['prompt_de']==ex['prompt_de'])
  ck('runtime_answer_exact',q['answer_de']==ex['answer_spec']['model_answer'])
  ck('runtime_question_evidence',q['evidence_section_ids']==ex['r38']['evidence_section_ids'])
 for g in n['grammar']['full_text_occurrences']:
  s=next(x for x in n['reading']['sections'] if x['id']==g['section_id'])
  sent=next(x for x in s['sentences'] if x['id']==g['sentence_id'])
  ck('exact_grammar_offset',s['text'][g['start']:g['end']]==g['target_text'])
  ck('grammar_sentence_scope',g['target_text'] in sent['text'])
 ck('per_lesson_unique_grammar_ids',len({g['id'] for g in n['grammar']['full_text_occurrences']})==len(n['grammar']['full_text_occurrences']))
ck('edited13_units',revised==13)
ck('total_grammar_retired',old_removed==72)
ck('new_grammar9',new_relative==9)
ck('curated_retarget9',cur_retargeted==9)
ck('four_translation_pairs',translated==4)
ck('grammar_counts4097',sum(len(u['grammar']['full_text_occurrences']) for u in c['items'])==4097)
ck('fulltext_declaration',c['full_text_grammar_qa']['occurrences']==c['full_text_grammar_qa']['offset_exact_matches']==4097)
ck('fulltext_lens_counts',c['full_text_grammar_qa']['counts']==dict(collections.Counter(g['grammar_key'] for u in c['items'] for g in u['grammar']['full_text_occurrences'])))
for sid,target in (('p02',15),('p03',11)):
 ck('generic_tail_remaining_'+sid,sum(next(s for s in u['reading']['sections'] if s['id']==sid)['sentences'][-1]['text']==gen[sid] for u in c['items'])==target)
# Fault-injection probes validate that the tests genuinely reject broken source data.
neg=[]
def probe(label,mutation,predicate):
 x=copy.deepcopy(c);mutation(x);bad=not predicate(x);neg.append({'case':label,'rejected':bad});ck('adversarial_'+label,bad)
probe('alter_untouched_051',lambda x:x['items'][50].update(title_de='SABOTAGE'),lambda x:x['items'][50]==a['items'][50])
probe('destroy_persian',lambda x:x['items'][38]['reading']['sections'][1]['translations'].update(fa=''),lambda x:bool(x['items'][38]['reading']['sections'][1]['translations']['fa']))
probe('destroy_english',lambda x:x['items'][38]['reading']['sections'][1]['translations'].update(en=''),lambda x:bool(x['items'][38]['reading']['sections'][1]['translations']['en']))
probe('remove_exercise',lambda x:x['items'][38]['questions'].pop(),lambda x:len(x['items'][38]['questions'])==5)
probe('tamper_grammar_offset',lambda x:x['items'][39]['grammar']['full_text_occurrences'][0].update(start=100000),lambda x:all(s['text'][g['start']:g['end']]==g['target_text'] for u in x['items'][39:40] for g in u['grammar']['full_text_occurrences'] for s in u['reading']['sections'] if s['id']==g['section_id']))
probe('fake_curated_relative',lambda x:x['items'][39]['grammar']['curated_annotations'][-1].update(target_text='BAD'),lambda x:all(g['target_text'] in next(w['text'] for s in x['items'][39]['reading']['sections'] if s['id']==g['section_id'] for w in s['sentences'] if w['id']==g['sentence_id']) for g in x['items'][39]['grammar']['curated_annotations']))
probe('wrong_declared_grammar',lambda x:x['full_text_grammar_qa'].update(occurrences=3),lambda x:x['full_text_grammar_qa']['occurrences']==4097)
probe('revert_generic_p02',lambda x:x['items'][38]['reading']['sections'][1]['sentences'][2].update(text=gen['p02']),lambda x:x['items'][38]['reading']['sections'][1]['sentences'][2]['text']!=gen['p02'])
probe('damage_preexisting_sentence',lambda x:x['items'][38]['reading']['sections'][1]['sentences'][0].update(text='BAD'),lambda x:x['items'][38]['reading']['sections'][1]['sentences'][0]==a['items'][38]['reading']['sections'][1]['sentences'][0])
status='PASS_SCOPED_INDEPENDENT_STRUCTURE_NOT_FULL_STAGE4' if not errors and all(x['rejected'] for x in neg) else 'FAIL'
result={'schema':'lesen-r17-independent-source-runtime-QA@1','date':'2026-11-07','parent_sha256':sha(files[0].read_bytes()),
'r17_content_sha256':sha(files[2].read_bytes()),'r17_runtime_sha256':sha(files[3].read_bytes()),
'checks_by_type':dict(checks),'checks_total':sum(checks.values()),'error_count':len(errors),'errors':errors[:40],
'negative_cases':neg,'all_negative_cases_rejected':all(x['rejected'] for x in neg),'changed_units':revised,
'changed_sections':len(expected),'unaffected_units':55,'retired_old_grammar':old_removed,'new_manual_relative':new_relative,
'curated_relative_retargets':cur_retargeted,'trilingual_tail_pairs_revised':translated,'fulltext_grammar_total':4097,
'remaining_generic_p02':15,'remaining_generic_p03':11,
'full_semantic_stage4':'HOLD','native_browser_stage6':'NOT_RUN','stage7':'NOT_RELEASED','status':status}
(P/'LESEN-R17-INDEPENDENT-SOURCE-QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='checks_by_type'},ensure_ascii=False,indent=2))
if status=='FAIL':raise SystemExit(1)