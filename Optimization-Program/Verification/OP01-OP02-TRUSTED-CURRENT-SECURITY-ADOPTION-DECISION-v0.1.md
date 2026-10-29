# OP-01 / OP-02 — Decision-ready CURRENT trust & CI enforcement migration v0.1

**As-of:** 2026-10-29. **Classification:** SECURITY-ARCHITECTURE PROPOSAL — NOT APPROVED, NOT ACTIVATED.
**Mission:** Optimization of Stage1–7 process only, no content edits. This proposal is an implementation decision pack rather than a new artificial PASS test.

## 1. Verified facts, actual project state

| Item | Observed status / evidence |
| --- | --- |
| Public Content Kit `main` | `protected=false`, `protection.enabled=false`, `GET /rulesets=[]`; current public repo checks repeated 2026-10-29 |
| Private German Flashcards Pro `main` | `protected=false`; rulesets API denied with "Upgrade to GitHub Pro or make this repository public"; private visibility must be preserved |
| Actual WIP50 CURRENT promotion | `1f94eac9e4038bdfa30a1a343edcab402997288a`, unsigned; exact WIP50 ZIP, Canonical, TSV, PDF and immutable Git blob/lineage had previously passed *scoped byte-integrity review* |
| Independent CURRENT issuer | **NOT AUTHENTICATED**; SHA, Git author name, GitHub-signed squash merge or CI is not independent scoped user authorization |
| Aber Hallo Stage4 | Current WIP50 unsigned worksheet has 788 rows, 0 decisions and 604 stale unit IDs; no full semantic signoff |
| OP-01 writer scopes | Exact `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL` and `scopes=[]` — not a tamper-proof enforcement boundary while main remains unprotected |
| Historical [PR #31](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/31) | Actual docs-only status trigger PASS but **closed unmerged** due to security bypass |
| [PR #33](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/33) | Real PR-head workflow mutation kept name `op01-governance-preflight`, removed actual check, emitted [SUCCESS 40955556999](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40955556999) with bypass marker. **Never use a plain green PR-head workflow as a trusted issuer** |

## 2. GitHub platform constraints relevant to October 2026

1. An ordinary `pull_request` workflow runs in PR context and can be authored/changed by the PR. **Stable job name + GitHub Actions expected source alone does not prove a protected policy check**; PR #33 reproduced the false-positive locally on isolated branches.
2. `pull_request_target` uses workflow defined by default/base repository, making it a potential *trusted-definition* control. It must **never checkout or execute PR-head code, scripts, package scripts or untrusted artifacts**; restrict token to `contents: read`, prefer inspection of PR paths/metadata as **data** via safely parsed GitHub API. A protected default branch remains prerequisite.
3. Official GitHub docs (accessed 2026-10-29) describe a **new public-repository default Actions event policy for `pull_request_target`**, currently `evaluate`, with planned **enforcement on 2026-12-02**. Verify fresh docs/policy insights at implementation: an unapproved `pull_request_target` deployment may cease running, leaving required checks Pending. Only enable a narrowly scoped event-policy exception if its security risks and availability are understood. No exception was configured here.
4. `workflow_run` is **not** listed among workflow-triggered check events GitHub accepts for required PR status checks, despite its utility for safely separating privileges; do not adopt it as a Required Check until a real compatible status-projection mechanism is proven. An external GitHub App check can be treated separately under GitHub's documented rules.
5. GitHub supports selecting a specific expected GitHub App as source of a required check; this is **not enough if genuine and spoofed checks both originate from GitHub Actions**. Trusted workflow identity and protected policy/configuration must be guaranteed as well. Branch rules can be piloted in `Evaluate` mode where that feature is available without active enforcement.
6. Existing `stage3-4-compatibility.yml`, `content-zip-guard.yml` and `content-quality-v3.1.11.yml` use `paths` filters. Requiring their checks for every PR can deadlock unrelated changes. A required gate must emit on all covered PRs and be tested on docs-only/changed-workflow/reopened/synchronized PRs and concurrency.

GitHub documentation:
- https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository

## 3. Two actual deployment choices; neither automatically approved

**Route A: Protected public main + trusted base-defined status (simpler ownership, conditional on event policy).**
- Review and explicitly authorize a minimum read-only `pull_request_target` workflow **from trusted default branch**, with `permissions: contents: read`, no untrusted checkout, no caching/upload of secrets, no dynamic shell interpolation from PR titles/messages.
- Via authenticated API, retrieve bounded paginated changed-file paths and latest PR head SHA; allow-list benign paths and **fail closed** on `.github/workflows/**`, `Optimization-Program/WRITER-SCOPES.json`, content `Workspaces/**/LATEST.json`, source manifests, ambiguous renamed/too-large/incomplete diffs unless separately approved with exact workstream/path/commit. Re-read head SHA before accepting to reject races. These checks decide *governance preflight* only, never Stage4 or CURRENT publisher authority.
- Protect public Content Kit `main` (PR-only merges, disallow force push and deletion, bypass scope narrowly controlled) **before** trusting the workflow as immutable. Consider status source and all-required-check availability, solo-owner recovery strategy, and whether it is possible to use this event under GitHub's coming default block. Preserve owner write workflows without accidental permanent deadlock.
- **Must not** copy the untrusted `pull_request` pilot PR31 code into a required check without redesign.

**Route B: Protected public main + independently installed/protected GitHub App verifier (stronger check origin separation).**
- Independent App analyzes PR metadata and content as untrusted **data** and publishes a named check bound to exact PR head/merge SHA; source pinned to *that specific GitHub App* in rulesets. App keys and policy live outside repository/PR-author control.
- Prevent App from treating branch-shared self-attested `approved=true` flags or an author's title as issuer authorization. Signed promotion approval is a *separate* exact-workstream, exact-portable-hash, exact Git-target decision from independently authenticated owner/security principal.
- This route needs selecting/installing a verifier App, permissions, credential custody, operational cost and owner approval. No current connector action implements or installs such an independent verifier; do not claim it is already available.

**Separate private App repo:** keep private. Current account feature limitation makes branch protection/rulesets unavailable via observed API. Explicit later choice: upgrade supported GitHub plan **or** use external signed release manifest / independent verification for App until protections become available. Do not change visibility, subscription, repo settings or v486-R120 app.

## 4. Exact safe rollout and rollback protocol (approval-gated)

| Phase | Gate / acceptance proof | Failure recovery |
| --- | --- | --- |
| 0: OWNER DECISION | Choose route A/B, protected targets, signer/reviewer, ruleset and bypass/recovery owner; approval specifically names exact repository/main and scope | No change; leave DENY_ALL |
| 1: TRUSTED ROOT | Verify trusted workflow/App implementation and its maintained key/code are not writable by the PR author; if using `pull_request_target`, confirm allowed event policy and no untrusted code execution | Disable/abort candidate before any enforcement |
| 2: STATUS PILOT | On trusted default base, test doc-only, workflow mutation, writer-scope mutation, unrelated code, force push attempt (non-destructively), synchronizations, missing/partial API responses and up-to-date head SHA | Never make required until actual checks pass, including malicious PR failure |
| 3: RULESET EVALUATION | Inspect available `Evaluate` status and insights on public Content Kit; define precise stable check name **and origin**, avoid path-filtered checks and nonexistent required reviewer; observe real PRs | Keep `Evaluate`/disabled rather than activating a broken rule |
| 4: ENFORCE MAIN | Only after explicit OWNER approval and demonstrated recoverability: require PRs, protect against force push/deletion, enforce trusted check; independently read back `main.protected`, rulesets, bypass list, and current branch HEAD | Emergency, audited owner/admin change with approval and post-action readback; not silent force push |
| 5: AUTHORIZE ONE CURRENT | Explicit independently authenticated user approval binds a named workstream, exact artifact hashes/source, HEAD SHA and expiry; verify signer externally to repo and re-read Git/Drive before CAS | Reject/hold on stale SHA, invalid signer, missing semantic Stage4 or unresolved source; never silently downgrade |
| 6: SEPARATE STAGE4–7 | Actual 788-unit independent Stage4, new exact worksheet and review receipts, Stage5 four-role clean delivery, Stage6 importer and Stage7 app regression have their own authorities/checkpoints | Preserve original, LOCKED, latest verified backups; no premature release |

**Decision invariant:** neither PR/CI success, GitHub commit verification nor byte-integrity PASS can independently grant writer scopes, replace a reviewer's verified identity, or qualify a final release. `Optimization-Program/WRITER-SCOPES.json` stays DENY_ALL until *separate* named authorization and external enforcement.

## 5. Present disposition

`DECISION_READY_GOVERNANCE_DESIGN_ONLY` — **not implemented**.
All test PRs #31/#32/#33 are closed without merge. No new workflow, branch protection, ruleset, review requirement, event-policy exception, checker installation, account billing, writer grant, content edition, CURRENT update, Library operation, app runtime or visible UI changed by this document.

**Owner-facing recommended first decision:** for the *public Content Kit only*, choose between (A) base-defined `pull_request_target` read-only preflight **after** verifying the new event policy and protecting main, or (B) independent GitHub App/source-pinned status. Keep the private app decision separate. Explicit authorization is required before deploying either.
