# Aspekte B1+ — independent source-only production

**Status (2026-11-06): STAGE4 QA Gate2D Part02 — NONIMPORT, NOT RELEASE READY.**
The definition is **LOCKED v1.0**. Only the user's exact B1+ CSV supplies lexical inventory; cross-level Menschen and Aspekte materials are read-only comparison witnesses, never a new B1+ headword source.

## Current verified checkpoint
- Sanitized B1+ source: **1,548 rows across 10 lessons**, SHA-256 `cca32df935397a81367b38f9b51ee33aac357ea135947a131b712969f0339033`.
- All **1,548** source rows have Stage3 DE–FA drafts; all have first-pass Stage4 source/selected-card reviews. This does **not** mean final independent full-card approval.
- **340 distinct HOLD rows** remain blocking. **383 editorial overlays** remain proposed, not formally approved.
- Gate2B/C scoped 90 HOLD rows. Gate2D Parts 01–02 scoped 100 P2 polysemy/comparator rows, for **190 scoped** HOLD rows in total; the next **150 P2** require individual scope checks.
- Gate2D Part02 reviewed 50 new source rows, recorded contextual DE–FA risk notes and **18 additional proposed bilingual examples**. Existing source/candidate payloads were not changed.
- **0 final approved cards.** No import TSV, no publication, Stage5–Stage7 not completed.

## Verified private Library baseline

`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Current/Aspekte-B1plus-STAGE4-FINAL-QA-GATE2D-PART02-100-P2-SEMANTIC-REVIEWS-NONIMPORT-20261106.zip`

- SHA-256: `87e876dc970f689d73f299ddea367e7510dc317634e35b6e2dbd544adfb290c1`.
- The **3,118,714-byte ZIP** contains 385 members including manifest; library readback bytes, CRC, and all 384 SHA-256 manifest entries were independently checked.
- All new detailed private QA reports, 50 bilingual reviews, 340-HOLD crosswalk, 18 additional examples, and checkpoint are inside the ZIP. Separate Library sidecar uploads were **only partially successful** and are not assumed complete.
- GitHub contains only metadata, manifest pointers and receipts; original user CSV rows are **not committed**.

## Unresolved release gates
1. Reverify original combined 3,275-row private CSV checksum (recorded SHA: `09478483886661527b24bf00d9c375234d5877ac9189f01f1aa6ec467b85e0f1`); sanitized source was verified but original raw checksum gate remains open.
2. Use approved **final TSVs in each respective project folder** as comparator authority, plus authoritative C1 evidence where required; don't replace them with original textbook lists. Confirm independent senses, Rektion, separability, and duplicates.
3. Independently adjudicate all HOLDs and editorial overlays; validate front-side full inflections/article/plural and back-side Formen suppression against central presentation contract before making import data.
4. Run independent full-card QA and promotion checks. Never silently DROP a word merely from a headword match.

See [LATEST.json](LATEST.json), [CHECKPOINT.json](CHECKPOINT.json), [Gate2D Part02 receipt](Reports/STAGE4-FINAL-QA-GATE2D-PART02-SYNC-RECEIPT-20261106.json), and [file lifecycle rule](FILE-LIFECYCLE-RULE.md).

**Next:** Gate2D Part03: review next 50 source-ordinal P2 HOLDs, then remaining 100; no import/release.
