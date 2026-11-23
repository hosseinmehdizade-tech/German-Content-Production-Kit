# Aspekte neu C1 — Stage2 Kapitel 1: 20 additional actual cards, 154 cumulative

Date: 2026-11-23. Source of truth for the updated bytes is the **owner Library ZIP**, not just this report. No Stage1 rescan, no false Stage4 approval, no app release.

## Exact parent and immutable preservation

Opened and inspected the Library working ZIP `Aspekte-C1-STAGE2-K01-134-RICH-CARD-DRAFTS-20261123.zip`, SHA256 `f70148ae6b6f1dd670c34f86eff39bc5a4d40223837f754de07f0d3c3660c88e`. Its **39 historical ZIP member payloads are preserved byte-identically** in the new successor; the **134 previous canonical card objects** are identical by parsed JSON. No re-scanning or discarding the 3,270 original C1 source occurrences, 435 prior lexical decisions, 9 working corrections or 29/8 contextual source decisions. The printed PDF `aspekte-neu-c1-lb-kapitelwortschatz.pdf` source SHA256 `b05c90320ad75dc19be12a374087830bd2c379206a5711e604a6aea699e189cf` supplies the exact 20 unchanged source strings and identities, **not** these newly authored teaching example sentences.

## Actual new source-bound lexical targets — PDF page 4

20 distinct previously `NOT_YET_AUTHORED` and `C1_NEW_LEMMA_CANDIDATE` source IDs:

- `C1-P04-E001` mitentscheiden
- `C1-P04-E003` beseitigen
- `C1-P04-E004` mitgestalten
- `C1-P04-E005` Beseitigung
- `C1-P04-E010` Physiotherapeut
- `C1-P04-E015` es handelt sich um + Akk
- `C1-P04-E016` real
- `C1-P04-E018` hierbei
- `C1-P04-E020` lauwarm
- `C1-P04-E021` Leitung
- `C1-P04-E023` Überfluss
- `C1-P04-E024` nachkommen
- `C1-P04-E029` unterschätzen
- `C1-P04-E033` Vielfalt
- `C1-P04-E036` undicht
- `C1-P04-E037` Warmwasser
- `C1-P04-E038` Zukunftsperspektive
- `C1-P04-E039` Wohnbereich
- `C1-P04-E041` Wohnungstür
- `C1-P04-E044` Behebung

**154 cumulative typed rich-card drafts**, exactly **616 new-or-old original DE/FA/EN example triplets** (four distinct examples per card), **770 decisions across the five right categories**, and per-card grammar reviews. All 80 newly written German sentences use the intended target lemma/inflection, all have complete Persian and English translations; the 80 German sentences are pairwise distinct. The 20 new IDs were not in the old 134 card IDs. **Exactly 93 provisional un-authored new-headword IDs** remain in the 397-source Chapter1 queue. The number 93 is source IDs, not a final card count.

New right-side dispositions: **11 source-grounded VERIFIED_PRESENT, 89 CLOSED_NO_FORCE with concrete reason**. Independent `Kombinationen` documented as `im Überfluss leben` ([Duden](https://www.duden.de/rechtschreibung/Ueberfluss)) and `einer Aufforderung nachkommen` ([Duden](https://www.duden.de/rechtschreibung/nachkommen)); these are not entire reused example sentences, and teach idiomaticity/Rektion rather than false free phrases. No fake synonym, antonym or collocation was inserted to meet a count.

## Bounded linguistic QA findings, no source rewriting

- `Leitung` has at least pipe/utility-line and management senses ([Duden](https://www.duden.de/rechtschreibung/Leitung)). Two senses retained on **one card**. In the actual learner examples, use **aus der Leitung**; printed source's telegraphic `aus Leitung` retained in `source_raw`, not treated as a correct learner sentence.
- `es handelt sich um`: impersonal, required `es` and **um + Akkusativ** ([IDS grammis](https://grammis.ids-mannheim.de/verbs/view/400549)); source lemma `handeln (sich)` kept raw, pedagogical front uses precise full construction.
- `lauwarm`: **do not invent a normal comparative/superlative paradigm**; front and grammar use reliable attributive inflection instead ([Verbformen](https://www.verbformen.de/deklination/adjektive/lauwarm.htm)).
- `nachkommen`: `kommt nach, kam nach, ist nachgekommen`, **Dativ** in the compliance meaning ([Duden](https://www.duden.de/rechtschreibung/nachkommen)).
- `Physiotherapeut`: weak masculine declension `des Physiotherapeuten`; plural `die Physiotherapeuten` ([Duden](https://www.duden.de/deklination/substantive/Physiotherapeut)).
- `Zukunftsperspektive`: preserves genuine plural `die Zukunftsperspektiven` ([Duden](https://www.duden.de/rechtschreibung/Zukunftsperspektive)).
- `Beseitigung` and `Behebung` are distinct nouns with overlapping senses; both kept per separate printed source identity without inventing separate cards per sense.
- Language checks are bounded on the **actual new text**, not full linguistic Stage4 acceptance. No claims that all DE/FA/EN examples have independent native-editor certification.

## Reproducible official project structural result

Ran actual `Workspaces/aspekte-c1-v336/04-qa/validate_c1_rich_card.py` from the identical on-disk Git blob SHA `4c0f613665bf0c0db5df9e353d218ef86490d67d` against the **entire current 154-card JSON**:

- `STRUCTURAL_PASS_NOT_STAGE4_5_6_7`
- `cards_checked=154`
- `errors=[]`
- `approved_cards=0`
- Card JSON SHA256 `99e88c90f45dc17def6c3b16dff5afeee57a10873e5e0bc112b52d6f1ab61e69`.
- Additional checks: 80/80 target present and DE/FA/EN populated, exact 134 parent card JSON values preserved, 20 unique new IDs, 397 source rows, no copied example as a Kombination, 39 historical archive payloads exact, ZIP CRC PASS.

## Verified current owner portable ZIP

- **Library path:** `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-C1/Checkpoints/Aspekte-C1-STAGE2-K01-154-RICH-CARD-DRAFTS-20261123.zip`
- **Library file ID:** `libfile_7b57ad8ece9881919b911ab79eded1ef`
- **ZIP SHA256:** `e6d1070a1f086e56f5c87f26256a5c16b18b9f3be08281909849cc0f7f964153`
- **Size:** 904128 bytes; **44 ZIP members**, of which 39 inherited parent payloads byte-identical; CRC PASS.
- Cumulative card JSON: `C1-STAGE2-K01-154-RICH-CARD-DRAFTS-20261123.json`.
- Cumulative 397-source queue: `C1-STAGE2-K01-397-SOURCE-QUEUE-154-DRAFTS-20261123.json`.
- Official validation, bounded editorial QA, and CURRENT-manifest records included.
- **Stage4 linguistic approved cards = 0. Stage5 imported/approved = 0. PR #301 remains open and unmerged.**

**Strict next action:** Resume Stage2 only from the **93 exact NOT_YET_AUTHORED C1_NEW_LEMMA_CANDIDATE** source IDs in the new verified 397-row queue. Author a genuine finite batch from the actual source, skip all 154 old drafts, preserve 4 DE/FA/EN examples and all five explicit right statuses, and execute exact official structural validator plus targeted language checks. No repeated Stage1 lexical audits, invented Stage4 approval or infinite review loops.
