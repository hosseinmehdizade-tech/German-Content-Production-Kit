#!/usr/bin/env python3
"""Read-only, independently implemented structural/transport regression for Lesen R11.
Checks invariants and adversarial probes; not a substitute for independent multilingual Stage4
or native browser/IndexedDB Stage6.
"""
import json,hashlib,collections,copy,pathlib
P=pathlib.Path('/mnt/data/lesen_r11_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r10_20261107/Lesen-Production-Master-v1.3.0-R10-10P04-TRILINGUAL-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r10_20261107/Lesen-R10-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R11-9P04-TRILINGUAL-CANDIDATE.json'
NEWR=P/'Lesen-R11-v505-9P04-RUNTIME-PREENTRY-CANDIDATE.json'
LEDGER=P/'LESEN-R11-9P04-TRILINGUAL-GRAMMAR-LEDGER.json'
OUT=P/'LESEN-R11-INDEPENDENT-STRUCTURAL-QA.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
assert sha(OLDM.read_bytes())=='4be5bf368b23a1a46bae2d28686b3d4f9336ac01d98c2c1449ab19df81b9509a'
assert sha(OLDR.read_bytes())=='e2e5d395679f772f7ec4cf845da4af2aadb148f3362b3ed3955ed76d280e9aa3'
a=json.loads(OLDM.read_text());b=json.loads(NEWM.read_text());c=json.loads(OLDR.read_text());d=json.loads(NEWR.read_text());ledger=json.loads(LEDGER.read_text())
checks=collections.Counter();fail=[]
def ck(label,condition):
    checks[label]+=1
    if not condition:fail.append(label)
expected={31,32,33,34,36,37,38,39,40}
ck('68_units',len(a['items'])==len(b['items'])==len(c['entries'])==len(d['entries'])==68)
ck('pack_id_transport_contract',a['pack_id']==b['pack_id'] and c['pack_id']==d['pack_id']==a['pack_id']+'-runtime-v1')
ck('runtime_entries_integrity',sha(canon(d['entries']))==d['integrity']['entries_sha256'])
ck('runtime_payload_integrity',sha(canon({k:v for k,v in d.items() if k!='integrity'}))==d['integrity']['payload_sha256'])
ck('runtime_compiled_from_R11_exact',d['compiled_from']['sha256']==sha(NEWM.read_bytes()))
ck('ledger_parent_exact',ledger['parent_content_sha256']==sha(OLDM.read_bytes()))
ck('ledger_candidate_exact',ledger['candidate_content_sha256']==sha(NEWM.read_bytes()))
ck('legacy_fulltext_count',sum(len(u['grammar']['full_text_occurrences']) for u in a['items'])==4520)
changed=[];removed=[];added=[];retarget=[];shifted=0;retained=0
for i,(old,new,oldd,newd) in enumerate(zip(a['items'],b['items'],c['entries'],d['entries'])):
    n=i+1;target=n in expected
    ck('same_lesson_id_and_order',old['id']==new['id']==oldd['source_item_id']==newd['source_item_id'] and old['order']==new['order'])
    ck('same_title',old['title_de']==new['title_de'])
    ck('same_questions',old['questions']==new['questions'])
    ck('same_vocabulary',old['vocabulary']==new['vocabulary'])
    ck('same_legacy_provenance',old['legacy_source']==new['legacy_source'])
    ck('same_grammar_tasks',old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks'])
    ck('same_auto_lens_targets',old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets'])
    ck('same_question_ids',[q['id'] for q in old['questions']]==[q['id'] for q in new['questions']])
    ck('same_section_ids',[s['id'] for s in old['reading']['sections']]==[s['id'] for s in new['reading']['sections']])
    ck('same_reading_except_p04',old['reading']['sections'][:3]==new['reading']['sections'][:3] and old['reading']['sections'][4:]==new['reading']['sections'][4:])
    ck('unchanged_runtime_exercises',oldd['exercises']==newd['exercises'])
    ck('runtime_word_count',new['reading']['word_count_de']==newd['unit']['r38']['word_count_de'])
    ck('runtime_grammar',new['grammar']==newd['unit']['r38']['grammar'])
    ck('runtime_quality',new['quality']==newd['unit']['r38']['quality'])
    ck('same_unit_comprehension_ids',oldd['unit']['comprehension_exercise_ids']==newd['unit']['comprehension_exercise_ids'])
    if target:
        changed.append(new['id']);sa=old['reading']['sections'][3];sb=new['reading']['sections'][3]
        ck('allowed_fields_only',{k for k in old if old[k]!=new[k]}=={'reading','grammar','quality'})
        ck('template_before',sa['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.'))
        ck('template_removed',not sb['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.'))
        ck('same_middle_sentence',sa['sentences'][1]==sb['sentences'][1])
        ck('s01_s03_both_changed',sa['sentences'][0]!=sb['sentences'][0] and sa['sentences'][2]!=sb['sentences'][2])
        ck('new_p04_text_assembled',sb['text']==' '.join(s['text'] for s in sb['sentences']))
        ck('trilingual_changed_and_nonblank',sa['translations']!=sb['translations'] and all(len(sb['translations'][k])>140 for k in ('fa','en')))
        ck('new_word_count',new['reading']['word_count_de']==len(' '.join(s['text'] for s in new['reading']['sections']).split()))
        ck('new_content_hash',new['quality']['content_hash']==sha(' '.join(s['text'] for s in new['reading']['sections']).encode())[:16])
        ck('runtime_p04_exact',newd['unit']['passages'][3]['text_de']==sb['text'] and newd['unit']['passages'][3]['translations']==sb['translations'])
        ck('runtime_other_passages_exact',all(oldd['unit']['passages'][j]==newd['unit']['passages'][j] for j in (0,1,2,4,5,6)))
        oldp=[x for x in old['grammar']['full_text_occurrences'] if x['section_id']=='p04']
        newp=[x for x in new['grammar']['full_text_occurrences'] if x['section_id']=='p04']
        oldmap={x['id']:x for x in oldp}
        for x in oldp:
            if x['sentence_id']!='p04-s02':removed.append((new['id'],x['id']))
        for x in newp:
            if x['id'].startswith('ftg-r11-'):
                added.append((new['id'],x['id']))
                ck('new_K2_specific_scoped_source',x['grammar_key']=='konjunktiv_ii' and x['annotation_source']=='editorial_scoped_r11' and x['sentence_id']=='p04-s03' and x['target_text'] in ('könnten','wäre','sollten','müssten'))
                ck('new_K2_form_exclusive',sb['sentences'][2]['text'].count(x['target_text'])==1)
            else:
                ck('only_old_middle_kept',x['sentence_id']=='p04-s02' and x['id'] in oldmap and oldmap[x['id']]['sentence_id']=='p04-s02')
                if x['id'] in oldmap:
                    prev=oldmap[x['id']]
                    ck('kept_grammatical_metadata_exact',all(x.get(k)==prev.get(k) for k in prev if k not in ('start','end')))
                    ck('reanchored_relative_to_middle_exact',x['start']==len(sb['sentences'][0]['text'])+1+(prev['start']-len(sa['sentences'][0]['text'])-1))
                    shifted+=int(x['start']!=prev['start']);retained+=1
        for g in new['grammar']['curated_annotations']:
            if g['section_id']=='p04' and g['sentence_id']=='p04-s03':
                retarget.append((new['id'],g['id']))
                ck('curated_new_s03_exact',g['annotation_source']=='editorial_retarget_r11' and g['target_text']==sb['sentences'][2]['text'])
    else:
        ck('untouched_master_59',old==new)
        ck('untouched_runtime_59',oldd==newd)
    for section,passage in zip(new['reading']['sections'],newd['unit']['passages']):
        ck('source_runtime_passage_text_exact',section['text']==passage['text_de'])
        ck('source_runtime_trilingual_exact',section['translations']==passage['translations'])
        ck('translation_nonblank',all(section['translations'][k].strip() for k in ('fa','en')))
        ck('sentence_ids_consistent',[s['id'] for s in section['sentences']]==passage['sentence_ids'])
    for q,e in zip(new['questions'],newd['exercises']):
        ck('question_prompt_exact',q['prompt_de']==e['prompt_de'])
        ck('answer_exact',q['answer_de']==e['answer_spec']['model_answer'])
        ck('question_evidence_exact',q['evidence_section_ids']==e['r38']['evidence_section_ids'])
    for g in new['grammar']['curated_annotations']:
        sec=next(s for s in new['reading']['sections'] if s['id']==g['section_id'])
        sent=next(s for s in sec['sentences'] if s['id']==g['sentence_id'])
        ck('curated_anchor_exact',g['target_text'] in sent['text'])
    for g in new['grammar']['full_text_occurrences']:
        sec=next(s for s in new['reading']['sections'] if s['id']==g['section_id'])
        sent=next(s for s in sec['sentences'] if s['id']==g['sentence_id'])
        ck('grammar_offset_exact',sec['text'][g['start']:g['end']]==g['target_text'])
        ck('grammar_sentence_membership',g['target_text'] in sent['text'])
    ck('grammar_ID_uniqueness',len({g['id'] for g in new['grammar']['full_text_occurrences']})==len(new['grammar']['full_text_occurrences']))
ck('changed_unit_scope',changed==[f'LES-PRES-{n:03d}' for n in sorted(expected)])
ck('accepted_035_remains_byte_equivalent',a['items'][34]==b['items'][34] and c['entries'][34]==d['entries'][34])
ck('removed_grammar_count',len(removed)==ledger['invalidated_old_occurrences'])
ck('new_grammar_count',len(added)==9)
ck('shift_count_matches_ledger',shifted==ledger['middle_anchors_repositioned'])
ck('retained_middle_count_matches_ledger',retained==ledger['middle_anchors_retained'])
ck('curated_retarget_count_matches_ledger',len(retarget)==ledger['curated_annotations_retargeted'])
ck('fulltext_grammar_total',sum(len(u['grammar']['full_text_occurrences']) for u in b['items'])==d['counts']['full_text_grammar']==b['full_text_grammar_qa']['occurrences']==4475)
ck('curated_grammar_total',sum(len(u['grammar']['curated_annotations']) for u in b['items'])==669)
ck('native_runtime_counts',d['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4475})
ck('generic_p04_remaining',sum(u['reading']['sections'][3]['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.') for u in b['items'])==26)
ck('distinct_q01_q02_q03_q04',all(len({u['questions'][i]['prompt_de'] for u in b['items']})==68 for i in range(4)))
negative=[]
def neg(label,modify,check):
    mutated=copy.deepcopy(b);modify(mutated);rejected=not check(mutated)
    negative.append({'name':label,'rejected':rejected});ck('negative_'+label,rejected)
neg('tampers_035',lambda x:x['items'][34].update(title_de='INVALID'),lambda x:x['items'][34]==a['items'][34])
neg('wrong_middle',lambda x:x['items'][30]['reading']['sections'][3]['sentences'][1].update(text='INVALID'),lambda x:x['items'][30]['reading']['sections'][3]['sentences'][1]==a['items'][30]['reading']['sections'][3]['sentences'][1])
neg('missing_Farsi',lambda x:x['items'][30]['reading']['sections'][3]['translations'].update(fa=''),lambda x:bool(x['items'][30]['reading']['sections'][3]['translations']['fa']))
neg('bad_K2_offset',lambda x:next(y for y in x['items'][30]['grammar']['full_text_occurrences'] if y['id'].startswith('ftg-r11-')).update(start=100000),lambda x:all(x['items'][30]['reading']['sections'][3]['text'][z['start']:z['end']]==z['target_text'] for z in x['items'][30]['grammar']['full_text_occurrences'] if z['section_id']=='p04'))
neg('break_question_id',lambda x:x['items'][30]['questions'][0].update(id='INVALID'),lambda x:x['items'][30]['questions']==a['items'][30]['questions'])
neg('corrupt_unchanged_lesson',lambda x:x['items'][0].update(title_de='INVALID'),lambda x:x['items'][0]==a['items'][0])
neg('resurrect_retired_span',lambda x:x['items'][30]['grammar']['full_text_occurrences'].append(copy.deepcopy(next(y for y in a['items'][30]['grammar']['full_text_occurrences'] if y['sentence_id']=='p04-s01'))),lambda x:len(x['items'][30]['grammar']['full_text_occurrences'])==len(b['items'][30]['grammar']['full_text_occurrences']))
neg('missing_new_annotation',lambda x:x['items'][30]['grammar']['full_text_occurrences'].pop(),lambda x:any(z['id']=='ftg-r11-031-p04-k2' for z in x['items'][30]['grammar']['full_text_occurrences']))
neg('bad_reported_occurrence_total',lambda x:x['full_text_grammar_qa'].update(occurrences=-1),lambda x:x['full_text_grammar_qa']['occurrences']==4475)
result={'schema':'lesen-r11-independent-source-structural-qa@1.0.0','date':'2026-11-07',
 'parent_content_sha256':sha(OLDM.read_bytes()),'parent_runtime_sha256':sha(OLDR.read_bytes()),
 'candidate_content_sha256':sha(NEWM.read_bytes()),'candidate_runtime_sha256':sha(NEWR.read_bytes()),
 'checks_total':sum(checks.values()),'failed_count':len(fail),'failed_check_labels':fail[:30],
 'check_groups':dict(checks),'negative_tests':negative,'all_negative_rejected':all(t['rejected'] for t in negative),
 'changed_units':changed,'unchanged_units':59,'accepted_035_untouched':True,'changed_de_sentences':18,
 'invalidated_prior_grammar':len(removed),'new_scoped_k2_grammar':len(added),
 'retargeted_curated_g07':len(retarget),'reanchored_mid_sentence_grammar':shifted,
 'fulltext_grammar_final':4475,'still_generic_p04':26,
 'v505_native_js_source_preentry':'SEPARATE_REQUIRED','independent_complete_stage4':'HOLD','native_full_grammar_engine':'NOT_RUN',
 'browser_indexeddb_stage6':'NOT_RUN','stage7':'NOT_FINAL',
 'status':'PASS_SCOPED_SOURCE_FIDELITY_AND_STRUCTURE_ONLY' if not fail and all(t['rejected'] for t in negative) else 'FAIL'}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='check_groups'},ensure_ascii=False,indent=2))
if result['status']!='PASS_SCOPED_SOURCE_FIDELITY_AND_STRUCTURE_ONLY':raise SystemExit(1)