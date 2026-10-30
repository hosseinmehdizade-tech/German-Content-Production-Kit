# OP-02 — First producer-path prevention of stale Aber Hallo CURRENT metadata

**NONRELEASE PROCESS HARDENING.** 2026-10-30. Strictly scoped to
`Tools/content_package_guard.py` **when** the archive contains the
Aber Hallo eight-folder active metadata layout. No change to original
WIP65-69 ZIPs, source PDFs, learner data, workstream LATEST, LOCKED,
GitHub branch protections, app runtime/UI, or writer scopes.

## Original bytes and transition evidence

Original WIP65/66 Library packages had embedded pointer versions
WIP65/WIP66 and correct current Canonical/Import digest bindings. The
WIP66 `WORKING-STATE.json.status`, however, already reported
`WORKING_WIP65_...`, so the **earliest observed stale working-state
status is WIP66**, preceding the WIP67 pointer failure. WIP67, WIP68
and WIP69 then reused the exact same WIP66
`CURRENT-WORKSTREAM-POINTER.json` (5,339 bytes, SHA256
`2770c722c1b0684168b3f620daa61a56c827718cf6dc8509b7c188d6ed9c7103`).
WIP68 and WIP69 `WORKING-STATE.json.status` also stayed WIP65,
though their working Canonical/Import digests and current_content_status
were updated. The WIP69 original Library file SHA256
`624dca6a6cdd09996f72693d16149914ab7c583bf6c78c41554f2b3a35ee4ef6`
matched the subsequently observed Git WIP69 CURRENT. The precise
external producer script remains unlocated: GitHub code search found
no uniquely identifiable writer of these Aber Hallo WIP ZIPs.

**Never guess a root-cause script without source.** The byte history
shows parent metadata was selectively carried forward while other
active fields were updated. That is sufficient to justify a
*prepublication anti-staleness gate*, not to assert which agent/script
performed copying.

## Actual process hardening (not merely a synthetic verifier)

`Tools/content_package_guard.py` is an existing shared tool used by
the tracked Clean Delivery and Menschen A2 builders. Its
`guarded_zip()` creates a temporary archive, computes the archived
payload signature and only then links the complete ZIP into the output.
This PR inserts a strictly scoped **Aber Hallo active-contract
preflight** immediately before that final signature/publication step.

If an archive declares the exact Aber Hallo workstream with active
roles, it must have all of:

- `MANIFEST.json.summary.status` with `CURRENT_WIP<N>_...`
  and the exact SHA256 of final canonical and import bytes;
- `07-Checkpoint-State/CURRENT-WORKSTREAM-POINTER.json.current`
  with the same WIP version, and all four active canonical/import SHA
  aliases equal to the final bytes;
- `07-Checkpoint-State/WORKING-STATE.json.status` with
  `WORKING_WIP<N>_...` and all four active SHA aliases equal to the
  final bytes;
- no ambiguous/duplicate JSON keys, missing active role, nonfinite
  JSON numbers, or mismatched workstream identity.

Historical `previous_wip...` hashes remain immutable and **are not
silently reinterpreted** as active pointers. The checker does not
rewrite the pointer, construct a WIP70 successor, or grant Stage4–7.

If validation fails, `guarded_zip()` fails closed before atomically
publishing the output. The temporary archive is cleaned up and
no published ZIP/index is added by this failed attempt. This does
not retroactively protect a producer that does not use
`guarded_zip()`. To support that path,
`Tools/prepublish_aber_hallo_guard.py` is a **read-only** independent
CLI for any just-built original ZIP; exit 2 on a mismatch, exit 0 on
scoped internal consistency only. No approval follows from exit 0.

Example future candidate after an authorized producer creates it:

```bash
python Tools/prepublish_aber_hallo_guard.py /path/to/candidate.zip \
  --expected-milestone WIP70_EXPLICIT_CANDIDATE \
  --expected-sha256 <exact-scope-independent-zip-sha256>
```

The exact milestone and digest must be provided from a separately
resolved authority; do not accept values from self-serving candidate
metadata as independent issuer evidence. A false-green CI on a PR
cannot authenticate a user/grant.

## External tests and acceptance boundary

Dedicated `Verification/test_op02_guarded_aber_current.py`
covers valid active WIP70, version independence, stale predecessor
pointer, bad active digests, stale `WORKING-STATE.status`, malformed
manifest, missing active files, duplicate keys, generic ZIP isolation,
atomic no-output on failure, and CLI exit codes. CI cross-OS +
existing content regression and ZIP safety regression must all PASS
before merge.

**LIMITATION:** The actual WIP69 producer is still not proven to
be wired to `guarded_zip()`. This PR hardens the known canonical
guarded route and exposes a local CLI; the producer must explicitly
adopt the gate and refresh all active metadata from final bytes before
a successor is eligible. WIP69 retains its original defect; Stage4
OPEN, Stages5–7 NOT_RUN, and OP01 `DENY_ALL`/issuer HOLD remain.
