# NVV Auto-Mission Controller

Recommended controller package: `ChatGPT-Auto-Mission-Controller-v3.1.3-SOURCE-SHELF-HARDENING-VERIFIED-CANDIDATE`

Package SHA-256: `b60fd1d63005538ef48a2cde22319cf240be3217385d2227e2f688f33bfc9c49`

Recommended Mission Type: `NVV Long-Run Production — Persistent Batch`

Verification boundary:
- JavaScript syntax PASS
- static protocol invariants PASS
- v3.1 semantic invariants PASS
- synthetic browser harness PASS
- unified NVV bootstrap preset PASS
- source-shelf hardening PASS
- live ChatGPT + Tampermonkey UI NOT RUN

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

Raw-source resolution is explicit in v3.1.3 and must follow this order:
1. explicitly newer/current source supplied by the user in the current chat
2. **ChatGPT Project Sources**
3. **ChatGPT Library**
4. matching current-chat attachment
5. ask the user only if unresolved

Whenever raw bytes are available, verify the registered SHA-256. Same-hash copies in Project Sources and Library are one logical source and must not be processed twice.

This same source-awareness rule is now hardened across the controller's App, generic Content, NVV, Content→App and project-aware Custom paths; historical hardcoded Content Kit version labels are not project authority.

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
