# Aspekte C1 — CORRECTION: curated per-project TSV is the comparator (2026-11-06)

**Status: SOURCE AUTHORITY CORRECTED; STAGE1 IN_PROGRESS; NO KEEP/DROP/MERGE RELEASE, NO CARDS.**

The prior 9,109-row historical raw Menschen Memrise CSV is a **source-provenance archive only**, **NOT** the accepted reference for C1 duplicate/sense decisions. The earlier 1,490 raw/sanitized witness checks and 68 strict headword matches remain reproducible as historical audits, but do **NOT** establish duplicate decisions against the corrected course content. Their use as the current semantic comparator is revoked.

Current corrected content TSVs, independently opened and SHA-256 checked:
- **Menschen A1:** `Content/Menschen-A1-ALL-24-LESSONS-2997-CARDS.tsv`, 2,997 cards, SHA `dc2f7e17aff41481f9c0c28e3afacff750182fc5b6df72093810c25c6857f91e`. Within corrected **V48-R1** content-only ZIP SHA `3005b24a8928bee6eab28a3d8c1a8fe13d2c5ff6eb7975d7ed470d822a22ccac`. The A1 Library files were intentionally removed after verified Drive backup; current user-owned Drive artifact: https://drive.google.com/file/d/1aXi2Xm3I1hvkMdJtsYGMQGhE6hZ8YCUT/view
- **Menschen A2:** `01-Content/A2-C3-1778-cards.tsv`, 1,778 cards, SHA `b9f4ce62e5c91cb3d5f225b203e180c4007880a076b67c9f51d0800881055d76`. In `/Flasch kart/German-Content-Production-Kit/Content/Menschen-A2/Releases/Menschen-A2-24-Lektionen-1778-KARTEN-ALLE-KORREKTUREN-GEPRUEFT-CONTENT-ONLY-20261106.zip`.
- **Menschen B1:** `01-Import/Menschen-B1-24-ALLE-KORREKTUREN-MERGED-UNIVERSAL-v2.tsv`, **3,088** cards, SHA `bcf0410a88037848bca273672dda2435aa4713efa02c1ffbe367eada5c1848d6`, in `/Flasch kart/German-Content-Production-Kit/Content/Menschen-B1/Current/Menschen-B1-24-Alle-Korrekturen-Integriert-20261106.zip`. The older standalone 3,089-card TSV in Releases does not include the same latest correction and is not this version's authority.

**Aspekte B1+/B2:** no approved learner-facing final TSV in their project Release folders as presently checked; their sanitized source CSVs and Stage2/4 editorial candidates are not substitutes for a finalized corrected release.

Correction-only screening: the **7,863** verified curated card rows yield **79** literal normalized front-field headword matches among **2,219** preflight NEW C1 candidates. **79 is not a count of duplicate senses.** No semantic/idiom final decisions are made. A distinct read-only QA independently resolved all 79 evidence references to real corrected TSV card IDs and DE/FA front/back fields.

Full 79-item evidence queue, differences from old 68-item queue, source registry, independent QA and manifest are contained in the Library checkpoint:
`Aspekte-C1-STAGE1-CURATED-TSV-COMPARATOR-CORRECTION-20261106.zip`
SHA-256: `f853697636340d76f4a789804b68e85a2e784428ec5abbf4e79b02d153bfd4b1`
Library file: `libfile_2d85ea8f62108191828caac8786c9e91` (219 ZIP members; parent 213 members unchanged).

**Verbindliche Regel:** Für den Dublettenvergleich gelten die jüngsten freigegebenen und korrigierten Projekt-TSV-Daten — nicht die historischen Memrise-Rohdaten. Formgleichheit allein ist kein Beleg für Bedeutungsgleichheit.
