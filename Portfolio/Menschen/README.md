# Menschen Portfolio — P0 Read-only Dashboard

**Status:** P0 completed (2026-10-16), isolated from all content LOCKs and German Flashcards Pro runtime.

## Where to resume
1. Read [LATEST.json](LATEST.json) for the exact verified dashboard ZIP filename, SHA256, Library ID and the pinned workstream LATEST hashes.
2. Resolve newer explicit user artifact / verified portable and the A1, A2, B1 workstream-local `LATEST.json` + receipts **before** treating the P0 report as current. A changing Git blob invalidates the frozen snapshot, not the underlying LOCKED content.
3. Materialize the package from ChatGPT Library: `/German-Content-Production-Kit/Checkpoints/Menschen-Portfolio-P0-Verified-Dashboard-2026-10-16-R2.zip`.
4. Open `DASHBOARD.html` for searchable 72-lesson status, or `DASHBOARD.md` for direct Git receipt links. `Tools/build_dashboard.py` can rebuild offline or refresh from a checkout. Run the 16 Python unittests.
5. **Only update Portfolio records from workstream evidence.** Do not use this derived index to overwrite any `LATEST.json`, Stage7 LOCKED ZIP, source identity, SRS or app files.

## Explicit coverage
- A1: L02–L24 23/23 individually Git-verified Stage7 receipts; L01 historical v3.3.2, v3.3.6 incomplete. A1 audit M12 synthetic read-only/rollback proof **not** official content FINAL.
- A2: L01–L19 19/19 individually Git-verified Stage7 receipts; L20 Stage3C passed, Stage4 next at pinned Git SHA.
- B1: L01–L18 18/18 individually Git-verified Stage7 receipts; L19 Stage4 Repair3 scoped PASS, full Stage4 BLOCKED at pinned Git SHA.
- B1+/B2/C1: future scope; original sources and **actual** lesson counts must be registered first.

## Scope of P0's PASS
16/16 positive and negative Python tests, fresh-extraction 16/16, deterministic ZIP, 12/12 manifest paths, 13/13 sums and byte-identical Library roundtrip. Git Stage7 receipt contents were read for 60 lessons; lesson ZIP bytes, live IndexedDB, runtime Stage6 and full language QA were **not** reverified as part of P0.

## Guardrails
The artifact is read-only and content-free (only source metadata and checkpoint references). No automatic scheduled task is installed and no change to learner-visible UI is authorized. After each validated content milestone, call the refresh script from an updated checkout and record the new snapshot; this project's latest verified portable artifact always outranks an outdated central summary. See `WORKSTREAM-RESUME-CURRENTNESS-POLICY.json` and `CONTENT-OUTPUT-DELIVERY-POLICY.json`.

## P1 — Event-triggered read-only refresh (2026-10-16)

The new source-controlled automation is [.github/workflows/menschen-portfolio-refresh.yml](../../.github/workflows/menschen-portfolio-refresh.yml). After pushes affecting any of the A1/A2/B1 workstream directories, or a manual `workflow_dispatch`, it runs 17 Python unit/negative tests and rebuilds a **derived** dashboard from the exact checked-out workstream `LATEST.json`, referenced milestone receipts, A1 audit pointer, and individually stored Stage7 lesson receipts.

Source: [Tools/refresh.py](Tools/refresh.py). Tests: [Tests/test_refresh.py](Tests/test_refresh.py). P0’s 60 exact original LOCKED Git blob SHAs are pinned in [P0-BASELINE-EVIDENCE.json](P0-BASELINE-EVIDENCE.json). Report destination after a successful run: [LIVE/DASHBOARD.html](LIVE/DASHBOARD.html), [LIVE/DASHBOARD.md](LIVE/DASHBOARD.md), [LIVE/PORTFOLIO-STATUS.json](LIVE/PORTFOLIO-STATUS.json), and `LIVE/REFRESH-STATE.json`.

The workflow may write **only** those derived files. It does not write/retire/merge any source card, locked package, A1/A2/B1 `LATEST.json`, importer, app, or SRS record. A missing/edited previous Stage7 lock, inconsistent receipt SHA, or premature Stage7 publication makes the job fail closed. Unchanged fingerprints do not rewrite timestamps or create redundant commits.

Operational constraints: actual GitHub Actions execution and write permission must be observed before claiming end-to-end automatic refresh is active. Workflow execution/branch protection can block the generated report without blocking content work. The P0 portable ZIP remains an immutable verified fallback; `Portfolio/Menschen/LATEST.json` is **not** repointed to any unverified LIVE output.
