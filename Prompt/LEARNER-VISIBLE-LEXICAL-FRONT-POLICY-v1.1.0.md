# Learner-Visible Lexical Front Policy v1.1.0

Status: ACTIVE HOTFIX OVERLAY (HF2) for German vocabulary projection.

## Purpose
Neutral presentation identity does **not** permit learner-visible morphology to disappear. `de-vocabulary` remains the one ordinary-vocabulary presentation family, while required morphology must bind to the actual learner-visible front in every supported surface.

## Required visible bindings
- Noun Sense: show an explicit article-bearing singular form and the verified plural when applicable. Multi-gender/substantivized nouns must expose every reviewed article-bearing singular form represented by the canonical meaning. Examples: `der Bart, Bärte`; `der Prominente / die Prominente, die Prominenten`; `der Neue / die Neue / das Neue, die Neuen`.
- Verb Sense: show the clean infinitive/lemma plus verified 3sg Präsens, Präteritum and Perfekt. Example: `reagieren, reagiert, reagierte, hat reagiert`.
- Adjective Sense: show comparative/superlative when verified/present.
- Expression: preserve the canonical expression form. Argument placeholders belong to expression/structure patterns, not to a Verb Sense lemma.

## Noun morphology normalization
The learner-visible noun model MUST understand all approved canonical shapes, including:
- simple `article` + headword + `plural`;
- `singular_forms` + `plural`;
- nested substantivized-adjective `person_forms.singular_forms` / `person_forms.plural`;
- nested `thing_forms.forms` / `thing_forms.article`; only article-bearing noun forms belong to the main front (e.g. `das Neue`; `etwas Neues` stays semantic/example data, not a replacement for the article-bearing form).

An ordinary Noun Sense may not silently pass with no article-bearing form. Missing article or plural requires an explicit machine-readable reviewed disposition such as `article_status` / `plural_status = NOT_APPLICABLE` or `CLOSED_NO_FORCE`; absence alone is FAIL.

## Lemma cleanliness
For Verb Sense targets, argument placeholders (`etw.`, `jdn.`, `jdm.`, `jemanden`, `jemandem`, `etwas`, explicit case markers, etc.) MUST NOT be part of the lexical lemma/headword. Reflexive `sich` is allowed when it is lexical. A form like `sich etw. ansehen` is not a clean Verb Sense lemma; the clean lemma is `sich ansehen`, while the argument pattern stays in structure/Rektion.

## Transport/runtime rule
- `card_type = de-vocabulary` remains unchanged.
- `custom_fields.presentation_contract = gfp-vocabulary-neutral@1` remains unchanged.
- `typingCore` remains the clean lexical lemma, not the expanded display string.
- Generic surfaces that render `front` must receive a learner-complete display form.
- Rich Study/Quick presentation must independently expose the same required morphology from canonical semantic fields.
- Runtime compatibility fallback must never replace a richer approved raw front with a poorer derived front.

## QA hard gate
Stage 5 fails if required learner-visible bindings are absent, if nested noun morphology is lost, if a Verb Sense lemma is polluted by argument placeholders, or if the final learner front differs from the normalized canonical display model. Stage 6 must probe actual Study/Quick/model/generic front output using simple nouns, multi-gender/substantivized nouns and verbs. Metadata presence alone is FAIL.
