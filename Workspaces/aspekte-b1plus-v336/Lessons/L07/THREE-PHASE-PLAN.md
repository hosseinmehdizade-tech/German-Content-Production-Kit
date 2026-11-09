# Aspekte B1+ · L07 „Für immer und ewig“ — Drei-Phasen-Abschluss

**2026-11-09 · Phase 1 DONE · Phase 2 DONE · Phase 3 strict QA EVALUATED → RELEASE_BLOCKED_NONIMPORT**

**Canonical curated owner:** Library `libfile_4e8d3ac0eac481919bc8627f21f0f2bd`; SHA256 `14841de70a121551121c6c1bced5cca987a659e006d0b225d980f302939dac81`; 269 ZIP members / 268 SHA256 member hashes plus CRC and exact Library readback PASS. 154 L07 learner card IDs retained, 153 mapped original source rows, 1571 corpus card IDs / 1548 map rows unchanged, and all 1417 other-lesson card objects unchanged.

**Actual Phase3 content result:** 10 modified saved L07 card objects (ordinal 852,855,860,861,889,891,904,948,987,999). Each has **case-scoped Duden grammar attestation** only, not full DE/FA learner-card approval. Fixed inverted example→meaning link on `schmieden`, separated `schweben` and `pendeln` auxiliary usages, added 3 still-pending DE/FA examples. 348→351 total L07 example pairs; 41 semantic network cards with no structurally unrouted examples. Exactly 10 scoped G2 forms attested, 144 L07 cards without case-specific G2 evidence; 38 legacy curated HOLDs preserved.

**Release gate:** real `qa_lesson_release_gate_v1.py` run against persisted ZIP as a separate validation from the editing script and returned `release_allowed=false`, all 154 records BLOCKED; blockers include 154 full-card approvals absent, 154 example/translation independent signoffs absent, 154 real app imports not tested, 144 individual form attestations missing, and 38 curated HOLDs. Complete QA-only HTML 154 cards/351 examples and offline 154-row TSV roundtrip PASS, **NOT actual German Flashcards Pro app runtime import**. Finite-clause v4 global FAIL 3 legacy examples wrongly filed as Kombinationen in L02/L03/L09; exact duplicate-example groups 2 in L08/L09. Preserve as release backlog without editing other lessons during L07.

**Normal next production: L08 Phase1 ONE-WHOLE-LESSON audit**. Keep L07 `RELEASE_BLOCKED_NONIMPORT`; do not reopen microreviews or claim full-card signoff from limited scoped proof. No separate external human reviewer is mandatory.

Receipt: `Lessons/L07/PHASE3-FINAL-VERIFIED-OWNER-RECEIPT-20261109.json`; full blocker ledger `Lessons/L07/PHASE3-154-CARD-BLOCKER-LEDGER.jsonl`, language evidence `Lessons/L07/PHASE3-SCOPED-DUDEN-FORM-EVIDENCE-20261109.json` and scripts under `Tools/`.

---
## Historical L07 Phase1/Phase2 plan
# Aspekte B1+ · L07 „Für immer und ewig“ — Drei-Phasen-Plan

**2026-11-09 · Phase1 DONE · Phase2 DONE (154 case dispositions / 54 real card changes) · Phase3 NEXT · NONIMPORT**

**Current curated owner:** personal Library `libfile_913f640e14848191ab5c158bfc5cbcf7` (ZIP SHA256 `fa13137b65c7e071da8eb857a01a82e0709c60874978df42ceb00d021e66ead6`). Actual 1571-card primary JSONL SHA `567005150e40cf8987f815e38f70c999802f58a9dc4677121182430b347d48ef`. Library readback byte-identical; ZIP CRC / all 257 manifest hashes PASS. Source mapping 1548 rows unchanged, all 1417 non-L07 card objects unchanged.

**Phase2 actual outcome:** all 154 cards classified, 54 saved learner-card objects changed; 34 new sense networks, 55 sense blocks, 105 explicit DE/FA example-to-sense bindings, 110 new bilingual combinations (global count now 832). Misrouted `jemals`/`niemals` examples corrected without splitting either lemma; one exact `Alles Liebe!` German example deduplicated, two Persian alternatives kept, 38 example status entries marked PENDING. 348 current bilingual example objects, same count as Phase1. 38 original L07 HOLDs retained; zero proven per-form morphology attestations in primary L07 data. No full-card signoff or actual app import test.

**Phase3 / next whole-lesson action:** verify unresolved linguistic ambiguity and 38 HOLD cases, inspect all 54 targeted modifications plus untouched 100 cards in proper contextual QA, independently check actual morphology (without treating missing provenance as a wrong German form), compare collocations/sense examples to German/Farsi meanings, apply strict regression gate and test real app importer/front/back if available. Whole-lesson 154-card gate must end either RELEASED with proof or explicit RELEASE_BLOCKED_NONIMPORT; never invent human/external reviewer or repeat 10-word cycles. Keep unresolved global finite clause candidate cases in L02/L03/L09 (3), and duplicate groups in L08/L09 (2), without editing them as part of L07.

Canonical evidence:
- `Lessons/L07/PHASE2-VERIFIED-CURATED-OWNER-RECEIPT-20261109.json`
- `Lessons/L07/PHASE2-WHOLE-154-CARD-REPORT-20261109.json`
- `Lessons/L07/PHASE2-154-CARD-DISPOSITIONS.jsonl`
- `Lessons/L07/PHASE2-CONTENT-EDIT-DETAILS-20261109.json`
- `Tools/build_L07_phase2_v1.py`

---
## Historical Phase1 plan (preserved for evidence)
# Aspekte B1+ · L07 „Für immer und ewig“ · Drei-Phasen-Plan

**Stand 2026-11-09 · Phase 1 / 3 DONE · Phase 2 NEXT · Phase 3 planned · NONIMPORT**

**Authoritative learner-card owner (UNCHANGED):** Library `libfile_714e7e818a4881919c2639503c928bc8` SHA256 `cc964921ac68e2dabac96e7074a72101c4cf47beda7f14b876ff248aff029990`, 1571 cards and 1548 mapped original source records. The audit ZIP is only an evidence archive, **not a new learner-data version**.

## Phase 1 — complete whole lesson
- All **154 current cards / 153 original source rows 847–999** checked. Original row **956 correctly splits** into two separate existing cards `jemals` and `niemals`; all 154 card IDs mapped; no orphan source row.
- **348** current DE–FA examples, zero missing examples or blank bilingual fields. **41** examples missing explicit QA status on **35** cards; **38** previous curated HOLDs; **one** identical German example duplicate in `Alles Liebe!` (source ordinal 971; two near-equivalent Persian versions).
- **6** word-network cards / **7** meaning blocks / **12** examples without meaning-specific sense routing; **14** existing meaning-specific combinations. No scoped front morphology approval fields set on L07 cards (**0/154**); two unapproved individual morphology proposals do not constitute verification.
- All **154 phase2 decisions** saved, priorities **P1=44, P2=14, P3=96**. P3 is not a full-card German–Persian approval, just no flagged urgent structural issue.
- Existing finite-clause heuristic v4: **0 L07 candidates in 14 combinations**, but **3 corpus-wide candidates outside L07** (L02/L03/L09). Global release gate remains blocked.
- **Verified audit-only Library bundle:** `libfile_ac51645712a48191a220524cfca00934`, SHA256 `0c6cac38097636700f24458e19b32d0c49bd9a89526119e7366adabb8c572375`, 79,793 bytes, 9 ZIP members / 8 SHA256 manifest checks and CRC PASS, exact Library byte readback PASS. Contains all 154 complete decision JSONL rows, evidence report, source-map coverage, v4 global report, QA-only 154-card HTML, replayable audit script, and this lesson plan. GitHub receipt: `PHASE1-VERIFIED-AUDIT-RECEIPT-20261109.json`. Library is the complete audit/decision queue owner.

## Phase 2 — one whole-lesson editorial pass NEXT
Evaluate all 154 cards (not ten-card review loops). Resolve or preserve the 38 HOLDs with explicit reasons; consolidate exact duplicate example without losing useful Persian paraphrase; assign appropriate **PENDING** state to 41 statusless examples, never auto-PASS. Match 12 examples to meanings only if evidence supports the correct sense; preserve ambiguous routing as pending. Improve or add natural bilingual collocations and repair grammatical forms with proportionate evidence; do not demand outside human validation. Multiple accepted meanings stay in ONE card in primary-to-secondary order.

**Persist actual changes in the primary 1571-card JSONL in a NEW ZIP.** Require validated before/after card-object diffs, unchanged 1417 non-L07 cards, all original 1548 source links and stable 1571 IDs, ZIP manifest and CRC plus exact Library readback. Report-only edits must not count as learner-card changes. Original publisher CSV is not the source of truth.

## Phase 3 — full-lesson final gate
Document case-by-case German–Persian semantics, front morphology, examples and right-card relations, including all HOLD outcomes. Run global and L07 finite-clause and duplicate regression; test **actual German-Flashcards-Pro import/render if accessible**. Offline HTML or TSV simulations do not substitute for app runtime. If unresolved, close as **RELEASE_BLOCKED_NONIMPORT**, not as endless micro-review. No separately hired human reviewer prerequisite.
