# Aspekte B2 — Projektdefinition v1.0.0 (2026-11-04)

**Status: APPROVED. Production authorized. Stage 1 BLOCKED on original CSV bytes.**

Only the exact user-supplied Memrise CSV `aspekte-b1b2 [5791881]_(3275)(1).csv`, SHA256 `09478483886661527b24bf00d9c375234d5877ac9189f01f1aa6ec467b85e0f1`, defines the lexical inventory. Publisher textbooks and external wordlists MUST NOT be used to add, remove, or validate source coverage. Checkpoints describe **1,726 B2 entries across 10 lessons** (1,720 distinct surface strings, 190 nonempty source examples, zero audio references); these values have **NOT been revalidated in this run** because the CSV bytes were not available.

Keep completely independent B2 IDs, row positions, provenance, QA, Library path, reports and standalone ZIP. No cross-level deduplication with B1+ or C1. Preserve CSV originals immutable; put corrections and enrichments in separate fields with explicit provenance. Never persist personal `Progress` or `Learnable meta` to GitHub/cards. Audio requires real verified files.

Cards: DE front, FA meaning; noun Artikel/Plural, verb morphology/separability/reflexivity/Rektion, two high-quality examples (goal, not fabrication), sense-matched Synonyme/Antonyme, evidence-backed diverse source-first Kombinationen distinct from Rektion, verified typed Wortnetz. Record source disposition KEEP/FIX/MERGE/DROP/HOLD with lineage; do not silently discard any row. Apply current German-Content-Production-Kit v3.3.6 governance, including active source-first Kombinationen and Related Taxonomy policies without changing CSV membership.

Stage1 verify source SHA256 and 7 columns, then filter B2 and reconcile original positions/10 lesson totals; provisional earlier Stage1 is NOT adopted. Stage2 POS/meaning/duplicate audit; Stage3A/B/C enriched content; Stage4 100% structural + high-risk semantic + stratified AI/adversarial QA (no fake human claims); Stage5 lossless import package; Stage6 verify then-CURRENT runtime + actual import/persistence/study (issue #25 cannot be assumed fixed); Stage7 final only after all gates.

**Blocker as of 2026-11-04:** dedicated Library `Aspekte-B2/Source` is empty, Library search returned no CSV, conversation has no CSV attached, old definition ZIP only contains metadata. Therefore 0 original B2 rows were newly processed, 0 cards generated, no importer/test/release. User may supply exact original CSV bytes; verify SHA first.

All changes and outputs scoped exclusively to `Workspaces/aspekte-b2-v336/` and `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/`. No application/runtime or other-project edits.
