# Aspekte B1+ — P3 final 30 / end of scoped content HOLD backlog
Date: 2026-11-11 · Status: **NONIMPORT** · Release NOT approved

## Verified owner
- Library: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Reports/Aspekte-B1plus-P3-30-SCOPED-CONTENT-GATE-NONIMPORT-20261111.zip`
- ZIP: `2ccbece909f1a3141a08846afa8b4ea2f1a68b4a411a734c677fa7b1ec3aeacc`, 5,776,696 bytes, 375 archive members, 374 SHA-256 manifest entries. Library byte-exact readback and ZIP CRC verified.
- Primary 1571-card JSONL SHA-256: `b840478d232ef4701c9af53bf6f80847da240c759abb99f022cbb755061a8bd0` (identical to parent P2 primary; **no content edits in P3**).
- Source map 1548 rows SHA-256: `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882` (unchanged).
- 3584 German–Persian example pairs carried forward exactly.

## P3 case result
All 30 original P3 cases were inspected for existing German form, Persian meaning, available DE–FA examples and sense routing. **0 new demonstrable defects in the scoped P3 risk reports**, 0 primary edits needed. These are inherited flags, often missing optional Wortnetz or historical overlay evidence that no longer contains an applicable difference. No fake enrichment or forced human reviewer.
- [Duden Volksmund](https://www.duden.de/rechtschreibung/Volksmund): no plural; current card correctly uses singular.
- [Duden zurückhaben conjugation](https://www.duden.de/konjugation/zurueckhaben): hat zurück / hatte zurück / hat zurückgehabt are indeed correct though colloquial and unusual.
- Every P3 case retains the current complete bilingual example/sense evidence and an individually recorded justification in the ZIP.

**Scoped risk HOLD ledger**: historic 359 cases now dispositioned; P1=0, P2=0, P3=0. **This does not mean all 1571 cards are globally certified or import-ready.** Exact old reports remain retained.

## Fixed route to finished release (without restarting linguistic review cycles)
1. Final *bounded* schema/format and targeted regression QA on current canonical primary. Verify all final display rules including morphology on front, no duplicated Formen on back, meaning-specific combination examples, DE–FA integrity, mapping preservation. Report evidenced exceptions with changed-card fixes only; no publisher CSV reinventory or invented human independent review.
2. Trusted release authorization manifest/digest must explicitly approve the current content owner; do not promote editable NONIMPORT marker handling to an authentication mechanism.
3. German Flashcards Pro [PR #41](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/pull/41) remains OPEN/DRAFT/UNMERGED. Review and integrate native TSV/JSON/ZIP ingress safeguards, then real success-path import with approved content, right-card multi-sense/Wortnetz visualization, origin-backed IndexedDB write and restart, full SRS preservation plus rollback.
4. Only after user-approved actual app acceptance and documented quality gates: publish verified importable artifact and set CHECKPOINT/Latest release flags. Otherwise fail closed.

No new P1–P3 or lesson-by-lesson review cycle is authorized without a distinct regression tied to a real card.
