# OP-02 — Close a known final-Library admission gap without blocking recovery

**2026-10-30 | Scope: process only.** No learner card, original source,
workstream LATEST, immutable/LOCKED ZIP, app runtime/UI, author rights,
issuer policy or Library file was changed by this work.

## Current original-byte observation

Current observed registered `WIP70` is the actual Library ZIP
`Aber-Hallo-WIP70-7-EXACT-REKTION-907-ATTESTED-74-HOLDS-2026-10-30.zip`,
8,084,954 bytes, SHA256
`669e7e73da4822709d5751e443b15439da69e68f693b408d2559e55ea71e57ad`.
It is pinned in the workstream's live Git
`Workspaces/aber-hallo-listen-tabellen/LATEST.json`.
The exact original ZIP was materialized read-only, SHA256 checked, and
all 470 members passed ZIP CRC validation.

The active pointer advanced from WIP66 to WIP70 in only **some** fields:

- `CURRENT-WORKSTREAM-POINTER.json.current =
  WIP70_7_EXACT_LEXICON_907_ATTESTED_74_HOLDS` (correct version).
- Pointer `canonical_sha256` and `import_sha256` match the current
  actual payload bytes. However both `working_canonical_sha256` and
  `working_import_sha256` still match the WIP66 predecessor, **not**
  the WIP70 canonical/import bytes.
- `WORKING-STATE.json.status =
  WORKING_WIP65_845_REKTION_ATTESTED_136_HOLDS_STAGE4_OPEN`
  still names WIP65. Its `working_*` hashes are current, but
  `canonical_sha256` and `import_sha256` still name older bytes.
- The outer `MANIFEST.json.summary` correctly claims CURRENT_WIP70
  and the actual WIP70 canonical/import digests.

Thus the original file integrity and corrected primary pointer are
not enough for coherent publication. This WIP70 is **not** a final
release; 907/981 governed patterns have been attested, 74 remain held,
full Stage4 OPEN, Stage5–7 NOT_RUN.

## Real default publisher gap and narrow fix

`Tools/content_package_guard.py` was hardened in PR #64 so builders
using `guarded_zip()` reject wrong active metadata before atomic ZIP
publication. However the original Aber Hallo producer's exact code
entrypoint is still not located, and the real WIP70 Library upload
occurred with stale roles. No statement that every producer uses
`guarded_zip()` is warranted.

`Tools/library_publish_preflight.py` previously checked source ZIP
CRC/member paths, a caller-provided quality receipt, destination
collisions and duplicate hashes, but **did not check active
CURRENT-WORKSTREAM-POINTER and WORKING-STATE**. An internally stale
Aber Hallo ZIP with an otherwise plausible, attacker-supplied Stage7
receipt could therefore reach `ALLOW` through this preflight.

This PR adds a second gate, **only** if
`workstream == "aber-hallo-listen-tabellen"` and
`purpose in {"final_delivery","validated_major_checkpoint"}`.
The actual original archive members are checked with the shared
`check_aber_hallo_active_pointer()` contract before the Library
preflight evaluates a quality receipt, catalog or ALLOW result.
Malformed, missing, mismatched CURRENT/pointer/working/manifest roles
return `BLOCK` with a narrow reason. No archive is rewritten.

The deliberately distinct
`required_recovery` and `explicit_user_checkpoint` purposes do
**not** acquire a false FINAL requirement: they may preserve a broken
original as immutable recovery material, but they are never promoted
to final merely because the Library transfer succeeded.

The change does not affect other workstream categories, and the
standard existing Library preflight tests must stay green.
The new synthetic tests bypass `guarded_zip()` by producing raw test
ZIPs, so they specifically prove that the second publisher boundary
detects a defect from an external/unguarded producer.

## Still not solved by this gate

The Library API can be invoked without executing this repository's
preflight. This code cannot intercept those calls and does not
independently authenticate a producer, user approval, current
authorized commit or protected issuer. A caller may also label
an actual release as `explicit_user_checkpoint`; labels alone are not
a trusted release role. Existing OP01 writer scopes remain DENY_ALL;
Content Kit main branch protection and trusted issuer are still
unresolved. All Stage4/5/6/7 remain separately gated.

**Next architecture decision (requires explicit owner approval):**
a mandatory enforceable trusted issuer/ruleset and final-publish
server-side attestation, plus producer wiring. Only an independent
trusted boundary can prevent callers from bypassing this opt-in
preflight. Do not claim that nonrequired green PR-head CI is a
production authorizer.
