# Menschen A1-L01 — Final Audit Round 1

**Status: PASS_WITH_ADVISORIES**

Exact locked authority:
- `German-Flashcards-Pro-v413-R47-Menschen-A1-L01-GOLDEN.zip`
- SHA-256: `0507cf3209942af303b8dfdb25bbf57fbc9c8e468dad76eaebea4f661a9d8075`
- 151 archive members
- nested content ZIP SHA-256: `0cd1f0c41881f1614977f49cf1d8fbb41d77be1f23bcaf806b8101761fa400d7`

## Round 1 result

- 59 independent checks: **57 PASS, 0 FAIL, 2 advisory checks**
- Packaged Stage 4 validator rerun from clean extraction: **25/25 PASS**
- 118 cards = 86 senses + 32 expressions
- 472 German examples = exactly 4/card, all with Persian + English translations
- 21 review flags: **21/21 resolved**
- 21 relations: identity/evidence integrity PASS
- Source mapping: **89 source rows → 118 canonical targets**, complete
- Audio lineage: **113 target refs**, five no-audio split targets explained by two source rows; no invented audio
- Delivery: projected JSON ↔ Universal-v2 TSV exact field parity
- Card types: 98 de-vocabulary + 20 german-verb
- Release manifest rehash, nested package hash, package hygiene, raw-source exclusion: PASS
- Later v433 regression evidence also imported the actual locked L01 payload as 118 cards and preserved cumulative persistence/reload.

## Advisories to investigate/fix

1. `ma1m-lu-0071 rückfragen`: historical learner payload has `present_3sg=null` and `preterite=null`, while Perfekt is `hat rückgefragt`. This was accepted by the old locked validator, but Round 2 must decide whether these morphology fields should now be completed.
2. `RELEASE-FILE-MANIFEST.json` still contains the pre-final status `LOCKED_CANDIDATE_PENDING_FINAL_ARCHIVE_HASH`.
3. `Reports/A1-L01-CHECKPOINT.json` still contains a stale next action asking to verify the final archive/start L02.
4. `Docs/HANDOFF.md` still contains pre-final wording that is no longer current.

The three metadata items do **not** indicate learner-content corruption; they are stale embedded handoff/finality metadata.

## Next gate

Round 2 is mandatory before declaring L01 fully re-audited: card-by-card linguistic/adversarial review of German, Persian and English, morphology, Rektion, register, CEFR suitability, examples and relations.

Any learner-facing defect confirmed in Round 2 will produce a repaired successor artifact with a **new SHA-256**. The historical locked ZIP will not be silently overwritten.
