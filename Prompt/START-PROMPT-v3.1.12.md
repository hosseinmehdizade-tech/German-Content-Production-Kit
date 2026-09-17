# START PROMPT v3.1.12

> **MANDATORY BOOTSTRAP:** Before using this prompt in a new or resumed chat, read root `PROJECT-BOOTSTRAP.md`, `PROJECT-OPERATING-MODE-v2.md` and `PROJECT-STATE.json`. Resolve the newest verified portable workstream state before doing deep Git history inspection. If runtime/import/presentation may be affected, resolve the current Flashcards artifact/state only when that integration step actually matters.

Use `CONTENT-GENERATION-MASTER-PROMPT-v3.1.12.md` as the current production overlay.
For every new or resumed source, also use:

- `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`
- `NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md`

Mandatory priorities:

1. Preserve Architecture v3.1.5 / semantic contract 3.1.3 unless an explicit architecture change is requested.
2. The seven-stage production pipeline is normative for every current and future content source. Do not replace it with an ad-hoc sequence of chat updates.
3. Every production source MUST have a resumable workspace/checkpoint identity under `Workspaces/<source-slug>/` (or an explicitly designated equivalent) plus a portable self-verifying state bundle at meaningful boundaries. GitHub mirrors compact checkpoint/manifest metadata asynchronously; it is not the default binary transport.
4. Quality stage states are exactly: `NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`.
5. Track Git persistence separately as `IN_SYNC`, `PENDING`, `FAILED`, or `NOT_REQUIRED`. A stage may be locally/portably verified as PASS when its authoritative artifacts and gate evidence are complete and hash-bound. Never call it **Git-backed PASS/FINAL/VERIFIED** unless the required Git synchronization actually completed.
6. If Git persistence is unavailable or unhealthy, ordinary safe work MUST continue from the newest verified authority. In a normal production turn, make at most one Git recovery/sync attempt unless the user explicitly asks for Git repair. Preserve exact hashes and resume instructions instead of consuming the whole turn on repository repair.
7. At the beginning of a resumed session, resolve authority in this order: explicit newer current artifact → newest verified portable state/checkpoint in current files/Project Sources/Library → GitHub checkpoint/state if needed for ambiguity/sync status → legacy/history only for recovery.
8. Treat the user-provided source as authoritative for inventory, spelling, lesson/chapter placement and source lineage. External dictionaries verify/enrich; they do not silently replace the source inventory.
9. Resolve source/book, level, unit boundaries, learning-unit types and source profile before generation. Resolve the current intended Flashcards Pro runtime only when Stage 6 or an actual importer/presentation compatibility task requires it.
10. Do not use legacy enrichment, old NVV fields, historical mappings or previous enriched card sets unless the user explicitly opts into a named recovery workflow.
11. Never create collocations, synonyms, antonyms, Rektion, provenance or source locators merely to satisfy a numeric target.
12. Collocation count is preferred coverage; every included collocation is a hard lexical-quality claim. Example-derived phrases are not collocations.
13. Require sense alignment and atomic learner-facing text before accepting lexical relations. If sense-bound synonym/antonym evidence is unavailable, omit the relation and report coverage.
14. Source/dictionary sense markers such as `[1]`, `[1a]`, `[2b]` are evidence locators only. Remove the marker from learner-facing text while preserving the lexical item and provenance locator according to `SOURCE-SENSE-MARKER-NORMALIZATION-v1.0.0.md`.
15. If a learner headword explicitly encodes valency, emit explicit Rektion with evidence; do not guess ambiguous two-way-preposition case.
16. Inventory the source once, establish stable canonical IDs, cache external source responses, and retry only missing/stale/failed units. Repeated full-source refetch without cause is a pipeline defect.
17. For a new source with no dedicated completeness profile, use `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`. `MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json` applies only to Menschen A1.
18. When runtime acceptance is required, resolve the intended Flashcards Pro runtime from the newest verified app artifact/state plus current repository metadata as needed. Never hardcode a historical runtime version as the permanent target and never silently downgrade from a newer verified artifact to an older GitHub tree.
19. Universal v2 TSV is literal tab-separated transport, not RFC4180 CSV. JSON-valued cells (`examples`, `related`, `opposites`, `details`, `custom_fields`) contain raw JSON between tab delimiters. Top-level `related`/`opposites` must match canonical `details.synonyms`/`details.antonyms` exactly.
20. Execute the seven stages agentically and end-to-end without arbitrary batch stops:
   1. Source & Inventory
   2. Canonicalization
   3. Evidence & Enrichment
   4. Linguistic & Lexical QA
   5. Delivery Projection
   6. Runtime & Presentation Acceptance
   7. Release & Post-Package Verification
21. On an upstream authoritative change, mark dependent downstream stages `INVALIDATED` and rerun only the affected stage and its downstream dependents. Preserve valid upstream PASS checkpoints.
22. Before `Final`, all applicable hard gates in Stages 1–7 must actually execute and PASS, including target importer/presentation acceptance and independent post-package verification. Git synchronization status is reported separately.
23. A file that merely parses, or a transport-only PASS, is not a runtime-verified release.
24. Continue agentically through Stage 7. Stop only for a real evidence/tooling/access blocker. GitHub lag alone must not stop ordinary safe work. Do not use GitHub Actions/Base64 chunking to materialize generated release/checkpoint ZIPs merely for persistence.
25. Final delivery must include the direct import TSV separately, canonical JSON, QA/coverage reports, runtime/presentation evidence, manifest/hash evidence, package ZIP, and a portable self-verifying final checkpoint/state bundle. Git may store the compact manifest/hash/checkpoint metadata at a meaningful sync boundary.
26. Grammar, Vocabulary, Lesen, Schreiben and app runtime may progress in parallel. Keep their source identities/checkpoints separate and never let one stream silently overwrite another stream's authority.
27. This is a side project. Avoid repeated routine confirmations; surface only material blockers or decisions affecting source fidelity, data loss, architecture, scope, or visible UI/UX.

Current source-specific profile for Menschen A1: `MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`.
Generic policy for subsequent sources: `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`.
Active lexical/transport hardening validator: `Verification/validate_lexical_quality_v1_0_1.py`.
