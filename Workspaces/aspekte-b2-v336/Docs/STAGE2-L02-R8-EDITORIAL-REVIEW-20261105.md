# Aspekte B2 / R8 – Lesson 02 full first-pass editorial coverage

Date: 2026-11-05. **Only the user's sanitized CSV is the source for lexical membership**; source SHA256 `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`. Exact private seven-column source hash remains only historically attested, not rehashed this run.

## Lesson 02 (Sprich mit mir!) 
108 source rows 1709–1816 with exact original German, Persian, example, audio, tags and ID preserved. R7 prior 35 source-specific editorial proposals read again. R8 evaluated the remaining **73 individually**: 45 KEEP_PROVISIONAL, 21 KEEP_USAGE_NOTE, five FIX_PROPOSAL, two HOLD. Combined: 45 KEEP_PROVISIONAL, 25 KEEP_USAGE_NOTE, 28 FIX_PROPOSAL, nine unresolved HOLD, one MERGE_CANDIDATE. Every class is **provisional** and nonimport.

The R8 five new fixes are #1734 Konzentrationsleistung, #1735 nachweisen, #1754 nichtssagend, #1759 draufhauen, #1791 Probenraum Persian typo. No source field overwritten; all corrected learner explanations live in an append-only overlay.

Four R7 proposals are **amended**, rather than silently overridden:
- #1737 *Sprachenpolitik* — in specialist linguistics it differs from *Sprachpolitik*, covering status and relationships between multiple languages; preserve original lemma. Source: Nina Janich, 2005 (https://edoc.vifapol.de/opus/volltexte/2008/805/pdf/forost_Arbeitspapier_29.pdf), Duden (https://www.duden.de/rechtschreibung/Sprachpolitik).
- #1721 *vorgeben* — sport/handicap sense (granting a head start) is attested in Duden, alongside feigning and predefining; source-context HOLD remains (https://www.duden.de/rechtschreibung/vorgeben).
- #1797 *daherkommen* — literal approach and figurative appearance attested; source-context HOLD remains (https://www.duden.de/rechtschreibung/daherkommen).
- #1794 *Umschulung* — preferential occupational retraining gloss for the source noun; do not assume the source specifically teaches school transfer (https://www.duden.de/rechtschreibung/Umschulung).

Duden confirms *Sprachschatz* as legitimate, synonym of Wortschatz (https://www.duden.de/rechtschreibung/Sprachschatz) and *draufhauen* colloquial strike (https://www.duden.de/rechtschreibung/draufhauen). Dictionaries used only to check user-source entries, never import new lexemes.

**Nine L02 HOLD ordinals:** #1719 wahrnehmen; #1721 vorgeben; #1726 bilingual (paired with #1743); #1727 einsprachig / monolingual; #1742 unterfordern / überfordern (antonyms, not synonyms); #1763 verschuldet comparative; #1795 bewusst genitive and constructions; #1797 daherkommen source context; #1799 gezeichnet sein polysemy. Row 1743 is also a pending *merge candidate*; source IDs must both remain. No merge or suppression executed.

**Lesson01:** five unresolved prior accepted-card identity HOLDs (1556, 1575, 1609, 1630, 1671), 160/160 R6 previous source-bound firstpass reviewed. No actual imported SRS card IDs verified, no suppressions.

**QA:** 39/39 native independent structural tests, including 8 adversarial mutant cases; 13/13 ZIP payload hash checks, ZIP CRC PASS, exact Library ZIP readback and sha256 PASS. Structural tests do NOT constitute exhaustive independent German/Persian semantic QA. No human attestation, no final card, no Import. Stage2 NOT_APPROVED; Stage3–7 NOT_STARTED.

**Library checkpoint R8:** `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Checkpoints/Aspekte-B2-STAGE2-L02-R8-108-FIRSTPASS-4-REVISED-9-HOLD-20261105.zip`. SHA256 `4e70168883eb7b471b5d1cdb1d0a6039570f15967dc826778a73a530051af231`, 471971 bytes, 14 members, stable Library ID `libfile_17d240c80b748191a46028af16d1ee14`. Contains source sanitized CSV, unchanged R7 full parent, full L02 108-row overlay, 73 new individual reviews, 35 challenged prior reviews, reasons in DE and suggested Persian, tests, tools, README and hashes. Only B2 metadata is committed to GitHub, not raw private CSV.

**Next:** focused adjudication of nine L02 HOLDs, linked bilingual/zweisprachig identity, independent semantic QA before Stage2 approval or Stage3.
