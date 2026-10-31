# OP-02: WIP73 compact original ZIP to exact WIP72 full-source parent chain

**Date:** 2026-10-31. **Classification:** read-only byte-provenance and recovery-scope QA, not authorization. No edits to original source, original WIP72/73 ZIPs, learner cards, LATEST, LOCKED, app runtime/UI, writer scopes or GitHub permissions.

## Actual evidence from Library originals

The current Git `Workspaces/aber-hallo-listen-tabellen/LATEST.json` (readback blob `3c257adee7adfd8f09e13bf4cd881e413d57dcab`) identifies:
- **WIP73_SIX_EXACT_REKTION**, 935 attested of 981 patterns, 46 holds.
- **Compact WIP73** `Aber-Hallo-WIP73-COMPACT-6-EXACT-935-ATTESTED-46-HOLDS-2026-10-31.zip`, Library ID `libfile_cbe0500bf2f4819198fa26e30a15b2f1`, 1,892,783 bytes, raw SHA256 `6b0f29e98e3648b3f0a29921fbc9e7a73322ad83ea009fca16becb74774899a7`.
- **Parent full WIP72** `Aber-Hallo-WIP72-12-EXACT-REKTION-929-ATTESTED-52-HOLDS-2026-10-30.zip`, 8,056,905 bytes, raw SHA256 `b41b2a814eed37d87f01f90937ab21ee2976e9f059007c2f091b5d743e4ac225`.

Both raw files were independently materialized from Library. The WIP73 ZIP has **13 members**, all CRC-valid, with **12/12** exact `SHA256SUMS` entries and **11/11** exact MANIFEST file members with matching SHA256/size. It contains **no original PDF byte files**: instead it carries exact parent source references. The independently read WIP72 parent contains two actual original PDFs (A1-A2, B1-C2) whose raw byte SHA256 values match the separately registered manifest:
`4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3` and
`ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04`.

WIP73 contains a new canonical JSON (788 learning units) and import TSV (787 lexical card rows, 23 columns). The canonical learning-unit IDs and TSV stable card-ID order are identical to WIP72. **Exactly six** canonical units differ; **exactly six** TSV card rows differ, and only column 20 (0-based index 19) in those six rows. No card IDs were added or removed. The 46 unresolved patterns are explicitly carried forward; the reported 935 attested is not a full semantic Stage4 PASS.

This **does not retroactively make WIP72 full parent a FINAL**. The original WIP72 still has the previously verified active pointer working_* and WORKING-STATE stale metadata and Stage4 OPEN. WIP73 is a **COMPACT_NOT_FINAL recovery/current working snapshot**, not the single complete final release ZIP.

## Nonactive fail-closed contract

New `Verification/audit_op02_compact_parent_chain.py` accepts independent exact SHA256/identity/count snapshot, actual compact ZIP path and actual full-parent ZIP path. It verifies:
- outer raw SHA and bounded safe member read of **both original ZIPs**, rejecting absent or substituted parents;
- all compact SHA256SUMS member bytes and exact MANIFEST coverage/digests;
- checkpoint, QA, manifest and source-provenance parent SHA and file-name references;
- actual raw PDF bytes inside the **parent** against independently provided SHA256 pins, not only the compact's own claims;
- actual canonical/TSV SHA256 against external pins and in-archive declarations;
- exact stable IDs/order, 788-unit canonical integrity and six-item difference bounds;
- 52 prior holds, six exact attestation deltas, 935 cumulative attested, 46 remaining holds, and explicit Stage4 OPEN / Stage5–7 NOT_RUN declarations.

If any checks fail, `status=BLOCKED`. If everything matches, `status=PASS_SCOPED_COMPACT_PARENT_RECOVERY_NOT_FINAL`; it **always** reports issuer authenticated=false, writer granted=false, Stage4/5–7 accepted=false, no writes. The scope and known WIP73 schema are explicit; future compact schema revisions require independently reviewed changes. No trust root is created by an externally supplied SHA alone.

The `test_op02_compact_parent_chain.py` synthetic negative cases include parent substitution/missing, stale source hash declarations, wrong independent pins, same-name reassignment, seven changed rows instead of six, stale or malformed compact checksum/metadata, false Stage4/Stage5 status, progress drift and duplicate JSON keys. Ubuntu and Windows CI is **nonrequired**, not an issuer.

## Existing guard boundary

The prior shared `guarded_zip()` and final Library preflight identify a compact Aber Hallo archive as lacking the full active pointer/WORKING-STATE roles; thus the repository's known FINAL paths must not accept WIP73 as a complete final archive. Recovery-purpose code paths may preserve the original compact without mislabeling Stage4 or FULL. These controls remain **bypassable** by direct external GitHub/Library upload APIs that don't call them.

**Next security decision:** user-approved protected public Content Kit main and an independently protected issuer/check-origin enforcement. Existing security decision pack:
`Optimization-Program/Verification/OP01-OP02-TRUSTED-CURRENT-SECURITY-ADOPTION-DECISION-v0.1.md`. Do not change GitHub branch settings, private app visibility/plan, writer scopes, or final/current authority from this optimization mission.
