# Unified Vocabulary Import & Presentation Policy v1.1.0

Status: ACTIVE MANDATORY

## Core invariant
Ordinary German lexical content has two independent axes:
1. **Presentation/transport family** — always `de-vocabulary` for new ordinary vocabulary.
2. **Linguistic semantics** — POS, morphology, gender, Rektion, expression type, structure, relations and provenance.

Semantic richness MUST NOT select or override a presentation family.

## Authority precedence
- An explicit supported outer `card_type` / `cardType` is authoritative.
- Runtime heuristics may infer legacy `german-verb` only when an old record has no explicit supported card type.
- Legacy schema markers are compatibility provenance, never presentation selectors for newly produced neutral cards.

## New-production contract
- `card_type = de-vocabulary` for every ordinary lexical Sense/Expression.
- `custom_fields.presentation_contract = gfp-vocabulary-neutral@1` is mandatory.
- POS/morphology/gender/Rektion/structure remain semantic data.
- Presentation-selector namespaces are closed: top-level or recursively nested layout/template/renderer/presentation/schema/card selector keys are rejected case-insensitively.
- `source_schema_profile` is the explicit provenance-only exception; `presentation_examples` is content, not a selector.

## Compatibility
Historical locked artifacts are not rewritten. Runtime may still accept explicit `german-verb` and old schema-only records, but compatibility logic must not override an explicit neutral type.

## QA
Stage 5 validates outer type, mandatory neutral contract, neutral schema lineage, and hidden selectors recursively. Stage 6 verifies cross-POS presentation parity and legacy compatibility separately.
