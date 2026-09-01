# Changelog — v3.1.10 Completeness Hotfix

- Added a separate `PRODUCT_CONTENT_COMPLETE` gate so structural/content validation cannot hide empty rich-card sections.
- Added target completeness profile schema and Menschen A1 rich-card profile.
- Menschen A1 Verb now requires auxiliary/reflexive/separability and at least three verified collocations (target four, preferred max six).
- Present Collocation/Rektion/Synonym/Antonym content now requires explicit claim-level provenance appropriate to that claim.
- Synonym/Antonym remain preferred enrichment, not hard minimums; no-fabrication policy is explicit.
- Added executable completeness validator and regression tests.
- Added a semantic safety rule for legacy `NVV1..NVV6`: values are recovery candidates, not automatically canonical `nvv` or `collocation`.
- Architecture v3.1.5 and semantic contract 3.1.3 are unchanged.
