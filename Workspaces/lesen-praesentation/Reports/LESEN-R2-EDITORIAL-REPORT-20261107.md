# Lesen B2–C1 — R2 three-unit editorial successor (2026-11-07)

**Scope:** Real content edits in `LES-PRES-035` (Elektronische Geräte), `LES-PRES-051` (Technische Studiengänge), `LES-PRES-059` (Fernstudium/Präsenzstudium). This is a **separate candidate**, not a rewrite of accepted v1.3.0, and not a compiled import pack.

**Authority:** v1.3.0 immutable ZIP SHA-256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` at `/Flasch kart/German-Content-Production-Kit/Content/Lesen/Current/`. New candidate master SHA-256 `bbeec4c3823879b5037c3669edbc41f2a441662312887f84a8f0ee9bb2e61549`. This candidate has an exact, reversible field patch including DE/FA/EN text plus question before/after values.

## Material improvements

- **035:** device benefits, unequal access, school-provided support and goals now align across DE, FA, EN; three evidence-specific reading questions replace generic templates.
- **051:** removed a nonsensical generic benefit conclusion from a causal gender/technical-studies explanation; restored a credible cultural-vs-individual explanation, checked DE/FA/EN and wrote three topic-specific questions.
- **059:** replaced ‘it is dangerous that even campus students must study independently’ with the substantive limitation that both formats require self-management and program support varies; narrowed three questions to actual study-organization evidence.

All 65 other units are exact-original JSON item records. All **68 IDs**, **340 question IDs**, **478 reading sections** and **669 curated grammar annotations** retain stable identity and 3-unit anchors are present in their linked German sentences. All edited units remain 300–500 German words. Existing 68-unit coverage and DE/FA/EN translations remain present.

## Hard independent QA and known HOLDs

- Separate source-native verifier: **20/20 scoped structural tests PASS**, including parent ZIP/master SHA, unchanged 65 units, sentence concatenation, question/evidence links, grammar anchored substring/linked sentence, content wordcounts and truthful aggregate metadata.
- The old full-text grammar engine **was NOT rerun**: 4,578 of 4,612 exact legacy spans survive and were shifted to their new exact text positions; **34 spans lost their old target text** and are documented by ID and sentence in `LESEN-R2-3UNIT-DELTA-AND-QA-20261107.json` for regeneration. The top-level grammar QA status is explicitly `INCOMPLETE`, not PASS.
- Across the 68 readings the 58-unit question-template problem falls to **55** because 035, 051 and 059 now use distinct prompts. Additional exact sentence duplicate instances fall from **479 to 467**. The other 55 units have NOT been rewritten.
- Independently found **eight inherited word-count metadata mismatches** (004, 005, 012, 025, 031, 038, 048, 055). These are untouched baseline issues, not introduced by R2. They remain in the verification ledger; no unapproved broad edits.
- This is a targeted language revision, not independent all-unit semantic Stage4. Compiled/runtime projection and real browser import against current v505 are **not done**; previous exact v505 preentry PASS applies **only to historical v1.3.0 runtime**, not to this newly edited master.

## Exact next action

Run a source-native grammar derivation for affected 3 lessons and verify offsets/metadata, then independent adversarial DE/FA/EN meaning review. Only after content Stage4 and separate compiler/Stage5 gates should an importable R2 runtime be produced; native Stage6/Stage7 stay separate. Do not switch current to candidate, remove originals, edit app UI, or touch learner SRS/FSRS. No report-only ZIP.

## Durable files

- `Candidates/Lesen-Production-Master-v1.3.0-R2-3UNIT-EDITORIAL-CANDIDATE.json` — candidate master (Library only, Git stores only exact pointer)
- `Reports/LESEN-R2-3UNIT-FIELD-PATCH-20261107.json` — reversible edited-field diff
- `Reports/LESEN-R2-3UNIT-DELTA-AND-QA-20261107.json` — unmatched grammar trace ledger
- `Reports/LESEN-R2-INDEPENDENT-QA-20261107.json` — independent assertions and inherited issues
- `Checkpoints/QUALITY-REVIEW-CHECKPOINT-R2-20261107.json` — resume/governance authority