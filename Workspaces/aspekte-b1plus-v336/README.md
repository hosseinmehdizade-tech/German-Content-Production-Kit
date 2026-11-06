# Aspekte B1+ — independent source-only production

**Current: 2026-11-06, Stage4 QA Gate2D Part03 — NONIMPORT / NOT RELEASE READY.**

Definition **LOCKED v1.0**. Only the user’s exact B1+ CSV supplies vocabulary rows. Other German projects are read-only duplicate/comparator witnesses, never sources of new B1+ headwords. Do not use the old coursebook vocabulary as authority for this project.

## Current verified content state

- **1,548 source rows across 10 lessons**; sanitized source SHA-256 `cca32df935397a81367b38f9b51ee33aac357ea135947a131b712969f0339033`.
- All 1,548 rows have nonimport Stage3 DE–FA drafts and first-pass Stage4 source-focused editorial review. This is **not** final independent QA.
- **340 HOLD rows**, all remain release-blocked. **383** prior source-preserving editorial overlays proposed, none formally approved.
- Earlier Gate2B/C **90** scoped HOLDs; Gate2D P2 **150/250** meaning/comparator rows individually scoped and reviewed, 100 remaining. Combined **240/340** distinct HOLDs scoped, none released.
- Gate2D Part03 (new 50 source-ordinal-sorted cases, ordinals 701–1035) includes 50 individualized bilingual semantic assessments, 15 proposed DE–FA example pairs and a 340-row HOLD crosswalk.
- Targeted crosslevel comparison from **actual final project files**: Menschen A2 release TSV with 1,778 rows and Menschen B1 released TSV with 3,089 rows. The latest B1 current-merged TSV (3,088 rows) was additionally inspected, yielding the same narrow exact-lemma match in this set. These string matches **do not establish semantic duplicates**. A1 and C1 primary final-file comparisons remain open.
- No changes to the sanitized original, parent source rows or previous Stage3 draft members. No source rows committed to GitHub.
- **0 final approved cards; no import-ready TSV; no release.**

## Library baseline (verified with byte-exact readback)

`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Current/Aspekte-B1plus-STAGE4-FINAL-QA-GATE2D-PART03-150-P2-INDIVIDUAL-REVIEWS-NONIMPORT-20261106.zip`

- SHA-256: `c26c093d3d58bdc0c370cc8a2b538bce6cc8b450b72c0f533c34181885c55202`.
- 3,167,467 bytes, 394 ZIP members, 393 verified SHA-256 manifest entries, successful CRC check, 384 previous parent content members preserved.
- Detailed editorial notes, proposed examples, final TSV narrow comparator checks and checkpoints are **inside the verified private ZIP**. GitHub is a metadata/receipt layer, not storage for private original vocabulary content.

## Release blockers

1. Validate the original combined private CSV binary SHA (recorded `09478483886661527b24bf00d9c375234d5877ac9189f01f1aa6ec467b85e0f1`). The sanitized file was validated; original raw 3,275-row input check remains open.
2. Compare against actual approved final TSVs in the right project folder for Menschen A1/A2/B1, Aspekte where relevant; finish independent evidence/sense/rection comparisons. Never auto-DROP solely on identical lemma.
3. Complete next 100 ordered Gate2D P2 reviews, adjudicate all HOLDs, review all 383 overlays.
4. Verify front-side morphology (verb inflections, noun article and plural, adjective forms) and conditional suppression of duplicate back-side `Formen` under the centralized presentation standard; run independent full-card QA.
5. Only then generate/validate an app-compatible final TSV, Stage5–Stage7 and release.

See [LATEST.json](LATEST.json), [CHECKPOINT.json](CHECKPOINT.json), [Gate2D Part03 receipt](Reports/STAGE4-QA-GATE2D-PART03-METADATA-RECEIPT-20261106.json), [safe cleanup contract](FILE-LIFECYCLE-RULE.md).

**Next:** Gate2D Part04 (next 50 P2 records), then final 50; no publication.
