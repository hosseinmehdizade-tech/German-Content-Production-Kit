# Lesen R37 — contextual trilingual model first pass, lessons 031–040 (2026-11-08)

**Authority:** exact R36 parent master SHA `2e942a095a61a50143a0b8c6ea9a221324ecda1421dbaebaafe4e84ef8da8772`, runtime SHA `50a4583bec1ef3be4ba5b3fe9255186f87ba6a8e35ef0ecb6d71442ed830725a`, Library ZIP SHA `c9b7825884af2c0cae2088a534fc53d58baf2d70b6039fd53352602b11350915` (ID `libfile_485165d7a7c88191abcbc5a8f76a547b`). No fall back to old book/PDF or stale Git source.

## Actual content review and changes

The AI model compared the German source to Persian and English in context for all **70 actual sections** of LES-PRES-031..040. Exactly **10 sections / 18 local translation fields** changed. Source German sentences, paragraph identities, 340 question records, 350 vocabulary entries, all 669 curated grammar examples and 3,539 derived fulltext grammar occurrences are untouched.

- **031/p02 (FA/EN):** Restored the explicit condition *mit klaren Aufgaben* and learning beyond mere media consumption.
- **031/p03 (FA):** Restored *durch Benachrichtigungen* and the less absolute *stören* rather than destroying concentration.
- **031/p04 (FA):** Corrected a misconstrued *nicht das Smartphone selbst ... sondern der Auftrag*: the teaching task matters, rather than the phone being “an important task.”
- **031/p06 (FA/EN):** Restored German concessive *obwohl digitale Selbstkontrolle ...* rather than two disconnected/additive assertions.
- **034/p06 (FA/EN):** Restored concessive relation and that personal performance and real professional experience remain decisive.
- **036/p06 (FA/EN):** Restored source concession involving parental/social influence, and *Handlungskompetenz* as a capacity to act, not merely decide.
- **037/p02 (FA/EN):** Restored explicit pedagogical expertise required *also at universities* beyond subject expertise.
- **038/p03 (FA/EN):** Preserved explicit threat to educational quality and missing teaching staff, support and funding, rather than generic “problematic.”
- **039/p02 (FA/EN):** Preserved fair agreement and both increased independence and financial relief for parents.
- **040/p02 (FA/EN):** Preserved authority that supports teaching *while allowing critical questions* rather than simply being useful.

Full exact German text anchors, old/new translation fields and a **70-section model-first-pass ledger** are in `03-Reports/LESEN-R37-STAGE4-BATCH-031-040-REVIEW-LEDGER.json`.

Cumulative first-pass cohorts: R34 72 + R35 70 + R36 70 + R37 70 = **282/478 sections**; **196 not yet first-pass**. First-pass does **not** certify that the 282 are error-free, nor constitute external expert verification.

**Unresolved discourse/grammar watchlist**: 017/p06, 018/p06, 025/p06, 039/p06, 040/p06: `obwohl` clauses with additive translations or rhetorically awkward German source. Not blindly changed; each needs source/context/grammar dependency evaluation before a German rewrite.

## Actual scoped technical QA

- Separate source/runtime delta verifier **7,386/7,386 PASS** and **15/15** intentionally malformed source mutations rejected; verifies all unchanged DE, grammar, questions, vocabulary and full runtime projection.
- Exact R32 curated grammar currentness and R33 known syntactic counterexample prevention gates **PASS** on R37.
- Genuine current v505 `reading-content-import-v38.js`, SHA `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`, executed in isolated Node VM. Native validator **PASS zero errors/warnings**, **10/10** malformed runtime payloads rejected; in-memory 68 readings, 340 exercises. **Not** a real installed Chrome/IndexedDB Stage6 test.
- The ten source-anchored meaning-direction probes are model-authored spot checks, **not independently verified complete language meaning**.
- Full independent 478-section DE/FA/EN Stage4 **HOLD**, original full nine-lens grammar **NOT_RERUN**, actual Chrome IndexedDB Stage6 **NOT_RUN**, Stage7 **NOT_RELEASED**.

## Durable recovery and separation

- R37 master SHA `5849aea046d16244e8449c5f333a4a04cc13fb99e199882015f93318bc66f9d7`; runtime SHA `056042705503393e9c3c9b8727c678f052125cc8a25eb57cd568d810ff56be93`.
- ZIP `Lesen-R37-FOURTH-TEN-TRILINGUAL-SEMANTIC-BATCH-CANDIDATE-20261108.zip`, SHA `f86d95e0de70736b650bb1894bd5569e6331b3934be67ee2803dbed437e0fb09`, 3449164 bytes, 17 entries and 16/16 internal SHA checks/CRC PASS. Stable owner Library `/Flasch kart/German-Content-Production-Kit/Content/Lesen/Checkpoints/Lesen-R37-FOURTH-TEN-TRILINGUAL-SEMANTIC-BATCH-CANDIDATE-20261108.zip`, ID `libfile_ad1d439459bc8191ad9278c21974daa2`.
- Library postupload independent re-materialization **exact SHA256 and raw byte-by-byte compare PASS**. Extracted Library ZIP and `python -B 04-Tools/verify_portable_r37.py` reproduced exact candidate bytes, 7,386 independent QA, 15 negative source probes and actual v505 JS preentry **PASS**.
- Original v1.3.0 curated CURRENT SHA `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` unchanged. No changes to application UI/runtime, user learner FSRS/SRS state, other workstreams, original publisher PDF or Library deletions.

**Next R38:** exact R37 Library candidate, contextual trilingual first pass lessons **041–050**, preserve previous receipts, carry watchlist and continue toward a genuine complete Stage4 before any Stage6 / FINAL.
