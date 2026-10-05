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
