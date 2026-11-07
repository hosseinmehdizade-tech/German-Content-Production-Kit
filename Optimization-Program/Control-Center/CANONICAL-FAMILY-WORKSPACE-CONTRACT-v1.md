# Canonical Family Workspace Routing — Operating Contract v1

**Effective:** 2026-11-07. **Authority type:** non-destructive, prospective management routing. **Applies:** all 21 content families, not app runtime. **Main register:** [CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json](CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json).

## The failure being eliminated

Previously, 36 Git Workspace directories covered 21 content families. Some families had many Workspaces, each with its own Checkpoint or release evidence. For example, Menschen A1 Verben's central pointer incorrectly selected historical Repair4 while the separate Wortfamilie Workspace had the user's already-accepted R10. The correct response is to route **future work to one canonical family Workspace** and retain all historical source-owner receipts, not to delete the legacy lineage or regenerate the content from a textbook.

## Exact operating model

1. **One stable family ID + one Library root per family.** The master catalog owns family identity. The canonical route registry selects **at most one active Git Workspace per family**. The 16 currently represented families have one designated existing Git Workspace each. The remaining five families have no existing Git Workspace and stay Library-only; no empty directory is created by this policy.
2. **One CURRENT source-content authority per family, independent of working folders.** For the ten curated families with a verified accepted source, preserve its source-owner pointer and exact accepted artifact SHA/bytes. These owner Workspaces are the canonical route. Other families get routing only, not a made-up CURRENT, Stage5, Stage6, or release claim.
3. **New source work lives under the selected family's canonical Workspace.** Put task-level branches/working folders, semantic QA, vocabulary/grammar/Lesen/Schreiben, enrichment, and new candidate checkpoints *inside the existing canonical route*. Avoid a new top-level `Workspaces/*-repairN-...` directory.
4. **Compatibility Workspaces remain intact.** The 20 existing noncanonical directories remain on GitHub with existing CHECKPOINTs, reports, and hashes. The routing registry marks them `COMPATIBILITY_LEGACY`, meaning **not the destination for a new family CURRENT owner**. It does not declare all their work obsolete, frozen, archived, or deletable.
5. **New Git workspace for one of the five Library-only families:** only after explicit authorized initiation; the same reviewed change must add a canonical route + catalog identity + exact approval receipt. A new additional/sibling Workspace for a represented family is forbidden. Canonical relocation is an exception requiring explicit user approval, a previous-route handoff and verified CAS/lineage.
6. **Release/current promotion remains separately gated.** This routing contract does not override source owner's curations, latest user-uploaded artifacts, exact SHA checks, Stage4-7 gates, app runtime pin, or FSRS/SRS state. Neither a newer date nor another folder automatically creates a release.
7. **Unmapped sibling detection is fail-closed in CI.** [Tools/validate_canonical_family_workspaces_v1.py](../../Tools/validate_canonical_family_workspaces_v1.py) checks all 21 family identities, all 36 grandfathered directories, catalog/role consistency, canonical uniqueness, ten accepted owner paths and SHA pointers, and actual directory inventory. A newly created top-level directory needs exact authorized migration evidence or CI HOLD. [Workflow](../../.github/workflows/canonical-family-workspaces.yml) runs on relevant PR/push/dispatch for Linux and Windows. No provider tokens or private Library/Drive downloads in CI.

## Deployment stages and safe migration

| Phase | Status | Action |
| --- | --- | --- |
| 1. Identity audit | COMPLETE, routing only | 21 family IDs, 36 mapped Git folders, 16 canonical Git routes, 20 compatibility folders, five Library-only families |
| 2. Prevent recurrence | IMPLEMENTED WITH CI VALIDATION | Route new work into the canonical family and block unregistered new sibling directories |
| 3. Per-workstream referral | PROSPECTIVE | At next authorized source edit or release, read this route, then the exact source-owner LATEST/CHECKPOINT; add an internal sub-workstream rather than creating another top-level folder |
| 4. Physical relocation / archive consolidation | **NOT AUTHORIZED / NOT ATTEMPTED** | Only if independently justified and explicitly approved after enumerating inbound Git/Library/Drive links, manifests, raw bytes/hashes, import scripts, test gates and recovery paths |
| 5. App changes | NONE | The current app ZIP/source/UI and SRS/FSRS remain untouched |

## Distinguishing routing from release evidence

The canonical path identifies **where new family work should happen**, not whether a source, QA or app delivery is FINAL. Source-owned accepted artifacts and family-specific Checkpoints are still authoritative. The dynamic portfolio's ten verified content families remain independently scoped and not tied to an old app version. The parallel-source detector continues to scan grandfathered historical paths to catch the next Repair4/R10-like divergence, but it cannot make another sibling a CURRENT owner.

## Check before any new Workspace

Read `PROJECT-BOOTSTRAP.md`, `PROJECT-STATE.json`, the catalog, the canonical routing file, the family source-owner checkpoint and current accepted TSV/ZIP. Check that all new paths stay under `canonical_git_workspace` if one exists. If not, use the existing Library family root and route the initial Git workspace through an approved identity change. Report genuine uncertainty; do not ask the user to rediscover history and do not silently move or delete existing folders.
