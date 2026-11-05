# GFP-OPT P1 — Four branch-qualified root checkpoint discoveries, one grammar HOLD

**Program:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`)  
**Manager:** Project Control Center  
**Scope:** Root checkpoint **navigation recovery**, not new content authority, Stage acceptance, CURRENT or policy adoption.

## Findings from the live GitHub source-owner branches (2026-11-05)

The previous central dashboard reported five `ROOT_CHECKPOINT_UNTRACKED` paths. The paths genuinely are not tracked on the current `main`. But **four same-path CHECKPOINTs were directly retrieved from explicit, named, source-owner branches**:

| Root key | Git branch that contains the originally referenced path | Exact observed checkpoint Git blob | What this proves |
| --- | --- | --- | --- |
| 250 Verben Deutschweb | `250-verben-mit-praepositionen-production` | `3a4c32612761085a6d962e7c4b9510d5f4a2bb53` | Historic source checkpoint reachable as `branch:path`; it reported Stage7 locked with Library persistence pending |
| 250 Verben Kombinationen | `250-verben-mit-praepositionen-kombinationen-v336` | `677b51fa426052790be9d92dabea10a8049c2fc2` | Historic LOCKED source release checkpoint reachable, **no reissue of FINAL** |
| Nomen-Verb-Verbindungen | `nvv-production` | `03eb899e8f46ec27ceb79eb540a0bbc70f534401` | **Old** branch checkpoint reachable; its `updated_at` is **October 7, 2026**, so do NOT mark current |
| Unregelmäßige Verben Kombinationen | `unregelmaessige-verben-v130-kombinationen` | `edb1b4e223effd3bdc305646a10e80d055ec9b21` | Historic v1.3.0 branch content reachable, never replace independent newer v1.3.1 work |
| Grammatik aktiv A1–C1 | **No exact branch candidate independently found** | — | Keep source-owner Checkpoint **HOLD**; both Grammar Aktiv source PDF registrations remain separate |

Paths and source families are anchored in [`RESUME-ROUTES.json`](../RESUME-ROUTES.json) and the [master catalog](MASTER-PROJECT-CATALOG-v1.json). The machine-readable [branch evidence registry](ROOT-CHECKPOINT-BRANCH-CANDIDATES-v1.json) records these four exact historical Git blob SHA1s, owning workstreams and the one grammar HOLD. It does **not** rewrite `RESUME-ROUTES.json` or the root `PROJECT-STATE.json`.

### Important NEW NVV freshness conflict

The `nvv-production` branch checkpoint still describes the old **2026-10-07** final-content state. But a fresh authenticated ChatGPT Library folder listing on **2026-11-05** exposes a newer source-owned artifact *candidate*:

- `NVV-R6.1-B01-STAGE4-RISK-BASED-ACCEPTED-87-20261105.zip`
- Library record ID `libfile_a8efd55b225c81918b304349f475e92e`
- Listed size **3,430,764 bytes**, modified at `2026-11-05T16:59:27.814296+00:00`

The ZIP itself has **not** been downloaded, hashed, unzipped or approved in this control-center task; its title and last-modified timestamp do not prove Stage4/FINAL or CURRENT. This observation is a **blocker to promoting the older branch checkpoint as latest**, not evidence that the new artifact is authoritative.

## Actual independent live verification

[`Verification/reconcile_live_root_checkpoints_v1.py`](../../Verification/reconcile_live_root_checkpoints_v1.py) performs provider-API readback, not a text-only checklist:

1. Read the registry, current source identities, root routes and version-pinned Git index blobs. Require exact coverage of all five root keys.
2. Read `GitHub main` HEAD and its exact **five checkpoint paths** at immutable commit SHA. Paths being present means the old root warning has changed and needs reevaluation.
3. For each of four branch witnesses, independently resolve its **branch HEAD**, read exact same-path `CHECKPOINT.json` at immutable branch commit, verify Git Contents API SHA, decoded content's true Git-blob SHA1, length, named workstream owner, versioned historical status and expected witness blob.
4. Resolve that branch HEAD again. If changed in mid-read, refuse the old witness as current. Also recheck `main` HEAD at the end.
5. Emit an **exclusive**, external JSON receipt, with each root tagged `PASS_BRANCH_QUALIFIED_CHECKPOINT_BLOB_EXISTS__NOT_CURRENT`, a review/drift status, or `NO_BRANCH_CANDIDATE__SOURCE_OWNER_HOLD` for Grammar.

The GitHub Actions workflow [`gfp-opt-p1-root-branch-recovery.yml`](../../.github/workflows/gfp-opt-p1-root-branch-recovery.yml) verifies actual live GitHub source owner branches on Ubuntu and Windows with read-only `GITHUB_TOKEN`; it separately runs mocked adversarial ref/blob/owner/main-change tests. GitHub API authentication checks only GitHub; Library metadata is documented separately and **does not become proof of Library ZIP content**.

The four static historical branch-qualified navigational references also appear in the **same existing Control Center dashboard** through `Tools/build_domain_adapter_preflight_v1.py`. The global dashboard itself labels them **`EXACT_BRANCH_BLOB_OBSERVED_PREVIOUSLY__NOT_LIVE_VERIFIED_BY_DASHBOARD`**, while the separate independent live verifier supplies dated remote readback evidence. Both agree: root contents are **never auto-copied from another branch**.

## Commands

```bash
# GitHub private repo: set a read-only GITHUB_TOKEN in environment if needed.
python -B -m unittest discover -s Verification/tests \
  -p test_live_root_checkpoint_recovery_v1.py -v

python -B Verification/reconcile_live_root_checkpoints_v1.py \
  --summary --report /new/external/branch-checkpoint-readback.json

# Existing all-family status dashboard includes the four branch locators.
python -B Tools/build_policy_adoption_control_center_v1.py \
  --output-dir /new/external/global-control-center-status
```

## What is still OPEN

No one is authorized to declare source CURRENT from a historic branch `CHECKPOINT`. For each root workstream, source-owner approval and the latest explicit user artifact/valid source portable must be compared with current Git/Library bytes **before** changing any pointer. For Grammar the actual source-owner Checkpoint authority has not been located. NVV needs a direct comparison of its new Library R22-style Stage4 candidate against the older branch checkpoint, not a silent downgrade. Neither content, the original source PDFs, LOCKED releases, learner cards, App UI/runtime, IndexedDB nor SRS/FSRS is edited here.

**Next program milestone:** reviewable pointer-resolution proposals for the four source owners + first Grammar authority recovery, and source-owned native Stage2 for Lesen once source PDF CURRENT is independently verified. This optimization lane must not impersonate a content workstream's Stage approval.
