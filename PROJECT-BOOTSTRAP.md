# PROJECT BOOTSTRAP — MANDATORY FIRST STEP FOR EVERY NEW CHAT

This file is the cross-chat startup protocol for **German Content Production Kit** and all source workstreams.

**MANDATORY OUTCOME EXECUTION GATE (2026-10-23):** Read `EXECUTION-OUTCOME-EFFICIENCY-POLICY.json` for every substantive start/resume/`ادامه بده` turn alongside `EXECUTION-SAFETY-POLICY.json`. Continue the major workstream queue, not repetitive 3–5-card patch/report cycles. Track reviewed/kept/corrected/held/remaining; scoped QA, ZIP or Git sync is not completed parent Stage. Preserve original/LOCKED, final QA, single-writer/CAS, exact resume and bounded Git synchronization. New meaningful outcome receipts use `Verification/validate_execution_outcome_receipt.py`. Other chats receive this policy upon their next bootstrap/resume, not by automatic injection.

## 1. Resolve authority before doing work
Use this precedence order:
1. explicitly newer user-supplied current/latest artifact;
2. newest verified portable checkpoint/state from current chat, Project Sources or Library;
3. `PROJECT-STATE.json` + relevant Git checkpoint as durable metadata/ambiguity resolver;
4. historical branches/ZIPs/chat memory only for named recovery/comparison.

Never silently downgrade a newer verified artifact because GitHub is older.

## 2. Mandatory startup

**ACTIVE WORKSTREAM WIP RULE — MANDATORY READ:** Before working on or reporting active Menschen A1/A2/B1, Verben, NVV, Grammar, Vocabulary, Lesen, Schreiben, source-ingestion or QA streams, read `WORKSTREAM-LEAN-EDIT-POLICY.json`. Use one current working content authority per stream and compact edit/QA logs; do **not** generate a cumulative full ZIP or fill Library for every small correction. Preserve exact source provenance, active stream-specific frozen audit baselines (especially NVV post-S9), lightweight validated-milestone Git sync, required verified portable recovery, all Stage4-7 gates, and the ONE complete final vocabulary production ZIP contract. This is prospective; no existing LOCKED artifacts are mutated and no Library file is auto-deleted.
1. Read this file, `PROJECT-OPERATING-MODE-v2.md`, `PROJECT-MEMORY.json`, and `GIT-SYNC-POLICY.json`.
2. Read `PROJECT-STATE.json` to resolve the active framework/version; **do not hard-code an old START-PROMPT**.
3. Resolve the active START-PROMPT and exact portable authority/hash recorded in project state.
4. For a named workstream, read its `CHECKPOINT.json` and source `SOURCE-MANIFEST.json`.
5. Resolve raw sources via explicit current upload → Project Sources → Library, using `SOURCE-ACCESS-PROTOCOL-v1.0.0.md` and `SOURCE-REGISTRY.json`.
6. Inspect `German-Flashcards-Pro` only when runtime/import/presentation compatibility matters.
7. When runtime compatibility matters, read **`FLASHCARDS-RUNTIME-DEPENDENCY.json`**, then Flashcards Pro **`RUNTIME-CURRENTNESS-POLICY.json`** and **`RUNTIME-AUTHORITY-PIN.json`**.
8. Resolve **CURRENT** and **LAST_FULLY_VERIFIED** separately. Target CURRENT for new integration/development even if it has blockers; LAST_FULLY_VERIFIED is regression/fallback evidence only.
9. Materialize the CURRENT portable app artifact and verify SHA-256 before final runtime/import/UI/browser/offline/package acceptance.
10. If CURRENT artifact cannot be materialized or final acceptance is blocked, mark acceptance BLOCKED but **do not retarget integration to an older LAST_FULLY_VERIFIED runtime**.
11. **Mandatory vocabulary output/handoff:** for all new vocabulary/lexical workstreams and lessons, read and enforce `CONTENT-OUTPUT-DELIVERY-POLICY.json` v2.0.0. Deliver ONE organized **complete content-production ZIP** retaining final import-ready data **and** canonical/source/provenance/enrichment/QA/tests/reports/checkpoints/docs/content tools needed for future maintenance. **Never bundle the Flashcards Pro app/runtime.** The previous one-TSV-only simplification is superseded. Nonlexical workstreams retain their own delivery contracts; full app releases retain their separate organized app release contract.


### Workstream-currentness gate — mandatory for every named content status/resume

Read `WORKSTREAM-RESUME-CURRENTNESS-POLICY.json` **before** reporting a lesson's stage or continuing it. For the named workstream, check its local `LATEST.json` (when present) **and its referenced milestone receipt**, then cross-check the portable artifact/hash, central `CHECKPOINT.json` and root `PROJECT-STATE.json`. Workstream-local latest verified progress outranks stale central summaries; a newer validated user/portable artifact outranks Git. **Never report Stage 2B because the central checkpoint still says Stage 2B if local LATEST + receipt already document Stage 3C.** When pointers disagree, identify the stale record and keep the latest verified scope/quality separate from overall PASS/FINAL. After a validated milestone, auto-attempt bounded Git receipt + `LATEST.json` synchronization without using Git for binary transport. For the Menschen A2 lessons use `Workspaces/menschen-a2-24-lessons-v336/LATEST.json`, not just its central `CHECKPOINT.json`. No routine user cross-check should be needed.

## 3. Artifact-first, async Git
`PROJECT-OPERATING-MODE-v2.md` is active. GitHub is a durability/coordination mirror, not the binary transport or critical path. Large portable checkpoint/release bundles live in Project/Library/user-delivery surfaces; Git stores compact source identities, hashes, contracts, checkpoint summaries and sync metadata. Track quality state separately from Git persistence.

## 4. Cross-chat runtime hard gate
For Stage 6 or any other runtime-sensitive acceptance:
- CURRENT and LAST_FULLY_VERIFIED must be recorded separately;
- CURRENT is always the integration/development target, regardless of verification blockers;
- LAST_FULLY_VERIFIED is used only as a regression/fallback comparison;
- the exact CURRENT app/release artifact filename and SHA-256 must be recorded;
- CURRENT artifact must be materialized directly from current chat/Project/Library for final acceptance;
- FINAL/PASS requires testing the resulting overlay/package on the CURRENT portable artifact lineage;
- blockers may stop PASS, but they never cause a silent downgrade of the integration target.

Content-only stages are not invalidated merely because the app runtime moves forward. When runtime acceptance later occurs, it must re-resolve CURRENT at that time.

## 5. Content-production rules
- Preserve source terminology, lesson/chapter placement, spelling, order and lineage.
- External sources verify/enrich; they do not silently replace source inventory.
- Do not fabricate collocations, synonyms, antonyms, Rektion, NVV, provenance or locators.
- Preserve stable IDs and source memberships across chats.
- Keep Grammar, Vocabulary, Lesen, Schreiben and app runtime workstreams separate.
- Resolve runtime compatibility only at the stage where it matters.

## 6. Current framework resolution
The active framework is whatever `PROJECT-STATE.json -> active_framework` says. If Git metadata and a newer verified portable artifact disagree, use the newer verified artifact and mark Git sync pending.

## 7. User-time rule
Work agentically and minimize routine confirmations. Surface only material blockers or decisions involving data loss, architecture, scope, source fidelity or noticeable UI/UX changes.


## 8. Project memory reconsideration rule

Before recommending a process/automation/Git/authority/packaging/source-governance/UI change, read `PROJECT-MEMORY.json`.

If the proposal conflicts with an ACTIVE prior incident/decision, explicitly tell Hossein that the idea revisits a previous failure mode, summarize what happened, state the safe default, and only ask for override approval if he still wants to supersede it. Do not rely on Hossein remembering the old incident.

Git synchronization follows the ACTIVE superseding `MEM-006-AUTO-SYNC-VALIDATED-MILESTONES` and `GIT-SYNC-POLICY.json`: attempt lightweight sync after every validated milestone before handoff; bounded failures record PENDING. Temporary edits are not milestones.


## Execution safety / turn-boundary rule

`EXECUTION-SAFETY-POLICY.json` is mandatory. By default, complete **one major durable milestone per turn**: resolve authority → work → validate → persist checkpoint/artifact → sync compact Git metadata → **send a visible final response**. Do not silently start the next major stage in the same turn. Respect the bounded external-tool budget and one corrected retry per failed external operation; if the next stage cannot be completed safely within the turn, stop at a durable checkpoint and report the exact next action.


## Failure-prevention lifecycle

Read every applicable ACTIVE `PROJECT-MEMORY.json` entry, including its `prevention` lifecycle, gate status/limits and evidence. Root memory owns reusable lessons; checkpoints reference stable IDs and retain local counts/rejected candidates. Run applicable early gates before expensive downstream work. Schema/gate PASS is not linguistic or exact-runtime acceptance. Preserve original decision seals and reciprocal supersession lineage.

- Startup/metadata: `python -B Verification/prevention_preflight.py memory`; validate new/updated checkpoints with its `checkpoint` mode.
- Stage5 before packaging: run `projection PROJECTED.json` (or direct-import TSV) for envelope/ID/known learner-field defects; still use official v3.3.6 portable completeness/anti-bypass tooling.
- Final archive: run `package CANDIDATE.zip`, then manifest/hash and exact-runtime gates where applicable.
- Stage6/7 harness readiness: consume app memory `MEM-024-ASYNC-MANIFEST-READINESS`; wait for expected commit identity/count, reuse identical candidate bytes after harness-only failures.
- Full v3.3.6 authority remains the pinned portable package. These supplemental preflights do not promote this compact Git mirror to full framework authority.

For projection-only successors, run `Verification/prevention_preflight.py lineage PROJECTED.json --baseline RESOLVED_PARENT.json` at Stage5. Resolve the immutable parent from its checkpoint first; retain current canonical parity and reviewed metadata/identity changes as separate gates.


## User observation / runtime acceptance rule

For Stage6/Stage7 and other runtime-sensitive content acceptance, routine user-run acceptance kits and repetitive Y/N questionnaires are retired. Follow the canonical German-Flashcards-Pro `USER-OBSERVATION-POLICY.json`: default to automated acceptance plus a concise passive watchlist, and continue ordinary work without requiring an affirmative user response. Ask for one focused real-environment test only when a genuinely changed semantic boundary cannot be automated, a destructive/data-migration risk exists, essential platform-specific integration must be proven, or the user reports an actual regression. Silence is never recorded as manual PASS evidence.
