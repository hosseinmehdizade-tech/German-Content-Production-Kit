# General German Content Generation Master Prompt v3.1.13
## Source/Profile Layering + Thin-Card Prevention

This is the normative overlay on v3.1.12. Architecture v3.1.5 and semantic contract 3.1.3 remain unchanged.

## 1. Separate source-canonical and product-completeness authority

A new source has two different profile layers and they MUST NOT be conflated:

1. **Source canonical profile** — Stage 1/2 authority for source identity, allowed unit types, IDs, source-supported morphology/fields and source-only canonical validation. It may legitimately be sparse because the source itself may contain only one example and no definition.
2. **Product completeness profile/floor** — Stage 3/4/6 authority for the learner-facing Flashcards Pro card that must exist after enrichment.

A source-canonical profile is NEVER sufficient evidence that a learner-facing rich card is complete.

For `flashcards-pro-german-rich-card`, the mandatory generic product floor is `GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json` unless the user explicitly approves a named relaxation. A source-specific product profile may tighten or specialize this floor, but may not silently weaken it.

## 2. Thin-card failure mode is a hard defect

The following pattern is prohibited:

- source has one example;
- Stage 2 source profile sets one example as acceptable;
- Stage 3 merely translates that one example;
- external lexical enrichment is skipped;
- product completeness reports warnings only;
- runtime proves only that the sparse data imports;
- release is called Final.

This is a **false product PASS** even if transport and runtime shapes are valid.

Stage 3 cannot PASS for a non-empty rich-card verb dataset when external lexical enrichment was never attempted. Missing evidence may remain missing, but attempts/failures must be recorded and systematic zero-enrichment is a hard failure, not a successful minimalist interpretation.

## 3. Product floor for learner-facing richness

For the active generic rich-card floor:

- verbs require `persian_meaning`, `definition_de`, full required source-level core morphology, and at least 4 usable German examples;
- phrases require their structure, Persian meaning and at least 4 usable German examples;
- each unit requires at least one learner-facing German example with an English translation; additional German examples may remain German-only when their evidence is stronger than any available translation;
- collocation/synonym/antonym/Rektion content remains evidence-bound and must never be fabricated to hit a quota;
- verb lexical-detail coverage has a dataset-level system-health floor to detect a disabled/broken enrichment path. This is not a per-card truth quota.

If trustworthy lexical detail is unavailable for a particular unit, report the gap. If lexical detail is unavailable for almost the entire ordinary A1/A2/B1 verb dataset, treat that as a pipeline/parser failure requiring investigation.

## 4. Mandatory product-floor gate

Stage 4 MUST run:

`Verification/validate_rich_card_product_floor_v1_0_0.py`

against:

- the exact enriched canonical artifact;
- `Prompt/GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json` (or an explicitly stricter source-specific product profile);
- the Stage 3 evidence index containing per-unit external-evidence attempt records.

A source profile that says one example is acceptable does not override this gate.

## 5. Runtime/Presentation acceptance must test product semantics, not just transport

Stage 6 must prove both transport/runtime integrity and learner-visible product semantics. For representative rendered cards from every learning-unit type, assert as applicable:

- required definition is visible for verbs;
- the minimum example count survived import and is rendered;
- at least one English example translation is present per sampled unit;
- morphology survived;
- multi-value lexical details render as separate items;
- no raw JSON leaks;
- a rich card is not rendered with the generic “no supplementary details” state when the canonical artifact contains lexical details.

In addition, the imported canonical payload MUST pass the product-floor validator before Presentation acceptance can PASS.

## 6. Checkpoint authority

Every source `CHECKPOINT.json` must record both:

- `source_canonical_profile`
- `product_completeness_profile`

and their versions/paths. A stage may not cite the source-canonical profile as the final product-completeness authority.

## 7. Invalidation rule for this defect class

If a released dataset is discovered to have passed because source-canonical sparsity was mistaken for product completeness:

- preserve Stage 1 and a semantically correct source-only Stage 2;
- invalidate Stage 3 and every downstream stage;
- repair enrichment and evidence;
- rerun Stage 4 product-floor/lexical QA, Stage 5 projection, Stage 6 runtime/presentation and Stage 7 packaging;
- record the prior false PASS and root cause in Git.

All v3.1.12 quality, evidence, durability, no-legacy, no-fabrication and seven-stage rules remain binding.
