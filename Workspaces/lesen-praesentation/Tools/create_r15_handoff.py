#!/usr/bin/env python3
"""R15 evidentiary handoff, strictly candidate-only and no current promotion."""
import pathlib,json,hashlib,collections
P=pathlib.Path('/mnt/data/lesen_r15_20261107')
M=P/'Lesen-Production-Master-v1.3.0-R15-25CONCLUSIONS-TRILINGUAL-CANDIDATE.json';R=P/'Lesen-R15-v505-25CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json';L=P/'LESEN-R15-25CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json';QA=P/'LESEN-R15-INDEPENDENT-STRUCTURAL-QA.json';N=P/'LESEN-R15-v505-NATIVE-PREENTRY.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
master=read(M);ledger=read(L);qa=read(QA);native=read(N)
assert qa['errors_count']==0 and qa['status'].startswith('PASS') and native['checks']['candidate_pack_status']=='PASS'
assert all(r['rejected'] for r in qa['adversarial_negative_cases']) and all(r['rejected'] for r in native['checks']['negative_cases'])
assert len(ledger['before_after'])==25
source_review=[]
for row in ledger['before_after']:
 unit=next(x for x in master['items'] if x['id']==row['unit_id'])
 section=next(s for s in unit['reading']['sections'] if s['id']==row['section_id'])
 original_s01_s02=[s['text'] for s in section['sentences'][:2]]
 source_review.append({
  'unit_id':row['unit_id'],'title_de':row['title_de'],'section_id':row['section_id'],
  'source_evidence_original_s01_s02':original_s01_s02,
  'authored_claim_de':row['after_de'],
  'authored_claim_fa':row['after_fa'].split(row['old_first_two_fa_en_prefix_preserved']['fa']+' ',1)[-1],
  'authored_claim_en':row['after_en'].split(row['old_first_two_fa_en_prefix_preserved']['en']+' ',1)[-1],
  'translation_prefix_preserved':True,
  'editorial_reason':'Replace nonspecific repeated conclusion with a topic-specific consequence/inference supported by the preserved first two sentences.',
  'review_limit':'AI scoped alignment and source-context review; not independent linguistic Stage4 or native grammar regeneration.'
 })
scoped={'schema':'lesen-r15-25-conclusions-trilingual-ai-scoped-review@1.0.0','date':'2026-11-07',
 'master_sha256':sha(M.read_bytes()),'status':'SCOPED_AI_REVIEW_NOT_HOLISTIC_INDEPENDENT_STAGE4',
 'reviewed_conclusion_sentences':len(source_review),'language_alignment':'DE_FA_EN_AUTHORED_PER_SENTENCE',
 'source_authority':'R14 curated lesson passages, not book/PDF original',
 'checks':'25 source-related German conclusions and their Persian/English translations, unchanged source first two sentences',
 'limitations':['No external independent native-speaking semantic reviewer','Remaining generic text and global discourse coherence not fully reviewed','Native full nine-lens grammar engine not rerun','Browser Stage6 not run'],
 'items':source_review}
write(P/'LESEN-R15-TRILINGUAL-SCOPED-REVIEW.json',scoped)
meta={'schema':'lesen-quality-review-checkpoint-r15@1.0.0','date':'2026-11-07',
 'owner':'Workspaces/lesen-praesentation','family_id':'family:lesen',
 'status':'R15_25_SOURCE_GROUNDED_CONCLUSIONS__INDEPENDENT_STRUCTURE_AND_V505_PREENTRY_PASS__CURRENT_UNCHANGED_STAGE4_6_7_HOLD',
 'authoritative_current_immutable':{'library_file_id':'libfile_9b768265ff3c8191aca371baa38551d7','sha256':'558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565','role':'CURRENT_UNCHANGED_NOT_FINAL'},
 'parent_r14':{'master_sha256':'40f4eee25d4ea541d33f91f327bc88243ec5e2971419927ae43c2f0035af2568','runtime_sha256':'84b4e1aa8ad6f9299545eb52b2a730474dfc91e635be5cbd843d8e2bca4ea4f3'},
 'candidate_content':{'name':M.name,'sha256':sha(M.read_bytes()),'bytes':M.stat().st_size,'library_path':'/Flasch kart/German-Content-Production-Kit/Content/Lesen/Candidates/'+M.name,'library_file_id':None,'role':'CANDIDATE_NOT_CURRENT','postupload_byte_readback':'PENDING'},
 'candidate_runtime':{'name':R.name,'sha256':sha(R.read_bytes()),'bytes':R.stat().st_size,'library_path':'/Flasch kart/German-Content-Production-Kit/Content/Lesen/Candidates/'+R.name,'library_file_id':None,'role':'V505_PREENTRY_CANDIDATE_NOT_BROWSER_STAGE6','postupload_byte_readback':'PENDING'},
 'scope':{'units_changed':14,'units':'LES-PRES-011..024','sections_changed':25,'de_fa_en_conclusion_sentences_changed':25,'other_units_exact_unchanged':54,
 'p02_s03_remaining_exact_template':41,'p03_s03_remaining_exact_template':30,'questions_stable':340,'vocabulary_stable':350,'curated_grammar_count':669,
 'retired_invalid_old_fulltext_occurrences':78,'old_grammar_total':4298,'new_grammar_total':4220,
 'existing_curated_relative_examples_retargeted':9,'native_full_lens_regeneration':False},
 'qa':{'independent_structural_checks':qa['checks_total'],'independent_failures':qa['errors_count'],'adversarial_controls_rejected':len(qa['adversarial_negative_cases']),
 'native_current_v505_source_validator':'PASS_ZERO_ERRORS_ZERO_WARNINGS','native_source_negative_rejected':len(native['checks']['negative_cases']),
 'in_memory_projection':'PASS_68_UNITS_340_EXERCISES',
 'full_independent_semantic_stage4':'HOLD','source_native_nine_lens_engine':'NOT_RERUN','native_browser_indexeddb_stage6':'NOT_RUN','stage7':'NOT_RELEASED'},
 'evidence':{'report':'Workspaces/lesen-praesentation/Reports/LESEN-R15-EDITORIAL-AND-V505-REPORT-20261107.md',
 'ledger':'LESEN-R15-25CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json','scoped_review':'LESEN-R15-TRILINGUAL-SCOPED-REVIEW.json',
 'independent_structural':'LESEN-R15-INDEPENDENT-STRUCTURAL-QA.json','native_preentry':'LESEN-R15-v505-NATIVE-PREENTRY.json'},
 'preserved':{'no_current_promotion':True,'no_app_source_ui_change':True,'no_user_srs_fsrs_change':True,'no_library_deletion':True},
 'next_action':'Review next 14-lesson cohort 025..038, skipping prior corrected lesson 035; avoid replacing useful sentences. Then independent holistic Stage4, native grammar derivation if available, isolated native browser Stage6.'}
write(P/'QUALITY-REVIEW-CHECKPOINT-R15-20261107.json',meta)
msg=f'''# Lesen R15 — 25 topic-grounded concluding sentences in 14 lessons

**Date:** 2026-11-07  
**Owner:** `Workspaces/lesen-praesentation`  
**Status:** SOURCE-SCOPED CANDIDATE; not CURRENT, not final, Stage4/6/7 HOLD.

## What actually changed

- 14 lessons: LES-PRES-011…024; 25 sections (14 p02 plus 11 p03).
- Replaced **25 copied generic German conclusions** with unique, topic-specific consequences supported by each section's first two unchanged sentences. Wrote matching Persian and English concluding sentences. Their first two sentences in DE/FA/EN remain verbatim, as do all 54 untouched lessons.
- Retired **78 now-invalid old full-text grammar spans** tied to removed German sentences; no new grammar occurrences invented or bulk regenerated. All **4,220** remaining spans match their exact source offsets. Nine existing curated Relativsatz examples were legitimately retargeted to *new sentences with real relative clauses* and explicitly marked editorially retargeted.
- All 68 original IDs, 340 Q/A identities, 350 vocabulary and 669 curated grammar ID records remain stable.

## Results

| Test | Result |
|---|---|
| Independent read-only source/runtime checks | **{qa['checks_total']} / {qa['checks_total']} PASS** |
| Corruption/negative tests in independent QA | **{len(qa['adversarial_negative_cases'])} / {len(qa['adversarial_negative_cases'])} correctly rejected** |
| Exact CURRENT v505 reading import source validator | **PASS, zero errors and zero warnings** |
| Native source corruption controls | **{len(native['checks']['negative_cases'])} / {len(native['checks']['negative_cases'])} rejected** |
| In-memory record projection | **68 reading units / 340 exercises PASS** |
| Library checksum/readback | **PENDING UPLOAD** |

## Remaining content work

**41 p02** and **30 p03** identical generic conclusions remain (71 *sentences*, not 71 lessons); semantic/discourse QA remains larger than the template clean-up. The separate p04 template opening clean-up is completed in the previous R13.

## Boundaries

The actual historical 9-lens German grammar engine was **not rerun**. Native browser/IndexedDB import and preservation (Stage6) **not run** due to environment restrictions. Cross-content independently verified DE–FA–EN linguistic Stage4 **HOLD**; Stage7 **NOT RELEASED**. The curated v1.3.0 delivery ZIP remains immutable CURRENT, and no user study data, UI, or SRS/FSRS were touched.

Master SHA256: `{sha(M.read_bytes())}`  
Runtime SHA256: `{sha(R.read_bytes())}`  
Parent R14 master: `40f4eee25d4ea541d33f91f327bc88243ec5e2971419927ae43c2f0035af2568`.
'''
(P/'LESEN-R15-EDITORIAL-AND-V505-REPORT-20261107.md').write_text(msg,encoding='utf8')
print('Handoff created; M',sha(M.read_bytes()),'R',sha(R.read_bytes()),'QA',qa['checks_total'])