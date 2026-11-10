# Aspekte B1+ — Lektion 10 three-phase plan

**Stand:** 2026-11-10 · **Phase 1 DONE** · **Phase 2 DONE** · **Phase 3 NEXT** · **RELEASE_BLOCKED_NONIMPORT**.

## Current owner — Phase 2 verified, actual learner edits

- Library archive: `Aspekte-B1plus-L10-PHASE2-WHOLE-208-CARD-CURATED-NONIMPORT-20261110.zip`
- Library ID `libfile_8994942fe9888191af408b0a53a9cced`; ZIP SHA256 `0726c7daa1df91fb6198b8936ec95cf31617c358497022e7ee5e8b87ef049636`.
- Primary 1,571-card JSONL SHA256 `290179d3a84051cf4817c2f9bf8070b46d68ac285cee4c5876c72244ac29a60c`. Source-to-card map 1,548 original rows: SHA256 `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882` unchanged.
- ZIP: 302 members / 301 SHA256 manifest entries, CRC PASS, exact Library byte-for-byte readback PASS.
- Verified control receipt: `PHASE2-VERIFIED-CURATED-OWNER-RECEIPT-20261110.json`.

## Phase 1 DONE

208 original learner cards / 207 distinct source rows, 450 bilingual examples, 29 missing status entries, 60 missing/invalid sense routes, 5 full finite clauses wrongly used as Kombinationen and 46 inherited HOLDs. Phase1 package was AUDIT_ONLY and did not become the primary owner.

## Phase 2 DONE — substantive full-lesson screen

- All 208 L10 card objects passed one bounded per-card structural/editorial disposition; **59 actual primary learner cards were changed**. Other 1,363 cards in the 1,571-card dataset are unchanged as full JSON objects.
- 29 missing DE–FA QA statuses explicitly set to PENDING, not PASS; 60 examples routed to existing case-specific sense IDs, including ten polysemous records.
- Five full clauses in combination fields rewritten to non-finite useful collocations; two shared-source split-lemma examples rewritten to match the actual learner lemma; three newly authored DE–FA examples illustrate otherwise unused sense IDs. 450 → 453 examples.
- All 46 inherited HOLDs remain, no source ordinal/preview ID lost, no front morphology silently attested, no formal approvals, no original publisher re-inventory. Global known finite-pattern findings: 2 **outside** L10 in L02/158 and L03/232, **0 in L10**. No corpus-wide exact duplicate DE examples or exact collocation/example copies.
- Scope limit: the 208-row screen is **not** full German–Persian semantic certification. No independent human review is claimed, and real app import/render has not been tested. All retained flags stay unresolved as appropriate.

## Phase 3 NEXT — whole-208 final fail-closed QA

Conduct a case-level release/blocker disposition across all 208 cards, targeted bilingual/semantic/idiomatic challenges for risky forms and translations, sense routing tests, 29 prior PENDING statuses, 5 repaired collocations and the three new examples. Verify no regressions in 1,363 other cards and all 1,548 source rows. Run negative mutation tests. Retain `RELEASE_BLOCKED_NONIMPORT` if technical app import, language quality, or older blockers cannot be conclusively verified. No external independent human reviewer, no microlots and no textbook-source CSV rebuild.
