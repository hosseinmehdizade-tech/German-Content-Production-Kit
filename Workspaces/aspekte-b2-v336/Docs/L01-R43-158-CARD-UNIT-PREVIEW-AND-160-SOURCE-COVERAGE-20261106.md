# Aspekte B2 — Lektion 1 R43: source-to-card-unit planning, no release

**Date:** 2026-11-06. **Sole lexical inventory:** user's edited and sanitized B2 CSV; no publisher rechecks and no additions to source.

## Real result (not another AI re-review of all sentences)

- **160 immutable source rows** mapped one-to-one or many-to-one/many to one according to typed learner-unit decisions. Each source ordinal 1549–1708 has a mapped R43 unit ID.
- **158 draft NEW card units** with full bilingual front/back and 2 German + 2 Persian example sentences per unit, derived from the single consolidated R42 working CSV and with 4 newly authored DE/FA example pairs for structural splits/usage distinction.
- **One mixed-POS source (#1586)** becomes two learner units: `vielsprachig` adjective and `die Mehrsprachigkeit` noun. Both retain their common original source ID; each has two separate examples.
- **Two identical source rows (#1640 and #1641)** resolve to **one** `die Migrantenfamilie` draft card with both original source IDs. Two example pairs are selected (one per original row); all four original AI-authored pairs are preserved in the unchanged R42 canonical working file. This is only a draft consolidation, **not deletion or merging the source or user's existing cards**.
- **#1660 `gekommen`** is a *grammatical form facet* of `kommen`, not another independent infinitive/word card; preserve source and both examples in a 2-object sidecar. Target linking to an existing `kommen` accepted learner unit remains unverified.
- **#1630 `intolerant`** is a **conditional earlier B1 card reuse** `mb1m-lu-2779`, NOT an executed suppression. User-reported B1 import and final content same sense; independently verified app/SRS identity not established. Source and fallback DE/FA examples remain intact in sidecar and R42.
- **#1575 `ständig`**: B2 new-card preview is **attributive adjective only**, with two adjective-context examples; B1 `mb1m-lu-1040` handles common adverb. Source adverb example remains in R42.
- **#1616 `die Art`**: B2 preview focuses on `Fragen jeglicher Art` collocation; A2 `ma2m-lu-0281` is content-only, with no verified app import. B2 original standalone source entry is preserved.
- **#1588 `die Vielsprachigkeit`** remains a context-specific noun; do not imply a universal antonym/contrast to Mehrsprachigkeit.

## Accounting

`160 source rows + 1 extra learner unit from split #1586 – 1 duplicate draft from alias #1641 – 1 grammar facet #1660 – 1 conditional earlier B1 reuse #1630 = 158 NEW draft cards.`

In addition to the 158 draft new-card units: 1 participle facet and 1 conditional prior-unit reuse are preserved as full supplementary content objects. The canonical source-to-unit mapping always has exactly 160 rows. All four exceptions are described in a separate four-row decision ledger.

**Correctness limitations:** This is an AI-authored learner-unit plan, NOT an approved Stage2 gate and NOT Stage3 cards ready to publish. Every preview row has `export_importable=FALSE` and `linguistic_release_approved=FALSE`. Existing 17 R39 source/release HOLDs remain tracked, even where an editorial unit proposal has been operationalized. Independent bilingual semantic QA and prior actual app-card verification are outstanding. No user SRS, lower-level project, source inventory, previous flashcard or app changed.

## Files
- `Current/L01-158-UNIT-CARD-PREVIEW-NONIMPORT.csv`: 158 complete draft bilingual units, no import.
- `Reports/L01-160-SOURCE-TO-UNIT-COVERAGE.csv`: 160 immutable source rows, all accounted for.
- `Reports/L01-4-STRUCTURAL-EXCEPTION-DECISIONS.csv`: typed split, exact duplicate alias, B1 reuse, participle facet.
- `Reports/L01-2-NONCARD-CONTENT-OBJECTS.csv`: full DE/FA example content for participle form and earlier-B1 reuse.
- `Reports/L01-R43-LEARNER-UNIT-PLAN-SUMMARY.json`: gates, invariants and counts.
- `Checkpoints/Aspekte-B2-L01-CURRENT-UNIT-PLAN-NONIMPORT.zip`: portable bundle with hashes. The global R25/L05 checkpoint remains unchanged.
## B2 Library records (byte-verified)

- 158 card preview: `Current/L01-158-UNIT-CARD-PREVIEW-NONIMPORT.csv` (`libfile_63d0d516ccb0819192141fb520c2bd4e`) SHA256 `720154fe304c990aeec4dc7b69c70bc36fa22784f8e769d7f208d2724b0b50c3`.
- 160 source coverage: `Reports/L01-160-SOURCE-TO-UNIT-COVERAGE.csv` (`libfile_5e1b41d90c7c81918b04e7ee790511f5`) SHA256 `d1bd551c71306247eaedd71de6827c0e4cb4e5b619f8977a184dfa37b71f9bea`.
- Four exception decisions: `Reports/L01-4-STRUCTURAL-EXCEPTION-DECISIONS.csv` (`libfile_2d4feabb3a0c8191a6210957b46ae905`).
- Two noncard objects: `Reports/L01-2-NONCARD-CONTENT-OBJECTS.csv` (`libfile_acf6d43d713c8191b9dedd823d9b9017`).
- Portable checkpoint ZIP: `Checkpoints/Aspekte-B2-L01-CURRENT-UNIT-PLAN-NONIMPORT.zip` (`libfile_5f8aa8d263188191b19fbbc9bb94ed67`) SHA256 `ea98525737b06ce8dcb223c0d1de9ebe364c9a9b61690f2dc56fea8a66623e0c`, 32,316 bytes, Library readback, CRC, manifest verified.
