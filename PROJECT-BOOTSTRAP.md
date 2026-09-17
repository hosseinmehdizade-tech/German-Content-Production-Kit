# PROJECT BOOTSTRAP — MANDATORY FIRST STEP FOR EVERY NEW CHAT

This file is the cross-chat startup protocol for **German Content Production Kit** and all source workstreams such as Grammar, Vocabulary, Lesen, Schreiben, Menschen and future content sources.

> Active operating model: `PROJECT-OPERATING-MODE-v2.md` — **artifact-first, async Git**.
> This operating model supersedes older wording that put live GitHub persistence on the critical path of ordinary work.

## 1. Resolve working authority before doing work

Use this precedence order:

1. **Explicitly newer user-supplied source/app/state artifact in the current chat** — use immediately when the user identifies it as current/latest.
2. **Newest verified portable state/checkpoint artifact** available from current conversation files, ChatGPT Project Sources or ChatGPT Library.
3. **`PROJECT-STATE.json` + relevant GitHub checkpoint** when needed to resolve ambiguity or when no newer verified artifact exists.
4. **Historical branches, legacy enriched outputs, old mappings, old ZIPs, chat memory** — recovery/comparison only unless explicitly requested.

Never silently downgrade from a newer verified artifact to older GitHub content.

## 2. Startup sequence

At the start of substantial content work:

1. Read this `PROJECT-BOOTSTRAP.md`.
2. Read `PROJECT-OPERATING-MODE-v2.md` and `PROJECT-STATE.json`.
3. Read `README.md`, active `Prompt/START-PROMPT-v3.1.12.md`, `SOURCE-ACCESS-PROTOCOL-v1.0.0.md`, and `SOURCE-REGISTRY.json` when the task needs their rules.
4. Resolve the relevant workstream state from the newest verified portable checkpoint first; consult the GitHub `CHECKPOINT.json` only as much as needed to resolve authority or sync status.
5. Resolve raw source files according to `SOURCE-ACCESS-PROTOCOL-v1.0.0.md`: explicit newer current-chat source → Project Sources → Library → matching current-chat attachment.
6. Inspect `German-Flashcards-Pro` state only when importer/runtime/presentation compatibility actually matters, not as a ritual for unrelated content work.

Do not ask the user to reconstruct history or re-upload a registered source until Project Sources and Library have both been checked.

## 3. Source access is stable and cross-chat

- Project Sources are the primary active source shelf.
- ChatGPT Library is the persistent redundant/fallback shelf and may also hold portable checkpoint/release bundles.
- GitHub stores durable source identity, hashes, manifests, contracts, small text checkpoints and code history; it is not the default binary transport.
- Do not store/reconstruct generated release ZIPs through Base64 chunk workflows merely to make GitHub hold the binary.
- Durable source identity is `source_id + SHA-256/source version`, not transient file IDs or filenames alone.

## 4. GitHub is asynchronous durability, not a blocker

Follow `PROJECT-OPERATING-MODE-v2.md`:

- ordinary safe work continues from the newest verified authority even if GitHub lags or fails;
- make at most one Git repair/sync attempt in a normal production turn unless the user explicitly asks for Git repair;
- if sync fails, record `persistence.git=PENDING` or `FAILED`, preserve exact hashes/resume instructions, and continue the real work;
- quality/QA state and Git persistence state are separate;
- do not claim **Git-backed** PASS/FINAL/VERIFIED unless Git synchronization actually completed.

Git writes should happen at meaningful batch/milestone boundaries, not per card or per small step.

## 5. Parallel workstreams are first-class

Grammar, Vocabulary, Lesen, Schreiben, source ingestion, enrichment, QA, delivery projection and Flashcards runtime work may progress in parallel.

- Keep source identities and checkpoints separate.
- Do not let one workstream overwrite another workstream's authority.
- Do not hardcode content production to an old Flashcards runtime. Resolve the actual intended runtime at Stage 6.
- On a true upstream change, invalidate only affected downstream stages.
- Preserve stable IDs and provenance across chats.

## 6. Content-production rules

- Preserve source terminology, lesson/chapter placement, spelling, lineage and explicit source evidence.
- External sources verify/enrich; they do not silently replace source inventory.
- Do not fabricate lexical claims, collocations, synonyms, antonyms, Rektion, provenance or source locators to satisfy a target count.
- Keep Grammar concepts distinct from source chapters; multiple source chapters may map to one central concept when appropriate.
- Runtime/presentation acceptance must be pinned to the exact Flashcards artifact used at that moment.

## 7. Portable state rule

Every meaningful batch/milestone should produce a self-verifying portable state bundle containing or referencing:

- `CHECKPOINT.json`;
- canonical/derived data required to resume;
- QA/acceptance reports;
- review queue/open issues;
- artifact manifest + SHA-256;
- exact next action.

The bundle may live in Project/Library/user-delivery surfaces. GitHub keeps compact metadata and sync status; it does not need to carry the binary package itself.

## 8. User-time rule

This is a side project. Work agentically through the defined pipeline and avoid repeated routine confirmations. Surface only material blockers or decisions affecting data loss, source fidelity, architecture, scope or visible UI/UX.

## 9. If state is ambiguous

Do not guess. Identify the mismatch, prefer the newer verified authority, mark Git synchronization separately, and continue as far as safely possible. Ask only when source/checkpoint/hash/Project Sources/Library/current uploads cannot resolve the ambiguity.
