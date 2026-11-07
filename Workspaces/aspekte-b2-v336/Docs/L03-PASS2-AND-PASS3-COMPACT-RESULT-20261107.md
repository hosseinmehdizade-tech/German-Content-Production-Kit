# Aspekte B2 – Kapitel 3 · PASS 2 / PASS 3: quality and disposition

**Date:** 2026-11-07. **Owner:** Aspekte B2. **Source of truth:** R17 owner-curated lesson 3 and immutable 186-unit Pass-1 draft, not old textbook. **Status:** editorial QA completed; **BLOCKED / NONIMPORT** for actual final release. PASS 2 and PASS 3 are the remaining two of the user-mandated maximum three substantive passes.

## Verifiable work

- **186/186 draft learner unit IDs** preserved from PASS 1; 186 original curated source rows represented via 185 directly keyed ordinals, plus unchanged alias #1921 for the duplicate *Datumsangabe*. Ordinal #1933 legitimately maps to two independent words *Projektleitung* and *Projektmanagement*; original source and source-ID lineage retained. No auto-merge or learner SRS modification.
- **372 German–Persian example pairs** retained; all 186 card fronts, backs, 372 pairs and language-alignment reviewed in one AI editorial round. This is **NOT** an independent second-model or human verification and cannot be used as Stage-4 sign-off.
- A serious omitted-enrichment problem was fixed: all **186 cards now have three carefully proposed German collocations each (558)**, rather than zero; **70** units have sense-qualified synonym candidates and **28** have conditional antonym candidates. No fake antonym quota, no graph-target IDs invented, and these new additions are AI editorial proposals, not `SOURCE_EXACT` quotations or independently validated dictionary lists.
- **27 learner-visible field changes across 19 distinct units**: corrected noun semantics for *die Mode*, lexical-target consistency for *die Wette* and *locken*, multiple accepted senses for *betreiben*, *beschäftigen*, award-sense illustration of *dekorieren*, `drauf` colloquial sense, split vs non-split verbs, Persian alignment and morphology. The old French draft provenance annotation was normalized in 183 cards; preserved special-case notes for #1921/#1933/#1991.
- Duden-confirmed spot checks: *Mode* noun and plural; *umgestalten* `gestaltete um/hat umgestaltet`; *Anbau* plural `Anbauten` only for extension sense; *gliedern* dynamic accusative `in + A.`; *Arbeitsmarkt* plural `Arbeitsmärkte`; *rudern* `hat/ist` depending on usage; *dekorieren* can also mean award an order. Not a claim that Duden independently certified all 186 cards.

## Cross-level identity gates (actual user-curated current/final, NOT original inventories)

| B2 ordinal | Headword | Other project verified current content | Gate |
|---|---|---|---|
| #1905 | Geschäftsleitung | Menschen B1 user-accepted content `mb1m-lu-1488` | Avoid duplicate: identity/reuse needs live-app SRS verification |
| #1958 | umfangreich | Menschen B1 user-accepted content `mb1m-lu-2812` | Same accepted lexical target; do not create duplicate card without decision |
| #1833 | Arztpraxis | Menschen A2 latest content-only `ma2m-lu-0500` | Reuse only if actually imported; otherwise B2 fallback |
| #1964 | Anschrift | Menschen A2 latest content-only `ma2m-lu-1516` | Reuse only if actually imported; otherwise B2 fallback |

The B1 and A2 current ZIP hashes and their single accepted canonical TSV hashes were actually read and matched. A2's current package remains content-only; there is no observed proof of the user's active per-card identity. Full cross-level coverage of all historic decks was not claimed; only these exact/normalized verified overlaps are recorded.

## QA and pass-3 truth

- `Current/L03-PASS2-186-CURATED-REVIEW-NONIMPORT.csv` SHA256 **`c0cfeffa7b1b678336c42b3f8b226d2e2410a643455bf43d10bea71c4bcbd576`**; stable distinct IDs 186, cards with three collocations 186, preserved 372 paired examples, all `export_importable=FALSE` and `linguistic_release_approved=FALSE`; unchanged parent hash `b72509b2fb934ea8c0278e64760135e43f8ee0a31ee9a712697512a2c426078d`.
- `Reports/L03-PASS2-AND-PASS3-DISPOSITION.json`: single QA receipt with all **27** concrete before/after field corrections, source/current hashes and release blockers; no repeated small rounds or extra portable ZIPs.
- **PASS 1 COMPLETE DRAFT → PASS 2 COMPLETE AI EDITORIAL (independent QA unverified) → PASS 3 BLOCKED / NONIMPORT.** Formal Stage 4 independence, Stage 5 direct-import, native Stage 6 and final Stage 7 are **NOT PASSED**. Published/importable B2 cards: **0**.
- Do not create a fourth incremental micro-pass. Keep the exactly scoped blockers for future independently verified evidence and continue to **Kapitel 4, PASS 1/3**. The user's three-pass execution rule is not a license to skip validation or to claim fake release acceptance.

## Public lexical evidence (targeted only)

- https://www.duden.de/rechtschreibung/Mode_Stil
- https://www.duden.de/rechtschreibung/umgestalten
- https://www.duden.de/rechtschreibung/Anbau
- https://www.duden.de/rechtschreibung/gliedern
- https://www.duden.de/rechtschreibung/Arbeitsmarkt
- https://www.duden.de/rechtschreibung/rudern
- https://www.duden.de/rechtschreibung/dekorieren