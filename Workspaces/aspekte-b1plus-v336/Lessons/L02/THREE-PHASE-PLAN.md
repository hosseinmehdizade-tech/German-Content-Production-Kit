# Aspekte B1+ / Lektion 02 — Drei-Phasen-Plan

**Stand:** 2026-11-08 — Phase 1/3 DONE; Phase 2 NEXT; NONIMPORT.

**Source of truth:** SHA-verified curated Library L01-Phase3 ZIP, SHA256 `dccda4967101f6c0ec4b3df49f3f9e050fd56c4bf20b14be3805899c3e9d8522`. Existing learner data are read-only in Phase1. No textbook re-import.

## Phase 1 — Whole-Lesson Inventory: DONE

- **91 L02 cards across 91 original source rows (ordinals 72–162)**, all mapped; no dropped or duplicate learner IDs. Overall project stays 1571 card views / 1548 source rows.
- **197 DE–FA example pairs**, 0 cards without examples, 12 examples lacking an explicit QA status, 0 independent recorded morphology attestations (thus 91 require evidence/rule-scoped review).
- **18 existing curated HOLD card markers**; 3 cards already containing sense networks (3 sense blocks); 40 risk candidates for meaning/routing review — not automatically content errors.
- **1 exact duplicate DE example group** at ordinal 128 / `der Kastellan`: same sentence appears twice; preserve unique DE/FA examples in Phase2 and handle historical duplicate-release gate.
- **6 examples on already-networked cards lack correct explicit sense linkage**; do not assume other 88 cards all require an elaborate network.
- Priority groups are **P1 36; P2 21; P3 34**. Every one of 91 cards has a written Phase2 action in `L02-PHASE1-91-CARD-DECISION-QUEUE.jsonl`; priority is not approval.
- QA statuses: {"PENDING_INDEPENDENT_DE_FA_SEMANTIC_QA": 183, "PENDING_G4_INDEPENDENT_DE_FA_QA": 2, "NOT_MARKED": 12}. No invalid empty German/Persian example pair found. No changes to learner data in this phase.

## Phase 2 — Complete 91-card editorial correction: NEXT

Handle **all 91** cards and **all 197 examples** in one L02 whole-lesson stage. Prioritize HOLD, sense-ambiguity, valency and duplicate issues. Correct genuine errors only and keep multiple meanings on one existing card. Record explicit before/after evidence and 91 decisions. Do not create a micro-Review for every 10 cards.

## Phase 3 — Independent full-card QA and runtime import gate: LATER

Independent complete German/Persian release QA + morphologic and sense-routing gates + case-by-case HOLD decisions. Real German-Flashcards-Pro application TSV import and rendered Front/Back must be demonstrated rather than simulated. Failure → `RELEASE_BLOCKED`, never pretend the lesson is approved.

**Global unchanged:** 338/1571 prior G2 form attestations, 340 legacy release HOLD markers, seven exact duplicate groups across corpus (one L02); zero formal full-card release approvals. This L02 Phase1 creates **no new attestations or released cards**.