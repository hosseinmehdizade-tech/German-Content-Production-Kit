#!/usr/bin/env python3
import json,pathlib,hashlib,collections
P=pathlib.Path('/mnt/data/lesen_r14_20261107')
read=lambda n:json.loads((P/n).read_text(encoding='utf8'))
sha=lambda n:hashlib.sha256((P/n).read_bytes()).hexdigest()
master='Lesen-Production-Master-v1.3.0-R14-14P03-TRILINGUAL-CANDIDATE.json'
runtime='Lesen-R14-v505-14P03-RUNTIME-PREENTRY-CANDIDATE.json'
ledger=read('LESEN-R14-14P03-TRILINGUAL-GRAMMAR-LEDGER.json')
qa=read('LESEN-R14-INDEPENDENT-STRUCTURAL-QA.json')
native=read('LESEN-R14-v505-NATIVE-PREENTRY.json')
d=read(master)
assert qa['status']=='PASS_SOURCE_STRUCTURAL_ONLY' and qa['errors_count']==0 and qa['checks_total']==13140
assert all(n['rejected'] for n in qa['negative_cases'])
assert native['checks']['candidate_pack_status']=='PASS' and not native['checks']['candidate_warnings'] and native['checks']['all_7_negative_rejected']
assert len(d['items'])==68 and sum(len(i['grammar']['full_text_occurrences']) for i in d['items'])==4298
assert ledger['r14_master_sha256']==sha(master)
# Evidence-based backlog; identical strings alone are not proof that a passage is semantically wrong.
backlog=[]
for sect_id,sent_id,needle in [('p02','p02-s03','Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.'),('p03','p03-s03','Ein Vorteil auf der einen Seite kann also durchaus neue Probleme auf der anderen Seite erzeugen.')]:
 ids=[u['id'] for u in d['items'] for sec in u['reading']['sections'] if sec['id']==sect_id for ss in sec['sentences'] if ss['id']==sent_id and ss['text']==needle]
 backlog.append({'section':sect_id,'sentence_id':sent_id,'identical_count':len(ids),'lesson_ids':ids,'sample':needle,'action':'manual evidence-bound semantic audit, not blind replacement'})
assert [x['identical_count'] for x in backlog]==[55,41]
review={'schema':'lesen-r14-editorial-source-bound-review@1.0.0','date':'2026-11-07','method':'Authored German and FA/EN aligned to existing R13 exact p02/p03-s02/p03-s03/p04 text, with only source-text and scoped AI review; not independent semantic Stage4.',
'updated_units':ledger['changed_unit_ids'],'examples':[{'unit':x['unit_id'],'title':x['title_de'],'new_de':x['after_p03']['text'],'fa':x['after_p03']['translations']['fa'],'en':x['after_p03']['translations']['en']} for x in ledger['before_after']],
'new_grammar_count':ledger['new_manual_scoped_markers'],'grammar_not_native_regenerated':True,'open_duplicated_sentences':backlog,
'formal_stage4':'HOLD','native_browser_stage6':'NOT_RUN'}
(P/'LESEN-R14-TRILINGUAL-SCOPED-REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report=f'''# Lesen R14 — source-bound p03 trilingual editorial and v505 preentry report

**Date:** 2026-11-07. **Scope:** R13 → R14, 14 units, p03-s01 and p03-s04 only; **not an educational release**.

## Actual editorial changes

- Units: {', '.join(ledger['changed_unit_ids'])}.
- Replaced **28 generic German sentences** in 14 p03 sections, and authored aligned full Persian and English translations for each changed section.
- Preserved **28 source-specific middle sentences** (`p03-s02` and `p03-s03`) without rewriting them. Other **54 units**, all 340 existing comprehension questions, 350 vocabulary entries and 669 curated grammar annotations stayed exact.
- The former 14 identical p03 openings `Dem stehen jedoch gewichtige Einwände gegenüber.` and their generic p03-s04 conclusions were removed in those fourteen units.
- Scoped full-text grammar went from **4345 to 4298**: 56 invalid references to removed sentences retired; 95 annotations for the unchanged middle sentences exactly repositioned; **9 manually verified, varied constructions** added. This is **not** a complete native nine-lens grammar generation or completeness certification.

## Whole-pack verification and native code boundary

- Independent structural/source integrity: **{qa['checks_total']}/{qa['checks_total']} checks PASS**, {len(qa['negative_cases'])}/{len(qa['negative_cases'])} adversarial corruptions detected.
- All 4,298 full-text offsets match their exact target substrings and source sentences; exact mappings between 68 source items and v505 runtime entries match.
- Actual unmodified **v505-R141 Wordlinks R3** `01-App/modules/reading-content-import-v38.js` loaded in Node VM: **PASS, 0 errors, 0 warnings**, 7 deliberately broken payloads rejected. Isolated in-memory adapter projection: 68 units, 340 exercises. No browser/IndexedDB transaction performed.
- Candidate runtime: 68 entries, 478 multilingual passages, 340 questions, 350 vocabulary entries, 669 curated grammar, **4,298 scoped exact grammar occurrences**.

## Important unresolved quality issues

- Duplicate p03-s03 general conclusion remains in **41** lessons (`Ein Vorteil auf der einen Seite ...`).
- Duplicate p02-s03 general conclusion remains in **55** lessons (`Dadurch kann ein Nutzen entstehen ...`).
- These exact repetitions are an editorial review queue, **not evidence that all 96 need blanket substitution**. Inspect topic-specific arguments, translations and grammar anchoring before any changes.
- Whole-pack independent German–Persian–English semantic **Stage4 HOLD**. Native full nine-lens grammar engine **NOT RUN**. Browser/IndexedDB **Stage6 NOT RUN**. **Stage7 NOT RELEASED**.
- All future changes start from the curated R14 candidate. Do **not** rewind to source book/PDF. Do not modify app UI or user's SRS/FSRS records.

## Immutable current, parent and candidate

- Original curated v1.3.0 CURRENT ZIP still unchanged, SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.
- Parent R13 master SHA256 `d619d7d9777849a25a154b52574b66a3dd92fc4f4d045e7b4ceb4e0fbc16b30f`; parent R13 runtime SHA256 `628f56e6bab608a6ab5f7a8939eea3a8451f1fbc4a8699bcaeb23a56f10d78a7`.
- R14 **content candidate** `{master}` SHA256 `{sha(master)}`, { (P/master).stat().st_size } bytes.
- R14 **v505 runtime preentry candidate** `{runtime}` SHA256 `{sha(runtime)}`, { (P/runtime).stat().st_size } bytes.
- Report, before/after ledger, independent verifier and deterministic source-aware transport tools accompany these candidates; no temporary artifacts were promoted into CURRENT.
'''
(P/'LESEN-R14-EDITORIAL-AND-V505-REPORT-20261107.md').write_text(report,encoding='utf8')
checkpoint={'schema':'lesen-quality-review-checkpoint-r14@1.0.0','date':'2026-11-07','owner':'Workspaces/lesen-praesentation','family':'family:lesen',
 'status':'R14_14_P03_TRILINGUAL_SOURCE_STRUCTURAL_PASS__V505_PREENTRY_PASS__CURRENT_UNCHANGED_STAGE4_6_7_HOLD',
 'original_current':{'sha256':'558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565','library_file_id':'libfile_9b768265ff3c8191aca371baa38551d7','status':'CURRENT_IMMUTABLE_NOT_PROMOTED'},
 'parent_r13':{'content_sha256':'d619d7d9777849a25a154b52574b66a3dd92fc4f4d045e7b4ceb4e0fbc16b30f','runtime_sha256':'628f56e6bab608a6ab5f7a8939eea3a8451f1fbc4a8699bcaeb23a56f10d78a7'},
 'candidate_content':{'name':master,'sha256':sha(master),'bytes':(P/master).stat().st_size,'library_file_id':None,'path':'/Flasch kart/German-Content-Production-Kit/Content/Lesen/Candidates/'+master,'role':'CANDIDATE_NOT_CURRENT'},
 'candidate_runtime':{'name':runtime,'sha256':sha(runtime),'bytes':(P/runtime).stat().st_size,'library_file_id':None,'path':'/Flasch kart/German-Content-Production-Kit/Content/Lesen/Candidates/'+runtime,'role':'PREENTRY_CANDIDATE_NOT_NATIVE_BROWSER_STAGE6'},
 'actual_edits':{'unit_ids':ledger['changed_unit_ids'],'changed_units':14,'revised_de_sentences':28,'trilingual_sections_changed':14,'source_specific_middle_sentences_preserved':28,'untouched_units':54,'questions_unchanged':340,'vocabulary_unchanged':350,'curated_grammar_unchanged':669},
 'grammar':{'previous_count':4345,'old_removed':56,'old_middle_exact_reanchored':95,'new_scoped_attested':9,'current_count':4298,'source_nine_lens_engine_rerun':False},
 'tests':{'independent_static_checks':qa['checks_total'],'independent_static_errors':0,'adversarial_structural_rejections':9,'actual_v505_source_preentry':'PASS_0_WARNINGS','v505_native_negative_cases_rejected':7,'browser_indexeddb_stage6':'NOT_RUN','whole_semantic_stage4':'HOLD','stage7':'NOT_FINAL'},
 'remaining':{'original_14_p03_generic_openings':0,'repeated_p03_s03_general_sentences':41,'repeated_p02_s03_general_sentences':55},
 'report':'Workspaces/lesen-praesentation/Reports/LESEN-R14-EDITORIAL-AND-V505-REPORT-20261107.md',
 'evidence_files':['LESEN-R14-14P03-TRILINGUAL-GRAMMAR-LEDGER.json','LESEN-R14-TRILINGUAL-SCOPED-REVIEW.json','LESEN-R14-INDEPENDENT-STRUCTURAL-QA.json','LESEN-R14-v505-NATIVE-PREENTRY.json','LESEN-R14-RUNTIME-TRANSPORT-EVIDENCE.json'],
 'no_app_ui_fsrs_srs_change':True,'no_current_mutation':True,'no_file_deletion':True,
 'next_action':'Review p02-s03 55 and p03-s03 41 identical conclusions by topic in bounded trilingual batches; require source-grounded changes and exact grammar QA; then independent Stage4 and isolated Stage6.'}
(P/'QUALITY-REVIEW-CHECKPOINT-R14-20261107.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'master_sha':sha(master),'runtime_sha':sha(runtime),'report_lines':len(report.splitlines()),'pending':[v['identical_count'] for v in backlog]},indent=2))