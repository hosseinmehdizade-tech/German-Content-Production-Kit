# OP-02 Aber Hallo: prepublish CURRENT contract (NONACTIVE)

2026-10-30 — process proposal only. No source/LOCKED/card/ZIP edits, grant, Stage4 semantic PASS, or production activation.

## Observed incident

Real WIP61 LATEST: `authority.current_portable` points to the WIP61 ZIP while `complete_working_content_package` still points to **WIP60**. Real WIP61 receipt `gcpk-wip61-checkpoint@1` was initially unregistered. The explicit **read-only** family registration now recognizes its exact fields, but CURRENT remains BLOCKED by stale WIP60 complete-package role, missing WIP61 predecessor pointer and 415-versus-420 member-count conflict. Registration is NOT approval to repair content metadata or promote CURRENT; do not auto-repair or downgrade.

## Producer procedure BEFORE publication

1. Work only on a separately prepared candidate snapshot. Keep the previous CURRENT unchanged until actual producer approval/CAS.
2. Both candidate roles MUST identify the same exact ZIP: filename, SHA256, byte length, Library ID and path.
3. Parent receipt/package must equal `previous_wipN_source_current.portable.sha256`. Require registered source manifest identity (two original PDFs), Canonical/Import SHA256 and 788/787; attested + held = 981 governed, Stage4 OPEN, Stages5–7 NOT_RUN.
4. Reuse a registered stable receipt schema. An unknown schema needs explicit registration and adversarial validation before any promotion; never silently guess fields by the WIP number.
5. Run `Verification/audit_aber_hallo_producer_prepublish.py` with `--latest`, `--receipt`, `--sources`, `--receipt-relative-path`, and **`--strict`**. Exit 2 = do NOT promote. The normal diagnostic mode exits 0 even on BLOCKED and must not be used as an enforcement check.
6. After producer promotes through its separately authorized process, re-read exact CURRENT bytes and rerun the official currentness / Stage3–4 QA. Recheck concurrent main/head changes.

**Safety boundary:** This gate checks untrusted metadata only. It cannot verify original ZIP or PDF binary bytes, linguistic Stage4, independent issuer, Git branch protection or release authority. The installed workflow is explicitly nonrequired/nontrusted; actual producer-side enforcement still needs separate scope approval.
