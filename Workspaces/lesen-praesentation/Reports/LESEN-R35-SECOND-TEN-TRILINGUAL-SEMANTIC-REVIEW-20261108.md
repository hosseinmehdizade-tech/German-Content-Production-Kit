# Lesen R35 — contextual DE/FA/EN first-pass lessons 011–020 (2026-11-08)

**Exact editable parent R34; new scoped R35 candidate.** First-pass AI editorial check of **70 real sections**, with **four sections / five FA+EN fields** corrected against actual curated German text. This is **not** independent wholepack semantic Stage4 or external-human certification; 336 sections have not yet received this first pass, and the earlier 142 first-pass sections are not guaranteed flawless.

## Edited content, with exact before/after in the ZIP ledger

- **LES-PRES-012 p03 Persian**: `unsportliche oder gesundheitlich eingeschränkte Kinder` means less athletic or limited by health; Persian `کم‌تحرک` wrongly claimed inactivity, and `محدودیت جسمی` reduced health to bodily impairment. Correction restores exact semantic scope.
- **LES-PRES-016 p01 Persian**: German generic present `verändern` had been shifted to Persian perfect `تغییر داده‌اند`; correction restores ongoing/general present.
- **LES-PRES-016 p02 FA + EN**: German `Gemeinschaften finden` does not in this passage specify `that suit their interests`; remove unwarranted qualifier while preserving surrounding text.
- **LES-PRES-020 p05 English**: German strict `nicht davon ... sondern davon` was softened to `depends less ... than`; change to `depends not on whether ... but on how` to preserve the claimed distinction.
- **Watchlist, no automatic mutation:** 017/p06 and 018/p06 conjunction/discourse `obwohl` versus translated additive sentences. German wording and grammar dependencies require joint contextual adjudication; it would be unsafe to silently force a Persian/English conjunction.

Parent R34 master SHA256 `9041a1414766dba7fd0dd6c37098b5b17eb2b9fc4873572230c15d6f7f1a1e5f`, runtime SHA256 `54b16cbd19cb0ef283230c8d479c4dfe7fcba1a4b7370a258c445b139808709f`, owner Library `libfile_63319e22e038819197d1b5d64bb01fd6`. R35 new master `0df741a6253293c513600b46eec85847cae7ce8234c23f43aae7f96954558184`, compiled runtime `ac0015640e68732ff447bf86b2c866a3735133fda4ea2545f2c28eb75735604d`. All German paragraphs, sentences and IDs, 68 lesson identities, 478 passages, 340 questions, 350 vocabulary rows, 669 curated grammar entries and 3539 fulltext occurrences preserved; all unaffected translations are exact.

## Actual QA, evidence, limits

- Independently written parent-to-child scoped delta verifier **6,732 checks PASS**, **10/10** damaged candidate source mutations rejected. R32 curated currentness gate and R33 syntactic counterexample gate PASS zero known errors.
- Actual current v505 `reading-content-import-v38.js` SHA256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc` in isolated Node VM: **PASS zero errors/warnings**, **10/10** deliberately malformed runtime packs rejected, isolated in-memory **68 reading units / 340 exercises**. This does **not** perform installed-browser/IndexedDB Stage6.
- R34 previous cohort 001–010: 72 sections; R35 011–020: 70 sections, cumulative first-pass **142/478**; **336** outside first-pass. No inference of full independent Stage4, complete original nine-lens grammar re-extraction or Stage7.

## Portable ZIP / Library proof

- Recovery ZIP `Lesen-R35-SECOND-TEN-TRILINGUAL-SEMANTIC-BATCH-CANDIDATE-20261108.zip`, SHA256 `12d4f316c300d41e0cb5086db1937b36f0178ce3053f18c7ef75df66b21bc9ae`, 3438244 bytes, 17 entries, 16/16 SHA256SUMS PASS, ZIP CRC PASS.
- Owner Library `/Flasch kart/German-Content-Production-Kit/Content/Lesen/Checkpoints/Lesen-R35-SECOND-TEN-TRILINGUAL-SEMANTIC-BATCH-CANDIDATE-20261108.zip` ID `libfile_35f29cd34cc0819188fbef82fb08e7cb`. The independently rematerialized Library ZIP has **exact same SHA and raw byte comparison PASS**; clean extracted `python 04-Tools/verify_portable_r35.py` reconstructed exact master/runtime/ledger/QA/native JS outputs PASS.
- Original v1.3.0 curated CURRENT SHA `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` unmodified. No app UI/FSRS/SRS/progress, other workstreams or original publisher PDF changes; no Library deletion.

**Next R36:** from exact byte-verified R35, review lessons 021–030 and contextual DE/FA/EN logic; keep grammatical/document dependencies and wholepack Stage4 HOLD, then real browser Stage6 only after full acceptance.
