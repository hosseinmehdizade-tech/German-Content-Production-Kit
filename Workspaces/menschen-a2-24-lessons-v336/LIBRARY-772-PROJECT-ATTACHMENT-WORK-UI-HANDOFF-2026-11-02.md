# Menschen A2 — 772 Project-linked root attachments: Work UI handoff (2026-11-02)

Status: **UNMOVED — BLOCKED IN CONNECTOR**. The `files.manage_library` action returned `project_library_mutation_unsupported`. This document is an operational UI test/runbook, **not** evidence of moved files.

## Inventory authorities
- Root A2-prefix (256): `LIBRARY-ROOT-ATTACHMENT-BLOCKED-A2-PREFIX-2026-11-02.json`
- Root Menschen-A2-prefix (516): `LIBRARY-ROOT-ATTACHMENT-BLOCKED-MENSCHEN-A2-PREFIX-2026-11-02.json`
- Destination (698 existing): `LIBRARY-FOLDER-RELOCATION-INDEX-2026-11-02.json`
- Collisions and detailed analysis: `LIBRARY-ROOT-RELOCATION-COLLISION-AUDIT-2026-11-02.json`
All paths are relative to this file's GitHub directory and must be fetched at runtime, never assumed stale.

## Target
`/Flasch kart/German-Content-Production-Kit/Content/Menschen-A2/`
- A2-prefix group -> `Checkpoints/`
- Menschen-A2-prefix group -> `Imported-Legacy/`
- Do not mix with `Menschen-A2-Verben`; mixed A1/A2/B1 source remains in Reference Library.

## Supported-capability pilot: ONE FILE ONLY
1. Open ChatGPT Library (or Space if it replaces Library), browse `/Flasch kart` and locate:
   `A2-L09-STAGE6-POST-PACKAGE-VERIFICATION.json`
   root Library ID `libfile_925a9734ff908191a78f111290e10dce`, original size 550 bytes.
   This exact basename is **not present** among the 698 indexed target records (snapshot 2026-11-02).
2. Check whether this **Project-linked** file exposes a genuine **Move / Verschieben** command that preserves the source file's identity and Project references. Do not mistake a **chat** `Move to project` command for a **file move**.
3. If available and eligible, move to `.../Menschen-A2/Checkpoints/` **without overwrite, duplicate upload, delete, or reattach**. Re-read exact Library ID, new path and reference visibility. Record the result.
4. If Move is absent, refuses the operation, or returns `project_library_mutation_unsupported`, **STOP**. Do not attempt another file or workaround. State that the UI does not offer an authorized move capability.

## Only after a real and verified pilot pass
- Re-fetch both root inventories and current destination.
- Process only exact, still-present files; skip already migrated IDs.
- Group by collision: 478 names absent at destination; 291 names/sizes match but content hashes unverified; 3 filename-size conflicts.
- Migrate the 478 no-name-collision records in small verifiable batches, with pre-/post-path and library ID checks. Never silently overwrite a target.
- On 291 same-name same-size entries, require exact bytes/SHA-256 on both sides before treating as copies; otherwise preserve both versions separately. Zero deletions by default.
- The 3 name-size conflicts require manual review; A2-L15 root JSON includes two extra metadata sections `library` and `roundtrip_sidecar`; preserve both.
- Never claim all 772 migrated until post-audit verifies original records and destination with stable IDs.
- No source content, app runtime, lesson LOCK, or user SRS changes as part of organization.

## Verified 2026-11-02 preflight snapshot
- 698 files in dedicated folder.
- 772 disjoint project-linked root records, 1,905,775,262 bytes total.
- 478 no-name-collision; 291 same-name/same-size **not proven byte-identical**; 3 filename/size conflicts.
- 0 files moved by connector in prior attempts.
- Personal Library move API not authorized for these Project-linked files.

## Work mode instruction for new session
"Use the Cloud Browser to inspect the actual ChatGPT Library interface for a supported move operation on the single explicitly named pilot file above. If and only if it is supported, move that exact file into the specified Menschen A2/Checkpoints destination and verify the unchanged stable Library ID and Project attachment visibility. Never copy, delete, reupload, overwrite, or detach any file. Then report what happened. Read this GitHub handoff and the referenced inventories, and do not start bulk migration until the pilot is verified."

This handoff does not grant permissions. Cloud Browser support for signed-in sites does not establish that the ChatGPT Library allows Project-linked attachment relocation.
