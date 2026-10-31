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


### 4A. Real GitHub check-run source collision (2026-10-30 read-only recheck)

A fresh read of GitHub's **real** `GET /commits/{pr-head-sha}/check-runs` and the **real** [PR #33 diff](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/33) verified that a green GitHub Actions check is not a trusted base-defined status:

| Actual public PR | PR-head SHA | Check name | Conclusion | Check app slug / integration ID |
| --- | --- | --- | --- | --- |
| [#33 (malicious unmerged test)](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/33) | `c2aeb4fe30e47cb0150aa828472af92961e8c1b5` | `op01-governance-preflight` | `success` | `github-actions` / **15368** |
| [#51 (merged safe code/test change)](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/51) | `fdc3aed7bb16e6e108b9be109a08ebdff8150fc2` | `safe-packaging (ubuntu-latest)` | `success` | `github-actions` / **15368** |

The actual #33 patch replaced the **DENY_ALL** verification with an `echo` statement, without changing the check name or GitHub Actions app identity, then returned green. Therefore a branch rule that merely pins required-check `context` and integration ID **15368** cannot distinguish a head-defined spoofed job from a protected base-defined job. The two checks above have **different names**; they corroborate that source identity is shared, not that their validation logic is identical. A check success at an exact PR-head SHA still does not authenticate the workflow definition used to produce it.

**Required before real protection rollout:** Route A must demonstrate that the policy check executes from an independently protected **base-defined workflow**, that an attacker cannot redefine it in a PR head, and that current GitHub event policy permits it on every intended PR. Route B needs an independently controlled GitHub App issuer with keys/policy outside the PR author's control. Neither route is approved or deployed; `WRITER-SCOPES` remains `DENY_ALL`. The read-only OP01 check-origin analyzer now returns `BLOCKED_CHECK_ORIGIN_NOT_AUTHENTICATED` even when the check is green and its GitHub Actions app ID matches.


## 5. Present disposition

`DECISION_READY_GOVERNANCE_DESIGN_ONLY` — **not implemented**.
All test PRs #31/#32/#33 are closed without merge. No new workflow, branch protection, ruleset, review requirement, event-policy exception, checker installation, account billing, writer grant, content edition, CURRENT update, Library operation, app runtime or visible UI changed by this document.

**Owner-facing recommended first decision:** for the *public Content Kit only*, choose between (A) base-defined `pull_request_target` read-only preflight **after** verifying the new event policy and protecting main, or (B) independent GitHub App/source-pinned status. Keep the private app decision separate. Explicit authorization is required before deploying either.


## 6. 2026-10-31 live owner decision refresh — no setting changes

**Observed from the connected GitHub repository REST API**, not self-asserted CI:

| Exact subject | Read-only live observation (2026-10-31) | Implication |
| --- | --- | --- |
| Public Content Kit `main` | `protected=false`; `protection.enabled=false`; `GET /rulesets=[]` | No independently enforced merge/publish policy root. |
| Private Flashcards Pro `main` | `protected=false`; private rulesets endpoint returns HTTP 403, GitHub plan/visibility restriction | **Keep app PRIVATE**. Upgrade eligibility is a separate explicit owner decision; do not make private source public. |
| `WRITER-SCOPES.json` | `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL`, empty scopes | No content write grant; editable policy file itself is not independently protected. |
| Actual closed unmerged [PR #33](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/33) | spoofed `op01-governance-preflight` succeeded on head `c2aeb4fe30e47cb0150aa828472af92961e8c1b5`; GitHub checks app slug `github-actions`, integration ID `15368` | Same event/workflow/check name may be replaced in an untrusted PR while the returned check is green. |
| Actual merged [PR #68](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/68) | all sampled green PR-head checks also use `github-actions` / integration `15368` | Pinning `15368` does not distinguish valid protected logic from spoofed job logic. |
| Public GitHub Actions `pull_request_target` default | GitHub official docs **currently say enforcement December 2, 2026**, now evaluate mode; a repository-specific event policy may be needed to keep a legitimate base-defined workflow running | Do **not** mark a `pull_request_target` check required before verifying the event policy, pilot execution, and sole-maintainer recovery. |

GitHub current documentation, checked 2026-10-31:
- https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches

### Concrete choice to request from the owner (NOT implicit in “continue”)

**Recommend split Route A into two independently approved changes:**

**A0 — baseline public-main protection only:** With explicit authorization limited to `hosseinmehdizade-tech/German-Content-Production-Kit:refs/heads/main`, create an exact-name `main` ruleset in GitHub's UI (public repositories support rulesets on GitHub Free), no broad bypass actor, require PRs, disallow force push and deletion. **Initially require zero status checks** until a stable, independently sourced check is proven. Do not require an unavailable second human reviewer for a solo-maintainer project; evaluate review-requirement availability first. Check feasibility and emergency owner recovery before activation. Re-read `main.protected`, complete ruleset and bypass details after. This controls accidental/unreviewed direct pushes but is **not** authenticated CURRENT issuance. A ruleset-admin can still change settings, so it is not an external trust principal.

**A1 — separately approved trusted publication authorization:** Pilot a base-defined read-only workflow with the required event policy, or a separately controlled GitHub App with its own required-check origin and policy/key custody. Verify trigger behavior on docs-only, changed-workflow, stale/head-updated, reopened and malicious same-name PRs before requiring the check. On GitHub, an ordinary `pull_request` job with the expected context and `github-actions/15368` **is not sufficient**; the PR #33 real counterexample must stay a release blocker. A protected branch plus a green CI is still not a signed owner approval of exact content bytes. Bind any eventual producer approval to independent exact workstream/portable SHA/CAS and separate full Stage4/5/6/7 evidence.

**Route B — independently managed GitHub App** is an alternative to A1 if event policy or source protection cannot be proven. Requires separate credentials, installation and owner approval. Do not deploy as a silent alternative.

**Private App repo:** Stay private and maintain its independent runtime/QA authorities. Neither A0 nor A1 automatically applies to the private app repository. The observed private ruleset 403 is not permission to change plan, expose source, or claim its `main` protected.

**Operational minimum:** Do not require the currently path-filtered Stage3-4/content/ZIP workflow statuses, because unrelated PRs can leave those checks absent. No default required check exists at this time. Rollback must be an approved, auditable admin change, with post-rollback ruleset readback. The connector exposed in this chat does not provide an authorized branch-protection or ruleset-write action. **No GitHub repository settings changed in this optimization turn.**

**Result:** `DECISION_READY_SECURITY_OWNER_APPROVAL_REQUIRED`. This append-only update refreshes the *existing* decision pack and supersedes stale date/status examples in its historical observations, without modifying the original historical evidence. No Stage4/5/6/7 or issuer/writer PASS is claimed.

## 7. 2026-10-31 live direct-writer dependency before A0 activation

**Classification:** New *live GitHub repository evidence*; does not authorize any security setting change, content write, branch rewrite or issuer activation.

### A0 deployment blocker discovered by actual GitHub commit-to-PR association API

The live Content Kit `main` has recently accepted workstream state/receipt commits with **no associated pull request**. We separately checked GitHub's `GET /repos/{owner}/{repo}/commits/{sha}/pulls` for each of these exact commits; all eight responses contained **zero** associated PRs:

| Exact main commit (prefix) | Actual workstream path / role | Associated PR count |
| --- | --- | --- |
| `f37acb7f2` | Menschen A1 consolidation receipt | 0 |
| `6b74d156e` | Menschen A2 current stage4 state | 0 |
| `ea3f53aba` | Menschen A2 stage4 phase21 receipt | 0 |
| `6c27cc001` | Aber Hallo `LATEST.json` | 0 |
| `d3730f9fd` | Aber Hallo WIP75 work outcome | 0 |
| `6e14aa2d6` | Aber Hallo WIP75 checkpoint | 0 |
| `280be93e8` | Menschen A2 source-derived current state | 0 |
| `179bbb100` | Menschen A2 stage4 phase20 receipt | 0 |

Scope: a deliberately selected sample of recent real one-file commits, **not** a statistical census of all writers. The API's empty PR association does not by itself authenticate who held the credential or establish intent. It does establish that the *observed checkpoint persistence path is not via PR*. An immediately **Active** ruleset requiring a PR could reject subsequent direct writes from these currently operating workstreams. That would interrupt durable state sync even though it would not mutate already registered artifacts.

**Revised A0 prerequisite — PR-compatible writer transport before Active:** Identify every affected bot/chat/workstream writer (Aber Hallo, Menschen A1/A2, other content checkpoints) and update their write path to create an isolated branch, upload an exact immutable candidate via GitHub CAS, open a scoped PR, independently read back the candidate file and current main, check head/base freshness, then merge through the permitted path. Preserve concurrent workstream authorities, originals, Library recovery and single-writer discipline. A green untrusted PR-head check or successful merge is **not** source-level owner authorization, Stage4 acceptance or signed CURRENT issuance. Do not create a blanket bypass for existing bot credentials: it would cancel the value of A0.

**Revised A0 recommended sequence:** (i) owner selects explicit target/policy; (ii) audit all actual writers and a no-content synthetic transport pilot *in isolated branches*; (iii) migrate and prove end-to-end one-file checkpoint persistence on ordinary non-release files without disturbing active workstreams; (iv) if this account's UI offers an applicable Evaluate mode for the chosen rules, observe proposed failures before enforcement, otherwise use a **Disabled** draft plus manual read-only comparison; (v) only after explicit separate go-live approval and demonstrated recovery path activate PR-only/anti-force-push/no-delete on exact public `main`. Keep required status checks unset until trustworthy A1 check origin is proven.

**GitHub docs caveat:** Generic ruleset instructions show `Active` and `Disabled` enforcement states, and specifically mention `Evaluate` in some contexts (not guaranteed for this repo/account/rule combination); Rule Insights for an Evaluate ruleset are documented, but do not assert that the user's current GitHub Free UI offers Evaluate for all branch rules. If absent, **never invent an Evaluate switch**. Sources: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository and https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/managing-rulesets-for-a-repository.

**Disposition:** `BLOCKED_ACTIVE_A0_PENDING_WRITER_PR_MIGRATION_AND_OWNER_APPROVAL`. Public Content Kit `main` still unprotected and zero rulesets at last read; private Flashcards Pro stays private; OP01 writer grants stay DENY_ALL, Stage4/5/6/7 remain independent. No repository settings, source, learner data, ZIPs, runtime or Library content changed by this documentation.
