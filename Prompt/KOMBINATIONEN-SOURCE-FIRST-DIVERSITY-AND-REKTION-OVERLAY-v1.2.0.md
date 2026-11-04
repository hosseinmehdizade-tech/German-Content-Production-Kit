# Kombinationen: source-first diversity + Rektion role boundary v1.2.0

**Status:** USER-APPROVED OPERATIONAL CONTENT OVERLAY, 2026-11-04. Prospective at the next safe editable source-bound lexical Stage 3 boundary. Applies to all lexical workstreams (Menschen A1/A2/B1 and future sources) without rewriting historical LOCKED artifacts. Supersedes only the candidate-discovery preference and the separate Rektion tile semantics in the prior combination policies; keep all remaining v3.3.6, lean Stage3/Stage4, risk-based Stage4, graph, source, copyright and non-fabrication protections. Does not claim completed Stage4/5/6/7 or UI release.

## Problem / desired learner benefit

A card's four German example sentences already show the word in context. Copying their fragments into the right-hand `Kombinationen` adds little. For `der Weg`, `auf dem Weg sein` and `den richtigen Weg finden` are basic; a stronger mix illustrates lexical diversity, e.g. `ein mühsamer Weg`, `auf halbem Weg`, `den Weg versperren`, `den Weg kennen`, `der Weg zum Erfolg`. **No quota, no forced figurative/technical item.** Creativity = verified natural combinations, varied syntactic templates, surprising but relevant contrasts, clear bilingual explanations; NOT hallucinated, obscure, or overly literary language.

## Candidate discovery — genuinely source-first, not examples-first

1. Resolve the exact card sense, learner level, registered source inventory, all existing combinations, and 4 DE/FA/EN examples. Examples are **a non-novelty comparison set**, not a default generator. Do not copy an example fragment to satisfy combination completeness.
2. Consult available registered dictionaries/corpora and the exact course source for useful lexical patterns (Duden / DWDS when accessible, course source, dict.cc as *secondary supplemental dictionary*, PONS/Langenscheidt for translation). Browse live entries per lemma/sense where available; record source ID, exact URL/entry locator, access date and whether that entry actually supports the proposed pattern. If access is blocked or indirect, record `UNVERIFIED` — never pretend a search snippet proves a source-specific claim it does not contain.
3. Look for **independent slots and pattern families**, according to word class and meaning: adjective+noun; verb+accusative noun; preposition/locative phrase; noun+genitive or noun+preposition; phrasal/idiomatic/metaphorical extension; typical professional construction only when relevant. For verbs use object, preposition, manner, register, fixed idiom; for adjectives use noun pairing, degree, complements and oppositions. A two-word fragment can be very good; a full sentence may be an *example*, not a collocation.
4. Assemble candidate expressions in correct dictionary form, with inflection, case and capitalisation (e.g. **`den Weg sperren`**, never `der Weg sperren`). Reject semantic shift without a declared matching sense; mark an advanced domain-specific expression (e.g. `kritischer Weg` in CPM/project management) as specialist rather than forcing it onto a general A2 `der Weg` card.
5. Select only cases with defensible **added teaching value** beyond the card's examples and its already approved combinations. Diversity is a review preference, not an automatic required count. If one especially useful new phrase survives, one is enough; zero can be `CLOSED_NO_FORCE` with source-backed reason. Do not confuse abstract syntax slots with extra lexical expression entries.
6. Every accepted item carries `de`, source-appropriate `fa`, `en` (when profile requires), `kind`/pattern family, a sense/level, `teaching_delta`, and truthful `origin` (`REGISTERED_SOURCE`, `CURATED_PEDAGOGICAL`, etc.), source reference/provenance and independent Stage4 disposition. An AI-authored variation inspired by a dictionary remains **CURATED_PEDAGOGICAL** until the exact pattern is verified; a dictionary's presence in the source registry does not verify every expression or translation.
7. Copyright and attribution: use dictionary entries to validate individual short lexical phrases, not bulk-extract an entire site or copy its example sentences into the cards. Provide citations/entry URLs in audit metadata, not a dictionary dump. No automatic scraping or bulk page replication. Original authored DE/FA/EN explanations and context where needed.

## Rektion versus Kombinationen — exact division of responsibilities

- `Rektion` visible tile: abstract governed argument or required case/preposition when **the grammatical valency itself** needs concise teaching, e.g. `warten auf + Akkusativ`, `jemandem helfen + Dativ`. One validated grammatical assertion, not another copied example. Keep original `REKTION` graph typing.
- `Kombinationen` visible tile: **lexicalised/reusable concrete German combinations**, e.g. `auf den Bus warten`, `einen schweren Weg gehen`; internally preserve `COLLOCATION`, `NVV`, `pattern`, `adjective_noun`, etc. This tile may demonstrate the Rektion pattern as a real phrase, provided it teaches additional vocabulary or usage. `NVV` is *not* relabelled as `COLLOCATION` in canonical graph.
- Same text or merely the grammatical slot **must not** appear twice across the two tiles. When a combination says nothing beyond `warten auf + Akk.`, choose the abstract Rektion tile and do not create a fake extra lexical Kombination. Conversely, if the abstract Rektion adds no information beyond an already clear concrete combination and independent grammatical relevance is not established, keep the combination and omit the redundant Rektion tile. If both give distinct value, both are permitted, with separate `teaching_delta`.
- No mandatory Rektion for every word, especially nouns like `Weg`; differentiate prepositional adverbials (`auf halbem Weg`) from true government/valency. A preposition occurring in a phrase does **not** automatically prove `REKTION`.
- This resolves the old policy line “all Rektion families go under one visible Kombinationen section” only in respect of **one distinct, user-approved Rektion tile for nonredundant abstract valency**. All true combination families still use one visible `Kombinationen` tile. UI 15-category ordering is unchanged. Backend semantic types and provenance remain separate.

## One-pass editorial and quality operations

- Stage3 3A/3B/3C remain **one authoring pass**; source-first research and same-card example comparison are a single integrated decision, not new manual review rounds.
- Stage4 risk-based independent QA checks German correctness, sense, frequency/level, literal vs idiomatic interpretation, idiomaticity, bilingual DE/FA/EN, evidence, duplicate and cross-tile added value. Flags may be advisory when ambiguity is low; ungrounded exact source claims and linguistic errors are HIGH.
- Stage5 projects accepted structured combination **as one DE/FA(/EN) learner-visible item**, never flattens metadata keys `de/fa/en/kind` into separate lines. The runtime adapter requires source-shape parity tests before claiming UI acceptance. The known 196-card A1 structured-combination rendering gap is separate; this overlay does not fix it by itself.
- Stage6/7 remain dependent on actual current-version import, persistence, display and packaging; never claim full PASS from policy/QA alone.
- LOCKED sources/collections and their verified examples are immutable. Reopen only via separately hashed successor under a real editor/workstream authority. Do not overwrite the user's installed collection or SRS state.

## Compact authoring record (illustrative shape; optional fields depend on workstream)

```json
{
  "card_ref": "EXACT_STABLE_ID_FROM_ACTIVE_SOURCE",
  "sense_id": "sense_1",
  "candidate": {"de": "auf halbem Weg", "fa": "در نیمهٔ راه", "en": "halfway", "kind": "prepositional_phrase", "teaching_delta": "PATTERN"},
  "origin": "REGISTERED_SOURCE",
  "evidence": [{"source_id": "dict_cc_de_en", "locator": "https://www.dict.cc/german-english/Wege.html", "access_status": "VERIFIED_EXACT_ENTRY"}],
  "status": "REVIEWED_CANDIDATE_PENDING_CURRENT_STAGE4",
  "comparison": {"examples_checked": 4, "duplicates_removed": 0, "reused_example_fragment": false},
  "display_target": "Kombinationen"
}
```

**Warning:** This example record format is guidance, not a migration of all old serializers. Use exact current workstream schema and compatible projections.