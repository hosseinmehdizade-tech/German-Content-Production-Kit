# File Lifecycle Rule — aspekte-b2-v336

**FILE_LIFECYCLE_RULE_V1_0_0 — ACTIVE.** This workspace MUST use the single global [File Lifecycle & Safe Cleanup Contract](../../Library-Organization/FILE-LIFECYCLE-AND-SAFE-CLEANUP-v1.0.0.md) before writing new content files, at every meaningful milestone and whenever a file is replaced. Read it without waiting for a reminder from the user.

- Put the **owner-scoped** file identity, provider Library ID, SHA-256, lifecycle state, source/recovery dependencies and supersession evidence in the existing `CHECKPOINT.json` or `LATEST.json` when schema-safe, otherwise maintain one `ARTIFACT-REGISTER.json` for this workspace.
- Keep original source, active/recoverable/final/LOCKED files and unresolved HOLDs; proactively identify removable candidates at the next lesson/milestone handoff.
- No deletion from this rule alone. Only delete explicitly user-approved, individually verified Library IDs after backup/dependency checks and post-delete readback.
- This anchor introduces **no** semantic approval, no automatic migration of historical data, no app/UI/SRS/FSRS change, and no release promotion.
