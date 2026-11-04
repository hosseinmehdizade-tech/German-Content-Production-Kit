# Source-first combinations, diversity and Rektion boundary — implementation receipt
Date: 2026-11-04. User-directed. **Scope: POLICY + SOURCE REGISTRY + TOOL + PILOT, not user-installed app or source LOCKED edits.**

## Changes persisted in GitHub main
- `Prompt/KOMBINATIONEN-SOURCE-FIRST-DIVERSITY-AND-REKTION-OVERLAY-v1.2.0.md`: candidate research **from registered dictionaries/corpora before examples**; no example-derived default filling; teaching benefit/diversity, actual source URLs, language sense/learner level, no number quota, no fake dictionary claims, no bulk copyrighted example copying.
- `Prompt/KOMBINATIONEN-ACTIVE-POLICY.json`, `Prompt/START-PROMPT-v3.3.6.md`, `README.md`: active overlay wired into existing one-pass Stage3 and independent risk-based Stage4, with historical contracts preserved.
- `Architecture/03-SOURCES/SOURCE-REGISTRY.json`: `dict_cc_de_en` registered as **approved secondary per-entry dictionary source**, with `collocation/usage` claims but NOT grammatical valency/Rektion claims; Duden/DWDS/grammis remain primary grammar/usage corroboration.
- `Verification/audit_kombinationen_source_first_v1_2.py`: advisory, read-only checks for exact example clones / mere fragments, cross-tile exact Rektion duplicates, duplicate combinations, missing FA/EN, false source claims, source evidence and low-diversity family. `Verification/tests/test_audit_kombinationen_source_first_v1_2.py`: **19/19 unittest PASS locally**, including negative/non-destructive cases. The new diagnostic is NOT a replacement for existing `Verification/audit_kombinationen_mehrwert.py` or Stage4 acceptance.
- `Workspaces/menschen-a2-24-lessons-v336/Proposals/DER-WEG-SOURCE-FIRST-KOMBINATIONEN-PILOT-20261104.json`: independent provenance-bound illustrative 7-item `der Weg` shortlist with 6 structural kinds, explicit DE/FA/EN, original four examples for comparison, `rection=[]`, extended-level marking and rejections. Standalone diagnostic **0 issues**; independent Stage4 linguistics/translation, exact current card-ID and source hash remain pending. Screenshot number `#814` is NOT assumed a stable card ID.

## Important semantic distinction
- `Rektion` visible only for independently useful **abstract governed case/preposition/argument valency**, e.g. `warten auf + Akk.`.
- `Kombinationen` visible for **specific useful phrases**, e.g. `auf den Bus warten`. A shared verb/preposition is acceptable when separate learning value exists, but not a duplicate field. An ordinary locative `auf halbem Weg` is NOT a claim that the noun Weg governs `auf + Dativ`.
- No `Rektion` asserted for `der Weg` without evidence. `kritischer Weg` is domain-specific, not a compulsory A2 expression. `der Weg sperren` corrected to `den Weg sperren` as an accusative object, while the sample instead uses attested `den Weg versperren`.

## QA limits and release decision
- Independent refetch of **8 modified/relevant Git files** after commits and **11/11 cross-file checks PASS** (registered source exactly once, secondary-only, allowed claims and URL refs, active link, installed code/test, proposal without fake card ID, no fictitious Rektion, diversity, source/copyright notes, active Start Prompt and README).
- No native A2 collection mutation, content export, app UI, import, SRS, Wortnetz, source identity, older LOCKED artifact, or Stage4/5/6/7 completion asserted. The full multilingual object rendering defect identified previously for some A1 cards is a distinct app runtime issue; this source-first policy does not cure it.
- Future Stage3 editors should use one source-first research pass with justified delta, then existing Stage4 challenge. Historical cards only by explicit versioned successor.

## Portable audit kit in personal Library

- Archive: `GCPK-KOMBINATIONEN-SOURCE-FIRST-V1.2-20261104.zip` (content-only; **not the app or a ready-to-import A2 release**).
- SHA256: `cc73a503494519fac077e0f17bb2c10666f0d43ff03e3e7c9564c3013a35815f`, size **15,018 bytes**, **8 files** (7 checksummed entries). ZIP CRC and all SHA256SUMS verified; unit tests 19/19 PASS.
- Verified Library path: `/Flasch kart/German-Content-Production-Kit/Candidates/GCPK-KOMBINATIONEN-SOURCE-FIRST-V1.2-20261104.zip`; stable ID `libfile_6670863d9c4881919511e7c76b3a2a01`; upload and list readback succeeded.
- The archived guide, advisory tool, tests and `der Weg` pilot are copies of the committed policy/tool/proposal; the canonical active policy and source registry reside in Git, no historical locked card content rewritten.
