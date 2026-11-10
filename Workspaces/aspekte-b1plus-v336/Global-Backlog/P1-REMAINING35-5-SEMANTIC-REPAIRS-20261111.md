# Aspekte B1+ — P1 remaining35, five substantive repairs (2026-11-11)

Current curated owner: /Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Reports/Aspekte-B1plus-P1-REMAINING35-5-SEMANTIC-REPAIRS-NONIMPORT-20261111.zip

- ZIP SHA256: `f4e91400c4ecc5c5fd714d6d533833b3ad1f558057353aa1c6f09d41ad537464`
- Primary SHA256: `1114b412adf39e4769125234d6b8686d00724e7cabf4bd557d3a15a4888615e7`
- Source map SHA256: `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882`
- 1571 card IDs and 1548 source-map rows retained; 1566 card objects unchanged
- Scoped P1 HOLD closures: 5, leaving 30 P1, 190 P2, 30 P3 (250 total)
- Five new DE/FA examples, two newly anchored meaning blocks. Total DE/FA pairs: 3563.

## Real content changes

1. **324 der Absatz:** fixed false identity between the shoe's raised heel component and the anatomical heel. [Duden](https://www.duden.de/rechtschreibung/Absatz)
2. **669 die Forderung:** distinguished `Forderungen an + Akk.` (recipient) from a financial claim against a debtor; added two sense-bound examples. [Duden](https://www.duden.de/rechtschreibung/Forderung)
3. **1206 der Transfer:** knowledge/information transfer was listed in Persian meaning but missing from sense routes; added S4 and bilingual example, kept all original senses in one card. [Duden](https://www.duden.de/rechtschreibung/Transfer)
4. **1297 anführen:** old colloquial "foppen/hereinlegen" accepted in primary meaning but absent from sense network; added S4 and example. [Duden](https://www.duden.de/rechtschreibung/anfuehren)
5. **1448 anhalten:** intransitive stopping added to existing S1 with usage guidance and example; no unnecessary card/sense split. [Duden](https://www.duden.de/rechtschreibung/anhalten)

## QA / release

Library exact-byte readback, ZIP CRC, all 352 manifest SHA256 entries, source-map bytes, unchanged 1566 cards and all 1571 IDs passed. Historical ledgers retained in ZIP, plus new current 359-case ledger, five-case full before/after and proof report.

**BLOCKED NONIMPORT.** Newly authored examples remain PENDING. This is a scoped lexical QA closure, not complete corpus signoff. PR #41 for the app is still a draft; real native import, right-card rendering, persistent restart and SRS preservation are not signed off.

**Next:** Evaluate remaining 30 P1 against demonstrated semantic/grammar defects; don't invent quality problems merely from legacy HOLD flags. Address P2/P3 and the app release gate separately.
