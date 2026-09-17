# New Source Agentic Runbook v1.0.0

Use this runbook with the active repository START-PROMPT (currently `START-PROMPT-v3.1.12.md`) whenever a new book/source is supplied or an existing source is resumed.

The human-trackable execution model is the mandatory seven-stage pipeline in `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`. Execution remains agentic and end-to-end; the stages are recovery/gate boundaries, not manual approval stops.

> Persistence model: `PROJECT-OPERATING-MODE-v2.md` — artifact-first, async Git. GitHub is a durability mirror, not a prerequisite for ordinary work.

## 1. Resolve the source before generation

- Treat the user-provided source as authoritative for inventory, source spelling, lesson/chapter placement, and source lineage.
- Resolve authority in this order: explicit newer current artifact → newest verified portable state/checkpoint in current files/Project Sources/Library → Git checkpoint/state if needed → historical material only for recovery/comparison.
- Identify level, source/book name, unit boundaries, included word types, and source profile.
- Resolve the current Flashcards runtime only when actual runtime/import/presentation acceptance is needed.
- Do not reuse a source-specific profile from another dataset. In particular, `MENSCHEN-A1-*` profiles are not default profiles for A2/B1/another book.
- If no source-specific product profile exists, start from `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json` and derive only the source-specific metadata/coverage expectations actually required.

## 2. Freeze inventory once

Create one source inventory and stable semantic identity map before enrichment. Preserve it throughout the run. Do not repeatedly re-OCR/re-read/recount the entire source after each batch.

The inventory checkpoint must record at least:

- source unit/order;
- source headword/phrase;
- detected learning-unit type;
- lesson/chapter/deck placement;
- stable canonical ID;
- source locator/image/page reference when available.

## 2A. Portable persistence is mandatory; live Git is not

Every production source must have a resumable workspace/checkpoint identity plus a self-verifying portable state bundle at meaningful boundaries. Chat history alone is not enough.

Default logical workspace layout:

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

The portable state bundle may be stored in current files, Project Sources, ChatGPT Library or user-delivery surfaces. It must carry or reference exact hashes/manifests and the next resume action.

Track two independent dimensions:

- quality state: `NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`
- Git persistence: `IN_SYNC`, `PENDING`, `FAILED`, `NOT_REQUIRED`

A stage may be quality `PASS` when its authoritative artifacts and gate evidence are complete and hash-bound in a verified portable state bundle. Never call it **Git-backed PASS/FINAL/VERIFIED** until the relevant Git sync actually completed.

Git policy:

1. Sync GitHub at meaningful batch/milestone/architecture/handoff boundaries, not per card or small step.
2. Store compact text checkpoints/manifests/hashes/provenance/code in Git.
3. Do not use GitHub as the default transport for generated release ZIPs or large binary checkpoint packages.
4. Do not reconstruct generated ZIPs through Base64 chunks/GitHub Actions merely to make Git hold the binary.
5. In a normal production turn, make at most one Git repair/sync attempt unless the user explicitly asks for Git repair.
6. If Git fails, set `persistence.git=PENDING` or `FAILED`, preserve exact artifact/hash/resume instructions, and continue ordinary safe work.

`CHECKPOINT.json` must record at least:

- dataset/source identity;
- source authority and source file/image inventory;
- active Prompt/Architecture/Contract versions;
- seven stage quality states;
- paths/refs + SHA-256 for authoritative artifacts created so far;
- separate persistence status;
- known blockers/failures/invalidations and exact resume instruction.

At the start of a new chat/session, prefer the newest verified portable checkpoint. Consult Git only as needed to resolve ambiguity or synchronization state; do not reconstruct completed stages from conversation memory.

## 3. Produce canonical content

Build canonical Learning Units under Architecture v3.1.5 / semantic contract 3.1.3. Preserve source facts and distinguish them from externally verified enrichment.

External lexicons may verify/enrich morphology, sense, translation, Rektion, collocations and lexical relations, but may not silently replace the source inventory.

## 4. Evidence/cache model

- Cache external responses by normalized lemma/construction + source + access/version key.
- Retry only failed/missing/stale units with backoff.
- Never rerun a full-source web retrieval merely because a subset failed.
- Keep raw evidence separate from canonical learner-facing content.
- Legacy enrichment, historical mappings, NVV fields, or previous card datasets remain disabled unless the user explicitly requests a named recovery workflow.
- Preserve successful evidence/cache progress in the portable state bundle so later Git trouble does not force re-fetching.

## 5. Quality before density

Run lexical-quality validation before interpreting coverage numbers.

- Do not create content to satisfy a count.
- Example-derived phrases are not collocations.
- Collocations must be atomic, evidence-backed and sense-aligned.
- Synonyms/antonyms require sense-bound evidence; otherwise omit them.
- Explicit valency notation in the learner headword requires explicit Rektion.

Preferred coverage gaps are reported numerically and do not authorize fabrication.

## 6. Delivery and runtime

Resolve the current Flashcards Pro runtime only when Stage 6 or an actual integration task is reached. Historical baselines are evidence, not permanent targets.

Before Final, execute the actual target importer/presentation contract or an exact version-pinned acceptance fixture and prove:

- every row/card imports;
- no invalid or duplicate IDs;
- learner-facing fields have runtime-compatible shapes;
- canonical content round-trips without loss;
- examples retain DE + FA + EN grouping;
- verb forms and changed learner details render;
- raw JSON is not exposed to the learner UI.

If the target runtime cannot be executed or equivalently pinned, Stage 6 is `BLOCKED` and the artifact must not be called runtime-verified Final.

Runtime acceptance artifacts must be included in the portable state bundle with exact runtime identity and hashes. Git synchronization may follow at a meaningful boundary.

## 7. Required seven-stage gate order

1. **Source & Inventory** — source inventory QA + stable IDs
2. **Canonicalization** — canonical construction + Architecture/Contract validation
3. **Evidence & Enrichment** — incremental evidence cache + evidence-linked enrichment
4. **Linguistic & Lexical QA** — linguistic audit + lexical quality + product coverage
5. **Delivery Projection** — Universal v2/selected transport + delivery validation
6. **Runtime & Presentation Acceptance** — target importer/runtime + Presentation Model/practice acceptance
7. **Release & Post-Package Verification** — packaging + manifest/hash + independent post-package verification

A hard-gate failure triggers repair and rerun of the affected stage plus every downstream stage invalidated by the change. Do not restart valid upstream PASS stages without evidence they are invalid. Do not stop every N cards or after every stage to ask the user to say continue.

## 8. Final deliverables

A completed source run should deliver, at minimum:

- canonical JSON;
- Flashcards Pro Universal TSV (when selected transport);
- source inventory / identity map;
- lexical-quality report;
- completeness/coverage report;
- delivery validation;
- runtime acceptance report;
- presentation acceptance report;
- final status + manifest/hash evidence;
- final package ZIP;
- direct TSV separately for normal Flashcards Pro import;
- portable `CHECKPOINT.json` / state bundle showing all seven quality states and exact artifact hashes;
- separate Git persistence status.

Only call the package `Final` when every applicable hard quality gate actually executed and passed. Only call it **Git-backed Final** when the required Git synchronization also completed.
