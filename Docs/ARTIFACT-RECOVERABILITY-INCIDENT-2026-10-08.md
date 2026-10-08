# Artifact recoverability incident — 2026-10-08

Status: **OPEN / BINARY RESTORE BLOCKED**. This is diagnostic documentation, not a new authoritative release or a change to CURRENT.

## Confirmed observation

The ChatGPT Library folder `/Flasch kart` contains real artifact entries with file size, filename, IDs and timestamps, including:

- `Menschen-A1-Verben-v3.3.6-FINAL-CONSOLIDATED-CONTENT-PACKAGE.zip` (2,556,294 bytes; catalog file ID `file_000000000d94820a8ef7630c344b36a8`)
- `Menschen-A2-Verben-v3.3.6-FINAL-CONSOLIDATED-CONTENT-PACKAGE.zip` (955,677 bytes; catalog file ID `file_00000000f0e882108eb33da67e588589`)
- `German-Flashcards-Pro-v465-R99-Menschen-B1-Verben-v3.3.6-Kombinationen-Repair1-RELOCKED.zip` (5,170,700 bytes; catalog file ID `file_000000001be88210a6321afaeffd23df`)

The direct `files.materialize(raw_file)` attempt for these entries and B1 sidecar returned: **"This Project file does not have an authorized raw-byte materialization path."** Retrying B1 by stable `libfile_4e9706043cf88191846dba1b0c3713ac` also failed. Exact current-session readback SHA and ZIP CRC are therefore **NOT VERIFIED**. Historical Stage7 claims of prior rematerialization do not establish current access.

The earlier generic search did not show ZIPs, while direct paginated folder listing did. Thus **not searchable** is not **not stored**; **listed** is not **recoverable**. Do not infer deletion from this failure.

## Non-destructive recovery gate (proposed operational addition)

Keep established policies: no ZIPs reconstructed via Git/Base64, no runtime downgrade, no overwriting newer artifacts, no UI changes, workstream authority remains separate. Git holds text metadata/code; large portable binaries do not depend solely on ChatGPT Library.

Before reporting any artifact as `RECOVERABLE_VERIFIED`, require:

1. Exact immutable ZIP and SHA-256/ZIP CRC at creation.
2. Two independently controlled, separate failure-domain copies beyond the active chat session (e.g. external disk + cloud object store), plus optional Library copy.
3. Independent **actual remote download**, SHA-256/CRC reread and a fresh-location restore drill with exact bytes.
4. Record exact name, size, digest, provider/object locator, confirmation timestamp, and evidence for each copy; distinguish `DISCOVERED_METADATA_ONLY`, `LOCAL_READBACK_PASS`, `REMOTE_READBACK_PASS`, `RECOVERABLE_VERIFIED`, `RECOVERY_BLOCKED`.
5. Fail closed when bytes are inaccessible; don't label metadata-only `FINAL_RECOVERABLE`.
6. Keep at least current and two predecessor releases, without deleting unique checkpoints; do not claim indefinite availability without provider/retention checks.

## Resolution status / next action

**OPEN**, pending actual raw-byte restoration of original A1/A2/B1 ZIP files. No historical content is regenerated or silently substituted. An independent local integrity-and-restoration testing kit was produced in chat for validation; that tool alone does **not** establish off-device/cloud storage. The remaining infrastructure step requires an authorized off-ChatGPT binary store (e.g. cloud backup account and/or external disk), ingestion of the exact raw ZIP bytes, and a remote readback recovery drill.

Issue is cross-project; do not mutate source content or current runtime pins as a response to this infrastructure incident.
