# Aspekte B2 · L01 · Read-only SRS Identity Preflight

**Status:** Implemented and synthetic-tested; **not** verified against the user's live browser profile. `BLOCKED_NONIMPORT` remains mandatory. Scope: exactly seven L01 cross-level identity cases. Date: 2026-11-08.

This helper consumes **local files only** and never accesses, writes, merges or imports live SRS / IndexedDB / localStorage. It does not contact GitHub or any server. Never upload a user's raw forensic archive to GitHub or Library. The helper reports **presence of IDs in an input file**, never live acceptance. A user-supplied JSON claiming `kind: live` does **not** prove runtime authenticity.

## Inputs

- Authoritative curated Library Current: `L01-CURRENT-158-UNIT-REVIEW-R47-NONIMPORT.csv` (158 cards, SHA-256 `72bddff2d900322b8fb3b3b7094d59281636c5bc6be390aae46d74d35ed32716`).
- Existing immutable seven-case matrix: `Workspaces/aspekte-b2-v336/Reports/B2-L01-CROSSLEVEL-7-CASE-IDENTITY-MATRIX-20261108.csv`.
- **Optional** user-owned/exported JSON: either `{"cards":[{"id":"...", ...}]}`, `{"cards":{"id":{...}}}`, `{"store":{"cards":...}}`, or a v471 forensic wrapper `{"payload":{"localStorage": [["gfp_progress_v8", "..."]], "databases": [...]}}`. The forensic wrapper is **historical**/recovery evidence; only the legacy localStorage cache is examined. IndexedDB stores are intentionally **not** interpreted without an active-generation proof. Other JSON structures fail closed; the script does not guess nested card IDs.

## Run locally (Python 3.10+)

```
python b2_identity_readonly_preflight.py \
  --matrix B2-L01-CROSSLEVEL-7-CASE-IDENTITY-MATRIX-20261108.csv \
  --l01-current L01-CURRENT-158-UNIT-REVIEW-R47-NONIMPORT.csv \
  --expected-l01-sha256 72bddff2d900322b8fb3b3b7094d59281636c5bc6be390aae46d74d35ed32716 \
  --out-dir local-output
```

To inspect a **local** JSON file, add `--evidence-json /path/to/private-export.json` (do not share the raw export). Reports are written **only** under `--out-dir` and contain no raw reviews, due dates, browser URLs or card text. Input files are not modified. Return code **2** means a safe, successful **non-importable** preflight; return code **3** means an invalid or unsupported input. Neither means permission to import.

## Self-contained tests

```
python -m unittest discover -s . -p 'test_b2_identity_readonly.py' -v
```

12 deterministic, synthetic tests cover successful read-only behavior, wrong checksum, tampered seven-case matrix, source safety gate, unknown archive, malformed JSON, duplicate candidate IDs, forensic legacy caveat, privacy scrubbing, deliberate nonzero release block and nonmutation. The actual L01 SHA+matrix integration was also run locally without user SRS evidence.

## Remaining release gates

1. Independent German–Persian meaning, grammar, example and collocation quality signoff.
2. Real read-only **active** installed-app generation + accepted B1/A2 IDs + SRS identity evidence. GitHub or historical archive alone is **not** proof.
3. Isolated native import/persistence/rollback test before any change to real SRS.

**Do not** equate a user statement about prior imports, an archived ID, a source vocabulary match, or an on-disk progress-cache entry with native active-card identity.
