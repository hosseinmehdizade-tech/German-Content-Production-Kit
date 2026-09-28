# GFP v411 Vocabulary Projection v1.1.0 — Unified Vocabulary Envelope

Purpose: losslessly project lexical Sense/Expression objects into the ordinary German Flashcards Pro vocabulary library without leaking linguistic part of speech into presentation geometry.

- Sense -> one ordinary vocabulary card.
- Expression -> one ordinary vocabulary card.
- New production MUST use the neutral ordinary vocabulary envelope `cardType = de-vocabulary` for every lexical Sense/Expression.
- `german-verb` is legacy compatibility input only. New projection MUST NOT emit it.
- Noun, verb, adjective, adverb, phrase, Redemittel, NVV, idiom and other lexical Expressions share the same outer import/presentation envelope.
- Preserve POS, category, morphology, Rektion, expression type/subtype, relations and structure as semantic fields.
- Optional detail sections may differ because data differs; POS/card type must never select a different Study/Flashcard container geometry.
- Do not invent CEFR, relations, component IDs or lexical evidence.
- Preserve exactly four examples when the active profile requires four.
- Stage 5 must run the unified projection validator; any non-neutral ordinary-vocabulary card type is a failure.
- Stage 6 must sample noun/verb/adjective/expression when present and assert shared canonical Study geometry.
