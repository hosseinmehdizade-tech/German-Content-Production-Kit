# New Source Agentic Runbook v1.0.0

Use this runbook with the active repository START-PROMPT resolved from the root `README.md` (at this revision: `START-PROMPT-v3.1.13.md`) whenever a new book/source is supplied or an existing source is resumed. Never infer the active prompt from this sentence alone; inspect current `main` first.

The human-trackable execution model is the mandatory seven-stage pipeline in `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`. Execution remains agentic and end-to-end; the stages are durable recovery/gate boundaries, not manual approval stops.

## 1. Resolve the source before generation

- Treat the user-provided source as authoritative for inventory, source spelling, lesson/chapter placement, and source lineage.
- Identify level, source/book name, unit boundaries, included word types, and target delivery runtime.
- Resolve two independent profile layers: a `source_canonical_profile` for Stage 1/2 and a `product_completeness_profile` for Stage 3/4/6. A sparse source profile must never be used as proof that the learner product is rich enough.
- Do not reuse a source-specific profile from another dataset. In particular, `MENSCHEN-A1-*` profiles are not default profiles for A2/B1/another book.
- If no source-specific product profile exists, use `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json` for lexical/completeness policy and `GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json` as the mandatory rich-card product floor unless the user explicitly approves a named relaxation.

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

A stage is not considered durably `PASS` until its authoritative artifact(s) and gate evidence have been committed and pushed to the configured Git branch. A local file that has not reached Git is never `PASS`.

Allowed stage states are exactly:

- `NOT_STARTED`
- `RUNNING`
- `PASS`
- `FAIL`
- `BLOCKED`
- `INVALIDATED`

`CHECKPOINT.json` must record at least:

- dataset/source identity;
- repository and branch;
- source authority and source file/image inventory;
- active Prompt/Architecture/Contract versions;
- both source-canonical and product-completeness profile identities;
- target Flashcards Pro repository, branch and commit SHA;
- the seven stage states from `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`;
- paths + SHA-256 for authoritative artifacts created so far;
- commit SHA establishing each latest durable PASS;
- known blockers/failures/invalidations and exact resume instruction.

Checkpoint policy:

1. Stage 1 PASS commits source inventory + stable IDs + inventory QA.
2. Stage 2 PASS commits canonical data + Architecture/Contract validation before enrichment mutates downstream outputs.
3. Stage 3 PASS commits evidence index/cache state + authoritative enriched canonical; for non-empty rich-card verb datasets the external lexical-enrichment path must actually have been attempted. Missing evidence is allowed and recorded; a disabled enrichment path is not a PASS.
4. Stage 4 PASS commits enriched-canonical structural validation, linguistic QA, lexical quality, coverage evidence, the mandatory product-floor result, and any repaired canonical artifact.
5. Stage 5 PASS commits selected delivery projection + validation/hash/loss evidence.
6. Stage 6 PASS commits exact target runtime identity + importer/persistence + canonical roundtrip + Presentation Model + representative learner-visible product acceptance evidence, including the product floor after import.
7. Stage 7 PASS commits release metadata/manifest/hash/post-package verification and the package or immutable release-asset identity.
8. Never mark a stage `PASS` in chat unless the corresponding durable Git commit exists.
9. At the start of a new chat/session, inspect current Git `main`, active README/START-PROMPT, the source workspace and `CHECKPOINT.json`; do not reconstruct completed stages from conversation memory.
10. When an upstream authoritative artifact changes, mark all dependent downstream stages `INVALIDATED`; preserve unaffected upstream PASS stages.

If Git write access is unavailable, continue only as far as is safe and mark the affected stage `BLOCKED` with reason `PERSISTENCE_BLOCKED`. Before the session ends, produce a recovery bundle and state explicitly that the checkpoint is not durable until committed. Do not silently rely on temporary storage.

## 3. Produce canonical content

Build canonical Learning Units under Architecture v3.1.5 / semantic contract 3.1.3. Preserve source facts and distinguish them from externally verified enrichment.

External lexicons may verify/enrich morphology, sense, translation, Rektion, collocations and lexical relations, but may not silently replace the source inventory.

The source-canonical profile remains the Stage 1/2 authority. Do not mutate it merely to make post-enrichment product data validate; when structural post-enrichment cardinality differs, use an explicitly named validator overlay while keeping the product floor as a separate authority.

## 4. Evidence/cache model

- Cache external responses by normalized lemma/construction + source + access/version key.
- Retry only failed/missing/stale units with backoff.
- Never rerun a full-source web retrieval merely because a subset failed.
- Keep raw evidence separate from canonical learner-facing content.
- Legacy enrichment, historical mappings, NVV fields, or previous card datasets remain disabled unless the user explicitly requests a named recovery workflow.
- Evidence cache progress must be persisted through the Git-backed workspace rules in §2A; a long-running full-source enrichment that can lose all successful cache progress on timeout is a pipeline defect and must be repaired before blind refetch.

## 5. Quality before density

Run lexical-quality validation before interpreting coverage numbers.

- Do not create content to satisfy a count.
- Example-derived phrases are not collocations.
- Collocations must be atomic, evidence-backed and sense-aligned.
- Synonyms/antonyms require sense-bound evidence; otherwise omit them.
- Explicit valency notation in the learner headword requires explicit Rektion; do not guess ambiguous two-way-preposition case.
- Source sense markers such as `[1]`, `[1a]` and `[2b]` are evidence locators, not learner-facing content.
- Real evidence-backed multi-value fields remain arrays and must not be flattened merely for transport/UI convenience.

Preferred lexical coverage gaps are reported numerically and do not authorize fabrication. Hard product-floor requirements are separate learner-product gates; if they cannot be met with acceptable evidence/content, the stage fails or is blocked rather than inventing data.

## 6. Delivery and runtime

Resolve the current intended Flashcards Pro runtime from `hosseinmehdizade-tech/German-Flashcards-Pro/main` at delivery time. No version number in this runbook is a permanent target.

Before Final, execute the actual target importer and Presentation Model on the exact committed delivery artifact and prove:

- every row/card imports;
- no invalid or duplicate IDs;
- learner-facing fields have runtime-compatible shapes;
- the canonical payload round-trips without semantic loss;
- required rich-card definitions/examples/morphology survive import;
- primary reviewed example translations survive and learner-visible DE/FA/EN behavior is correct where applicable;
- synonyms, antonyms, Rektion and collocations remain separate multi-value items;
- representative verb/phrase cards actually render the required richness;
- relevant Study/Quick/Writing/Audio practice projections remain valid;
- raw JSON is not exposed to the learner UI;
- the imported canonical artifact independently passes the mandatory product floor.

A transport/import PASS cannot rescue a thin-card product failure. If the target runtime cannot be executed or equivalently pinned, Stage 6 is `BLOCKED` and the artifact must not be called Final.

Runtime acceptance artifacts and the exact target runtime commit SHA must be committed to the persistent workspace before Stage 6 may be `PASS`.

## 7. Required seven-stage gate order

1. **Source & Inventory** — source inventory QA + stable IDs
2. **Canonicalization** — canonical construction + Architecture/Contract validation
3. **Evidence & Enrichment** — incremental evidence cache + evidence-linked enrichment + rich-card preflight
4. **Linguistic & Lexical QA** — enriched-canonical structural validation + linguistic audit + lexical quality + coverage + mandatory product floor
5. **Delivery Projection** — Universal v2/selected transport + delivery/loss/array validation
6. **Runtime & Presentation Acceptance** — current target importer/persistence + lossless canonical roundtrip + Presentation Model/practice + rendered product acceptance + imported product floor
7. **Release & Post-Package Verification** — packaging + manifest/hash + independent reopen/re-hash/re-parse verification

A hard-gate failure triggers repair and rerun of the affected stage plus every downstream stage invalidated by the change. Do not restart valid upstream PASS stages without evidence they are invalid. Do not stop every N cards or after every stage to ask the user to say continue.

The detailed stage inputs/outputs/gates are normative in `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`.

## 8. Final deliverables

A completed source run should deliver, at minimum:

- canonical JSON;
- Flashcards Pro Universal TSV (when that is the selected transport);
- source inventory / identity map;
- evidence index/cache or immutable evidence locators;
- enriched-canonical / linguistic / lexical-quality reports;
- completeness/coverage + rich-card product-floor report;
- delivery validation + loss check;
- runtime acceptance report;
- Presentation Model + representative product-presentation acceptance report;
- imported-product-floor result;
- final status + manifest/hash evidence;
- internal and independent post-package verification;
- final package ZIP;
- direct TSV separately for normal Flashcards Pro import;
- `CHECKPOINT.json` showing all seven stages as durable `PASS`, with the establishing Git commit SHA and authoritative evidence paths.

Only call the package `Final` when every applicable hard gate actually executed and passed and Stage 7 is durably committed to Git.
