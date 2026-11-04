# Menschen A1 — source and lineage reconciliation (2026-11-04)

Read-only forensic audit of the existing **V48-R1** content checkpoint. Original card data, App, UI, IndexedDB and SRS were NOT changed.

## Verified original source

- Original RAR: **113,754,051 bytes**, SHA256 `a2ffb791c29ddaa43e27bb944f430bff6896dc3156115f8989eee3056d5471c1`, exact match to registered `SOURCE-MANIFEST.json`.
- RAR5: **7,725 entries** including 7,719 MP3 files.
- Export CSV SHA256 `52f8bb896f5aa1c8f878aeb0ea74ef07ddbeee75261af89dfb2fcad624fc1222`; 9,109 data rows after four Memrise metadata lines. `info.md` SHA256 also matches.
- The earlier mismatch observation is superseded **for the current exact registered archive**; no source was silently replaced.

## Exact 24-stage replay

Each exact checkpoint **V25–V48** was independently replayed against the previous complete 2,997-card TSV. **1,606 changed cards across 24 stages, zero edits outside the stage's own lesson, zero mutations in protected identity/source fields.** Final replay matches V48-R1.

- `details`: 160 baseline nonappend changes; 154 explained by English expansions and six by documented section redistribution. 265 old values retain their German and Persian prefix with appended English explanations.
- `custom_fields`: 29 changed existing keys; 27 additive combination lists preserve prior entries, and two relation fields in L08 correct `nächst` phrase links from `WORD_FAMILY` to `RELATED` without changing link IDs or targets.
- Persian example: one intended correction in L01/V25 `ma1m-lu-0116-ex-03` for German `Cousine`, explicitly accepted in the historical Stage4 review. Original German and all 11,988 English example translations remain exact.
- Display qualification: exact old collocation `eine Antwort ankreuzen` remains in `canonical_relations` for `ma1m-lu-0075` but is not repeated verbatim in learner-visible `Kombinationen` details.

## Evidence and remaining gate

Complete 160+29+1 case-level ledger, all 24 stage hashes, archive verification and replay scripts are in Library forensic ZIP SHA256 `7d577feb7df4de633d010e311371e0942185979fc131cf88a17792ee17f67f84`, Library ID `libfile_b20402800b6c81918b0a0bad0c3e4255`.

**Stage4/5 24/24 content passes remain unchanged; this is NOT real-browser Stage6 acceptance.** v505 Import regression [issue #25](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/issues/25), IndexedDB/SRS safety and Stage7 final remain open. **NO IMPORT.**
