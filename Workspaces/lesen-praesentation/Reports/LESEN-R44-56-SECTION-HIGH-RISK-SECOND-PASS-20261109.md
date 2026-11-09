# Lesen R44 — 56 exact non-p05 DE/FA/EN passages compared (2026-11-09)

**Status:** New editable R44 candidate from byte-verified exact R43 owner parent; contextual model second-pass **56 real sections** (53 previously pending, 3 R43 previously repaired revisited). Exactly **8 sections / 16 Persian+English fields** repaired against current German source. **Not full Stage4 or FINAL.**

## Detailed source-anchored repairs

- **030/p02 FA+EN:** German refers specifically to job applications and additional attention resulting from a well-known university name.
- **032/p02 FA+EN:** Technical assistance improves safety and autonomy **crucial for many people's daily lives**, not just generic independence.
- **034/p03 FA+EN:** Online data may be **stored permanently**, not simply accessible for a long time.
- **036/p06 FA+EN:** Schools teach **knowledge about nutrition** but cannot control all factors affecting **children's eating habits**.
- **038/p02 FA+EN:** Broader university access benefits society through **greater diversity and new perspectives**.
- **042/p03 FA+EN:** Overseas career opportunities may involve **personal strain**, not only unspecified opportunities or costs.
- **044/p03 FA+EN:** Long-term sustainable pension systems need multiple **financing sources and safeguards**.
- **060/p03 FA+EN:** **Private online teacher/student contacts** create perceived favoritism, not merely emotional online closeness.

A complete **56-section ledger** with exact German/Persian/English text and SHA-256, preserved German sentence IDs, all old/new full translation fields and narrow source-specific rationale is inside the portable ZIP at `03-Reports/LESEN-R44-56-SECTION-CONTEXTUAL-SECOND-PASS-LEDGER.json`. Three prior R43 corrections were reread (023/p06,039/p03,058/p03) without changes, 45 other reviewed passages had no newly confirmed defect. Other source content remains byte-exact. **Cumulative non-p05 contextual second-pass: 61/410; pending 349.** 478/478 initial pass and 68/68 p05 second pass remain previous model work; they are not external expert signoff.

## Technical reproducibility and limits

- Parent master SHA `37e852e58fde13cefbaa5f6c5e7550555ba20e4315799afc05dd4767d0aa8022`, runtime SHA `2ecf997f60fb2f366e2101733511e44a25ec48f8212c186064e892b6aec8efdc`. New master SHA `1926b0f521d63155a8b218f2b47c31608ef505176ae3c43bd0c12c9e31998fbf`, runtime SHA `3327f545d71f143809d4962d3132d33aea283b1e725715f233970d18da4eebde`.
- Standalone independent source-to-runtime delta checker **19386/19386 PASS**, **14/14** corrupted-source variants blocked. All **3537** current fulltext grammar anchors (section-relative) valid, curated 669 untouched, R32/R33 known-error gates PASS. **No original complete nine-lens grammar rerun.**
- Actual exact-current v505 JS `reading-content-import-v38.js` SHA `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc` in isolated Node VM: validator **zero errors/warnings**, **10/10** malformed packs rejected, 68 reading units/340 exercises in memory. **Not a real browser IndexedDB Stage6 test**.
- ZIP `Lesen-R44-56-SECTION-HIGH-RISK-SECOND-PASS-CANDIDATE-20261109.zip` SHA `87aecd84809490d3d827e7788c13fe465e95bd9de0bba283b7ce70792bc0c8e5` (3476402 bytes; 18 members, **17/17 SHA256SUMS**, ZIP CRC PASS), stored owner Library stable ID `libfile_498d79d4d1b48191b7b6e8c80cbf2508`. Fresh Library materialization exact SHA/raw byte CMP PASS; completely separate extraction and `python -B 04-Tools/verify_portable_r44.py` rebuilt identical source/runtime and reran independent QA and actual v505 JS source PASS.
- **Full semantic Stage4 HOLD**: AI comparison is not independent full-language certification; **349** remaining non-p05 texts still need equivalent in-depth second pass. **Real Chrome/IndexedDB Stage6 NOT_RUN, Stage7 NOT_RELEASED**. Curated CURRENT and all app UI, SRS/FSRS, user progress and unrelated content unchanged.

**Next:** R45 meaningful contextual review for remaining 349 passages in large batches, continuing from the exact Library R44 candidate—not historical source, not an obsolete app version.