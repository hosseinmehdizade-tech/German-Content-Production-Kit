# Aspekte C1 — Kapitel 1: all 247 provisional new-lemma source IDs routed to 246 typed cards + 1 same-lemma alias

Date: 2026-11-23. **Finite genuine Stage2 authoring result.** No Stage1 rescans; no Stage4 or app approval claims.

## Exact parent preservation and source provenance

Directly opened the owner Library `Aspekte-C1-STAGE2-K01-199-RICH-CARD-DRAFTS-20261123.zip` (verified SHA256 `c084f04f4cb2c39658e1defce0c98407011a4f8da820598ea03b5ba3c3fb00dc`). It contained exactly 199 typed cards and 397 Kapitel1 source-occurrence records. The original lower-level lexical dispositions of 435, 3,270 immutable source text lines, nine mutable source corrections and prior stage decisions are preserved in the inherited archived members.

**47 new actual typed cards** were authored in this turn, in two bounded source-indexed subbatches (30 + 17). Each contains exactly **4 distinct original German example sentences with Persian and English translations**, DE/FA/EN meaning(s), explicit grammar review and all five right-side statuses: Synonyme, Antonyme, Wortfamilie, Verwandte Wörter, Kombinationen. Newly authored examples are teaching text, **not quoted from the textbook**.

- **Previous 199 cards retain exactly their original parsed JSON content**, no rewrites.
- **All 54 parent ZIP member payloads preserved byte-identically**, and all five interim 229-member ZIP additions also preserved in the final 246 archive: **64 total ZIP members**, testzip/CRC PASS.
- **397 original source IDs, raw strings, triage and base-policy decisions unchanged**. Production status was updated for 47 new cards and one source-alias only. The immutable original source PDF stays unchanged.
- Exact current canonical file: `C1-STAGE2-K01-246-RICH-CARD-DRAFTS-20261123.json`; exact current source queue: `C1-STAGE2-K01-397-SOURCE-QUEUE-246-DRAFTS-20261123.json`. The final ZIP embeds explicit latest-manifest and official-validator receipts to prevent mistakenly loading an inherited historical snapshot.

## Identity correction: one genuine duplicate source entry (no second card)

`gerade` appears in the printed original as two source records:
- `C1-P01-E067`: emphatic/especially, e.g. *gerade wir*.
- `C1-P02-E032`: temporal now/just, e.g. *gerade erforscht*.

The actual new **one** card `C1-P01-E067` includes both senses and four trilingual examples split 2 + 2. `C1-P02-E032` is marked `STAGE2_SOURCE_ALIAS_NOT_SEPARATE_CARD` with direct pointer to `C1-P01-E067`. No lost source ID, no separate SRS card, no fabricated source sense.

**Chapter1 provisional new-lemma subset is now fully routed: 247 initial source IDs = 246 actual typed draft cards + 1 source alias. Exactly ZERO not-yet-authored source IDs remain in this subset.** Do not equate this scoped milestone with completed all-chapter C1 content or Stage4 approval.

## Cumulative QA on actual output

- **246** cumulative typed card drafts; **984 original German/Persian/English example triplets** = exactly 4 per card.
- All 188 **newly authored** examples (120+68) have non-empty German, Persian and English; each was checked for a visible target or appropriate inflection using source-specific morphology patterns; no duplicate German examples in the cumulative **984**-example dataset.
- **Official exact source-owned C1 validator** `04-qa/validate_c1_rich_card.py`, **verified Git blob SHA `4c0f613665bf0c0db5df9e353d218ef86490d67d`**, executed on exact cumulative final JSON bytes: `STRUCTURAL_PASS_NOT_STAGE4_5_6_7`; **246 checked, errors=[], approved_cards=0, mutated=false**. JSON SHA256 **`6ea8f17f6ee1ca48ef22126e2ed9e7d925e7193da956c9bd7a00b3f038f1279a`**.
- Right-side sections with no independently confirmed contribution are explicitly `CLOSED_NO_FORCE` with reasons, not padded with bogus synonyms or copied examples. Source-grounded new Wortfamilie and related links added for `Engagement`, `Verein`, `Kriminologie`, `herstellen`, `wirken`, `Nadel`, `Zucker`, `Zahnarzt`, `nähen`, `zünden`. This **remains incomplete enrichment** compared with full language Stage4; structural results do not demonstrate native-quality or independently verified semantic review.
- Specific bounded correctness notes:
  - `recht haben` lower-case is Duden-preferred, capital is allowed ([Duden](https://www.duden.de/rechtschreibung/recht_haben)).
  - `gerade` temporal vs emphasis on one card ([Duden](https://www.duden.de/rechtschreibung/gerade_soeben_direkt_knapp)).
  - `eine Erfindung zum Patent anmelden` examples do not assume that an abstract idea is patentable; original loose phrase is unchanged ([PatG §34](https://www.gesetze-im-internet.de/patg/__34.html)).
  - `Klickgarant` is an original printed compound; only component `Garant` is separately dictionary-attested, hence full-compound standardness remains a specific Stage4 note ([Duden](https://www.duden.de/rechtschreibung/Garant)).
  - `Doppelstich` is attested in sewing instructions, but its exact stitching mechanism/translation is **not** determined from the isolated source glossary and remains a source-context Stage4 watch ([sewing manual](https://s3.eu-west-1.wasabisys.com/sewdirect/B6966_deutsch_ins.pdf)).
  - `Homöopathie` is described as an alternative-treatment concept **without claims of scientifically proven therapeutic efficacy** ([IQWiG](https://www.gesundheitsinformation.de/glossar/homoeopathie.html), [AOK](https://www.aok.de/pk/leistungen/alternative-heilmethoden/homoeopathie/)).
  - `kiefergerecht` is marked as a product-description term, not a proven safety or medical benefit ([Apotheken Umschau](https://www.apotheken-umschau.de/familie/freizeit-alltag/ausstattung/welcher-schnuller-ist-der-richtige-793027.html)).
  - `Nadelöhr` literal eye of needle vs bottleneck, one typed card ([Duden](https://www.duden.de/rechtschreibung/Nadeloehr)).
- This is source-grounded **bounded Stage2 content QA, NOT full Stage4 linguistic signoff, native format projection, Stage5/Stage6, SRS, app import or release.** Stage4-approved = **0**.

## Other Kapitel1 source-occurrences must NOT be silently ignored

The frozen printed chapter has **397** source occurrences, of which the just-finished provisional new-lemma group accounted for 247. Remaining **150 other source occurrences** are already categorized and are **NOT 150 new independent cards**:

- **61 `HOLD_C1_DISTINCT_SENSE_OR_PHRASE`** (priority: check genuine C1 sense/collocation; enrich existing lower-level card if appropriate, rather than generate a new duplicate headword).
- **67 `EXCLUDE_CANDIDATE_LOWER_LEMMA`** and **10 `EXCLUDE_CANDIDATE_LOWER_SAME_USAGE`** (preserved lower-level merges).
- **7 `HOLD_ALIAS_LOWER`**, **2 `POTENTIAL_FALSE_POS_MATCH`**, **2 `SENSE_DIFFERENCE_HOLD`**, **1 `MORPHOLOGY_ERROR_HOLD`**.
- All 150 retain original triage and raw data. No claim that those remaining semantic/grammar review items are complete. To prevent infinite Stage4 loops, process these **finite named source-ID groups**, not general whole-project rescans.

## Current owner Library checkpoint

`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-C1/Checkpoints/Aspekte-C1-STAGE2-K01-246-RICH-CARD-DRAFTS-20261123.zip`

- Library ID **`libfile_163a52fd8cb48191a661e9ee5033ea6c`**
- ZIP SHA256 **`0f8a1fece86ad4f2e834e64e48ddfa077649558d0210f4557738728c3ab3fe2b`**
- ZIP size **1,530,510 bytes**, **64 members**, testzip/CRC PASS, **59** inherited 229-ZIP payloads and all **54** original 199-ZIP payloads intact.
- Exact newest canonical JSON SHA256 `6ea8f17f6ee1ca48ef22126e2ed9e7d925e7193da956c9bd7a00b3f038f1279a`.
- All 397 raw source entries preserved; no deletion of source or historical data.

**Strict next action:** Do one bounded meaning-based Stage2 disposition of the exact **61 `HOLD_C1_DISTINCT_SENSE_OR_PHRASE` Kapitel1 source IDs**, using the already-frozen lower-level decision ledger. Preserve all 246 draft objects. Decide whether each legitimately enriches an existing base lexical card or is a genuine separate idiom/sense candidate; do not invent 61 cards. Then handle remaining 7+2+2+1 true exceptions and perform one scoped linguistic Stage4 gate on actual card content. No Stage1 reopening, no artificial source gates, no unbounded independent-review loops.
