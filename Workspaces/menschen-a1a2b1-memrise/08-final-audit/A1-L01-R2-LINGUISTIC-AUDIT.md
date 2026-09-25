# Menschen A1-L01 — Final Audit Round 2

**Status: REVIEW_REQUIRED**

Exact historical authority: `German-Flashcards-Pro-v413-R47-Menschen-A1-L01-GOLDEN.zip`
SHA-256: `0507cf3209942af303b8dfdb25bbf57fbc9c8e468dad76eaebea4f661a9d8075`

Round 2 independently reviewed 118 targets, 472 DE examples, 472 FA translations, 472 EN translations, noun morphology, verb morphology/separability, 21 relations, Rektion, sense/source alignment, register/CEFR suitability and pragmatics.

Result: **96 CLEAN · 12 REPAIR_REQUIRED · 6 NATURALNESS_REPAIR · 1 IDENTITY_REVIEW_REQUIRED · 3 ADVISORY**. There are 37 findings across 22 target IDs.

Highest-priority confirmed defects:
- `ma1m-lu-0095 eins`: two German examples use `eins` before nouns (`eins Personen`, `eins Bücher`); both English translations are also ungrammatical.
- `ma1m-lu-0081 spielen`: `Klavier spielen` leaks into the instrument-playing sense while this source-scoped card is game-playing.
- `ma1m-lu-0091 Herkunft`: card mixes personal/national origin with origin-of-a-thing (`Herkunft des Wortes`), contrary to the source-scoped sense.
- `ma1m-lu-0071 rückfragen`: `separable=false` is inconsistent. Do not blindly fill finite forms; Duden notes Infinitiv and Partizip II are the common forms.
- `ma1m-lu-0066 hören`: explicit identity decision required because the source row spans `hear` + `listen` while the active profile says split when meaning changes.

Other required repairs include direct-speech punctuation on 0004–0008, Persian `مونث` -> `مؤنث`, Persian `یک اطلاعات`, the self-contradictory `Wir sind null Personen.`, and several Persian naturalness fixes.

Dataset advisories: numeral examples 0096–0118 are highly templated; all 472 examples use blanket `register=neutral`, which is not trustworthy for every register-sensitive target.

Historical LOCKED ZIP remains immutable. Build a repaired successor only after resolving the `hören` identity decision, then rerun semantic/profile validation, exact-4 examples, relation evidence, Canonical→Projected→Universal-v2 parity, package rehash/hygiene, and CURRENT runtime acceptance.

Detailed local report hashes:
- Markdown: `8b9324c1f6f53135dfc601ab95df3e8b2760009ef82fc11ee754c8f78961952c`
- JSON: `ed26d03f23ea75ca91b376ae85b60053ff7463d2f0b2c02818250cfdc6f73819`
- Card ledger TSV: `3a2c87764b551512d2761ed5bf5430f2e807d20ac49b930b6d3e1e0c5c887089`
