# Aspekte B2 — Stage2 R14 editorial progress (2026-11-05)

**Only lexical authority:** user's CSV-derived sanitized B2 file (1726 entries, 10 lessons), exact SHA256 `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`. Historical full private raw source SHA256 `09478483886661527b24bf00d9c375234d5877ac9189f01f1aa6ec467b85e0f1` not rehashed. Original source strings/IDs and every R13 ledger field unmodified. Dictionaries verify the user's entries; no extra headwords are introduced.

## Lesson02: two previously open semantic HOLDs now with editorial disposition proposals
- **#1763 `verschuldet`:** LEO lists both `verschuldeter` and `am verschuldetsten` as formal morphological degrees. Do **not** claim these written forms wrong. PONS attests the indebted sense and separately the causative participle `etwas verschuldet`. Proposed display: financially indebted `hoch/stärker verschuldet` vs caused by one's fault `selbst verschuldet`, with register/usage label. `https://de.pons.com/%C3%BCbersetzung/deutsche-rechtschreibung/verschuldet`
- **#1799 `gezeichnet sein`:** original Persian contains patterned/marked and signed senses. Duden `zeichnen` also attests figurative hardship/illness traces and older abbreviation `gez.` for signed. Proposed **sense-labeled unit**, preserve the original Persian and both independent source senses, do not falsely attribute Duden illustrative examples to CSV. `https://www.duden.de/rechtschreibung/zeichnen` and `https://www.duden.de/rechtschreibung/gezeichnet`.

Both original R13 HOLD actions remain in the immutable parent. These are **AI editorial resolution proposals, not approved flashcards or published semantic assurance**. L02 108/108 AI first/second reviews still need release signoff and an explicitly separate `AI_AUTHORED_NOT_USER_CSV` example pipeline.

## Lesson03: 30 newly reviewed / 186 total source records
All 186 original user CSV rows ordinals 1817–2002 inventoried. Individual first-pass proposals for #1817–1846: **10 provisional FIX**, **20 provisional KEEP/usage**, **156 remaining** without a detailed semantic first-pass. Notable:
- #1821 `Handwerk` plural Handwerke (Duden); not absolute singular-only.
- #1822 `hauptberuflich` = main profession, not automatically full-time.
- #1824 `kreieren` = kreierte, **hat** kreiert.
- #1827 `Nervenkitzel` a noun for thrill/excitement, not an adjective.
- #1829 `Rezeptur` a formulation/composition (especially cosmetics, medicines and foods), not simply cooking instructions.
- #1839 `Geschick` skill in `handwerkliches Geschick`, without productive skill-plural; `Geschicke` belongs to separate fate homonym.
- #1843 `Privatwohnung` private home ≠ necessarily property owned by resident.
- #1844 `reichen` separate `jemandem [Dativ] etwas [Akk.]` and `für + Akk.`; original typo `r eicht` retained in source, pedagogical normalization proposed only.
- #1846 `stimmen` separate correct/vote/tune/cause mood constructions, including `jdn. [Akk.] traurig stimmen`.

## Reproducibility, approval and archive
Self-contained archive with *exact* R13 checkpoint and source CSV: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Checkpoints/Aspekte-B2-STAGE2-R14-L02-TWO-HOLDS-EDITORIAL-L03-FIRST30-20261105.zip`, SHA256 `44b8cc48f2c8247af56806429bea421cdf4410661ab339228d6680fc868d9cca`, 1169847 bytes, 15 members, 14 SHA256 payload hashes, stable Library `libfile_5f0d74db29288191bac7ebc4c901b0e1`, exact Library byte readback PASS. Fresh-extraction builder reproduced JSONL bytes and QA counted 1,758 invariants incl. 8 adversarial mutations. These technical assertions are **not** human German/Persian signoff. L01 five earlier-card identity holds remain. **Stage2 NOT APPROVED, Stage3–7 NOT_STARTED, 0 finished/importable cards, no app/SRS writes.**