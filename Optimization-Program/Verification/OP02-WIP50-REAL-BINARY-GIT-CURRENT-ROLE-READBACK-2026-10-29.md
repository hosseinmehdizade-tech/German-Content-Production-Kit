# OP-02 — Actual WIP50 binary, native Git receipt ancestry, and exact CURRENT role (2026-10-29)

**Result: `PASS_SCOPED_REAL_WIP50_BINARY_ROLE_AND_GIT_ANCESTRY_READBACK`**, not a new release or Stage4 linguistic PASS. This is actual read-only local materialized artifact inspection plus live GitHub content/commit API verification. No data or metadata rewritten.

## 1. Current WIP50 materialized artifacts independently recalculated from bytes

| Actual local WIP50 master/portable role | Size | Calculated SHA-256 | Agrees with WIP50 receipt AND current master role |
| --- | ---: | --- | --- |
| `Aber-Hallo-WIP50-CANONICAL-MASTER.json` | 7,076,256 | `fe50217d519edbb1c4d5eb5fc4da36faf1f562e859ccfe58b0153dbf684c48aa` | YES |
| `Aber-Hallo-WIP50-IMPORT.tsv` | 12,951,743 | `d640179d3fdfa2ecff0681b707519bc6d10ff687aba22482a7e8694aba374a8a` | YES |
| `Aber-Hallo-WIP50-23-DUDEN-GENITIV-ADJECTIVE-552-ATTESTED-432-OPEN-2026-10-29.zip` | 7,297,862 | `a558055dbddda45d5d3040fb096bf28eb8f51e2c0863f5634c445094decfc96b` | YES |

Both ZIP members `02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json` and `01-Final-Import/IMPORT.WORKING.tsv` are **byte-for-byte identical** to the separately materialized current WIP50 master Canonical and Import. ZIP has **362** members; all **361** `SHA256SUMS` records match member bytes, no missing checksum entry (excluding the `SHA256SUMS` file itself), no CRC error. The internal two original PDFs also exactly match the user-uploaded original local files:

- A1-A2 PDF SHA256 `4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3`;
- B1-C2 PDF SHA256 `ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04`.

Original content was not changed. The native Canonical has **788** units: 647 `verb` + 140 `adjektiv` + 1 `grammatische_struktur`. All **787** lexical unit IDs match **787** import TSV IDs in exact order and without duplicates; the grammar unit `ahl-lu-0001` is correctly present only in Canonical.

## 2. Live GitHub readback of CURRENT Git role and lineage

- Native `Workspaces/aber-hallo-listen-tabellen/LATEST.json` exact Git blob `f490ba8debb7277f07e1e0accce94364229fb2e9` matches the blob at promotion commit `1f94eac9e4038bdfa30a1a343edcab402997288a`. The original WIP50 receipt file exact blob `e3e745a479a12467ecb4028d73711781212e7b1c` matches the blob at receipt commit `7194527f8dde7b627be6fda469a9504e80b78bbe`.
- The commit `1f94eac9...` changing `LATEST.json` has **exactly** `7194527f...` as its direct parent; `7194527f...` adds the referenced WIP50 receipt. Both are ancestors of present `main` (GitHub compare returned `ahead`, behind_by 0 for both).
- **Actual binary authority:**
  - Zip role: `LATEST.authority.current_portable`.
  - Current canonical/import master roles: `LATEST.wip50_master_files.canonical/import`, consistent with `LATEST.authority.current_portable.canonical_sha256/import_sha256` and WIP50 receipt `artifacts.canonical/import`.
  - **Do not use `LATEST.authority.canonical` to resolve current WIP50.** That is a preserved historical `CANONICAL-ENRICHED.WORKING.json` with SHA `3abbd4984e5cdb69551230c2fb6c1373e559b78e2a5f132eb3f53fb9aa8d180d`, not the WIP50 master SHA `fe50217d...`. Selecting by old key instead of explicit current master role silently downgrades the input.
- Existing `Verification/audit_aber_hallo_current_identity.py` already checks the correct current_portable/master/receipt mapping; **no duplicate ruleset or new synthetic-only guard needed**.

## 3. Actual trust boundary (must not overstate)

**The user-uploaded/mounted materialized files were rehashed and compared to current Git metadata. This turn did not freshly download the same three binaries from Google Drive.** Prior Drive readback appears as scoped evidence in WIP50's native receipt. Equal hashes, Git commit ancestry and an unchanged LATEST do **not** authenticate the issuer or grant authority to advance CURRENT. GitHub REST reported **both** receipt `7194527f...` and promotion `1f94eac9...` as `verification.verified=false`, `reason=unsigned`. The Content Kit `main` remains unprotected; no branch policy change here.

Current Stage4 still lacks a full independent-method linguistic review of **788** units and 604 stale worksheet unit snapshots remain with **zero** completed decisions. The remaining case-sense queue is **432** (338 old holds plus 94 external-to-original-ledger). Stage5–7 are not authorized. No WIP50 content, LOCKED, sources, PDF, Library, app/runtime/UI or `LATEST.json` mutation; OP01 `WRITER-SCOPES` remains `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL` and `scopes=[]`.

## 4. Resulting actionable rule for future OP-01/02 work

**Resolve newest explicit artifact first**, then `LATEST.wip50_master_files` + `LATEST.authority.current_portable` + exact `latest_receipt_path` and committed receipt, and recompute actual local/remote bytes. Reject any consumer that attempts to infer CURRENT WIP50 from the historical `LATEST.authority.canonical` field. The independent issuer/protected-policy/root decision is a separate security approval gate; do not treat this scoped SHA match as that decision.

Checked against WIP50 materialized binary files mounted locally 2026-10-29, and GitHub API `GET /commits/{sha}`, `GET /compare/{sha}...main`, plus Git file readbacks at both promotion/receipt commit and current main. No actual semantic edits performed.
