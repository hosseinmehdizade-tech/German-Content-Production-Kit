# Aspekte B1+ Lektion 04 — Drei-Phasen-Abschluss

**Stand 2026-11-08 · Phase 1 DONE · Phase 2 DONE (AFTER CRITICAL PERSISTENCE FIX) · Phase 3 RELEASE GATE EVALUATED → BLOCKED / NONIMPORT**

**Datenintegritäts-Vorfall:** Der ursprüngliche Phase2-ZIP-Inhalt hat nur Sidecar-Berichte und Statuszählungen gespeichert, nicht die tatsächlichen 62 card-edits im primären JSONL. Dieses Paket (Library `libfile_e1d6e3a7045c81918bf679544a3fa2f0`) ist als falsch/superseded markiert. Die korrekt gespeicherten 62 Änderungen sind im reparierten ZIP `libfile_b56dcf2878648191a36919b6322c5a31`, SHA `49146d3266c5b802136d41cace941c986c39f0d00c82eb02897fa02ade5f53d9`, nachgewiesen. Beim Schreiben jedes künftigen Owners: vollständiges JSONL aus bearbeiteten Karten neu schreiben, wieder einlesen, tatsächliche Objekt-Diffs nachweisen und Manifest/CRC mit Readback prüfen.

**Current L04 Phase3 owner:** Library `libfile_10c0072c60b881919cfb3ce2cfaab2fb`, SHA `31d8d0640d5bacdb080f0a379aa926542498a905c82b4e3d2f3d670d7bb2aca4`. Exactly **160 cards**, **365 DE–FA examples**, **44 sense networks**, **115 linked examples** (1 dual-meaning sentence unlinked by design), **3 additional verified-context meaning edits** (`recherchieren`, `quasi`, `der Ball`). All other lesson card objects and the original 1548-row map unchanged. Exact Library readback, 234 internal manifest hashes and CRC pass.

**Actual strict QA:** the whole-lesson 160-card release gate was run and returned BLOCKED, with 54 scoped form-evidence gaps, 32 inherited editorial HOLDs, unfinished bilingual QA, 1 ambiguous example, no actual application importer receipt, and five old duplicate examples outside L04. 665 global structured Kombinationen pass the structural noncopy gate; this is not evidence that every combination is natural or fully context-checked. Complete QA-only HTML and 160-card offline TSV parser roundtrip are inside the owner archive. **Zero formally released cards.**

**Final workflow state: `RELEASE_BLOCKED_NONIMPORT` (not a reopened Phase2/another small Review cycle).** No fictional external human examiner prerequisite; explicitly verified content and deterministic checks are sufficient in principle, but current release evidence is incomplete. Next general production milestone is **L06 Phase1 whole-lesson inventory**, from the current L04 Phase3 SHA-verified Library owner. Preserve this L04 unresolved release backlog until actual issues can be resolved; don't pretend app runtime was tested.

Linked receipts:
- `Lessons/L04/PHASE2-CORRECTED-MAIN-DATA-REPAIR-20261108.json`
- `Lessons/L04/PHASE3-160-CARD-QUALITY-GATE-20261108.json`

---
## Historische Phasenpläne / prior notes

# Aspekte B1+ · Lektion 04 · Drei-Phasen-Plan

**Stand: 2026-11-08 · Phase 2/3 editorial/structural work DONE WITH DOCUMENTED HOLDS · Next Phase 3 QA · NONIMPORT**

## Current Phase2 owner (supersedes the earlier Phase1 note)
- Library ID: `libfile_e1d6e3a7045c81918bf679544a3fa2f0`.
- SHA256: `a3b9166fa670c14b3c0c40cc381c5b0ae96402b080a63c8a1934e19c18aee792`.
- **160/160 decisions**, of which **62 existing cards received targeted edits**: 13 new semantic networks, 36 new sense blocks, 112 new example-to-sense links, four Persian meaning refinements and 31 example pending-status repairs.
- One exact German example repetition in `schätzen` removed while preserving both Persian translations. Original 365 examples now 364, and remaining five exact DE example duplicate groups are outside L04.
- All 1571 source-derived card IDs, all 1548 original source mappings and non-L04 card contents preserved. All 32 L04 curated HOLD markers kept. No new form attestations or release approvals. **No external 'independent reviewer' prerequisite** beyond grounded content decisions and deterministic QA.
- 98 other cards were preserved on structural review; this is not a claim that all their DE/FA content has received final language validation.

## Phase 3 — next work unit
1. Case-level German–Persian meaning, example, grammar and collocation decisions for all 160 cards, prioritizing unresolved cases, not repetitive microbatches.
2. Re-evaluate 32 curated HOLDs and 54 form-attestation gaps without treating lack of reference metadata as proof of a linguistic mistake. Retain ambiguous mixed-sense example unlinked unless justified.
3. Strict corpus regression, complete HTML/TSV projections and an **actual app import/render test** if accessible; offline simulation does not count.
4. Finish with **RELEASED only for proven, app-tested cases**, else clearly label remaining as **RELEASE_BLOCKED/NONIMPORT**. Do not invent another person to perform a second review.

---
## Historical Phase1 plan (retained for traceability)

# Aspekte B1+ L04 — Drei-Phasen-Plan

**Stand:** 2026-11-08 — Phase 1/3 vollständige 160-Karten-Gesamtinventur **DONE**; Phase 2 NEXT; **NONIMPORT**.

## Quelle und Grenzen

- Nur der letzte SHA-verifizierte **kuratierte** Library-Owner wird für Lernkartendaten verwendet, SHA256 `ea0bde4b38aebca9973f9b8d90e201f627edd8c1c491d752006792991b2a34e6`; keine Rückkehr zur Lehrbuch-CSV. Original-Source-Map: 1548 Zeilen, SHA256 `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882`. Gesamtkorpus 1571 Karten. Owner **in Phase1 nicht verändert**.
- L04 **160 Karten / 158 Originalzeilen (358–515)**: bestehende Aufteilungen in Originalzeilen 358 (3 Karten: Freizeitbeschäftigung/Freizeitaktivität/Freizeitgestaltung) und 436 (2 Karten: plaudern/schwatzen), **bereits korrekt integrierte Quellzeile 443 in der bestehenden Karte 442 `schätzen`**, plus Cross-Lesson-Quellverbindung **44 → 405 `Wohlstand`** erhalten. Alle 158 L04-Originalzeilen vorhanden; kein Duplikat wegen Split automatisch löschen.
- 365 originale DE–FA-Paare, alle Texte vorhanden, **0 Karten ohne Beispiel**. Scoped Duden G2 bereits für **106** Karten, **54** ohne unabhängige Form-Einzelnachweise. **32** kuratierte Karten-HOLDs bewusst nicht entfernt. 31 Netzwerk-Karten mit 45 Sinnblöcken; **67 der 69** Beispiele in diesen Karten fehlen derzeit die eindeutige Verbindung zu einem Sinn (2 sind bereits verbunden), keine Zwangszuordnung, wenn mehrdeutig. **32** Beispiele ohne QA-Status; alle 365 brauchen vollständige sprachliche Freigabe.
- **Eine exakte deutschsprachige Wiederholung in `schätzen` (Ordinal 442)**: `Ich schätze, dass wir noch zehn Minuten brauchen.` kommt mit zwei unterschiedlichen, sehr ähnlichen persischen Übersetzungen vor. Nicht ohne Prüfung einer Übersetzungsnuance einfach beide löschen.

## Phase 2 — gesamte Lektion redaktionell korrigieren, nicht 10-Wort-Reviews

1. Vollständige 160-Karten-Queue in einer einzigen Lektionseinheit abarbeiten: Risikofälle **P1 63**, **P2 5**, **P3 92**, ohne P3 als automatisch freigegeben zu betrachten.
2. Mit Priorität die `schätzen`-Dublette, 67 Beispiel-Sinn-Zuordnungen bei 31 Netzwerk-Karten, 32 Beispiele ohne QA-Status, 32 ererbte HOLDs und falsche Wortarten/Mehrdeutigkeiten bearbeiten. Den aktuell vorhandenen Sinn- und Kombinationen-Inhalt erhalten.
3. Für alle 160 Einzelkarten Ergebnis festhalten: **wirklich geändert / geprüft ohne Textänderung / HOLD samt Grund**. Nur belegte Korrekturen eintragen; DE–FA-Beispiele, Artikel/Plural, Verben und Mehrdeutigkeiten ausdrücklich prüfen, ohne künstliche Sinn-Splits.
4. Nach Änderung aktuelle 1571 Karten, 1548 Originalzeilen und alle Nicht-L04-Karten mit Parent bitweise/objektweise abgleichen; strenge Kollokations-, Duplikations- und Morphologie-Gates laufen lassen. L04-Releases bleiben gesperrt.

## Phase 3 — separate Endprüfung

- Echte Sinn-/Übersetzungs-QA und zielgenaue Grammatikevidenz, 32 erhaltene HOLDs einzeln bestimmen. Tatsächlichen App-TSV-Importer/Renderer prüfen. Fehlt der Nachweis, Endstatus **RELEASE_BLOCKED**, nicht künstlich alle Karten bestätigen.
- Keine erneuten 10-Karten-Mikrobatches und keine Rückkehr zum Lehrbuch-Original als Source of Truth.