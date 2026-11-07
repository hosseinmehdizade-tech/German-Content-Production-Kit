# Dynamic Content Portfolio — Operating Contract v1

**Program:** Continuous Optimization Program / Project Control Center. **Scope:** the 10 user-selected content families, as a subset of the existing 21-family catalog. **As-of seed:** 2026-11-07.

## Purpose and authority
The adjacent `DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json` is the compact **observed, read-only management index** of the curated accepted/usable content per family. It is **not** the new source of truth for a TSV, a semantic acceptance, a release, a Library file, an app runtime, or learner FSRS/SRS. Resolve the live source-owner LATEST/CHECKPOINT, user-approved exact TSV/ZIP, current Library/Drive bytes and app runtime pin independently. A newer accepted user artifact outranks stale Git. The seed records source-reported prior hashes, **not** new independent byte verifications. For B1, last known Stage5 is deliberately not labeled accepted Final.

## Dynamic update contract
1. On each **new source review, enrichment, released successor, user acceptance, or explicit Control Center audit**, read the active repo bootstraps, central policy registry, project catalog, source-owned LATEST/CHECKPOINT, and its most recent accepted curated TSV/ZIP. Reconcile Library/Drive evidence; flag missing or moved files. An opened chat must re-resolve; old open chats are not updated in real time.
2. Separate `candidate`, `working`, `user_accepted_with_exceptions`, `content_final` and `runtime_final`. A new ZIP/date alone is **not** a promotion. Verify actual user acceptance or applicable gates, exact SHA, cards, source and stable IDs before updating the selected baseline. Never change another family.
3. **Compare-and-swap**: record expected immediate parent artifact SHA and Git owner-LATEST blob at the beginning of a change. Before publication re-fetch both; if either changed, **HOLD_CONCURRENT_UPDATE**, reconcile (never overwrite). For a new accepted baseline, append a small promotion receipt with `family_id`, `parent_sha256`, `successor_sha256`, `evidence`, `decision`, `date` and update only that family's entry.
4. Measure **delta** from the immediate accepted curated TSV, not the months-old publisher source. Review changed IDs, semantic dependencies and required structural/runtime gates; reuse still-valid evidence for unchanged rows. Never repopulate removed vocabulary for publisher fidelity.
5. If source Git LATEST is older than an accepted Library/Drive release, show `STALE_OWNER_POINTER`, do not downgrade. If current artifact cannot be verified, `HOLD_AUTHORITY_UNRESOLVED`. Do not substitute original PDFs.
6. Track content semantic/Stage4, packaged/Stage5, actual app import and persistence/Stage6, content-only Stage7 and **full runtime FINAL independently**. User-reported browser success is not independent native verification.
7. This is **event-driven on the next authorized tool run**, not an autonomous background sync. A true scheduled watcher or CI-driven reconciler requires separate implementation and appropriate GitHub/Library permissions. Do not claim live automation from this file.
8. Keep historical accepted releases immutable and retain source-specific checkpoints. Do not delete Library/Drive files without explicit separate scope approval. No app UI, import, SRS, source or flashcard mutation from registry maintenance.

## Expansion and anti-churn
Use stable `family:<slug>` identifiers from `MASTER-PROJECT-CATALOG-v1.json`. New families (Aspekte, Grammar, Lesen/Schreiben) are added only after identifying their exact curated authority; do not manufacture CURRENT. Refresh a record on an actual decision/delta, not cosmetic report cycles. Compact `STATE.json` and the root catalog remain separate from the 10-family registry. No extra release ZIP is warranted.

**Initial inventory:** 10 families, 12,605 card records including cross-family overlap (unique deduplicated count unknown). The initial seed contains *no* source card edits and *no* native Stage4–7 acceptance promotions.
