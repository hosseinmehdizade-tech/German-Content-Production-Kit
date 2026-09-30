# Menschen A2 Verben Repair v3.3.6

Current durable milestone: **Stage5 Clean Delivery Projection PASS**.

- Upstream Stage4 canonical remains authoritative: **292 targets = 228 verbs + 64 expressions**
- Stable IDs/order: **292/292 preserved**
- Examples preserved: **1168 DE + 1168 FA + 1168 EN**
- Semantic relation graph preserved: **1205 relations**
- Stage5 projection: **292/292 de-vocabulary**
- Presentation contract: **gfp-vocabulary-neutral@1 — 292/292**
- Hidden/nested presentation selector conflicts: **0**
- Dataset: `A2-VERBEN-UNIVERSAL-v2.tsv`
- Dataset SHA-256: `704a928de4149c2c7e34cfd64f00ed9bf38008b421067a58e49c5c14a4a87172`
- Projected-cards SHA-256: `15ff751500766608871618f2a12d780fccb066acdc64b1ae3a050e23a37022fe`
- Source authority: **297 screenshot rows → 336 normalized occurrences → 335 mapped occurrences**, with one explicit retired occurrence; no source audio exists and `SOURCE_HAS_NO_AUDIO` remains explicit.
- v3.3.6 anti-bypass gates: source occurrence PASS, identity closure PASS, candidate ledger PASS, completeness **4508/4508 / 0 unresolved**, unified vocabulary projection PASS.
- Independent Stage5 QA: **319/319 PASS**.
- Post-package: ZIP CRC PASS; manifest **33/33**; SHA256SUMS PASS; fresh unified validator PASS; JSON reparse **27/27**; hygiene PASS.
- Checkpoint: `Menschen-A2-Verben-v3.3.6-PostLock-Repair1-Stage5-PASS-CHECKPOINT.zip`
- Checkpoint SHA-256: `9fe56aabeb55291e1bad0141b58b42d2cf952a70880c2af7b7615d23e522b76a`
- Clean delivery SHA-256: `996ea2159fbe9d7908b57d4ac4d36ef711de99b71df7eddee0815ea209f14c8b`
- Library rematerialization: **PASS exact SHA-256 + byte compare** for checkpoint, clean delivery and post-package report.
- Runtime/UI were not changed.

Next milestone: **Stage6 Runtime & Presentation Acceptance**. Re-resolve Flashcards CURRENT at execution; do not bind Stage5 to an older runtime.
