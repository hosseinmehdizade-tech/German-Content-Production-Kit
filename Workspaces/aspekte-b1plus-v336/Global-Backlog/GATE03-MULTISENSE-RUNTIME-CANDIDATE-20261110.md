# Aspekte B1+ — Global Gate03, exact-current runtime multi-sense candidate

**Date:** 2026-11-10 · **Evidence state:** EXECUTED_ISOLATED_CANDIDATE · **Release state:** BLOCKED_NONIMPORT · **Primary learner changes:** **0** · **Current app source edits:** **0**

## 1. Frozen authority and provenance

- Current B1+ curated 1,571-card owner is the verified **Global Gate01**, Library `libfile_261160dae9508191904f55a410076d40`, archive SHA256 `a2fa93f3389b43db12e562331cc3302e24e51f0cb028a494ce61b3e825e6a50b`; PRIMARY JSONL SHA256 `829a1d9e16df96cf1467659835f7fcaa14aefa705f7d639910a150e9d37bfe22`, source map SHA256 `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882`. None changed.
- Actual user-current app authority: **v505-R141 WORDLINKS_FRONTBACK_R3**, immutable original Library `libfile_ae33f334c1bc8191aa65dd079f710d01`, ZIP SHA256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`. Do NOT compare or patch old main/01-App v486.
- Evidence archive in B1+ Library Reports: `libfile_eea7e5081ec88191b171d67b1660d0f5`, `Aspekte-B1plus-GATE03-ISOLATED-MULTISENSE-CANDIDATE-22-ASSERTIONS-NONIMPORT-20261110.zip`, SHA256 `3401226b57dea8321461ace17830f8a571e765dedd7e7be1cf7034fd5f6a0dd7`. 8 members / 7 manifest records, CRC and **exact Library byte readback PASS**.

## 2. Exact-source causes and narrowly scoped isolated candidate

In the actual R3 `01-App/index.html` (not the old main mirror):

1. `runtimeExampleProjectionV483` projects `id`, `label` and `sense_id` but omits `sense_ids`. Candidate copies the source array unchanged into compact example metadata.
2. The `covered` optimization compares text, example ID and translation but **not meaning identity**. Candidate tests scalar `sense_id` and full `sense_ids` equality before treating rich examples as redundant with canonical fallback. No arbitrary source-to-sense auto-inference.
3. `normalizeCanonicalExampleGroupV348` likewise only projects `sense_id`. Candidate preserves explicitly supplied `sense_ids` in canonical example groups.

The archive includes the exact minimal JSON patch and two executable local Chromium source-exact test scripts. It contains **no modified app runtime or promotable import file**.

## 3. Executed evidence

- Baseline/current app failure reproduced on **real source ordinal 363** (`alle / alles / aller-`), source example `Alle waren da, aber nicht alles hat funktioniert.`, which is deliberately linked to S1 **and** S2: after compaction the displayed example group loses its second sense; the full authority still has both.
- **15/15** focused comparison assertions against baseline and two-change candidate passed: runtime retains both IDs after compaction and a repeated compaction, Persian example translation and three example count stay unchanged, and a canonical fallback with insufficient semantic links no longer causes the rich version to be dropped from runtime.
- **7/7** additional canonical example normalization and presentation-model assertions passed on the three-change candidate: explicitly present S1+S2 survives before/after compaction and appears in the Presentation model. Baseline loses it.
- Total **22/22 expected focused assertions**, including expected failures and remaining blockers. This is NOT 22/22 product acceptance criteria. Headless Chromium with original current runtime in an isolated synthetic document; three real cards, one controlled fallback variant. Gate02 had already passed the full 1,571-card parser-only check.

## 4. Remaining release blockers — MUST NOT BE SILENTLY CLEARED

- **Canonical presentation precedence:** when canonical examples omit multi-sense links but secondary rich examples contain them, the current Presentation model can still prefer canonical content and omit S2, although the rich runtime payload survives. Needs a precedence/identity contract, not a blind merge.
- **Right card / Wortnetz:** the QA-only source adapter retains all 713 network-bearing cards in custom metadata but does not map them into visible typed Presentation sections. Rendering and stable sense-level clicking remain unverified.
- **Durable persistence:** the exact test environment blocked navigation to a stable test origin (`ERR_BLOCKED_BY_ADMINISTRATOR`); opaque-origin IndexedDB/localStorage are denied. **No durable write/restart test passed or was falsely claimed.**
- No approved app release, complete bilingual semantic QA, or native user-profile import. All **359 inherited HOLDs** and all 1,571 curated cards remain intact.

## 5. Next substantive step (Gate04)

Define **non-lossy canonical/rich precedence**, meaning-anchored right-card adapter and stable target IDs with the app's Deep Audit. Build a true origin-backed, persistent parser→compact→Presentation→durable save→restart acceptance test in an authorized environment. Keep user current app and learner owner unchanged until app-side QA and owner review; **RELEASE_BLOCKED_NONIMPORT**.
