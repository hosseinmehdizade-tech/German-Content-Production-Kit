# OP-02 — Stable typed receipt v1 (NONACTIVE PROPOSAL)

**Status:** PROPOSED / SYNTHETIC TESTS ONLY. Not a production receipt,
not a producer migration, not an issuer, not a Stage4/5/6/7 acceptance
and not a replacement for exact learner content CURRENT.

## The defect this addresses

Observed Aber Hallo WIP58–WIP63 receipt shapes use changing field
names and sometimes changing schema names per milestone. This has
required repeated validator edits and risks accidental acceptance of
a stale old schema or accidental WIP downgrades. WIP63 is the latest
observed CURRENT at this proposal's design snapshot. Never pin WIP63
permanently; resolve live LATEST + receipt on every continuation.

## Proposed stable envelope (never auto-adapt historic receipts)

`schema: gcpk-content-milestone-typed@1` remains constant across
new versions **only when the producer deliberately emits this exact
approved schema**. The WIP sequence belongs to `milestone`, the
`receipt_path`, the portable's filename, and the separately resolved
`previous_wipN_source_current` predecessor. Neither filename nor
schema alone grants currentness.

Mandatory typed fields are `workstream, milestone, receipt_path, status,
portable, parent_sha256, source_sha256, counts, zip_members, gates`.
`portable` contains exact ZIP filename/hash/size, Library ID/path and
Canonical/Import SHA256. `counts` holds learning_units, import_cards,
attested, holds, governed_patterns, new_attested, changed_cards and the
changed_card_ids ledger. `gates` records Stage4 OPEN, Stages5–7 NOT_RUN
and explicitly scoped canonical/import parity claim.

A separate trusted profile pins workstream identity, ordered
source IDs/SHA256, imported/learned cardinalities, governed universe
and stable card-ID prefix. The profile is a **local test assumption**,
not authenticated independently in this experiment. Workstream-specific
cardinality rules must not be generalized to unlike content.

## Adversarial behavior

- Unknown/missing/extra typed fields, schema spoof and historical
  receipt replay: BLOCK.
- Mismatch in any of the three ZIP identity roles, parent/predecessor
  lineage, path/current milestone or size/member count: BLOCK.
- Changed-card ledger duplicate, count drift, foreign prefix, source
  hash list reorder, altered manifest, forged PDF source identity: BLOCK.
- Boolean-as-integer, NaN, duplicate JSON keys and false Stage4/5–7:
  BLOCK.
- Synthetic WIP63 then synthetic WIP64 with **the same stable schema**
  are accepted only as `PASS_NONACTIVE_TYPED_METADATA_ONLY_NOT_RELEASE`.
- The result always returns false for issuer authentication, raw ZIP
  and PDF verification, Stage4 semantic PASS, Stage5/6/7 and writer grant.

## Rollout and rollback (approval required)

1. Keep all existing WIP58–63 receipt adapters and read-only CURRENT
   checks intact. Historical receipts are *not* rewritten and the
   existing active/nonactive prepublish checker is not redirected.
2. Execute the isolated Python unittest suite on Ubuntu and Windows,
   with adversarial negatives, verified exact Git branch/head.
3. Before considering producer activation, create a separately
   approved immutable schema/profile and producer-owned candidate
   emission path, with exact original bytes and independent trust-root
   or authenticated issuer plan. Do not infer new schema from WIP number.
4. Prove the typed candidate matches actual ZIP/manifest bytes, pass
   independent Stage4 linguistic review, anti-downgrade, CAS,
   source/LOCKED preservation and all relevant Stage5–7 acceptance.
5. Adopt via opt-in, versioned producer contract with a rollback
   switch retaining historical read support; only after verified
   cross-repository compatibility and explicit migration approval.
6. On failure, **stop typed producer promotion**, retain prior CURRENT,
   restore legacy read path and preserve all immutable artifacts.
   Never change the real content workstream LATEST in this optimization PR.

## Evidence boundaries

Only read-only Git checkpoint/manifest metadata underlies this plan.
Current original PDF bytes, the registered Library ZIP and exact
runtime v503+ compatibility are **not** verified by these tests. A
synchronized forged set of Git text plus profile can pass locally,
which is why a separately trusted issuer and original-binary checks
must remain required for any release. Do not call this final, source
verified, issuer authenticated, Stage4 PASS or production activated.
