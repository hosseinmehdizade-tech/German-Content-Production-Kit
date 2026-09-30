# Menschen A1 Verben Repair v3.3.6

This workspace is a **delta repair successor** of the immutable locked A1 Verben release.

Current durable milestone: **Stage3C Disposition Closure PASS — 4776/4776 cells final, 0 unresolved**.

- Parent locked release: `German-Flashcards-Pro-v435-R69-Menschen-A1-Verben-v3.3.2-LOCKED.zip`
- Active canonical: **310 targets = 247 senses + 63 expressions**
- Canonical SHA-256: `9b4a58b6002e8ea9d3c521367d4cdf14941af41b094511dd853a89703017e0b4` — unchanged from Stage3B NVV
- Examples: **1240 unchanged**
- Relations: **769 unchanged**; relation-content SHA-256 `c93e18fd030ae39b80f7a009e2022f6998c473ccd8a33a59bd7a1b10b158153d`
- Stage3C disposition: **3304 VERIFIED_PRESENT + 1472 CLOSED_NO_FORCE + 0 NOT_APPLICABLE = 4776/4776**
- MUST_HAVE: **1923/1923 VERIFIED_PRESENT**
- REVIEW_TO_CLOSURE: **1073 VERIFIED_PRESENT + 1470 CLOSED_NO_FORCE**
- OPTIONAL: **308 VERIFIED_PRESENT + 2 CLOSED_NO_FORCE**
- Candidate ledger: **2184 = 709 ACCEPTED + 1475 REJECTED + 0 DEFERRED**
- Fresh Stage3C validators: **7/7 PASS**
- Post-package: **CRC PASS; SHA256SUMS 153/153; manifest 152/152; package hygiene PASS**
- Canonical bytes, candidate ledger, and target-level disposition content are exact-preserved from the Stage3B NVV milestone.
- Library rematerialization: **PASS exact SHA-256 + byte compare**
- Current checkpoint: `Menschen-A1-Verben-v3.3.6-PostLock-Repair1-Stage3C-DISPOSITION-CLOSURE-CHECKPOINT.zip`
- Checkpoint SHA-256: `aa41e69b33b31435562ec43a6382ef01f0ec7b9e900038c4653095dd2734cc73`

Dependency fingerprints:
- resolved enrichment policy: `147cf7c81d8e74b00ce7eb1d8833549729a7bb14f49bc9ae6f1daa71a52abc12`
- identity closure: `bb3c099663a54015cf71b7be0e9ff7537177aca766a571a69c1e4e58c8dbd7c9`
- dataset profile: `d0563205a66b181bbf06a51cf3b1320e171c16e3e3c7ae89b02b80f0605a22e5`
- source occurrences: `043b9a43cd95f0bd27cd4671822bd963e03780250939bfac336e74405456b6b4`

Stage3C is certification, not enrichment: no canonical lexical content, relations, examples, morphology, structure, runtime or UI were changed.

Next milestone: **Stage4 independent linguistic/lexical re-audit**. Stage4 must independently recompute applicability and recheck source IDs, relation endpoints/duplicates, expression structure, fingerprints, no-force decisions, German/FA/EN quality and example quality rather than trusting Stage3 self-report.
