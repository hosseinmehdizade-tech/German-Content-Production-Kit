# OP-01 — Docs-only PR probe (2026-10-29)

This intentionally changes **only this Markdown file** relative to the
isolated base branch `ci/op01-always-on-pr-gate-pilot-20261029`.

Purpose: independently verify that the candidate unfiltered
`pull_request` workflow emits a stable, successful
`op01-governance-preflight` check when a PR's **entire diff is documentation**,
not just its newest commit.

No active production policy, security/branch protection settings, writer
scopes, WIP50, source/LOCKED, learner cards, Library or runtime/UI changed.
This is not issuer authentication or Stage4 signoff. The PR must not be
merged into `main` or treated as approval to activate any required check.
