# Aspekte neu C1 — Stage2 Kapitel 1: exactly 61 source usages routed, three real new idiom drafts

Date: 2026-11-23. **Actual work, not a whole-project lexical re-audit.** The `HOLD_C1_DISTINCT_SENSE_OR_PHRASE` category in the immutable 397-entry Kapitel1 source queue contained exactly 61 named source IDs. Each now has an individually recorded, evidence-bounded `stage2_61_routing_decision`, its printed `source_raw`, older lower-level witness and a specific rationale. These are production routing dispositions, **not** certification that lower-level B1+/B2 master cards were actually modified or learner-facing enrichment shipped.

## Exact input and preservation

Read the existing **owner Library** `Aspekte-C1-STAGE2-K01-246-RICH-CARD-DRAFTS-20261123.zip`, SHA256 `0f8a1fece86ad4f2e834e64e48ddfa077649558d0210f4557738728c3ab3fe2b`. Actual members read:
- latest `C1-STAGE2-K01-397-SOURCE-QUEUE-246-DRAFTS-20261123.json`: 397 rows, of which 61 `HOLD_C1_DISTINCT_SENSE_OR_PHRASE`;
- latest `C1-STAGE2-K01-246-RICH-CARD-DRAFTS-20261123.json`: exact 246 original typed cards;
- `C1-STAGE1-WORKING-3270-9-ERRATA-435-ROUTED.jsonl`: original evidence, prior lower-headword witnesses, source context;
- `C1-STAGE1-435-LATEST-B1PLUS-L05-B2-V33-LEXICAL-DECISIONS.jsonl`: frozen 435 lexical routes.

The 3,270 original C1 working source lines, all 435 lexical routes, prior source corrections, all **246 original canonical card objects**, and **all 64 previous ZIP member payloads** are preserved byte-for-byte. Only the exact 61 targeted production-status fields, explicit scoped routing metadata, and three genuinely new independent idiom card objects were added. No original printed lexeme or triage identity was rewritten.

## Every one of the 61 decisions — exact distribution

| Production routing | Source IDs | Outcome |
|---|---:|---|
| ENRICH_LOWER_LEMMA_WITH_SOURCE_USAGE_CANDIDATE | 29 | Forward a source-attested phrase/collocation for possible enrichment of its already existing lower-level headword; not applied to lower master |
| ENRICH_LOWER_LEMMA_DISTINCT_SENSE_OR_REKTION | 12 | Source-specific sense, separability, register or Rektion needs to remain visible under existing lower-level lexical identity; not a duplicate independent headword |
| KEEP_SOURCE_USAGE_EXAMPLE_NO_DUPLICATE_C1_CARD | 7 | Printed source sentence or contextual example is not automatically a fixed idiom or Kombination |
| MERGE_LOWER_LEMMA_PREVIOUS_WITNESS_CONFIRMED | 4 | Explicit earlier lower-level witness/expression or already closed targeted HOLD |
| RESOLVE_ARTICLE_HOMOGRAPH_AND_ROUTE_TO_LOWER_NEUTER | 1 | `C1-P04-E068` source `der Gefallen` conflicts with phrase `bei jemandem Gefallen finden` that belongs to `das Gefallen`; source raw preserved; existing lower neuter witness is a different lexeme from masculine favor |
| LINK_TO_ALREADY_AUTHORED_C1_CARD | 3 | Genuine expression already in source-authored C1 cards; do not create duplicate |
| CREATE_DISTINCT_C1_IDIOM_DRAFT | 3 | Exactly three newly authored full rich-card drafts, with lexicographic idiom evidence |
| SOURCE_ALIAS_TO_ONE_IDIOM_CARD | 2 | Another source occurrence points to the same newly authored idiom card, not another SRS item |
| **Total** | **61** | **61/61 individually accounted for** |

Three **already authored C1 expression targets**: `C1-P02-E023 → C1-P02-E017 der Schatten` ("über seinen Schatten springen"), `C1-P02-E079 → C1-P02-E052 der Alarm` ("Alarm schlagen"), `C1-P03-E041 → C1-P03-E042 die Vereinbarung` ("eine Vereinbarung treffen"). Verified by reading actual earlier card meanings/examples/details, not guessing from titles.

Three **new distinct idiom draft cards**:
1. `C1-P03-E065` **jemandem auf die Nerven gehen** ([Duden Nerv](https://www.duden.de/rechtschreibung/Nerv)), collloquial, Dativ of affected person. `C1-P03-E077` aliases it;
2. `C1-P04-E071` **in Serie gehen** ([Duden Serie](https://www.duden.de/rechtschreibung/Serie)), product enters serial manufacturing; `C1-P05-E013` aliases it;
3. `C1-P05-E038` **etwas an den Nagel hängen** ([Duden Nagel](https://www.duden.de/rechtschreibung/Nagel)), colloquial, give up an activity/profession.

Each new card has exactly **four distinct DE/FA/EN example triplets**, a typed DE/FA/EN meaning, a sourced idiom grammar/rection/register record, explicit review of all **five** right-side sections, independently sourced useful connections where available, and reasons where a false synonym/antonym/Kombination should not be inserted. They are **Stage2 drafts**, not approved or published.

### Actual detected source errata and quality boundaries

- `C1-P04-E068`: source prints `der Gefallen, - (Gefallen finden bei jmd.)`. Duden documents the printed idiom under **das Gefallen**, meaning approval/liking; **der Gefallen** means a favor and is a distinct lexeme. Therefore do not mix the two senses or invent a new independent C1 gendered noun. Preserve printed source; record the pedagogical correction ([Duden das Gefallen](https://www.duden.de/rechtschreibung/Gefallen_Wohlgefallen)).
- `C1-P04-E055`: printed `abbrechen, bricht ab, bracht ab` has **bracht** instead of **brach**; keep printed source unchanged and attach correction to a future learner-facing lower-base enrichment, no duplicate C1 headword.
- `C1-P04-E042`: `Es zieht.` concerns draught (impersonal), not the elementary transitive pulling sense; keep the sense distinction.
- `C1-P04-E017`: `sich finanziell rechnen` is a reflexive 'worthwhile financially' use, not merely an arithmetic verb. `C1-P04-E035` `von Job zu Job ziehen` contrasts in auxiliary and sense with `ziehen` transitive.
- **No B1+/B2 lexical-card changes have been written.** All 61 routing suggestions and source corrections are documented for later scope-limited actual production. A routing label is not a claim of learner-visible enrichment.

## Exact official validator and artifact integrity

Ran actual project validator `Workspaces/aspekte-c1-v336/04-qa/validate_c1_rich_card.py`, Git blob SHA `4c0f613665bf0c0db5df9e353d218ef86490d67d`, on the exact cumulative **249-card JSON**:
- `STRUCTURAL_PASS_NOT_STAGE4_5_6_7`
- **249 cards checked, 0 errors, approved_cards = 0**;
- exactly **996** original learner example triplets, 4 per card, each newly authored idiom card has DE/FA/EN meanings and examples; all 246 previous cards unchanged.
- Cumulative canonical card JSON SHA256 `5e0faab09e64c09c9a959488c4a82701f54dc4b7b3ab8e46479558efb8b787ab`.
- 61-row routing report and exact validator receipt are persisted within the new ZIP.
- **No full native linguistic Stage4, Stage5 app serialization/import, Stage6 app test, release, or merger claimed.**

Latest complete owner Library ZIP:
- Path: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-C1/Checkpoints/Aspekte-C1-STAGE2-K01-61-PHRASES-ROUTED-249-CARD-DRAFTS-20261123.zip`
- Library ID: `libfile_953e137b118c8191b8f55859985a3459`
- ZIP SHA256: `91d6f5a8a85661037b1ec5af7e653e76b5962701e2869f1aa940ab5beb247261`
- Size: 1,724,012 bytes; **69 ZIP members**, CRC/testzip PASS, **64 parent member payloads identical**.
- Latest actual card JSON: `C1-STAGE2-K01-249-RICH-CARD-DRAFTS-20261123.json`.
- Latest exact 397-row queue: `C1-STAGE2-K01-397-SOURCE-QUEUE-249-DRAFTS-20261123.json`.
- Complete per-item 61 decisions: `C1-STAGE2-K01-61-DISTINCT-USE-DISPOSITIONS-20261123.json`.

## Finite next action — no new review loop

Of the 397 Kapitel1 source occurrences, **247 provisional new-lemma sources are previously routed (246 cards + one gerade alias)**, now **61 additional distinct-sense/phrase source IDs are routed**, leaving **89 other source occurrences**: **77 already classified as lower-headword excludes (67 lower lemma + 10 same usage)** and exactly **12 true exception source IDs** (7 HOLD_ALIAS_LOWER, 2 POTENTIAL_FALSE_POS_MATCH, 2 SENSE_DIFFERENCE_HOLD, 1 MORPHOLOGY_ERROR_HOLD). Next: resolve those exact 12 exceptions once; do not turn 77 lower excludes into 77 new cards. Then one finite, substantive Stage4 linguistic, trilingual translation and five-right-field QA gate against actual 249 card bytes. Stage4 approved remains 0.
