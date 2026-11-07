# Legacy Workspace Reference Handoff — audited, not physically migrated

**Scope:** 20 `COMPATIBILITY_LEGACY` directories in the 21-family canonical routing registry. The old folders are **not empty**. Git HEAD tree inspection on 2026-11-07 observed **1,391 tracked files** and **7,735,198 reported Git blob bytes** in those legacy directories (this excludes provider archives, user Library, Drive and raw binary contents not represented in the Git tree).

This is a **dependency analysis and future-work routing plan**, not a deletion plan or a declaration that all older workstreams are finished.

## Mechanism

Run `python Tools/audit_legacy_workspace_dependencies_v1.py --repo-root . --expect-legacy 20` in a full Git checkout. Git HEAD is scanned for tracked file objects and exact literal inbound references to the 20 legacy `Workspaces/<folder>` paths. Results group inbound referers by CI/code, canonical Workspace, another historical Workspace, root startup/state, governance and other tracked text; the canonical work target is read from the pre-existing official routing file, not inferred from a filename. Generated JSON and Markdown reports are written **outside** the Git checkout, uploaded as ephemeral GitHub Actions artifacts in the [Canonical Family Workspace Guard](../../.github/workflows/canonical-family-workspaces.yml) on Linux and Windows.

The tool reports **P0** for code/CI or current canonical inbound references, **P1** for other inbound references, and **P2** for no exact tracked inbound observed. These are **review priorities**, not permissions to delete, move, disable or mark any Workspace stale. Source-owner checkpoints and user-approved final content remain untouched.

## Workstream-safe consolidation rule

At the next authorized edit to a family:
1. Resolve its canonical Git destination from `CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json`; resolve that family's accepted current TSV/ZIP independently from source-owner LATEST/CHECKPOINT and accepted artifact.
2. Read the CI dependency audit for historic paths and its explicit limitations. Preserve source, tests, manifests, hashes, history and older receipts.
3. Put the **new task/work product** inside the canonical Workspace's scoped folder/branch. Inbound links to the old immutable history may remain valid; do not alter them merely for aesthetic folder uniformity.
4. If a true historical code/path refactor is needed, first collect exact owner change and reviewer approval, update old and new link(s) in one atomic PR, prove both lineage and tests, and retain a reversible compatibility alias/receipt. No moving 1,391 old tracked files merely to reduce folder count.
5. New accepted current artifacts must have independent source-specific acceptance and byte evidence; never infer from Git file date, filename or ZIP CRC alone. App runtime, installed-card identity, user SRS/FSRS and visible UI remain independently protected.

## Current completion boundary

- **Completed:** one canonical destination for each of 16 Git-represented content families; 5 Library-only families; automatic no-sibling-Workspace guard; Git tracked-file inventory baseline; read-only exact inbound reference audit.
- **Not completed / not claimed:** raw private provider dependency search; binary archive nested-path scan; runtime import regression for source-specific paths; physical historical file move; legacy directory deletion; source owner relocation or release promotion.

**Policy:** No safe-delete recommendation can be derived from absence of a literal tracked Git reference.
