# B2 execution exit guard — v1.0.0 (ACTIVE, 2026-11-07)

**Purpose:** Stop the observed "continue → status checks → retry latest.json → more status checks" loop. This is a source-owned operating rule, not a change to ChatGPT's platform/runtime.

## Strict rules for EVERY response (including «ادامه بده»)

1. **One target per turn.** Select exactly the next unfinished substantive lesson pass from `RUN-CONTROL.json`, not from an older R-number in `CHECKPOINT.json`. A turn can perform internal work and corrections within that pass, but it must end with one explicit outcome and a terminal answer. Never keep a chat message running while repeatedly switching to metadata maintenance.
2. **Actual work first, metadata last.** Resolve accepted source once; create/improve the actual lesson artifact; run content/format QA; optionally record a concise receipt. Do not begin a response by attempting to repair every legacy pointer. `LATEST.json` is secondary history if newer verified owner-local artifacts and `RUN-CONTROL.json` exist.
3. **Sync circuit breaker.** At most **ONE** attempt per destination (Library and GitHub) to save the pass result or update a pointer in a given turn. On an error, write/keep a clear `SYNC_PENDING` status with exact path and last known good artifact, then **STOP**. Do not recursively retry, refresh, refetch, rematerialize and retry inside the same response. No "first synchronize the previous lesson" preflight on each «ادامه بده».
4. **No endless QA micro-rounds.** Each lesson uses the existing maximum of three milestone passes: (1) full content, (2) full linguistic QA and corrections, (3) real technical release or precise BLOCKED disposition. If approved evidence is unavailable, finish PASS 3 with `BLOCKED_NONIMPORT`; carry forward exact blockers and move on. Never label a single AI's reread as independent signoff.
5. **Mandatory explicit terminal state.** Each assistant response must end with: `LESSON`, `PASS`, `ACTUAL OUTPUT / SAVED LOCATION`, `PASS OR BLOCKED`, `NEXT ACTION`. If no source mutation or artifact saved, say so explicitly. A truthful `BLOCKED` is an acceptable *end of response*; it is not permission to bypass quality.
6. **Keep QA mandatory, avoid false release.** Preserve accepted curated edits, IDs, all verified senses on one lexical card, DE/FA correctness, full-lesson coverage, nonimport flags, seven technical stages, independent checks where required and real app/SRS tests. Do not re-import the historical book. Do not delete or merge imported cards without authorization.
7. **Bounded files.** At most one working full-lesson dataset and one compact receipt per substantive pass. Save in the B2 owner Library/GitHub paths. No miniature R-number chain, repeated ZIP, duplicated LATEST files, or unrelated optimization work.
8. **Meaning of status:** `PASS_COMPLETE_DRAFT` means draft produced, not linguistic release. `PASS2_AI_REVIEW_DONE` means editorial check, not independent QA. `PASS3_BLOCKED_NONIMPORT` means end of this three-pass production cycle without import permission. Never imply `RELEASED` with zero approved cards.
9. **User is not the retry controller.** If they say only «ادامه بده», continue the next task in RUN-CONTROL. Do not ask for more "continue" just to finish a sync; and do not re-run completed passes.

## Exact recovery point, established from owner artifacts (2026-11-07)

- L01: R47 158 draft units, HOLD. Do not re-review historical source.
- L02: 110 reviewed draft units, PASS3 BLOCKED_NONIMPORT, published/imported cards 0.
- L03: 186 reviewed draft units with 372 DE/FA pairs; PASS3 BLOCKED_NONIMPORT, published/imported cards 0. Verified Library current file `Current/L03-PASS2-186-CURATED-REVIEW-NONIMPORT.csv`, SHA256 `c0cfeffa7b1b678336c42b3f8b226d2e2410a643455bf43d10bea71c4bcbd576`. Related GitHub report `Docs/L03-PASS2-AND-PASS3-COMPACT-RESULT-20261107.md`.
- L04: NEXT ACTIVE = **PASS 1 OF 3**, use curated `Current/R22-L04-184-ONE-MORPHOLOGY-EDITORIAL-RESOLUTION.jsonl`, SHA256 `32176c1775445854633a968823a4b3abfd8c920b9fa60ca08c8520781f69f78a`; create a full 184-row learner-card draft, including proper handling of existing source-unit shape exceptions. No R22 re-ingestion, no book re-audit. Do not claim completion until actual full draft is stored and verified.
- Global L05 R25 ZIP checkpoint stays historical; no regression or global stage promotion.

**This guard takes priority over stale "next_action" strings and previous unconstrained instructions about repeated checking. It changes execution discipline only, not stage/quality authority.**
