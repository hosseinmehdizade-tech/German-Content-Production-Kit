# Aspekte B2 — Kapitel 1 R34: applied eight editorial fixes; seventeen holds retained (2026-11-06)

**Source policy:** user CSV only as lexical inventory. The sanitized B2 source SHA256 is `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`. Original unredacted user CSV was NOT reverified in this run. Original source and R32 working file unchanged.

## Actual work
- R32 exact 160 source rows, ordinals 1549–1708; 320 German and 320 Persian example drafts.
- The R33 AI second-pass proposals were evaluated and **eight** edits were applied only in a newly versioned, **non-importable** 160-row working CSV (ordinals 1552, 1566, 1576, 1577, 1633, 1657, 1678, 1680).
- At ordinal **1566** the German example now uses `Durch Gespräche mit Menschen aus anderen Kulturen erweitere ich meinen Horizont.` to remove the ambiguous `ihren`.
- At **1633**, the proposed Persian editorial display gloss for `Unverständnis` was corrected to avoid equating it with `Missverständnis`.
- **17** unresolved source-unit/cross-level holds were individually dispositioned without execution: 1556, 1575, 1586, 1588, 1609, 1610, 1611, 1616, 1630, 1640, 1641, 1647, 1660, 1671, 1675, 1693, 1697.
- Source #1640 and #1641 exact duplicate headword+meaning verified. Proposed canonical #1640 and alias #1641 ONLY. **No merges, deletions, suppressions, or source mutations.**
- Earlier B1 `ständig` and `intolerant` cards found only as NONIMPORT candidates `mb1m-lu-1040`, `mb1m-lu-2779`; there is no verified imported/live accepted-card identity. Earlier `im Voraus entscheidend` is a phrase, not standalone `entscheidend`.
- R34 review also calls out `geteilt (in+D)` source-frame discrepancy against `teilen in + Akk`, `Juryvorsitz` office/person distinction, and `gekommen` being a participle.
- Deterministic 160-row source-integrity and ZIP manifest replay passed. This is **targeted AI editorial QA, NOT independent full 160-row linguistic certification**.
- **Stage2 NOT APPROVED. Stage3–7 NOT STARTED. Final cards/importable = 0.**

## Verified outputs in the dedicated B2 Library
- Current working CSV: `Current/L01-R34-160-EDITORIAL-WORKING-NONIMPORT.csv` · Library ID `libfile_c5f37d79dd208191adb53fddecbd12d5` · SHA256 `cbe2e36baedad8682cf91de083fb5e202111777050ce38445b430a06d74acf1a`.
- Targeted 25-row evidence matrix: `Reports/L01-R34-25-TARGETED-DECISIONS-AND-HOLDS.csv` · Library ID `libfile_36df314c94748191b8b7eb6a1ca3df7d` · SHA256 `8e4939ab2ce545baa775dd0e093dfdffe16bb9eacbe95aff552743e928dfb401`.
- Summary: `Reports/L01-R34-SUMMARY.json` · Library ID `libfile_5ec24fe45390819195c8706dc23b847b`.
- Detailed report: `Reports/L01-R34-EDITORIAL-8-FIXES-17-HOLDS-REPORT.md` · Library ID `libfile_bc71bfa392c88191bc18136e561ef3da`.
- Portable scope-specific checkpoint ZIP: `Checkpoints/Aspekte-B2-STAGE2-L01-R34-8-CORRECTIONS-17-HOLDS-NONIMPORT-20261106.zip` · Library ID `libfile_f5cd555b16f481919a7318d841c9ec35` · SHA256 `50623b81943f77fec3047ff21c60c67e4f9777326c6f07c95a9315d057dee4b4`.
- Main global portable R25 L05 checkpoint remains unchanged. R34 is editorial working state, not new global release.

## Next concrete gate
Independent bilingual review of all 160 draft rows **as changed in R34**, supported evidence for 17 remaining HOLDs and semantic QA for original 48 FIX proposals. No imports/Stage3 before gate approval.

Selected lexicographic evidence used for semantics (never for source membership): Duden `Unverständnis`, `Missverständnis`, `teilen`, `Diplom`, `Vorsitz`, `einig`.
