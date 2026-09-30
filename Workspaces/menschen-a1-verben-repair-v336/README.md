# Menschen A1 Verben Repair v3.3.6

This workspace is a **delta repair successor** of the immutable locked A1 Verben release.

Current durable milestone: **Stage3B in progress — Antonym 100% disposition PASS**.

- Parent locked release: `German-Flashcards-Pro-v435-R69-Menschen-A1-Verben-v3.3.2-LOCKED.zip`
- Parent SHA-256: `6651704a8a508f66cd850a88565be6a151e047d442e8c375c3860beff5b266db`
- Active canonical: **310 targets = 247 senses + 63 expressions**
- Examples: **1240 unchanged**
- Canonical relations: **625**
- Rektion: **260 VERIFIED_PRESENT + 50 CLOSED_NO_FORCE + 0 unresolved = 310**
- Synonym: **247 VERIFIED_PRESENT + 63 CLOSED_NO_FORCE + 0 unresolved = 310**
- Antonym: **23 VERIFIED_PRESENT + 287 CLOSED_NO_FORCE + 0 unresolved = 310**
- Final antonym closure: **306 reviewed = 19 newly VERIFIED + 287 CLOSED_NO_FORCE; 19 new ANTONYM relations**
- ANTONYM relations total: **23**
- Candidate ledger: **1003 = 562 ACCEPTED + 441 REJECTED + 0 DEFERRED**
- Current richness: **3607 final / 1169 unresolved of 4776**
- Current checkpoint: `Menschen-A1-Verben-v3.3.6-PostLock-Repair1-Stage3B-ANTONYM-FINAL-CLOSURE-CHECKPOINT.zip`
- Checkpoint SHA-256: `3eabfcbb40cdf94ad66e6a7bf56d17657bb1fe5595917b5434e3a8fee136a28d`
- Canonical SHA-256: `6fdb5ec6bfa3f99cc39da9ca8efefacda7db28d2989f0f162ea9b81a225d6865`
- Duden Bedeutungswörterbuch source SHA-256: `a7c65e270e73eb799d535c3084431061adffeb45118b532f84b023a4342edb71`
- Library rematerialization: **PASS exact SHA-256 + byte compare**
- Post-package: **CRC PASS; SHA256SUMS 102/102; manifest 101/101; 5/5 fresh current validators PASS**
- Historical locked bytes and predecessor checkpoints were not changed.
- Identity, definitions, translations, **1240 examples**, morphology, expression structure, completed Rektion/Synonym state, runtime and UI were not changed.

The remaining **306** antonym cells were reviewed against registered `DUDEN_BEDEUTUNG_10` evidence using explicit `/Ggs./` markers on the target headword plus exact reverse `/Ggs./` lookup. Only active-sense alignments were accepted. A surface homograph false positive such as verb `überlegen` versus adjective `überlegen` was rejected rather than serialized.

Representative accepted claims include `absagen ↔ zusagen`, `abfahren ↔ ankommen`, `aussteigen ↔ einsteigen`, `einladen ↔ ausladen`, `lachen ↔ weinen`, `anfangen ↔ beenden`, `ausmachen ↔ anmachen`, `ausschalten ↔ einschalten`, `mieten ↔ vermieten`, `anmelden ↔ abmelden`, `zumachen ↔ aufmachen`, `öffnen ↔ schließen`, `ausräumen ↔ einräumen`, and `anziehen ↔ ausziehen`.

The other **287** cells are explicitly **CLOSED_NO_FORCE** after those bounded routes were exhausted. No density target was used.

Next Stage3B milestone: **Collocation**, then **Word Family → Related → NVV**.
