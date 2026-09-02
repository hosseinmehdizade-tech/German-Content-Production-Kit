# German Content Production Kit v3.1.11

```text
Start here:
Prompt/START-PROMPT-v3.1.11.md
```

v3.1.11 is the active production overlay. It strengthens v3.1.10 with lexical-quality, source-adaptive agentic execution, incremental/cached enrichment, and version-pinned Flashcards Pro runtime acceptance. Architecture v3.1.5 and semantic contract 3.1.3 are unchanged.

## Active authority map

- Active entrypoint: `Prompt/START-PROMPT-v3.1.11.md`
- Active overlay: `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.11.md`
- New-source runbook: `Prompt/NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md`
- Generic new-source rich-card policy: `Prompt/GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`
- Menschen A1-specific policy: `Prompt/MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`
- Base producer/workflow prompt: `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md`
- Architecture package: v3.1.5
- Semantic contract: `gfp-german-language-content@3.1.3`
- Universal transport authority: `Architecture/01-CORE/FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md`
- Lexical quality validator: `Verification/validate_lexical_quality_v1_0_0.py`

Do not use `MENSCHEN-A1-*` product profiles as defaults for another book/level. A new source without a dedicated profile starts from the generic rich-card policy and keeps its own source identity.

## v3.1.11 production rules

- Quality outranks field density. Never fabricate learner content or evidence to satisfy a count.
- Example-derived phrases are not collocations.
- Included collocations must be atomic, sense-aligned and explicitly evidence-backed.
- Synonym/antonym content is omitted when evidence cannot be bound to the selected sense.
- Explicit valency notation in a learner headword requires explicit Rektion with evidence.
- External source retrieval is cached and incremental. Retry only failed/missing/stale units; repeated full-dataset refetch is considered a pipeline defect.
- Legacy enrichment, old NVV fields, historical mappings and previous enriched datasets are disabled unless the user explicitly opts into a named recovery workflow.
- Final delivery requires actual target runtime/import + presentation acceptance or an exact version-pinned equivalent. Parse/transport-only PASS is not Final.
- Resolve the current intended Flashcards Pro runtime at delivery time. v354 is the current verified baseline for this revision, not a permanent hardcoded target.
- Continue agentically through QA, delivery, runtime acceptance, packaging and post-package verification. Do not stop every N cards.

## New-source execution

When the user supplies a new book/source, follow `Prompt/NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md`:

1. Resolve source/book, level, units/types and target runtime.
2. Freeze source inventory and stable canonical IDs once.
3. Produce canonical content under Architecture v3.1.5 / semantic contract 3.1.3.
4. Cache external evidence and enrich incrementally.
5. Run canonical validation, linguistic audit and lexical-quality validation.
6. Report product coverage without fabricating missing preferred content.
7. Build Universal TSV/selected delivery.
8. Execute target runtime importer/presentation acceptance.
9. Package, hash, independently verify, and only then mark Final.

Expected final handoff includes the direct import TSV separately, canonical JSON, QA reports, runtime evidence, manifest/hash evidence and the package ZIP.

## Version/provenance note

The root `PRODUCTION-KIT-MANIFEST.json` and older full-package audit artifacts remain historical baseline evidence and must not be misrepresented as a newly regenerated full v3.1.11 package manifest. v3.1.11 is a production overlay and QA hardening layer; Architecture v3.1.5 is not rewritten.

See `Prompt/CHANGELOG-v3.1.11.md` for the current changes.
