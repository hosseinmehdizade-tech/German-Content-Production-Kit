# GFP v411 Vocabulary Projection v1.0.0

Purpose: losslessly project lexical Sense/Expression objects into the ordinary German Flashcards Pro vocabulary library.

- Sense -> one vocabulary card.
- Expression -> one vocabulary card.
- `nvv` and `idiom` are ordinary lexical cards, not separate application sections.
- Do not invent CEFR, relations, component IDs, or lexical evidence during projection.
- Preserve exactly four examples when the active profile requires four.
- Word Explorer consumes definition/translation/structure/source refs.
- Wortnetz consumes projected relations plus resolved structure components.
- v411 may derive inbound edges at runtime; projection must not serialize those as canonical facts.
