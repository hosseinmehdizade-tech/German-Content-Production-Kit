#!/usr/bin/env python3
"""Independent read-only R14 whole-pack source fidelity/offset + v505 preentry transport QA.
Does NOT approve holistic meaning, native nine-lens extraction or browser IndexedDB stage6.
"""
import json,pathlib,hashlib,collections,copy
P=pathlib.Path('/mnt/data/lesen_r14_20261107')
OM=pathlib.Path('/mnt/data/lesen_r13_20261107/Lesen-Production-Master-v1.3.0-R13-16P04-TRILINGUAL-CANDIDATE.json')
OR=pathlib.Path('/mnt/data/lesen_r13_20261107/Lesen-R13-v505-16P04-RUNTIME-PREENTRY-CANDIDATE.json')
NM=P/'Lesen-Production-Master-v1.3.0-R14-14P03-TRILINGUAL-CANDIDATE.json'
NR=P/'Lesen-R14-v505-14P03-RUNTIME-PREENTRY-CANDIDATE.json'
LED=P/'LESEN-R14-14P03-TRILINGUAL-GRAMMAR-LEDGER.json'
OUT=P/'LESEN-R14-INDEPENDENT-STRUCTURAL-QA.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
a=json.loads(OM.read_text());b=json.loads(NM.read_text());c=json.loads(OR.read_text());d=json.loads(NR.read_text());l=json.loads(LED.read_text())
expected={13,17,21,25,29,33,37,41,45,49,53,57,61,65}
checks=collections.Counter();errors=[];change=[];retired=retained=moved=added=0

def ck(label,ok):
 checks[label]+=1
 if not ok:errors.append(label)
ck('r13_master_sha',sha(OM.read_bytes())=='d619d7d9777849a25a154b52574b66a3dd92fc4f4d045e7b4ceb4e0fbc16b30f')
ck('r13_runtime_sha',sha(OR.read_bytes())=='628f56e6bab608a6ab5f7a8939eea3a8451f1fbc4a8699bcaeb23a56f10d78a7')
ck('source_ledger_pin',sha(NM.read_bytes())==l['r14_master_sha256'])
ck('runtime_master_pin',d['compiled_from']['sha256']==sha(NM.read_bytes()))
ck('runtime_entry_integrity',sha(canon(d['entries']))==d['integrity']['entries_sha256'])
ck('runtime_payload_integrity',sha(canon({k:v for k,v in d.items() if k!='integrity'}))==d['integrity']['payload_sha256'])
ck('runtime_schema',d['schema_version']==c['schema_version']=='lesen.runtime.v1.0.0')
ck('runtime_packid',d['pack_id']==c['pack_id'])
ck('counts68',len(a['items'])==len(b['items'])==len(c['entries'])==len(d['entries'])==68)
for index,(old,new,oe,ne) in enumerate(zip(a['items'],b['items'],c['entries'],d['entries'])):
 n=index+1;editing=n in expected
 ck('unit_id',old['id']==new['id']==ne['source_item_id']==oe['source_item_id']==f'LES-PRES-{n:03d}')
 ck('unit_title',old['title_de']==new['title_de']);ck('unit_order',old['order']==new['order'])
 ck('question_unchanged',old['questions']==new['questions']);ck('vocabulary_unchanged',old['vocabulary']==new['vocabulary'])
 ck('source_unchanged',old['legacy_source']==new['legacy_source'])
 ck('grammar_tasks_unchanged',old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks'])
 ck('curated_grammar_unchanged',old['grammar']['curated_annotations']==new['grammar']['curated_annotations'])
 ck('auto_lens_unchanged',old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets'])
 ck('runtime_questions_unchanged',oe['exercises']==ne['exercises'])
 ck('runtime_grammar',new['grammar']==ne['unit']['r38']['grammar'])
 ck('runtime_quality',new['quality']==ne['unit']['r38']['quality'])
 ck('runtime_wordcount',new['reading']['word_count_de']==ne['unit']['r38']['word_count_de'])
 ck('section_ids_stable',[s['id'] for s in old['reading']['sections']]==[s['id'] for s in new['reading']['sections']])
 if editing:
  change.append(new['id']);s0=old['reading']['sections'][2];s=new['reading']['sections'][2]
  ck('edit_fields_only',{k for k in old if old[k]!=new[k]}=={'reading','grammar','quality'})
  ck('other_sections_stable',old['reading']['sections'][:2]==new['reading']['sections'][:2] and old['reading']['sections'][3:]==new['reading']['sections'][3:])
  ck('old_p03_template',s0['sentences'][0]['text']=='Dem stehen jedoch gewichtige Einwände gegenüber.')
  ck('new_first_last',s['sentences'][0]!=s0['sentences'][0] and s['sentences'][3]!=s0['sentences'][3])
  ck('unchanged_two_middle',s['sentences'][1:3]==s0['sentences'][1:3])
  ck('p03_text_join',s['text']==' '.join(z['text'] for z in s['sentences']))
  ck('new_translation',s['translations']!=s0['translations'] and len(s['translations']['fa'])>170 and len(s['translations']['en'])>185)
  ck('new_wordcount',new['reading']['word_count_de']==len(' '.join(z['text'] for z in new['reading']['sections']).split()))
  ck('new_qualityhash',new['quality']['content_hash']==sha(' '.join(z['text'] for z in new['reading']['sections']).encode())[:16])
  ck('runtime_changed_passage',s['text']==ne['unit']['passages'][2]['text_de'] and s['translations']==ne['unit']['passages'][2]['translations'])
  ck('other_runtime_passages',all(oe['unit']['passages'][j]==ne['unit']['passages'][j] for j in range(7) if j!=2))
  oldmap={z['id']:z for z in old['grammar']['full_text_occurrences'] if z['section_id']=='p03'}
  newocc=[z for z in new['grammar']['full_text_occurrences'] if z['section_id']=='p03']
  retired+=sum(z['sentence_id'] in ('p03-s01','p03-s04') for z in oldmap.values())
  for ann in newocc:
   if ann['id'].startswith('ftg-r14-'):
    added+=1;ck('manual_annotation_flag',ann['annotation_source']=='editorial_scoped_r14' and ann['derivation_method']=='manual_exact_span_not_native_nine_lens')
    ck('manual_key_allowed',ann['grammar_key'] in ('konjunktiv_ii','relative_clauses_all','subordinate_clauses_all','infinitive_with_zu'))
   else:
    ck('old_middle_only',ann['id'] in oldmap and ann['sentence_id'] in ('p03-s02','p03-s03'))
    if ann['id'] in oldmap:
     z=oldmap[ann['id']];retained+=1;moved+=int(z['start']!=ann['start'])
     ck('old_grammar_metadata',all(z.get(k)==ann.get(k) for k in z if k not in ('start','end')))
     old_offset=len(s0['sentences'][0]['text'])+1
     new_offset=len(s['sentences'][0]['text'])+1
     ck('relative_position_in_middle',ann['start']-new_offset==z['start']-old_offset)
 else:
  ck('unchanged_unit',old==new);ck('unchanged_runtime_entry',oe==ne)
 for sec,pas in zip(new['reading']['sections'],ne['unit']['passages']):
  ck('section_text_runtime',sec['text']==pas['text_de'])
  ck('section_translation_runtime',sec['translations']==pas['translations'])
  ck('trilingual_nonempty',bool(sec['text']) and bool(sec['translations']['fa']) and bool(sec['translations']['en']))
  ck('sentence_id_runtime',[z['id'] for z in sec['sentences']]==pas['sentence_ids'])
 for q,ex in zip(new['questions'],ne['exercises']):
  ck('qtext_runtime',q['prompt_de']==ex['prompt_de'])
  ck('qanswer_runtime',q['answer_de']==ex['answer_spec']['model_answer'])
  ck('qevidence_runtime',q['evidence_section_ids']==ex['r38']['evidence_section_ids'])
 for occ in new['grammar']['full_text_occurrences']:
  sec=next(s for s in new['reading']['sections'] if s['id']==occ['section_id'])
  sent=next(s for s in sec['sentences'] if s['id']==occ['sentence_id'])
  ck('exact_fulltext_section_offset',sec['text'][occ['start']:occ['end']]==occ['target_text'])
  ck('grammar_sentence_containment',occ['target_text'] in sent['text'])
 ck('unique_fulltext_id',len({z['id'] for z in new['grammar']['full_text_occurrences']})==len(new['grammar']['full_text_occurrences']))
ck('changed_units_exact',change==[f'LES-PRES-{n:03d}' for n in sorted(expected)])
ck('grammar_retired',retired==l['old_context_markers_removed']==56)
ck('grammar_retained',retained==l['old_mid_markers_retained']==95)
ck('grammar_moved',moved==l['old_mid_markers_shifted']==95)
ck('grammar_new',added==l['new_manual_scoped_markers']==9)
ck('grammar_totals',sum(len(z['grammar']['full_text_occurrences']) for z in b['items'])==d['counts']['full_text_grammar']==b['full_text_grammar_qa']['occurrences']==4298)
ck('pack_counts',d['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4298})
ck('generic_p03_zero',all(z['reading']['sections'][2]['sentences'][0]['text']!='Dem stehen jedoch gewichtige Einwände gegenüber.' for z in b['items']))
ck('preserved_questions_unique',all(len({u['questions'][i]['prompt_de'] for u in b['items']})==68 for i in range(4)))
probes=[]
def neg(name,edit,predicate):
 tmp=copy.deepcopy(b);edit(tmp);rejected=not predicate(tmp);probes.append({'name':name,'rejected':rejected});ck('negative_'+name,rejected)
neg('empty_fa',lambda o:o['items'][12]['reading']['sections'][2]['translations'].update(fa=''),lambda o:bool(o['items'][12]['reading']['sections'][2]['translations']['fa']))
neg('empty_en',lambda o:o['items'][16]['reading']['sections'][2]['translations'].update(en=''),lambda o:bool(o['items'][16]['reading']['sections'][2]['translations']['en']))
neg('mutate_mid_s02',lambda o:o['items'][12]['reading']['sections'][2]['sentences'][1].update(text='bad'),lambda o:o['items'][12]['reading']['sections'][2]['sentences'][1]==a['items'][12]['reading']['sections'][2]['sentences'][1])
neg('mutate_mid_s03',lambda o:o['items'][16]['reading']['sections'][2]['sentences'][2].update(text='bad'),lambda o:o['items'][16]['reading']['sections'][2]['sentences'][2]==a['items'][16]['reading']['sections'][2]['sentences'][2])
neg('grammar_bad_offset',lambda o:next(x for x in o['items'][12]['grammar']['full_text_occurrences'] if x['id']=='ftg-r14-013-p03-manual').update(start=9999),lambda o:all(z['reading']['sections'][2]['text'][x['start']:x['end']]==x['target_text'] for z in [o['items'][12]] for x in z['grammar']['full_text_occurrences'] if x['section_id']=='p03'))
neg('remove_manual_marker',lambda o:o['items'][12]['grammar']['full_text_occurrences'].pop(),lambda o:sum(len(x['grammar']['full_text_occurrences']) for x in o['items'])==4298)
neg('modify_untouched',lambda o:o['items'][0].update(title_de='bad'),lambda o:o['items'][0]==a['items'][0])
neg('bad_question',lambda o:o['items'][12]['questions'][0].update(answer_de='bad'),lambda o:o['items'][12]['questions']==a['items'][12]['questions'])
neg('wrong_total',lambda o:o['full_text_grammar_qa'].update(occurrences=11),lambda o:o['full_text_grammar_qa']['occurrences']==4298)
result={'schema':'lesen-r14-independent-structural-and-source-fidelity@1.0.0','date':'2026-11-07',
 'parent_r13_master_sha256':sha(OM.read_bytes()),'parent_r13_runtime_sha256':sha(OR.read_bytes()),
 'r14_master_sha256':sha(NM.read_bytes()),'r14_runtime_sha256':sha(NR.read_bytes()),
 'checks_by_type':dict(checks),'checks_total':sum(checks.values()),'errors_count':len(errors),'errors':errors[:30],
 'negative_cases':probes,'all_negative_cases_rejected':all(q['rejected'] for q in probes),
 'changed_units':change,'unchanged_units':54,'middle_sentences_preserved':28,
 'grammar_retired':retired,'grammar_exact_middle_retained':retained,'grammar_exact_middle_shifted':moved,'new_manual_scoped_grammar':added,
 'grammar_total':4298,'remaining_literal_generic_p03_openings':0,
 'independent_linguistic_stage4':'HOLD','native_nine_lens_rerun':False,'native_browser_stage6':'NOT_RUN','stage7':'NOT_RELEASED',
 'status':'PASS_SOURCE_STRUCTURAL_ONLY' if not errors and all(q['rejected'] for q in probes) else 'FAIL'}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='checks_by_type'},ensure_ascii=False,indent=2))
if result['status']=='FAIL':raise SystemExit(1)