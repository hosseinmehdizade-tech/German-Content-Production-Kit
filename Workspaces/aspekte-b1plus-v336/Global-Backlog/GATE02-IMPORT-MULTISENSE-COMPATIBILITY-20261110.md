# Aspekte B1+ — Global Gate02: app importer and multi-sense compatibility

**2026-11-10 · Executed isolated runtime QA · Gate02 BLOCKED / NONIMPORT.**

## Verified data and application authority

- B1+ current curated owner is **unchanged**: Library `libfile_261160dae9508191904f55a410076d40`, archive SHA256 `a2fa93f3389b43db12e562331cc3302e24e51f0cb028a494ce61b3e825e6a50b`, primary 1571-card JSONL SHA256 `829a1d9e16df96cf1467659835f7fcaa14aefa705f7d639910a150e9d37bfe22`.
- Actual current app **v505-R141 WORDLINKS_FRONTBACK_R3**, immutable Library `libfile_ae33f334c1bc8191aa65dd079f710d01`, verified ZIP SHA256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`. Historical main-branch app not used.
- Isolated headless Chromium ran actual app inline source and 38 exact original JS modules. No user profile, no native durable write, no actual release deployment. Full scripts were loaded unchanged internally with local script-tag inlining to avoid blocked network requests.

## Actual source-exact results

1. **Full 1571-card parser preflight PASS.** A QA-only universal TSV projection (not a deliverable import file) parsed all 1571 via `GFP_CONTENT_V360.parseTsvText`; 3524 German–Persian example translations preserved; 713 network-bearing cards, 1097 sense blocks and 359 inherited HOLDs preserved as custom metadata; 0 invalid rows / 0 parser warnings. The one actual `sense_ids` multi-sense array survived parsing.
2. **Three real-card runtime test: FAIL_MULTISENSE.** Used `GFP_TEST_API.simulateReplace` and `compactRuntimeV425ForTest` in a disposable test browser. Card source ordinal 363, `alle / alles / aller-`, has a single example linking senses S1 and S2. Both sense IDs survived initial parse and remained in the full authority record. **After runtime compaction, only S1 remained in projected example metadata and the `sense_ids` array was absent**. The exact current runtime `index.html` helper `runtimeExampleProjectionV483` (around line 3837) only carries `id`, `label`, `sense_id` to a minimal example, not the `sense_ids` array. This is a runtime projection limitation, not proof of durable authority corruption.
3. **QA adapter presentation gap.** The QA-only parser fixture placed the 713 semantic networks in custom metadata, but did not map them to recognized rendered `details`/typed relations; tested card's Presentation model showed only the QA note. Thus **preservation is not equivalent to visible semantic content**. This alone cannot be generalized to a future canonical/native import adapter.

## Decision and required next gate

- **No change to 1571 learner primary, no forced split of polysemy, no removal of the second sense, no change to current app source, no new approved cards.** All 359 HOLDs remain. Release `BLOCKED_NONIMPORT`.
- Compatibility work before import: define explicit transport for multiple example-to-sense links, teach runtime compactor to retain it, map meaning networks to visible sections with stable sense IDs, and test parser → runtime compaction → Presentation → durable commit/restart. Coordinate app-side code in its dedicated Deep Audit; do not patch CURRENT app within content production.
- **Source evidence:** verified Library report `libfile_d608cfdf65e4819195f195f834fea2d6` (`Reports/GATE02-COMPATIBILITY-REPORT-20261110.json`), SHA256 `14e3b4c2f25de109f72d478aee75e321c2c3e05778bb49e59db7725bbd4f2cf5`, exact Library readback PASS.
