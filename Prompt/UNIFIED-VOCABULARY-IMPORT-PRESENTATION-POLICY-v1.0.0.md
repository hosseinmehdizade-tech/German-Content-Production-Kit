# Unified Vocabulary Import & Presentation Policy v1.0.0

Status: ACTIVE MANDATORY OVERLAY  
Date: 2026-09-28

## Purpose

All ordinary German lexical content uses one neutral Flashcards import/presentation envelope regardless of part of speech.

This policy exists because legacy projections used `german-verb` versus `de-vocabulary` as top-level card types, and historical runtime code treated `german-verb` as a Study-layout discriminator. That leaked linguistic POS into presentation geometry and produced inconsistent card layouts.

## Normative rules

1. **One ordinary vocabulary envelope**
   - Noun, verb, adjective, adverb, function word, phrase, Redemittel, Sense and lexicalized Expression all project to the same ordinary vocabulary import/presentation envelope.
   - New production MUST NOT use POS to select a separate visual card template.

2. **POS stays semantic**
   - Preserve POS in canonical `lexeme.pos`, projected `category`, `entry_type`, morphology, Rektion, structure and custom fields as appropriate.
   - POS-specific morphology is required when the source/profile requires it.
   - Semantic distinctions must never be erased merely to unify presentation.

3. **Neutral projected card type**
   - New direct-import projections use the neutral ordinary vocabulary card type `de-vocabulary` for lexical Sense/Expression cards.
   - `german-verb` is legacy compatibility input only and MUST NOT be emitted by new production.
   - Existing legacy files remain importable.

4. **Presentation independence**
   - Study/Flashcard geometry MUST NOT branch on noun/verb/adjective/adverb/expression or legacy card type.
   - Optional content sections may appear when data exists (e.g. morphology, Rektion, synonyms, collocations), but container/grid/column ownership remains canonical and shared.

5. **Projection tooling**
   - A projector that hard-codes `german-verb`, maps POS to different card containers, or emits mixed visual card types for ordinary vocabulary FAILS Stage 5.
   - Expressions remain semantic Expressions but use the same neutral card envelope.

6. **Stage 5 QA**
   - Verify every projected ordinary lexical card has `card_type=de-vocabulary`.
   - Verify semantic POS/category/morphology/Rektion data is preserved losslessly.
   - Verify legacy input compatibility separately; legacy compatibility is not permission to emit legacy types.

7. **Stage 6 presentation QA**
   - Include at least one noun, verb, adjective and expression when present in the dataset.
   - Assert the same canonical Study layout owner / geometry contract across those cards.
   - Assert POS-specific detail sections do not change outer card geometry.

## Runtime compatibility

German Flashcards Pro v450/R84 is the first runtime root fix that removes legacy structured-verb Study geometry ownership. Runtime compatibility with old `german-verb` files remains required, but new content production must emit the neutral envelope above.

## Relationship to semantic model

This policy does **not** flatten linguistic structure. It unifies the transport/presentation envelope only. Canonical lexical identity, Sense/Expression splits, POS morphology, Rektion and relations remain governed by the v3.3.2 master content contract.
