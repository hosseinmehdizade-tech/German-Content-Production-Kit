#!/usr/bin/env python3
"""R17 scoped semantic evidence and durable checkpoint. No FINAL promotion."""
import pathlib,json,hashlib,re
P=pathlib.Path('/mnt/data/lesen_r17_20261107')
master=P/'Lesen-Production-Master-v1.3.0-R17-23CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
runtime=P/'Lesen-R17-v505-23CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'
ledger=json.loads((P/'LESEN-R17-23CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json').read_text())
ind=json.loads((P/'LESEN-R17-INDEPENDENT-SOURCE-QA.json').read_text())
native=json.loads((P/'LESEN-R17-v505-NATIVE-PREENTRY.json').read_text())
a=json.loads(master.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert ind['status'].startswith('PASS') and native['checks']['candidate_pack_status']=='PASS' and not native['checks']['candidate_warnings']
reviews=[]
for rec in ledger['changes']:
 n=int(rec['lesson_id'][-3:]);unit=a['items'][n-1]
 s=next(s for s in unit['reading']['sections'] if s['id']==rec['section_id'])
 first2=[z['text'] for z in s['sentences'][:2]]
 last=rec['after_de'];assert s['sentences'][-1]['text']==last
 fr=re.split(r'(?<=[.!?؟])\s+',s['translations']['fa'])
 en=re.split(r'(?<=[.!?؟])\s+',s['translations']['en'])
 assert len(fr)==len(en)==3
 reviews.append({'lesson_id':rec['lesson_id'],'title_de':rec['title_de'],'section_id':rec['section_id'],
 'original_german_context_s01_s02':first2,'reviewed_german_conclusion_s03':last,
 'reviewed_persian_conclusion':fr[-1],'reviewed_english_conclusion':en[-1],
 'source_grounding':'Conclusion draws only on preceding German claims or accepted specific FA/EN interpretation.',
 'meaning_note':'Scoped AI-authored comparison; no independent native Stage4 linguistic review.',
 'translations_changed':rec['translation_revised'],
 'legacy_curated_preservation':'First two German sentences and first two existing FA/EN sentences unchanged.'})
review={'schema':'lesen-r17-scoped-trilingual-review@1','date':'2026-11-07','status':'SCOPED_AI_EDITORIAL_NOT_INDEPENDENT_STAGE4',
'candidate_sha256':sha(master),'all_23_conclusions_reviewed':len(reviews)==23,
'four_translation_tail_pairs_revised':sum(z['translations_changed'] for z in reviews)==4,
'readonly_source_preservation':True,'full_lesson_semantic_stage4':'HOLD','reviewed_items':reviews}
write(P/'LESEN-R17-TRILINGUAL-SCOPED-REVIEW.json',review)
print('Hashes',sha(master),sha(runtime),sha(P/'LESEN-R17-INDEPENDENT-SOURCE-QA.json'))
md=f'''# Lesen R17 – Editorial and v505 pre-entry report (7 November 2026)

**Status: SOURCE-GROUNDED EDITORIAL CANDIDATE; NOT CURRENT, NOT FULL STAGE4, NOT A RELEASE.**

## Scope and actual changes

- Continued byte-verified **R16**, never the original PDF or older app main.
- On lessons **039–050 and 052**, replaced **23 identical German p02-s03/p03-s03 conclusions** with lesson-specific conclusions grounded in the accepted preceding sentences. Lesson **051**, previously corrected, is **byte-identical**. **55/68 lessons are unchanged**.
- **19** German conclusions now explicitly agree with their **already curated** FA/EN third-sentence meanings; their translations were retained unchanged. The remaining **4** generic translation-ending pairs were rewritten in both FA and EN, without changing preceding sentences (p03 of 046, 047, 050; p02 of 052).
- Original lesson titles, passages outside the 23 sections, 340 questions, 350 vocabulary entries, 669 curated grammar annotation identities, and source provenance remain intact.
- **72** former source-offset grammar occurrences associated with deleted generic sentences were retired, rather than silently left pointing to wrong text. **9** existing curated g06 samples were retargeted to real new relative clauses; **9** narrowly reviewed exact-offset fulltext relative-clause occurrences added. Fulltext counts **4,160 → 4,097**. The original native nine-lens grammar engine **was not rerun**.
- Identical generic conclusions remaining: **p02-s03 = 15, p03-s03 = 11** (26 sentence occurrences, not 26 lessons).

## Technical quality evidence

- Independent read-only structural/source/runtime checks **{ind['checks_total']:,}/{ind['checks_total']:,} PASS**, with **{len(ind['negative_cases'])}/{len(ind['negative_cases'])}** deliberate negative cases rejected. This does **not** establish complete learner-facing multilingual correctness.
- Actual current-v505 source module `reading-content-import-v38.js` SHA-256 `{native['module_sha256']}`: `validate()` **PASS, zero warnings**; 7/7 corrupted inputs rejected; `validateRecord()` and **isolated in-memory** `adoptCommittedMirrorV505()` PASSED (68 units / 340 exercises).
- **NO browser navigation, IndexedDB write or production app import. NO user review state, UI, SRS or FSRS modification.**

## File identities

| Artifact | SHA-256 | Bytes |
|---|---|---:|
| R17 editorial master | `{sha(master)}` | {master.stat().st_size} |
| R17 v505 pre-entry runtime | `{sha(runtime)}` | {runtime.stat().st_size} |

Source-aware parent: R16 content `0b31f21ed6cd65b2562d3806e58269294196d161b05ba87cc7af35e3ab87ffa5`; v505 pre-entry `afec137c5868eb26051c913e3dedefcc848a4a932d5e4cf23e5e21409516f641`.

## Remaining gates and work

- **Stage 4 independent full 68-lesson German–Persian–English semantic review: HOLD.** The 23-change scoped review in `LESEN-R17-TRILINGUAL-SCOPED-REVIEW.json` is AI-authored and not this gate.
- **Stage 5 official finalized compiler/grammar regeneration: HOLD** (this runtime is a reversible exact-v505 delta).
- **Stage 6 real browser/IndexedDB native import: NOT RUN** (prior Chromium environment blocked navigation).
- **Stage 7 release: NOT RELEASED.** Do not claim native import compatibility beyond v505 source validation.
- Next: inspect 26 remaining generic endings, likely lessons 053–068; avoid replacing high-quality specific sentences. Then examine p01–p05 reasoning and independent semantic quality, plus potential original word count drift.
- **Immutable CURRENT source-owner v1.3.0 ZIP** SHA-256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`; R16 retained as recovery parent. No new redundant sibling workspace, no auto-cleanup.
'''
(P/'LESEN-R17-EDITORIAL-AND-V505-REPORT-20261107.md').write_text(md,encoding='utf8')
ck={'schema':'lesen-quality-review-checkpoint-r17@1','date':'2026-11-07','family_id':'family:lesen','owner':'Workspaces/lesen-praesentation',
 'status':'R17_23_SOURCE_ALIGNED_CONCLUSIONS_INDEPENDENT_STRUCTURAL_PASS__V505_PREENTRY_PASS__CURATED_CURRENT_UNCHANGED_STAGE4_6_7_HOLD',
 'original_current':{'sha256':'558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565','library_file_id':'libfile_9b768265ff3c8191aca371baa38551d7','role':'CURRENT_IMMUTABLE_NOT_PROMOTED'},
 'parent_r16':{'content_sha256':ledger['parent_r16_sha256'],'runtime_sha256':'afec137c5868eb26051c913e3dedefcc848a4a932d5e4cf23e5e21409516f641'},
 'candidate_content':{'name':master.name,'sha256':sha(master),'bytes':master.stat().st_size,'role':'CANDIDATE_NOT_CURRENT','library_file_id':None,'library_postupload_sha256_cmp':'PENDING'},
 'candidate_runtime':{'name':runtime.name,'sha256':sha(runtime),'bytes':runtime.stat().st_size,'role':'PREENTRY_NOT_BROWSER_STAGE6','library_file_id':None,'library_postupload_sha256_cmp':'PENDING'},
 'changes':{'lessons':[f'LES-PRES-{i:03d}' for i in ledger['changed_units']],'changed_conclusion_sections':23,'changed_de_sentences':23,'fa_en_approved_conclusions_retained':38,'fa_en_translation_pairs_changed':4,
 'unaltered_units':55,'questions':340,'vocabulary':350,'curated_grammar_count':669,'fulltext_before':4160,'invalid_spans_retired':72,'real_relative_curated_retargeted':9,'new_scoped_relative':9,'fulltext_after':4097,'remaining_generic_p02':15,'remaining_generic_p03':11},
 'qa':{'source_structural_checks':ind['checks_total'],'source_structural_errors':ind['error_count'],'negative_mutations_rejected':9,'actual_v505_source_preentry':'PASS_ZERO_WARNINGS_7_NEGATIVES',
 'isolated_in_memory':'PASS_68_UNITS_340_EXERCISES','native_browser_indexeddb':'NOT_RUN','independent_full_semantic_stage4':'HOLD','native_nine_lens_grammar_rederive':'NOT_RERUN','stage7':'NOT_RELEASED'},
 'evidence':{'report':'Reports/LESEN-R17-EDITORIAL-AND-V505-REPORT-20261107.md','ledger':'LESEN-R17-23CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json',
 'review':'LESEN-R17-TRILINGUAL-SCOPED-REVIEW.json','independent_qa':'LESEN-R17-INDEPENDENT-SOURCE-QA.json','native_v505':'LESEN-R17-v505-NATIVE-PREENTRY.json'},
 'next_actions':['Study 26 remaining p02/p03 generic endings in lessons 053..068','Independent full 68 unit DE/FA/EN semantic Stage4, inspect remaining templated arguments','Native isolated browser/IndexedDB Stage6 when environment supports navigation'],
 'no_current_promotion':True,'no_app_ui_or_user_srs_fsrs_change':True,'no_auto_cleanup':True}
write(P/'QUALITY-REVIEW-CHECKPOINT-R17-20261107.json',ck)
print('Handoff files ready')