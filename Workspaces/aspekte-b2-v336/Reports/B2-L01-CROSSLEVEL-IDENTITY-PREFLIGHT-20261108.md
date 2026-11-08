# Aspekte B2 · L01 — Cross-level identity and SRS preflight

**Status:** READ-ONLY, BLOCKED_NONIMPORT. **No learner content or user SRS changed.**

## Checkpoint

- 158 candidate learner cards plus 2 documented noncard objects cover all 160 L01 source ordinals. Ordinal 1586 is split into ADJ/NOM units; ordinals 1640+1641 are combined into one unit.
- Of seven R40 cross-level cases, six are B2 card drafts and **intolerant (1630) is a noncard reuse sidecar**.
- gekommen (1660) is a separate grammar-only sidecar, not a new vocabulary card.
- The app repository current version is v505-R141, but **full real-browser runtime/individual learner SRS state is not attested**.
- Existing B1/A2 IDs are *documented content references*, not proof of live imported cards.

## Seven cases

| Source | Lexeme | Record | Decision | Gate |
|---|---|---|---|---|
| 1556 | abenteuerlich | CARD_DRAFT | KEEP_STANDALONE_B2 | INDEPENDENT_B2_SEMANTIC_QA |
| 1575 | ständig | CARD_DRAFT | HOLD_B1_USAGE_ENRICHMENT_LINK | LIVE_B1_SRS_CARD_ID_AND_ADJECTIVE_SENSE_QA |
| 1609 | entscheidend | CARD_DRAFT | KEEP_STANDALONE_B2 | INDEPENDENT_B2_SEMANTIC_QA |
| 1616 | die Art | CARD_DRAFT | HOLD_A2_ENRICHMENT_OR_B2_FALLBACK | LIVE_A2_SRS_CARD_ID_AND_B2_PHRASE_QA |
| 1630 | intolerant | NONCARD_REUSE_SIDECAR | KEEP_NONCARD_CONDITIONAL_B1_REUSE | LIVE_B1_SRS_CARD_ID_BEFORE_ANY_ENRICHMENT |
| 1671 | zerreißen | CARD_DRAFT | KEEP_STANDALONE_B2 | INDEPENDENT_B2_VERB_VALENCY_QA |
| 1697 | die Kinokasse | CARD_DRAFT | KEEP_STANDALONE_B2 | INDEPENDENT_B2_SEMANTIC_QA |

## Release control

Approval requires **(1)** independently signed DE/FA semantic QA, **(2)** a read-only export of actual accepted A1/A2/B1 card IDs and relevant SRS profiles, and **(3)** native app transactional import/persistence/rollback test on safe copy, not the actual user data.
Until then: no duplicate deletion, no SRS migration, no B2 release.

## Provenance

- Canonical L01 SHA256: `72bddff2d900322b8fb3b3b7094d59281636c5bc6be390aae46d74d35ed32716`
- Noncard sidecar SHA256: `c74442d8fef409391a2789d06b4abbe13c39b01922c685215a7f0008dda2a10d`
- Prior crosslevel decision source: `Workspaces/aspekte-b2-v336/Reports/L01-R40-7-CROSSLEVEL-CURRENT-FINAL-TSV-DECISIONS.csv`
- App root authority: `German-Flashcards-Pro/RUNTIME-AUTHORITY-PIN.json`
