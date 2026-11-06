# Global Policy Synchronization Contract v1.0.0
**Status:** ACTIVE PROSPECTIVE ROUTING — process optimization only, 2026-11-05.

This file is the common **policy resolver**, not a new content dataset, a new authoring stage, a migration, or proof that 34 workstreams have been reviewed. The machine-readable authority is `Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json`; use its exact paths, Git blob pins, scopes and invariants. The currently activated entrypoint remains `Prompt/ACTIVE-PROMPT.txt` -> `Prompt/START-PROMPT-v3.3.6.md`. **Never overwrite the immutable v3.3.6 portable master:** `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.3.6.md` is only a locator; this prospective overlay extends its future-safe execution rules.

## Curated-current authority and scope-limited source provenance (2026-11-06)

At each eligible content resume resolve the registry's `curated_current_delta_qa` binding and `Prompt/CURATED-CURRENT-AUTHORITY-AND-DELTA-QA-POLICY-v1.0.0.md`. **New-source inventory** uses raw original evidence; **mature user-curated content** uses the latest verified owner-specific current/final TSV/CSV/JSON (or fully recoverable approved current bundle) and accepted decisions as learner-facing selection authority. Old sources remain immutable and useful for quoted attribution/recovery, but cannot veto months of accepted new, removed or corrected words. Compare a proposed successor against the immediate accepted curated parent, review changed IDs plus impacted dependencies and preserved unresolved QA risks, then run full current-state Stage5/7 structural checks and required app Stage6 gates. Never silently fall back to a raw original if a claimed curated current file is inaccessible; mark authority HOLD. The original Stage1–7 pipeline remains version-pinned for initial ingestion and stage evidence; this overlay prevents redundant original-vs-final matching from being mistaken for a mandatory release gate. Source-provenance exact claims remain independently testable; this is not a waiver of grammar, multilingual semantic QA, integrity, SRS or true runtime testing. No prior LOCKED/current/user data is automatically changed.

## Four independent axes: do not conflate them

1. **Source authority/currentness**: user-specified newer validated attachment > validated newest portable workstream artifact > local `LATEST.json` with matching SHA-bound milestone receipt > workstream `CHECKPOINT.json` > stale global summary. New files are not automatically newer merely because of filename/date. Source fidelity and immutable raw/LOCKED always constrain edits.
2. **Normative policy version**: explicit user scope and preservation obligations > active cross-repository safety/authority policy > this exact registry's version-pinned active bindings > per-domain rules > compatible source-specific additive restrictions > historical documents for replay only. A source-specific rule may **strengthen** QA or select a source-specific schema; it cannot secretly bypass provenance, Stage4 review, Stage5 safety, UI/SRS protection or currentness.
3. **Adapter and output schema compatibility**: a synthetic TSV/JSON mapping PASS confirms only that format. Real producer output must be tested separately using the exact current artifact bytes. Invalid structural data fails closed; do not coerce prose into structured `details`, invent senses or translate unsupported content.
4. **Stage acceptance evidence**: scoped Git/Library receipt, exact source/input/output SHA and independent stage-specific QA. Technical advisory PASS is not semantic Stage4; static packaging PASS is not browser/IndexedDB Stage6 or Stage7. A workstream's PASS cannot be copied to any other.

**If policies conflict:** first identify which axis they govern. Where two active rules govern the same axis and claim incompatible behavior, record `POLICY_CONFLICT_HOLD`; do not silently pick a convenient value or rewrite data. To resolve, explicitly supersede one path in the central registry and provide an evidence-backed migration/compatibility test. Read `WORKSTREAM-RESUME-CURRENTNESS-POLICY.json` for the currentness axis. Read this registry's exact paths rather than old README narrative.

## Execution contract, Stage 1–7

| Boundary | Required behavior | Acceptance evidence |
|---|---|---|
| 1 — Source | Inventory the exact registered source, location, license and SHA; never synthesize missing original material | source inventory/manifest |
| 2/2B — Canonical | Close identity and sense; stable IDs and exact target references; no guessing | canonical/lineage and disposition |
| 3A/B/C — Enrichment | One source-bound ledger; classify Synonyme/Antonyme/Wortfamilie/genuine Verwandte Wörter; source-first useful Kombinationen separate from abstract Rektion; no artificial quotas | Stage3 decision/evidence and advisory checks |
| 4 — Linguistic QA | Independent AI semantic/source/DE–FA–EN review with separate adversarial method, risk-based acceptance and explicit HOLD | independent Stage4 receipt; advisory scanner not sufficient |
| 5 — Projection | Preserve graph vs details vs structured sidecar; validate exact projected fields, including present `details` JSON list of sections; run exact clean builder pre-copy and on staged copy | source-to-projection parity, validator, packaged SHA |
| 6 — Runtime | Resolve CURRENT runtime only when integration matters; real required browser/import/storage proof or declare environment boundary | runtime-specific evidence, not synthetic QA |
| 7 — Release | Exact ZIP, manifests/checksums, dependency/provenance, frozen LOCKED/source rules and correct content-only vs app bundle boundary | hash-bound verification receipt |

The **ordinary neutral vocabulary** builder's `details` gate is scoped to that consumer, not a claim that every alternative source importer already uses it. Registered source-specific adapters stay in place until **real** parity is proven. A workstream whose content is nonlexical can mark lexical policies `NOT_APPLICABLE_BY_SCOPE`, but must still obey general source and QA protections.

## Adoption ≠ compliance: evidence ladder

The adoption matrix `Optimization-Program/Verification/GLOBAL-POLICY-ADOPTION-MATRIX-20261105.json` inventories the **21 known Library content families separately from the 34 Git tracked workspace directories**. These are different classifications; one family can have multiple repair or audit workstreams. Its default `CENTRAL_ROUTED_NOT_IMPLEMENTATION_VERIFIED` proves only the central router exists. Move a workstream through:
`DISCOVERED -> CENTRAL_ROUTED -> ADAPTER_SYNTHETIC_VERIFIED -> REAL_OUTPUT_SCOPED_VERIFIED -> INDEPENDENT_SEMANTIC_VERIFIED -> STAGE5_EXACT_BUILT_VERIFIED -> STAGE6_REAL_RUNTIME_VERIFIED -> STAGE7_RELEASE_VERIFIED`.
Each step needs source-bound independently checked evidence. No automatic promotions, retroactive rewriting, or blanket status propagation.

Existing observations: PR #80 synthetic adapter QA 65/65 on Ubuntu/Windows; A1 2,997 and A2 L17 112 rows parsed read-only; 250 Verben 292, NVV 2,492 schema-only; B1 master 3,088 rows **fail-closed** because 145 B1-L19 `details` cells contain prose not JSON; PR #81 central Stage5 future gate 18/18 on both OS; PR #82 refreshed navigation-only routes. See the exact receipts in `Optimization-Program/Verification/`; **none of these proves all-native adapters, full Stage4 or global release**.

## One central Vorderseite / Rückseite contract (2026-11-06)

Resolve the registry's `global_flashcard_front_back_presentation` binding at every new or resumed applicable German lexical owner. The version-pinned `Prompt/GLOBAL-FLASHCARD-FRONT-BACK-PRESENTATION-CONTRACT-v1.0.0.md` coordinates **existing** HF2 front-production policy with **conditional** Lean Formen back presentation. These govern **different sides of the producer/consumer boundary**: Stage5 must source-bind article/plural, verb principal forms and evidenced adjective comparison, while Stage6 must compare actually visible front values before hiding only redundant display facts from `Formen`. Preserve source-pinned HF2 v1.2 governed constructions, plural-only and non-gradable exceptions, all extra forms, card settings, typing, SOURCE/LOCKED/SRS. The 2026-11-04 app candidate is STATIC/NOT FULLY CORRECT, not a proven CURRENT/FINAL app implementation; independent browser validation and native-adapter QA remain pending.

## Source-specific and historical boundaries

- Current `RELATED-SECTIONS-TAXONOMY-POLICY-v1.1.0.md` supersedes v1.0 only for prospective mutable production. v1.0 and historical README paragraphs remain for exact replay, not the active selector.
- `LEXICAL-RELATION-PRESENTATION-AND-SENSE-POLICY-v1.0.0.md` governs prospective typed bilingual relation content. Keep `vnext_relations` Wortnetz graph separate from learner-visible `details`; never synthesize a display link from opaque IDs.
- Do not recategorize/import/rewrite historical Menschen A1/A2/B1, Verben, NVV, Vocabulary, source PDFs, LOCKED content, or any user FSRS/SRS based on an optimization audit.
- Respect the Menschen A2 **no separate Stage6 kits** user override. Do not change established UI without approval.
- `RESUME-ROUTES.json` is navigation-only and never establishes quality/progress. Missing current Vocabulary import/export is an explicit evidence gap, not an alias of legacy A2 Verben.
- Any new policy, changed version, or new Git workspace must update the **registry pins/matrix** in the same proposed change and pass `Verification/audit_global_policy_sync_v1.py --check` on Ubuntu and Windows. This is a coordination guard, not a blanket source acceptance gate.
