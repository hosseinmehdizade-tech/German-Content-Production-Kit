#!/usr/bin/env python3
"""Independent read-only R12 verification. Real source-text and v505 payload equality.
Structural/source fidelity, offsets and deliberate negative probes; not independent language Stage4.
"""
import json,hashlib,collections,copy,pathlib,re
P=pathlib.Path('/mnt/data/lesen_r12_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r11_20261107/Lesen-Production-Master-v1.3.0-R11-9P04-TRILINGUAL-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r11_20261107/Lesen-R11-v505-9P04-RUNTIME-PREENTRY-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R12-10P04-TRILINGUAL-CANDIDATE.json'
NEWR=P/'Lesen-R12-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json'
LEDGER=P/'LESEN-R12-10P04-TRILINGUAL-GRAMMAR-LEDGER.json'
OUT=P/'LESEN-R12-INDEPENDENT-STRUCTURAL-QA.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
assert sha(OLDM.read_bytes())=='8a0bf2d16ce51b39501e5b6bc26b912cb47d9a4a14c0f42699e6b49b4ba3e3fe'
assert sha(OLDR.read_bytes())=='ecc79df87f851f1196b4b6799c4b7b671ecaf77c089dc620e89ef497224730a2'
a=json.loads(OLDM.read_text());b=json.loads(NEWM.read_text());c=json.loads(OLDR.read_text());d=json.loads(NEWR.read_text());ledger=json.loads(LEDGER.read_text())
checks=collections.Counter();fail=[]
def ck(label,ok):
    checks[label]+=1
    if not ok:fail.append(label)
expected=set(range(41,51));changed=[];removed=[];added=[];shifted=0;retained=0;retarget=[]
ck('68_unique_ordered_units',len(a['items'])==len(b['items'])==len(c['entries'])==len(d['entries'])==68)
ck('runtime_pack_contract',c['schema_version']==d['schema_version']=='lesen.runtime.v1.0.0' and c['pack_id']==d['pack_id']==a['pack_id']+'-runtime-v1')
ck('entry_integrity',d['integrity']['entries_sha256']==sha(canon(d['entries'])))
ck('payload_integrity',d['integrity']['payload_sha256']==sha(canon({k:v for k,v in d.items() if k!='integrity'})))
ck('source_hash',d['compiled_from']['sha256']==sha(NEWM.read_bytes()) and ledger['candidate_sha256']==sha(NEWM.read_bytes()))
ck('parent_hash',ledger['parent_sha256']==sha(OLDM.read_bytes()))
ck('p04_middle_template_not_deleted',sum(x['reading']['sections'][3]['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.') for x in b['items'])==16)
for i,(old,new,oe,ne) in enumerate(zip(a['items'],b['items'],c['entries'],d['entries'])):
    n=i+1;edited=n in expected
    ck('stable_unit_ids',old['id']==new['id']==oe['source_item_id']==ne['source_item_id']==f'LES-PRES-{n:03d}')
    ck('stable_titles',old['title_de']==new['title_de'])
    ck('unchanged_order',old['order']==new['order'])
    ck('unchanged_questions',old['questions']==new['questions'])
    ck('unchanged_vocab',old['vocabulary']==new['vocabulary'])
    ck('unchanged_legacy_source',old['legacy_source']==new['legacy_source'])
    ck('same_old_grammar_tasks',old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks'])
    ck('same_old_auto_lens_targets',old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets'])
    ck('stable_sections',[x['id'] for x in old['reading']['sections']]==[x['id'] for x in new['reading']['sections']])
    ck('other_p_sections_unchanged',old['reading']['sections'][:3]==new['reading']['sections'][:3] and old['reading']['sections'][4:]==new['reading']['sections'][4:])
    ck('runtime_exercise_unchanged',oe['exercises']==ne['exercises'])
    ck('runtime_r38_grammar_equal',ne['unit']['r38']['grammar']==new['grammar'])
    ck('runtime_r38_quality_equal',ne['unit']['r38']['quality']==new['quality'])
    ck('runtime_wordcount_equal',new['reading']['word_count_de']==ne['unit']['r38']['word_count_de'])
    ck('comprehension_exercise_ids_unchanged',oe['unit']['comprehension_exercise_ids']==ne['unit']['comprehension_exercise_ids'])
    if edited:
        changed.append(new['id']);s0=old['reading']['sections'][3];s1=new['reading']['sections'][3]
        ck('only_expected_master_fields_changed',{k for k in new if new[k]!=old[k]}=={'reading','grammar','quality'})
        ck('old_generic_start',s0['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.'))
        ck('new_topic_specific_start',not s1['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.'))
        ck('same_middle_sentence_identity',s0['sentences'][1]==s1['sentences'][1])
        ck('changed_first_last',s0['sentences'][0]!=s1['sentences'][0] and s0['sentences'][2]!=s1['sentences'][2])
        ck('p04_text_is_exact_join',s1['text']==' '.join(v['text'] for v in s1['sentences']))
        ck('trilingual_updated_and_substantial',s0['translations']!=s1['translations'] and len(s1['translations']['fa'])>160 and len(s1['translations']['en'])>190)
        ck('reading_full_wordcount',new['reading']['word_count_de']==len(' '.join(s['text'] for s in new['reading']['sections']).split()))
        ck('quality_hash_exact',new['quality']['content_hash']==sha(' '.join(s['text'] for s in new['reading']['sections']).encode())[:16])
        ck('runtime_updated_p04_exact',ne['unit']['passages'][3]['text_de']==s1['text'] and ne['unit']['passages'][3]['translations']==s1['translations'])
        ck('runtime_other_passages_unchanged',all(oe['unit']['passages'][j]==ne['unit']['passages'][j] for j in (0,1,2,4,5,6)))
        oldp=[x for x in old['grammar']['full_text_occurrences'] if x['section_id']=='p04'];newp=[x for x in new['grammar']['full_text_occurrences'] if x['section_id']=='p04']
        oldmap={x['id']:x for x in oldp}
        for x in oldp:
            if x['sentence_id']!='p04-s02':removed.append((new['id'],x['id']))
        for x in newp:
            if x['id'].startswith('ftg-r12-'):
                added.append((new['id'],x['id']))
                ck('manual_k2_provenance',x['grammar_key']=='konjunktiv_ii' and x['annotation_source']=='editorial_scoped_r12' and x['sentence_id']=='p04-s03' and x['target_text'] in ('müsste','müssten','sollten','könnten','könnte'))
                ck('unique_k2_location',s1['sentences'][2]['text'].count(x['target_text'])==1)
            else:
                ck('only_middle_kept',x['id'] in oldmap and x['sentence_id']==oldmap[x['id']]['sentence_id']=='p04-s02')
                if x['id'] in oldmap:
                    prev=oldmap[x['id']]
                    ck('middle_kept_annotation_metadata',all(x.get(k)==prev.get(k) for k in prev if k not in ('start','end')))
                    ck('middle_new_relative_offset',x['start']-(len(s1['sentences'][0]['text'])+1)==prev['start']-(len(s0['sentences'][0]['text'])+1))
                    shifted+=int(x['start']!=prev['start']);retained+=1
        for cur in new['grammar']['curated_annotations']:
            if cur['section_id']=='p04' and cur['sentence_id']=='p04-s03':
                retarget.append((new['id'],cur['id']))
                ck('curated_r12_retarget',cur['id']=='g07' and cur['annotation_source']=='editorial_retarget_r12' and cur['target_text']==s1['sentences'][2]['text'])
    else:
        ck('untouched_master_unit_exact',old==new)
        ck('untouched_runtime_entry_exact',oe==ne)
    for sec,passage in zip(new['reading']['sections'],ne['unit']['passages']):
        ck('passage_text_exact',sec['text']==passage['text_de'])
        ck('passage_translations_exact',sec['translations']==passage['translations'])
        ck('fa_en_present',all(sec['translations'][lang].strip() for lang in ('fa','en')))
        ck('sentence_ids_stable',[s['id'] for s in sec['sentences']]==passage['sentence_ids'])
    for q,e in zip(new['questions'],ne['exercises']):
        ck('question_prompt_exact',q['prompt_de']==e['prompt_de'])
        ck('question_answer_exact',q['answer_de']==e['answer_spec']['model_answer'])
        ck('question_evidence_exact',q['evidence_section_ids']==e['r38']['evidence_section_ids'])
    for cur in new['grammar']['curated_annotations']:
        sec=next(s for s in new['reading']['sections'] if s['id']==cur['section_id'])
        sent=next(s for s in sec['sentences'] if s['id']==cur['sentence_id'])
        ck('curated_exact_sentence_text',cur['target_text'] in sent['text'])
    for occ in new['grammar']['full_text_occurrences']:
        sec=next(s for s in new['reading']['sections'] if s['id']==occ['section_id'])
        sent=next(s for s in sec['sentences'] if s['id']==occ['sentence_id'])
        ck('fulltext_grammar_exact_offset',sec['text'][occ['start']:occ['end']]==occ['target_text'])
        ck('grammar_in_sentence',occ['target_text'] in sent['text'])
    ck('fulltext_grammar_unique_ids',len({g['id'] for g in new['grammar']['full_text_occurrences']})==len(new['grammar']['full_text_occurrences']))
ck('changed_units_exact',changed==[f'LES-PRES-{n:03d}' for n in sorted(expected)])
ck('removed_count',len(removed)==ledger['old_invalid_context_occurrences_retired']==60)
ck('added_count',len(added)==ledger['new_scoped_K2_occurrences']==10)
ck('shifted_count',shifted==ledger['middle_grammar_reanchored'])
ck('retained_count',retained==ledger['middle_grammar_retained'])
ck('curated_retargeted_count',len(retarget)==ledger['curated_g07_retargets']==5)
ck('grammar_count',sum(len(u['grammar']['full_text_occurrences']) for u in b['items'])==d['counts']['full_text_grammar']==b['full_text_grammar_qa']['occurrences']==4425)
ck('curated_count',sum(len(u['grammar']['curated_annotations']) for u in b['items'])==d['counts']['curated_grammar']==669)
ck('source_runtime_counts',d['counts']=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4425})
ck('distinct_first_four_questions',all(len({u['questions'][i]['prompt_de'] for u in b['items']})==68 for i in range(4)))
ck('accepted_035_exact',a['items'][34]==b['items'][34] and c['entries'][34]==d['entries'][34])
negative=[]
def neg(name,mutate,valid):
    bad=copy.deepcopy(b);mutate(bad);rejected=not valid(bad)
    negative.append({'name':name,'rejected':rejected});ck('negative_'+name,rejected)
neg('modify_unrelated_035',lambda x:x['items'][34].update(title_de='INVALID'),lambda x:x['items'][34]==a['items'][34])
neg('drop_persian_translation',lambda x:x['items'][40]['reading']['sections'][3]['translations'].update(fa=''),lambda x:bool(x['items'][40]['reading']['sections'][3]['translations']['fa']))
neg('modify_middle_source_sentence',lambda x:x['items'][40]['reading']['sections'][3]['sentences'][1].update(text='INVALID'),lambda x:x['items'][40]['reading']['sections'][3]['sentences'][1]==a['items'][40]['reading']['sections'][3]['sentences'][1])
neg('bad_grammar_offset',lambda x:next(g for g in x['items'][40]['grammar']['full_text_occurrences'] if g['id'].startswith('ftg-r12-')).update(start=99999),lambda x:all(x['items'][40]['reading']['sections'][3]['text'][g['start']:g['end']]==g['target_text'] for g in x['items'][40]['grammar']['full_text_occurrences'] if g['section_id']=='p04'))
neg('change_question_id',lambda x:x['items'][40]['questions'][0].update(id='BAD'),lambda x:x['items'][40]['questions']==a['items'][40]['questions'])
neg('change_unmodified_unit',lambda x:x['items'][0].update(title_de='BAD'),lambda x:x['items'][0]==a['items'][0])
neg('restore_obsolete_grammar',lambda x:x['items'][40]['grammar']['full_text_occurrences'].append(copy.deepcopy(next(y for y in a['items'][40]['grammar']['full_text_occurrences'] if y['sentence_id']=='p04-s01'))),lambda x:len(x['items'][40]['grammar']['full_text_occurrences'])==len(b['items'][40]['grammar']['full_text_occurrences']))
neg('delete_new_k2',lambda x:x['items'][40]['grammar']['full_text_occurrences'].pop(),lambda x:any(g['id']=='ftg-r12-041-p04-k2' for g in x['items'][40]['grammar']['full_text_occurrences']))
neg('wrong_pack_qa_grammar_total',lambda x:x['full_text_grammar_qa'].update(occurrences=-1),lambda x:x['full_text_grammar_qa']['occurrences']==4425)
res={'schema':'lesen-r12-independent-structural-qa@1.0.0','date':'2026-11-07','source_r11_master_sha256':sha(OLDM.read_bytes()),'source_r11_runtime_sha256':sha(OLDR.read_bytes()),
     'candidate_r12_master_sha256':sha(NEWM.read_bytes()),'candidate_r12_runtime_sha256':sha(NEWR.read_bytes()),
     'checks':dict(checks),'checks_total':sum(checks.values()),'errors_count':len(fail),'failed_check_labels':fail[:20],
     'negatives':negative,'all_negatives_rejected':all(x['rejected'] for x in negative),'scope_changed_units':changed,'unchanged_units':58,
     'source_middle_sentence_anchors_retained':retained,'source_middle_sentence_anchors_reanchored':shifted,
     'legacy_context_spans_removed':len(removed),'manual_scoped_k2_added':len(added),'curated_g07_retargeted':len(retarget),
     'fulltext_grammar_total':4425,'generic_p04_remaining':16,
     'no_full_native_grammar_engine_rerun':True,'semantic_stage4':'HOLD','browser_indexeddb_stage6':'NOT_RUN','stage7':'NOT_RELEASED',
     'status':'PASS_SCOPED_STRUCTURAL_AND_SOURCE_FIDELITY' if not fail and all(x['rejected'] for x in negative) else 'FAIL'}
OUT.write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in res.items() if k!='checks'},ensure_ascii=False,indent=2))
if res['status'].startswith('FAIL'):raise SystemExit(1)