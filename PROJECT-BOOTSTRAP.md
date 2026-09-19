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
1. Read this file and `PROJECT-OPERATING-MODE-v2.md`.
2. Read `PROJECT-STATE.json` to resolve the active framework/version; **do not hard-code an old START-PROMPT**.
3. Resolve the active START-PROMPT and exact portable authority/hash recorded in project state.
4. For a named workstream, read its `CHECKPOINT.json` and source `SOURCE-MANIFEST.json`.
5. Resolve raw sources via explicit current upload → Project Sources → Library, using `SOURCE-ACCESS-PROTOCOL-v1.0.0.md` and `SOURCE-REGISTRY.json`.
6. Inspect `German-Flashcards-Pro` only when runtime/import/presentation compatibility matters.
7. When runtime compatibility matters, read **German-Flashcards-Pro/`RUNTIME-AUTHORITY-PIN.json`** and materialize the pinned portable app artifact before any runtime/import/UI/browser/offline/package acceptance.
8. If that pinned artifact cannot be materialized or its SHA mismatches, runtime acceptance is BLOCKED. **Never substitute the Flashcards Git runtime tree.**

## 3. Artifact-first, async Git
`PROJECT-OPERATING-MODE-v2.md` is active. GitHub is a durability/coordination mirror, not the binary transport or critical path. Large portable checkpoint/release bundles live in Project/Library/user-delivery surfaces; Git stores compact source identities, hashes, contracts, checkpoint summaries and sync metadata. Track quality state separately from Git persistence.

## 4. Cross-chat runtime hard gate
For Stage 6 or any other runtime-sensitive acceptance:
- the exact app/release artifact filename and SHA-256 must be recorded;
- the artifact must be materialized directly from current chat/Project/Library;
- acceptance evidence must state the portable artifact identity;
- a stale Git runtime branch can be used only for engineering/diff work, never as final runtime authority;
- FINAL/PASS requires testing the resulting overlay/package on the pinned portable artifact lineage.

Content-only stages are not invalidated merely because the app runtime moves forward.

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
