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

## 3. Produce canonical content

Build canonical Learning Units under Architecture v3.1.5 / semantic contract 3.1.3. Preserve source facts and distinguish them from externally verified enrichment.

External lexicons may verify/enrich morphology, sense, translation, Rektion, collocations and lexical relations, but may not silently replace the source inventory.

## 4. Evidence/cache model

- Cache external responses by normalized lemma/construction + source + access/version key.
- Retry only failed/missing/stale units with backoff.
- Never rerun a full-source web retrieval merely because a subset failed.
- Keep raw evidence separate from canonical learner-facing content.
- Legacy enrichment, historical mappings, NVV fields, or previous card datasets remain disabled unless the user explicitly requests a named recovery workflow.

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
- direct TSV separately for normal Flashcards Pro import.

Only call the package `Final` when every applicable hard gate actually executed and passed.
