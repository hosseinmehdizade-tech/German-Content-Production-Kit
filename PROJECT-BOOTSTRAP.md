# PROJECT BOOTSTRAP — MANDATORY FIRST STEP FOR EVERY NEW CHAT

This file is the cross-chat startup protocol for **German Content Production Kit** and all source workstreams such as Grammar, Vocabulary, Lesen, Schreiben, Menschen and future content sources.

## 1. Resolve authority before doing work

Use this precedence order:

1. **Explicitly newer user-supplied source/app artifact in the current chat** — if the user uploads a file/ZIP/folder and explicitly identifies it as the latest/current authority, use it immediately for that task.
2. **`PROJECT-STATE.json` + current GitHub `main`** — durable cross-chat coordination and framework state.
3. **Relevant source/workstream `CHECKPOINT.json` on the branch recorded in project state** — authoritative resume position and stage status.
4. **Historical branches, legacy enriched outputs, old mappings, old ZIPs, chat memory** — never treat these as current unless the user explicitly requests recovery/comparison.

Never silently downgrade from newer explicit user input to older GitHub content.

## 2. Mandatory startup sequence

At the start of every substantial content session:

1. Read this `PROJECT-BOOTSTRAP.md` from `German-Content-Production-Kit/main`.
2. Read `PROJECT-STATE.json`, `README.md`, and the active `Prompt/START-PROMPT-v3.1.12.md` from current `main`.
3. Read the relevant source/workstream `CHECKPOINT.json` from the branch recorded in `PROJECT-STATE.json`.
4. Inspect `hosseinmehdizade-tech/German-Flashcards-Pro/main/PROJECT-BOOTSTRAP.md` and `PROJECT-STATE.json` whenever the task may touch importer/runtime/presentation compatibility.
5. Compare any user-supplied newer artifact with durable Git state before choosing the working authority.

Do not ask the user to reconstruct history that Git/checkpoints/manifests can answer.

## 3. GitHub is durable coordination, not a blocker

- Git persistence is required for durable PASS/FINAL checkpoints.
- Ordinary safe work may continue from a newer explicit user artifact while GitHub temporarily lags or is unavailable.
- Never label local-only work `PASS`, `FINAL`, or `VERIFIED` if the production rules require Git-backed evidence.
- When Git becomes available, persist the exact artifact identity/version/SHA-256 and resume from the durable checkpoint without redoing unrelated completed work.

## 4. Parallel workstreams are first-class

Grammar, Vocabulary, Lesen, Schreiben, source ingestion, enrichment, QA, delivery projection and Flashcards runtime work may progress in parallel.

Rules:

- Keep source identities and checkpoints separate.
- Do not let one workstream overwrite another workstream's authority.
- Do not hardcode content production to an old Flashcards runtime. Resolve the actual intended runtime at Stage 6.
- On a true upstream change, invalidate only the affected downstream stages.
- Preserve stable IDs and provenance across chats.

## 5. Content-production rules

- Preserve source terminology, lesson/chapter placement, spelling, lineage and explicit source evidence.
- External sources verify/enrich; they do not silently replace source inventory.
- Do not fabricate lexical claims, collocations, synonyms, antonyms, Rektion, provenance, or source locators to satisfy a target count.
- Keep Grammar concepts distinct from source chapters; multiple source chapters may map to one central concept when appropriate.
- Runtime/presentation acceptance must be pinned to the exact Flashcards artifact/commit used at that moment.

## 6. User-time rule

This is a side project. Work agentically through the defined pipeline and avoid repeated routine confirmations. Surface only material blockers or decisions that affect data loss, source fidelity, architecture, scope, or visible UI/UX.

## 7. If state is ambiguous

Do not guess. Identify the mismatch, prefer the newer explicit user authority when the user has identified it, record the discrepancy, and continue as far as safely possible. Ask the user only when GitHub, checkpoints, manifests, hashes, and the current uploads cannot resolve the ambiguity.
