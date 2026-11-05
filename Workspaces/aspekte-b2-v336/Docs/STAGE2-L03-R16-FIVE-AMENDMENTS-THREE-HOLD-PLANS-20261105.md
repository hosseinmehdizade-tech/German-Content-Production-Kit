# Aspekte B2 — R16 L03 targeted AI second-pass challenge

**Date:** 2026-11-05. Scope: Lesson03 all **45 FIX** first-pass proposals, **three HOLD source identity cases**, plus **18 individually selected KEEP/usage** cases, total **66/186 source rows**; **120 rows still pending second-pass**. Every reviewed row has its original German headword, Persian definition, exact source example, proposed Persian learner meaning and case-specific German rationale in the B2-only Library JSONL.

**Five consequential amendments to R15**, not silent overwrites:
- #1847 `umgestalten`: separable `er gestaltete um`, `hat umgestaltet`; avoid `umgestaltete` as independently valid finite simple past. Duden https://www.duden.de/konjugation/umgestalten
- #1850 `Bürokauffrau, -en`: show full learner plural `Bürokauffrauen` while acknowledging original `-en` is legitimate suffix shorthand, not necessarily a false plural.
- #1906 `nahegelegen`: source spelling is legitimate alongside `nahe gelegen`, physical proximity; `naheliegend` is a distinct *plausibility* sense (though spelling compounds can overlap). Duden https://www.duden.de/rechtschreibung/nahe_gelegen and https://www.duden.de/rechtschreibung/naheliegend_einleuchtend
- #1907 `rudern`: both `hat gerudert` and `ist gerudert` can occur with different usage. Duden https://www.duden.de/konjugation/rudern
- #1976 `avancieren zu + Dat.`: `ist avanciert`, not necessarily `hat avanciert`; Duden https://www.duden.de/konjugation/avancieren

**Three former HOLDs:** #1921 Datumsangabe exact duplicate #1920 proposes one eventual pedagogical unit mapped to two different source IDs; #1933 contains both `Projektleitung` and `Projektmanagement` in one CSV cell, propose distinct teaching targets under one source ordinal, without falsely declaring absolute job separation; #1991 corrupt `respektvoll` source headword includes a TAB plus duplicated text, propose display normalization only. No merger, source deletion or new card performed.

**Boundaries:** exact user CSV sole lexical authority; sanitized B2 source SHA256 `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`, original seven-column raw SHA historical only. Immutable R15 parent ZIP is included. No publisher content incorporated as inventory. Source examples reproduced verbatim; **zero AI-authored examples** generated. No human language review claim, no final imported card, no other workspace changes, no SRS mutation.

**Technical checks:** 186/186 CSV ordinal/DE/FA/audio/example/tag exact identity matches, all 66 case records anchored to source IDs, 10 intentional corruptions rejected, nine manifest hashes verified, ZIP CRC passes and Library re-download byte-exact SHA256 `f6f8c0f8dae042b9b0ff25e815af8bcbb53e8f25f89e7e4c1d53b22ce643c6d8`. Portable verifier runs via `python Tests/test_r16_invariants.py .` from a fresh extraction. Tests confirm *structural provenance* only.

**Archive:** `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Checkpoints/Aspekte-B2-STAGE2-L03-R16-66-TARGETED-SECOND-PASS-3-HOLD-PLANS-20261105.zip` (1368964 bytes, 10 ZIP members), stable Library `libfile_6196360b87a08191b9f508df123cfd3a`.

**Stage2 NOT APPROVED.** L03 has 120 second-pass rows remaining, L01 five actual prior accepted-card identity gates, L02 bilingual/example release gate. Stage3–7 NOT_STARTED.
