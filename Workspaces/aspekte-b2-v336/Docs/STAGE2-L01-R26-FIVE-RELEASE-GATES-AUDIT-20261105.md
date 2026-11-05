# Aspekte B2 — Kapitel 1: release-gate audit (R26, 2026-11-05)

Scope: B2 only, lesson 1, source ordinals 1549–1708 (160 rows). User CSV is the sole vocabulary inventory. This is an evidence consolidation, **not** a card release or independent human linguistic approval.

## Five unresolved cross-level gates

| B2 source ordinal | German headword | Earlier-level evidence | Decision |
| --- | --- | --- | --- |
| 1556 | abenteuerlich | No exact standalone B1 master entry documented | HOLD: search A1/A2/supplementary and actual accepted cards; do not suppress |
| 1575 | ständig | Menschen B1-L05 candidate `mb1m-lu-1040`, exact front | HOLD: candidate is not proof of imported/live accepted card; verify sense |
| 1609 | entscheidend | B1-L12 `mb1m-lu-1880` is phrase `im Voraus entscheidend`, not standalone adjective | HOLD: do not equate phrase with standalone B2 learner unit |
| 1630 | intolerant | Menschen B1-L19 candidate `mb1m-lu-2779`, exact front | HOLD: candidate is not proof of imported/live accepted card; verify sense |
| 1671 | zerreißen | B1+ raw-source overlap, no accepted B1+ learner-card proof | HOLD: compare transitive `hat zerrissen`, intransitive `ist zerrissen`, adjectival participle separately |

## Findings and invariants

- Existing R6 reviewed all 160 L01 source rows. R6 reclassified four unsafe suppression proposals to guarded HOLD and proposed a corrected linguistic analysis for #1671; no actual suppression was executed.
- Prior R7 canonical evidence includes two exact B1 candidate IDs but does not demonstrate published/learner-visible imported cards.
- B1+ L01 current formal-gate inventory is non-importable, with formal Stage4 accepted false. A raw B1+ match cannot justify eliminating B2 #1671.
- L01 Gate2 is **NOT_APPROVED**. Stage3–7 remain **NOT_STARTED**, final/importable cards **0**. This audit introduces no new lexical entry and changes no source, earlier-level project, application, or user SRS data.

## Required next evidence

1. Actual earlier accepted/imported learner-card status and sense for #1575 and #1630, and search independent A1/A2/supplementary accepted cards for #1556/#1609.
2. B1+ final learner-unit status and whether its documented `zerreißen` sense is identical to B2 #1671.
3. Independent bilingual semantic review of all 48 L01 FIX proposals and contextual examples, before formal Stage2 release.

References: B2 Library `STAGE2-L01-R6-GUARDRAIL-SUMMARY.json`; `STAGE2-L01-5-B1-CANONICAL-ID-EVIDENCE-20261105.jsonl`; existing GitHub `Docs/STAGE2-R7-B1-CANONICAL-EVIDENCE-AND-L02-TRIAGE-20261105.md`. All evidence is historical/current-documentary, **not fresh app runtime verification**.
