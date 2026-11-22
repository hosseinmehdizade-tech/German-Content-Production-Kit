# Aspekte neu C1 — Rich Card Production Contract v1.0.0
Status: ACTIVE FOR ALL FUTURE/MUTABLE C1 CARDS; registered 2026-11-22. Owner: Aspekte C1. This is an additive source-specific card-level requirement routed through the active GCPK v3.3.6 start prompt and global version-pinned policies. It does **not** rewrite historical master prompt files, source material, portable checkpoints, apps, SRS, or already accepted cards.

## Required outcome — one complete C1 card

1. **Lexical identity:** one stable card per verified lexical target, with all accepted senses on that one card (MEM-009). Do not split each sense into another SRS card. Retain genuine lexical/part-of-speech/expression identity exceptions after review.
2. **Meaning:** each accepted meaning has a useful German explanation/definition, accurate Persian translation and accurate English translation. Never infer English from a Persian-only back; retain source context and meaningful sense distinctions.
3. **Exactly four examples per card:** four **distinct**, natural German example sentences or appropriate complete utterances, each with an accurate Persian **and** English translation, grouped as a DE/FA/EN triplet. Four is a **card-level** rule, not a mandatory four examples per sense. If a word has multiple senses, select examples to represent important uses without a separate sense quota. If four truthful useful examples cannot be produced, keep the card HOLD; never fabricate filler.
4. **Five right-side categories reviewed for every card:** Synonyme, Antonyme, Wortfamilie, Verwandte Wörter, Kombinationen. Each category must receive either VERIFIED_PRESENT with sourced, sense-aligned learner-facing entries, CLOSED_NO_FORCE with a concrete reason, or NOT_APPLICABLE with a concrete reason. HOLD cannot ship. Genuine empty categories may remain unrendered, **not** stuffed with invented relations. When present, each relation contains German and Persian; a Kombination additionally carries its meaningful English translation.
5. **Kombinationen:** use independent source-first evidence and an explicit teaching benefit. Do not copy a complete example into Kombinationen. Phrase/expression overlap with an example alone is a REVIEW signal, not proof of an error; if overlapping, record source and independent teaching delta. Do not turn examples, bare Rektion or generic word associations into false collocations.
6. **Grammatical accuracy:** confirm applicable article/plural, verb principal forms/auxiliary/reflexive/separability, adjective degrees, Rektion and usage/register. Verified non-applicability is allowed; never invent inflection. Follow central HF2 front/back, morphology, neutral de-vocabulary transport and typed relation policies.
7. **QA and provenance:** each new or changed card undergoes German/Persian/English linguistic correctness review, example-to-sense alignment, five-section taxonomy review, cross-tile duplication checks and actual source/lexical evidence. The structural script below is only a fail-closed preflight, NOT linguistic QA, real Stage5 builder parity, installed app Stage6 or release certification.

## Execution boundary and no-stage-regression rule

- **Stage1 remains IN_PROGRESS with 0 approved cards.** Finish the current curated cross-level semantic KEEP/DROP/MERGE analysis without re-extracting the PDF. This contract starts at Stage2/3 construction, is challenged at Stage4 and rechecked against the **actual selected C1 card bytes and packaged projection** at Stage5. Do not claim any C1 Stage2–7 PASS until real evidence exists.
- QA entrypoint: `python Workspaces/aspekte-c1-v336/04-qa/validate_c1_rich_card.py ACTUAL_C1_CARDS.json` or `ACTUAL_C1_PROJECTION.tsv`. It accepts an explicit typed C1 canonical card list or a TSV projection with exact JSON columns `meanings`, `examples`, `details`, and `c1_right_review` (top-level or inside `custom_fields`). `c1_grammar_review` is also mandatory. Missing/unmapped structures are BLOCKED, not assumed from flat strings.
- Existing canonical/import schema is not replaced. The C1 native producer must map its actual accepted canonical/TSV fields into this auditable view losslessly; run the checker **before and after** the Stage5 package on the exact hashes, alongside official global validators. If no native adapter exists, **STAGE5 BLOCKED**, not fake success.
- Structural pass means *only* counts/translated-field presence/section decisions/obvious clones are structurally present. Check semantics, grammar, idiomaticity and noncopy source evidence with the applicable central Stage4 policies. Never hide QA fields by deleting data or override accepted central safety rules.

## Central authorities inherited

`Prompt/ACTIVE-PROMPT.txt → Prompt/START-PROMPT-v3.3.6.md → Prompt/GLOBAL-POLICY-SYNCHRONIZATION-v1.0.0.md → Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json`

Use active global related-taxonomy, lexical-relation, KOMBINATIONEN didactic/source-first, HF2 and morphology policies. The MEM-009 optional-per-sense example rule does **not** waive this compatible and stricter **per-card** four-example requirement.

## Currentness

Only a new C1-specific **policy and preflight** were introduced on 2026-11-22; no C1 card data, Library portable ZIP or checkpoint hash changed. The accepted 2026-11-06 Stage1 portable bundle remains the authoritative content state.