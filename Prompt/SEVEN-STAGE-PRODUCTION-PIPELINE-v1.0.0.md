# Seven-Stage Production Pipeline v1.0.0

Status: ACTIVE
Scope: all current and future content sources/datasets handled by German-Content-Production-Kit.

This pipeline is the human-trackable production model. Execution remains agentic and end-to-end: the agent must continue through all applicable stages without asking the user to manually approve every stage. The seven stages exist to make progress, recovery, invalidation and QA explicit.

**Global content/runtime split (2026-11-12; all 21 source families, prospective only):** Stages 1–5 establish the validated source content and content-only projection. Stage 7 has two independently named acceptance scopes: `CONTENT_ONLY` (content package/handoff) and `APP_INTEGRATED` (installed-runtime release). Stage 6 is **app-owned integration acceptance**: it is not an automatic prerequisite for `CONTENT_ONLY` Stage 7, but remains a mandatory PASS for `APP_INTEGRATED` Stage 7 and for any claim of actual native import, IndexedDB persistence, SRS/FSRS safety or app FINAL. A historical accepted content artifact is never retroactively reclassified or rebuilt by this policy change.

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

## Stage 6 — App-owned Runtime & Presentation Acceptance

Purpose: prove real Flashcards Pro app integration and protect existing learner data **without making every content-only project depend on a blocked browser**.

Owner: the central `German-Flashcards-Pro` application/runtime workstream. Source owners provide SHA-bound content and an app-integration handoff, **not 21 repeated browser retries**. Source workstream Stage 6 is a reference to app-owned evidence, not another per-source mandatory execution loop.

Required work **when claiming installed-app/native release**:
- resolve/pin the exact CURRENT Flashcards Pro artifact/version, importer/schema and the exact content SHA-256;
- real importer acceptance, duplicate and stable-ID preservation, canonical roundtrip/losslessness;
- reload/persistence in the actual app origin (IndexedDB), plus pre/post import user-state backup, SRS/FSRS continuity and rollback safety;
- Presentation Model acceptance: DE/FA/EN grouping where applicable, arrays as individual items, no raw JSON leakage, relevant practice modes;
- document the test environment and the exact app/content/feature fingerprint.

Required app-owned outputs only if executed:
- `06-runtime/RUNTIME-ACCEPTANCE.json`
- `06-runtime/PRESENTATION-ACCEPTANCE.json`
- runtime target identity, input SHA-256, real browser/import/reload/SRS evidence and explicit outcome.

**Blocked-environment anti-loop:** if browser access returns `ERR_BLOCKED_BY_ADMINISTRATOR` or the equivalent environment limitation, record one evidence-bound `BLOCKED` observation (app SHA, content SHA, environment identity, attempted capability and exact reason). Do **not** reattempt the same blocked browser test in the same environment with unchanged permissions, app/runtime and relevant importer/format conditions. Resume the test only after a documented execution-capability change, an authorized reachable browser, or a materially affected new app/importer/content version **with a runnable environment**. Do not invent browser artifacts or convert synthetic/parser QA into native PASS.

**Stage gate:** `APP_INTEGRATED` requires applicable real runtime and presentation hard gates `PASS` against the exact source and CURRENT app. If execution is impossible, Stage 6 is `BLOCKED` (a hold/deferred **reason**, not a new `PASS` or quality-state enum). This does **not** invalidate previously verified Stages 1–5 and does **not** block `CONTENT_ONLY` Stage 7.

## Stage 7 — Scoped Release & Post-Package Verification

Purpose: produce a reproducible handoff **with an explicit release scope**; do not treat content delivery and installed-app release as equivalent.

Required work for `CONTENT_ONLY`:
- require the applicable verified content stages (including Stage4 linguistic QA and Stage5 exact validated projection) and source-owned identity, delta/lineage, rights and recovery evidence;
- assemble direct import TSV, canonical JSON and source/QA/checkpoint evidence **without bundling the app**; build a package only when a new authorized content delivery is actually requested;
- generate manifest and SHA-256; independently re-open/re-hash/verify the exact delivery bytes and unchanged accepted stable IDs;
- report Stage6 status separately: `BLOCKED` / not independently executed must be explicit, **never** represented as runtime compatible, native installed acceptance or full app FINAL.

Additional requirements for `APP_INTEGRATED`:
- exact app owner/runtime Stage6 real native `PASS` receipt, including import/IndexedDB reload/SRS/FSRS safeguards and target app version/source hashes;
- trusted app-side final release approval and independent post-package/runtime verification; if Stage6 is blocked, `APP_INTEGRATED` stays `BLOCKED`, even when `CONTENT_ONLY` is accepted.

Required outputs for an actually produced content handoff:
- `07-release/FINAL-STATUS.json` with `release_scope=CONTENT_ONLY` or `release_scope=APP_INTEGRATED`, source and runtime evidence identities and separate states;
- `07-release/BUILD-METADATA.json`
- `07-release/MANIFEST.json`
- `07-release/SHA256SUMS.txt`
- final package or immutable portable artifact locator/hash; direct import TSV separately accessible.

Stage gate: `CONTENT_ONLY` may `PASS` with verified source/linguistic/projection/package QA even while Stage6 is `BLOCKED`; its FULL APP status must remain `NOT_VERIFIED` / `BLOCKED`. `APP_INTEGRATED` can `PASS` only after exact applicable Stage6 `PASS` and app-owner release acceptance. Git persistence is tracked separately; no Git-backed final claim without actual synchronization.

## Invalidation / repair rules

- A failed stage is repaired in place; do not restart earlier PASS stages without evidence they are invalid.
- When an upstream authoritative artifact changes, mark every dependent downstream stage `INVALIDATED`.
- Rerun the changed stage and all invalidated downstream gates.
- Preserve valid upstream checkpoints.
- External evidence retrieval is incremental; never refetch the full source merely because a subset failed.

Dependency chains by release scope:

- `CONTENT_ONLY: 1 → 2 → 3 → 4 → 5 → 7 (content handoff)` — Stage6 status recorded independently, not a release prerequisite.
- `APP_INTEGRATED: 1 → 2 → 3 → 4 → 5 → 6 (app owner PASS) → 7 (app FINAL)` — no shortcut around real browser/SRS evidence.

## Agentic execution rule

The agent MUST continue through the applicable `CONTENT_ONLY` production/packaging gates and hand off app-runtime acceptance separately. Stop the applicable route only when:
- a **content** hard gate fails and requires repair;
- its source/output authority cannot be verified;
- a required tool/provider for **that chosen release scope** prevents continuation.

A Stage6 browser `BLOCKED` receipt is an **app-integration blocker only**, not a reason to restart or delay accepted `CONTENT_ONLY` source work. Never repeat a blocked browser action without a new executable environment or material affected version/capability change. Never promote `APP_INTEGRATED` or user-data safety without an actual verified Stage6 receipt.

Git persistence failure alone is not a production blocker. Record `persistence.git=PENDING` or `FAILED`, preserve exact hashes/resume instructions, and continue safe work. In a normal production turn, make at most one Git recovery/sync attempt unless the user explicitly asks for Git repair.

Do not stop every 10/20 cards or after each stage to ask the user to say “continue”.

## CHECKPOINT.json minimum stage model

Every source workspace must expose the seven-stage summary for compatibility, but mark the **independent release scopes** and app-owned Stage6 evidence/reference explicitly. Legacy accepted content-only receipts remain valid at their original scope. Minimum fields:
- stage number + name;
- quality state;
- authoritative output paths/portable artifact refs;
- gate evidence paths;
- artifact hashes;
- blockers/failures;
- invalidated downstream stages when applicable;
- exact resume instruction;
- separate persistence state, including Git sync status when Git is used.
- `release_scope` (content-only versus app-integrated), `content_acceptance`, `app_runtime_acceptance` and a single app-owned blocked-environment receipt reference if relevant; never fake Stage6 PASS.

A Git commit SHA is useful durability metadata when available, but it is no longer required to resume ordinary work from a verified portable checkpoint.
