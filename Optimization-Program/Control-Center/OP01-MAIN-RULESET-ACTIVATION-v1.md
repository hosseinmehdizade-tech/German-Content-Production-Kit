# OP01 — Activate the single required `main` governance check

**Authority:** owner action plan only; not a report of changed GitHub security settings.

## Live observed security facts — 2026-11-11
- Repository: `hosseinmehdizade-tech/German-Content-Production-Kit`, public, default branch `main`.
- Authenticated GitHub GET `/repos/.../rulesets` returned `[]`: no repository rulesets existed at observation time.
- Existing classic `/branches/main/protection` GET returned HTTP 403 `Resource not accessible by integration`: **classic branch protection remains UNKNOWN**, not proven absent.
- GitHub connected toolset **cannot create/edit branch rulesets**, even though repository metadata says the user has admin rights. Do not represent this file, a green Action, or repo owner permissions as actual security activation.

## Step A — make the check eligible
- Merge the exact PR that introduces `.github/workflows/gfp-required-governance-gate.yml` **only after all its CI runs complete and pass**.
- Confirm the job name shown in its GitHub Actions run is exactly `GFP-Required-Governance-Gate` (the workflow display name is `GFP Required Governance Gate`). Required status is the **job**, not the filename.
- The workflow has `pull_request: branches: [main]` and `push: branches: [main]`, with NO `paths` filters or conditional job steps. It uses read-only GitHub permissions, no persisted checkout token, and fails if the comparison base is missing. Do not make a path-filtered diagnostic workflow individually mandatory.

## Step B — repository OWNER must activate
1. GitHub → this repository → **Settings → Rules → Rulesets → New branch ruleset**.
2. Name `GFP-OPT-main-governance`; set **Enforcement status: Active**, not Evaluate/Disabled.
3. **Target branches:** Include default branch `main` only (or explicit `refs/heads/main`). No bypass actor, role or GitHub App.
4. Turn on **Require a pull request before merging**. For a sole maintainer, do **not** set a mandatory independent reviewer approval count (self-approval is not an independent review and would make solo work impossible).
5. Turn on **Require status checks to pass before merging**, add `GFP-Required-Governance-Gate`, and select **GitHub Actions** as the trusted source if offered. Keep `GFP-Required-Governance-Gate` as the sole universal required check; the existing path-filtered matrix workflows can continue running but may be skipped for unrelated PRs.
6. Turn on **Block force pushes** and **Restrict deletions**. Consider `Require branches to be up to date before merging` (strict); with many parallel content branches this produces more rebases/re-runs but tests exact current main integration. Do not enable merge queue until a `merge_group` trigger is separately implemented and tested.
7. Save. If Rulesets is unavailable on this account, use **Settings → Branches → Add branch protection rule** for `main` with the same PR, required-check, force-push and deletion rules, including administrators/no bypass where offered. First inspect/avoid conflicting pre-existing classic protection.

## Step C — provider readback and negative proof (not yet done)
- Read `GET /repos/hosseinmehdizade-tech/German-Content-Production-Kit/rulesets` again. Resolve the created ruleset ID and verify **Active**, correct `main` target, `pull_request`, `required_status_checks`, `required_check=GFP-Required-Governance-Gate`, no bypass and no force pushes/deletion.
- Run a new **synthetic negative PR** that violates one guard, and verify the required check is red AND GitHub prevents merge; close test PR without merging, with no learner content change.
- Record rule ID, provider readback, expected source, successful PR check and blocked negative merge in OP01 evidence. Until these exist: `OP01_SECURITY_HOLD` and **not** `BRANCH_PROTECTED_PASS`.

## Scope and residual risks
This check combines currently available deterministic policy, source/Stage5 receipt and ZIP and canonical-route tests on every PR. It is **not** an independent semantic Stage4 judge, authenticated Library byte attestation, browser Stage6/7 or a formal ADOPTED claim. Workflow files themselves are still mutable in PRs; a single-owner repository with no external trusted approval cannot claim adversary-proof protection solely by requiring a mutable GitHub Actions job. Code-owner approval or organization-managed required workflows may improve that later if additional authorized reviewers/infrastructure exist.

Official GitHub guidance:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks

<!-- OP01 Mergify Merge Protections real positive PR: docs-only, never merge. -->
