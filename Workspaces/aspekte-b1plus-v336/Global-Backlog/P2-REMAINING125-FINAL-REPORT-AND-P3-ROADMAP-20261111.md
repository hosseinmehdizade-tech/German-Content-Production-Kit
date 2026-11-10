# Aspekte B1+ — P2 remaining 125, scoped review complete
Date: 2026-11-11 · **NONIMPORT**

## Verified current owner
Library file: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Reports/Aspekte-B1plus-P2-REMAINING125-CONTENT-RESOLUTION-NONIMPORT-20261111.zip` · `libfile_0b9e26af6fb081918dffe8ea8b10a305`
- Archive SHA-256: `3872d7d489d23ce17f7a6ff507bbf753741b1339429e6499cc75c51f46fa6911`, 5,689,969 bytes, 371 members, 370 SHA-256 manifest entries.
- Curated primary JSONL SHA-256: `b840478d232ef4701c9af53bf6f80847da240c759abb99f022cbb755061a8bd0`
- Source-map SHA-256: `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882` (unchanged)
- Exact Library byte readback, ZIP CRC, independent verifier and 10 negative mutation tests: PASS.

## Whole P2 scope result
- Previously: 125 remaining P2, plus 30 P3 (155 global HOLD).
- **125/125 P2 cases individually documented** in the current case-ledger. 16 primary card objects received actual fixes; 109 stale/covered case-scoped risk flags dismissed after contextual front, meanings and German–Persian example screening. This is **not** a blanket full-language certificate.
- **13 new bilingual examples** (3571→3584); four existing DE/FA examples repaired. New examples retain QA=PENDING.
- **1571 cards, 1548 source map rows preserved**, 1555 other cards byte-identical. All prior reports retained in ZIP; no publisher source reinventory; no extra human evaluator requirement.
- **Current P1=0, P2=0, P3=30** — 30 global scoped HOLDs remain.

## Substantive repairs in Master
| Source ordinal | Headword | Actual change |
|---|---|---|
| 475 | ermordend → ermorden | Normalized isolated Partizip-I form into a learnable verb, preserved Partizip I on front and original source provenance; added verb example |
| 634 | der Aufwand | Dedicated excess/pomp example for missing S2 |
| 747 | der Lebenslauf | Routed 5 existing examples to two meanings: CV vs course of a life |
| 879 | schwer/leicht vermittelbar | Exact adjective example for explainability |
| 990 | relativ | Added S1 frame-of-reference example distinct from degree adverb |
| 1022 | überhören | Routed accidental vs intentional non-hearing as two senses |
| 1031 | hohl | Explicit tree, sunken cheeks, hollow voice senses + voice example |
| 1215 | entschädigungslos | Replaced 3 ambiguous booking/cancellation contexts with clear expropriation usage |
| 1312 | aufgreifen | Added rare pickup meaning S3 and example |
| 1325 | das Hauptwerk | Added musical organ Hauptwerk S3 and example |
| 1341 | der Vorgang | Included event/occurrence within general S1 with context example, not gratuitous split |
| 1417 | der Spatz | Corrected direct-nickname quotation grammar |
| 1443 | ausreden | Added regionally marked reflexive S3 for confiding in someone |
| 1484 | die Assoziation | Added scientific link S2 example and rare political union S3 example |
| 1513 | die Strukturierung | Added result/layout sense and corresponding example |
| 1525 | die Fünfzigerjahre | Added decade-of-life S2 with age-specific example |

### Reference dictionary links (use only for specific lexical edits)
- [Duden: Aufwand](https://www.duden.de/rechtschreibung/Aufwand)
- [Duden: relativ](https://www.duden.de/rechtschreibung/relativ)
- [Duden: Assoziation](https://www.duden.de/rechtschreibung/Assoziation)
- [Duden: ermorden / Partizip I](https://www.duden.de/konjugation/ermorden)
- [Duden: hohl](https://www.duden.de/rechtschreibung/hohl)
- [Duden: ausreden](https://www.duden.de/rechtschreibung/ausreden)
- [Duden: Fünfzigerjahre](https://www.duden.de/rechtschreibung/Fuenfzigerjahre)
- [Duden: Hauptwerk](https://www.duden.de/rechtschreibung/Hauptwerk)
- [Duden: aufgreifen](https://www.duden.de/rechtschreibung/aufgreifen)
- [Duden: Lebenslauf](https://www.duden.de/rechtschreibung/Lebenslauf)

## Exact audit trails within archive
`Global-Backlog/P2-REMAINING125-20261111/P2-125-CASE-CONTEXT-DECISIONS.jsonl`
`Global-Backlog/P2-REMAINING125-20261111/P2-359-CASE-STATUS-CURRENT.jsonl`
`Global-Backlog/P2-REMAINING125-20261111/P2-16-CHANGED-CARD-OBJECTS-BEFORE-AFTER.json`

## Fixed roadmap
1. **P3=30**: one risk-focused pass, fix only evidenced content defects; all 359 case decisions traceable. No reopening completed P1/P2 absent specific regression.
2. **Content release gate**: final regression, bilingual examples and combination validation, approved trusted manifest. P1/P2 scoped closure is not full semantic signoff.
3. **App acceptance gate**: PR #41 remains draft/unmerged. Test real import formats, origin-backed IndexedDB persistence across restart, typed multi-sense right-card rendering, SRS preservation and rollback before import authorization.

No merge, release, production import or app changes authorized by this checkpoint.
