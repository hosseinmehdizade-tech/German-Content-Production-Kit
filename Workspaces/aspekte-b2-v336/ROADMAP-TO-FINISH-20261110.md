# Aspekte B2 — feste Abschluss-Roadmap / نقشهٔ نهایی پروژه

**Checkpoint:** 2026-11-10 · owner-curated current is authoritative · no original textbook reconciliation.

**Einzige Inhaltsquelle / تنها مرجع داده:** `Current/ASPEKTE-B2-FINAL-MASTER-1719-CURATED-NONIMPORT.tsv` (1719 rows, 66 columns, SHA-256 `1b77fe453aff2084c6fd91baa0f0dd47cbdd3c4c8f5eced5f0842b84bd2312cc`). The 10 lesson-level Current CSVs are preserved as validated recovery snapshots, not parallel work branches. At the end of each accepted content edit, update *this* Master, preserve a backup, verify row/ID/cell differences and update GitHub checkpoint.

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

**Progress now:** all 1719 cards machine-screened; **0 of 1719 receive a newly claimed semantic signoff** until actual review. The screening is a risk sorter, not a semantic judgement. Stage4 first active batch: **L01, all 158 cards, pass 1/≤3**.

| Lektion | Karten | Stage 4 semantic decisions |
|:--|--:|--:|
| L01 | 158 | 0 / 158 |
| L02 | 110 | 0 / 110 |
| L03 | 186 | 0 / 186 |
| L04 | 183 | 0 / 183 |
| L05 | 227 | 0 / 227 |
| L06 | 141 | 0 / 141 |
| L07 | 222 | 0 / 222 |
| L08 | 180 | 0 / 180 |
| L09 | 161 | 0 / 161 |
| L10 | 151 | 0 / 151 |
| **TOTAL** | **1719** | **0 / 1719** |

## Stage 5 — final regression & risk disposition (NOT STARTED)
One **single all-1719** regression: Master schema/IDs/counts, absence of unintended diffs, 3438 bilingual examples, 4891 collocations (or documented content revisions), semantic decision coverage 1719/1719. Every remaining `DOCUMENTED_EXCEPTION` has an explicit decision (hold/exclude/resolve). Produce one release-candidate QA receipt and reproducible hash. No new rounds merely for confirming original publisher fidelity.

## Stage 6 — isolated technical import/SRS readiness (NOT STARTED; no automatic import)
Run **one documented native-app import dry-run** and ID/SRS continuity/rollback test using exact target app and existing accepted-card IDs, when supported. Until tests pass, file remains `NONIMPORT` and **zero cards are marked release approved**. If environment cannot access the native app/IDs, record the concrete blocker once; stop and hand off the runnable artifact to Codex / app environment instead of looping. Live SRS import is not performed without an explicit request.

**Terminal rule:** no new HF/Phase/Scenario may be opened without a verified new defect and a measurable impact on the above acceptance criteria. After each message report `master SHA / lesson / reviewed / edited / remaining / blocker / next exact batch`. Don't claim success for tests that were not actually executed.