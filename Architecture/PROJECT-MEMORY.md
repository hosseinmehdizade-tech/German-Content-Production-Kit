# Project Memory — v3.1.5 Claim-Coverage + Runtime-State-Aware Gate

## Frozen-candidate decisions

- Semantic canonical contract: `gfp-german-language-content@3.1.3`.
- Architecture is Clean-Slate; new linguistic content is generated from scratch.
- Canonical persistence is the JSON model in `LEARNING-UNIT-SCHEMA.json`.
- General Contract, Dataset Profile, Type Rules, Presentation Settings, Practice Settings and Delivery Transport are separate authorities.
- Examples are dynamic source groups; FA/EN translations remain attached to their German source in Canonical JSON.
- `english_gloss` never substitutes for an English sentence translation.
- Example identity is stable and independent from text/hash/order.
- `connections[]` stores semantic relation kinds without layout ownership; NVV and Collocation remain semantically distinct.
- Profile owns default/per-Type count, languages, CEFR, source policy and strictness.
- Type Rule owns typed `core`/`details`; similar Types share rule families.
- App runtime never generates or corrects linguistic content.
- Structural, linguistic, provenance, transport and runtime-import statuses are separate gates.

## Runtime-state failure discovered after v3.1.3

The 30-card pilot proved a second boundary bug. The Universal-v2 file was parsed as 30 cards, but the user's live v343 browser session was still in a recovery/write-blocked state. The app correctly rolled the transaction back and preserved the existing library. Therefore an isolated parser/roundtrip PASS was insufficient to call the file “ready now”.

## v3.1.4 decision

Finality is now two-axis:

```text
Artifact: CONTENT_VALIDATED → TRANSPORT_VALIDATED → APP_COMPATIBLE
Current runtime: CURRENT_RUNTIME_NOT_VERIFIED | RUNTIME_PREFLIGHT_PASS | RUNTIME_BLOCKED → IMPORT_VERIFIED
```

Hard guardrails:

- Semantic contract stays `gfp-german-language-content@3.1.3`; v3.1.4 is prompt/delivery governance.
- Canonical JSON remains source-of-truth; Universal-v2 TSV remains the import transport.
- `APP_COMPATIBLE` requires an isolated Runtime matrix including an **existing non-empty library**, not just an empty/clean harness.
- Recovery/write-block scenario must fail closed and preserve the previous library; that is a safety PASS, not an import success.
- A live browser may be `RUNTIME_BLOCKED` even when the artifact is `APP_COMPATIBLE`.
- Telling the user “import now” requires live `RUNTIME_PREFLIGHT_PASS`.
- Actual success requires `IMPORT_VERIFIED`: transactional persistent commit + reload/reopen survival.
- `IMPORT_READY` and `RUNTIME_IMPORT_NOT_VERIFIED` are retired because they mixed artifact and runtime axes.
- No automatic Clear Site Data / reset / delete-database workaround is allowed for a blocked runtime.
- Every runtime claim beyond transport validation must have `RUNTIME-IMPORT-EVIDENCE.json`.

## Completed in v3.1.4

- Master Prompt runtime-state split and live preflight gate.
- Mandatory isolated runtime state matrix.
- Runtime import evidence schema + validator.
- Negative tests against false current-runtime claims from isolated evidence.
- Negative tests against preflight PASS with `writes_blocked=true`.
- Negative tests against import success without verified commit/reload.

## Outside this phase

- bulk Dataset generation
- App Runtime/UI changes
- Sentence Practice or SRS implementation
- independent expert linguistic certification

## Next stage

Use v3.1.4 for the next 30-card run. First establish `APP_COMPATIBLE` in the target-app harness. On the user’s actual v343 browser, run live preflight before recommending import; if recovery/write-block is present, report `RUNTIME_BLOCKED` and resolve the runtime through its official recovery path before retrying.


## v3.1.5 decision
- Translation grouping is semantically fixed: FA/EN, when present, translate the same German Example and keep its Stable ID.
- Translation requiredness is not globally fixed; each Dataset Profile decides which translation languages are mandatory.
- Learner-facing `details.rection` cannot be Final without explicit claim-level Evidence `rection` from an approved German authority. Generic grammar review is insufficient.
