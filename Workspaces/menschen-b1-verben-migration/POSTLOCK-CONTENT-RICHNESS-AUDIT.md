# Menschen B1 Verben v3.3.2 — Post-lock Content & Richness Audit

Status: **REVIEW_REQUIRED_BEFORE_PEDAGOGICAL_FINALITY**

The locked artifact remains byte-valid and Stage7 runtime/package acceptance remains intact. This audit checks a different axis: lexical richness, identity consistency and usefulness of the Word Explorer/Wortnetz layer.

## Core integrity
- 400/400 unique card IDs.
- 1600 German examples; exactly 4 per card; FA + EN present.
- 279 german-verb + 121 Expression.
- Morphology/Rektion/core meanings structurally complete.

## Richness findings
- 472 relations total: 402 REKTION, 64 SYNONYM, 4 ANTONYM, 2 RELATED.
- 339/400 cards (84.75%) have only Rektion and no non-Rektion semantic relation.
- 0 COLLLOCATION relations.
- 0 WORD_FAMILY relations.
- 0 COMPONENT relations.
- structure.components non-empty: 0/121 expressions.
- structure.argument_slots non-empty: 0/121 expressions.
- Expression inventory exists (80 reflexive_verb, 20 multiword_expression, 13 nvv, 8 collocation), but the expression graph is structurally under-linked.
- Projected visible detail coverage: English 400, Rektion 400, Synonyme 56, Antonyme 4, Verwandt 2.

## Identity findings under MEM-009
Exact duplicate active fronts requiring reconciliation:
- sich amüsieren: mb1m-lu-0033, mb1m-lu-0034, mb1m-lu-0392
- sich behaupten: mb1m-lu-0072, mb1m-lu-0073
- sich bemühen: mb1m-lu-0441, mb1m-lu-0442

Orthographic/lexical variant duplicate candidate:
- achtgeben / Acht geben: mb1m-lu-0276, mb1m-lu-0370

At least five active cards are likely excess if the one-card multi-meaning rule is applied strictly; final reconciliation must remain evidence-based.

## Conclusion
Core learning content is strong, but the lexical-network/collocation layer is not sufficiently enriched to call the set fully equipped. A repair successor should preserve the locked artifact and add an explicit evidence-backed enrichment pass plus identity reconciliation.

Library audit:
- /German-Content-Production-Kit/Checkpoints/Menschen-B1-Verben-v3.3.2-POSTLOCK-CONTENT-RICHNESS-AUDIT.md
- /German-Content-Production-Kit/Checkpoints/Menschen-B1-Verben-v3.3.2-CARD-RICHNESS-MATRIX.csv
