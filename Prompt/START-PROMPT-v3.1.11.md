# START PROMPT v3.1.11

Use `CONTENT-GENERATION-MASTER-PROMPT-v3.1.11.md` as the current production overlay and `NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md` whenever a new book/source is supplied.

Mandatory priorities:

1. Preserve Architecture v3.1.5 / semantic contract 3.1.3 unless an explicit architecture change is requested.
2. Resolve the new source/book, level, unit boundaries, learning-unit types, source profile and current target runtime before generation. Never reuse a source-specific profile from another dataset merely because the card type is similar.
3. Treat the user-provided source as authoritative for inventory, source spelling, lesson/chapter placement and source lineage. External dictionaries verify/enrich; they do not silently replace the source inventory.
4. Do not use legacy enrichment, old NVV fields, historical mappings, or previous enriched card sets unless the user explicitly opts into a named recovery workflow.
5. Never create collocations, synonyms, antonyms, Rektion, provenance, or source locators to satisfy a numeric target.
6. Treat collocation count as preferred coverage; treat every included collocation as a hard lexical-quality claim. Example-derived phrases are not collocations.
7. Require sense alignment and atomic learner-facing text before accepting source-derived lexical relations. If sense-bound synonym/antonym evidence is unavailable, omit the relation and report coverage.
8. Source/dictionary sense markers such as `[1]`, `[1a]`, `[2b]` are evidence locators only. They may remain in provenance/source-location metadata but must never be copied into learner-facing synonym, antonym, collocation, Rektion, example, definition, or delivery text.
9. If a headword explicitly encodes valency, emit explicit Rektion with evidence; do not guess ambiguous two-way-preposition case.
10. Inventory the source once, establish stable canonical IDs, cache external source responses, and retry only missing/stale/failed units with backoff. A repeated full-source refetch is a pipeline defect.
11. For a new source with no dedicated completeness profile, use `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json` as the default quality/coverage policy. `MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json` applies only to Menschen A1.
12. Resolve the intended Flashcards Pro runtime at delivery time. v354 is the current verified baseline, but do not keep using v354 if the target application has advanced.
13. Universal v2 TSV is literal tab-separated transport, not RFC4180 CSV. JSON-valued cells (`examples`, `related`, `opposites`, `details`, `custom_fields`) must contain raw JSON between tab delimiters and must not be CSV-quoted/double-quoted by a CSV writer. Top-level `related`/`opposites` must exactly match canonical `details.synonyms`/`details.antonyms`.
14. Before `Final`, execute canonical/architecture validation, linguistic audit, lexical-quality validation with `Verification/validate_lexical_quality_v1_0_1.py`, product coverage/completeness reporting, delivery projection, version-pinned target runtime/import+presentation acceptance, packaging, and post-package hash verification.
15. A file that merely parses, or a transport-only PASS, is not a runtime-verified release.
16. Continue agentically through all applicable stages without arbitrary batch stops. Stop only for a real evidence/tooling blocker, report exactly what is blocked, and preserve completed checkpoints so the run can resume without repeating finished work.
17. Final delivery must include the direct import TSV separately in addition to the archive/package and QA reports.

Current source-specific profile for Menschen A1: `MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`.
Generic policy for subsequent sources: `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`.
Active lexical/transport hardening validator: `Verification/validate_lexical_quality_v1_0_1.py`.
