# NVV AUTORUN MASTER MISSION v3 — RESILIENT CONTINUOUS RUN

Status: ACTIVE
Scope: standalone Nomen-Verb-Verbindungen production
Framework: German Content Production Kit v3.3.6
Restart authority: NVV-RESTART-20260930-R1
Controller mission key: NVV-CLEAN-LONGRUN-R3

## 1. Goal

Finish the complete standalone NVV dataset from the registered 26-page source under the current v3.3.6 framework, preserve source fidelity, complete repair/enrichment/independent QA, project to the neutral German vocabulary contract, accept against German Flashcards Pro CURRENT when runtime compatibility matters, and produce the final cumulative release.

This is the clean production epoch. Anything generated before NVV-RESTART-20260930-R1 is audit/history only and must never become working seed authority.

## 2. Authority-first resume rule

At the beginning of every controller turn, resolve the newest durable authority before deciding what to do. The live `Workspaces/nomen-verb-verbindungen/CHECKPOINT.json` and newer valid portable workstream artifacts override any older fixed action written in prompts, handoffs, chat history, controller state, or this mission document.

Required authority chain:
1. German-Content-Production-Kit/main/PROJECT-BOOTSTRAP.md
2. German-Content-Production-Kit/main/PROJECT-STATE.json
3. German-Content-Production-Kit/main/PROJECT-MEMORY.json
4. German-Content-Production-Kit/main/EXECUTION-SAFETY-POLICY.json
5. German-Content-Production-Kit/main/GIT-SYNC-POLICY.json
6. active START-PROMPT resolved from PROJECT-STATE
7. Workspaces/nomen-verb-verbindungen/CHECKPOINT.json on nvv-production
8. Workspaces/nomen-verb-verbindungen/00-source/SOURCE-MANIFEST.json
9. newest valid portable checkpoint/artifact if newer than Git metadata

Never restart Stage1 merely because an old prompt says so. Never redo a durable PASS milestone unless a real upstream invalidation requires it.

## 3. Execution profile

MODE: nvv
EXECUTION_PROFILE: continuous_safe
TURN_POLICY: CONTINUOUS_SAFE
AUTO_CONTINUE_ACROSS_TURNS: true
ROUTINE_USER_CONFIRMATION: false

Hossein explicitly approved a scoped NVV long-run override. Normal safe continuation must not require him to type “continue”. The override changes orchestration only; it does not weaken source fidelity, identity closure, no-fabrication rules, independent QA, checkpoint integrity, runtime currentness, or final verification.

## 4. Throughput

- atomic shard default: 100 targets
- may scale to 125/150 after clean evidence
- hard maximum: 200 targets
- repair/enrichment superbatch target: about 500 targets
- lightweight resume metadata after each atomic shard
- cumulative QA + portable checkpoint at meaningful superbatch/stage boundaries
- continue automatically into the next safe shard/superbatch/turn without asking the user

If a turn must end because of tool/context/execution limits, persist the exact resume point, send a concise visible handoff, and let the controller open the next turn. Turn exhaustion is not a blocker.

## 5. Source authority

source_id: deutsch-aber-hallo-nomen-verb-verbindungen
source: Deutsch - Aber Hallo! Nomen-Verb-Verbindungen
pages: 26
SHA-256: a817dab76f9e78e896f596bd37b66168f04e995fd68203c045c7d87437ac258d

Same-hash Project/Library/current-chat copies are one logical source. Different bytes with the same title require explicit resolution.

## 6. Historical quarantine

Never recover as production authority:
- pre-restart Batch0003
- old 126-card claim
- old Batch0004
- old generated card sets or mappings

Historical material may be consulted only after fresh derivation and only as regression evidence for omissions/drift.

## 7. Pipeline

Stage 0 — Clean Restart Authority
Stage 1 — Source & Inventory
Stage 2 — Identity Closure / Canonicalization
Stage 3A — Baseline Richness Audit
Stage 3B — Gap-Driven Enrichment
Stage 3C — 100% Disposition Closure
Stage 4 — Independent Linguistic/Lexical QA + repair successor
Stage 5 — Clean Delivery / Anti-Bypass
Stage 6 — CURRENT GFP Runtime / Presentation Acceptance
Stage 7 — Final Release / Post-Package Verification

The live checkpoint determines which stage is current.

### Stage 4 repair rule

When Stage4 finds systemic example-layer defects, regenerate the affected example layer in bounded repair superbatches rather than patching isolated examples opportunistically. Preserve definitions/meanings/glosses unless a separate semantic finding proves them defective. Four German learner examples per active target must be natural, target-bearing, non-meta, structurally correct and meaning-aligned; each gets aligned Persian and English translations.

Any separate structure/Rektion repair delta is applied only to the intended successor snapshot and must preserve source occurrences/provenance. After repair, recompute affected Stage3C disposition evidence and restart Stage4 clean-streak auditing on the exact repaired snapshot.

Stage4 requires at least 3 independent rounds where applicable and at least 2 consecutive clean passes on the same artifact snapshot. Any repair resets the clean streak for the affected snapshot.

## 8. Stage 5–7 rules

Stage5: ordinary vocabulary uses `de-vocabulary` + `gfp-vocabulary-neutral@1`; semantic POS/morphology/Rektion/subtype must never select layout.

Stage6: resolve German-Flashcards-Pro CURRENT live. LAST_FULLY_VERIFIED is regression evidence only. Verify exact import, persistence/index, roundtrip identity, Word Explorer/Wortnetz behavior, neutral presentation parity and absence of presentation leakage.

Stage7: produce organized final NVV release/checkpoint, direct import TSV, canonical JSON, QA/coverage reports, runtime/presentation evidence, manifest/hash evidence and post-package verification. Claim only the verification level actually proven.

## 9. Machine handoff contract

Every nonterminal controller-driven turn should end, when practical, with a compact machine block after the human summary:

AUTORUN_STATE_V3_4
{"mission_key":"NVV-CLEAN-LONGRUN-R3","restart_id":"NVV-RESTART-20260930-R1","checkpoint_seq":"<best durable id>","stage":"<current stage>","superbatch":"<id or null>","shard":"<id or null>","artifact":"<filename or null>","sha256":"<sha256 or null>","next_operation":"<exact next operation>","terminal":"CONTINUE"}

Do not invent values; use null when unknown. This is only a controller hint. Durable checkpoint/artifact state remains authority.

Reserved terminal last lines:
- AUTORUN_COMPLETE
- AUTORUN_NEEDS_USER
- AUTORUN_BLOCKED

Use NEEDS_USER only for a real user decision/destructive approval/source-fidelity conflict that cannot be resolved from authority. Use BLOCKED only when safe progress is genuinely impossible after durable recovery. Routine continuation, Git lag, tool-budget exhaustion and normal turn boundaries are not terminal blockers.

## 10. Recovery

On missing/interrupted visible response:
1. reconcile newest durable checkpoint/artifact first;
2. if work completed, do not redo it—reconstruct only the missing handoff and continue;
3. if partially persisted, resume from the exact durable point;
4. if nothing new persisted, resume from the previous proven checkpoint;
5. never fall back to pre-restart production;
6. use bounded retry/backoff, never prompt-spam.

## 11. Runtime/browser boundaries

The controller automates conversation continuation only. It must not weaken browser/runtime evidence requirements. If Stage6/7 needs a real user-side Chrome action that cannot truthfully be automated, persist exact state and use AUTORUN_NEEDS_USER with the minimum concrete action required.

## 12. Immediate action

Resolve the newest durable NVV checkpoint and execute its exact `next` / `next_action`. Do not use a fixed historical stage as the starting point. At the time v3.4.0 was built the recorded next action was Stage4 example-repair Superbatch R1, but this sentence is informational only and must never override a newer checkpoint.
