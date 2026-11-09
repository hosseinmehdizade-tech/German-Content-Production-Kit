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
