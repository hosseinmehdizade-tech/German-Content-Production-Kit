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
