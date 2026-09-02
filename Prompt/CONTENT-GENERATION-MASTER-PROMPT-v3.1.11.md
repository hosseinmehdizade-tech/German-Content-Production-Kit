# General German Content Generation Master Prompt v3.1.11
## Lexical Quality + Runtime Acceptance Hardening

This file is the normative v3.1.11 overlay on `CONTENT-GENERATION-MASTER-PROMPT-v3.1.10.md`.
Architecture v3.1.5 and semantic contract 3.1.3 remain unchanged.

## 1. Quality outranks field density

The v3.1.10 rule `no fabrication to satisfy counts` remains binding and is strengthened:

- Absence of a trustworthy collocation is not a reason to manufacture or infer one.
- A source-availability gap is reported as coverage, not converted into fake learner content.
- `PRODUCT_CONTENT_COMPLETE` may PASS with fewer than three collocations when every included learner-facing claim passes the lexical-quality gate.
- Collocation density is a preferred coverage target, not a hard truth criterion.

For Menschen A1 use `MENSCHEN-A1-CONTENT-COMPLETENESS-v1.1.0.json`.

## 2. Every included collocation is a hard quality claim

A `connections[kind=collocation]` value must be all of the following:

1. explicitly supported by verified collocation/collocational evidence;
2. atomic learner-facing text, not a dictionary/editorial bundle;
3. aligned with the selected Learning Unit sense;
4. free of source UI/editorial text such as `Bearbeiten`, `Verzeichnis`, section labels or instructions;
5. not a comma/slash bundle that still contains multiple alternatives;
6. for a reflexive headword, aligned with the reflexive sense;
7. for a fixed/prepositional headword, aligned with the written construction rather than a different base-lemma sense.

Raw source shorthand may be normalized only by repeating grammatical material already explicit in the same source item. Lexical material must not be invented during atomicization.

## 3. Examples are not collocation evidence

A phrase mechanically extracted from this card's example sentence must never be promoted to canonical `collocation` merely to improve coverage.

If a future target intentionally exposes an example-derived learner combination, it must use an appropriate semantic kind such as `common_combination` and retain explicit lineage to the example. It must not satisfy a collocation hard claim.

## 4. Synonym / antonym safety

Synonyms and antonyms are optional unless a target profile explicitly says otherwise.

A broad part-of-speech section is not sufficient sense evidence when a lemma has multiple senses. If the extraction cannot bind the lexical relation to the selected Learning Unit sense, omit it and report the coverage gap.

Never preserve a wrong relation because the UI has a Synonym or Antonym slot.

## 5. Rektion from explicit learner headwords

When the learner-facing headword explicitly encodes valency (`jdn.`, `jdm.`, `etw.` and/or a governed preposition), `details.rection` must be explicit and evidence-linked.

A deterministic grammar analysis of the current headword may be used as current-dataset evidence when it only decodes information already written in the headword, for example:

- `jdn.` -> Akkusativ
- `jdm.` -> Dativ
- `mit` -> Dativ
- `für` -> Akkusativ

Ambiguous two-way prepositions require sense-aware case resolution; do not guess from the preposition alone.

## 6. Runtime acceptance is part of Delivery QA

A TSV/JSON artifact is not Final merely because its cells parse as JSON.

For the declared target runtime (currently German Flashcards Pro v354), the release must execute the target importer/presentation contract or an exact version-pinned acceptance fixture and prove at least:

- all rows import;
- no duplicate or invalid card IDs are introduced;
- `examples`, `related`, `opposites`, `details`, and `custom_fields` have the expected runtime shapes;
- the canonical envelope round-trips without loss;
- German examples remain grouped with their FA/EN translations;
- front core verb forms render;
- no raw JSON is exposed as learner-visible text;
- changed learner-facing details render through the Presentation model without exceptions.

A transport-only PASS cannot be promoted to Final without this acceptance evidence.

## 7. Incremental source workflow — do not refetch everything

For subsequent books/sources:

1. inventory the source units once;
2. create a stable canonical ID/headword map;
3. cache source responses by normalized lemma + source + access date/version;
4. rerun only missing/stale/changed units;
5. keep raw source evidence separate from canonical learner content;
6. classify/atomicize after retrieval, not during transport export;
7. run lexical-quality validation before product-density reporting;
8. run runtime acceptance on the final projected artifact;
9. package only after the two gates above PASS.

Rate-limit failures must be retried with backoff and cached; a second full 275-page refetch is a pipeline defect, not a normal workflow.

## 8. Required gates

For a current rich-card release, run in this order:

```text
Canonical / Architecture validation
Linguistic audit
Lexical Quality Gate
Product Completeness / coverage report
Delivery projection
Target Runtime Acceptance
Post-package hash verification
```

`Final` is allowed only when all hard gates actually executed and passed. Preferred coverage may remain incomplete and must be reported numerically rather than hidden or fabricated.
