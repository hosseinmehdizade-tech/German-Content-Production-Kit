# German Content Production Kit v3.1.13

```text
Start here:
Prompt/START-PROMPT-v3.1.13.md
```

v3.1.13 is the active production overlay. It preserves Architecture v3.1.5 / semantic contract 3.1.3 and corrects the thin-card false-pass class by separating source-canonical validation from learner-product completeness.

## Active authority map

- Active entrypoint: `Prompt/START-PROMPT-v3.1.13.md`
- Active overlay: `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.13.md`
- Seven-stage production authority: `Prompt/SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`
- New-source/resume runbook: `Prompt/NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md`
- Persistent source workspaces: `Workspaces/<source-slug>/CHECKPOINT.json`
- Generic lexical/completeness policy: `Prompt/GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`
- Mandatory generic rich-card product floor: `Prompt/GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json`
- Menschen A1-specific policy: `Prompt/MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`
- Architecture package: v3.1.5
- Semantic contract: `gfp-german-language-content@3.1.3`
- Universal transport authority: `Architecture/01-CORE/FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md`
- Current repair lexical-quality validator: `Verification/validate_lexical_quality_v1_0_2.py`
- Rich-card floor validator: `Verification/validate_rich_card_product_floor_v1_0_0.py`

A source-specific canonical profile is Stage 1/2 authority for source identity and canonical shape; it is never, by itself, proof that the Flashcards Pro learner product is complete. For rich-card targets, the product floor is a separate mandatory Stage 3/4/6 authority and may only be tightened or explicitly relaxed by a named user-approved policy.

Do not use `MENSCHEN-A1-*` product profiles as defaults for another book/level. A new source without a dedicated product profile starts from the generic rich-card authorities while preserving its own source identity.

## Production rules

- Every source uses the mandatory seven-stage lifecycle: Source & Inventory → Canonicalization → Evidence & Enrichment → Linguistic & Lexical QA → Delivery Projection → Runtime & Presentation Acceptance → Release & Post-Package Verification.
- Allowed stage states are `NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`.
- `PASS` requires authoritative artifacts + gate evidence committed to Git and recorded in the source `CHECKPOINT.json`.
- Chat history, `/mnt/data`, local Codex workspaces and temporary ZIPs are not durable checkpoints.
- If Git persistence is unavailable, use `PERSISTENCE_BLOCKED`; local-only work is never Final.
- At every resumed session, inspect current `main`, this README/active prompts, the source checkpoint, and current `German-Flashcards-Pro/main` before continuing.
- Preserve valid upstream PASS stages; when an authoritative upstream artifact changes, mark dependent downstream stages `INVALIDATED` and rerun only affected work.
- A rich-card verb dataset may not pass Stage 3 when the external lexical-enrichment path was never attempted. Missing evidence may be reported; a disabled evidence path is not success.
- Quality outranks field density. Never fabricate learner content or evidence to satisfy a count.
- Example-derived phrases are not collocations. Included collocations must be atomic, sense-aligned and evidence-backed.
- Synonym/antonym content is omitted when evidence cannot be bound to the selected sense.
- Explicit valency notation in a learner headword requires explicit Rektion with evidence; do not guess ambiguous two-way-preposition case.
- External source retrieval is cached and incremental. Retry only failed/missing/stale units; repeated full-dataset refetch without invalidation is a pipeline defect.
- Legacy enrichment, old NVV fields, historical mappings and previous enriched datasets are disabled unless the user explicitly opts into a named recovery workflow.
- Stage 4 must run canonical/linguistic/lexical/coverage checks plus the mandatory rich-card product-floor validator.
- Stage 6 must test the exact committed delivery artifact against the current intended Flashcards Pro runtime and prove importer/persistence, canonical roundtrip, Presentation Model behavior, learner-visible rich-card content, separate multi-value items and no raw JSON leakage.
- A parse/transport/import PASS cannot rescue a thin-card product failure.
- Resolve the intended Flashcards Pro runtime from `German-Flashcards-Pro/main` at delivery time; no app version is permanently hardcoded.
- Execute agentically through Stage 7. Do not stop every N cards or between stages for manual continuation.

## Seven-stage execution

1. **Source & Inventory** — source authority, classification, stable IDs, inventory QA.
2. **Canonicalization** — semantic Learning Units, duplicate/construction resolution, Architecture/Contract validation.
3. **Evidence & Enrichment** — incremental evidence cache and evidence-linked rich-card enrichment.
4. **Linguistic & Lexical QA** — structural enriched-canonical validation, linguistic audit, lexical quality, marker/array integrity, coverage and mandatory product floor.
5. **Delivery Projection** — Universal v2/selected transport, parity/loss validation.
6. **Runtime & Presentation Acceptance** — current version-pinned Flashcards Pro importer/persistence, lossless canonical bridge, Presentation and representative rendered-product acceptance.
7. **Release & Post-Package Verification** — direct TSV + canonical JSON + evidence/reports + ZIP + manifest/SHA-256 + independent reopen/re-hash/re-parse verification.

Expected final handoff includes the direct import TSV separately, canonical JSON, source inventory/stable-ID evidence, evidence index/cache, QA/coverage/product-floor reports, runtime/presentation/product-presentation evidence, manifest/hash evidence, package ZIP and final Git-backed checkpoint.

## Version/provenance note

The root `PRODUCTION-KIT-MANIFEST.json` and older full-package audit artifacts remain historical baseline evidence and must not be misrepresented as a newly regenerated v3.1.13 package manifest. v3.1.13 is a production orchestration/product-gate overlay; Architecture v3.1.5 is unchanged.
