# Changelog

## v3.1.5 — Claim-Coverage + Pilot Delivery Hardening
- Added learner-facing field-to-claim provenance binding: non-empty `details.rection` now requires a dedicated verified `rection` claim in production profiles.
- Generic `grammar` evidence no longer implicitly covers Rektion.
- Source Registry content version bumped to `gfp-approved-language-sources@1.1.0`.
- Duden may emit `rection` only when the exact entry/grammar/examples explicitly attest the pattern; grammis remains preferred.
- Made the existing rule explicit: DE is the Example anchor; FA/EN remain attached to that same Example, while language requiredness is entirely Dataset-Profile driven.
- Bumped prompt/builder/validator package versions for future builds; semantic content contract remains `gfp-german-language-content@3.1.3`.
- Added regression tests for missing Rektion evidence and explicit Duden/grammis coverage.
- No change to example count, canonical schema, runtime state gate, Presentation, Practice, or SRS.


## v3.1.4 — Runtime-State-Aware Import Gate
- Fixed the false-finality flaw exposed by the 30-card v343 pilot: the TSV parsed correctly, but the live browser was write-blocked by recovery state and the transactional import rolled back.
- Kept semantic contract at `gfp-german-language-content@3.1.3`; this release changes prompt/delivery governance, not linguistic schema.
- Split finality into two axes: Artifact Compatibility vs Current Runtime Readiness.
- Deprecated/forbid ambiguous `IMPORT_READY`.
- Added artifact status `APP_COMPATIBLE` and live statuses `CURRENT_RUNTIME_NOT_VERIFIED`, `RUNTIME_PREFLIGHT_PASS`, `RUNTIME_BLOCKED`, `IMPORT_VERIFIED`.
- Added mandatory isolated runtime matrix: empty library, existing non-empty library, write-blocked fail-closed, recovery-resolved→READY, reload durability, roundtrip and writer/concurrency guard.
- Added live preflight requirements for writable/READY mode, no write block/recovery issue, durability `canWrite`, writer authority and pre-import library fingerprint/count.
- Added `RUNTIME-IMPORT-EVIDENCE-SCHEMA.json` and validator.
- `APP_COMPATIBLE` no longer permits telling the user to import now; that requires a live `RUNTIME_PREFLIGHT_PASS`.
- Actual success wording requires `IMPORT_VERIFIED` after transactional commit and reload/reopen persistence.

## v3.1.3 — Flashcard Delivery Hardening
- Closed the gap between semantically valid Canonical JSON and a real Flashcards Pro import artifact.
- Added explicit `DELIVERY_TARGET` and `TARGET_RUNTIME` inputs to the Master Prompt.
- Added mandatory status separation: `CONTENT_VALIDATED`, `TRANSPORT_VALIDATED`, `RUNTIME_IMPORT_NOT_VERIFIED`, `IMPORT_READY`.
- Added official Flashcards Pro mapping to `gfp-german-learning-content@1.0.0` over `gfp-universal-card@2.0 / universal-v2`.
- Added exact 23-column Universal-v2 TSV delivery envelope.
- Added lossless `custom_fields.canonical_unit` preservation so runtime presentation limits cannot delete semantic data.
- Added explicit preservation of NVV vs Collocation semantic kinds through transport.
- Added `BUILD-METADATA.json` SHA-256 provenance requirement.
- Added Universal-v2 delivery builder and parity validator.
- Added sample delivery artifact and target-runtime validator evidence against Flashcards Pro v343.
- `IMPORT_READY` is now forbidden unless the actual target runtime import/roundtrip gate is executed successfully.

## v3.1.2 — Source-Policy Hardening
- Added approved Source Registry and Source Registry JSON Schema.
- Explicit DE→DE authorities: Duden, DWDS, grammis.
- Explicit DE↔FA resources: Langenscheidt Deutsch–Persisch, Wort.ir, B-Amooz, PONS Persisch.
- Explicit DE↔EN resources: Langenscheidt, PONS, Collins, Cambridge, Oxford Learner’s.
- Separated `approved` source status from per-run `verification_status`.
- Added claim-level source authority and claim-specific minimum verified sources.
- Added risk-based independence checks; Langenscheidt/Collins DE↔EN conservatively share one lineage group.
- Persian bilingual sources cannot verify German grammar/rection/morphology claims.
- Added source-policy positive/negative tests and schema meta-validation coverage.
- No changes to examples[], connections[], Type Rules, presentation, practice or Flashcards Pro Runtime.

## 3.1.1 — 2026-08-25

- الزام `singular` را برای Nomenهای `plural_only` حذف و `plural` را فقط در همان حالت شرطی required کرد.
- امکان حذف `plural` برای Nomenهای عادی بدون Plural مفید را حفظ کرد.
- الزام Profile-levelِ `plural` و overrideهای اثباتی Example count را از Menschen A1 حذف کرد؛ `by_type` در Profile Schema و Architecture Proof باقی ماند.
- `function` را در Phrase family عمومی optional کرد تا learner-facing metadata مصنوعی تولید نشود.
- تست‌های مثبت/منفی Patch و evidence اعتبارسنجی را اضافه کرد.

## 3.1.0 — 2026-08-25

- Package را به معماری Clean-Slate تبدیل کرد و تمام artifactهای compatibility/preservation قبلی را کنار گذاشت.
- `connections[]` و kindهای معنایی unified را اضافه کرد.
- Type Ruleها را از فهرست نام field به قرارداد value-type واقعی ارتقا داد.
- قابلیت Verb برای Partizip، Konjunktiv II، Imperativ، auxiliary، reflexivity، separability، modal و morphology variants را اضافه کرد؛ فقط core معمول required است.
- Profile example policy را به `default + by_type override` ارتقا داد.
- Required source/translation languageها را Profile-driven کرد.
- Schemaهای Learning Unit، Profile، Type Rule و Connection را جدا کرد.
- نمونهٔ ۱۰ Unit با Verb و پنج خانوادهٔ Non-Verb اضافه کرد.
- Validator typed و تست‌های مثبت/منفی اضافه کرد.
- Draft 2020-12 Meta-validation و Evidence قابل اجرا اضافه کرد.
- Presentation و Practice را به‌طور کامل خارج از Content schemas نگه داشت.
