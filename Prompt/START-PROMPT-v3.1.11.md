# START PROMPT v3.1.11

Use `CONTENT-GENERATION-MASTER-PROMPT-v3.1.11.md` as the current production overlay.

Mandatory priorities:

1. Preserve Architecture v3.1.5 / semantic contract 3.1.3 unless an explicit architecture change is requested.
2. Do not use legacy enrichment, old NVV fields, historical mappings, or previous enriched card sets unless the user explicitly opts into a named recovery workflow.
3. Never create collocations, synonyms, antonyms, Rektion, provenance, or source locators to satisfy a numeric target.
4. Treat collocation count as preferred coverage; treat every included collocation as a hard lexical-quality claim.
5. Require sense alignment and atomic learner-facing text before accepting source-derived lexical relations.
6. If a headword explicitly encodes valency, emit explicit Rektion with evidence.
7. Cache external source responses and retry incrementally; never refetch the full dataset when only a subset failed.
8. Before `Final`, execute lexical-quality validation and the version-pinned target runtime/import acceptance test.
9. A file that merely parses is not a runtime-verified release.
10. Continue agentically through QA/package verification unless a real tooling/evidence blocker prevents execution.

Current Menschen A1 completeness profile: `MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`.
