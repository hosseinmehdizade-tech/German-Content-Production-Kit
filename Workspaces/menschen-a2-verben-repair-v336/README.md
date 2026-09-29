# Menschen A2 Verben Repair v3.3.6

Current durable milestone: **Stage3B Collocation closure PASS**.

A useful correction was found here: the 38 supposedly open collocation cells were not real lexical gaps. The Repair1 canonical already contains learner-facing connection chunks for all 38; Stage3A had classified them as missing because its baseline detection looked only at outgoing COLLOCATION relation records.

- Active canonical: **292 targets = 228 verbs + 64 expressions**
- Stable IDs/order: **292/292 preserved**
- Examples: **1168 DE + 1168 FA + 1168 EN**, unchanged
- Rektion: **292/292 final**
- Synonym: **292/292 final**
- Collocation: **291 VERIFIED_PRESENT + 1 CLOSED_NO_FORCE = 292/292 final**
- Reclassified existing Repair1 connections: **38**
- New collocation relations: **0**
- Relations: **1068 -> 1068**, byte-identical
- Candidate ledger: **422 = 272 ACCEPTED + 150 REJECTED + 0 DEFERRED**
- Richness: **3429 final / 1079 unresolved of 4508**
- Fresh validators: **8/8 PASS**
- Package: CRC PASS; manifest **73/73**; SHA256SUMS **74/74**
- Library rematerialization: **PASS exact SHA-256 + byte compare**
- Checkpoint SHA-256: `2f80dd18eed2808f274f739e8de524bfedb0964c8f5581e617d0b3516b15e4ba`
- Historical locked parent, runtime and UI were not changed.

Next milestone: **Stage3B Related closure (218 unresolved)**, followed by Antonym / Word Family / NVV.
