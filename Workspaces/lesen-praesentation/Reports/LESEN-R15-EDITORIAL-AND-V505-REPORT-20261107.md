# Lesen R15 — 25 topic-grounded concluding sentences in 14 lessons

**Date:** 2026-11-07  
**Owner:** `Workspaces/lesen-praesentation`  
**Status:** SOURCE-SCOPED CANDIDATE; not CURRENT, not final, Stage4/6/7 HOLD.

## What actually changed

- 14 lessons: LES-PRES-011…024; 25 sections (14 p02 plus 11 p03).
- Replaced **25 copied generic German conclusions** with unique, topic-specific consequences supported by each section's first two unchanged sentences. Wrote matching Persian and English concluding sentences. Their first two sentences in DE/FA/EN remain verbatim, as do all 54 untouched lessons.
- Retired **78 now-invalid old full-text grammar spans** tied to removed German sentences; no new grammar occurrences invented or bulk regenerated. All **4,220** remaining spans match their exact source offsets. Nine existing curated Relativsatz examples were legitimately retargeted to *new sentences with real relative clauses* and explicitly marked editorially retargeted.
- All 68 original IDs, 340 Q/A identities, 350 vocabulary and 669 curated grammar ID records remain stable.

## Results

| Test | Result |
|---|---|
| Independent read-only source/runtime checks | **12953 / 12953 PASS** |
| Corruption/negative tests in independent QA | **9 / 9 correctly rejected** |
| Exact CURRENT v505 reading import source validator | **PASS, zero errors and zero warnings** |
| Native source corruption controls | **7 / 7 rejected** |
| In-memory record projection | **68 reading units / 340 exercises PASS** |
| Library checksum/readback | **PASS, SHA-256 and byte-exact readback for both files** |

## Remaining content work

**41 p02** and **30 p03** identical generic conclusions remain (71 *sentences*, not 71 lessons); semantic/discourse QA remains larger than the template clean-up. The separate p04 template opening clean-up is completed in the previous R13.

## Boundaries

The actual historical 9-lens German grammar engine was **not rerun**. Native browser/IndexedDB import and preservation (Stage6) **not run** due to environment restrictions. Cross-content independently verified DE–FA–EN linguistic Stage4 **HOLD**; Stage7 **NOT RELEASED**. The curated v1.3.0 delivery ZIP remains immutable CURRENT, and no user study data, UI, or SRS/FSRS were touched.

Master SHA256: `efa0fa9ece712f3a045ef47c802efe9230fe1baa366cb43e7f3ba5a8573e4c67`  
Runtime SHA256: `52b0d807bf1c9ab6dbc80011ddb98d131594ebdb4544981a8d0a1c9c22489e33`  
Parent R14 master: `40f4eee25d4ea541d33f91f327bc88243ec5e2971419927ae43c2f0035af2568`.