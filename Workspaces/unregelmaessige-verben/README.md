# Unregelmäßige Verben — CURRENT Stage4 WIP1 (2026-10-29)

**New working content authority:** `Unregelmaessige-Verben-v1.3.1-R8-Stage4-Morphology-174-SCOPED-WIP1-2026-10-29.zip` SHA-256 `77f6ec4857a58f512247a4a2c2ca051cf3573c84f66c2c9507144536d46b7a5c`; Library `/German-Content-Production-Kit/Checkpoints/Unregelmaessige-Verben-v1.3.1-R8-Stage4-Morphology-174-SCOPED-WIP1-2026-10-29.zip` (exact byte+SHA readback PASS). The R8 ZIP remains the immutable parent source baseline, its original seven screenshots stay historically unverified and no longer gate future R8-derived release. 174-card morphology crosscheck scoped PASS (153 exact, 18 verified variants, 1 corrected modern primary, 2 Duden/PDF discrepancy cases). Confirmed working corrections in `bleichen` and `weisen`; counts 174 cards, 696 DE examples, 530 accepted combinations, 901 relations (parent 902). Official didactic preflight found 131 advisory flags *not yet dispositioned*. Full Stage4 AI linguistic/translation/relation and didactic QA, official Stage5, CURRENT Stage6 and Stage7 remain open. No app/UI change; not a final release.

Milestone: `Workspaces/unregelmaessige-verben/V131-R8-STAGE4-MORPHOLOGY-174-SCOPED-WIP1-2026-10-29.json`. All older progress below is historical.

---

# Unregelmäßige Verben — current source governance (2026-10-29)

**ACTIVE working content baseline:** exact existing `Unregelmaessige-Verben-v1.3.1-R8-FINAL-USER-HANDOFF-TESTS-WAIVED-2026-10-23.zip` (SHA-256 `228e8c2cead0cd3e31d35802e4bb632df248203ffab4cd49798cd0b31bb0b486`); 174 cards, 696 trilingual examples, 530 accepted Kombinationen and 902 relations. User approved treating this immutable R8 content as the production baseline for future reviewed successors. This is a **derived content rebaseline**, not original screenshot attestation.

The seven original screenshot images and their 258 historical source occurrences are preserved in legacy provenance but are no longer a prerequisite for future **R8-derived** final acceptance. Do not claim pixel-to-image parity and do not substitute unrelated PDFs. The independent AI linguistic / Persian & English / morphology / semantic / combination didactic audit, official v3.3.6 Stage5, exact-current Stage6, and Stage7 exact-final gates remain mandatory. **No new content or app release is certified by this governance decision.**

Authoritative receipt: `Workspaces/unregelmaessige-verben/V131-R8-SOURCE-REBASELINE-DECISION-2026-10-29.json`; current pointers: `LATEST.json` and `CHECKPOINT.json`. Historical notes follow.

---

# Unregelmäßige Verben — v3.3.6 migration

Stage5 official clean delivery remains **PASS**.

Stage6 targeted **GFP CURRENT v458-R92** (artifact SHA-256 `94d9f7cce53d1cda50a05bcf3d1be2132e42f63deef6d5048356bdf1d7a194af`). LAST_FULLY_VERIFIED v451-R85 is regression reference only and was not used as the integration target.

Partial CURRENT-runtime evidence passes:
- static exact projection: 174 cards, 696 examples, 1392 translations, 902 relation items, 0 legacy-v217, 0 page errors;
- neutral vocabulary envelope regression: 21/21 PASS;
- Stage6 import-ready wrapper is byte-identical to the Stage5 TSV.

Exact-origin acceptance is **BLOCKED by environment**. Both localhost and file navigation return `ERR_BLOCKED_BY_ADMINISTRATOR` in the managed browser, so import persistence/reload, native persisted Study flow, default UI Content Package export, clean-profile reimport and runtime sidecar-lineage readback are not claimed.

No semantic content was changed. Resume by re-resolving CURRENT and running the exact real-origin Stage6 harness when the environment permits it.


## Stage6 local acceptance kit

Managed Chromium in the execution environment is governed by an enterprise URLBlocklist of `*`, so exact-origin navigation remains administratively blocked. No bypass was attempted. A self-contained Windows/Chrome acceptance kit is now the durable next step.

Kit: `Unregelmaessige-Verben-v1.2.0-v3.3.6-Stage6-LOCAL-ACCEPTANCE-KIT.zip`\nSHA-256: `86119e20a01a045c68646f18425292124ef67a4b955c21285f3b4d9f78bc4789`\nLibrary readback: exact byte/hash PASS. The kit preserves the exact 72-file v458-R92 `01-App` tree and validates all hashes before launch. It uses two disposable Chrome profiles to test real-origin import/persistence/reload/native Study/default-UI export and clean-profile reimport without touching the user's normal profile or library.


## Stage6 Local Acceptance Kit R1

The first local kit was superseded after a real Windows run exposed `HARNESS-001-FIND-CHROME-SCALAR-COUNT`: under PowerShell StrictMode, exactly one discovered Chrome path was returned as a scalar, so `.Count` failed before browser launch. R1 removes that scalar-count assumption and also counts verified runtime files explicitly.

R1 SHA-256: `8d8128736ca8e01b8aa1e163ceb0ef44e9966bc7ec418f6e5958f14767969c33`. Library readback is byte-identical. Only three harness files changed; all 72 CURRENT v458-R92 `01-App` hashes and the Stage6 input ZIP remain exact and unchanged.
