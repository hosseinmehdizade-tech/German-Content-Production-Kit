# VERB KOMBINATIONEN ENRICHMENT POLICY v1.0.0

Status: **ACTIVE**  
Framework overlay: **German Content Production Kit v3.3.6**  
Applies to: German verb targets and verb expressions in vocabulary/content workstreams.

## 1. Purpose

German verb cards must teach not only the isolated lemma and morphology, but also useful natural combinations that show how the verb is actually used.

The learner-facing model is intentionally simple:

> **Kombinationen**

There must not be separate learner-visible sections for `Rektion`, `Kollokationen`, `Nomen-Verb-Verbindungen`, adjective/adverb usage, fixed expressions, typical objects, direction, frequency, time, context, or similar subtypes.

These distinctions may and should remain structured in backend metadata for QA, evidence, future filtering and analytics.

## 2. Applicability

This policy is mandatory for:
- targets whose semantic lexical core is a German verb;
- `german-verb` cards;
- verb senses projected through a generic vocabulary card type;
- verb expressions when a Kombinationen section is pedagogically meaningful.

It is not automatically required for nouns, adjectives or other non-verb targets.

Historical LOCKED artifacts remain immutable. This policy applies to new work and to explicit successor/enrichment workstreams.

## 3. Learner-visible contract

Each applicable card has at most one visible combination section:

`Kombinationen`

All accepted useful combinations are projected into this one section.

Do **not** create separate visible headers such as:
- Rektion
- Kollokationen
- Nomen-Verb-Verbindungen
- Verb + Präposition
- Adjektiv + Verb
- Redewendungen
- Wie? / Art und Weise

The visible section should feel like one coherent set of natural ways to use the verb.

## 4. Eligible combination families

Useful items may come from any of these internal families when natural and pedagogically valuable:

- `object`: typical object or noun phrase, e.g. `eine E-Mail schreiben`
- `rection`: governed preposition/case/personal pattern, e.g. `an jemanden schreiben`
- `nvv`: Nomen-Verb-Verbindung / Funktionsverb-like combination when relevant
- `manner`: adjective/adverbial manner, e.g. `schnell schreiben`, `sorgfältig arbeiten`, `unleserlich schreiben`
- `pattern`: useful argument or sentence pattern
- `context`: common situational use
- `direction`: directional use
- `frequency`: typical frequency expression
- `time`: typical temporal use
- `fixed_expression`: useful fixed or semi-fixed expression
- another reviewed internal type only when the workstream needs it

No family has a mandatory quota. Variety is desirable, but naturalness and learning value win over density.

## 5. Quality rule: creativity without fabrication

Creative pedagogical combinations are allowed and encouraged, especially useful adjective/adverbial patterns and realistic contexts.

Every accepted combination must satisfy all of the following:
1. natural contemporary German;
2. semantically compatible with the target sense;
3. useful enough to teach something beyond the bare lemma;
4. not a near-duplicate of another item on the same card;
5. not artificially generated merely to reach a number;
6. appropriate to the workstream level, or exceptionally high-frequency/useful with an explicit review justification;
7. translated according to the workstream's required learner-language contract.

Examples of the intended richness include:
- `schnell schreiben`
- `sorgfältig schreiben`
- `unleserlich schreiben`
- `jemandem schreiben`
- `an jemanden schreiben`
- `eine Prüfung schreiben`
- `etwas zu Papier bringen`

These are examples of the design, not a fixed list.

## 6. No hard density quota

Do not force a fixed number of combinations.

For a common productive verb, a candidate generation pass may often find roughly 4–8 useful items, sometimes more. A narrower verb may have fewer.

`CLOSED_NO_FORCE` is valid when further items would be weak, redundant, unnatural, too advanced or unsupported.

A numerical target must never justify fabrication.

## 7. Provenance and evidence

Each combination retains an internal origin. Recommended origin vocabulary:

- `REGISTERED_SOURCE`
- `PARENT_GENERATED_EXAMPLE`
- `PARENT_CANONICAL_RELATION`
- `CURATED_PEDAGOGICAL`

Rules:
- `REGISTERED_SOURCE` requires explicit `evidence_refs` with registered `source_id` and a usable locator.
- A model-created or curated item must never be labeled source-backed merely because it sounds natural.
- Generated parent examples remain generated evidence unless independently supported by a registered source.
- Source material verifies/enriches; it does not silently replace source identity or course inventory.
- Backend typing must not be coerced into legacy relation types merely to fit an old taxonomy.

## 8. Stage integration

### Stage 3A — Baseline richness audit
For each applicable verb target, inspect existing examples, relations and source evidence for already-present useful combinations.

### Stage 3B — Gap-driven enrichment
Generate only meaningful missing candidates from:
- registered sources;
- accepted parent examples;
- existing canonical relations;
- curated pedagogical patterns.

### Stage 3C — Disposition closure
Every proposed combination ends in an explicit accepted/rejected/closed disposition. Rejected low-value candidates should remain recorded so they are not repeatedly regenerated.

### Stage 4 — Independent linguistic/provenance QA
Re-check:
- idiomaticity;
- semantic fit;
- level appropriateness;
- duplicate/near-duplicate risk;
- translation quality;
- backend kind;
- origin;
- evidence claims.

A structural PASS is not a linguistic PASS.

### Stage 5 — Projection
Project all accepted items into exactly one learner-visible `Kombinationen` section while retaining internal typing/provenance metadata.

Runtime compatibility is resolved only when runtime acceptance actually matters.

## 9. Adoption rule for current and future workstreams

### New workstreams
Adopt this policy immediately for all applicable verb targets from the first enrichment stage.

### Active workstreams before Stage 5
Adopt at the next safe enrichment/QA boundary. Already completed sub-batches do not need destructive regeneration; they must be audited/backfilled before Stage 4/Stage 5 closure if their verb targets lack this contract.

### Active workstreams already projected but not LOCKED
Do not silently mutate accepted projection bytes. Use a bounded successor/repair/enrichment step and invalidate only the affected downstream dependency.

### Historical LOCKED releases
Remain immutable. Add combinations only through an explicit successor/enrichment workstream.

## 10. Current Menschen adoption

- `menschen-a1-verben-kombinationen-v336` is the pilot/successor authority for retrofitting already-produced A1 verb cards. Continue from its newest accepted/candidate checkpoint.
- `menschen-a1a2b1-memrise` adopts this policy for current and future verb targets. The current in-progress A1-L22 enrichment must apply it at the next safe Stage3B/Stage4 boundary. Any already-completed A1-L22 sub-batch is audited/backfilled before Stage4/Stage5 rather than silently regenerated.
- Future A2 and B1 production in the unified Menschen workstream uses this policy from its first applicable verb target.
- Previously LOCKED A1/A2/B1 artifacts remain historical evidence and are not rewritten solely to satisfy this policy.
- Any future successor of the locked Menschen B1 verb repair/enrichment also uses this policy.

## 11. UI boundary

This policy defines content structure, not a new visual design.

If the current runtime can already render a generic detail section titled `Kombinationen`, use that path. Any significant new UI/UX component or visual redesign still requires explicit user approval under the project UI-preservation policy.

## 12. Acceptance invariant

An applicable verb card is combination-complete only when:
- the combination dimension has been reviewed;
- accepted items are natural and useful;
- rejected/closed candidates are explicit where applicable;
- source-backed claims have real evidence;
- the learner sees one coherent `Kombinationen` section;
- internal kind/provenance remains preserved;
- no density quota has forced weak content.
