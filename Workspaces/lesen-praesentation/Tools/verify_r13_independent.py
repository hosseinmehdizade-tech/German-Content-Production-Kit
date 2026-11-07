#!/usr/bin/env python3
"""Independent read-only R13 structural/native transport fidelity and source grammar offset QA.
Does NOT certify semantic Stage4, native nine-lens source generation, or browser IndexedDB Stage6.
"""
import json,hashlib,collections,copy,pathlib
P=pathlib.Path('/mnt/data/lesen_r13_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r12_20261107/Lesen-Production-Master-v1.3.0-R12-10P04-TRILINGUAL-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r12_20261107/Lesen-R12-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R13-16P04-TRILINGUAL-CANDIDATE.json'
NEWR=P/'Lesen-R13-v505-16P04-RUNTIME-PREENTRY-CANDIDATE.json'
LEDGER=P/'LESEN-R13-16P04-TRILINGUAL-GRAMMAR-LEDGER.json'
OUT=P/'LESEN-R13-INDEPENDENT-STRUCTURAL-QA.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
assert sha(OLDM.read_bytes())=='a41224ae7a054a959c942afb0b13fcb7d686c76fc27131ec813a9272dad6e7d2'
assert sha(OLDR.read_bytes())=='e08844a19137a1edece8deb9f39e036df7b4777de2e54db4312e0ab14c3bcd86'
a=json.loads(OLDM.read_text());b=json.loads(NEWM.read_text());c=json.loads(OLDR.read_text());d=json.loads(NEWR.read_text());ledger=json.loads(LEDGER.read_text())
expected=set(range(52,59))|set(range(60,69));checks=collections.Counter();fail=[];removed=0;added=0;reanchored=0;retained=0;retargeted=0;changed=[]
def ck(label,okay):
 checks[label]+=1
 if not okay:fail.append(label)
ck('unit_total',len(a['items'])==len(b['items'])==len(c['entries'])==len(d['entries'])==68)
ck('schema_contract',d['schema_version']==c['schema_version']=='lesen.runtime.v1.0.0' and d['pack_id']==c['pack_id']==a['pack_id']+'-runtime-v1')
ck('integrity_entries',sha(canon(d['entries']))==d['integrity']['entries_sha256'])
ck('integrity_payload',sha(canon({k:v for k,v in d.items() if k!='integrity'}))==d['integrity']['payload_sha256'])
ck('source_hash_pin',d['compiled_from']['sha256']==ledger['candidate_r13_sha256']==sha(NEWM.read_bytes()))
ck('parent_hash_pin',ledger['source_r12_sha256']==sha(OLDM.read_bytes()))
for i,(old,new,oe,ne) in enumerate(zip(a['items'],b['items'],c['entries'],d['entries'])):
 n=i+1;edit=n in expected
 ck('stable_id',old['id']==new['id']==oe['source_item_id']==ne['source_item_id']==f'LES-PRES-{n:03d}')
 ck('stable_title',old['title_de']==new['title_de']);ck('stable_order',old['order']==new['order'])
 ck('same_questions',old['questions']==new['questions']);ck('same_vocab',old['vocabulary']==new['vocabulary'])
 ck('same_legacy_source',old['legacy_source']==new['legacy_source']);ck('same_grammar_tasks',old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks'])
 ck('same_auto_lens',old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets'])
 ck('runtime_exercises',oe['exercises']==ne['exercises'])
 ck('runtime_grammar',new['grammar']==ne['unit']['r38']['grammar'])
 ck('runtime_quality',new['quality']==ne['unit']['r38']['quality'])
 ck('runtime_word_count',new['reading']['word_count_de']==ne['unit']['r38']['word_count_de'])
 ck('same_section_ids',[s['id'] for s in old['reading']['sections']]==[s['id'] for s in new['reading']['sections']])
 ck('other_sections_unchanged',old['reading']['sections'][:3]==new['reading']['sections'][:3] and old['reading']['sections'][4:]==new['reading']['sections'][4:])
 if edit:
  changed.append(new['id']);oldsec=old['reading']['sections'][3];newsec=new['reading']['sections'][3]
  ck('changed_fields_only',{k for k in old if old[k]!=new[k]}=={'reading','grammar','quality'})
  ck('before_template',oldsec['sentences'][0]['text']=='Entscheidend ist deshalb die konkrete Ausgestaltung.')
  ck('after_not_template',newsec['sentences'][0]['text']!='Entscheidend ist deshalb die konkrete Ausgestaltung.')
  ck('same_middle_sentence',oldsec['sentences'][1]==newsec['sentences'][1])
  ck('first_last_changed',oldsec['sentences'][0]!=newsec['sentences'][0] and oldsec['sentences'][2]!=newsec['sentences'][2])
  ck('text_join',' '.join(x['text'] for x in newsec['sentences'])==newsec['text'])
  ck('translations_changed',oldsec['translations']!=newsec['translations'] and len(newsec['translations']['fa'])>170 and len(newsec['translations']['en'])>190)
  ck('reading_wordcount',new['reading']['word_count_de']==len(' '.join(s['text'] for s in new['reading']['sections']).split()))
  ck('quality_content_hash',new['quality']['content_hash']==sha(' '.join(s['text'] for s in new['reading']['sections']).encode())[:16])
  ck('updated_runtime_p04',newsec['text']==ne['unit']['passages'][3]['text_de'] and newsec['translations']==ne['unit']['passages'][3]['translations'])
  ck('unmodified_other_passages',all(oe['unit']['passages'][j]==ne['unit']['passages'][j] for j in (0,1,2,4,5,6)))
  oldp=[x for x in old['grammar']['full_text_occurrences'] if x['section_id']=='p04'];newp=[x for x in new['grammar']['full_text_occurrences'] if x['section_id']=='p04']
  oldmap={x['id']:x for x in oldp}
  removed+=sum(x['sentence_id']!='p04-s02' for x in oldp)
  for occ in newp:
   if occ['id'].startswith('ftg-r13-'):
    added+=1
    ck('new_scoped_k2',occ['grammar_key']=='konjunktiv_ii' and occ['annotation_source']=='editorial_scoped_r13' and occ['sentence_id']=='p04-s03' and occ['target_text'] in ('sollten','müssten','könnten','könnte','müsste'))
    ck('new_k2_exact_once',newsec['sentences'][2]['text'].count(occ['target_text'])==1)
   else:
    ck('only_prior_middle_kept',occ['id'] in oldmap and occ['sentence_id']==oldmap[occ['id']]['sentence_id']=='p04-s02')
    if occ['id'] in oldmap:
     prev=oldmap[occ['id']];retained+=1;reanchored+=int(occ['start']!=prev['start'])
     ck('middle_annotation_metadata_preserved',all(occ.get(k)==prev.get(k) for k in prev if k not in ('start','end')))
     ck('relative_offset_middle_preserved',occ['start']-(len(newsec['sentences'][0]['text'])+1)==prev['start']-(len(oldsec['sentences'][0]['text'])+1))
  for cur in new['grammar']['curated_annotations']:
   if cur['section_id']=='p04' and cur['sentence_id']=='p04-s03':
    retargeted+=1;ck('curated_exact_retarget',cur['id']=='g07' and cur['annotation_source']=='editorial_retarget_r13' and cur['target_text']==newsec['sentences'][2]['text'])
 else:
  ck('unmodified_unit_byte_semantics',old==new)
  ck('unmodified_runtime_entry',oe==ne)
 for sec,pas in zip(new['reading']['sections'],ne['unit']['passages']):
  ck('passage_text',sec['text']==pas['text_de'])
  ck('passage_translations',sec['translations']==pas['translations'])
  ck('fa_en_present',all(sec['translations'][lang].strip() for lang in ('fa','en')))
  ck('sentence_ids',[s['id'] for s in sec['sentences']]==pas['sentence_ids'])
 for q,e in zip(new['questions'],ne['exercises']):
  ck('question_prompt',q['prompt_de']==e['prompt_de'])
  ck('question_answer',q['answer_de']==e['answer_spec']['model_answer'])
  ck('question_evidence',q['evidence_section_ids']==e['r38']['evidence_section_ids'])
 for cur in new['grammar']['curated_annotations']:
  sec=next(s for s in new['reading']['sections'] if s['id']==cur['section_id']);sent=next(s for s in sec['sentences'] if s['id']==cur['sentence_id'])
  ck('curated_grammar_target_sentence',cur['target_text'] in sent['text'])
 for occ in new['grammar']['full_text_occurrences']:
  sec=next(s for s in new['reading']['sections'] if s['id']==occ['section_id']);sent=next(s for s in sec['sentences'] if s['id']==occ['sentence_id'])
  ck('fulltext_exact_section_offset',sec['text'][occ['start']:occ['end']]==occ['target_text'])
  ck('fulltext_target_in_sentence',occ['target_text'] in sent['text'])
 ck('unique_fulltext_ids',len({x['id'] for x in new['grammar']['full_text_occurrences']})==len(new['grammar']['full_text_occurrences']))
ck('changed_units_exact',changed==[f'LES-PRES-{n:03d}' for n in sorted(expected)])
ck('preserved_051_059',a['items'][50]==b['items'][50] and a['items'][58]==b['items'][58] and c['entries'][50]==d['entries'][50] and c['entries'][58]==d['entries'][58])
ck('removed_count',removed==ledger['old_context_invalidated']==96)
ck('added_count',added==ledger['new_scoped_k2']==16)
ck('retained_count',retained==ledger['original_middle_retained'])
ck('reanchored_count',reanchored==ledger['original_middle_reanchored'])
ck('curated_retargeted',retargeted==ledger['curated_retargeted'])
ck('grammar_total',sum(len(u['grammar']['full_text_occurrences']) for u in b['items'])==d['counts']['full_text_grammar']==b['full_text_grammar_qa']['occurrences']==4345)
ck('curated_total',sum(len(u['grammar']['curated_annotations']) for u in b['items'])==d['counts']['curated_grammar']==669)
ck('pack_counts',d['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4345})
ck('unique_all_four_questions',all(len({u['questions'][i]['prompt_de'] for u in b['items']})==68 for i in range(4)))
ck('zero_original_generic_p04',sum(u['reading']['sections'][3]['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.') for u in b['items'])==0)
negatives=[]
def neg(name,change,condition):
 temp=copy.deepcopy(b);change(temp);rejected=not condition(temp);negatives.append({'probe':name,'rejected':rejected});ck('negative_'+name,rejected)
neg('corrupt_051',lambda x:x['items'][50].update(title_de='INVALID'),lambda x:x['items'][50]==a['items'][50])
neg('corrupt_059',lambda x:x['items'][58].update(title_de='INVALID'),lambda x:x['items'][58]==a['items'][58])
neg('missing_fa',lambda x:x['items'][51]['reading']['sections'][3]['translations'].update(fa=''),lambda x:bool(x['items'][51]['reading']['sections'][3]['translations']['fa']))
neg('change_middle',lambda x:x['items'][51]['reading']['sections'][3]['sentences'][1].update(text='BAD'),lambda x:x['items'][51]['reading']['sections'][3]['sentences'][1]==a['items'][51]['reading']['sections'][3]['sentences'][1])
neg('invalid_grammar_offset',lambda x:next(y for y in x['items'][51]['grammar']['full_text_occurrences'] if y['id']=='ftg-r13-052-p04-k2').update(start=9999),lambda x:all(x['items'][51]['reading']['sections'][3]['text'][y['start']:y['end']]==y['target_text'] for y in x['items'][51]['grammar']['full_text_occurrences'] if y['section_id']=='p04'))
neg('remove_k2',lambda x:x['items'][51]['grammar']['full_text_occurrences'].pop(),lambda x:any(y['id']=='ftg-r13-052-p04-k2' for y in x['items'][51]['grammar']['full_text_occurrences']))
neg('mutate_question',lambda x:x['items'][51]['questions'][0].update(id='BAD'),lambda x:x['items'][51]['questions']==a['items'][51]['questions'])
neg('mutate_untouched_unit',lambda x:x['items'][0].update(title_de='BAD'),lambda x:x['items'][0]==a['items'][0])
neg('false_total',lambda x:x['full_text_grammar_qa'].update(occurrences=-2),lambda x:x['full_text_grammar_qa']['occurrences']==4345)
res={'schema':'lesen-r13-independent-source-structural-qa@1.0.0','date':'2026-11-07',
 'source_r12_master_sha256':sha(OLDM.read_bytes()),'source_r12_runtime_sha256':sha(OLDR.read_bytes()),
 'candidate_r13_master_sha256':sha(NEWM.read_bytes()),'candidate_r13_runtime_sha256':sha(NEWR.read_bytes()),
 'checks':dict(checks),'checks_total':sum(checks.values()),'errors_count':len(fail),'errors':fail[:30],
 'negative_mutations':negatives,'all_negative_mutations_rejected':all(x['rejected'] for x in negatives),
 'changed_unit_ids':changed,'untouched_units':52,'retired_context_anchors':removed,'middle_anchors_retained':retained,
 'middle_anchors_shifted':reanchored,'new_scoped_K2':added,'curated_g07_retargeted':retargeted,
 'fulltext_grammar_after':4345,'remaining_original_generic_p04_starts':0,
 'native_nine_lens_engine_rerun':False,'independent_semantic_stage4':'HOLD',
 'native_browser_indexeddb_stage6':'NOT_RUN','stage7':'NOT_RELEASED',
 'status':'PASS_SCOPED_STRUCTURAL_AND_SOURCE_FIDELITY' if not fail and all(x['rejected'] for x in negatives) else 'FAIL'}
OUT.write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in res.items() if k!='checks'},ensure_ascii=False,indent=2))
if res['status']=='FAIL':raise SystemExit(1)