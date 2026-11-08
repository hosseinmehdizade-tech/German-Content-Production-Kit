# Aspekte B2 — Central release readiness, 8 November 2026

**ALL TEN LESSON CYCLES CLOSED WITH BLOCKERS · BLOCKED_NONIMPORT**

The owner-curated CSVs for all ten lessons were read directly; no original textbook reingestion or automatic card modifications occurred.

| Metric | Machine-audited value |
|:--|--:|
| Source ordinals accounted for (including sidecars) | 1726/1726 |
| Distinct draft learner-card IDs | 1719 |
| Complete primary German–Persian example pairs | 3438 |
| Additional L05 pilot pairs | 12 |
| Proposed collocation chunks | 4575 |
| Collocation chunks found verbatim inside same-card examples | 295 |
| Cards with at least one verbatim overlap | 270 |
| Internal duplicate collocation chunks | 1 |
| L01 cards lacking any collocation column | 158 |
| Source noncard/alias exceptions recorded | 11 |
| Live-approved/importable cards | 0 |

## The key newly exposed quality problem

The previous lesson-specific QA checks did not uniformly enforce the rule that `Kombinationen` should not reuse examples. The central checker now reports literal occurrences using the **same check across all files**, including short excerpts. This reports candidates requiring review—not evidence of copying intent or automatically wrong German.

| Lesson | Draft cards | Literal overlap flags | Cards affected | Collocation chunks |
|:--|--:|--:|--:|--:|
| 01 | 158 | 0 | 0 | 0 |
| 02 | 110 | 33 | 31 | 222 |
| 03 | 186 | 60 | 52 | 558 |
| 04 | 183 | 47 | 42 | 549 |
| 05 | 227 | 57 | 50 | 681 |
| 06 | 141 | 21 | 21 | 423 |
| 07 | 222 | 21 | 21 | 666 |
| 08 | 180 | 31 | 29 | 540 |
| 09 | 161 | 25 | 24 | 483 |
| 10 | 151 | 0 | 0 | 453 |

## Three independent release gates

1. Independent, sense-aware DE–FA linguistic sign-off covering forms, meanings, two examples and lexical relationships.
2. Verified current, live **accepted card IDs**, cross-level meaning identities and non-destructive SRS mapping.
3. Safe native app import, restart/roundtrip, SRS preservation and rollback test on a working copy.

**Until all gates pass, these drafts are not to be imported or have release flags changed.**

## Source exceptions and limitations

L01 source #1630 is a conditional B1 reuse, and #1660 is a grammatical facet (Partizip II of kommen); neither is a deleted source entry. L03 source #1921 is an alias of #1920. Four L05 source expressions and additional L06/L07/L09/L10 full-sentence objects are preserved in noncard sidecars.
L01 has a different/older draft schema without a `collocations_de` field; its 158 cards need their own explicit collocation-enrichment decision, not a false claim that this field passed.


**The machine gate detects literal reuse, but does not replace independent semantic review or independently validate live app state.**
