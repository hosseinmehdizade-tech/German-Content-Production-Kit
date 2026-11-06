# Aspekte B2 L01 — R40 evidence from current final TSVs (2026-11-06)

**Status: editorial cross-level decision update; NONIMPORT. No B2 source edits, card imports, merges, deletions, or user SRS changes.**

## Why R39 evidence needed revision
The former five/seven cross-level gates relied on old candidate sources. We examined the **current final content archive** for Menschen B1 (3088 cards), the current Menschen A2 **content-only** archive (1778 cards), and the newest inspected Aspekte B1+ Stage4 **NONIMPORT** archive (1548 source entries), instead of returning to textbooks or historic first-draft lists.

The B1 final package includes a user-reported successful import dated 2026-11-06. Crucially, the embedded `USER-ACCEPTANCE-AND-LIMITATIONS.json` does **not** claim independent native IndexedDB/SRS Stage6 validation. Thus its IDs are accepted final **content** with a user-reported import, but an individually verified live app record was **not** observed in this review. The A2 package explicitly says `one_import_candidate_only=true`; it cannot be treated as a known live app collection.

## Seven specific decisions

| B2 source | Existing current evidence | R40 non-executed decision |
| --- | --- | --- |
| 1556 **abenteuerlich** | No exact B1-final or A2-current match | Keep B2 adjective. A1 final TSV not located, so absence across *all* prior levels is not proven |
| 1575 **ständig** | B1 final `mb1m-lu-1040`, **adverb**; B2 example `Die ständigen Unterbrechungen` is an **attributive adjective** | Link B1 adverb; retain B2 adjective sense as a distinct candidate, subject to semantic QA |
| 1609 **entscheidend** | B1 final `mb1m-lu-1880` = phrase `im Voraus entscheidend`, not standalone adjective | Keep standalone B2 adjective |
| 1616 **die Art** | A2 current content `ma2m-lu-0281`, exact noun `die Art, Arten` | Prefer linking A2 noun once actual import verified; preserve the B2 source phrase `Fragen jeglicher Art` as a collocation candidate |
| 1630 **intolerant** | B1 final `mb1m-lu-2779`, exact adjective with same meaning and examples | Strongest redundant B2-card candidate: reuse existing B1 unit if real app identity confirmed; **retain B2 source lineage**, no suppression executed |
| 1671 **zerreißen** | B1+ `AB1P-SRC-0075` is `SOURCE_ONLY_NONIMPORT`, not an accepted card | Keep B2 verb; confirm `hat zerrissen` transitive and `ist zerrissen` intransitive separately |
| 1697 **die Kinokasse** | No standalone current B1/A2 match or B1+ source match | Keep B2 noun; no unsupported duplicate assertion. A1 final TSV was not verified |

**Interpretation:** All 7 *cross-level editorial actions* are now specified. Some remain dependent on actual prior-card import proof. **This does not mean 7 semantic release gates have passed**. There are still 10 other original R39 HOLDs and unfinished full independent B2 bilingual QA.

## Reproducible current-file evidence
- B2 sole lexical source, sanitized 1726 rows, SHA256 `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`.
- B2 L01 R37 working CSV, 160 rows, SHA256 `12aabe461eb751aea8bb6ef35a5f2f302e31db05601371ea13860c37380c4b0e`.
- Menschen B1 current final TSV, 3088 cards, SHA256 `bcf0410a88037848bca273672dda2435aa4713efa02c1ffbe367eada5c1848d6`. Parent content-final ZIP SHA256 `60ca66adc19581c8a5803c6eb359a320b7c222483932a262d46377a2d8bb0ee4`. User-reported successful import; independent native persistence unverified.
- Menschen A2 current content TSV, 1778 cards, SHA256 `b9f4ce62e5c91cb3d5f225b203e180c4007880a076b67c9f51d0800881055d76`. Parent content-only ZIP SHA256 `b8cffeeb25553eb254f410583ecda85041c2547a69ed9e99d8ef683e19590548`. Not verified imported.
- Aspekte B1+ latest inspected 1548-entry source-ledger package SHA256 `c26c093d3d58bdc0c370cc8a2b538bce6cc8b450b72c0f533c34181885c55202`; NONIMPORT.
- A1 authoritative final learner-card TSV was **not located** among inspected current/release folders. No A1 final coverage claims made.

## Outputs and remaining gates
Seven-row decision ledger: `Reports/L01-R40-7-CROSSLEVEL-CURRENT-FINAL-TSV-DECISIONS.csv` (in this GitHub B2 workspace). This R40 document is a compact snapshot: **no new 160-row R40 working copy or ZIP**, avoiding archive proliferation.

Stage 2 NOT APPROVED. Independent DE/FA semantic QA not complete. Stage3–7 NOT STARTED. Final/importable B2 cards 0. Global portable project checkpoint remains L05 R25. R38 remains authoritative for 48 prior FIX decisions; R39 remains authoritative for 17 HOLD identification.