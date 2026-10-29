# OP-01 — Reproduced PR-head status spoof in untrusted workflow

**Date:** 2026-10-29 · **Severity:** blocker to promoting candidate OP-01 pilot as a required security check · **Scope:** isolated test branches only. No content, original/LOCKED, LATEST, writer-scope grants, GitHub branch settings, application or UI modified.

## Starting point

The prior [pilot PR #31](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/31) added an always-emitted `pull_request` job with fixed name `op01-governance-preflight`, `contents: read`, and script checking `Optimization-Program/WRITER-SCOPES.json` is still `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL` with `scopes: []`. A [true docs-only nested PR #32](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/32) showed this job runs when the PR diff is only Markdown ([run 40954741660](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40954741660), SUCCESS and real DENY_ALL marker).

**That positive test verified triggering, not workflow integrity.** A `pull_request` workflow can execute a PR-authored workflow variant and report a green job with the same check name even if the security logic has been removed. An unprotected base branch plus a success-only status is not independent issuer authorization.

## Executed adversarial GitHub Actions integration probe

1. Branch `ci/op01-untrusted-pr-workflow-spoof-probe-20261029` forked from isolated candidate base `ci/op01-always-on-pr-gate-pilot-20261029`. Its only changed file was `.github/workflows/op01-always-on-pr-governance-pilot.yml`.
2. Kept workflow and **job name** `op01-governance-preflight` unchanged; replaced its policy-validation step with benign `echo` lines. It did **not** change `WRITER-SCOPES.json` or grant permissions. Source commit `c2aeb4fe30e47cb0150aa828472af92961e8c1b5`.
3. Opened [isolated Draft PR #33](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/pull/33) targeting the candidate branch (never targeting `main`).
4. [Exact GitHub Actions run 40955556999](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40955556999), real job `123734620908`: `op01-governance-preflight` **SUCCESS**.
5. Independently read the actual job log:
   - `OP01_WORKFLOW_BYPASS_PROBE_NONAUTHORITATIVE` **present**.
   - `This green job deliberately DID NOT validate DENY_ALL.` **present**.
   - `PASS_NONACTIVE_OP01_DENY_ALL_STRUCTURAL_ONLY` **absent**.
6. PR #33 was **CLOSED UNMERGED** immediately after the proof; pilot PR #31 was also **CLOSED UNMERGED** as unsafe to promote unchanged. PR #32 was already closed unmerged.

**Result: `VULNERABILITY_REPRODUCED_SCOPED_PR_HEAD_CHECK_SPOOF`** — the green status of the candidate cannot be treated as trusted enforcement. This proof does not mean current real production data was altered or that an external attacker controlled the repository. It demonstrates the CI trust boundary under an isolated PR-head simulation.

## Required design corrections (no permission changes made)

- Do **not** merge the current `pull_request` candidate or require its `op01-governance-preflight` status.
- Introduce a trusted execution boundary: for example, a carefully scoped `pull_request_target` workflow **defined on protected, trusted default branch**, with `permissions: contents: read` only; do not checkout, run scripts from, download-and-execute, or use untrusted PR-head code. Evaluate only PR metadata and/or untrusted content as data with strict parsing. `pull_request_target` itself is not a safe shortcut; execute arbitrary PR code or expose privileged tokens and it becomes dangerous.
- Alternatively use an independently protected external verifier/check-app whose status origin is pinned and whose configuration a PR author cannot edit, and enforce restrictions on workflow changes via reviewed CODEOWNERS/path protection.
- Before requiring a check: make it emit on **every** PR, validate docs-only and hostile workflow-change PRs, verify required-status **origin**, CI concurrency behavior, bypass exceptions, and an owner recovery procedure. Existing path-filtered workflows must not be blindly required.
- Separately enforce branch protection/rulesets (public Content Kit main currently unprotected) with no force push/deletion, PR review policy compatible with the solo-owner workflow, controlled overrides, and **explicit user approval**. The private App repo has a separate plan/feature limitation; do not make it public or upgrade automatically.
- Green CI, GitHub-signed squash merges, content hashes, or a self-authored receipt **still do not** authenticate the exact CURRENT promotion issuer. The Stage4 independent method, source evidence, signed/approved target, Stage5 four-role integrity and Stage6/7 runtime acceptance remain separate gates.

## Durable state boundary

`Optimization-Program/WRITER-SCOPES.json` on **main** remains `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL` with zero scopes. `Workspaces/aber-hallo-listen-tabellen/LATEST.json` and original cards unchanged. Existing WIP50 source+portable byte proofs remain scoped PASS, historical unsigned worksheet still stale with 0 independent reviewer decisions, no production Stage4/5/6/7 approval.

**Next step:** an actual security architecture choice and protected trust root are required. This document does **not** activate rulesets, required checks or a successor security workflow. The prior pilot's technical trigger proof remains historically valid but its promotion recommendation is explicitly superseded by this red-team result.
