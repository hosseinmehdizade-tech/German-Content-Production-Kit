# Menschen A1 Legacy Enrichment Recovery Policy v1.0.0

Purpose: safely reuse trustworthy enrichment from older Menschen A1 artifacts without repeating the old modeling mistake `NVV == Kollokation`.

## Identity mapping

Legacy IDs such as `MEN-A1-0001` and current canonical IDs such as `MEN-A1-00001` may be matched only after strict numeric-ID and row-order parity checks. Zero-padding is formatting, not a new identity. Any collision, missing ID, reordering mismatch, or sense mismatch is REVIEW_REQUIRED.

## Candidate extraction

Read non-absence values from legacy `NVV1..NVV6` as `legacy_phrase_candidate` records with original column, card ID, text and source artifact hash/locator. Do not write them directly into canonical connections.

## Classification

Every candidate must be assigned one current Connection Schema kind. Ambiguous candidates stay REVIEW_REQUIRED. Exact text may be preserved, but semantic kind must be current and explicit.

## Provenance

If a legacy linguistic-audit artifact actually reviewed the enrichment, record lineage as legacy audit/recovery evidence and list the specific claim it supports. Do not rewrite that lineage as live Duden/Langenscheidt evidence. Live lexicon evidence may be added only when actually checked.

## Conflict policy

Existing canonical content wins unless evidence proves it wrong. Never silently overwrite current synonyms, antonyms, rection, connections, senses or examples. Conflicts produce a repair record and REVIEW_REQUIRED.

## Release condition

Recovered content is not Final until canonical validation + linguistic audit of changed content + v3.1.10 product completeness all pass.
