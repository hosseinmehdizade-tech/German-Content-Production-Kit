# Aspekte neu C1 — Stage2 Kapitel 1: 20 more source-bound rich drafts (94 cumulative)

Date: 2026-11-23. **Substantive 20-card authoring, not a Stage1 rescan or final Stage4 language approval.**

## Exact inputs and source preservation

- Direct input: current owner `Aspekte-C1-STAGE2-K01-74-RICH-CARD-DRAFTS-20261123.zip` (SHA256 `aaee1d72a94d67b6f3b1af7085c1cd9a538addb31c48237a33ea25d2c93566f1`).
- All **25 previous ZIP member payloads** copied byte-identically. All **74 former card objects** identical in exact parsed JSON value, no rewrites.
- Existing Kapitel 1 queue: **397** source entries, **247** provisional newly learnable headword source IDs. The new batch uses exactly 20 previously `NOT_YET_AUTHORED` `C1_NEW_LEMMA_CANDIDATE` IDs, with **153** provisional candidate IDs remaining.
- Original 3,270 C1 raw source occurrences and prior 435 B1+/B2 lexical routes, 29/8/two-HOLD decision records, and nine earlier source-preserving learner corrections remain untouched. No Stage1 duplicate-screen reruns.
- 10 newly authored IDs from PDF p.2: `C1-P02-E068`, `E069`, `E070`, `E075`, `E080`, `E084`, `E087`, `E088`, `E090`, `E091`.
- 10 new IDs from PDF p.3: `C1-P03-E001`, `E002`, `E003`, `E006`, `E008`, `E009`, `E012`, `E013`, `E014`, `E015`.

## Concrete new German targets

`computerspielsüchtig`, `permanent`, `Computerwissenschaftler/-in`, `Reduktion (auf + Akk)`, `exzessiv`, `Forschungsinstitut`, `Spielcasino`, `Spielsucht`, `spielsüchtig`, `Stoppuhr`, `Topwert`, `überdenken`, `übermäßig`, `unbeschäftigt`, `widerstehen`, `durchschauen`, `Verhaltenstherapie`, `Hektik`, `Videospiel`, `Nutzungsverhalten`.

- **94 cumulative typed Stage2 draft cards** and exactly **376 DE/FA/EN example triplets** (= four distinct complete examples per card), each with typed DE/FA/EN meaning(s) and per-card grammar notes.
- **470** explicit five-right-section dispositions in cumulative cards. Of the **100 new** decisions: **30 VERIFIED_PRESENT with lexical evidence links**, **70 CLOSED_NO_FORCE with explicit non-forcing reasons**. Empty categories are not stuffed with unverifiable relations. One independent Duden-attested phrase is `die Reduktion auf das Wichtigste`; this is not a copied complete example and includes an educational valency explanation and English/Persian translations.
- Stage2 examples are original learning sentences, *not quotations from the published textbook*. The source PDF is provenance for vocabulary identity and source_raw, not proof of authored sentence text.
- Bounded semantic distinctions: `Spielsucht/spielsüchtig` focus on gambling in Duden, while `computerspielsüchtig` targets computer games; do not label frequent gamers automatically addicted. `unbeschäftigt` does **not** automatically mean unemployed. `Nutzungsverhalten` is collective usage-pattern behavior, not a single user.
- **Source typo handled without touching original**: C1-P03-E008 printed `widerstehen, widerstehen, widerstand, hat widerstanden`; Duden confirms the third person `widersteht`. New learner draft uses `widerstehen, widersteht, widerstand, hat widerstanden`, Dativ Rektion. [Duden widerstehen](https://www.duden.de/rechtschreibung/widerstehen).
- Some additional source-grounded lexicographic checks: [Duden Reduktion](https://www.duden.de/rechtschreibung/Reduktion), [überdenken](https://www.duden.de/rechtschreibung/ueberdenken), [Spielsucht](https://www.duden.de/rechtschreibung/Spielsucht), [Verhaltenstherapie](https://www.duden.de/rechtschreibung/Verhaltenstherapie), [Nutzungsverhalten](https://www.duden.de/rechtschreibung/Nutzungsverhalten), [Spielbank](https://www.duden.de/rechtschreibung/Spielbank), [Spitzenwert](https://www.duden.de/rechtschreibung/Spitzenwert), [Übermaß](https://www.duden.de/rechtschreibung/Uebermasz), [exzessiv](https://www.duden.de/rechtschreibung/exzessiv).

## Reproducible check on actual cumulative bytes

Ran the identical official repository `Workspaces/aspekte-c1-v336/04-qa/validate_c1_rich_card.py` **git blob SHA `4c0f613665bf0c0db5df9e353d218ef86490d67d`** against the cumulative 94-card JSON. Result **`STRUCTURAL_PASS_NOT_STAGE4_5_6_7`**, **94 checked, 0 errors, 0 approved cards**.

- Card JSON SHA256: `df39aa9f7823002ac616a5f5173ba7fd96e8dc735e7df5486062e4762231656b`.
- In addition, 80/80 new German examples each visibly include the matching lexeme or its valid inflected form and each has Persian and English translation; 80 unique new German examples. All 74 earlier cards retain their content. This is **bounded preflight, not final Stage4 DE/FA/EN translation/idiomatic approval**.

## Verified owner checkpoint

- New current working ZIP: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-C1/Checkpoints/Aspekte-C1-STAGE2-K01-94-RICH-CARD-DRAFTS-20261123.zip`
- Library file ID: `libfile_a6f849bf0adc8191afdf8a7e1f93afdc`
- ZIP SHA256: `a66887fba07f81d80f9c2e73b81f16ac0581d0cc261f134adc5d21da26d491c0`
- ZIP size: **570,081 bytes**, CRC PASS, 29 members, previous 25 member payloads byte-identical.
- Cumulative latest cards member: `C1-STAGE2-K01-94-RICH-CARD-DRAFTS-20261123.json`.
- Current 397-source queue member: `C1-STAGE2-K01-397-SOURCE-QUEUE-94-DRAFTS-20261123.json`.
- Structural and bounded language receipts are inside same ZIP. The preceding ZIP is retained historically.
- **Stage4 final approved cards = 0. Stage5 import approved = 0.** No release, no PR merge.

**Next action:** Continue Stage2 real authoring from the exact 153 still-unwritten C1_NEW_LEMMA_CANDIDATE source IDs in the saved source queue. Preserve prior 94 drafts and all prior lexical decisions. Use coherent finite batches and the actual validator, then bounded meaning/grammar/collocation checks. Do not build an unbounded renamed Stage4 audit loop.
