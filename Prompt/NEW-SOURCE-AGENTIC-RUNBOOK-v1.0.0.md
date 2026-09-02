# New Source Agentic Runbook v1.0.0

Use this runbook with `START-PROMPT-v3.1.11.md` whenever a new book/source is supplied.

## 1. Resolve the source before generation

- Treat the user-provided source as authoritative for inventory, source spelling, lesson/chapter placement, and source lineage.
- Identify level, source/book name, unit boundaries, included word types, and target delivery runtime.
- Do not reuse a source-specific profile from another dataset. In particular, `MENSCHEN-A1-*` profiles are not default profiles for A2/B1/another book.
- If no source-specific product profile exists, start from `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json` and derive only the source-specific metadata/coverage expectations that are actually required.

## 2. Freeze inventory once

Create one source inventory and stable semantic identity map before enrichment. Preserve it throughout the run. Do not repeatedly re-OCR/re-read/recount the entire source after each batch.

The inventory checkpoint must record at least:

- source unit/order;
- source headword/phrase;
- detected learning-unit type;
- lesson/chapter/deck placement;
- stable canonical ID;
- source locator/image/page reference when available.

## 2A. Git-backed persistence is mandatory

For every production source, the run MUST establish a persistent Git-backed workspace before substantial enrichment begins. Chat history, `/mnt/data`, local Codex workspace state, temporary ZIPs, or assistant messages are not durable checkpoints.

Default workspace layout inside the Content Production Kit repository:

```text
Workspaces/<source-slug>/
  00-source/
  01-inventory/
  02-canonical/
  03-evidence/
  04-qa/
  05-delivery/
  06-runtime/
  07-release/
  CHECKPOINT.json
```

If a project-specific repository is explicitly designated for production datasets, the same logical layout may live there instead. The repository + branch + path must be recorded in `CHECKPOINT.json`.

A stage is not considered durably `DONE` until its authoritative artifact(s) have been committed and pushed to the configured Git branch. A local file that has not reached Git is `LOCAL_ONLY`, never `DONE`.

`CHECKPOINT.json` must record at least:

- dataset/source identity;
- repository and branch;
- source authority and source file/image inventory;
- active Prompt/Architecture/Contract versions;
- target Flashcards Pro repository, branch and commit SHA;
- stage states (`NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `DONE`);
- paths + SHA-256 for authoritative artifacts created so far;
- last durable Git commit SHA;
- known blockers and exact resume instruction.

Checkpoint policy:

1. Commit source inventory + stable IDs immediately after inventory QA.
2. Commit canonical data before external enrichment mutates downstream outputs.
3. Commit evidence cache incrementally so successful external retrieval is never repeated merely because a later unit failed.
4. Commit QA reports after each hard gate execution.
5. Commit delivery projection and runtime evidence before packaging.
6. Commit release ZIP manifest/hash evidence after post-package verification.
7. Never mark a stage `DONE` in chat unless the corresponding durable Git commit exists.
8. At the start of a new chat/session, inspect the Git workspace and resume from `CHECKPOINT.json`; do not reconstruct completed stages from conversation memory.

If Git write access is unavailable, continue only as far as is safe and mark the run `PERSISTENCE_BLOCKED`. Before the session ends, produce a recovery bundle and state explicitly that the checkpoint is not durable until committed. Do not silently rely on temporary storage.

## 3. Produce canonical content

Build canonical Learning Units under Architecture v3.1.5 / semantic contract 3.1.3. Preserve source facts and distinguish them from externally verified enrichment.

External lexicons may verify/enrich morphology, sense, translation, Rektion, collocations and lexical relations, but may not silently replace the source inventory.

## 4. Evidence/cache model

- Cache external responses by normalized lemma/construction + source + access/version key.
- Retry only failed/missing/stale units with backoff.
- Never rerun a full-source web retrieval merely because a subset failed.
- Keep raw evidence separate from canonical learner-facing content.
- Legacy enrichment, historical mappings, NVV fields, or previous card datasets remain disabled unless the user explicitly requests a named recovery workflow.
- Evidence cache progress must be persisted through the Git-backed workspace rules in §2A.

## 5. Quality before density

Run lexical-quality validation before interpreting coverage numbers.

- Do not create content to satisfy a count.
- Example-derived phrases are not collocations.
- Collocations must be atomic, evidence-backed and sense-aligned.
- Synonyms/antonyms require sense-bound evidence; otherwise omit them.
- Explicit valency notation in the learner headword requires explicit Rektion.

Preferred coverage gaps are reported numerically and do not authorize fabrication.

## 6. Delivery and runtime

Resolve the current Flashcards Pro runtime before delivery. `v354` is the current verified baseline for this runbook, not a forever-hardcoded target. If the connected Flashcards-Pro repository has advanced, pin the acceptance test to the actual intended target version.

Before Final, execute the actual target importer/presentation contract or an exact version-pinned acceptance fixture and prove:

- every row/card imports;
- no invalid or duplicate IDs;
- learner-facing fields have runtime-compatible shapes;
- canonical content round-trips without loss;
- examples retain DE + FA + EN grouping;
- verb forms and changed learner details render;
- raw JSON is not exposed to the learner UI.

If the target runtime cannot be executed or equivalently pinned, Runtime Acceptance is `NOT_RUN`/blocked and the artifact must not be called Final.

Runtime acceptance artifacts and the exact target runtime commit SHA must be committed to the persistent workspace before Packaging can be marked `DONE`.

## 7. Required gate order

1. Source inventory QA
2. Canonical / Architecture validation
3. Linguistic audit
4. Lexical Quality Gate
5. Product Completeness / coverage report
6. Delivery projection
7. Target Runtime Acceptance
8. Packaging + manifest/hash
9. Independent post-package verification

A hard-gate failure triggers repair and rerun of affected stages. Do not stop every N cards and ask the user to say continue.

Each `DONE` transition above must also satisfy the durable Git checkpoint rule in §2A.

## 8. Final deliverables

A completed source run should deliver, at minimum:

- canonical JSON;
- Flashcards Pro Universal TSV (when that is the selected transport);
- source inventory / identity map;
- lexical-quality report;
- completeness/coverage report;
- delivery validation;
- runtime acceptance report;
- final status + manifest/hash evidence;
- final package ZIP;
- direct TSV separately for normal Flashcards Pro import;
- `CHECKPOINT.json` showing the final durable Git commit SHA and paths/hashes of all authoritative artifacts.

Only call the package `Final` when every applicable hard gate actually executed and passed and the final authoritative artifacts are durably committed to Git.
