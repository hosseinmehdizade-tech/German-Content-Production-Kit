# Aspekte B1+ · L01 · Drei-Phasen-Plan

**Stand 2026-11-08 — Phase 1/3 DONE (Gesamtaudit), NONIMPORT.**

## Source of truth
The current learner-data owner remains the SHA-verified L05 Phase3 Library ZIP (`libfile_8e25215035b48191a9481393e7856510`), SHA256 `b5e470617bd72a34e6ab6236ba3232d247d2a1ee0a45f35126e5c7beed6e41f6`. It contains 1,571 provisional learner cards and 1,548 original-source mapping rows. **No learner data edited in Phase 1.** Never restart from the textbook or original raw CSV.

## Phase 1 / Ganzlektion-Audit — DONE
- **90 cards corresponding to 71 source rows (ordinals 1–71), no missing rows.** The exact source map confirms that ordinals **14/15** are merged as collocations into `der Kontakt`, ordinal **57** into `greifen`, and external ordinal **733** is cross-linked to the established L01 card `Darauf kommt's an`. Do not split valid G1 consolidations or count 733 as an additional L01 source row.
- **139 DE–FA example pairs, all explicitly pending independent semantic QA.** 24 cards have no examples. 6 forms already attestations with specific scope; 84 have no independent attestation. 42 cards carry curated HOLD markers. 3 cards currently have sense-based semantic networks with 4 existing blocks.
- 67 semicolon-based possible multiple-sense cases without networks are candidates only: semicolons are not proof of faulty content or mandatory multi-sense routing.
- Two complete-sentence Fronts, ordinals 60 and 61, require a decision whether to keep an intentional sentence card or route sentence to a lexical card. No silent deletion. 0 exact duplicate DE examples within L01, 0 empty DE–FA pairs, no redundant Back Formen.
- **Priorities: P1=49 / P2=41 / P3=0**, purely editorial sorting, not approval or proof of faults. Per-card decision queue (90 JSONL records) available as attached local artifact. Audit and its sha-verified input owner are described in `Lessons/L01/PHASE1-90-CARD-AUDIT.json`.

## Phase 2 / Gesamtkorrektur — NEXT
Review **all 90 cards** in ONE lesson correction milestone, first P1 then P2; give all 139 bilingual example pairs an editorial language decision. Only fix demonstrated lexical/grammar errors, preserve main/secondary meanings in one card, add sense-specific examples when pedagogically necessary, validate case/prepositions. Evaluate 24 zero-example cards, 42 HOLD markers, 67 ambiguous-sense candidates, and two sentence Fronts. Keep the 14/15/57 consolidations and 733 cross-lesson link. Write one before/after ledger for substantive changes; no 10-word Reviews.

## Phase 3 / QA und Freigabe — AFTER Phase2
Run independent **full-card DE–FA / morphological** checks on the whole lesson; enforce global source-map, example, noncopy, sense and no-back-Formen gates. Check *actual* app importer and rendered cards, not just an offline HTML/TSV projection. Publish only independently approved units, otherwise mark explicit RELEASE_BLOCKED. Current project 0 full-card approvals, 340 historical global release HOLDs, no proven app import.

**Control policy:** whole lesson, at most three milestone stages; each stage must represent real work, and no fake release approval.
