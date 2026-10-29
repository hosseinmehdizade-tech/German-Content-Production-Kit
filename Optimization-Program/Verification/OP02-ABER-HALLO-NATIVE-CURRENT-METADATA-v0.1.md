# OP-02: Aber Hallo native CURRENT metadata adapter (NONACTIVE v0.1)

This is a **read-only**, single-workstream bridge, not a policy or content
migration. Source of truth at inspection time:

- `Workspaces/aber-hallo-listen-tabellen/LATEST.json`
- `LATEST.latest_receipt_path`, currently WIP50 and scoped `IN_PROGRESS`
- `Workspaces/aber-hallo-listen-tabellen/00-source/SOURCE-MANIFEST.json`

The new `Verification/audit_aber_hallo_current_identity.py` compares the
real native LATEST `authority.current_portable` ZIP/current Canonical/Import
hashes and Drive identities to its latest receipt `artifacts`, and the two
current master-file entries, ensuring a stale receipt, wrong source manifest,
altered TSV SHA, mismatched Drive identity or forged global Stage4 PASS
fails closed. Existing `Prompt/ACTIVE-PROMPT.txt` selects v3.3.6; no content
authority is moved to historical 3.1.11.

**Semantics:** a positive result is
`PASS_SCOPED_NATIVE_METADATA_CONSISTENCY_ONLY`.
It means the tracked metadata fields agree at the checked snapshot.
It DOES NOT prove that the named latest pointer is the authorized newest
CURRENT (that needs independently pinned Git commit/issuer), that actual PDF
or Drive binary bytes match, that Stage4 independent semantic review is
complete, or that a Stage5 clean 4-role package exists. Even when metadata
passes, `production_stage5_allowed = false`, no writer grant or rollback
is performed. WIP50 still reports 432 unresolved Rektion cases and
Stage4 OPEN / Stage5-7 NOT_RUN; this adapter does not resolve them.

The synthetic mutation tests plus a real tracked-metadata read-only test
run on the unchanged content in CI. If WIP50 pointer changes in another
content stream, this WIP50-only adapter should BLOCK rather than silently
claim a newer final release.

**Separate CI maintenance:** the legacy content-quality v3.1.11 workflow
used to insist the active README contains `START-PROMPT-v3.1.11.md`.
That contradicts the real active v3.3.6 pointer. Update only the assertion,
without editing README, v3.1.11 historical prompts or active governance.
