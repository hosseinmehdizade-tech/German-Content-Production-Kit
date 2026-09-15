# NVV Production — Persistent Handoff / READ FIRST

Updated: 2026-09-15
Canonical workspace: `nomen-verb-verbindungen`
Persistent Git branch: `hosseinmehdizade-tech/German-Content-Production-Kit` → `nvv-production`

## Non-negotiable resume rule

In every new chat/session, BEFORE producing or changing anything:

1. Read this file from branch `nvv-production`.
2. Read `Workspaces/nomen-verb-verbindungen/CHECKPOINT.json` from the same branch.
3. Read the latest cumulative canonical/projected state and validation/acceptance reports.
4. Inspect current `German-Flashcards-Pro/main` and compare against the pinned app baseline below; do not silently downgrade or overwrite newer valid app work.
5. Preserve completed bounded batches. Do **not** regenerate Batch 0001 or Batch 0002 unless an upstream contract change explicitly invalidates them.
6. Continue from the exact `next` action in CHECKPOINT.

Chat history is never the source of truth. A local `/mnt/data` file is not the only source of truth. The Git-backed checkpoint + latest downloadable checkpoint ZIP are the continuation anchors.

## Current production target

Source: `nomen_verb_verbindungen.pdf` (Deutsch – Aber Hallo!, May 2023)

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
- Word Explorer and Wortnetz are universal lexical infrastructure for all vocabulary-card types, not only NVV
- component and relation targets should be clickable only when they resolve safely; ambiguity must fail closed
- do not materially redesign the existing flashcard appearance without user approval

## Completed production work

Completed cards: 26 / 2,493
Completed examples: 104 (4 per card)
FA example translations: 104
EN example translations: 104
Completed batches: 2

Batch 0001 (13 cards):
- DAH-NVV-EXP-00149 — einen Antrag stellen
- DAH-NVV-EXP-00314 — einen Beitrag leisten
- DAH-NVV-EXP-01694 — Rücksicht nehmen
- DAH-NVV-EXP-00345 — einen Beschluss fassen
- DAH-NVV-EXP-02137 — etw. zur Verfügung stellen
- DAH-NVV-EXP-00111 — etw. in Angriff nehmen
- DAH-NVV-EXP-00374 — etw. in Betracht ziehen
- DAH-NVV-EXP-01891 — Stellung nehmen
- DAH-NVV-EXP-00265 — den Ball flach halten
- DAH-NVV-EXP-00266 — etw. auf die lange Bank schieben
- DAH-NVV-EXP-00190 — jdn. auf den Arm nehmen
- DAH-NVV-EXP-00078 — sich zum Affen machen
- DAH-NVV-EXP-00077 — sich aus der Affäre ziehen

Batch 0002 (13 cards):
- DAH-NVV-EXP-00038 — Abschied nehmen von + Dat.
- DAH-NVV-EXP-00042 — etw. zum Abschluss bringen
- DAH-NVV-EXP-00052 — die Absicht haben
- DAH-NVV-EXP-00059 — Abstand nehmen von + Dat.
- DAH-NVV-EXP-00066 — etw. außer Acht lassen
- DAH-NVV-EXP-00019 — ein Abkommen schließen mit + Dat.
- DAH-NVV-EXP-00023 — eine Abmachung treffen mit + Dat.
- DAH-NVV-EXP-00025 — eine Abneigung haben gegen + Akk.
- DAH-NVV-EXP-00026 — eine Abneigung hegen gegen + Akk.
- DAH-NVV-EXP-00121 — Anklage erheben gegen + Akk.
- DAH-NVV-EXP-00141 — Anspruch erheben auf + Akk.
- DAH-NVV-EXP-00143 — einen Anspruch haben auf + Akk.
- DAH-NVV-EXP-00160 — zur Anwendung kommen

These 26 cards are bounded PASS checkpoints and must not be recreated casually.

## App state pinned for this production line

Pinned tested app package: `GFP-v411-DEVELOPMENT-BASELINE-R37.zip`
SHA-256: `fc8c9c82216cb8fe3699bbd293618e91599e24038f9ac1c2b8eaa74589e3cc0b`

Relevant verified behavior on the 26-card cumulative scope:
- 52/52 structural component resolutions
- 52 reverse Wortnetz links
- runtime JS syntax PASS
- runtime asset references PASS
- inline script syntax PASS
- live browser import/persistence/reload: NOT RUN

R37 contains fail-closed component resolution: prefer stable object ID; exact unique lexical fallback only; never guess an ambiguous target.

## Current pipeline state

- source/input capability profile: PASS
- source inventory: PASS
- canonical semantic graph: RUNNING
  - slash variant review: PASS
  - evidence-driven sense resolution: RUNNING
- lexical enrichment/evidence: RUNNING
- examples/semantic annotations: RUNNING
- global QA: RUNNING
- delivery projection: RUNNING
- runtime/presentation acceptance: RUNNING
- release verification: NOT STARTED

Do not claim global completion while only bounded batches are PASS.

## Exact next action

Do NOT continue with 13-card micro-batches as the long-term strategy.

Before Batch 0003, switch to a scalable production cadence:
- normal safe/evidence-backed expressions: 100–200 cards per production batch
- ambiguous/polysemous/conflicting items: quarantine into a review queue and do not block the safe batch
- run validators automatically on each batch and cumulatively
- checkpoint after each successful batch
- update this READ-FIRST file, CHECKPOINT.json, cumulative canonical/projected artifacts, validation/acceptance reports, and downloadable checkpoint ZIP

Next semantic blocker to preserve explicitly:
`etw. / jdn. in Anspruch nehmen` has more than one supported sense and must not be collapsed into one generic meaning.

## Persistence protocol after EVERY successful batch

Required outputs:
1. `CHECKPOINT.json` — machine-readable authoritative status and exact next action.
2. `HANDOFF-READ-FIRST.md` — human-readable session handoff.
3. cumulative canonical JSON — all completed cards, not only latest batch.
4. cumulative projected cards — exact app-facing projection.
5. cumulative validation + acceptance reports.
6. unresolved/review queue — ambiguity must survive across chats.
7. manifest with SHA-256 hashes.
8. one downloadable checkpoint ZIP containing the pinned app package + current Content Kit checkpoint + handoff files.
9. update the Git branch `nvv-production` with the current text artifacts before stopping a session whenever GitHub write access is available.

## Rule for a new chat

The user should be able to say only:

> «NVV را از آخرین checkpoint ادامه بده. branch `nvv-production` را اول بخوان و هیچ PASS قبلی را دوباره نساز.»

The assistant must recover the exact state from GitHub. If GitHub is unavailable, ask for the latest `NVV-Production-Checkpoint-*.zip`; do not reconstruct progress from memory.
