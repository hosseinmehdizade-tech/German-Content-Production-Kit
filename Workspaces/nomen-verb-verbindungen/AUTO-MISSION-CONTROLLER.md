# NVV Auto-Mission Controller

Recommended controller package: `ChatGPT-Auto-Mission-Controller-v3.1.2-UNIFIED-PROJECT-BOOTSTRAP-VERIFIED-CANDIDATE`

Recommended Mission Type: `NVV Long-Run Production — Persistent Batch`

## Controller role

Auto-Mission is an optional **executor**, not a second project-state system.

It must consume the same unified authority chain used by normal chats:
1. `German-Content-Production-Kit/main/PROJECT-BOOTSTRAP.md`
2. `German-Content-Production-Kit/main/PROJECT-STATE.json`
3. current README + active START prompt + Source Access Protocol + Source Registry
4. branch/workstream resolved from Project State
5. `Workspaces/nomen-verb-verbindungen/00-source/SOURCE-MANIFEST.json`
6. `Workspaces/nomen-verb-verbindungen/CHECKPOINT.json`
7. cumulative artifacts/review queue referenced by the checkpoint
8. `German-Flashcards-Pro/main/PROJECT-BOOTSTRAP.md` + `PROJECT-STATE.json` only when runtime/import/presentation compatibility matters

Chat memory, old ZIP names and the controller's localStorage are never durable project authority.

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
- B6 Projection / Word Explorer / Wortnetz acceptance against the live-resolved current runtime
- B7 Persistent Git + ZIP checkpoint

## Required persistence after every successful batch
- cumulative canonical JSON
- cumulative projected cards
- persistent review queue
- cumulative QA/acceptance report
- updated `CHECKPOINT.json`
- updated `HANDOFF-READ-FIRST.md`
- SHA-256 manifest
- cumulative standalone checkpoint ZIP when practical
- Git update on branch `nvv-production` when write access is available

If a chat/run ends mid-batch, persist exact B1..B7 counters, last completed record, next record/operation, current review queue and artifact hashes. A resumable checkpoint is the correct outcome; never force false completion because of a run limit.
