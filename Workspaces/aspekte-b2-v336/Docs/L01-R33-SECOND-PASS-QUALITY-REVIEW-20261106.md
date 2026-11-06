# Aspekte B2 — Kapitel 1, R33: AI bilingual second-pass and QA gates

**Date:** 2026-11-06. **Only B2 workspace/library.** Source inventory unchanged; original raw CSV not reverified this run.

## Scope and evidence
- Sanitized user-only B2 CSV: 1,726 rows; SHA256 `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`.
- R32 working file: SHA256 `50297fddcc6c3f46592956df415e2c4c9c22613e18c69d76b72b06a632e0ea1c`.
- Compared all 160 chapter-1 IDs, German original headwords, Persian original meanings and source example strings against the sanitized user CSV, ordinals 1549–1708: exact.
- All 160 rows have two non-empty German AI example drafts plus two Persian translations. 320 DE + 320 FA. No duplicate example cells. 13 original source example strings retained.
- A separate **AI-led editorial second pass** read both examples and translations for 160 rows. This is **not independent human/model QA or formal semantic sign-off**.

## Row-level results
- 131: no new example problem flagged in this AI pass (NOT APPROVED).
- 8: example/translation corrections proposed, ordinals **1552, 1566, 1576, 1577, 1633, 1657, 1678, 1680**.
- 17: existing unresolved source/cross-level release gates, ordinals **1556, 1575, 1586, 1588, 1609, 1610, 1611, 1616, 1630, 1640, 1641, 1647, 1660, 1671, 1675, 1693, 1697**.
- 4: additional source/editorial cautions, ordinals **1551, 1602, 1607, 1706**.
- **No merges/suppressions executed. No stage-3 cards generated. Stage 2 still NOT APPROVED.**

## Targeted example proposals
- **1552 auflösen:** contextualize `eine Wohnung auflösen` using household clearing following a death.
- **1566 Horizont:** say `Gespräche mit Menschen aus anderen Kulturen`, not `Gespräch mit anderen Kulturen`.
- **1576 zerschneiden:** clarify `Prüfung` as document review, use Persian for *cut*, not *tear*.
- **1577 Landessprache:** use Switzerland as unambiguous national-language context.
- **1633 Unverständnis:** idiomatic Persian for `auf Unverständnis stoßen`, not `Missverständnis`.
- **1657 Hausverwaltung:** prefer `eine Firma mit der Reparatur beauftragen`.
- **1678 begehrt:** improve Persian phrasing for popular/sought-after apartments.
- **1680 Diplom:** distinguish German university `Diplom` from ordinary school diploma.

## Exact Library records
- Detailed 160-row QA with DE/FA replacement proposals (source is not overwritten):
  `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Reports/L01-R33-160-ROW-AI-SEMANTIC-SECOND-PASS-QA.csv`; Library ID `libfile_3453f24c3b848191b009545fd0372367`; SHA256 `575f2684e797e15e7c720f3e47806ea27cd46079ec00588603e0f864f0d815ae`.
- Detailed Markdown report:
  `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Reports/L01-R33-AI-SEMANTIC-SECOND-PASS-AND-RELEASE-GATES-20261106.md`; Library ID `libfile_93d09e0468008191a4e915f3cec95634`; SHA256 `846692cfe19b1f4fe5aee802a329bd39329812be61ee5beab577f2e315b3a358`.
- Portable R33 chapter-local **QA-only** archive (includes JSON summary, CSV, Markdown and manifest):
  `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Checkpoints/Aspekte-B2-STAGE2-L01-R33-AI-QA-160-8-REVISIONS-17-HOLDS-20261106.zip`; Library ID `libfile_faa607197f9c819188797c129a630a91`; SHA256 `82d9e644cd701f1767aa11fd4c8a3835e4ca40b0919800b03726a8f9a8a51cc4`; 10,213 bytes.
- The separate summary JSON upload failed with a transient container-session error; summary remains in this archive. Do not claim standalone upload.

## Remaining work / QA gate
Independent bilingual semantic and idiomatic QA of all 160 rows, review proposed corrections, and accepted lower-level card witnesses for #1556, #1575, #1609, #1630, #1671. Resolve all other source-unit HOLDs before final Stage 2. **R32 working CSV and main comprehensive R25 portable checkpoint remain unchanged.**
