# Grammatik aktiv A1–C1 — Production Workspace

This workspace is the durable Git-backed production area for integrating the two user-supplied grammar books into German Flashcards Pro without mixing source extraction, canonical content, QA, and runtime integration.

## Sources

- `Grammatik aktiv A1–B1` — expected chapter inventory: 80 chapters.
- `Grammatik aktiv B2–C1` — expected chapter inventory: 88 chapters.
- Combined expected source chapter inventory: **168 chapters**.

The books are source authorities for chapter order, chapter naming, source examples/tables/exception coverage, and source lineage. Learner-facing explanations and exercises are normalized into a structured canonical grammar model before runtime projection.

## Working principle

Do **not** build the 168 chapters directly inside the app.

Production flow:

```text
PDF sources
  -> source inventory + stable chapter IDs
  -> canonical grammar concepts + source-chapter lessons
  -> provenance-aware explanations/rules/examples/errors/exercises
  -> linguistic + structural QA
  -> Grammar Runtime Pack
  -> exact-version Flashcards Pro acceptance
  -> one final structured release package
```

## Workspace layout

```text
00-source/      source identity, hashes, locators, runtime-baseline note
01-inventory/   168-chapter catalog, stable IDs, section/CEFR mapping, inventory QA
02-canonical/   Grammar Content Contract + canonical lesson/concept data
03-evidence/    evidence bindings and source-derived/generated distinction
04-qa/          structural, linguistic, coverage, duplicate/concept QA
05-delivery/    runtime projection and loss/parity validation
06-runtime/     exact Flashcards Pro acceptance evidence
07-release/     one final package, manifest, hashes, post-package verification
CHECKPOINT.json durable seven-stage state
```

## Non-negotiable rules

1. `main` is not modified by this workspace. Production work happens on branch `grammar-aktiv-a1-c1-production` until explicitly merged.
2. No chapter is called complete merely because a PDF page was extracted.
3. A source chapter and a grammar concept are separate entities. Multiple chapters/levels may map to the same canonical grammar concept.
4. Every learner-facing rule/example/error/exercise keeps provenance: source-derived, source-adapted, generated, or externally verified.
5. Long source text/pages are not copied into the app as a substitute for structured content.
6. Existing Flashcards Pro UI appearance is not changed during content production. Runtime/UI changes are deferred to the integration stage.
7. Final delivery remains **one structured release ZIP**, not separate user/developer ZIPs.

## Current status

Stage 1 is `RUNNING`: source identities and hashes are frozen; the full 168-chapter inventory is the next authoritative artifact.

The intended runtime supplied in chat is `GFP v411 R43`, while the connected `German-Flashcards-Pro/main` still reports an older v352-era README. Therefore runtime acceptance is intentionally deferred until the Git/runtime baseline mismatch is reconciled. No app repository changes are made from this workspace yet.
