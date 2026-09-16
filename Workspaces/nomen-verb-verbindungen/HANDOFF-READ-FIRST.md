# NVV Production — Persistent Handoff / READ FIRST

Updated: 2026-09-16  
Canonical workspace: `nomen-verb-verbindungen`  
Workstream branch: `hosseinmehdizade-tech/German-Content-Production-Kit` → `nvv-production`

## Unified project resume rule

This workstream no longer uses an NVV-only handoff hierarchy. It follows the same project-wide authority chain as Grammar, Lesen, Schreiben and other future workstreams.

Before substantial work in every new/resumed chat:

1. Read `German-Content-Production-Kit/main/PROJECT-BOOTSTRAP.md`.
2. Read `German-Content-Production-Kit/main/PROJECT-STATE.json`, `README.md`, active `Prompt/START-PROMPT-v3.1.12.md`, `SOURCE-ACCESS-PROTOCOL-v1.0.0.md`, and `SOURCE-REGISTRY.json`.
3. From `PROJECT-STATE.json`, resolve this workstream branch and read:
   - `Workspaces/nomen-verb-verbindungen/CHECKPOINT.json`
   - `Workspaces/nomen-verb-verbindungen/00-source/SOURCE-MANIFEST.json`
4. Resolve the raw source using the Source Access Protocol: explicit newer current-chat source → Project Sources → Library → matching current-chat attachment.
5. Only when runtime/import/presentation compatibility matters, read `German-Flashcards-Pro/main/PROJECT-BOOTSTRAP.md` and `PROJECT-STATE.json`, plus any explicitly newer current app artifact.
6. Continue from the exact `next` action in the live CHECKPOINT. Preserve bounded PASS work unless a real upstream change invalidates it.

Chat history, old ZIP names and remembered runtime versions are not project authority.

## Source identity

- `source_id`: `deutsch-aber-hallo-nomen-verb-verbindungen`
- canonical title: `Deutsch - Aber Hallo! Nomen-Verb-Verbindungen`
- source SHA-256: `a817dab76f9e78e896f596bd37b66168f04e995fd68203c045c7d87437ac258d`
- PDF pages: 26
- Source Manifest: `Workspaces/nomen-verb-verbindungen/00-source/SOURCE-MANIFEST.json`

If the same title resolves to different bytes, do not silently substitute it.

## Current production target

Inventory / identity status:
- source bullet items: 2,475
- FVG: 859
- Idiom/Redewendung: 519
- general NVV: 1,097
- slash/variant source items reviewed: 221
- semantic split source items: 17
- current provisional expression identities: 2,493
- lexeme identities: 1,512
- open evidence/sense issues: 1 (`etw. / jdn. in Anspruch nehmen` polysemy)

User-approved learning model:
- each final expression = one vocabulary card
- NVV/FVG/Idiom stays inside Wortschatz; no separate NVV practice silo
- German definition (`definition_de`) required
- Persian meaning required
- English gloss required
- structure/Rektion required where applicable
- exactly 4 original German learner examples per completed card
- every example gets FA + EN translation
- Word Explorer and Wortnetz use the same canonical lexical graph
- relation/component navigation must fail closed when ambiguous
- no material flashcard visual redesign without user approval

## Completed bounded PASS work

Completed cards: 26 / 2,493  
Completed examples: 104  
FA example translations: 104  
EN example translations: 104  
Completed pilot batches: 2

Batch 0001 and Batch 0002 remain bounded PASS checkpoints. Do not regenerate them casually.

## Runtime evidence vs current runtime authority

Historical bounded runtime evidence:
- `GFP-v411-DEVELOPMENT-BASELINE-R37.zip`
- SHA-256: `fc8c9c82216cb8fe3699bbd293618e91599e24038f9ac1c2b8eaa74589e3cc0b`
- 52/52 component resolutions
- 52 reverse Wortnetz links
- runtime JS syntax PASS
- runtime asset references PASS
- inline script syntax PASS
- live browser import/persistence/reload NOT RUN

R37 is historical evidence only. It is **not** the current runtime authority.

At the 2026-09-16 migration, `German-Flashcards-Pro/main/PROJECT-STATE.json` reported durable runtime `v411-R44`. That observation is informational only; Stage 6 must always resolve the actual current runtime live at acceptance time.

## Current seven-stage pipeline state

1. Source & Inventory — PASS
2. Canonicalization — RUNNING
   - slash variant review PASS
   - evidence-driven sense resolution RUNNING
3. Evidence & Enrichment — RUNNING
   - 26 completed cards
4. Linguistic & Lexical QA — RUNNING
   - Batch 0001 PASS
   - Batch 0002 PASS
   - cumulative 26-card validation PASS
   - global dataset QA not complete
5. Delivery Projection — RUNNING
   - 26 cumulative projected cards
6. Runtime & Presentation Acceptance — RUNNING
   - historical R37 bounded acceptance retained
   - current runtime acceptance must be resolved live
7. Release & Post-Package Verification — NOT_STARTED

## Scalable production cadence

Batch 0003 is the first scalable batch:
- target 100 safe expressions end-to-end
- ambiguous/polysemous/conflicting items go to persistent REVIEW-QUEUE and are replaced by the next safe item
- after two clean 100-card batches, cadence may increase to 150
- never exceed 200 without explicit user approval
- every 500 completed cards run a cross-batch global audit

Per-batch stages:
B1 Sense/Evidence Lock → B2 DE/FA/EN Meaning → B3 Structure/Lexical Graph → B4 Exactly 4 examples + FA/EN → B5 QA → B6 Live-resolved runtime projection/acceptance → B7 Git-backed persistent checkpoint.

## Persistence protocol

After every successful batch update:
- `CHECKPOINT.json`
- this `HANDOFF-READ-FIRST.md`
- cumulative canonical data
- cumulative projected data
- QA/acceptance reports
- persistent review queue
- artifact/hash manifest
- downloadable cumulative checkpoint ZIP when practical

GitHub is the durable coordination layer. A local ZIP is a backup/handoff convenience, not a parallel source of truth.

## Exact next action

Start Batch 0003 with 100 safe expressions using the unified project startup chain. Preserve Batch 0001/0002. Keep `etw. / jdn. in Anspruch nehmen` quarantined until its supported senses are resolved. At B6 resolve the current Flashcards runtime live rather than treating R37 as current.
