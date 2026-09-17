# German Content Production Kit v3.1.12

> **MANDATORY FIRST STEP FOR EVERY NEW CHAT:** read `PROJECT-BOOTSTRAP.md` first, then `PROJECT-OPERATING-MODE-v2.md`.

```text
Start here:
PROJECT-BOOTSTRAP.md
PROJECT-OPERATING-MODE-v2.md
PROJECT-STATE.json
Prompt/START-PROMPT-v3.1.12.md
```

v3.1.12 remains the active production overlay. Architecture v3.1.5 and semantic contract 3.1.3 are unchanged. The active execution model is now **artifact-first / async Git**: the seven-stage production lifecycle remains normative, but live GitHub synchronization is no longer on the critical path of ordinary work.

## Cross-chat startup protocol

Before substantial project work, resolve the newest verified state quickly: explicit newer current-chat artifact first, then a verified portable checkpoint/state bundle from Project Sources/current files/Library, then GitHub only as needed for ambiguity resolution or durability sync. Read `PROJECT-BOOTSTRAP.md`, `PROJECT-OPERATING-MODE-v2.md`, `PROJECT-STATE.json`, this README, the active START-PROMPT and the relevant source/workstream checkpoint rules. Inspect `German-Flashcards-Pro` only when runtime/import/presentation compatibility actually matters.

GitHub is the durable asynchronous coordination/mirror layer, not the execution engine and not the default binary transport. Generated ZIPs/checkpoint packages should not be reconstructed through Base64 chunk commits or GitHub Actions merely for persistence. Store their exact filename/hash/manifest metadata in Git when useful and keep the actual package in Project/Library/user-delivery surfaces.

## Active authority map

- Mandatory cross-chat bootstrap: `PROJECT-BOOTSTRAP.md`
- Active operating model: `PROJECT-OPERATING-MODE-v2.md`
- Cross-chat registry: `PROJECT-STATE.json`
- Active entrypoint: `Prompt/START-PROMPT-v3.1.12.md`
- Active overlay: `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.12.md`
- Seven-stage production authority: `Prompt/SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`
- New-source/resume runbook: `Prompt/NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md`
- Source/workstream checkpoints: `Workspaces/<source-slug>/CHECKPOINT.json`
- Generic new-source rich-card policy: `Prompt/GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`
- Menschen A1-specific policy: `Prompt/MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`
- Architecture package: v3.1.5
- Semantic contract: `gfp-german-language-content@3.1.3`
- Universal transport authority: `Architecture/01-CORE/FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md`
- Active lexical-quality validator: `Verification/validate_lexical_quality_v1_0_1.py`

Do not use `MENSCHEN-A1-*` product profiles as defaults for another book/level. A new source without a dedicated profile starts from the generic rich-card policy and keeps its own source identity.

## v3.1.12 production rules

- Every source uses the seven-stage lifecycle: Source & Inventory → Canonicalization → Evidence & Enrichment → Linguistic & Lexical QA → Delivery Projection → Runtime & Presentation Acceptance → Release & Post-Package Verification.
- Allowed quality states are `NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`.
- **Quality state and Git persistence state are separate.** A stage may be locally/portably verified as PASS when its artifacts and gate evidence are complete and hash-bound. Track Git separately as `IN_SYNC`, `PENDING`, `FAILED` or `NOT_REQUIRED`.
- Do not call a result **Git-backed PASS/FINAL/VERIFIED** unless the required Git synchronization actually completed.
- Chat history alone is not a durable checkpoint. A self-verifying portable state bundle in Project/Library/current delivery is a valid resume authority when its manifest/hash and checkpoint are intact.
- If Git persistence is unavailable or unhealthy, continue ordinary safe source work from the newest verified authority. Make at most one Git repair/sync attempt in a normal production turn unless the user explicitly asks for Git repair.
- GitHub writes happen at meaningful batch/milestone boundaries, not per card or per small step.
- Do not use GitHub Actions/Base64 chunking to materialize generated release/checkpoint ZIPs merely for persistence.
- Preserve valid upstream PASS stages; when an authoritative upstream artifact changes, invalidate only affected downstream stages.
- Quality outranks field density. Never fabricate learner content or evidence to satisfy a count.
- Example-derived phrases are not collocations.
- Included collocations must be atomic, sense-aligned and explicitly evidence-backed.
- Synonym/antonym content is omitted when evidence cannot be bound to the selected sense.
- Explicit valency notation in a learner headword requires explicit Rektion with evidence.
- External source retrieval is cached and incremental. Retry only failed/missing/stale units; repeated full-dataset refetch without invalidation is a pipeline defect.
- Legacy enrichment, old NVV fields, historical mappings and previous enriched datasets are disabled unless the user explicitly opts into a named recovery workflow.
- Final delivery requires target runtime/import + Presentation acceptance on the exact projected artifact. Parse/transport-only PASS is not Final.
- Resolve the current intended Flashcards Pro runtime at delivery time, not on every content turn. Historical verified baselines are not permanent hardcoded targets.
- Execute agentically through Stage 7. Do not stop every N cards or between stages for manual continuation.
- Grammar, Vocabulary, Lesen, Schreiben and app runtime may advance in parallel, each with its own checkpoint/state bundle.
- The project is a side project: avoid repeated routine confirmations; surface only real blockers or decisions that materially affect scope, data loss, architecture or visible UX.

## Seven-stage execution

1. **Source & Inventory** — source authority, classification, stable IDs, inventory QA.
2. **Canonicalization** — semantic Learning Units, duplicate/construction resolution, Architecture/Contract validation.
3. **Evidence & Enrichment** — incremental evidence cache and evidence-linked enrichment.
4. **Linguistic & Lexical QA** — linguistic audit, lexical-quality validation, marker/array integrity, coverage reporting.
5. **Delivery Projection** — Universal v2/selected transport, parity/loss validation.
6. **Runtime & Presentation Acceptance** — current version-pinned Flashcards Pro importer, roundtrip, Presentation and relevant practice acceptance.
7. **Release & Post-Package Verification** — direct TSV + canonical JSON + reports + ZIP + manifest/SHA-256 + independent verification.

Expected final handoff includes the direct import TSV separately, canonical JSON, source inventory/stable-ID evidence, QA/coverage reports, runtime/presentation evidence, manifest/hash evidence, package ZIP and a portable final checkpoint/state bundle. Git synchronization is strongly preferred at meaningful boundaries but is tracked separately from package quality.

## Version/provenance note

The root `PRODUCTION-KIT-MANIFEST.json` and older full-package audit artifacts remain historical baseline evidence and must not be misrepresented as a newly regenerated full v3.1.12 package manifest. v3.1.12 remains a production orchestration overlay; Architecture v3.1.5 is not rewritten.

See `Prompt/CHANGELOG-v3.1.12.md` for the current changes.
