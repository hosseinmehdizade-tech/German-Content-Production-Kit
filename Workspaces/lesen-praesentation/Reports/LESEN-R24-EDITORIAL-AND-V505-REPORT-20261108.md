# Lesen R24 — letzter Abschluss der ursprünglichen p06-s02-Standardaussagen (08.11.2026)

**Status: scoped trilingual editorial + structural QA PASS; exact-current-v505 JS preentry PASS; Library post-upload byte verification + portable reproduction PASS. NOT full Stage4/Stage6/Stage7, NOT curated CURRENT.**

## Authority and scope

- Parent: user-curated **R23**, not the original source PDF. Source SHA256 `028805009f323685f6282afe277cbdffac5c3f319fb7ff1f4fa67bdb93a759b6`; runtime SHA256 `21a8596d267c04a9591beb4928e0fe21fdc6148b148591b4305fe52cc02361af`; parent recovery ZIP SHA256 `9f80baec5e1f7167db10dbe402652ad3826f77d7e65a7a560e5bcbaba196d28e`.
- Scope **LES-PRES-061–068**: 8 generic p06-s02 German sentences replaced with topic-specific DE statements grounded in existing p02/p03/p05 and p06-s01. Exactly 8 related Persian and 8 English conclusion translations updated, prior p06-s01 and 60 complete other source/runtime lesson objects retained.
- 68 units, 478 passages, 340 question/answer identities, 350 vocabulary, 669 curated grammar IDs preserved. **Formerly identical generic p06-s02 sentences: 8 → 0**, across entire R24 pack. Do not equate this scoped clearance with full original-text quality.
- Grammar: 32 old generic-specific fulltext markers retired and 8 real, manually attested, offset-exact targets added; total 3,891 → **3,867**. Full original nine-lens grammar producer **NOT_RERUN**; metadata explicitly attributes manual scope.
- Detailed before/after trilingual edits, grammar offsets, provenance: `03-Reports/LESEN-R24-8P06-EDITORIAL-GRAMMAR-LEDGER.json` within R24 ZIP.

## Independent QA and actual v505 source preentry

- 18,332 / 18,332 independent deterministic structural/identity/runtime mirroring checks **PASS**, 0 failures; 9/9 source corruption probes rejected.
- Exact current `reading-content-import-v38.js` module SHA `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`: native JS validation PASS with **0 errors and warnings**, 10/10 malformed packs rejected, isolated in-memory projection 68 units / 340 exercises PASS. **Not an installed Chrome/IndexedDB Stage6 transaction**.
- Independent wholepack semantic DE/FA/EN Stage4: **HOLD**; original nine-lens exhaustive re-run: **NOT_RERUN**; browser Stage6: **NOT_RUN**; Stage7: **NOT_RELEASED**.

## Separately discovered wholepack p01/p07 quality backlog

Read-only `03-Reports/LESEN-R24-P01-P07-WHOLEPACK-TEXT-RISK-AUDIT.json` shows 68 unique whole p01 introductions but repeated formulaic sentences (p01 second sentence patterns appear 15, 15, 14, 14 times; one p01 third sentence repeats 15 times). **p07 contains 16 unique whole-text endings for 68 topics; 58 lessons belong to 6 exact repeated p07 groups**. Repetition flags require full contextual/translation/grammar review, not automatic synonyms or a fake Stage4 PASS.

## Portable and independent Library acceptance

- Candidate Master SHA256 `84ad3fe63569dfecb269de270210796922bbe668628f9e5d23fba1435c9ae562`
- Candidate v505 runtime SHA256 `9ff20a564566d66b19fd63b7c8966adbb6d9e947f3cce6ae90a89547e9807122`
- ZIP `Lesen-R24-8P06-CONTENT-RECOVERY-CHECKPOINT-20261108.zip` SHA256 `c2ed57f6018aa584639429a994a0b3a00229988aea608fa73e26d57a1db5542d`, 3,382,815 bytes; 16 members, CRC PASS, internal 15/15 SHA256 PASS; reproducible output and independent tests from extracted ZIP PASS.
- Library `/Flasch kart/German-Content-Production-Kit/Content/Lesen/Checkpoints/Lesen-R24-8P06-CONTENT-RECOVERY-CHECKPOINT-20261108.zip`, stable ID `libfile_958c3ae928a881919df751f39bf3036f`. Independent post-upload rematerialization **SHA256 identical and byte-CMP PASS**, archive CRC and extracted `python 04-Tools/verify_portable_r24.py` clean-replay PASS.
- Curated v1.3.0 original CURRENT `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` immutable. No app/UI/SRS/FSRS/progress, other streams or source PDF touched, no auto Library deletion.

**Next:** Comprehensive topic-specific p01/p07 DE/FA/EN meaning review and original grammar dependency scan, independent full trilingual Stage4, nine-lens grammar review, real isolated browser/IndexedDB Stage6 and packaged Stage7. Do not restart from old publisher PDF.