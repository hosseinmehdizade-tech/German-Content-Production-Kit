# OP-01 — Always-on pull request governance check (ISOLATED PILOT, 2026-10-29)

## Why this experiment is needed

Real GitHub API inspection found **Content Kit public main unprotected** and with
**zero rulesets**, while the private App main was also unprotected and returned
an account feature limitation for ruleset inspection. The Aber Hallo WIP50
promoting commit was **unsigned**; several OP-02 PRs passed CI with **no
independent submitted PR reviews**. These are *governance gaps*, not failures
of binary source checks or the nonactive synthetic CI suites.

GitHub explicitly warns: a required check produced by a workflow skipped
due to `pull_request.paths` filtering can remain **Pending**, blocking merge.
The existing Stage3–Stage4 and Content quality/ZIP workflows have path filters.
They should **NOT** be made blanket required checks as-is.

## Pilot design

- Draft PR #31, isolated from `main`; not an approved security policy
- Candidate workflow `.github/workflows/op01-always-on-pr-governance-pilot.yml`
- Trigger: all `pull_request` events (opened, synchronized, reopened,
  ready_for_review), **no branch filter and no `paths`/`paths-ignore` filter**
- One stable status job: `op01-governance-preflight`
- `permissions: contents: read`, checkout credentials not persisted
- Read-only inventory check: `Optimization-Program/WRITER-SCOPES.json`
  must remain exact `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL` and `scopes=[]`
- No status-dependent or conditional skip paths
- A follow-up commit containing only this document in PR #31 is insufficient to
  prove docs-only PR behavior because GitHub evaluates the **aggregate PR diff**.
- Instead a separate nested documentation-only PR targets the isolated pilot
  branch, where the candidate workflow already exists. Only its own docs
  file diff counts; workflow is not changed in that nested PR.

## Acceptance evidence required before proposing enforcement

1. Find a real GitHub Action `pull_request` run for the original workflow
   commit, with stable `op01-governance-preflight` job and its complete logs.
2. Open a **separate docs-only PR targeting the candidate branch**, with
   no workflow or Python modifications in its PR diff, and confirm the same
   stable job is emitted and PASS. Do not rely on PR #31's aggregate diff.
3. Verify the nested PR changed-files list contains only documentation.
   Its other path-filtered workflows should not be mistaken for required checks.
4. Note that a green job tests **only default DENY_ALL structural
   presence**, not external issuer authentication, Git signer, review
   identity, branch protection, Stage4 or Stage5–7.
5. Leave this Draft PR unmerged until the owner explicitly authorizes the
   architecture/security configuration and a recovery route. Changing
   branch rulesets/visibility, requiring a reviewer or enforcing signed
   commits is **not** authorized here.

## Explicitly not a solution to independent CURRENT authorization

An admin who can change both this workflow and the scope registry can
bypass the gate on an unprotected branch. Branch protection plus a verified,
scope-specific issuer/approval channel is required for actual enforcement.
A self-authored `approved=true` JSON and any green CI are insufficient.

Relevant official docs:
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow

**Policy status:** DENY_ALL active. **Branch security settings changed: 0.**
No content or application files changed in this proposal.
