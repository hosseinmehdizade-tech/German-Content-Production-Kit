# START PROMPT v3.3.6

**ACTIVE CROSS-PROJECT LINGUISTIC REVIEW OVERRIDE (user-approved 2026-10-25):** Read `LINGUISTIC-QA-AUTHORITY-POLICY.json` before any Stage4/content quality/release acceptance. Mandatory external qualified-human/independent-specialist signature is REMOVED for all content streams. Require full documented AI semantic/translation/source review, independent-method adversarial second pass and deterministic QA; label it AI review, never human approval. Stage5/6/7 and source-fidelity gates remain unchanged. Historical reports/LOCKED artifacts remain immutable; old reviewer-identity gates must not block solely for missing external human. The override itself does not imply Stage4 PASS.

**ACTIVE work-outcome and concurrency rule:** On `continue`/`ادامه بده`, read `EXECUTION-OUTCOME-EFFICIENCY-POLICY.json`; progress toward a whole reviewable stage/queue, not another arbitrary 3–5-card edit/report. Count corrected/kept/held/remaining separately, perform scoped QA, preserve unchanged/LOCKED, and use `Verification/validate_execution_outcome_receipt.py` at meaningful milestone handoff. Neither scoped PASS nor a Git checkpoint substitutes for the full documented AI-linguistic Stage4 audit, Stage5 or CURRENT Stage6. External human signoff is not required.

The active production framework is **v3.3.6 — Source-Agnostic Completeness Gate**.

Resolve the full master prompt from `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.3.6.md` inside the verified portable authority recorded in PROJECT-STATE.json.

Mandatory architecture:
- source format is isolated to Stage 1 adapters; readable sources normalize to universal source occurrences;
- Stage 2 must close occurrence/duplicate/split/merge identity questions before enrichment;
- Stage 3 is `3A baseline richness audit -> 3B gap-driven enrichment -> 3C disposition closure`;
- every applicable target/dimension ends as `VERIFIED_PRESENT`, justified `CLOSED_NO_FORCE`, or policy-permitted `NOT_APPLICABLE`; unresolved/blank is never PASS;
- `CLOSED_NO_FORCE` is a reviewed first-class outcome; density quotas never justify fabricated relations;
- rejected candidates are persisted so they are not repeatedly proposed;
- Stage 4 independently re-audits completeness/source IDs/relations/structure and does not trust Stage 3 self-report;
- Stage 5 uses the v3.3.6 clean-delivery anti-bypass gate from the portable authority;
- ordinary vocabulary still uses `de-vocabulary` + `gfp-vocabulary-neutral@1`;
- ACTIVE HF2 learner-visible front overlay: `Prompt/LEARNER-VISIBLE-LEXICAL-FRONT-POLICY-v1.1.0.md` is mandatory. Stage 5 must run `Verification/validate_learner_visible_lexical_front_v1_1_0.py`; Stage 6 must verify actual learner-facing simple and nested/multi-gender noun article/plural forms plus verb/adjective morphology, not metadata presence only. Missing noun article/plural requires an explicit reviewed closure; Verb Sense lemmas must not absorb argument placeholders such as `etw.` or `jdn.`; runtime fallback must not replace a richer approved front with a poorer derived front;
- dependency fingerprints invalidate only affected work; historical LOCKED artifacts stay immutable.

Normative full contracts/tools are inside the portable v3.3.6 authority recorded in PROJECT-STATE.json.

Before production, read root `PROJECT-MEMORY.json` including `prevention` gates/limits. Run `python -B Verification/prevention_preflight.py memory`; new/updated checkpoint pointers must pass its `checkpoint` mode. At Stage5 run `projection` before packaging, and run `package` on final candidate archives. These supplemental checks do not replace the official portable completeness/anti-bypass gates or Stage6 exact-runtime presentation acceptance. Resolve app memory MEM-024 for bounded asynchronous commit readiness and exact-byte harness reruns.

For projection-only successors, run `Verification/prevention_preflight.py lineage PROJECTED.json --baseline RESOLVED_PARENT.json` at Stage5. Resolve the immutable parent from its checkpoint first; retain current canonical parity and reviewed metadata/identity changes as separate gates.


## Mandatory lexical Kombinationen overlay

For every lexical target, read and apply:
`Prompt/LEXICAL-KOMBINATIONEN-ENRICHMENT-POLICY-v1.0.0.md` and resolve current-workstream adoption from `Prompt/LEXICAL-KOMBINATIONEN-ADOPTION-MATRIX-v1.0.0.json`.

This overlay is ACTIVE for verbs, nouns, adjectives, adverbs and lexical expressions in new work and active workstreams at the next safe enrichment/QA boundary. It requires at most one learner-visible `Kombinationen` section, preserves backend typing/provenance, permits reviewed curated lexical combinations, forbids false source claims and density-forced fabrication, allows `CLOSED_NO_FORCE`, and leaves historical LOCKED artifacts immutable.

## Mandatory vocabulary delivery / output contract

For EVERY user-facing lexical/vocabulary content production handoff (Menschen lessons, verbs, nouns, expressions, NVV lexical decks, or future word card outputs), enforce `CONTENT-OUTPUT-DELIVERY-POLICY.json` v2.0.0 before packaging:
- Deliver ONE organized complete **vocabulary content-production ZIP** containing the import-ready final output **plus** canonical/working data, source/provenance mappings, enrichment/disposition ledgers, QA/tests, reports, portable checkpoint/manifest and content-only tools/docs needed for updates and future repair.
- **Exclude the Flashcards Pro app, app runtime, UI assets, installers and app launchers.** App/runtime release ZIPs are separate and unchanged.
- Do **NOT** simplify the vocabulary delivery to one TSV, do **NOT** silently omit the editable/source/QA lineage, and do **NOT** confuse import-only output with a complete portable production handoff.
- Preserve the exact approved content bytes and stable IDs; full-source licensing/size exceptions require explicit hash/locator/dependency accounting. Stage 6 real-browser import status must remain honest.
- User overrides apply only when they explicitly ask for an import-only file, whole-app release, or alternate scope. Nonlexical content delivery follows its own policies.
