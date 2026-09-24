# PROJECT BOOTSTRAP — MANDATORY FIRST STEP FOR EVERY NEW CHAT

This file is the cross-chat startup protocol for **German Content Production Kit** and all source workstreams.

## 1. Resolve authority before doing work
Use this precedence order:
1. explicitly newer user-supplied current/latest artifact;
2. newest verified portable checkpoint/state from current chat, Project Sources or Library;
3. `PROJECT-STATE.json` + relevant Git checkpoint as durable metadata/ambiguity resolver;
4. historical branches/ZIPs/chat memory only for named recovery/comparison.

Never silently downgrade a newer verified artifact because GitHub is older.

## 2. Mandatory startup
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

Git synchronization follows `GIT-SYNC-POLICY.json`: bounded, deferred, coalesced, and never required on every batch/version.


## Execution safety / turn-boundary rule

`EXECUTION-SAFETY-POLICY.json` is mandatory. By default, complete **one major durable milestone per turn**: resolve authority → work → validate → persist checkpoint/artifact → sync compact Git metadata → **send a visible final response**. Do not silently start the next major stage in the same turn. Respect the bounded external-tool budget and one corrected retry per failed external operation; if the next stage cannot be completed safely within the turn, stop at a durable checkpoint and report the exact next action.
