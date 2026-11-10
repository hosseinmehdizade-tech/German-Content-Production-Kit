# Aspekte B1+ — P2 case-scope checkpoint, 11 Nov 2026

## Saved authoritative version

- Library: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Reports/Aspekte-B1plus-P2-SCOPED65-6-EDITORIAL-REPAIRS-NONIMPORT-20261111.zip` (ID `libfile_7baa78175fd88191a157b468ca049287`)
- ZIP SHA-256: `7ef8d8874752a887a93b3495cb17395eda52306d37fe02f933f979372f16ffd8`
- Curated primary JSONL SHA-256: `beb925d726b5e398b9c4374c2a26412c9e659a5ebe64c556d7a3221b9d50e690`
- Source map SHA-256 (unchanged): `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882`
- Previous canonical curated owner: `85fb2a1962424224d50701be17f465bad5bf2a1bd3f8f7b1a368e301b3fb1b6b`
- Readback exact Library bytes, ZIP CRC and all 363 member SHA-256 entries **PASS**.

## What changed

- Exactly **190 P2 cases screened structurally** from current 359-case ledger.
- **65 scoped P2 HOLDs closed**, including 59 cases whose *only* inherited flag was absence of optional structured Wortnetz with no specific defect evidenced, plus six cards with actual German–Persian lexical/sense repairs.
- **6 actual primary card objects changed**; **1565 untouched raw JSONL lines preserved**, 1571 IDs and all 1548 original source mapping rows preserved.
- **5 new DE–FA examples** added; 3566→3571 bilingual pairs. All new examples remain PENDING (not auto-PASS).
- **Important:** Scoped closures are **not** global semantic certification. 125 P2 cases stay open; no mandatory human independent reviewer or publisher source re-import.

### Real edited cards

| Ordinal | Lemma | Fix |
|---|---|---|
| 412 | die Spielfigur | Persian gloss narrowed to board-game playing piece; removed unsupported generic film-character sense ([Duden](https://www.duden.de/rechtschreibung/Spielfigur)) |
| 1438 | der Stall | corrected figurative idiom *hier sieht es aus wie in einem Stall* as dirty/untidy, added sense S2, DE/FA example ([Duden](https://www.duden.de/rechtschreibung/Stall)) |
| 1408 | die Zeitbombe | added German/Persian example for existing literal S1 rather than only metaphorical examples ([Duden](https://www.duden.de/rechtschreibung/Zeitbombe)) |
| 1510 | die Aufmerksamkeit | added example of *kleine Aufmerksamkeit* = small gift for existing S2 ([Duden](https://www.duden.de/rechtschreibung/Aufmerksamkeit)) |
| 1515 | der Übergang | added pedestrian-crossing example for existing S2 ([Duden](https://www.duden.de/rechtschreibung/Uebergang)) |
| 1520 | die Bindung | added contractual obligation example for existing S2 ([Duden](https://www.duden.de/rechtschreibung/Bindung)) |

### What was *not* changed

- **meterdick** remains untouched: Duden specifically uses *mehr als einen Meter dick*, so correcting it to “around one meter” would have introduced an error.
- Case 475 **ermordend** remains **open**: current examples cover `ermorden/ermordet`, not the isolated Partizip I itself. No fake pass or automatic lemma change.
- Optional synonyms/antonyms/word families were not generated to fill empty fields.
- Older G5 preview projection artifacts remain historical QA snapshots; the current owner is the G2 1571-card primary inside the same ZIP.
- The app's PR #41 remains draft; native import, right-card multi-sense rendering, origin-backed restart and SRS preservation not signed off.

## Locked next step — 125 P2 cases, not a new whole-lesson loop

- 73 cases carry MULTISENSE risks, 47 inherited content-edit pending status, 37 legacy overlay delta flags, with overlaps; 14 retain *no Wortnetz* signals among other risks (signals overlap, not additive).
- Continue **case-specific semantic QA** directly against the 125 still-open current cards, prioritize actual DE–FA meaning, grammar/morphology, distinct sense/example routing, and invalid Kombinations.
- Move to **P3 30** only after recording explicit P2 dispositions and real changes. No redoing P1/L01–L10 without a documented regression.
- Keep content validation distinct from app PR41 integration and full release authorization.

## Release gate

**NONIMPORT:** 155 total open HOLDs (P1 0 / P2 125 / P3 30), zero formal full-card release approvals, no real import acceptance. Never promote isolated archive/in-memory app tests as durable production import.
