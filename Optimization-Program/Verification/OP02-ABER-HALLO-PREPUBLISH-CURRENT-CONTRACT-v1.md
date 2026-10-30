# OP-02 Aber Hallo: prepublish CURRENT contract (NONACTIVE)

2026-10-30 — process proposal only. No source/LOCKED/card/ZIP edits, grant, Stage4 semantic PASS, or production activation.

## Observed incident

Real WIP61 LATEST: `authority.current_portable` points to the WIP61 ZIP while `complete_working_content_package` still points to **WIP60**. Real WIP61 receipt `gcpk-wip61-checkpoint@1` was initially unregistered. The explicit **read-only** family registration now recognizes its exact fields, but CURRENT remains BLOCKED by stale WIP60 complete-package role, missing WIP61 predecessor pointer and 415-versus-420 member-count conflict. Registration is NOT approval to repair content metadata or promote CURRENT; do not auto-repair or downgrade.

## WIP62 process follow-up (2026-10-30)

The content producer subsequently promoted WIP62. It is the live recorded
CURRENT rather than WIP61. WIP62 has coherent dual package roles (ZIP name,
SHA256, size, Library ID/path, member count) and an explicit WIP61 parent
SHA recorded in `previous_wip62_source_current`. WIP61's earlier stale role
is historical evidence, NOT a current WIP62 blocker.

The original WIP62 receipt `gcpk-aber-hallo-wip62-checkpoint@1` introduced
another contract format. The read-only WIP62 adapter explicitly checks:

- receipt-to-CURRENT ZIP identity, exact size/path, parent and member count;
- source SHA256 list in manifest order, not just `source_pdfs="PASS"`;
- count conservation (777+204=981), 788 units / 787 lexical cards;
- nine changed-card IDs: uniqueness, stable ID syntax and ledger count;
- scoped canonical/import parity claim, Stage4 OPEN, Stages5–7 NOT_RUN.

The synthetic prepublish diagnostic now calls the same registered receipt-family
validator, so a new schema name alone cannot cause a false metadata PASS.
A **new WIP63+ schema remains blocked until its exact field mapping is
registered and tested**; no automatic migration, schema inference, issuer
authorization or content editing is granted here.

All tests are **tracked-metadata-only**. A coherent metadata result is NOT
proof that ZIP/PDF binary bytes, linguistic decisions or importer/runtime
integration were independently accepted.

## Producer procedure BEFORE publication

1. Work only on a separately prepared candidate snapshot. Keep the previous CURRENT unchanged until actual producer approval/CAS.
2. Both candidate roles MUST identify the same exact ZIP: filename, SHA256, byte length, Library ID and path.
3. Parent receipt/package must equal `previous_wipN_source_current.portable.sha256`. Require registered source manifest identity (two original PDFs), Canonical/Import SHA256 and 788/787; attested + held = 981 governed, Stage4 OPEN, Stages5–7 NOT_RUN.
4. Reuse a registered stable receipt schema. An unknown schema needs explicit registration and adversarial validation before any promotion; never silently guess fields by the WIP number.
5. Run `Verification/audit_aber_hallo_producer_prepublish.py` with `--latest`, `--receipt`, `--sources`, `--receipt-relative-path`, and **`--strict`**. Exit 2 = do NOT promote. The normal diagnostic mode exits 0 even on BLOCKED and must not be used as an enforcement check.
6. After producer promotes through its separately authorized process, re-read exact CURRENT bytes and rerun the official currentness / Stage3–4 QA. Recheck concurrent main/head changes.

**Safety boundary:** This gate checks untrusted metadata only. It cannot verify original ZIP or PDF binary bytes, linguistic Stage4, independent issuer, Git branch protection or release authority. The installed workflow is explicitly nonrequired/nontrusted; actual producer-side enforcement still needs separate scope approval.
