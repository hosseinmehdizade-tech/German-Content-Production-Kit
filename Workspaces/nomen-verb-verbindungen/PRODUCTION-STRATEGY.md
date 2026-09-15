# NVV Production Strategy — Scalable Hybrid Pipeline

Updated: 2026-09-15
Branch: `nvv-production`
Workspace: `Workspaces/nomen-verb-verbindungen`

## Decision
Use a **hybrid pipeline**:

- Global structural work is done once across the full source.
- Learner-content enrichment is produced in bounded end-to-end batches.
- Ambiguous/polysemous cases are quarantined into a persistent review queue instead of blocking safe production.

Do **not** use a pure field-by-field whole-corpus pipeline such as: all Persian meanings for 2,493 expressions -> all German definitions -> all examples -> all relations. That creates cross-field drift, delays QA feedback, and makes partial recovery harder.

Do **not** continue 13-card micro-batches. They were pilots only.

## Global layer — full corpus, once

These fields/decisions should be completed or maintained globally before/while enrichment progresses:

1. source inventory and source locator
2. stable expression ID
3. source class: `nvv`, `fvg`, `idiom`
4. canonical surface/headword
5. semantic split/merge identity
6. valency / Rektion skeleton when source-supported
7. lexical components (noun/verb etc.)
8. unresolved sense/ambiguity queue

Already established as of Batch 0002:
- 2,475 source bullet items
- 2,493 provisional expression identities
- 221 slash/variant source items reviewed
- 17 semantic split source items
- 26 cards completed
- 1 explicitly preserved polysemy blocker: `etw. / jdn. in Anspruch nehmen`

## Production batch unit

Default batch size: **100 expressions**.

After two consecutive 100-card batches pass all validation and cumulative checks without systematic defects, batch size may increase to **150**. Do not exceed 200 without explicit evidence that quality and validation remain stable.

A batch is selected from safe expressions only. Ambiguous records go to the review queue and are replaced by the next safe records so the batch can still reach its target size.

## Internal stages for EVERY production batch

### B1 — Evidence + sense lock
For each selected expression:
- verify the intended sense
- bind evidence to the expression/sense
- preserve source form and source subtype
- confirm Rektion/pattern if claimed
- quarantine ambiguous/polysemous/conflicting items

Gate: no learner content is generated for a sense that is not locked well enough to describe safely.

### B2 — Core meanings
Produce together for the locked sense:
- `definition_de`
- `persian_meaning`
- `english_gloss`

These three are generated/checked as one semantic bundle, not in separate corpus-wide passes.

Gate: DE/FA/EN must describe the same sense.

### B3 — Structure + lexical graph
Produce/confirm:
- structure / Rektion
- noun/verb components
- semantic equivalent/simple verb where supported
- related lexical units
- Wortfamilie / sibling expressions where evidence-supported
- typed relations for Word Explorer/Wortnetz

Gate: relation targets must be stable IDs or safely resolvable exact unique lexical targets; ambiguous targets fail closed.

### B4 — Examples
Create exactly **4 original German learner examples per card**, then add independent FA + EN translations.

The four examples should collectively cover, where natural:
1. simple canonical use
2. valency/object/preposition pattern
3. another tense/person/syntactic frame
4. natural B2/C1-style context/register use

Do not copy source example sentences verbatim into production learner examples. Source examples are evidence, not output text.

Gate: examples must be natural, sense-aligned, non-duplicative, structurally correct, and translation-aligned.

### B5 — Automated + linguistic QA
Run batch-level and cumulative validation for:
- required fields
- exactly 4 examples
- DE/FA/EN completeness
- stable IDs / duplicates
- semantic type integrity
- NVV vs collocation separation
- component resolution
- reverse Wortnetz links
- source/evidence references
- projection compatibility

Any failing card is fixed or moved to review; do not lower the gate to hit the batch count.

### B6 — Projection + runtime regression
Project completed cards to the app-facing format and run relevant importer/lexical graph/runtime regression tests against the current pinned/approved app baseline.

This is a regression check, not a visual redesign step.

### B7 — Persistent checkpoint
After a successful batch:
- append to cumulative canonical dataset
- append/update cumulative projected dataset
- update validation/acceptance reports
- update review queue
- update `CHECKPOINT.json`
- update `HANDOFF-READ-FIRST.md`
- update this strategy only if the strategy itself changes
- persist text artifacts to `nvv-production`
- create a downloadable cumulative checkpoint ZIP

No successful batch exists only in chat or `/mnt/data`.

## Why this hybrid approach is preferred

A pure whole-corpus field pass (for example 2,493 Persian meanings first, then 2,493 definitions, then 9,972 examples) is rejected because:
- sense decisions made later can invalidate earlier translations
- examples expose semantic/valency problems that should feed back immediately
- relations depend on the final sense and canonical identity
- QA feedback arrives too late
- a chat/session failure leaves huge partially coherent layers
- later contract changes can invalidate thousands of disconnected fields at once

End-to-end batches keep every completed card internally coherent and immediately testable while the global identity layer preserves cross-card consistency.

## Quality-control cadence

- Every batch: full batch validation + cumulative structural validation.
- Every 500 completed cards: corpus-level audit for duplicate meanings, relation consistency, repeated/generic examples, Persian terminology consistency, register/CEFR drift, and graph connectivity.
- At full enrichment completion: global QA before final delivery projection/release.

## Progress accounting

Track separately:
- source bullets
- canonical expression identities
- completed cards
- review-queue items
- completed examples
- batch count
- last completed stable ID / selection cursor

Never report "percent complete" from source bullets when the production target is canonical expression identities.

## Current next move

Batch 0003 is the first scalable production batch.
Target: **100 safe expressions** end-to-end through B1–B7.

Batch 0001 and Batch 0002 remain bounded PASS and are not regenerated unless a contract/schema change explicitly invalidates them.
