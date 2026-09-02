# START PROMPT v3.1.12

Use `CONTENT-GENERATION-MASTER-PROMPT-v3.1.12.md` as the current production overlay.
For every new or resumed source, also use:

- `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`
- `NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md`

Mandatory priorities:

1. Preserve Architecture v3.1.5 / semantic contract 3.1.3 unless an explicit architecture change is requested.
2. The seven-stage production pipeline is normative for every current and future content source. Do not replace it with an ad-hoc sequence of chat updates.
3. Every production source MUST have a Git-backed workspace under `Workspaces/<source-slug>/` (or an explicitly designated equivalent) and a `CHECKPOINT.json`.
4. Stage states are exactly: `NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`.
5. A stage may be marked `PASS` only after its authoritative artifacts and gate evidence are committed to the configured Git branch and recorded in `CHECKPOINT.json`. Chat history, `/mnt/data`, local Codex state and temporary ZIPs are not durable checkpoints.
6. If Git persistence is unavailable, use `PERSISTENCE_BLOCKED`; never represent local-only work as `PASS`, `DONE`, `FINAL`, or `VERIFIED`.
7. At the beginning of every resumed session, inspect the current `main` state and the source `CHECKPOINT.json`. Resume from the last durable checkpoint; do not rebuild completed stages from chat memory.
8. Treat the user-provided source as authoritative for inventory, spelling, lesson/chapter placement and source lineage. External dictionaries verify/enrich; they do not silently replace the source inventory.
9. Resolve source/book, level, unit boundaries, learning-unit types, source profile and the current intended Flashcards Pro runtime before generation. Never reuse a source-specific profile from another dataset merely because the card type is similar.
10. Do not use legacy enrichment, old NVV fields, historical mappings or previous enriched card sets unless the user explicitly opts into a named recovery workflow.
11. Never create collocations, synonyms, antonyms, Rektion, provenance or source locators merely to satisfy a numeric target.
12. Collocation count is preferred coverage; every included collocation is a hard lexical-quality claim. Example-derived phrases are not collocations.
13. Require sense alignment and atomic learner-facing text before accepting lexical relations. If sense-bound synonym/antonym evidence is unavailable, omit the relation and report coverage.
14. Source/dictionary sense markers such as `[1]`, `[1a]`, `[2b]` are evidence locators only. Remove the marker from learner-facing text while preserving the lexical item and provenance locator according to `SOURCE-SENSE-MARKER-NORMALIZATION-v1.0.0.md`.
15. If a learner headword explicitly encodes valency, emit explicit Rektion with evidence; do not guess ambiguous two-way-preposition case.
16. Inventory the source once, establish stable canonical IDs, cache external source responses, and retry only missing/stale/failed units. Repeated full-source refetch without cause is a pipeline defect.
17. For a new source with no dedicated completeness profile, use `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`. `MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json` applies only to Menschen A1.
18. Resolve the intended Flashcards Pro runtime from `hosseinmehdizade-tech/German-Flashcards-Pro/main` at delivery time. v354 is only the current verified baseline at the time of this prompt revision, not a permanent target.
19. Universal v2 TSV is literal tab-separated transport, not RFC4180 CSV. JSON-valued cells (`examples`, `related`, `opposites`, `details`, `custom_fields`) contain raw JSON between tab delimiters. Top-level `related`/`opposites` must match canonical `details.synonyms`/`details.antonyms` exactly.
20. Execute the seven stages agentically and end-to-end without arbitrary batch stops:
   1. Source & Inventory
   2. Canonicalization
   3. Evidence & Enrichment
   4. Linguistic & Lexical QA
   5. Delivery Projection
   6. Runtime & Presentation Acceptance
   7. Release & Post-Package Verification
21. On an upstream authoritative change, mark dependent downstream stages `INVALIDATED` and rerun only the affected stage and its downstream dependents. Preserve valid upstream `PASS` checkpoints.
22. Before `Final`, all applicable hard gates in Stages 1–7 must actually execute and PASS, including target importer/presentation acceptance and independent post-package verification.
23. A file that merely parses, or a transport-only PASS, is not a runtime-verified release.
24. Continue agentically through Stage 7. Stop only for a real evidence/tooling/access blocker; record the blocker and exact resume instruction in Git-backed `CHECKPOINT.json`.
25. Final delivery must include the direct import TSV separately, canonical JSON, QA/coverage reports, runtime/presentation evidence, manifest/hash evidence, package ZIP, and the final durable checkpoint.

Current source-specific profile for Menschen A1: `MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`.
Generic policy for subsequent sources: `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`.
Active lexical/transport hardening validator: `Verification/validate_lexical_quality_v1_0_1.py`.
