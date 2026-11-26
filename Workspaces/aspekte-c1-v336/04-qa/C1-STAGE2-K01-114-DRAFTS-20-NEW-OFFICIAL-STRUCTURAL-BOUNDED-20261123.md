# Aspekte neu C1 — Stage 2 Kapitel 1: 20 new actual rich-card drafts, 114 cumulative

Date: 2026-11-23. One bounded authoring round; **no Stage1 rescan, no forced Stage4 review loop, no app import**.

## Source, identity and preservation

Exact parent: `Aspekte-C1-STAGE2-K01-94-RICH-CARD-DRAFTS-20261123.zip`, SHA256 `a66887fba07f81d80f9c2e73b81f16ac0581d0cc261f134adc5d21da26d491c0`.

All previous **29 ZIP member payloads** are byte-identical in the new successor. All 94 prior card objects retain their values unchanged. Original C1 working source **3,270** lines, earlier 435 lexical decisions, 29/8 and 2-context source decisions, and all nine previous learner-form corrections are inherited unchanged. The 397-row Chapter1 source queue retains the exact source IDs, source_raw, triage and base-policy fields; only 20 existing `production_status` fields change from `NOT_YET_AUTHORED` to `STAGE2_DRAFT_STRUCTURALLY_PREFLIGHTED_NOT_APPROVED`.

New source IDs, all **previously un-authored C1_NEW_LEMMA_CANDIDATE** from original source PDF page 3:

`C1-P03-E016` voreilig; `E018` Vorstufe; `E020` wegbrechen; `E021` unterordnen; `E023` verspielen; `E025` widerspiegeln; `E026` Forscher; `E027` Verstehenshilfe; `E029` Bewerber; `E031` Casting; `E033` Studiogast; `E038` sich gesellen; `E039` ungerecht; `E042` Vereinbarung; `E044` anbauen; `E045` Nervensäge; `E047` Partylöwe; `E048` Arbeitsleben; `E050` Arbeitsraum; `E051` Putzplan.

The source PDF SHA256 is `b05c90320ad75dc19be12a374087830bd2c379206a5711e604a6aea699e189cf`. Its headword statements are the **source of identity**, not a claim that newly authored sentences occur in the original book.

## Real authored contents and language guardrails

- **114** typed rich-card Stage2 drafts = 94 previous + 20 new.
- **456** original teaching example triplets in German/Persian/English = exactly 4 per card, including **80 new** triplets. Bounded check confirms 80/80 newly written German examples contain the intended lemma or an accepted inflection; 80/80 have both translations and all 80 German example sentences are distinct.
- **570** five-section right-side decisions cumulative, including **100 new**. New group: **20 source-anchored VERIFIED_PRESENT**, **80 reasoned CLOSED_NO_FORCE**. No relation invented to fill a section; no complete German example copied into Kombinationen. The source-based `eine Vereinbarung treffen` is independently attested in Duden and is not copied from any of this card's 4 examples.
- Grammar/source checks:
  - `C1-P03-E020 wegbrechen`: original PDF prints `bracht weg`; valid form `brach weg`, Duden: https://www.duden.de/rechtschreibung/wegbrechen. Corrected **only in learner draft**, source_raw immutable.
  - `C1-P03-E025 widerspiegeln`: uses common separated construction `spiegelt … wider`, `spiegelte … wider`, `hat widergespiegelt`; Duden https://www.duden.de/rechtschreibung/widerspiegeln.
  - `C1-P03-E038 sich gesellen`: reflexive with `zu + Dativ` and Perfekt `hat sich gesellt`; lexical usage https://www.duden.de/rechtschreibung/dazugesellen.
  - `C1-P03-E047 Partylöwe`: weak masculine inflection, humorous/colloquial register; source entry retained.
  - `C1-P03-E045 Nervensäge`: colloquial, derogatory/pejorative register; Duden https://www.duden.de/rechtschreibung/Nervensaege.
  - `C1-P03-E044 anbauen`: two independently sourced senses, plant cultivation vs building extension; Duden https://www.duden.de/rechtschreibung/anbauen.
- Word-family / synonym / related entries cite lexical sources when available. `Verstehenshilfe`, `Casting`, `Studiogast`, `Partylöwe`, `Putzplan` retain explicit source-only limitations where a dictionary relation was not verified, instead of invented links.

## Official structural preflight, actual output

Downloaded/reproduced the **exact** canonical official project validator `Workspaces/aspekte-c1-v336/04-qa/validate_c1_rich_card.py`, and verified Git blob SHA `4c0f613665bf0c0db5df9e353d218ef86490d67d`. Executed on the actual cumulative 114-card JSON bytes:

`STRUCTURAL_PASS_NOT_STAGE4_5_6_7`; **cards_checked = 114**, **errors = []**, **approved_cards = 0**, **mutated = false**.

- Card JSON SHA256: `ec69a13fcfe89ef279f0f2231df052255e2871f28890142b009fbe38259811fd`.
- The official exact validator output is included as `C1-STAGE2-K01-114-OFFICIAL-STRUCTURAL-VALIDATION-20261123.json`.
- The extra bounded, explicit source/translation/identity report is included as `C1-STAGE2-K01-114-TARGETED-LINGUISTIC-AND-SOURCE-NOTES-20261123.json`.
- **Structural PASS != independent Stage4 language approval, native app renderer/serializer Stage5, SRS, Stage6 or release.** No official Stage4 approvals.

## Verified current owner Library successor

`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-C1/Checkpoints/Aspekte-C1-STAGE2-K01-114-RICH-CARD-DRAFTS-20261123.zip`

- Library file ID: `libfile_2137b79c0e448191981f5d8b8afc42b7`
- ZIP SHA256: `1a8360e33c4f8eed48ec121c17af300a5c8b0e35f04b9f6be6f1f6bb7c8329c4`
- 674,650 bytes, **34 members**, CRC PASS, all 29 parent members byte-identical when extracted.
- Latest cumulative card JSON: `C1-STAGE2-K01-114-RICH-CARD-DRAFTS-20261123.json`.
- Latest exact 397-source queue: `C1-STAGE2-K01-397-SOURCE-QUEUE-114-DRAFTS-20261123.json`.
- Current-manifest JSON in the ZIP specifies newest members and prevents the reader from mistaking an inherited older snapshot for CURRENT.

**Finite next action:** Resume only the **133 remaining provisional C1_NEW_LEMMA_CANDIDATE** source IDs in the saved queue, in substantial finite authoring batches. Do not redo any former 94 drafts or Stage1 duplicates. Preserve 4 DE/FA/EN examples, five meaning-specific right-section decisions, and no fake combinations. Final Stage4 linguistic approval of actual cards remains separate and pending.
