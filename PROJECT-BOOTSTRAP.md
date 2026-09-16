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
2. Read `PROJECT-STATE.json`, `README.md`, the active `Prompt/START-PROMPT-v3.1.12.md`, `SOURCE-ACCESS-PROTOCOL-v1.0.0.md`, and `SOURCE-REGISTRY.json` from current `main`.
3. Read the relevant source/workstream `CHECKPOINT.json` and source `SOURCE-MANIFEST.json` from the branch recorded in `PROJECT-STATE.json`.
4. Resolve raw source files according to `SOURCE-ACCESS-PROTOCOL-v1.0.0.md`: Project Sources first, then ChatGPT Library, while an explicitly newer user-provided source in the current chat overrides older registered copies.
5. Inspect `hosseinmehdizade-tech/German-Flashcards-Pro/main/PROJECT-BOOTSTRAP.md` and `PROJECT-STATE.json` whenever the task may touch importer/runtime/presentation compatibility.
6. Compare any user-supplied newer artifact with durable Git state before choosing the working authority.

Do not ask the user to reconstruct history or re-upload a registered source until Project Sources and Library have both been checked.

## 3. Source access is stable and cross-chat

`SOURCE-ACCESS-PROTOCOL-v1.0.0.md` is the stable source-location protocol.

- Project Sources are the primary active source shelf.
- ChatGPT Library is the persistent redundant/fallback shelf.
- GitHub stores durable source identity, hashes, manifests, checkpoints and derived production artifacts, not raw copyrighted books by default.
- A source present in both Project Sources and Library is one logical source when the SHA-256 matches; do not process it twice.
- Durable identity is `source_id + SHA-256/source version`, not transient ChatGPT file IDs or filenames alone.
- Same title with a different hash is an edition/revision conflict and must not be silently substituted.
- New sources are registered when they first become active; the user does not need every Library book pre-registered.

Do not keep changing Project Instructions for ordinary source-management refinements. Project Instructions point to this Bootstrap; operational source rules live in the versioned Source Access Protocol.

## 4. GitHub is durable coordination, not a blocker

- Git persistence is required for durable PASS/FINAL checkpoints.
- Ordinary safe work may continue from a newer explicit user artifact while GitHub temporarily lags or is unavailable.
- Never label local-only work `PASS`, `FINAL`, or `VERIFIED` if the production rules require Git-backed evidence.
- When Git becomes available, persist the exact artifact identity/version/SHA-256 and resume from the durable checkpoint without redoing unrelated completed work.

## 5. Parallel workstreams are first-class

Grammar, Vocabulary, Lesen, Schreiben, source ingestion, enrichment, QA, delivery projection and Flashcards runtime work may progress in parallel.

Rules:

- Keep source identities and checkpoints separate.
- Do not let one workstream overwrite another workstream's authority.
- Do not hardcode content production to an old Flashcards runtime. Resolve the actual intended runtime at Stage 6.
- On a true upstream change, invalidate only the affected downstream stages.
- Preserve stable IDs and provenance across chats.

## 6. Content-production rules

- Preserve source terminology, lesson/chapter placement, spelling, lineage and explicit source evidence.
- External sources verify/enrich; they do not silently replace source inventory.
- Do not fabricate lexical claims, collocations, synonyms, antonyms, Rektion, provenance, or source locators to satisfy a target count.
- Keep Grammar concepts distinct from source chapters; multiple source chapters may map to one central concept when appropriate.
- Runtime/presentation acceptance must be pinned to the exact Flashcards artifact/commit used at that moment.

## 7. User-time rule

This is a side project. Work agentically through the defined pipeline and avoid repeated routine confirmations. Surface only material blockers or decisions that affect data loss, source fidelity, architecture, scope, or visible UI/UX.

## 8. If state is ambiguous

Do not guess. Identify the mismatch, prefer the newer explicit user authority when the user has identified it, record the discrepancy, and continue as far as safely possible. For source lookup, check Project Sources and Library before asking the user. Ask only when GitHub, source registry/manifests, checkpoints, hashes, Project Sources, Library, and current uploads cannot resolve the ambiguity.
