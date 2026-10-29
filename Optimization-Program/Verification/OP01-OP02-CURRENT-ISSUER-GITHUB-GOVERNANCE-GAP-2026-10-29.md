# OP-01 / OP-02 — CURRENT issuer authorization and GitHub enforcement audit

**Observed:** 2026-10-29. **Scope:** READ-ONLY factual governance inspection + proposed plan; NO branch or ruleset changes, no writer grants, content workstream edits, signer enrollment or release. This is **not** an approval for a production migration.

## Real API observations (not synthetic results)

| Gate / evidence | German-Content-Production-Kit | German-Flashcards-Pro |
| --- | --- | --- |
| Repository visibility | `public` | `private` |
| Default branch | `main` | `main` |
| `GET /branches/main` `protected` | **false** | **false** |
| `GET /branches/main` `protection.enabled` | **false** | **false** |
| `GET /rulesets` | HTTP 200, empty `[]` | HTTP 403, `Upgrade to GitHub Pro or make this repository public to enable this feature.` |
| Connector `GET /branches/main/protection` | HTTP 403 `Resource not accessible by integration` | not retried; branch summary already reports no protection |
| Repository owner/admin identity | `hosseinmehdizade-tech` | `hosseinmehdizade-tech` |
| Direct WIP50 `LATEST.json` promotion commit | `1f94eac9e4038bdfa30a1a343edcab402997288a`: `verification.verified=false`, `reason=unsigned`, `signature=null` | not a content authority |
| GitHub web-flow PR #30 squash merge commit | `00e0525ba64b2ac13f2f3f9d2f3f6d749f9d962e`: `verification.verified=true`, `reason=valid`; committer `web-flow` / GitHub signature | n/a |
| Independently submitted approvals on OP-02 PRs #27–#30 | all `reviews=[]` from GitHub API | n/a |

**Important distinctions:** A GitHub-verified signature on a merge commit attests the GitHub signing mechanism; it is NOT proof of independent user authorization of a named CURRENT. A self-declared CAS title also is not independent enforcement of CAS. A bare Git author/committer username is not an independent trusted issuer. The WIP50 actual binary/source-chain and ancestry evidence remain scoped PASS but do not cure this governance gap.

**Account/feature context:** GitHub documents branch rulesets/protected branches for public repositories on Free, and private repositories on Pro/Team/Enterprise. The actual private repo rulesets endpoint returned a paid-feature 403; **do not assume private protection has been enabled**. Current GitHub App integration can inspect public rulesets and branch summary but cannot query admin-protected branch detail; its authorization is separate from account admin UI settings.

## Why blindly requiring current CI as a branch protection check can deadlock

Existing `.github/workflows/stage3-4-compatibility.yml`, `content-zip-guard.yml`, and `content-quality-v3.1.11.yml` use `pull_request.paths` filters. They only run on relevant path changes. A blanket `required_status_checks` rule naming these checks could leave unrelated PRs waiting for a skipped workflow indefinitely. First create a **minimal always-on, stable-named governance status gate** (on every PR to `main`) or restructure the existing workflows to ensure each required check always reports, then test an unrelated documentation PR. This is a distinct CI/branch-policy architecture change and requires explicit approval.

## Proposed protection contract (approval-gated, not applied)

1. **Public Content Kit (feasible on current public visibility):** after checking CI names and tool compatibility, enable a main-branch ruleset or branch protection to block force-push/deletion, require PRs, prohibit bypass when practical, and require **only always-emitted, stable CI checks**. Scope any exceptions narrowly. Keep `OP01/WRITER-SCOPES` at DENY_ALL regardless of green checks.
2. **Signed commits:** first test actual GitHub-connector direct edits, local Git signing and squash merges on an isolated branch. The real WIP50 direct commit is unsigned but recent GitHub-generated squash merge is verified. Requiring all future commits signed immediately would block current unsigned direct-write automation. Do not activate until compatible signing method and recovery workflow are tested.
3. **Independent approval:** one approval from a reviewer independent of author/automated producer would meaningfully strengthen release authorization. A solo repository owner cannot self-approve their own PR in GitHub; do NOT turn on a required human review that makes the current single-user workflow permanently unmergeable unless a real eligible reviewer and escalation path exist. Alternatively retain PR+CI for maintenance but keep **production CURRENT independently approval-gated outside that channel**, with a specifically authenticated/verified user-decision record bound to exact workstream, exact SHA-256, target Git commit and expiry. A self-authored JSON `approved=true` is not that record.
4. **Private app repo:** do not change visibility, subscription, billing, repo structure or permission policy silently. Choose paid branch-protection capability vs a separate signed release-verification route only after explicit user choice. Visibility change would be significant and is not a workaround applied here.
5. **Promote-current contract:** even after repository protection, continue to demand independently pinned current Git commit + hash, exact role/input provenance, semantic Stage4, Stage5 clean builder, Stage6 runtime import and Stage7 acceptance. Independent promotion/release permission must be tied to the exact target, not the color of unrelated CI.

## State/decision boundary

**Outcome:** `GOVERNANCE_GAP_CONFIRMED_READONLY`; `NO_INDEPENDENT_ISSUER_AUTHORIZATION`; `NO_PRODUCTION_PROMOTION`. This audit makes a formerly inferred blocker demonstrable with real API response fields. **No security configuration has been changed** and no impact on production content, Library, Git writer scopes or v486-R120 runtime/UI has been introduced.

**Next required decision (real architecture/permissions):** user selects whether to introduce a public Content Kit main-branch ruleset and whether to fund private app branch protection or instead use a separate externally authenticated release approval process. After approval, pilot with one reversible workflow and observe CI/no-bypass behavior before adoption. Do not interpret a generic `continue` as authorization to make this permission change.

Sources: GitHub API `https://api.github.com/repos/hosseinmehdizade-tech/German-Content-Production-Kit/rulesets`, `.../branches/main`, `.../commits/1f94eac9e4038bdfa30a1a343edcab402997288a`, `.../commits/00e0525ba64b2ac13f2f3f9d2f3f6d749f9d962e`, `.../pulls/30/reviews`; App `.../branches/main` and `.../rulesets`; [GitHub ruleset availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), [protected branch options](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
