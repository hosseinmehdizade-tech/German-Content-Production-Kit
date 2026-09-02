# German Content Production Kit v3.1.12

```text
Start here:
Prompt/START-PROMPT-v3.1.12.md
```

v3.1.12 is the active production overlay. It keeps the v3.1.11 lexical-quality/runtime hardening and makes the seven-stage Git-backed production lifecycle normative for all current and future sources. Architecture v3.1.5 and semantic contract 3.1.3 are unchanged.

## Active authority map

- Active entrypoint: `Prompt/START-PROMPT-v3.1.12.md`
- Active overlay: `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.12.md`
- Seven-stage production authority: `Prompt/SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`
- New-source/resume runbook: `Prompt/NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md`
- Persistent source workspaces: `Workspaces/<source-slug>/CHECKPOINT.json`
- Generic new-source rich-card policy: `Prompt/GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`
- Menschen A1-specific policy: `Prompt/MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`
- Base lexical-quality overlay: `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.11.md`
- Architecture package: v3.1.5
- Semantic contract: `gfp-german-language-content@3.1.3`
- Universal transport authority: `Architecture/01-CORE/FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md`
- Active lexical-quality validator: `Verification/validate_lexical_quality_v1_0_1.py`

Do not use `MENSCHEN-A1-*` product profiles as defaults for another book/level. A new source without a dedicated profile starts from the generic rich-card policy and keeps its own source identity.

## v3.1.12 production rules

- Every source uses the mandatory seven-stage lifecycle: Source & Inventory → Canonicalization → Evidence & Enrichment → Linguistic & Lexical QA → Delivery Projection → Runtime & Presentation Acceptance → Release & Post-Package Verification.
- Allowed stage states are `NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`.
- `PASS` requires authoritative artifacts + gate evidence committed to Git and recorded in the source `CHECKPOINT.json`.
- Chat history, `/mnt/data`, local Codex workspaces and temporary ZIPs are not durable checkpoints.
- If Git persistence is unavailable, use `PERSISTENCE_BLOCKED`; local-only work is never Final.
- At every resumed session, inspect current `main`, the active prompts, the source checkpoint, and current `German-Flashcards-Pro/main` before continuing.
- Preserve valid upstream PASS stages; when an authoritative upstream artifact changes, mark dependent downstream stages `INVALIDATED` and rerun only affected work.
- Quality outranks field density. Never fabricate learner content or evidence to satisfy a count.
- Example-derived phrases are not collocations.
- Included collocations must be atomic, sense-aligned and explicitly evidence-backed.
- Synonym/antonym content is omitted when evidence cannot be bound to the selected sense.
- Explicit valency notation in a learner headword requires explicit Rektion with evidence.
- External source retrieval is cached and incremental. Retry only failed/missing/stale units; repeated full-dataset refetch without invalidation is a pipeline defect.
- Legacy enrichment, old NVV fields, historical mappings and previous enriched datasets are disabled unless the user explicitly opts into a named recovery workflow.
- Final delivery requires target runtime/import + Presentation acceptance on the exact projected artifact. Parse/transport-only PASS is not Final.
- Resolve the current intended Flashcards Pro runtime at delivery time. v354 is the verified baseline when v3.1.12 was introduced, not a permanent hardcoded target.
- Execute agentically through Stage 7. Do not stop every N cards or between stages for manual continuation.

## Seven-stage execution

1. **Source & Inventory** — source authority, classification, stable IDs, inventory QA.
2. **Canonicalization** — semantic Learning Units, duplicate/construction resolution, Architecture/Contract validation.
3. **Evidence & Enrichment** — incremental evidence cache and evidence-linked enrichment.
4. **Linguistic & Lexical QA** — linguistic audit, lexical-quality validation, marker/array integrity, coverage reporting.
5. **Delivery Projection** — Universal v2/selected transport, parity/loss validation.
6. **Runtime & Presentation Acceptance** — current version-pinned Flashcards Pro importer, roundtrip, Presentation and relevant practice acceptance.
7. **Release & Post-Package Verification** — direct TSV + canonical JSON + reports + ZIP + manifest/SHA-256 + independent verification.

Expected final handoff includes the direct import TSV separately, canonical JSON, source inventory/stable-ID evidence, QA/coverage reports, runtime/presentation evidence, manifest/hash evidence, package ZIP and final Git-backed checkpoint.

## Version/provenance note

The root `PRODUCTION-KIT-MANIFEST.json` and older full-package audit artifacts remain historical baseline evidence and must not be misrepresented as a newly regenerated full v3.1.12 package manifest. v3.1.12 is a production orchestration/persistence overlay; Architecture v3.1.5 is not rewritten.

See `Prompt/CHANGELOG-v3.1.12.md` for the current changes.
