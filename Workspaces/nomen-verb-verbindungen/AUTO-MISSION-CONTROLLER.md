# NVV Auto-Mission Controller — Clean Long-Run v2

Status: ACTIVE FOR CLEAN RESTART
Workstream: nomen-verb-verbindungen
Authority restart: `NVV-RESTART-20260930-R1`
Mission file: `Workspaces/nomen-verb-verbindungen/NVV-AUTORUN-MASTER-MISSION-v2.md`

## Important

The old preset `NVV Long-Run Production — Persistent Batch` is **DEPRECATED FOR THIS CLEAN-RESTART EPOCH** because it embeds pre-restart Batch0003 / 126-card recovery assumptions.

Do not use that preset for the current NVV run.

Use:
- Mission Type: **Project-aware Custom**
- MODE: `nvv`
- EXECUTION_PROFILE: `continuous_safe`
- TURN_POLICY: `CONTINUOUS_SAFE`
- master mission: exact contents of `NVV-AUTORUN-MASTER-MISSION-v2.md`

The controller is an executor, not project authority. The current workstream checkpoint and portable artifacts remain authority.

## Throughput

This mission is sized for roughly 2.5k source targets.

- atomic shard: 100 targets by default; may scale to 125/150; hard maximum 200;
- production superbatch: about 500 safe targets;
- lightweight resume state after every shard;
- heavyweight portable checkpoint + cumulative audit at each superbatch;
- no visible stop after every 100-card shard;
- continue across stage boundaries in the same turn while safe;
- when a turn ends, auto-open the next turn without asking the user.

This preserves no-loss checkpoints without turning ~2.5k targets into dozens of manual interactions.

## Watchdog

The prior 75-second orphan detector is too aggressive for long reasoning/tool/file operations.

Recommended:
- silent recovery delay: 300 seconds;
- only recover when ChatGPT is no longer visibly generating and no newer durable state/assistant response exists;
- silent recovery attempts: max 3;
- final-delivery recovery attempts: max 3;
- automatic mission turn budget: >= 20.

A watchdog timeout must never inject the historical Batch0003 recovery path.

## Recovery payload

Keep recovery compact. Do not resend the whole master mission.

Required fields only:
- mission_key = NVV-CLEAN-LONGRUN-R2
- restart_id = NVV-RESTART-20260930-R1
- checkpoint_seq
- current_stage
- current_superbatch
- current_shard
- newest_artifact + SHA-256
- next_operation

Recovery always reconciles newest durable authority first.

## Historical quarantine

Pre-restart generated cards/batches/checkpoints are audit-only.

Never:
- recover Batch0003 as working authority;
- restore the old 126-card claim;
- resume old Batch0004;
- block the new run because old Batch0003 bytes are missing.

## Source resolution

1. explicitly newer/current user source in active chat
2. ChatGPT Project Sources
3. ChatGPT Library
4. matching current-chat attachment
5. ask user only if unresolved

Registered source:
- source_id: `deutsch-aber-hallo-nomen-verb-verbindungen`
- PDF pages: 26
- SHA-256: `a817dab76f9e78e896f596bd37b66168f04e995fd68203c045c7d87437ac258d`

Same-hash mirrors are one logical source.

## Runtime

Runtime is resolved only when Stage6 actually requires it.
Always target German-Flashcards-Pro CURRENT; LAST_FULLY_VERIFIED is regression evidence only.

## Current controller build

Version: `3.3.0`

Tampermonkey/full package:
- `ChatGPT-NVV-AutoMission-v3.3.0-CHROME-READY.zip`
- SHA-256: `52dd28226e0d39bfd9a78a6b6fd600c0be6d75e019ed610d2238730ba2498315`
- Library: `/Flasch kart/ChatGPT-NVV-AutoMission-v3.3.0-CHROME-READY.zip`
- Library stable id: `libfile_916a20edeebc8191a511b80f92820416`

Chrome unpacked-extension package:
- `ChatGPT-NVV-AutoMission-v3.3.0-Chrome-Extension.zip`
- SHA-256: `ca95075a18f36cda8b78b9656ec59ffdcdaef5c1ea49a2d57ccdaa54e45f5187`
- Library: `/Flasch kart/ChatGPT-NVV-AutoMission-v3.3.0-Chrome-Extension.zip`
- Library stable id: `libfile_f83be21f42208191849fe9069d834d01`

Build verification:
- JavaScript syntax: PASS (Tampermonkey + Chrome content script)
- manifest JSON parse: PASS
- static long-run invariants: PASS
- live ChatGPT DOM acceptance: PENDING USER CHROME

The 3.3.0 controller is rebuilt for `NVV-CLEAN-LONGRUN-R2`; it does not use the deprecated stage-safe preset as the active execution profile.
