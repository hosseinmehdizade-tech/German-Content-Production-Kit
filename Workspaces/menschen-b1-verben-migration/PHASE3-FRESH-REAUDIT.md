# Menschen B1 Verben — Phase3 Fresh Full Re-Audit

Status: **PASS — CANONICAL AUDIT GATE CLOSED**

Audited content checkpoint:
`Menschen-B1-Verben-v3.3.2-PostLock-Repair1-Phase3-AuditFix-CHECKPOINT.zip`

- checkpoint SHA-256: `38f31d50290ab9a541174a86eabd820652adfe330cbdee09bc78b24c5bdd6203`
- canonical SHA-256: `e431a855027bae94166be776c562704ace03e6607f47bdd555aa69d605a32273`

## Full re-audit result

- 395 active cards = 279 senses + 116 expressions
- 1580 examples; exactly 4 per card
- 2510 relation IDs, all unique
- duplicate semantic relation keys: 0
- relation source owners/endpoints: PASS
- self-relations: 0
- all relation and object provenance source IDs registered
- 95/95 resolved component object IDs valid
- 116/116 expressions have structured components
- 116/116 expressions have at least one COMPONENT relation
- 86/116 expressions have argument slots
- 388/395 cards (98.23%) enriched beyond Rektion
- 7 Rektion-only cards remain, all seven now explicitly documented as conservative no-force decisions

Relation profile:
REKTION 400; SYNONYM 933; COLLOCATION 637; COMPONENT 251; WORD_FAMILY 252; RELATED 22; ANTONYM 15.

## Prior audit findings

- **F001 PASS:** 0 `DUDEN_SYNONYM` refs remain. Exactly 109 prior relations changed only by source-ID normalization to registered `DUDEN_SYNONYME`.
- **F002 PASS:** exactly 8 COMPONENT relations were added; all 116 expressions now have an explicit COMPONENT relation.
- **F003 PASS_CONSERVATIVE:** `mb1m-lu-0037` is explicitly closed as `CLOSED_CONSERVATIVE_NO_FORCE`; no relation was invented to increase density.

## Bounded-diff verification

Sources, lexemes, senses, expressions and examples are unchanged from Batch0020. No prior relation was deleted. The only prior-relation mutation is the 109 source-ID corrections; exactly eight new COMPONENT relations were appended.

109 common inherited files are byte-identical; only `README.md`, `MANIFEST.json` and `SHA256SUMS.txt` changed, plus five intentional Phase3 files were added.

Package integrity of the Phase3 content checkpoint: manifest 115/115 PASS; checksums 116/116 PASS; ZIP CRC PASS.

## Decision

The **canonical-content audit gate is closed**. This does not claim Stage5, Stage6, runtime acceptance or final re-lock.

Next: repair-successor **Stage5 delivery projection under active v3.3.5**, enforcing neutral `card_type=de-vocabulary` and `custom_fields.presentation_contract=gfp-vocabulary-neutral@1`. Stage6 must resolve CURRENT again at execution before runtime/presentation acceptance.
