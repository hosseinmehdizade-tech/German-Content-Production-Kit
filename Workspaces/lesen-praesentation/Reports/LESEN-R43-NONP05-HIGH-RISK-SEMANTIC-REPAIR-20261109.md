# Lesen R43 — non-p05 current-version semantic drift corrections and risk ledger (2026-11-09)

**Authority and limits:** Built from exact R42 owner ZIP SHA `c5a5809ad986cb5bc7156eba622f22d08ed4e9bf84ddfb131538c722a63dc7f8`; parent master SHA `1567d8b9a7cacfec0933709da2f0c64cdc494ea2ef2087947dd17c44762cb518`, native runtime `3e5a6f60491db2a91e3c70adb643f8b302b2216c439e9834224824cc1a5144be`. Latest source-grounded R43 candidate is **not** curated CURRENT, **not** full semantic Stage4, and **not** a real installed-browser/IndexedDB Stage6 acceptance.

## Meaning corrections from CURRENT German, not historical textbook

**Eight exact source sections / sixteen Persian-English language fields / one German sentence**, each with complete source text, exact before/after fields and rationale in the recovery archive's `03-Reports/LESEN-R43-EXACT-SEMANTIC-REPAIR-LEDGER.json`:

- **023/p06 FA+EN:** Restore employer–employee division of further vocational training responsibility rather than generic shared duty.
- **033/p06 FA+EN:** Music class should be **judged by educational contribution**, not just have a declared/clear role.
- **036/p02 FA+EN:** Nutrition literacy helps children make **informed daily decisions**; the initial translations only said general food literacy.
- **039/p03 FA+EN:** Blanket cost requirements are inappropriate **if** income and study/training circumstances are not considered. The specific condition was dropped in FA/EN.
- **043/p03 German+FA+EN:** Current German first sentence inaccurately framed the **need for inclusion resources and planning** as a *danger*; replace with truthful `Trotz dieser Vorteile bleibt zu berücksichtigen, dass ...`, and keep the genuine `dass` dependent clause and stable sentence ID. Both translations' final sentence also restores **practical steps accommodating different needs**, not only generic policies. Retire precisely old derived attributive adjective marker `ftg-0023` no longer found in this sentence, and reanchor all other p03 section-relative offsets. No other German source changed.
- **048/p02 FA+EN:** Patient need for **conversation and personal attention** in treatment, not vague communication needs.
- **049/p02 FA+EN:** Volunteer work offers perspectives young people **would scarcely encounter in their ordinary environment**.
- **058/p03 FA+EN:** Boarding-school fit **depends on personality and family circumstances**, not generic disapproval of boarding schools.

All other 470 source sections, 340 questions, 350 vocab, 669 curated grammar examples and 68 stable reading identities untouched. Fulltext grammar count **3,538→3,537** by deliberate retirement of one no-longer-evidenced annotation, not inventory loss.

## Explicit machine-versus-editorial boundary

The owner ZIP includes `03-Reports/LESEN-R43-ALL-410-NONP05-RISK-TRIAGE.json` recording all **410 non-p05 sections** with content field hashes, source sentence counts, length ratio risk flags and status. This is **mechanical screening**, not independent semantic translation review.

**Only eight** entries carry an explicit source-adjudicated correction. **402** remain pending a substantive second pass; the previous 478/478 first pass and 68/68 p05 second pass remain historically preserved, not upgraded to independent semantic certification.

## Reproduced technical evidence

- Independent source/runtime exact-delta and grammar offsets: **25,318/25,318 checks PASS**, **12/12** deliberately corrupt candidate mutations rejected; **3,537/3,537** exact section-relative grammar offsets and all 669 curated grammar IDs valid under existing narrow guards.
- Exact current v505 `reading-content-import-v38.js` SHA `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc` executed in isolated Node VM: **PASS zero errors/warnings**, **10/10** malformed packs rejected, 68 readings and 340 exercises projected in memory. This is **NOT** a real Chrome IndexedDB Stage6 test.
- Portable ZIP `Lesen-R43-NONP05-RISK-TRIAGE-AND-SEMANTIC-REPAIRS-CANDIDATE-20261109.zip`, SHA `225f3829fe0eba33c1fad9091a35af0524903a6cc21f86eef8faae3a1b14adf2`, **3,506,125 bytes, 19 entries/18 SHA256SUMS**, CRC PASS. Stored owner Library `/Flasch kart/German-Content-Production-Kit/Content/Lesen/Checkpoints/Lesen-R43-NONP05-RISK-TRIAGE-AND-SEMANTIC-REPAIRS-CANDIDATE-20261109.zip`, stable ID `libfile_6ec3f02f9ac08191ac1ea2d6254e1b44`. Post-upload materialization yielded exact raw bytes and SHA-256, extracted fresh and reran `python -B 04-Tools/verify_portable_r43.py`: exact parent→child master/runtime, QA and v505 native source **PASS**.

**Gates:** Wholepack Stage4 **HOLD**; original complete native nine-lens grammar extraction **NOT RERUN**; true installed Chrome IndexedDB Stage6 **NOT RUN**, Stage7 **NOT RELEASED**. No human review requirement reinstated. Protected original curated CURRENT ZIP SHA `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` unchanged; no app UI/FSRS/SRS/other-family changes and no deletion.

**Next R44:** Continue exact owner Library R43 content and meaning-based review of 402 remaining non-p05 sections in substantive high-risk-first batches. Do not count machine screen as linguistic second-pass PASS.
