# Aspekte B1+ · L06 — Drei-Phasen-Abschluss

**2026-11-09 · Phase 1 DONE · Phase 2 DONE · Phase 3 strict QA evaluated → RELEASE_BLOCKED_NONIMPORT**

Canonical, verified curated Library owner `libfile_714e7e818a4881919c2639503c928bc8`, SHA `cc964921ac68e2dabac96e7074a72101c4cf47beda7f14b876ff248aff029990`. 177 cards, 378 bilingual examples, 5 actual card changes in saved primary data (ordinal 737, 742, 750, 751, 846); 1571 corpus IDs and 1548 mapped source rows preserved. Three finite-clause `Kombinationen` corrected in L06; `formal` vs `formell` fixed; `per` Duden-scoped Akk./Dat. attestation gained. 109 scoped forms attested, 68 without such evidence, 33 curated HOLDs retained. 177 of 177 release-gate decisions **BLOCKED**, no real app import. Global finite-clause v4 **FAIL 3 candidates in L02/L03/L09**; old strict 722-combination structural gate alone is insufficient. 177-card QA HTML + 378 examples and offline 177 TSV records passed but are not the application runtime.

**Next: L07 Phase1 whole-lesson audit.** L06 stays in a separate release-blocked backlog. Do not restart per-10-word reviews. Do not invent 177 full bilingual linguistic signoffs or independent external reviewer.

Authoritative receipt: `Lessons/L06/PHASE3-FINAL-VERIFIED-OWNER-RECEIPT-20261109.json`. Strict finite gate `Tools/qa_combinationen_finite_clause_v4.py`; main saved-card integrity is mandatory. Wider cross-project wiring is NOT yet verified.

---
## Historical Phase1–2 plans
# Aspekte B1+ · Lektion 06 — Drei-Phasen-Plan (LIVE)

**2026-11-09 · Phase 1 DONE · Phase 2 DONE (editorial, 45 targeted data/status cards) · Phase 3 NEXT · NONIMPORT**

## Latest verified owner
- B1+ Library `libfile_3832285495208191a078ee53fc37feb7` / SHA256 `bba74617aae6abfb849c28a03b2f279ed75171075c9717c2e6f3ad4c2d9f7d8f` / 3,605,537 bytes.
- Original curated source has **1571 learner IDs / 1548 mapped source rows**. L06 **177 learner cards from 175 source rows**; all original IDs and source links preserved; all 1394 non-L06 card objects unchanged.
- **177/177 Phase2 disposition decisions** written to active card objects plus independent decision JSONL. **45 targeted content / QA status card changes** (not 177 language fixes). 89 new example-to-sense links and 19 new meaning networks containing 42 sense blocks; no separation of meanings into new cards. L06 example count **378** after 10 new examples and 2 duplicate-removals. 14 previously statusless examples marked **PENDING**, with two previous statusless exact duplicates removed.
- Primary 1571-card JSONL actually changed and was byte-reopened and compared: SHA256 `8271f00d2ae686c835e1b489cf1385b82705a7290fd26781f7f7017932a0bed1` → `3766d3bbd7e85809f79719db758857e2deac2a5363982b863d878086a44cd059`. Mandatory regression guard PASS; Library exact readback and ZIP CRC PASS.
- 722 global structured bilingual combinations, zero exact copy / finite-clause / required-field failures in deterministic QA. This does NOT certify every collocation's linguistic naturalness.
- Existing 33 L06 curated HOLD markers and 69 unverified scoped morphology forms intentionally preserved. Corpus exact same-card example duplicate groups 5→3, remaining three still block release. **Zero fully approved learner cards, no real app import tested.**

## Phase 3 — final release gate, NOT a new micro-review loop
1. Examine unresolved L06 case-level German/Persian grammar, senses, idiomatic combination accuracy, and all examples, explicitly addressing original 33 HOLD cases, 69 morphology evidence gaps and any lexeme-specific hazards. Do not treat absent external dictionary evidence as proof of a wrong form, and do not invent a required second external human reviewer.
2. Validate all 177 existing L06 card identities and the 175 original source rows; compare exact canonical primary saved JSONL, unchanged other lessons, 1548 ordinal links, 378 bilingual examples, 37 meaning-network cards and 722 global combinations.
3. Run fail-closed duplicate and semantic link gates; perform an actual `German-Flashcards-Pro` TSV import/front/back renderer test when accessible, not just an offline HTML screenshot/TSV parser simulation.
4. For unresolved QA or unavailable real runtime app test, conclude Phase 3 with explicit **RELEASE_BLOCKED_NONIMPORT** and preserve blockers as an actionable ledger. Do not restart 10-word `ReviewXX` loops. Next general lesson after this is L07 Phase1 if the normal sequence remains unchanged.

Evidence: `Lessons/L06/PHASE2-PERSISTENCE-RECEIPT-20261109.json`; `Lessons/L06/PHASE2-WHOLE-177-CARD-REPORT-20261109.json`; `Lessons/L06/PHASE2-177-CARD-DISPOSITIONS.jsonl`; `Lessons/L06/PHASE2-CONTENT-BEFORE-AFTER.json`; `Tools/build_L06_phase2_v1.py`.

---
## Historical Phase1 plan
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
