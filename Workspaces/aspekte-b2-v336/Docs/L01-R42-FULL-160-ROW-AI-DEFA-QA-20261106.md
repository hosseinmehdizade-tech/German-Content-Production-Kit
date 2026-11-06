# Aspekte B2 — Kapitel 1 R42: row-by-row German–Persian AI QA

**Date 2026-11-06. Sole lexical source: user's edited sanitized CSV.** This is a genuine manual AI read of all **160 rows** and all **320 DE / 320 FA AI-authored example pairs**, followed by targeted edits; it is **not** an independent human or separate-model audit. No claims of release approval.

## What changed in the same stable canonical file

- **13 distinct source rows**, **14 edited fields**, 160/160 reviewed (AI); **147 rows** did not receive a new edit in this pass.
- Fixes: 1565 (natural Persian), 1578 (Elite concept), 1588 (societal language plurality), 1590 (amtlich is not ordinarily gradable in its institutional sense), 1618 (natural Persian), 1633 (Unverständnis not Missverständnis), 1638 (kontrovers ≠ merely different), 1660 (two better Persian tense renderings), 1668 (contextual gradability of vollkommen), 1681 (natural Persian), 1697 (ticket office gloss), 1698 (natural Persian), 1703 (Milieu biological medium ≠ ecology/environmentalism).
- Duden confirmed that **entstammen: ist entstammt** was **already correct** in parent R41; it was not silently changed or double-counted as an edit.
- No source fields, source examples or original user lexical rows were changed. All 160 edited rows preserve contiguous IDs and 13 original user examples. Draft example counts remain 320/320, zero nonempty-field failures.
- Source-comparison only verifies integrity against the **already edited project CSV**. Publisher files were not consulted for vocabulary membership.

## Release decisions still pending

17 legacy R39 HOLD source rows (cross-level identity, split/merge and grammar), 48 original FIX proposals previously reconciled in R38 but without independent final signoff. Source-linked proposal: split #1586 adjective and noun, keep #1588 contextual noun, canonical #1640 + alias #1641 (no deletion), attach #1660 Partizip II to kommen (no independent infinitive), prior B1 final identity reuse for #1630 only if accepted app identity is verified. **These are proposals, not executed card merges or imports.**

Stage 2 = **NOT APPROVED**; Stages 3–7 = **NOT STARTED**; imported/published cards = **0**. Human signoff = false; separate independent model review = false. Comprehensive global R25/L05 checkpoint is not overwritten. This is one local canonical L01 editorial checkpoint, not the full-project release.

## Auditable files

- `Current/L01-CANONICAL-WORKING-NONIMPORT.csv`, SHA256 `9da4568db9edc592429d35d2ddac4a91fb5369cfff1a5782ce1ce5ef74b88d0b` (replaces earlier Library current working copy under same pathname, retaining Library version history).
- `Reports/L01-R42-13-ROW-14-FIELD-AI-QA-EDITS.csv`, SHA256 `e60effa5c1f60c2318ea09dae1488e3689918c267a10906df2e3eb181e4eed7e`.
- `Reports/L01-R42-QA-SUMMARY.json`, SHA256 `fe87483f73ded8b32db018b27a042fcfcf3a1e36b57d4745ea06bfa0b73c9416`.

Lexicographic evidence strictly for morphology/semantics (not source membership): https://www.duden.de/rechtschreibung/entstammen ; https://www.duden.de/sprachwissen/sprachratgeber/steigerung-komparation-deutsche-adjektive .

## Authoritative Library IDs

- Canonical working CSV: `libfile_aa88f1a1a0908191ac691a7a5f3ed7c8` (overwritten in-place).
- 13-row, 14-field corrective matrix: `libfile_7aaef513fd688191b833b97f46856ac5`.
- QA summary: `libfile_9717ab286214819197555e2fe89d1578`.
- Current L01 canonical ZIP: `libfile_4ac85525a4ac8191994b0ba71f1e6f1e`, SHA256 `93bbff27342182cf702184eadcedb465ccbf66e15b9d0693c2bb7aa7fda3eccf`.
