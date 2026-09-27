# Menschen A2 Verben — Post-Lock Content Audit (2026-09-27)

Status: REVIEW_COMPLETE__REPAIR_CANDIDATES_FOUND__LOCK_NOT_MUTATED

Authority reviewed:
- Locked release: German-Flashcards-Pro-v444-R78-Menschen-A2-Verben-v3.3.2-LOCKED.zip
- Release SHA-256: 984cc519057115da49ac2479330704f7ed767e47df38d049330180ff516848b2
- Locked runtime: v444-R78
- Runtime CURRENT at audit time: v445-R79

## Structural result
- 292/292 cards present: 228 german-verb + 64 de-vocabulary.
- 292/292 have German definition, Persian meaning and English gloss.
- Exactly 4 DE examples per card; every example has FA + EN translation.
- 894 canonical relations: 308 COLLOCATION, 295 REKTION, 188 SYNONYM, 86 RELATED, 16 ANTONYM, 1 NVV.
- Existing Stage7 contract remains valid; this review applies a stricter pedagogical-enrichment criterion.

## Kombinationen / Kollokationen result
- 235/292 cards have at least one explicit runtime-visible combination.
- 115/292 have at least two explicit runtime-visible combinations.
- 57/292 currently have no explicit runtime-visible combination.
- 4 of those 57 already have evidence-backed collocations in canonical relations, but 6 relation items are lost during projection because early relations use value.text.
- Therefore 53 cards have no explicit collocation/connection evidence anywhere in the locked package.
- Production consistency is uneven: Batch1 20/20, Batch2 20/20, Batch3 0/20, Batch4 1/20, Batch5 5/20; from Batch6 onward coverage is almost complete.
- Six projected collocation entries are pedagogically empty because the item equals the headword itself.

### Lost evidence-backed collocations
- ma2-lu-0044 anstrengen -> jdn. sehr anstrengen
- ma2-lu-0045 sich anstrengen -> sich bei der Arbeit anstrengen
- ma2-lu-0046 beraten -> Kunden beraten
- ma2-lu-0046 beraten -> jdn. bei der Wahl beraten
- ma2-lu-0054 absenden -> eine E-Mail absenden
- ma2-lu-0054 absenden -> ein Formular absenden

## Other projection defects
- 18 evidence-backed SYNONYM/RELATED items using early value.text shape are canonical but absent from projected related.
- One genuine total Rektion omission in projected Grammatik: ma2-lu-0004 übergeben -> jdm. (Dat.) etw. (Akk.) übergeben.
- Canonical connections are dynamically consumed by the v444 presentation layer, so Batch1/2 combinations can appear in Study even though static projected details omit them; Universal/static portability is still inconsistent.

## Presentation / portability observations
- 199/228 german-verb records have front != plain canonical headword; 30 front values exceed 70 characters. Study presentation uses canonical headword, so this is primarily a Library/import portability cleanliness issue.
- Formen exposes raw enum labels: non_prefixed 88, inseparable 74, separable 66. Learner-facing German labels should be used.

## Decision
The content is structurally strong and contract-compliant, but under the user's stricter "fully equipped and practical combinations" requirement it is not yet uniformly complete.

Recommended controlled repair, not wholesale regeneration:
1. Normalize relation projection across term | text | pattern | string value shapes.
2. Restore 6 lost collocations, 18 related/synonym items and the one genuine Rektion omission.
3. Make canonical connections portable in Universal/projected output.
4. Run an evidence-backed A2-usefulness Kombinationen pass on the 53 true-gap cards, normally 1–3 useful chunks where natural, with no fabricated density.
5. Replace six headword-equals-collocation fillers and review weak/advanced combinations.
6. Clean front portability and raw separability labels while preserving stable IDs.
7. Re-run full QA/runtime acceptance against CURRENT v445-R79 and re-lock exact-final bytes.

The existing LOCK is intentionally not mutated by this review.
