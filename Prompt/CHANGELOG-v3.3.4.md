# CHANGELOG v3.3.4

- Hardened `Tools/build_clean_delivery.py` into an independent unified-vocabulary release gate.
- Direct-import TSV must contain `card_type` and `category`.
- Missing, legacy `german-verb`, mixed, or otherwise non-neutral rows fail before ZIP creation.
- The builder invokes the unified projection validator internally, closing the standalone-validator bypass.
- Delivery-role matching is case-insensitive for real Universal filenames.
- Historical LOCKED content and Flashcards runtime/UI bytes are unchanged.
