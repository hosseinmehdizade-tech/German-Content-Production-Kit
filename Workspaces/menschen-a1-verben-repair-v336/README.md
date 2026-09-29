# Menschen A1 Verben Repair v3.3.6

This workspace is a **delta repair successor** of the immutable locked A1 Verben release.

Current durable milestone: **Stage3B in progress — explicit-source Rektion + Duden global-transitive Rektion clusters PASS**.

- Parent locked release: `German-Flashcards-Pro-v435-R69-Menschen-A1-Verben-v3.3.2-LOCKED.zip`
- Parent SHA-256: `6651704a8a508f66cd850a88565be6a151e047d442e8c375c3860beff5b266db`
- Active canonical: **310 targets = 247 senses + 63 expressions**
- Examples: **1240 unchanged**
- Canonical relations: **297**
- Stage3A baseline: **4776 cells; 2624 final / 2152 unresolved**
- Definitions: **3/3 baseline defects repaired**
- Structure components: **63/63 expressions complete**
- Argument slots: **63/63 final = 43 VERIFIED_PRESENT + 20 CLOSED_NO_FORCE**
- Component relations: **63/63 final = 47 VERIFIED_PRESENT + 16 CLOSED_NO_FORCE**
- Rektion: **187/310 VERIFIED_PRESENT; 123 unresolved**
- Explicit-source/argument-slot Rektion cluster: **94 accepted**
- Duden global-transitive Rektion cluster: **18 accepted**, each only where the headword entry is unambiguously transitive and sense-aligned; relation value `+ Akkusativ`
- Candidate ledger: **275 = 234 ACCEPTED + 41 REJECTED + 0 DEFERRED**
- Current richness: **2894 final / 1882 unresolved**
- Current checkpoint: `Menschen-A1-Verben-v3.3.6-PostLock-Repair1-Stage3B-REKTION-DUDEN-TRANSITIVE-CHECKPOINT.zip`
- Checkpoint SHA-256: `9a411d81bdb23b299fed2c43702259b265ec29629af7426de8708158e1ee16fa`
- Canonical SHA-256: `bc99b54168449273cb0cd8a9bb4301505ce0414f0066bd7808f48540e894803f`
- Library rematerialization: **PASS exact SHA-256 + byte compare**
- Post-package: **CRC PASS; SHA256SUMS 32/32; manifest 31/31; 5/5 fresh current validators PASS**
- Historical locked bytes and prior checkpoints were not changed.

Next Stage3B milestone: **review the remaining 123 Rektion cells through Duden mixed/intransitive/prepositional routes**. Never infer `CLOSED_NO_FORCE` from `itr.` alone when a governed prepositional complement may exist; preserve sense alignment and do not chase relation density.
