import pathlib,json,hashlib,datetime
P=pathlib.Path('/mnt/data/lesen_r16_20261107')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cont=P/'Lesen-Production-Master-v1.3.0-R16-22CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
run=P/'Lesen-R16-v505-22CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'
ledger=json.loads((P/'LESEN-R16-22CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json').read_text())
qa=json.loads((P/'LESEN-R16-INDEPENDENT-SOURCE-QA.json').read_text())
native=json.loads((P/'LESEN-R16-v505-NATIVE-PREENTRY.json').read_text())
assert qa['error_count']==0 and qa['checks_total']==12672 and native['checks']['candidate_pack_status']=='PASS' and len(native['checks']['candidate_warnings'])==0
rpt=f'''# Lesen R16 — topic-grounded p02/p03 conclusions, 2026-11-07

## Result and scope
- **Authoritative parent**: R15 Library content `libfile_4e9ee6f0ef388191a6a26302b70c4af4`, SHA `efa0fa9ece712f3a045ef47c802efe9230fe1baa366cb43e7f3ba5a8573e4c67`.
- **Curated CURRENT**: original v1.3.0 ZIP SHA `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` unchanged. R16 is a candidate, NOT current/final.
- 13 lessons changed: 025–034 and 036–038. Lesson 035 explicitly preserved because the content was already repaired.
- 22 **German** generic concluding sentences changed in `p02` and `p03`; 55 other lesson objects were byte-equivalent at the JSON-data level, all 340 question identities and 350 vocabulary entries unchanged. The 44 existing Persian/English concluding translations of those 22 sections were **preserved verbatim**, because they already reflected each lesson's specific argument. German was improved to align with them and the preceding German sentences. No fabricated translation edits were claimed.
- All original p02/p03 first two sentences and their FA/EN translations retained exactly.
- 70 invalid obsolete grammar occurrences on removed German endings retired; ten existing curated Relativsatz samples retargeted to **actual** newly written relative clauses; ten narrow/manual full-text relative-clause occurrences added with exact offsets and explicit non-native provenance. Overall 4,220 -> **4,160** occurrences; all 669 curated grammar identities and 68 lesson identities preserved. Native full nine-lens extraction **not rerun**.
- Repeated generic conclusions still remain: **p02=28, p03=21** (49 sentences across possibly overlapping lessons). These are a review queue; do not mass-replace by template.

## Illustrative evidence
- **025, good study organization**: `Realistische Lernpläne schaffen Freiräume, die auf Dauer konzentriertes Arbeiten und höhere Produktivität ermöglichen.` The pre-existing FA/EN translations already said productivity improves over time.
- **026, film vs book**: `Was den Film schnell zugänglich macht, kann zugleich einen Teil der eigenen Vorstellung beim Lesen verdrängen.` This now reflects the approved translation's explicit tradeoff.
- **031, smartphones as educational media**: `Das gleiche Gerät, das spontan beim Lernen hilft, kann durch Benachrichtigungen zugleich die Konzentration stören.` The German now makes the educational benefit/distraction contrast explicit.
- **035, devices at school**: entirely unchanged; already had source-grounded conclusions from R2.

## Tests and limitations
- Independent read-only source/runtime QA: **{qa['checks_total']} checks, {qa['error_count']} errors**, 9/9 adversarial mutations detected.
- Exact real v505 `reading-content-import-v38.js` source pre-entry validator: PASS, **zero warnings**, 7/7 broken packs rejected. In-memory projection: 68 lessons and 340 exercises. **NO browser or IndexedDB Stage6 run.**
- Runtime is a scoped, verified delta transport, not a native compiler re-execution or an app release.
- AI-scoped source/translation alignment was reviewed in this batch; **independent holistic Stage4** for all 68 lessons is **HOLD**, native complete nine-lens engine **NOT_RERUN**, browser Stage6 **NOT_RUN**, release Stage7 **NOT_RELEASED**.
- No source-PDF restoration, no app UI, FSRS/SRS, installed user-data or other content-family changes. No automatic deletion.

## File identities
- R16 master: `{cont.name}`, SHA256 `{sha(cont)}`, {cont.stat().st_size:,} bytes.
- R16 v505 runtime: `{run.name}`, SHA256 `{sha(run)}`, {run.stat().st_size:,} bytes.
- Detailed before/after with actual already-existing FA/EN end translations: `LESEN-R16-22CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json`.
- Independent QA: `LESEN-R16-INDEPENDENT-SOURCE-QA.json`.
- Exact importer QA: `LESEN-R16-v505-NATIVE-PREENTRY.json`.
- Reproducible scripts: `build_r16.py`, `build_r16_runtime.py`, `verify_r16_independent.py`, `verify_v505_r16_preentry.js`.

## Next
Review next source-grounded batches of generic conclusions, for example 039–052, excluding already-specialized conclusions. In parallel conduct a genuinely independent trilingual editorial quality audit on each lesson, preserving current curated authority; Stage4 must not be inferred from structural PASS. Keep source-owner canonical `Workspaces/lesen-praesentation` and one final release ZIP only after all release gates.
'''
(P/'LESEN-R16-EDITORIAL-AND-V505-REPORT-20261107.md').write_text(rpt,encoding='utf8')
checkpoint={'schema':'lesen-quality-review-checkpoint-r16@1.0.0','date':'2026-11-07','owner':'Workspaces/lesen-praesentation','family_id':'family:lesen',
 'state':'R16_22_SOURCE_GROUNDED_CONCLUSIONS_INDEPENDENT_STRUCTURE_PASS__V505_PREENTRY_PASS__CURATED_CURRENT_UNCHANGED_STAGE4_6_7_HOLD',
 'original_current':{'sha256':'558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565','library_file_id':'libfile_9b768265ff3c8191aca371baa38551d7','status':'IMMUTABLE_CURRENT'},
 'parent_r15':{'master_sha256':'efa0fa9ece712f3a045ef47c802efe9230fe1baa366cb43e7f3ba5a8573e4c67','runtime_sha256':'52b0d807bf1c9ab6dbc80011ddb98d131594ebdb4544981a8d0a1c9c22489e33'},
 'candidate_master':{'name':cont.name,'sha256':sha(cont),'bytes':cont.stat().st_size,'status':'CANDIDATE_NOT_CURRENT','library_file_id':None},
 'candidate_runtime':{'name':run.name,'sha256':sha(run),'bytes':run.stat().st_size,'status':'V505_PREENTRY_ONLY_NOT_BROWSER_STAGE6','library_file_id':None},
 'scope':{'edited_units':ledger['changed_units'],'edited_units_count':13,'edited_conclusion_sentences':22,'unchanged_units':55,'existing_fa_en_conclusion_sentences_preserved':44,'all_question_ids_preserved':340,'all_vocab_preserved':350,'curated_grammar_ids_preserved':669,'obsolete_fulltext_occurrences_retired':70,'new_manual_verified_relative_clauses':10,'retargeted_10_curated_relative_clause_examples':10,'grammar_before':4220,'grammar_after':4160,'remaining_exact_duplicate_p02_s03':28,'remaining_exact_duplicate_p03_s03':21},
 'QA':{'independent_source_structural_checks':12672,'independent_errors':0,'adversarial_source_negatives':'9/9_REJECTED','actual_v505_preentry':'PASS_ZERO_WARNINGS','native_corrupt_pack_negatives':'7/7_REJECTED','in_memory_projection':'68_UNITS_340_EXERCISES_PASS','holistic_independent_stage4':'HOLD','native_nine_lens_rederive':'NOT_RERUN','browser_indexeddb_stage6':'NOT_RUN','stage7':'NOT_RELEASED'},
 'evidence':{'report':'Workspaces/lesen-praesentation/Reports/LESEN-R16-EDITORIAL-AND-V505-REPORT-20261107.md','ledger_sha256':sha(P/'LESEN-R16-22CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json'),'independent_QA_sha256':sha(P/'LESEN-R16-INDEPENDENT-SOURCE-QA.json'),'native_v505_QA_sha256':sha(P/'LESEN-R16-v505-NATIVE-PREENTRY.json')},
 'next_action':'Review source-bound conclusions 039-052 selectively. Independent trilingual Stage4 remains a gate. No CURRENT promotion or auto-delete.'}
(P/'QUALITY-REVIEW-CHECKPOINT-R16-20261107.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'master_sha':sha(cont),'runtime_sha':sha(run),'report_sha':sha(P/'LESEN-R16-EDITORIAL-AND-V505-REPORT-20261107.md'),'checkpoint_sha':sha(P/'QUALITY-REVIEW-CHECKPOINT-R16-20261107.json')},indent=2))