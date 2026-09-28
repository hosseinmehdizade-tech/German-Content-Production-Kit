# CHANGELOG v3.3.3

- Fixed the generic v411 vocabulary projector so ordinary lexical cards emit `de-vocabulary` instead of `german-verb`.
- Added unified vocabulary import/presentation policy and projection contract v1.1.0.
- Added a Stage 5 validator for JSON/Universal TSV that rejects POS/layout-selecting card types.
- Added noun/verb/adjective/expression/NVV regression coverage.
- Added clean-delivery guard against non-neutral `card_type`.
- Projection parity proof: across golden noun/verb/adjective/idiom/NVV plus NVV integration sample, the only projected-card value changed is outer `cardType`; semantic/content fields are preserved.
- Historical LOCKED content is not rewritten. Legacy `german-verb` remains runtime-import compatible.
