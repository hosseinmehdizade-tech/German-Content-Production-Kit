# Aspekte B2 — Kapitel 1 R28, 48 FIX proposals: second-pass semantic audit (2026-11-05)

Only original user CSV supplies lexical membership. Source ordinals 1549–1708, 160 entries. Existing R6 source-bound overlay and R27 48-item matrix re-examined row-by-row.

## Output
- **48/48** FIX candidate rows now have individual DE and FA editorial notes.
- **38** prior generic PENDING rows receive source-specific second-pass notes; earlier **10** targeted entries retained and rechecked.
- Library CSV: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Reports/L01-R28-48-FIX-SECOND-PASS.csv`
- Library ID: `libfile_7d4db28685708191b3ac7aeb467810fc`; SHA256: `9013db832bc3c3ff44949314a2a66abe688952a7940963f6a6456345d97f0209`.

## Corrections requiring attention
1. **#1670 Windeseile:** previous R27 hesitation about `mit Windeseile` was incorrect. Duden attests **both `in Windeseile` and `mit Windeseile`**: https://www.duden.de/rechtschreibung/Windeseile . Preserve both.
2. **#1652 fernliegen:** `liegt fern, lag fern, hat ferngelegen` (not *ist ferngelegen*): https://www.duden.de/rechtschreibung/fernliegen .
3. **#1685 entstammen:** `entstammt, entstammte, ist entstammt`; takes Dativ: https://www.duden.de/rechtschreibung/entstammen .
4. **#1649 Betriebswirtschaft:** field of study is a frequent sense; plural `Betriebswirtschaften` does exist and must not be mechanically marked impossible: https://www.duden.de/rechtschreibung/Betriebswirtschaft .
5. **#1633 Unverständnis:** lack of understanding is not automatically the same as `Missverständnis` (misunderstanding).
6. **#1617 äußerst:** intensifying adverb distinct from adjective superlative `äußerste`.
7. **#1644 Zugewanderte:** substantivized adjective inflection, not fixed noun ending.
8. **#1689 gläubig:** not equal to `leichtgläubig`.
9. **#1706 Scheinehe:** sham marriage not automatically all marriages of convenience.
10. **#1552 auflösen:** correct separable past `löste auf`, not `auflöste` in standard finite main clause.

## Gate status
This is source-bound **AI editorial second-pass**, not independent human or full lexicographic QA. The matrix records source text unchanged, provisional interpretation and no release. Five cross-level accepted-card and meaning identity gates remain #1556, #1575, #1609, #1630, #1671. Stage2 NOT_APPROVED, Stage3–7 NOT_STARTED; final/importable cards = 0. No original, user SRS, lower-level project, or app modified.

Next: (a) independent bilingual full-entry QA with examples for 160 entries, including the 48 FIX rows; (b) resolve exact earlier-level accepted/visible card identity for five holds, (c) formal Stage2 gate before Stage3.
