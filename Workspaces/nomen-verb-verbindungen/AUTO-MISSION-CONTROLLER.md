# NVV Auto-Mission Controller

Recommended controller package: `ChatGPT-Auto-Mission-Controller-v3.1.1-NVV-PERSISTENT-BATCH-VERIFIED-CANDIDATE`

Recommended Mission Type: `NVV Long-Run Production — Persistent Batch`

## Resume authority
Before work in every chat/session, read:
1. `Workspaces/nomen-verb-verbindungen/HANDOFF-READ-FIRST.md`
2. `Workspaces/nomen-verb-verbindungen/CHECKPOINT.json`
3. latest cumulative canonical/projected/QA/review artifacts referenced there
4. current `German-Content-Production-Kit/main` authority
5. current `German-Flashcards-Pro/main` baseline

Chat memory is not authoritative.

## Batch cadence
- Default bounded production batch: 100 safe completed expression cards.
- After two consecutive clean 100-card batches, cadence may increase to 150.
- Do not exceed 200 without explicit user approval.
- Ambiguous/polysemous/conflicting items go to persistent REVIEW-QUEUE and do not block safe cards.
- Every 500 cumulative completed cards, run a global cross-batch audit.

## Per-batch stages
- B1 Sense/Evidence Lock
- B2 DE/FA/EN Meaning
- B3 Lexical Graph / Structure / Relations
- B4 Exactly 4 German Examples + FA/EN translations
- B5 Batch QA + cumulative regression
- B6 Projection / Word Explorer / Wortnetz acceptance at supported evidence depth
- B7 Persistent Git + ZIP checkpoint

## Required persistence after every successful batch
- cumulative canonical JSON
- cumulative projected cards
- persistent review queue
- cumulative QA/acceptance report
- updated `CHECKPOINT.json`
- updated `HANDOFF-READ-FIRST.md`
- SHA-256 manifest
- cumulative standalone checkpoint ZIP
- Git update on branch `nvv-production` when write access is available

If a chat/run ends mid-batch, persist exact B1..B7 counters, last completed record, next record/operation, current review queue and artifact hashes. A resumable checkpoint is the correct outcome; never force false completion because of a run limit.
