# v343 Recovery-Blocked Import Regression Case

## Trigger that exposed the v3.1.3 prompt flaw

A 30-row Universal-v2 TSV was recognized by Flashcards Pro v343 (`universal-v2 · 30`), but the live browser import did not commit. The UI reported that the transactional import was not verified, the previous library was restored unchanged, and database recovery was not complete.

## Relevant v343 runtime behavior inspected

The supplied v343 source contains independent persistence state concepts including:

- `STORAGE_RUNTIME_MODE` with `READY`, `RECOVERING`, `DEGRADED_READ_ONLY`, `FATAL`.
- `STORAGE_WRITES_BLOCKED` and `STORAGE_WRITE_BLOCK_REASON`.
- durability writer authority / `canWrite()` gate before import.
- transactional import capture + `saveStoreConfirmed(...)` + verified persistence.
- rollback to the pre-import runtime snapshot when persistence verification fails.
- explicit recovery confirmation / official transition back to `READY`.

This proves that **TSV parse compatibility and current-session write readiness are different facts**.

## Regression requirement added in v3.1.4

The Master Prompt must never derive a current-browser “import now” claim from an isolated parser/roundtrip PASS. It must:

1. establish Artifact compatibility separately;
2. test an existing non-empty library in the isolated compatibility matrix;
3. prove write-blocked/recovery states fail closed without mutating the previous library;
4. require live preflight for the actual browser before recommending import;
5. require transactional commit + reload/reopen before declaring actual import success.

`IMPORT_READY` is therefore deprecated. The replacement statuses are `APP_COMPATIBLE`, `CURRENT_RUNTIME_NOT_VERIFIED`, `RUNTIME_PREFLIGHT_PASS`, `RUNTIME_BLOCKED`, and `IMPORT_VERIFIED`.
