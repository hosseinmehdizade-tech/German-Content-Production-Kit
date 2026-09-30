# NVV AUTORUN MASTER MISSION v2 — CLEAN LONG-RUN

Status: ACTIVE
Scope: standalone Nomen-Verb-Verbindungen production
Framework: German Content Production Kit v3.3.6
Restart authority: NVV-RESTART-20260930-R1
Controller mission key: NVV-CLEAN-LONGRUN-R2

## 1. Final goal

Build the complete standalone NVV dataset from the registered 26-page source under the current v3.3.6 framework, preserve source fidelity, complete enrichment and independent QA, project to the neutral German vocabulary contract, accept against German Flashcards Pro CURRENT when runtime compatibility matters, and produce the final cumulative release.

This is a clean production epoch. Historical generated NVV cards/batches are audit-only and never seed the new run.

## 2. Execution profile

MODE: nvv
EXECUTION_PROFILE: continuous_safe
TURN_POLICY: CONTINUOUS_SAFE
AUTO_CONTINUE_ACROSS_TURNS: true
USER_CONFIRMATION_FOR_ROUTINE_CONTINUATION: false

The user explicitly overrides the default one-major-stage-per-turn stopping rule for this NVV mission.

The override changes only turn orchestration. It does NOT weaken:
- source authority;
- identity closure;
- linguistic QA;
- explicit disposition closure;
- checkpoint integrity;
- runtime currentness;
- no-fabrication rules;
- final verification.

A turn may complete multiple stages and/or multiple production shards while safe. Every completed stage/shard remains separately attributable and resumable.

## 3. Throughput model for ~2.5k source targets

Do not use one user-visible turn per 100 cards.

Use three levels:

### Atomic shard
- default: 100 targets;
- may increase to 125 or 150 after clean evidence;
- never exceed 200 targets in one atomic shard;
- every shard gets lightweight resumable state.

### Production superbatch
- target: 500 safe targets;
- composed of multiple atomic shards;
- a superbatch is the normal durable production milestone;
- run cumulative QA at the superbatch boundary;
- create the portable checkpoint ZIP at the superbatch boundary, not after every 100-card shard unless risk requires it.

### Turn
- continue through as many safe shards/stages as the execution/tool/context budget permits;
- target up to one full 500-target superbatch per long production turn;
- if capacity remains, the next stage/shard may begin;
- stop only at a durable boundary when the real execution window requires it;
- the controller automatically opens the next turn from the newest checkpoint.

Expected Stage3 scale from the historical source-size estimate is about five 500-target superbatches, not dozens of manual user continuations. The fresh Stage1/Stage2 counts remain authoritative once recomputed.

## 4. Authority startup

Before substantial work resolve:
1. German-Content-Production-Kit/main/PROJECT-BOOTSTRAP.md
2. German-Content-Production-Kit/main/PROJECT-STATE.json
3. German-Content-Production-Kit/main/PROJECT-MEMORY.json
4. German-Content-Production-Kit/main/EXECUTION-SAFETY-POLICY.json
5. German-Content-Production-Kit/main/GIT-SYNC-POLICY.json
6. active START-PROMPT from PROJECT-STATE.json
7. Workspaces/nomen-verb-verbindungen/CHECKPOINT.json
8. Workspaces/nomen-verb-verbindungen/00-source/SOURCE-MANIFEST.json

Read German-Flashcards-Pro bootstrap/state only when runtime/import/presentation compatibility matters, and always target CURRENT.

Newest valid portable workstream state outranks older Git metadata. Git remains durability/coordination, not the binary transport or execution blocker.

## 5. Source authority

source_id: deutsch-aber-hallo-nomen-verb-verbindungen
source: Deutsch - Aber Hallo! Nomen-Verb-Verbindungen
pages: 26
SHA-256: a817dab76f9e78e896f596bd37b66168f04e995fd68203c045c7d87437ac258d

Clean restart baseline:
NVV-CLEAN-RESTART-BASELINE-v1.zip
SHA-256:
b207db91e59b69e4380105c4c4a5cd9f03da4af11b27a7124940148eb6c92a44

## 6. Historical quarantine

Everything generated before NVV-RESTART-20260930-R1 is HISTORICAL_ONLY.

Never:
- recover old Batch0003 as production authority;
- resume old Batch0004;
- restore the previous 126-card state;
- seed canonical data from old generated cards;
- block this clean run because old Batch0003 bytes are missing.

Historical counts/artifacts may be consulted only after fresh derivation as regression evidence for omissions or drift.

## 7. Pipeline

Stage 0 — Clean Restart Authority
Current state: PASS.

Stage 1 — Fresh Source Inventory
Recompute the complete inventory directly from the registered PDF.
Preserve source order, noun header, source surface, source subtype/classification, locator/provenance and source-visible variants.
Persist Stage1 checkpoint.
If safe capacity remains, continue directly to Stage2 in the same turn.

Stage 2 — Identity Closure
Close occurrence mapping, duplicate/split/merge decisions, stable target identities and source-to-target mapping before enrichment.
Apply MEM-009: multiple verified meanings of the same lexical target remain one card unless evidence proves a genuinely separate lexical/expression identity.
Persist Stage2 checkpoint.
If safe capacity remains, continue to Stage3A.

Stage 3A — Baseline Richness Audit
Determine applicable dimensions and gap state for every canonical target.
No historical generated content is promoted as authority.
Persist audit state, then continue when safe.

Stage 3B — Gap-Driven Enrichment
Process the corpus in ~500-target superbatches built from atomic shards.
For every completed target, produce the required v3.3.6 semantic content, including learner-comprehensible German definition, Persian meaning, English gloss, structure/Rektion where applicable, provenance/subtype, relations only when evidence-backed, and exactly four original German learner examples with aligned FA and EN translations.

Ambiguous/conflicting targets go to the persistent review queue and must not block safe targets.

After each atomic shard:
- validate shard invariants;
- update lightweight resume state;
- record exact completed IDs/range;
- record review-queue changes;
- record next target.

After each ~500-target superbatch:
- cumulative regression/duplicate/drift/translation/register/example-diversity/relation-integrity audit;
- cumulative canonical update;
- cumulative QA report;
- portable checkpoint ZIP;
- SHA-256 manifest;
- bounded lightweight Git metadata sync.

Then continue automatically to the next superbatch without asking the user.

Stage 3C — Disposition Closure
Every applicable target/dimension must end as VERIFIED_PRESENT, justified CLOSED_NO_FORCE, or policy-permitted NOT_APPLICABLE.
Blank/unresolved is never PASS.
Never fabricate relations to satisfy density.

Stage 4 — Independent Re-Audit
Run independent linguistic/lexical/source-ID/structure/Rektion/relation/provenance/completeness audits.
Minimum 3 full audit rounds where applicable.
Require 2 consecutive clean independent passes on the exact same artifact snapshot.
Any repair resets the clean streak for the affected snapshot.

Stage 5 — Clean Delivery / Anti-Bypass
Project cumulative canonical truth under v3.3.6.
New ordinary vocabulary uses:
- de-vocabulary
- gfp-vocabulary-neutral@1

Semantic POS/morphology/Rektion/subtype never selects layout.
Delivery must be cumulative and preserve stable identities, meanings, four examples, FA/EN alignments, provenance and typed relations.

Stage 6 — CURRENT GFP Runtime / Presentation Acceptance
Resolve German-Flashcards-Pro CURRENT live at Stage6.
Never downgrade to an older LAST_FULLY_VERIFIED runtime.
Verify exact import, persistence/index, roundtrip identity, Word Explorer/Wortnetz navigation, neutral presentation parity and absence of semantic/presentation leakage at the strongest truthful verification level.

Stage 7 — Final Cumulative Release
Produce final organized NVV release/checkpoint, hashes, reports, post-package verification and exact handoff.
Do not claim stronger runtime/browser verification than evidence supports.

## 8. Persistence strategy

Lightweight resume state after every atomic shard.
Portable ZIP at:
- Stage1 PASS;
- Stage2 PASS;
- each ~500-target Stage3 superbatch;
- Stage3 completion;
- Stage4 completion;
- Stage5 completion;
- Stage6 completion/boundary;
- Stage7 final release.

Do not create heavyweight ZIPs for every small shard unless the run is unstable or a turn is about to end.

Git sync:
- compact metadata/source/checkpoint only;
- bounded;
- never Git/Base64 binary transport;
- Git failure becomes PENDING and does not erase valid work.

## 9. Turn and watchdog behavior

A stage boundary is NOT automatically a turn boundary.

Continue in the same turn while:
- authority is clear;
- no user decision is required;
- execution/tool/context budget remains safe;
- durable resume state exists.

When the turn must end:
- persist the newest resume point;
- emit one concise visible summary for everything completed in that turn;
- emit machine state;
- specify exact next_operation;
- controller opens the next turn automatically.

Recommended controller watchdog:
- silent recovery delay: 300 seconds, not 75;
- trigger only when ChatGPT is no longer visibly generating AND no newer durable state/response appeared;
- maximum silent recovery attempts: 3;
- final-delivery recovery attempts: 3;
- automatic mission turn budget: at least 20 turns.

Do not interpret a long tool call or long reasoning interval as failure merely because 75 seconds passed.

## 10. Compact recovery contract

Recovery prompts must NOT paste the entire master mission again.

Recovery needs only:
- mission key;
- restart_id;
- newest checkpoint_seq;
- current stage/shard/superbatch;
- newest artifact/hash;
- exact next_operation.

On recovery:
1. reconcile newest durable state;
2. if work already completed, do not repeat it;
3. if partially complete, resume from exact durable point;
4. if nothing persisted, resume from previous proven checkpoint;
5. never fall back to historical pre-restart NVV production.

## 11. Terminal conditions

AUTORUN_COMPLETE only when Stage7 and completion preflight truthfully pass at the strongest available evidence level.

AUTORUN_NEEDS_USER only for a genuine user decision, destructive approval, source-fidelity conflict, or external action that cannot be safely automated.

AUTORUN_BLOCKED only when safe progress is genuinely impossible after durable recovery.

Execution-window exhaustion is NOT a blocker:
persist state, end the turn, and auto-continue in the next turn.

## 12. Immediate action

Start from the current durable authority:
Stage0 PASS.
Run fresh Stage1 inventory from the authoritative 26-page PDF.
Then continue automatically under CONTINUOUS_SAFE into Stage2 and beyond as capacity permits.
