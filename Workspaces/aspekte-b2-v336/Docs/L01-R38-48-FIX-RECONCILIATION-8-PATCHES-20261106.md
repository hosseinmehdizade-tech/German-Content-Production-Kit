# Aspekte B2 — L01 R38: 48-FIX editorial reconciliation, eight precise deltas

**Scope:** only B2. User CSV is the sole vocabulary inventory; no source additions/deletions/merges. This is an **AI editorial pass, not independent/human semantic certification**.

- Compared **48/48** historical R28 FIX entries with current R37 DE/FA draft front/back and their immutable user CSV source rows.
- **40** R28 issues are already represented in R37 reasonably at an AI-editorial level; they are **not release-approved**. **8** rows require additional fixes: **1552, 1555, 1559, 1574, 1643, 1644, 1674, 1684**.
- Noteworthy: #1552 restore source's neglected polysemy; #1559 include both `nach + Dativ` and `in + Akkusativ`; #1574 restore the invoice line-item sense. #1555, #1643, #1644, #1684 have explicit nominal gender/plural/declension front forms; #1674 distinguishes adverbial use and rare genitive.
- The eight corrections live in an **8-row overlay**, not an untracked rewrite of R37 or the user source. Apply only after additional QA and only with the exact source-ordinal join.
- All 160 source IDs and original source strings preserved; 13 nonempty original examples, 320 AI example drafts + 320 FA translations remain in R37. 17 other HOLD gates are untouched.
- Corrective morphology on the front has **not** been integrated into the real app: hide redundant `Formen` on back only if the front includes the complete **verified** paradigm, per the proposed display policy.

## Evidence URLs for specific claims

- https://www.duden.de/rechtschreibung/aufloesen
- https://www.duden.de/rechtschreibung/auswandern
- https://www.duden.de/rechtschreibung/Position
- https://www.duden.de/rechtschreibung/Nachmieter
- https://www.duden.de/rechtschreibung/Nachmieterin
- https://www.duden.de/rechtschreibung/Pate_Taufpate_Patron_Patenonkel
- https://www.duden.de/rechtschreibung/entsprechend_betreffend_laut
- https://www.duden.de/rechtschreibung/Einwanderer

## Gate status

Stage2 not approved; no independent full 48-row QA, no live earlier-level accepted-card evidence; 17 holds outstanding. Stage3–7 not started; importable cards **0**. The main R25 L05 portable checkpoint is unchanged.

## Exact Library artifact IDs

- 48-row matrix: `libfile_bf83a72d1e2c8191931287eb80e8edba`.
- 8-row delta: `libfile_ddc158c69e688191bd03a3f2ce4b0b7c`.
- Summary: `libfile_26cd720a3f6c819199b67ad96756feb2`.
- Checkpoint ZIP: `libfile_d07243f29ed4819190e319887fed2af5`, SHA256 `c70742f86fafe87cde12e14b3e4099874c8ef4b148ad1396f9645099bb335146`, size 13088 bytes; exact fresh Library readback and manifest verification passed.
