# Menschen B1 · 24 lessons — read-only SRS import preflight (26 Oct 2026)

**Status:** SYNTHETIC PRE-FLIGHT TOOLING PASS; **not** approval to import into an existing personal profile.

## Authority
- Exact newest one-ZIP handoff **SHA-256:** `bada18c9ca05b99a5504e9fee7d2db7daf1b7367cc8b0065940c76c3f0fd93bb`
- Filename: `German-Flashcards-Pro-v486-Menschen-B1-24-Lektionen-IMPORT-REPAIRED-AUDIO-COMPANION-NONIMPORT.zip`
- Durable exact Drive backup: [current thirteen-part ZIP](https://drive.google.com/drive/folders/11B72YuLK-fnspVTxPwG9IHdZmK-YZuHy)
- Historical obsolete B1 backups were removed at user request; do **not** fall back to deleted URLs.
- Runtime remains v486-R120 unchanged.

## What has been done
- Added `Tools/B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.mjs`, a pure, no-write Node module for read-only normalized membership/snapshot preflight.
- Added `Tools/B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.TEST.mjs`, a reproducible 16-case synthetic regression suite.
- Executed the pure planner against a full-scale synthetic 24-lesson fixture using a separate JS engine: **16/16 cases PASS**, including 101 unchanged synthetic SRS records, 43 reuse groups, three protected aliases, and 192 reversible example-ID derivations.
- **Neither the user's real SRS nor the newest 213 MB ZIP was executed by this tool.** This run was constrained by container execution failure; therefore no new binary release or live Stage6/7 PASS exists.

## Protected semantics and safety boundaries
- Historical IDs kept distinct for `allumfassend` (L15 2293 vs L19 2839), `trotzdem` (L04 0918 vs L12 1900), `Vorschrift` (L20 2974 vs L23 4049).
- 43 intentionally reused stable-ID groups must preserve **48 additional** course memberships; they are not 43 malformed duplicates.
- 12,548 language triplets arise from 3,137 lesson membership rows; 3,089 IDs are distinct.
- 192 duplicate source example-ID rows in the full 24-lesson fixture are derived only in the new-library dry-run map, with original source IDs and lesson IDs retained. Never overwrite a historical source ID.
- The missing strict `PASS0023` archive for L24 directional `rein` remains a hold.
- If an existing user SRS snapshot is present or is required, this tool **will not apply any merge**. It reports `HOLD_EXISTING_PROFILE_ALL_WRITES_DISABLED`.
- **Do not give untrusted or copied user-profile exports to third parties**; use local, encrypted backups.

## Running locally once a normalized dataset is available
```bash
node Tools/B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.TEST.mjs
node Tools/B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.mjs normalized_memberships.json NEW_LIBRARY_DRY_RUN
node Tools/B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.mjs normalized_memberships.json EXISTING_PROFILE_DRY_RUN protected_profile_snapshot.json
```

`normalized_memberships.json` must contain `{"memberships":[{"id":"mb1m-lu-...","lesson":"B1-L01","lemma":"...","pos":"...","examples":[{"id":"...","de":"...","fa":"...","en":"..."},...exactly four]},...]}`. It is **not** a converter for raw historical 17/23/32-column TSV; normalize from SHA-verified files through the existing v486 import adapters and then run this preflight. Source input is only read. The tool does not import, write files, access IndexedDB, or alter the app UI.

## Remaining real gates
1. Recover access to the exact current portable ZIP in an executable file runtime and produce a normalized **actual** 24-lesson membership snapshot from 24 source-authoritative TSVs.
2. Re-run the checks against the actual normalized dataset and original exact v486 parser; fix any unexpected source layout/IDs without mutating LOCKED sources.
3. Inspect native IndexedDB/backup API contract on exact v486; using an isolated disposable profile, prove full backup, ingest, reload, rollback, audio and course selection.
4. Only after an **independent protected real user SRS backup** and verified no-loss rollback should an existing personal profile be considered. **Never auto-import or auto-alias.**

Git current-pointer for the 213 MB original is unchanged, and this work is stored as an auxiliary QA tooling checkpoint.
