# NVV Auto-Mission Controller — Resilient Long-Run v3.4.0

Status: ACTIVE FOR CLEAN-RESTART LONG-RUN
Workstream: nomen-verb-verbindungen
Authority restart: `NVV-RESTART-20260930-R1`
Mission file: `Workspaces/nomen-verb-verbindungen/NVV-AUTORUN-MASTER-MISSION-v3.md`
Mission key: `NVV-CLEAN-LONGRUN-R3`

## Purpose

This controller exists so Hossein does not have to keep typing “continue” during the long NVV production run. It opens the next ChatGPT turn automatically after a stable nonterminal response, while the newest durable project checkpoint remains the authority.

The controller is only an executor/orchestrator. It does not weaken source fidelity, checkpointing, QA, runtime currentness, or user-decision boundaries.

## Why v3.4.0 supersedes v3.3.1

v3.3.1 fixed the generic-DOM-mutation settlement bug, but it could still enter silent dead-end states when:
- the composer was temporarily unavailable;
- generation was still active exactly when an auto-send was attempted;
- send submission was not confirmed;
- multiple ChatGPT tabs were open;
- the user navigated to another chat;
- the user had typed a manual draft;
- the browser slept/woke or temporarily went offline;
- a transient rate/usage/UI error occurred.

v3.4.0 adds bounded recovery for those cases instead of requiring routine manual “continue”.

## Active behavior

- Smart Start / Resume; existing state is preserved rather than reset.
- Default max automatic turns: 80; configurable up to 250.
- Default watchdog: 420 seconds.
- Automatic continuation after stable assistant response.
- Bounded exponential retry/backoff for temporary composer/send/UI failures.
- Single-tab lease: only one ChatGPT tab may send controller prompts at a time.
- Conversation-route binding: navigation to another chat pauses the mission instead of leaking prompts into the wrong conversation.
- User-draft protection: a non-empty composer is never overwritten.
- Manual-user-message guard: unexpected manual conversation intervention pauses AUTORUN until Resume.
- Focus/online/visibility wake-up hooks for browser sleep/resume.
- Offline/rate-limit/transient UI waiting instead of prompt spam.
- Optional `AUTORUN_STATE_V3_4` machine handoff improves next-operation hints, but does not replace durable CHECKPOINT authority.
- State migration from v3.3.1 and v3.3.0.
- Historical pre-restart Batch0003 / 126-card / Batch0004 state remains quarantine-only.

## Throughput

- atomic shard default: 100 targets;
- may scale to 125/150; hard max 200;
- normal repair/enrichment superbatch: ~500 targets;
- lightweight resumability at shard boundaries;
- portable checkpoint + cumulative QA at meaningful superbatch/stage boundaries;
- no user-visible stop after every shard;
- normal turn exhaustion is followed by automatic next-turn continuation.

## Safety boundaries

AUTORUN stops rather than guessing when:
- a genuine user decision is required;
- destructive approval is required;
- source fidelity cannot be resolved safely;
- Stage6/7 needs a real user-side browser action that cannot truthfully be automated.

It also pauses if it detects:
- a different conversation route;
- a user draft in the composer;
- an unexpected manual user message;
- too many bounded transient/recovery failures.

## Current build

Version: `3.4.0`

Full package:
- `ChatGPT-NVV-AutoMission-v3.4.0-CHROME-READY.zip`
- SHA-256: `d1e57823df909ccfd491666c282ae48785081e6f976a93bf22b1f89533e0beab`

Chrome unpacked-extension package:
- `ChatGPT-NVV-AutoMission-v3.4.0-Chrome-Extension.zip`
- SHA-256: `869729e008520687470b781b7281075e8d15b2fe9de1169b45602e104b06ffcd`

Tampermonkey userscript:
- `ChatGPT-NVV-AutoMission-v3.4.0.user.js`
- SHA-256: `c7e5144b13cd13e9f211a7024992cd9dbd8cab51a4ac8a57cf444b969e55b46b`

Mission source:
- `NVV-AUTORUN-MASTER-MISSION-v3.md`
- SHA-256: `dcbc01770fdb887195f6ff143143faa6f56690510c35e24db7d277feab274804`

Build verification:
- JavaScript syntax: PASS (Tampermonkey + Chrome content script)
- Manifest JSON parse: PASS
- ZIP CRC: PASS (full package + Chrome extension)
- Internal SHA256SUMS: PASS
- static checks for single-tab lease, route binding, user-draft guard, manual-message guard, retry/backoff, platform-limit backoff, checkpoint-first prompt, machine handoff, legacy quarantine and v3.3.1 migration: PASS
- live ChatGPT DOM acceptance: PENDING USER CHROME

Persistence:
- Git mission/controller metadata: SYNCED
- binary package Library sync: PENDING_CONTAINER_SESSION_UNAVAILABLE
- user-delivery package: AVAILABLE IN THE BUILD CHAT
- binary ZIPs are not transported through Git.

## Installation

Preferred: Chrome extension.

1. Disable/remove the older v3.3.1 controller.
2. Extract `ChatGPT-NVV-AutoMission-v3.4.0-Chrome-Extension.zip`.
3. Open `chrome://extensions` → Developer mode → Load unpacked.
4. Select the extracted `chrome-extension` folder.
5. Refresh the NVV ChatGPT conversation.
6. Click **Smart Start / Resume** once.

Do not enable the Tampermonkey and Chrome-extension versions at the same time.
