# Aspekte C1 Kapitel 1 — finite Stage5 source→Universal v2 transport probe

**Date:** 2026-11-23  
**Result:** `PASS_SOURCE_TO_TSV_FIELD_ROUNDTRIP__NATIVE_GFP_IMPORT_UNVERIFIED`; **0** cards imported or Stage5-approved. This is NOT a production/import acceptance report and does NOT reopen completed Stage4.

## Exact actual sources

- Immutable 251-card Stage4 editorial source ZIP in Library: `Aspekte-C1-STAGE4-K01-251-APPROVED-251-CARDS-20261123.zip`, SHA-256 `8bcd5fe6451489479be361628cc2f303ff8066393307b7138fd00c1ca47264f7`, library `libfile_d24b2c0c387481918a189a5878f0e21e`.
- Canonical source JSON **actual** member `C1-STAGE4-K01-251-RICH-CARDS-251-APPROVED-20261123.json`, SHA-256 `e7dd416d517f75fb8df3417df1725bfb6985d1f2bc31cc528b151d95ed173e06`.
- **Current** GFP application from its own current Library pointer: `GFP-v507-R143-FINAL-COMPLETE.zip`, SHA-256 `2df83709c3b1d8359f796ee12cab4afe5fc28b3eee663516caa57428160ba871`; actual ZIP `GFP-v507-R143-FINAL/01-App/index.html`, SHA-256 `7ca38469ae41861c8d08cb843c67a6e15e06029f7026d8fa6fe86d684a245261`. The app repository `main` is historical v486, **not** the pinned target. GFP repo `RUNTIME-AUTHORITY-PIN.json` records v507 as CURRENT and its candidate-branch source mirror.
- Actual v507 `index.html` parser inspected, not assumed: exact `UNIVERSAL_TSV_COLUMNS` **23**-column order (line approx. 12393), `universalRawFromRow` (line 12586), `tsvRowsToCards` Universal prefix detection (line 12771), and `canonicalExampleGroupsV348` for trilingual presentation (line approx. 4169). **Static source compatibility inspection only; did not run native function or import into GFP.**

## Deliverable / exact hashes

- Library ZIP: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-C1/Checkpoints/Aspekte-C1-STAGE5-K01-251-CARDS-TRANSPORT-PROBE-20261123.zip`
- Library ID `libfile_d3f003aa07d0819193af898e3eab0e5a`
- ZIP SHA-256 `ce56b404e39358aeba73b625804b86b2e99973273ee97fb2ba148431e3d8e37b`, **5,106,336 bytes**, **133 members**: 127 complete Stage4 source ZIP member payloads preserved byte-identically plus 6 `STAGE5-PROBE/` members, ZIP CRC PASS, no duplicate names.
- Source-preserving, 251-row **candidate-only** Universal v2 TSV: `STAGE5-PROBE/Aspekte-C1-Kapitel1-251-CARDS-UNIVERSAL-v2-STAGE5-PROBE.tsv` SHA-256 `008cc3be9863e65cf7184287ea41b0c86483b5b88e6fe89d38c2785725e05d23`; 4,152,668 bytes.
- Reproducible pinned Python probe builder `STAGE5-PROBE/build_c1_stage5_transport_probe.py`, SHA-256 `985c921f689bf652f9c2829a82b1b0345da7101bb7ef968021be881eefb28f0f`. Requires exactly the source ZIP SHA and exact v507 index SHA; does not change either source.
- `STAGE5-PROBE/C1-STAGE5-SOURCE-OUTPUT-MAP.tsv`: all 251 original IDs, printed PDF page and section, original full card hash, order.
- `STAGE5-PROBE/C1-STAGE5-MAPPING-AND-ROUNDTRIP-RECEIPT.json`: exact 251 TSV row readback, source-card deep equality, DE/FA/EN example identity, 5-section distinctions, 20 historical status differences.
- `STAGE5-PROBE/BUILD-METADATA-PROBE.json`: transport-only build info; **not** a final user-facing acceptance sidecar.
- `STAGE5-PROBE/README-STAGE5-TRANSPORT-PROBE.md`: exact limitations/next gate.

## What passed vs what did NOT

- PASS exact source ZIP, app HTML version and Universal 23-column signature; 251 stable IDs, **313** typed DE/FA/EN meaning records, 1,004 DE/FA/EN example triplets, **583** right-section entries, both row-level and 251 full source-object deep roundtrips, unchanged source members and QA receipts.
- Every TSV row embeds an unmodified `custom_fields.c1_source_card` deep copy. A presentation-only `canonical_unit` and `presentation_examples` add ID-bound German sentences with Persian and English translation arrays. `details` has display strings, while source's typed five groups, EN, source URLs, individual teaching delta remain unchanged under `custom_fields`. This avoids v507 `normalizeDetails` flattening arbitrary relation objects into separate unrelated text items.
- Exactly **20** previously Stage4-approved source cards retain stale `production_status=STAGE2_DRAFT__STAGE4_NOT_STARTED__NOT_APPROVED`. Source status unchanged; a **separate** projection-only Stage4 indication records accepted editorial pass. **No source editing, Stage4 redo, or invented Stage5 approval.**
- **Unresolved type/POS bridge:** C1 source cards lack authoritative fully structured canonical entry type and `core` morphology per item. The TSV deliberately keeps `card_type=de-vocabulary` and `canonical_entry_type=generic` / `entry_type=custom`, rather than inferring noun/verb forms, Rektion or separability from the front. Hence grammatical drill compatibility is **not verified** and could be incomplete.
- **Unexecuted gate:** actual v507 `GFP_CONTENT_V360.parseTsvText`, native import/isolated storage, rich-example display and reload persistence were **not** run. Source-to-TSV byte parity is **not** app-compatible or import-verified proof. Stage5 import-approved cards=0.
- The original Stage4 C1 source-owned structural validator ran on the canonical at Stage4 completion; this transport step did its own 251-row field/semantic-data preservation checks. Do not mislabel the transport receipt as official Stage5 parser PASS.

## Next action: one bounded native compatibility gate (no new editorial loops)

Use exact pinned v507 **in an isolated non-personal test environment** to execute its actual Universal parser on **this exact TSV SHA**, compare 251 card IDs, 4 DE/FA/EN example triplets per card, meanings and five display categories and full canonical source fields after parse. If successful, decide whether a source-attested grammar/POS mapping is needed for noun/article and verb tests, then run a bounded native isolated import/roundtrip gate. Do **not** import into the user's live profile, overwrite existing cards or change SRS/FSRS. If import is unavailable, report `STAGE5_BLOCKED_NATIVE_IMPORT_NOT_VERIFIED` without inventing success or restarting Stage4/Stage6 loops. The 251 Stage4 editorial passes remain complete and frozen.
