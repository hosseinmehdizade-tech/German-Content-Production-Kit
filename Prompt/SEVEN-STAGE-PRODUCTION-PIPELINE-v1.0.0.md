# Seven-Stage Production Pipeline v1.0.0

Status: ACTIVE
Scope: all current and future content sources/datasets handled by German-Content-Production-Kit.

This pipeline is the human-trackable production model. Execution remains agentic and end-to-end: the agent must continue through all applicable stages without asking the user to manually approve every stage. The seven stages exist to make progress, recovery, invalidation and QA explicit.

> Persistence model: `PROJECT-OPERATING-MODE-v2.md` — artifact-first, async Git. Quality gates and Git synchronization are separate dimensions.

## Allowed stage states

Every stage MUST use exactly one of these quality states:

- `NOT_STARTED`
- `RUNNING`
- `PASS`
- `FAIL`
- `BLOCKED`
- `INVALIDATED`

`PASS` is allowed when the stage's authoritative outputs and gate evidence exist in a self-verifying portable state/checkpoint bundle and the required hashes/validation evidence pass. Git persistence is tracked separately as `IN_SYNC`, `PENDING`, `FAILED`, or `NOT_REQUIRED`.

Do not call a stage **Git-backed PASS** unless its required compact checkpoint/metadata has actually been synchronized to Git.

## Stage 1 — Source & Inventory

Purpose: freeze the authoritative source interpretation before enrichment.

Required work:
- source intake and source identity;
- source file/image inventory and source lineage;
- row/item classification;
- duplicate/malformed/construction candidate identification;
- stable canonical IDs;
- source order / lesson / chapter placement when present;
- source inventory QA.

Required outputs:
- `01-inventory/SOURCE-INVENTORY.json`
- `01-inventory/STABLE-ID-MAP.json`
- `01-inventory/INVENTORY-QA.json`
- source hashes/locators under `00-source/` when applicable.

Stage gate: inventory is internally consistent, source-authoritative, stable IDs are unique, and outputs are included in or referenced by the portable state bundle with hashes.

## Stage 2 — Canonicalization

Purpose: convert the frozen inventory into semantic canonical Learning Units without relying on legacy enriched outputs.

Required work:
- resolve lemma vs reflexive/fixed/prepositional construction vs sense vs collocation vs malformed row;
- consolidate true duplicates without silently merging distinct senses;
- populate source-supported canonical facts;
- preserve source lineage and stable identities;
- run Architecture / semantic-contract validation.

Required outputs:
- `02-canonical/CANONICAL.json`
- `02-canonical/CANONICAL-VALIDATION.json`
- `02-canonical/NORMALIZATION-DECISIONS.json` when nontrivial consolidation occurred.

Stage gate: canonical data passes current Architecture/Contract validation and is hash-bound before downstream enrichment changes it.

## Stage 3 — Evidence & Enrichment

Purpose: verify and enrich canonical units with external evidence without replacing the source inventory.

Required work:
- incremental evidence retrieval/cache;
- morphology, translations, definitions, Rektion, collocations and relations only when evidence supports them;
- sense alignment;
- no fabrication for density;
- no example-derived phrase promoted to collocation;
- preserve raw evidence separately from learner-facing canonical content.

Required outputs:
- `03-evidence/EVIDENCE-INDEX.json`
- cached evidence artifacts or immutable locators/hashes;
- `02-canonical/CANONICAL-ENRICHED.json` or equivalent authoritative enriched canonical artifact.

Stage gate: all included enrichment claims are evidence-linked; failed/missing units are explicitly recorded; successful cache entries are preserved in the portable state so they are not re-fetched unnecessarily.

## Stage 4 — Linguistic & Lexical QA

Purpose: prove learner-facing linguistic quality before transport projection.

Required work:
- linguistic audit;
- lexical-quality validation;
- sense alignment checks;
- source-marker leakage checks;
- array/multi-value integrity;
- product completeness/coverage reporting;
- repair loop for affected units only.

Required outputs:
- `04-qa/LINGUISTIC-QA.json`
- `04-qa/LEXICAL-QUALITY.json`
- `04-qa/COVERAGE-REPORT.json`
- corrected authoritative canonical artifact when repairs were required.

Stage gate: all hard linguistic/lexical checks PASS. Preferred coverage gaps may remain and must be reported rather than fabricated.

## Stage 5 — Delivery Projection

Purpose: project canonical content losslessly into the selected Flashcards Pro delivery transport.

Required work:
- Universal v2 or explicitly selected delivery mapping;
- preserve canonical payload and semantic types;
- raw JSON cells between literal TSV tabs where required;
- top-level related/opposites parity with canonical arrays;
- delivery validation and loss checks.

Required outputs:
- `05-delivery/<dataset>-UNIVERSAL-v2.tsv`
- `05-delivery/DELIVERY-VALIDATION.json`
- projection metadata/hashes.

Stage gate: transport validates without semantic loss and authoritative delivery artifacts are hash-bound in the portable state bundle.

## Stage 6 — Runtime & Presentation Acceptance

Purpose: prove the exact projected artifact works against the intended current Flashcards Pro runtime.

Required work:
- resolve/pin target Flashcards Pro artifact/version when Stage 6 is actually reached;
- importer acceptance;
- duplicate/ID/runtime-shape checks;
- canonical roundtrip/losslessness;
- Presentation Model acceptance;
- DE/FA/EN example grouping as applicable;
- arrays displayed as separate learner-facing items;
- no raw JSON leakage;
- relevant practice-mode checks.

Required outputs:
- `06-runtime/RUNTIME-ACCEPTANCE.json`
- `06-runtime/PRESENTATION-ACCEPTANCE.json`
- runtime target identity + input artifact SHA-256.

Stage gate: every applicable runtime and presentation hard gate PASS against the exact projected artifact. If execution is impossible, state is `BLOCKED`, never `PASS`.

## Stage 7 — Release & Post-Package Verification

Purpose: produce the final reproducible handoff only after all upstream hard gates PASS.

Required work:
- assemble direct import TSV, canonical JSON and QA/runtime evidence;
- build ZIP/package;
- generate manifest and SHA-256;
- independently re-open/re-hash/re-verify packaged contents;
- record final quality status and persistence status separately.

Required outputs:
- `07-release/FINAL-STATUS.json`
- `07-release/BUILD-METADATA.json`
- `07-release/MANIFEST.json`
- `07-release/SHA256SUMS.txt`
- final package or immutable portable artifact locator/hash;
- direct import TSV remains separately accessible.

Stage gate: package and independent post-package verification PASS and the final portable state bundle is complete. Git synchronization is a separate durability step; do not call it **Git-backed Final** until that sync succeeds.

## Invalidation / repair rules

- A failed stage is repaired in place; do not restart earlier PASS stages without evidence they are invalid.
- When an upstream authoritative artifact changes, mark every dependent downstream stage `INVALIDATED`.
- Rerun the changed stage and all invalidated downstream gates.
- Preserve valid upstream checkpoints.
- External evidence retrieval is incremental; never refetch the full source merely because a subset failed.

Typical dependency chain:

`1 → 2 → 3 → 4 → 5 → 6 → 7`

## Agentic execution rule

The agent MUST continue automatically from the newest verified checkpoint through Stage 7 unless:
- a hard gate fails and requires repair;
- a real evidence/tooling/access blocker prevents continuation.

Git persistence failure alone is not a production blocker. Record `persistence.git=PENDING` or `FAILED`, preserve exact hashes/resume instructions, and continue safe work. In a normal production turn, make at most one Git recovery/sync attempt unless the user explicitly asks for Git repair.

Do not stop every 10/20 cards or after each stage to ask the user to say “continue”.

## CHECKPOINT.json minimum stage model

Every source workspace must expose a seven-stage summary with:
- stage number + name;
- quality state;
- authoritative output paths/portable artifact refs;
- gate evidence paths;
- artifact hashes;
- blockers/failures;
- invalidated downstream stages when applicable;
- exact resume instruction;
- separate persistence state, including Git sync status when Git is used.

A Git commit SHA is useful durability metadata when available, but it is no longer required to resume ordinary work from a verified portable checkpoint.
