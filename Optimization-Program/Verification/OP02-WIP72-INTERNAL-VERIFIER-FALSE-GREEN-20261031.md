# OP-02 — WIP72 actual-byte QA false-green and original audit contract closure

**As observed:** 2026-10-31. **Scope:** OP01/OP02 process-only, nonactive original-ZIP verification. No workstream LATEST, original bytes, content, LOCKED, Library uploads, app/UI, Git rulesets or writer permissions edited.

## Exact original source of evidence

- The connected Library's exact WIP72 raw file:
  `/German-Content-Production-Kit/Checkpoints/Aber-Hallo-WIP72-12-EXACT-REKTION-929-ATTESTED-52-HOLDS-2026-10-30.zip`,
  registered `libfile_2ca6d2f2be508191971b80761222f18d`.
- Actual raw SHA-256 `b41b2a814eed37d87f01f90937ab21ee2976e9f059007c2f091b5d743e4ac225`, length 8,056,905, **exact** separately fetched Git LATEST and WIP72 receipt.
- All 484 ZIP members passed `testzip()` CRC. This says nothing about active-version semantic consistency.
- The embedded `05-QA-Tests/verify_package.py` was extracted unmodified from WIP72 original, SHA-256
  `0458762e9dc035db093c5f6f7bf522d7d1bac2bf669755fbfd197e0df5f44496`, and **executed against that same original WIP72 ZIP**. It returned exit 0, `result=PASS_SCOPED`, `errors=[]`, `error_count=0`, 788 units, 787 import rows, `durable_current_runtime=NOT_RUN`. Its published checks lack the four active pointer aliases, the `WORKING-STATE.status` edition and the working-state main hash aliases. It never claims full Stage4/Stage5-7.
- The exact WIP72 pointer *main* `canonical_sha256` and `import_sha256` equal actual canonical/import bytes and version `current=WIP72_12_EXACT_REKTION_929_ATTESTED_52_HOLDS` (therefore older two-field audits may falsely green).
- But exact pointer `working_canonical_sha256 =
  0f642168d96529fb32b6a90f3997eb69c9740c8d2f6c1c6d8417ffa2ce02ab74` and
  `working_import_sha256 =
  617c13856e2e2a3abfcffe12d6f013959bbedb14a61aec49487ffbbac6153ff4`
  are still inherited from WIP66, not WIP72.
- Exact `WORKING-STATE.status =
  WORKING_WIP65_845_REKTION_ATTESTED_136_HOLDS_STAGE4_OPEN` (WIP65); its main `canonical_sha256 =
  3f7ab282370638db20cbb1fe2c7c2f9f6f0dc97603d61519f2cd8f6e3c29fc1a` and
  `import_sha256 =
  1a5cf04bcebf4a5a8b136a9ae2706ac009683007f2d6a58204458fa2f9c74253`
  are WIP69 predecessors, not active WIP72. The `WORKING-STATE.working_*` fields are current.
- Active actual canonical SHA `b4e09dcf33aac4c41dc6db535817a4968c29c29aae048bfaef9e09b0f890a35f`, import SHA `38267e633db5ec2c5c3e0c109a94a80fba7c3a5ee3d2327e076aaab6e161d588`.

## Specific code gap closed

The previously merged nonactive `Verification/audit_op02_real_archive_pointer.py` validated exact ZIP bytes, SHA256SUMS, manifest, canonical/import and original sources, but verified only pointer current version and its **two main hashes**. That accepted the same sort of partially updated WIP72 pointer when all integrity bytes were self-consistent. The shared `Tools/content_package_guard.py` (PR64) and `Tools/library_publish_preflight.py` (PR65) already have stricter active-role checks; this change brings the *original independent readback checker* up to parity.

The read-only auditor now requires `WORKING-STATE.json` in the exact archive member universe; compares all four pointer active hash aliases to the actual present canonical/import bytes; verifies working state current WIP status and its four active aliases; and keeps parent/historical hashes outside the active role. It returns **BLOCKED** if ANY active alias/version is stale, while preserving `binary_integrity=PASS` when the original ZIP bytes themselves were valid.

The synthetic negative tests construct fully rehashed ZIPs with WIP72-correct main pointer hashes but stale working aliases, old WIP65 active status, old working-state main SHA or mixed stale states. They verify `status=BLOCKED` and all trust/issuer/Stage4–7/writer flags false. This is a QA tool repair, **not actual WIP72 content repair** and not a Stage4 release.

## Real independent issuer check remains blocked

A fresh GitHub API observation found:

- public Content Kit `main`: `protected=false`, `protection.enabled=false`, `rulesets=[]`;
- private Flashcards Pro `main`: `protected=false`; rulesets request returned 403 with GitHub's plan/visibility restriction — **keep app private**;
- WIP72 Git receipt commit `7cdb57e3961d361b5f38bea4e7971ec0367325c7` `verification.verified=false`, `reason=unsigned`. Its account login/author string is not independent user approval.
- `Optimization-Program/WRITER-SCOPES.json` remains `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL` with `scopes=[]`.

Even a completely coherent archive plus green CI is insufficient without independently authenticated issuer, exact authorized HEAD/hash, full AI semantic Stage4 and Stage5–7. Existing anti-bypass safeguards run only if invoked; direct GitHub/Library APIs remain outside those scripts.

## Decision boundary

**The only high-impact remaining architecture blocker is trusted enforcement**, not new hash algorithms. The explicit-owner decision pack already exists at
`Optimization-Program/Verification/OP01-OP02-TRUSTED-CURRENT-SECURITY-ADOPTION-DECISION-v0.1.md`. Request owner approval before installing an external GitHub App or enabling public Content Kit branch protection/trusted base-defined status; never change private app visibility or plan without approval.

Correct WIP73+ active producer metadata from exact final bytes before generating MANIFEST/SHA256SUMS; verify actual successor original ZIP and CAS under independently authorized producer scope. Do not mutate WIP72 in the optimization chat.
