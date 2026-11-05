# Phase 2 — Policy Dependency and Source Evidence Graph

**Status:** read-only metadata integration candidate. Does not certify a producer, source, linguistic Stage4, delivery Stage5, browser Stage6, or final Stage7.

The existing Phase1 Control Center resolves 21 Library family identities, 34 Git workspace directories and 17 central workstream summary keys. This second phase connects them to the 15 pinned domain policies in the current global registry and exposes **potential impact**, not assumed execution of a policy in any native producer.

## Outputs and source boundaries

- Generator: `Tools/build_project_dependency_evidence_v1.py`.
- Generated dashboard: `DEPENDENCY-EVIDENCE.md` and `DEPENDENCY-EVIDENCE.json` as read-only GitHub Actions build artifacts and job summaries.
- Graph node types: Content family, Git workspace, root summary key, pinned policy.
- Graph relation types: explicit workspace parent; root-summary-to-family; conditional policy impact on a workstream. A policy edge **does not mean its adapter or output is compatible**.
- Metadata evidence per workspace: Git-index blob of local LATEST/CHECKPOINT, declared 64-character SHA256 when present, and references to receipts that may or may not be Git-tracked. Each SHA is **declared but NOT independently read back**. Tracked receipt path is NOT a passed independent Stage4 assessment.
- Policy integrity: all 15 pinned Git policy blobs must match the central registry. A changed policy without a registry update fails closed.
- Content authority: current user-approved source files, portable artifacts, hash-bound receipts, Library data and runtime imports are not available to GitHub CI unless explicitly verified. Never promote this graph to CURRENT or FINAL.

## Run locally

```bash
python -B Tools/build_project_dependency_evidence_v1.py --check --output-dir project-dependency-evidence-output
python -B Tools/build_project_dependency_evidence_v1.py --check --changed-path Prompt/RELATED-SECTIONS-TAXONOMY-POLICY-v1.1.0.md --output-dir project-dependency-evidence-output
python -B -m unittest discover -s Verification/tests -p test_project_dependency_evidence_v1.py -v
```

The changed-path analysis returns only potentially affected workspaces, using declared scope. It never queues destructive edits, rewrites locked content, or changes the established app UI. A single workstream file should affect only that workspace; a change to a central policy returns an applicability-scoped review set.

## QA interpretation

This mission is a **structural integration step**, not 34 workstream real-output acceptance. There are known distinct blockers: historical Menschen B1-L19 contains 145 prose details values incompatible with the neutral Stage5 JSON contract, native generic Vocabulary output is not yet located, and app runtime CURRENT-source mirror gates are separately blocked. The existing Phase1 identified five root checkpoint paths not tracked by Git. None should be silently fixed or marked as source loss.

Future stage: evidence-specific independent attestation of the exact current portable source and real producer output at a named stage, with hashes and scoped decisions. Any repair of source/LOCKED or visible app UI requires its own separate authority.
