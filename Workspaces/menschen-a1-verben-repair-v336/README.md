# Menschen A1 Verben Repair v3.3.6

Final durable state: **Stage7 exact-final RELOCKED PASS on German Flashcards Pro v451-R85**.

- Release: `German-Flashcards-Pro-v451-R85-Menschen-A1-Verben-v3.3.6-Repair1-RELOCKED.zip`
- Release SHA-256: `cf3cc7e28f8af43369a2cf56d293f095c4524841e796a7d171d23d19b36036c3`
- Runtime `01-App`: **71/71 byte-identical to exact VERIFIED/FINAL v451-R85**
- Content: **310 cards = 247 Verb + 63 Expression**
- Presentation: **310/310 de-vocabulary + gfp-vocabulary-neutral@1**
- Examples: **1240 DE + 1240 FA + 1240 EN**
- Relations: **768**
- Source audio: **310 refs / 275 unique**; zero-audio targets: `ma1m-lu-0073`, `ma1m-lu-0074`
- Exact-final acceptance: **95/95 PASS = 48/48 Phase1 + 26/26 Phase2 + 21/21 v451 envelope**
- Commit manifest: **VERIFIED / 310**
- Static post-package: **CRC PASS; root SHA256SUMS 326/326; 327 package files; runtime 71/71 exact; JSON 140/140; hygiene PASS**
- Library release rematerialization: **PASS exact SHA-256 + byte compare**
- Stage7 checkpoint SHA-256: `3ae554eda62de03e8fe95a97fc3e85cfc7f33477a987ffe600790fb8976f02e1`
- Content lock state: **RELOCKED**
- Visible UI change: **NONE**

This repair successor is complete. Do not regenerate or mutate the relocked content without a real defect or an explicitly opened new repair successor. Runtime may advance independently.


## Post-relock overall review — 2026-09-30

A fresh exact-v451 learner-facing presentation review found real projection defects despite prior structural/runtime PASS gates. Repair1 bytes remain immutable and RELOCKED, but a narrow Repair2 is recommended.

- 247/247 Verb cards: front morphology core slots are empty although canonical morphology exists.
- 69 cards / 71 values: canonical RELATED values are rendered under Synonyme.
- 30 cards: literal `REKTION` is visible to the learner.
- 24 cards / 28 values: internal structure-role tokens are visible.
- 310/310 cards: German definition is duplicated as `Hinweis`.

The canonical lexical authority remains broadly strong; the defects are concentrated in Stage5 projection / v451 presentation binding. Do not mutate Repair1; open Repair2 for these bounded fixes.
