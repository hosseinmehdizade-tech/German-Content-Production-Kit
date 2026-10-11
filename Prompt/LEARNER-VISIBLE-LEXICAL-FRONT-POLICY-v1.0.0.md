# Learner-Visible Lexical Front Policy v1.0.0

Status: ACTIVE HOTFIX OVERLAY for German vocabulary projection.

## Purpose
Neutral presentation identity does **not** permit learner-visible morphology to disappear. `de-vocabulary` stays the single ordinary-vocabulary presentation family, while required morphology must still bind to the actual learner-visible front in every supported surface.

## Required visible bindings
- Noun Sense: show article + lemma; show plural when verified/present. Example: `der Bart, Bärte`.
- Verb Sense: show clean infinitive/lemma plus verified principal forms (3sg Präsens, Präteritum, Perfekt) in generic front text or the runtime's visible morphology slots. Example: `reagieren, reagiert, reagierte, hat reagiert`.
- Adjective Sense: show comparative/superlative when verified/present.
- Expression: preserve the canonical expression form. Argument placeholders belong to expression/structure patterns, not to the lexical lemma of a Verb Sense.

## Lemma cleanliness
For Verb Sense targets, `etw.`, `jdn.`, `jdm.`, `jemanden`, `jemandem`, case markers and other argument placeholders MUST NOT be part of the lexical lemma/headword. Reflexive `sich` is allowed when it is part of the lemma. Argument structure remains in `structure.argument_slots`, `grammarPattern`, Rektion, or expression targets.

## Transport/runtime rule
- `card_type = de-vocabulary` remains unchanged.
- `custom_fields.presentation_contract = gfp-vocabulary-neutral@1` remains unchanged.
- `typingCore` remains the clean lexical lemma, not the expanded display string.
- Generic surfaces that render `front` must receive a learner-complete display form.
- Rich Study/Quick presentation must independently expose the same required morphology from canonical semantic fields; raw metadata presence alone is not acceptance.

## QA hard gate
Stage 5 fails if required learner-visible bindings are absent or if a Verb Sense lemma is polluted by argument placeholders. Stage 6 must probe actual Study/Quick front output and model output for noun article/plural and verb principal forms. Data presence without visible binding is FAIL.
