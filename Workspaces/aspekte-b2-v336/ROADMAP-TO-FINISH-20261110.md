# Aspekte B2 — feste Abschluss-Roadmap / نقشهٔ نهایی پروژه

**Checkpoint:** 2026-11-10 · owner-curated current is authoritative · no original textbook reconciliation.

**Einzige Inhaltsquelle / تنها مرجع داده:** `Current/ASPEKTE-B2-FINAL-MASTER-1719-CURATED-NONIMPORT.tsv` (1719 rows, 66 columns, SHA-256 `b87f1924826e394e995cf2f9651d3505d4de4300c1d1fac1b0f578f9e5972d92`). The 10 lesson-level Current CSVs are preserved as validated recovery snapshots, not parallel work branches. At the end of each accepted content edit, update *this* Master, preserve a backup, verify row/ID/cell differences and update GitHub checkpoint.

## Completed — do not reopen
- [x] HF2 morphological front-form remediation: **643/643** completed across all lessons.
- [x] Merge all post-HF2 curated Current files: **1719/1719 cards**, **10/10 sources**, **66 union columns**.
- [x] Lossless reconstruction of all 10 lesson CSVs from Master: **10/10 exact cell equality**.
- [x] **3438** DE–FA primary pairs, **4891** collocations; no card-ID collisions and no import/SRS mutation.
- [x] Persistent Library Master SHA readback: exact byte match.

## Stage 4 — inhaltliche Qualitätskontrolle / کنترل معنایی (IN PROGRESS)
**Fixed scope:** all 1719 Master cards, lesson by lesson, L01 through L10, at most **three coherent passes per lesson** (not 10-word microbatches):
1. Meaning, POS, Rektion, Persian senses and sense priorities (DE↔FA, all important meanings remain on one card).
2. Examples/translations, Synonyme/Antonyme, Kombinationen and Wortnetz linked to relevant senses; preserve good existing content.
3. Only if needed, bounded targeted corrections + front/back field-level diff, backup, full structural QA and Library SHA readback. Do not add a separate post-fix re-review loop.

**Accountability / Definition of done:** exactly 1719 card decisions in one Stage4 ledger: `PASS`, `CORRECTED`, or `DOCUMENTED_EXCEPTION` (with explicit reason). A lesson is closed when its full roster has a decision, its edits are applied to the Master and validated, and its count is reconciled. No external independent human signature, no textbook-source comparison. Old QA status labels mentioning “independent” are historical only, not operative gates.

**Progress now:** L01–L05 **CLOSED**: L01 158/158 (117 CORRECTED, 41 PASS), L02 110/110 (90 CORRECTED, 20 PASS), L03 186/186 (114 CORRECTED, 72 PASS), L04 183/183 (156 CORRECTED, 27 PASS), L05 227/227 (189 CORRECTED, 38 PASS; 254 exact field changes). **864/1719 editorial decisions complete; 855 remain** in five lessons L06–L10. All 1492 non-L05 records byte-exact preserved. **Next: L06 141 cards (max three bounded passes).**

| Lektion | Karten | Stage 4 semantic decisions |
|:--|--:|--:|
| L01 | 158 | 158 / 158 (CLOSED: 117 CORRECTED, 41 PASS) |
| L02 | 110 | 110 / 110 (CLOSED: 90 CORRECTED, 20 PASS) |
| L03 | 186 | 186 / 186 (CLOSED: 114 CORRECTED, 72 PASS) |
| L04 | 183 | 183 / 183 (CLOSED: 156 CORRECTED, 27 PASS) |
| L05 | 227 | 227 / 227 (CLOSED: 189 CORRECTED, 38 PASS) |
| L06 | 141 | 0 / 141 |
| L07 | 222 | 0 / 222 |
| L08 | 180 | 0 / 180 |
| L09 | 161 | 0 / 161 |
| L10 | 151 | 0 / 151 |
| **TOTAL** | **1719** | **864 / 1719** |

## Stage 5 — final regression & risk disposition (NOT STARTED)
One **single all-1719** regression: Master schema/IDs/counts, absence of unintended diffs, 3438 bilingual examples, 4895 collocations (or documented content revisions), semantic decision coverage 1719/1719. Every remaining `DOCUMENTED_EXCEPTION` has an explicit decision (hold/exclude/resolve). Produce one release-candidate QA receipt and reproducible hash. No new rounds merely for confirming original publisher fidelity.

## Stage 6 — isolated technical import/SRS readiness (NOT STARTED; no automatic import)
Run **one documented native-app import dry-run** and ID/SRS continuity/rollback test using exact target app and existing accepted-card IDs, when supported. Until tests pass, file remains `NONIMPORT` and **zero cards are marked release approved**. If environment cannot access the native app/IDs, record the concrete blocker once; stop and hand off the runnable artifact to Codex / app environment instead of looping. Live SRS import is not performed without an explicit request.

**Terminal rule:** no new HF/Phase/Scenario may be opened without a verified new defect and a measurable impact on the above acceptance criteria. After each message report `master SHA / lesson / reviewed / edited / remaining / blocker / next exact batch`. Don't claim success for tests that were not actually executed.

## Latest Stage 4 applied patch — 2026-11-10
- `ab2-l01-u-1692`: `die Hommage (an + Akk.)` → `die Hommage, die Hommagen (an + Akk.)` (Duden: https://www.duden.de/rechtschreibung/Hommage).
- Changed exactly one `front_de_preview` cell in 1719-row unified Master; all other cells unchanged; original master backed up at `Checkpoints/STAGE4-L01-P1-MASTER-BACKUP-20261110`.
- Updated master SHA256: `85159cecc31fc09df066715777f362dbbac1f7e3f34428e74e2ce325c55cc4e5`; Library readback byte-exact. Ledger: `Reports/B2-STAGE4-CARD-STATUS-1719-20261110.tsv`.

## 2026-11-10 Stage 4 L01 closure (phases 2 and bounded 3)
- Reviewed all 158 lesson cards, both DE/FA example pairs and existing collocations, and sense-scoped relation fields.
- 116 `synonyms_de_sense_scoped` fields, 34 `antonyms_de_sense_scoped` fields, 1 `collocations_de` field and 1 `example_2_fa` field updated (152 field values across 117 cards); 41 cards retained PASS. Do not invent synonyms/antonyms for the other 42/124 cards where a safe relation was not established.
- L01 final semantic decisions: 158/158, all other lessons still pending (1561).
- Raw preimage master SHA: `85159cecc31fc09df066715777f362dbbac1f7e3f34428e74e2ce325c55cc4e5`; current master SHA: `88b3cc571d210facd7b14bcce579d7544ba86a71ff2d501d469ffe8119281a7c`. Backup and byte-exact Library readback verified; 1719 IDs/3438 example pairs and 4892 collocations preserved (1 new useful collocation).
- **Next task: L02 all 110 cards, Phase 1/3. No L01 re-review or new process.** Stage5/6 not started, release status NONIMPORT.


## 2026-11-10 Stage4 L02 closure (110/110, bounded to three phases)
- Owner-curated Master v2 SHA: `88b3cc571d210facd7b14bcce579d7544ba86a71ff2d501d469ffe8119281a7c` → Master v3 SHA: `0e3c902b4ed09b91d20f609140cf0df88fac3f2eadcd0dc1c129aa1fe683e73d`.
- **All 110 L02 cards editorially completed:** 90 CORRECTED, 20 PASS; 84 new sense-scoped synonym entries, 25 new sense-scoped antonyms, 5 collocation repairs, 2 German→Persian translation repairs and 1 fixed-expression front correction (117 field values in 90 cards). Existing 20 synonym and 11 antonym values retained; 104 L02 cards now have synonym entries, 36 have antonym entries; empty values remain when no safe equivalent.
- Specific issues fixed: `nach der Hand greifen` describes reaching **toward** the hand (not necessarily taking it); collocation of `deuten` now uses the actual verb `deuten`, not `hindeuten`; `es ernst meinen` front has the complete grammatical expression. For `ungefragt`, the Persian example no longer incorrectly requires prior permission when the German says unsolicited/without being asked.
- Full 1719 IDs preserved, 3438 bilingual pairs preserved, 4892 collocations preserved. Every cell and raw-byte record of the 1609 cards outside L02 unchanged. Backup in Library checkpoint folder; new master re-downloaded and exactly SHA verified. **Five deliberately mutated inputs blocked by fail-closed QA** (wrong SHA, duplicated ID, mutation outside lesson, unauthorized back edit, missing card).
- `Reports/B2-STAGE4-CARD-STATUS-1719-20261110.tsv` records 268 completed Stage4 decisions; **1451 remaining**. Stage5 and Stage6 remain NOT_STARTED. No automatic import or live SRS mutation; no mandatory external human review.
- **Next exactly: Stage4 L03, all 186 cards, max 3 coherent phases, from single Master v3**. No HF2 or L01/L02 restart.


## 2026-11-10 Stage4 L03 closure (186/186, one bounded review)
- Master v3 SHA `0e3c902b4ed09b91d20f609140cf0df88fac3f2eadcd0dc1c129aa1fe683e73d` → **Master v4 SHA `244513cc7acd1958b7f8e048def38f1290e6416670f44de121c4aee9283408da`**. One owner-curated master remains the only editable source.
- All 186 L03 cards completed: **114 CORRECTED, 72 PASS**. 140 field edits: 91 contextual Synonyme, 15 meaning-scoped Antonyme, 27 front morphology/declension repairs, 2 collocation repairs, 2 Persian meaning repairs, 1 Persian example repair, 1 German example repair, 1 Persian translation paired with that example. No invented antonyms to fill other blank cells.
- Lexical examples: Duden-verified `avancieren → ist avanciert`, `zutrauen → hat zugetraut`, `sich aufreiben → hat sich aufgerieben`; `Projektleitung` gains the team/person-leadership sense; `sich beschäftigen` example translation no longer implies professional employment; `Catering` stays in its example.
- Complete 1719 row/ID/schema QA; all 1533 other lesson records byte-exact preserved, both German/Persian primary pairs preserved (3438), collocations remain 4892; five **actually corrupted** inputs rejected, Library SHA readback exact for **Master v4 and ledger v4**. Raw backup snapshots stored in dedicated Checkpoints.
- **Stage4 progress: 454/1719 editorial decisions completed, 1265 remaining. Next exact step: L04 183 cards.** Stage5/6 remain unopened; NONIMPORT / no app or SRS mutations.


## 2026-11-10 Stage4 L04 closure (183/183, fixed roadmap)
- Master v4 SHA `244513cc7acd1958b7f8e048def38f1290e6416670f44de121c4aee9283408da` → **Master v5 SHA `12c9efc665309e59f96effa0f5a380569c1c22e1040c83963d9caa592a050850`**. One current authority remains unchanged in location.
- **All 183 L04 card decisions completed:** 156 CORRECTED, 27 PASS. Exactly **243** changed field values: 154 meaning-scoped Synonyme, 47 meaning-scoped Antonyme, 36 corrected/completed front forms and 6 sense-disambiguated Kombinationen. Overly broad antonyms excluded in final edit.
- Specific verified grammar cases: `einwerfen → wirft ein, warf ein, hat eingeworfen`; `zusammenhängen → hängt zusammen, hing zusammen, hat zusammengehangen`; `sich anschließen` with Dativ; `ausleihen` includes both lending and borrowing senses; `sicherstellen` distinguishes guarantee from police seizure.
- Master and ledger before/after snapshots retained in `Checkpoints/STAGE4-L04-MASTER-LEDGER-BACKUP-20261110`. Master v5 and ledger v5 readback SHA byte-exact. 1719 cards and 3438 DE/FA primary example pairs preserved; 4893 combinations; all 1536 non-L04 card rows preserved byte-exact. Six actually corrupted cases rejected in fail-closed QA. No live SRS or import mutations; `NONIMPORT`.
- **Stage4 now 637/1719 editorial decisions complete, 1082 remain. Next exact: L05 227 cards (up to 3 coherent passes).** Stage5/Stage6 not started and no new review loop opened.


## 2026-11-10 Stage4 L05 closure (227/227; no new review loop)
- One owner-curated 1719-card master, v5 SHA `12c9efc665309e59f96effa0f5a380569c1c22e1040c83963d9caa592a050850` → **v6 SHA `b87f1924826e394e995cf2f9651d3505d4de4300c1d1fac1b0f578f9e5972d92`**. Master and 1719-card ledger both SHA read back byte-exact from Library.
- **All 227 L05 decisions closed:** 189 CORRECTED, 38 PASS. 254 exact scoped field edits: 187 meaning-restricted synonyms, 49 explicit context-scoped antonyms/contrasts, 7 front grammar/plural repairs, 5 collocation improvements, 1 first example Persian translation, 1 German+2 Persian second-example changes, 2 Persian back sense repairs. Empty semantic cells remain when exact equivalence cannot be defended.
- Notable fixes: `übereinstimmen, stimmte überein, hat übereingestimmt` (Duden); full article/plural on `Nachwuchskraft`, `Schneeball`, `Damm`, `Laus`, `Ruheraum`; `einen Beitrag leisten` complete tense forms; `Ingenieurwissenschaft` sentence Persian grammatical number; `Strauß` second example now teaches ostrich vs flower bouquet; `Ruf` includes university appointment sense.
- Exact byte-preserving master patch; **all 1492 other-lesson records unchanged**; 1719 unique IDs, 3438 DEFA primary example pairs, 4895 combinations, release flags FALSE. Six actually corrupted candidates rejected. Original master+ledger snapshots retained in `Checkpoints/STAGE4-L05-MASTER-LEDGER-BACKUP-20261110`. No live app imports/SRS mutations.
- **Stage4: 864/1719 reviewed and decided, 855 remain. Next L06 141 cards**. Stage5 one regression and Stage6 one native app/SRS dry-run remain NOT_STARTED. NONIMPORT.


## 2026-11-20 Stage4 L06 closure (141/141; three bounded phases)
- **Authoritative Library owner: Master v9 SHA256 `6e6435e7d226c3ed13ca7360b69755f047332a08b6594924993858822544ce38`, Ledger v9 SHA256 `00d786792844edb27e286c41ac17aa52895f7aab5802c23b8e7fb847102ecbeb`; both exact-byte read back from the canonical Library files.** No new parallel source.
- Phase2 applied 160 field improvements on 124 L06 cards; Phase3 resolved **20 example-overlapping Kombinationen** and **4 circular/redundant synonym paraphrases** on 23 L06 cards. Final cumulative L06 content delta from the v7 starting point: **125 cards** changed, 180 field changes. No 1578 other-lesson Master or Ledger records changed in these passes.
- **All 141 L06 final editorial decisions:** 125 CORRECTED, 16 PASS. 1719 unique IDs; 3438 bilingual example pairs; 4895 collocations preserved. Formal native-app release and SRS import NOT attempted; all content remains `NONIMPORT`.
- **Stage4 progress: 1005/1719 editorial decisions complete; 714 remain (L07–L10). Next precisely L07 Phase 1/3 for all 222 cards** from verified Master v9. No re-open of L01–L06 and no old Library sync loop. See `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L06-141-CLOSED-RECEIPT-20261120.json`.


## 2026-11-20 Stage4 L07 Phase 1/3 (all 222 cards; phase2 next)
- Library single owner **Master v10 SHA256 `a979973903bacf092f47cbb600a339290b7daf7cd0ad72fdf8c99725174c9032`** and **Ledger v10 SHA256 `15565bc09e6e7f34c2c17ca540757c6b2d50c24df4ea48614c1d63a5c8bbbf6d`**, both exact-byte readback verified. Previous v9 retained through version history. 1719 IDs and all 1497 non-L07 rows byte-exact preserved.
- All 222 L07 fronts/backs and two DE–FA example slots structurally screened; each has 3 combinations. Exactly **1 actual learner-facing correction**: `aufschwingen` (intransitive door `ist aufgeschwungen`; reflexive `hat sich aufgeschwungen`) with source/dictionary confirmation. 44 priority flagged, 107 multisense tags, 88 relation-alignment tags, 4 legacy-duplicate tags; 20 combination/example exact-overlap candidates for Phase2; zero existing L07 sense-scoped synonym and antonym fields require justified enrichment.
- No L07 final Stage4 decision prematurely assigned; cumulative final decisions remain **1005/1719**, **714** pending. **Next precisely L07 Phase2/3 on all 222 cards** for meaning, idiom, German/Persian examples, sense-scoped relations and collocation overlap; then bounded Phase3/3 final dispositions. `NONIMPORT`, no app/SRS mutations. Receipt `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L07-PHASE1-222-RECEIPT-20261120.json`.


## 2026-11-20 Stage4 L07 Phase 2/3 — all 222 cards, Library v11 verified
- Single authoritative content owner **Master v11 SHA256 `143a637b0fa0014c3ade569e488bc28874d7b395b9e1b72ebdb616e7c4ab2ff0`**, **Ledger v11 SHA256 `98379810c95020371648759ffb3c5f4f952409cdd7cd95009a1e7fec3c9e9031`**; both files read back from Library and compared byte-exact. All 1,719 IDs and all 1,497 non-L07 rows preserved.
- **221 L07 cards genuinely changed, 600 field edits:** 201 sense-scoped synonym fields; 59 antonym fields (remaining blank when no defensible lexical opposite); 98 word-family fields; 218 related-word fields (exact cross-category duplicates excluded); 20 independent collocation rewrites where a full phrase overlapped an example; four Persian sense explanations clarified. Two bilingual example pairs per card are preserved. Full before/after diff is in the working edit receipt; no raw source or SRS mutation.
- **L07 phase3/3 next:** all 222 card-specific final editorial decisions from v11, not another general enrichment pass. Stage4 previously closed decisions still **1005/1719**; **714 remain** including L07. Release remains NONIMPORT; no native app test or blanket linguistic release claim. GitHub QA receipt: `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L07-PHASE2-222-QA-RECEIPT-20261120.json`.


## 2026-11-20 Stage4 L07 closure (222/222; three bounded phases)
- **Single authoritative Library Master v12 SHA256 `e91bd94dff3a6ded68579b488ee62534960871c0c72d39d5259f99288865f5b4`, Ledger v12 SHA256 `251b24753614721467715fdcdd7d7efc91acd5910b8f56a4a56cbb524f8bc7c6`; independently downloaded again with matching exact SHA256.** Old versions retained in Library history, not parallel current branches.
- L07 Phase1 screened all 222 and corrected the `aufschwingen` auxiliary in the learner front. Phase2 changed **600 content fields on 221 cards**, including 20 independent `Kombinationen` rewrites to prevent copying from examples. Phase3 corrected **83 more fields on 81 cards**, including removing 75 self-references in `Wortfamilie`, repairing the Evolution example and unsafe synonym/antonym equivalences. Every card has its own final Ledger decision and evidence.
- **L07 Stage4: 221 CORRECTED, 1 PASS; 222/222 case dispositions.** All 1,719 IDs and 1,497 non-L07 Master and Ledger records preserved byte-for-byte; all prior 1005 final decisions unchanged. No false app/FSRS release: NONIMPORT throughout. Structural, scoped bilingual editorial and five actual negative mutation controls passed. This is not a claim of independent specialist certification of all 222 terms.
- **Stage4: 1227/1719 final editorial decisions complete; 492 remain across L08 (180), L09 (161), L10 (151). Next exactly L08 Phase1/3 for all 180 cards.** See `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L07-222-CLOSED-RECEIPT-20261120.json`. No L07 fourth phase or repeated Stage6 browser loop.


## 2026-11-20 Stage4 L08 Phase 1/3 — 180/180 structure and form screen
- Single authoritative Library **Master v13 SHA256 `4f7c636723b345bc818d46b6fe2f0d98982d29a78b8ec938f509d93d433635e2`** and **Ledger v13 SHA256 `b7cd86a2b4ecc2c06be6112bba9dc6406324896a9f06ee03f1e1e6a8c027a684`** downloaded and compared byte-for-byte with new candidates; no parallel master. Both preserve 1,719 IDs, all 1,539 non-L08 rows byte-exact and all 1,227 earlier final Stage4 decisions.
- **Two verified learner-front edits:** `wachhalten, hielt wach, hat wachgehalten` (Duden compound lemma, original source unchanged) and removal of an irrelevant `Aufrüstung` number note from the distinct `die Rüstung, die Rüstungen` card. All 180 L08 fronts/backs and two DE–FA example slots structurally screened. **No blanket semantic approval.** Six negative destructive-mutation controls exercised.
- Phase2 work defined with exact evidence: **50 priority cards, 109 relation-alignment flags, 65 multi-sense flags, 11 legacy-duplicate flags; 31 literal example–collocation overlaps across 29 cards** (candidates for context review, not automatically errors). All 180 existing `Wortfamilie` fields need targeted scope/self-duplicate review. Zero existing L08 sense-scoped synonyms/antonyms; add only justified relations. One card has four combinations, not necessarily a defect.
- Stage4 remains **1227/1719 final decisions, 492 remaining**. **Next L08 Phase 2/3 all 180 cards**, then the third and last phase for 180 final editorial decisions. No Stage5/6 or native-app import. Receipt: `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L08-PHASE1-180-RECEIPT-20261120.json`.


## 2026-11-20 Stage4 L08 Phase 2/3 — 180/180 semantic-enrichment pass; v14
- Library single owner updated in-place: **Master v14 SHA256 `4c82c5916e5f786a3f1cc1e5869aa8d15ea39c0f8fa38146f7323f1ebf33d24d`**, **Ledger v14 SHA256 `2c1cd57a5828fa201018dea434bb49083a3545c4450cb2e425c5ec577043ecd4`**. Both downloaded anew from Library and verified byte-exact; 1719 unique IDs and 1539 non-L08 rows preserved literally, as are 1227 previous final decisions.
- **396 real changes on 180 L08 cards:** 125 meaning-qualified synonym fields, 52 antonym/opposite-action fields where defensible, 180 thematically related-word fields, 7 corrected word-family fields, 29 independent collocation-field rewrites replacing **31** phrases copied from example text, and three precise German–Persian example-1 fixes. Avoid guessed lexical equivalence; intentionally leave unsupported antonyms or synonyms blank.
- Structural check of both German–Persian example pairs and three or more collocations per L08 card, six actual negative mutation controls passed. No L08 final Stage4 decisions assigned yet; remains **1227/1719**, **492 pending**. Next **L08 Phase 3 of 3**, case-by-case final editorial dispositions for all 180; NONIMPORT and no SRS/app changes. Receipt: `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L08-PHASE2-180-RECEIPT-20261120.json`.


## 2026-11-20 Stage4 L08 closure (180/180; three bounded phases)
- **Single authoritative Library Master v15 SHA256 `0af61df0fe61fa1ce0a03b00a065ac5849cfe1451fee8549082c20972d308903` and Ledger v15 SHA256 `3a4560522b755f70f21aceb34b28678353cda3d5a1a819ea0cef1c21bb9d252e`**; both remotely read back and compared byte-for-byte against the reviewed candidates. 1719 unique IDs, all 1539 non-L08 Master and Ledger rows preserved, and all prior 1227 final decisions untouched.
- L08 Phase1 screened all 180 and corrected two front forms (wachhalten, Rüstung note). Phase2 made **396 real field edits** covering all 180 cards, including 31 collocation phrases copied from examples. In bounded Phase3, a **further 42 targeted field changes on 34 cards** were applied: 29 overbroad/false/circular synonyms, four word-family repairs, two Persian sense glosses, two German and two Persian example translations, two related-word fields, one copy-style combination. In particular, the technical separation between `Regelung` and `Steuerung`, German public-law meaning of `Rundfunkanstalt`, and funeral meaning of `Verabschiedungshalle` were repaired with contextual examples and sourced definitions.
- **All 180 L08 Stage4 final editorial decisions: 180 CORRECTED, 0 PASS** (each card received phase2 enrichment relative to pre-L08 v12). The row-specific decision ledger records the learner-facing sense and changed field names, not a blanket release signoff; 8 deliberate corruption tests failed closed. Semantic reviews are project editorial checks, **not** independently certified dictionary checks of every term or native-app acceptance. All content remains `NONIMPORT`, zero SRS/app mutations.
- **Stage4 progress now 1407/1719 completed, 312 remain**: L09 161 and L10 151. **Next exactly L09 Phase1/3 for all 161 cards**, without reopening previous lessons or browser Stage6 loops. Receipt `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L08-180-CLOSED-RECEIPT-20261120.json`.


## 2026-11-21 Stage4 L09 Phase1/3 — 161/161 morphology & structure screen
- Authoritative single-owner Library **Master v16 SHA256 `ede0a9f730f376ef432a09830617325def569faabdfdd661332c7b9d195cf660`** and **Ledger v16 SHA256 `318792bf157b0d4167d9fb029d161f68d4608a95106f3a180b77c7f949fd4b8c`** freshly downloaded and independently matched exact bytes after updating both original files. 1719 IDs and all 1558 non-L09 Master and Ledger records preserved byte-exact; **1407 previous final Stage4 decisions** untouched.
- Examined all **161** L09 front/back forms plus structural presence of 2 German–Persian example pairs and minimum 3 collocations per card. **5 verified field edits on 3 cards:** supply correct Präteritum/Perfekt for `sich (sehr) um etw. bemühen`; normalize official German `sich schwarzärgern`, its conjugation, one example and its collocation spelling; explicitly label both `einfrieren` auxiliaries by transitivity. Source headwords and source lineage remain unchanged; no unsupported edits.
- **Phase2 exact queue:** 11 priority cards, 55 multi-sense and 48 relation-alignment flags; 25 literal overlap candidates across 24 cards (not automatically invalid); 161 initially blank meaning-scoped synonyms and antonyms, 49 blank Wortfamilie. A single card has four combinations; not a defect by itself. Eight destructive-mutation regression controls executed and rejected.
- **Stage4 remains 1407/1719 final decisions; 312 pending**. L09 adds no premature final decisions in Phase1. **Next L09 Phase2/3 for all 161 cards**, then Phase3/3 final case dispositions. No extra Stage6/browser loop; `NONIMPORT` and zero SRS/app mutations. QA receipt: `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L09-PHASE1-161-RECEIPT-20261121.json`.


## 2026-11-21 Stage4 L09 Phase2/3 — all 161 cards edited in the single authoritative Library v17
- Single owner **Master v17 SHA256 `13708ce6f343c1ce88de2f82ece584a60b7383c255dfdc90f91d62e9c57683e0`**, **Ledger v17 SHA256 `e7efe38ac77663c88215f1a50f06ba47a568c4b84e4a4a876419fde01971f99f`**, independently downloaded and compared byte-for-byte to edited candidates. All 1,719 IDs, all 1,558 non-L09 Master and Ledger rows, all 1,407 prior case decisions unchanged.
- **387 real field edits on 161 L09 cards**: 121 meaning-scoped synonym fields (weak/circular candidates excluded), 40 defensible antonym fields (leave blank otherwise), 41 morphological word-family additions, 161 contextual related-word fields (exact duplicate family/synonym entries removed), 24 collocation-field rewrites replacing **25 phrases copied directly from examples**. Both German–Persian example pairs retained on each card; at least three independent combinations per card. Eleven deliberate destructive-mutation regression controls all rejected.
- **Not final yet:** all 161 L09 card decisions await case-specific Phase3/3 review and corrections; **Stage4 stays 1407/1719 final, 312 pending**. The word mappings are scoped editorial proposals, not claims of independent dictionary certification or app import. NONIMPORT; zero SRS/app mutations. Next exactly L09 Phase3/3, then L10 151 cards. Receipt: `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L09-PHASE2-161-RECEIPT-20261121.json`.


## 2026-11-21 Stage4 L09 closure (161/161; three bounded phases)
- **Single authoritative Library Master v18 SHA256 `d373e35a08ae0a7e7287a4ad4384ea073daecf67720b2a35fc87a57cfc47eaa3` and Ledger v18 SHA256 `d06c2f9c673bfdf79d43ec66c089a38d194a0529e329e152411d52b503728d6d`** independently downloaded after overwrite and matched byte for byte with reviewed candidates. All 1719 IDs, all 1558 non-L09 Master and Ledger rows and all 1407 previously final case decisions preserved.
- Phase1 screened all 161 fronts/backs, corrected 5 fields on 3 cards (including `sich schwarzärgern` and `einfrieren`). Phase2 enriched 161 cards and made 387 field edits in sense-scoped lexical relations and 25 independent combination rewrites. The last **Phase3 resolved 8 further fields on 5 cards**, removing unsafe synonym classifications (Lerneffekt vs Lernerfolg; Lesetext vs Übungstext; Kunstform vs Kunstgattung), improving the lexical equivalent of `erträglich`, and replacing a bare repeat of `sich schwarzärgern` as a combination.
- **All 161 L09 cards have individually recorded `CORRECTED` case dispositions** in the same 1719-row Stage4 Ledger, supported by their cumulative changes and example context. 14 deliberate unsafe-mutation tests executed and rejected; empty synonym or antonym fields permitted where exact meaning equivalence cannot be defended. Still NONIMPORT, zero native-app and SRS mutations. This is a project editorial closure, not independent specialist certification.
- **Stage4 now 1568/1719 finalized, 151 pending (L10 only).** Next precisely **L10 Phase 1/3 for all 151** from v18; then the remaining bounded phases and a single final all-1719 content/technical regression. No new review gate or repeated browser test. Receipt `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L09-161-CLOSED-RECEIPT-20261121.json`.


## 2026-11-21 Stage4 L10 Phase1/3 — all 151 front/morphology screens, Library v19
- Authoritative **Library Master v19 SHA256 `814d13d99c8c700526f47026f638616317d786f60fe9cec055051331aff5d46a`** and **Ledger v19 SHA256 `41fee553d64f27980a5a9ca218f8f1c4a25a60b7da53cf43680def06b22721b5`** overwritten in place, re-downloaded and compared byte for byte with reviewed candidates. All 1,719 unique IDs, all 1,568 outside-L10 Master and Ledger rows, and all 1,568 prior Stage4 final decisions preserved exactly; no new final L10 decisions.
- Two real learner-facing corrections, both dictionary-supported: `der Zugang, die Zugänge (zu + D.)` and `der Schwarm, die Schwärme` restore the missing definite plural article in the front. The other 149 L10 fronts required no confirmed Phase1 correction; no fabricated changes to fill an edit quota.
- All 151 cards contain both German–Persian example pairs and three combinations. Literal copying of an entire combination from an example: zero exact-text candidates in Phase1 (contextual idiomatic review still required). Phase2 focus: 76 priority, 94 multisense, 121 relation-alignment and 9 legacy duplication tags; all 151 have prefilled family and related-word fields; meaning-scoped Synonyme/Antonyme both blank and must be added only where defensible.
- Eight deliberate destructive-mutation controls rejected. Scope is **front/morphology and structural presence only**, not blanket semantic acceptance. Stage4 stays **1568/1719 (151 pending)**. **Next L10 Phase2/3 for all 151**, then individual case conclusions in Phase3/3, then one all-1719 regression. NONIMPORT; no native-app/FSRS changes. Receipt `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L10-PHASE1-151-RECEIPT-20261121.json`.


## 2026-11-21 Stage4 L10 Phase2/3 — meaning-scoped relations, both owner files v20
- Single owner Library **Master v20 SHA256 `2e3dd1d9c2e800d08cf7919a42d2205ad6d4efa86b062c858f7fa4b8c282f81b`** and **Ledger v20 SHA256 `08e5db821dd84313245f6233cabf812740ffcb3ca2cc7246da7f16f96a552d56`** replaced in place and independently downloaded with exact bytes matching candidates. All 1719 unique IDs and all 1568 outside-L10 Master and Ledger rows preserved byte-exact, as are prior 1568 final decisions.
- **151/151 L10 cards processed, 164 genuine content field edits:** 114 sense-scoped Synonyme, 29 defensible Antonyme, 15 independent combinations (previously merely related-word combinations corrected), five related-word de-duplication edits, one Persian headword gloss correction. Do not force invented relationships: **37 cards keep Synonyme empty, 122 keep Antonyme empty**. Both bilingual example pairs retained and no full example copied as combination. Thirteen static invariants checked (not represented as independent linguistic specialist sign-off or separate destructive-injection tests).
- **L10 Phase3/3 next: 151 card-specific editorial decisions** with context-aware correction of weak equivalences, examples and morphology, then a single global 1719-card QA. Stage4 count remains **1568/1719**, **151 pending** until Phase3. NONIMPORT; no native app/FSRS change. Receipt `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L10-PHASE2-151-RECEIPT-20261121.json`.


## 2026-11-21 L10 Phase3/3 closure and one-time all-1719 global QA
- **Single authoritative Library Master v21 SHA256 `8cd45f15690a290c61775e186c069415654c8e83058b6dfe0eb5c12f4b42f97a` and Ledger v21 SHA256 `68b6c988ad9693f85f48b479b059d41345f20c19575b5097133693cc33243b6a`**, read back byte-exact after in-place overwrite. 1719 unique aligned IDs; all 1568 non-L10 Master and Ledger records kept byte-for-byte identical to v20, previous final decisions unchanged. L10 Phase3 produced **17 genuine content edits in 10 cards**, including narrowing misleading synonym/subtype relations and revising a `Waise` example to use the target headword. L10 case dispositions: **120 CORRECTED, 31 PASS**, based on actual cumulative v18→v21 content differences. Earlier Phase2 claim “151 cards changed” was inaccurate: it changed 164 fields on 119 distinct cards; the final cumulative corrected count is 120 due to one newly fixed card. QA negative tests: 11 passed. L10 required no fourth phase.
- **All 1719/1719 Stage4 editorial case decisions now recorded**: 1473 CORRECTED + 246 PASS. This marks the end of lesson-by-lesson editorial disposition, **not project-wide content QA approval** or native-app import. All export and linguistic release flags remain FALSE, `NONIMPORT`.
- **One global regression RUN, not passed:** found 261 cards below the later three-combination standard (152 L01, 108 L02, 1 L03); 75 stale Ledger front/back previews differing from canonical Master (L02–L05); one sense-scoped synonym repeating a word-family term (L09 unit `ab2-l09-u-2999`); and 202 literal example/combination overlap **candidates** (contextual review needed, not all confirmed errors). 539 findings across 468 distinct cards. The first source-lineage scan had 1386 false positives due to only testing two legacy source fields; checked alternative provenance fields and removed these false alarms.
- **Next existing-roadmap action is narrowly scoped global QA remediation** on these specific findings: match Ledger to Master for 75 cases, adjudicate the one duplicate, enrich short L01/L02 combinations with actual natural usages without inventing fillers, and manually review exact overlaps. Preserve all case decisions unless a real issue requires revised evidence. No separate QA bureaucracy, no new roadmap, no browser-SRS test, no import, no parallel Master. Case closure receipt: `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-L10-151-CLOSED-RECEIPT-20261121.json`; global QA receipt: `Workspaces/aspekte-b2-v336/Reports/B2-STAGE4-GLOBAL-QA-1719-20261121.json`.
