# Aspekte B1+ · Lektion 06 · verbindlicher Drei-Phasen-Plan

**Stand 2026-11-09 · Phase 1 of 3 DONE (whole lesson structural inventory); Phase 2 NEXT; NONIMPORT.**

## Authority / No regressions
The **latest SHA-verified user-curated** B1+ Library owner (L04 Phase3 ZIP SHA256 `31d8d0640d5bacdb080f0a379aa926542498a905c82b4e3d2f3d670d7bb2aca4`) remains the sole learner-card authority. The owner is *unchanged* by Phase1. Do not return to textbook CSV. Full corpus of 1571 existing candidate cards and all 1548 source-row mappings remains valid; do not count old source files as new card data.

## Phase 1 whole-lesson findings
- **177 current L06 cards** across original source ordinals **672–846** (175 rows): every source row mapped. Legitimate dual-lexeme splits at **679**, **714**, **771**, **773** (2 cards each). Original row **762** merged into existing L06 ordinal 761 `einhalten`; source ordinal **733** crosslinked to existing L01 ordinal 18 `Darauf kommt's an`. Do not create replacement cards or delete valid split cards.
- **370 current DE–FA examples** = 345 existing + 25 supplemental, with 0 empty DE/FA pairs. **Four cards have no examples** (the separate lexical items `denkbar`, `undenkbar`, `erwünscht` and `unerwünscht`). **16 examples** missing explicit QA status on 14 cards; missing does not equal approved.
- **108 scoped form evidence flags / 69 not attested**; **33 inherited curated HOLD cards**. **18 cards with 26 existing meaning-network blocks**, but only **1/37** examples on those cards has a matching sense ID; **36 unrouted** (not necessarily 36 grammar errors). 2 exact within-card DE example duplicate groups in `die Besprechung` (ordinal 760) and `hin und her` (ordinal 820). **Five corpus-wide old duplicate groups remain**; two are in L06.
- Each of 177 cards has a case-specific Phase2 decision in the JSONL: **P1=51** (direct structural blockers / inherited HOLD / invalid or missing sense routes), **P2=46** (form evidence, examples and meaning heuristics), **P3=80** (remaining cards, still requiring full QA). These priorities are **not semantic or release approval**.

## Phase 2: whole 177-card editorial correction (NEXT)
- Work **all 177 in one lesson-level unit**, using P1 then P2 then P3 risk order; not 10-word Review loops. First adjudicate the 2 exact duplicate groups preserving all useful distinct translation variants, and add missing DE/FA example(s) to 4 zero-example cards.
- Review 36 unrouted network examples by their specific sense; do NOT force ambiguous context to a sense. Fill 16 example QA statuses with honest PENDING/verified evidence rather than automatic PASS. Recheck all 33 inherited HOLDs individually and 69 unverified forms where relevant.
- For ALL cards, review German + Persian meaning hierarchy, front morphology, example naturalness, sense-linked Synonyme/Antonyme/Wortfamilie/Kombinationen. Keep polysemy inside a single lemma card and preserve cross-lesson mapping.
- **Mandatory persistence regression:** when producing a corrected ZIP, verify the changed **primary 1571-card JSONL member** really contains the claimed card diffs; sidecars alone never count. Compare all non-L06 objects and the exact 1548-row map with parent, verify CRC/member SHA hashes and Library byte readback.

## Phase 3: full quality & import gate (LATER)
- Evaluate every case with explicit German–Persian content decisions and deterministic QA, record reasoned HOLDs (no fictitious external human examiner required).
- Test actual German-Flashcards-Pro TSV importer and real rendered front/back if available; offline TSV/HTML projection is NOT an app import.
- Finish with RELEASED for fully approved/tested cases, or an explicit RELEASE_BLOCKED/NONIMPORT lesson outcome with a concrete blocker ledger; never invent release approvals.
