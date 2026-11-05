# Aspekte B2 — Stage2 L01 first-pass editorial completed, gate NOT passed
2026-11-05

User CSV is the **only lexical inventory**; no publisher book and no new external wordlist. The exact B2-only sanitized CSV SHA256 is `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`, while original private CSV SHA `09478483886661527b24bf00d9c375234d5877ac9189f01f1aa6ec467b85e0f1` is **historic only** and not rehashed in this pass.

**Lektion 01 / Heimat ist …:** all 160 user-CSV rows editorial-reviewed (31 prior + 129 newly reviewed). The 129 new proposals are 93 KEEP, 33 FIX, 3 HOLD; final combined disposition: 96 KEEP family, 48 proposed FIX, 11 HOLD, 4 provisional earlier-level duplicate suppressions, 1 within-level merge preserving 1640+1641 source IDs. 0 final cards and no import or runtime updates.

**Eleven HOLD ordinals:** 1586 (two forms one cell), 1588 (near synonyms), 1610 (different frames), 1611 (added Rektion value), 1616 (prior lemma plus phrase), 1647 (Ausländerquote share/quota ambiguity), 1660 (isolated participle gekommen), 1671 (old-level sense), 1675 (einig valency), 1693 (Juryvorsitz reading), 1697 (Kinokasse from prior combination). No automatic deletion or forced decisions.

**Quality:** byte-exact Library archive readback PASS; ZIP CRC and 15/15 SHA256SUMS checks PASS; 31/31 independent structural tests PASS. This is not equivalent to independent human semantic QA or Stage4. Learner-facing content still unapproved. All source originals, legacy 31 decisions, IDs, examples, level tags and source provenance unchanged.

Examples of source-bound corrections: `auswandern`: `ist ausgewandert` (https://www.duden.de/konjugation/auswandern); `sich einleben`: `hat sich eingelebt` (https://www.duden.de/konjugation/einleben); `Chancengleichheit`: equal opportunities (https://www.duden.de/rechtschreibung/Chancengleichheit); `jeglich` needs inflected determiner (https://www.duden.de/rechtschreibung/jeglicher). Dictionary evidence does NOT add lexical inventory.

**Portable ZIP stored only in B2 Library:** `Aspekte-B2-STAGE2-L01-160-REVIEWED-11-HOLD-20261105.zip` SHA256 `769a2ff6376021edeae450a50534899b4ed5d071e7b477f1c93948f430a00e85`, 135057 bytes, 16 members, `libfile_ea7f75089fa08191a2c1934ba573a46f`. Full detailed 160-row decision ledger and build/test artifacts are in ZIP/Library; GitHub contains only metadata, checkpoint and report, not the private raw CSV.

**Next:** resolve 11 HOLD cases plus 4 prior-level suppression proposals; independent adversarial review of high-risk language; Stage2 gate remains NOT_APPROVED; Stage3–7 not started.
