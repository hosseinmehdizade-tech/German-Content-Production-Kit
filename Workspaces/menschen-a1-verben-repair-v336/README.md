# Menschen A1 Verben Repair v3.3.6

This workspace is a **delta repair successor** of the immutable locked A1 Verben release.

Current durable milestone: **Stage4 independent linguistic/lexical re-audit PASS**.

- Active canonical: **310 targets = 247 senses + 63 expressions**
- Examples: **1240 unchanged**
- Canonical SHA-256: `4a7b5a0d7dfa4d984e4afc375c237c80d8ea8f00f0afde6a3f86f6f11d75c0ce`
- Relations: **768**; relation-content SHA-256 `bac4a38ff67bef41bce1b6d40a905e234e4dad6c1b34ecc69e29fb4d8a1a5ebe`
- Disposition: **4776/4776 final = 3303 VERIFIED_PRESENT + 1473 CLOSED_NO_FORCE; 0 unresolved**
- Candidate ledger: **2185 = 709 ACCEPTED + 1476 REJECTED + 0 DEFERRED**
- Independent Stage4 audit: **42/42 PASS**
- Fresh official validators: **7/7 PASS**
- v3.3.6 framework pytest: **10/10 PASS**
- Post-package re-run: custom **42/42 PASS**, official **7/7 PASS**
- ZIP CRC **PASS**; manifest **31/31**; SHA256SUMS **32/32**; JSON reparse **27/27**; hygiene **PASS**
- Library rematerialization: **PASS exact SHA-256 + byte compare**

Stage4 found and closed bounded defects rather than rubber-stamping Stage3: 306 course-source evidence refs were reclassified from `approved` to `source_authority`; the source-backed `wählen` morphology projection gained `auxiliary=haben`; one redundant self-value `COLLOCATION` for `eine Frage stellen` was removed and its cell explicitly closed; one unused unregistered source declaration was removed; and exact successor fingerprints were rebound.

Stable IDs/order, learner-facing definitions/translations, expression structure and all **1240 examples** remain preserved. Runtime/UI were not changed.

Checkpoint: `Menschen-A1-Verben-v3.3.6-PostLock-Repair1-Stage4-INDEPENDENT-REAUDIT-PASS-CHECKPOINT.zip`
Checkpoint SHA-256: `b3c1601b5583ed60db2c79acd80f38416f4e36078880fb24b8662e11decda634`
Post-package verification SHA-256: `50fd67e5090b3d2f7e28256467cd4be6e984f50248962dfbe9703df40ba07358`

Next milestone: **Stage5 clean delivery projection through the v3.3.6 anti-bypass gate**. Runtime CURRENT is resolved only at Stage6.
