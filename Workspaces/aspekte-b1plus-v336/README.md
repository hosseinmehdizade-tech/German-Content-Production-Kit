# Aspekte B1+ — independent source-only production

**2026-11-05:** Definition **LOCKED v1.0**. User's original CSV is the **only lexical inventory**. Earlier cross-level Menschen material is **read-only duplicate-screening evidence**, not new headwords. No textbook source, cross-level merge, app runtime changes, imported cards, or release promotion.

**Current Stage1:** `SANITIZED_STRUCTURAL_PASS_RAW_ORIGINAL_GATE_OPEN`. A previously hashed sanitized user CSV from the dedicated Library **Source** folder was recovered and revalidated: 1,548 source rows, 1,541 exact distinct German strings, 224 examples, 1,375 audio references, 20 section tags mapping to 10 lessons. The sanitized file SHA256 is `cca32df935397a81367b38f9b51ee33aac357ea135947a131b712969f0339033`. **Original 3,275-row raw CSV bytes are still absent in this run**; the recorded original SHA256 `09478483886661527b24bf00d9c375234d5877ac9189f01f1aa6ec467b85e0f1` was not independently recomputed now.

**Risk triage:** Existing prior-stage provenance-matched audit identifies 99 provisional cases (60 earlier headword possibilities, 29 prior expression mentions, 10 intra-B1+ repeats), not automatic DROP candidates. L01 has 71 exact source-only rows; four earlier-level flags and 25 additional source-level editorial flags, totaling 29 distinct L01 review items. No final KEEP/FIX/MERGE/DROP decisions; every row is **HOLD_PENDING_STAGE2**.

**Verified Library artifact**: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Current/Aspekte-B1plus-Stage1-SANITIZED-PASS-L01-TRIAGE-20261105.zip` (SHA256 `8f4c2b76cbd1c6b8bce66c052e26092bb66b64a70a91478f6d4aa140022636c1`, stable ID `libfile_4a4205185dac8191a9775e42f1313cac`; readback byte equal and all SHA256SUMS validated). Contains the private sanitized source only for the user; **never commit source rows to GitHub**.

**Current gate:** Stage2 semantic editorial verification for 71 L01 source units; raw original SHA/projection must be independently rechecked before full Stage1 acceptance. Stage3–7 NOT STARTED. No import ready claim.

See `Reports/STAGE1-SANITIZED-STRUCTURAL-20261105.json` for metrics and `LATEST.json` for coordinates.
