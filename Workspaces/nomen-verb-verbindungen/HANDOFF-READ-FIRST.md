# NVV — FINAL LOCKED HANDOFF / READ FIRST

Updated: 2026-10-07  
Workstream: `nomen-verb-verbindungen`  
Branch: `nvv-production`  
Framework: **v3.3.6**  
State: **STAGE7_EXACT_FINAL_CONTENT_LOCKED**

## Authority

Global project authority lives on `main`:
- `PROJECT-BOOTSTRAP.md`
- `PROJECT-STATE.json`
- `Prompt/START-PROMPT-v3.3.6.md`
- `FLASHCARDS-RUNTIME-DEPENDENCY.json`

NVV workstream authority:
- `Workspaces/nomen-verb-verbindungen/CHECKPOINT.json`
- `Workspaces/nomen-verb-verbindungen/00-source/SOURCE-MANIFEST.json`
- `Workspaces/nomen-verb-verbindungen/07-release/STAGE7.json`
- `Workspaces/nomen-verb-verbindungen/07-release/STAGE7-POST-PACKAGE-VERIFICATION.json`
- `Workspaces/nomen-verb-verbindungen/07-release/FINAL-INDEPENDENT-AUDIT.json`

Do **not** resume from historical Batch0001/0002/0003, N0 recovery, v3.1.12, or old runtime notes. Those are historical only.

## Final locked release

`German-Flashcards-Pro-v465-R99-Nomen-Verb-Verbindungen-v3.3.6-LOCKED-CONTENT.zip`

SHA-256:  
`917ba9561245deea32cc3be1095af0185858d3d45d8eb7ff40e4a7b4c361771f`

Library path:  
`/German-Content-Production-Kit/Checkpoints/German-Flashcards-Pro-v465-R99-Nomen-Verb-Verbindungen-v3.3.6-LOCKED-CONTENT.zip`

Library stable ID:  
`libfile_c309354fb5c08191a604296de78a5f2d`

Library rematerialization: **PASS_EXACT_SHA256_AND_BYTE_COMPARE**

## Final content state

- source authority: registered 26-page user-supplied PDF
- source SHA-256: `a817dab76f9e78e896f596bd37b66168f04e995fd68203c045c7d87437ac258d`
- source occurrences: **2476**
- active cards: **2492**
- examples: **9968**
- unresolved completeness cells: **0**
- Stage4: **PASS / CLOSED**
- Stage5: **PASS / CLEAN DELIVERY**
- Stage6: **PASS_AUTOMATED_EXACT_CURRENT_WITH_ENVIRONMENT_BOUNDARY**
- Stage7: **PASS_EXACT_FINAL_CONTENT_LOCKED_WITH_PROJECT_RUNTIME_BOUNDARY**
- content lock: **LOCKED**

Learner content is immutable at this point. Any future content change requires a new successor release; do not mutate this locked artifact in place.

## Runtime boundary

Stage6/7 integration target: **German Flashcards Pro v465-R99**  
Exact runtime artifact SHA-256:  
`8b4921ebb7b1189e93336e3b0497aa3c1f05945abd130cb15e1b1fa3ceb08b17`

Content-specific runtime acceptance is complete:
- 2492/2492 import + persistence PASS
- 2492/2492 runtime index PASS
- exhaustive presentation/roundtrip PASS
- final package direct import/restart PASS
- runtime base preservation 339/339 exact

Separate app-level boundary remains:
`PENDING_USER_SAME_PROFILE_V465`

That boundary belongs to the global app runtime, not to NVV content. Do not reopen NVV because of it.

## Exact resume rule

For NVV content/package work, there is **no next production action**. Preserve the exact locked release SHA.

Only if the user explicitly requests a successor, content correction, source change, or re-integration against a newer CURRENT runtime should a new NVV work item begin.

If runtime compatibility is revisited, resolve CURRENT from German-Flashcards-Pro live at that time. Never downgrade to an older LAST_FULLY_VERIFIED runtime merely because it is final.

## Durable Git state

Stage7 lock workstream commit:
`6e3fa962dfcfbbd79607e49539d358b004c5f19c`

Main project-state sync commit:
`535eff71e26498b98873741d35bb687df025f4a1`

Runtime dependency sync commit:
`addda19ea029188ab58f57c0365421cd79dac92a`

