# Menschen Locked Lesson Delivery Contract v1.0.0

## Rule

Every lesson-level `LOCKED.zip` artifact must be directly importable by the current German Flashcards Pro runtime. The user must never need to extract a nested `05-delivery/*.zip` first.

## Required package contract

- Exactly one authoritative `BUILD-METADATA.json`.
- `BUILD-METADATA.json -> data_file.filename` points to the exact final TSV/JSON import dataset.
- The declared data file exists exactly once in the outer LOCKED bundle.
- QA/source TSV files may coexist and must be ignored by the runtime importer.
- Sidecar SHA-256 verification remains mandatory.
- Ambiguous or multiple authoritative sidecars fail closed.

## Mandatory Stage 7 gate

Before a lesson may be marked PASS/LOCKED:

1. Select the outer lesson `LOCKED.zip` directly in the latest resolved Flashcards runtime.
2. Preview must select the sidecar-declared final dataset, not source/QA TSVs.
3. Commit must PASS.
4. Persisted card count must equal the lesson projection.
5. Cumulative import with all previously locked lessons must PASS without ID collisions.
6. The resulting lesson bundle is the user-facing import artifact; no hidden second ZIP workflow is allowed.

Current runtime support: GFP v417/R51 and later compatible runtimes.
