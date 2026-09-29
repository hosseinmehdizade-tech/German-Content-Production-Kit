# Menschen B1 Verben — Post-Repair Richness Audit

Status: **AUDIT COMPLETE — REPAIR REQUIRED BEFORE RE-LOCK**

Audited authority: `Menschen-B1-Verben-v3.3.2-PostLock-Repair1-Phase2-Batch0020-CHECKPOINT.zip`  
SHA-256: `d1f59c5ae01d0684521103081cf9afe595c45e8a56060bbe06c18d0892261f8c`

## Executive result

Phase 2 is complete for **395/395** active cards and the enrichment improvement is large: **2502 relations**, **388/395 (98.23%)** cards enriched beyond Rektion, and **116/116** expressions with structured components. Core identity/example/relation integrity passes.

The successor is **not re-lock-ready yet** because the fresh full-dataset audit found two bounded repair defects and one residual review item.

## Current metrics

- Active cards: **395** = 279 senses + 116 expressions
- Examples: **1580**, exactly four per active card
- Relations: **2502**
- Relation types: REKTION 400; SYNONYM 933; COLLOCATION 637; WORD_FAMILY 252; COMPONENT 243; RELATED 22; ANTONYM 15
- Cards enriched beyond Rektion: **388/395 (98.23%)**
- Expressions with components: **116/116**
- Expressions with argument slots: **86/116**
- Relation density per card: min 1, median 6, mean 6.33, max 15

## Findings

### F001 — BLOCKER: evidence source-ID mismatch

**109 relations** (58 from Batch0016, 51 from Batch0017; 32 cards) cite `DUDEN_SYNONYM`, while the canonical source registry contains `DUDEN_SYNONYME`. These 109 relations have no second registered evidence ref. This is an identifier-integrity defect and must be normalized before re-lock.

### F002 — REPAIR REQUIRED: missing COMPONENT links for first 8 structured expressions

All expressions have `structure.components`, but these eight Batch0001 expressions have resolved component IDs and no explicit COMPONENT relation:

- `mb1m-lu-0001` — sich verabschieden
- `mb1m-lu-0002` — Abschied nehmen
- `mb1m-lu-0005` — sich durchsetzen
- `mb1m-lu-0007` — sich verstärken
- `mb1m-lu-0009` — sich abschwächen
- `mb1m-lu-0015` — sich übernehmen
- `mb1m-lu-0016` — das Vertrauen verlieren
- `mb1m-lu-0019` — Umgang mit jdm./etw.

### F003 — REVIEW: 7 cards remain Rektion-only

Six have documented conservative no-force decisions. `mb1m-lu-0037` (`etw. ziehen; an etw. ziehen`) has no equivalent explicit exception record and must be re-reviewed or documented.

## What passed

- 395/395 active IDs unique; expression canonical forms unique.
- 1580/1580 examples correctly attached; exactly four per card.
- 2502/2502 relation IDs unique; no duplicate semantic relation keys.
- Relation source owners and target endpoints valid; no self-relations.
- Every relation has provenance refs.
- All lexeme/sense/expression/example provenance refs use registered source IDs.
- 116/116 expressions have structured components; all 95 resolved component object IDs are valid.
- 30 expressions without argument slots are fixed/subject-driven or use optional location/time information; no blanket slot repair is justified.

## Next durable step

Create a bounded **PostLock Repair1 Phase3 audit-fix** checkpoint: normalize `DUDEN_SYNONYM` to the registered identity, add the eight missing COMPONENT-link sets, and resolve/document `mb1m-lu-0037`; then rerun the full audit. Do not re-lock or project to runtime before that passes.
