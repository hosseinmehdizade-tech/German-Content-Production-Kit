# LEXICAL KOMBINATIONEN ENRICHMENT POLICY v1.0.0

Status: **ACTIVE**
Framework overlay: **German Content Production Kit v3.3.6**
Supersedes for scope: `Prompt/VERB-KOMBINATIONEN-ENRICHMENT-POLICY-v1.0.0.md`

## 1. Purpose

Every lexical target should teach not only an isolated headword, but also useful natural combinations that show how the word is actually used in German.

The learner-facing model is intentionally simple:

> **Kombinationen**

This is a lexical enrichment layer, not a verb-only feature.

It applies to verbs, nouns, adjectives, adverbs and lexical expressions whenever meaningful combinations exist.

## 2. Learner-visible contract

Each applicable lexical card has at most one visible section:

`Kombinationen`

Do not create separate learner-visible sections for:
- Rektion
- Kollokationen
- Nomen-Verb-Verbindungen
- Adjektiv + Nomen
- Verb + Nomen
- Adverb + Adjektiv
- Verb + Präposition
- Redewendungen
- typische Objekte
- Art und Weise / Wie?
- fixed expressions
- context/direction/frequency/time patterns

All accepted useful combinations are projected into the single `Kombinationen` section.

Backend typing and provenance remain structured.

## 3. Applicability

Mandatory review applies to all lexical targets, including:
- verbs and verb senses;
- nouns;
- adjectives;
- adverbs;
- lexical expressions / multiword expressions;
- other vocabulary targets when a useful combination dimension exists.

Not every lexical target must end with visible items. If useful natural combinations cannot be justified, close the dimension as `CLOSED_NO_FORCE`.

This policy does not force enrichment onto Grammar lessons, Lesen passages, Schreiben prompts, UI strings or other non-lexical content unless they explicitly produce standalone vocabulary cards.

Historical LOCKED artifacts remain immutable. Retrofits use explicit successor/enrichment workstreams.

## 4. Combination families by lexical class

### 4.1 Verbs
Possible internal families include:
- typical object: `eine E-Mail schreiben`
- rection: `an jemanden schreiben`
- manner: `sorgfältig schreiben`
- context: `im Unterricht sprechen`
- direction/time/frequency patterns
- Nomen-Verb-Verbindung
- fixed/semi-fixed expression: `etwas zu Papier bringen`

### 4.2 Nouns
Possible internal families include:
- adjective + noun: `eine wichtige Entscheidung`
- verb + noun: `eine Entscheidung treffen`
- noun + governed preposition/frame: `Angst vor etwas`
- support-verb pattern: `Angst haben vor ...`
- typical quantifier/measure when genuinely lexical: `ein Stück Kuchen`
- fixed/semi-fixed expression: `zur Entscheidung kommen`
- common contextual phrase

### 4.3 Adjectives
Possible internal families include:
- degree/intensifier: `sehr wichtig`, `besonders schwierig`
- adjective + governed complement: `stolz auf jemanden sein`
- copular frame: `für jemanden wichtig sein`
- common noun pairing when it teaches actual usage: `eine schwierige Aufgabe`
- contrastive/contextual pattern when useful

### 4.4 Adverbs
Possible internal families include:
- intensifier/adverb pairing: `ganz besonders`
- verb + adverb: `oft vorkommen`
- temporal/spatial pattern: `direkt danach`, `ganz oben`
- sentence-use pattern when lexical rather than purely grammatical

### 4.5 Lexical expressions
Possible internal families include:
- common slot filling;
- natural extensions;
- typical object/complement;
- common register/context;
- fixed continuations or variants when they remain the same lexical meaning.

## 5. Backend type vocabulary

Suggested internal kinds include, but are not limited to:
- `object`
- `rection`
- `noun_verb`
- `adjective_noun`
- `adverb_adjective`
- `manner`
- `pattern`
- `context`
- `direction`
- `frequency`
- `time`
- `measure`
- `degree`
- `fixed_expression`
- `support_verb`
- `extension`

Backend kind is QA metadata. It must not create separate visible subsections.

## 6. Quality rule: creativity without fabrication

Creative pedagogical combinations are allowed and encouraged when they are genuinely natural and useful.

Every accepted item must be:
1. natural contemporary German;
2. semantically compatible with the target sense;
3. useful beyond merely repeating the headword;
4. non-duplicative and not a trivial reformulation;
5. appropriate to the learner level, or exceptionally high-value with explicit review justification;
6. translated according to the workstream language contract;
7. backed by honest provenance.

Do not invent a source claim because a phrase sounds plausible.

## 7. No hard density quota

There is no mandatory number of combinations per card.

Common productive words may naturally support many combinations. Narrow lexical items may support only a few or none.

`CLOSED_NO_FORCE` is valid and preferred over weak, artificial, redundant or excessively advanced filler.

A numerical target must never justify fabrication.

## 8. Provenance

Each item keeps an internal origin, such as:
- `REGISTERED_SOURCE`
- `PARENT_GENERATED_EXAMPLE`
- `PARENT_CANONICAL_RELATION`
- `CURATED_PEDAGOGICAL`

Rules:
- `REGISTERED_SOURCE` requires explicit evidence refs with registered source identity and usable locator.
- Model-created/curated items remain curated unless independently supported.
- Generated examples are not silently promoted to source evidence.
- Source material enriches/verifies; it does not silently replace source inventory or identity.
- Do not coerce free combinations into legacy relation taxonomies merely for storage convenience.

## 9. Stage integration

### Stage 3A — baseline richness audit
For every lexical target, inspect whether useful combinations already exist in examples, relations and registered sources.

### Stage 3B — gap-driven enrichment
Generate only useful missing candidates from registered sources, accepted parent examples, existing relations and reviewed curated patterns.

### Stage 3C — disposition closure
Every applicable target's Kombinationen dimension ends as:
- accepted/reviewed content present;
- justified `CLOSED_NO_FORCE`;
- policy-permitted `NOT_APPLICABLE`.

Rejected candidates should be persisted where the workstream supports rejection memory.

### Stage 4 — independent linguistic/provenance QA
Re-check:
- naturalness;
- semantic fit;
- lexical-class appropriateness;
- learner level;
- duplicate/near-duplicate risk;
- translation;
- backend kind;
- origin/evidence.

Structural PASS does not equal linguistic PASS.

### Stage 5 — projection
Project accepted items into exactly one learner-visible `Kombinationen` section, while preserving internal kind/provenance metadata.

## 10. Adoption

### New lexical workstreams
Adopt immediately from the first enrichment stage.

### Active workstreams before Stage 5
Adopt at the next safe Stage3B/Stage4 boundary. Backfill already-completed current-batch lexical targets before Stage4/Stage5 closure rather than destructively regenerating them.

### Projected but not LOCKED work
Use a bounded successor/repair/enrichment step. Invalidate only affected downstream dependencies.

### LOCKED / FINAL historical releases
Remain immutable. A successor/enrichment workstream adopts this policy.

## 11. Menschen adoption

- `menschen-a1-verben-kombinationen-v336` remains a valid verb-focused retrofit pilot and now conforms to this broader lexical policy.
- `menschen-a1a2b1-memrise` adopts this policy for **all lexical targets**, not only verbs.
- Current A1-L22 Stage3B applies this policy to remaining lexical targets; already checkpointed A1-L22 lexical targets must be audited/backfilled before Stage4/Stage5 closure.
- Future A2 and B1 lexical production adopts it from the first enrichment stage.
- Historical LOCKED Menschen releases remain immutable and use successor enrichment for retrofits.

## 12. UI boundary

This policy defines content structure, not a visual redesign.

Use the existing generic detail-section path when available. Any significant new UI component or visual redesign still requires explicit user approval.

## 13. Acceptance invariant

A lexical card is Kombinationen-complete only when:
- the dimension was explicitly reviewed;
- accepted items are natural, useful and non-redundant;
- evidence claims are honest;
- backend kind/provenance is preserved;
- the learner sees at most one coherent `Kombinationen` section;
- no density quota forced weak content;
- empty cases are explicitly closed rather than silently omitted.
