# Aspekte B1+ / Lektion 02 — Drei-Phasen-Plan

**Stand:** 2026-11-08 — Phase 2/3 editorial DONE; Phase 3 full-card QA next; NONIMPORT.

**Source of truth:** SHA-verified curated Library L01-Phase3 ZIP, SHA256 `dccda4967101f6c0ec4b3df49f3f9e050fd56c4bf20b14be3805899c3e9d8522`. Existing learner data are read-only in Phase1. No textbook re-import.

## Phase 1 — Whole-Lesson Inventory: DONE

- **91 L02 cards across 91 original source rows (ordinals 72–162)**, all mapped; no dropped or duplicate learner IDs. Overall project stays 1571 card views / 1548 source rows.
- **197 DE–FA example pairs**, 0 cards without examples, 12 examples lacking an explicit QA status, 0 independent recorded morphology attestations (thus 91 require evidence/rule-scoped review).
- **18 existing curated HOLD card markers**; 3 cards already containing sense networks (3 sense blocks); 40 risk candidates for meaning/routing review — not automatically content errors.
- **1 exact duplicate DE example group** at ordinal 128 / `der Kastellan`: same sentence appears twice; preserve unique DE/FA examples in Phase2 and handle historical duplicate-release gate.
- **6 examples on already-networked cards lack correct explicit sense linkage**; do not assume other 88 cards all require an elaborate network.
- Priority groups are **P1 36; P2 21; P3 34**. Every one of 91 cards has a written Phase2 action in `L02-PHASE1-91-CARD-DECISION-QUEUE.jsonl`; priority is not approval.
- QA statuses: {"PENDING_INDEPENDENT_DE_FA_SEMANTIC_QA": 183, "PENDING_G4_INDEPENDENT_DE_FA_QA": 2, "NOT_MARKED": 12}. No invalid empty German/Persian example pair found. No changes to learner data in this phase.

## Phase 2 — Complete 91-card editorial correction: NEXT

Handle **all 91** cards and **all 197 examples** in one L02 whole-lesson stage. Prioritize HOLD, sense-ambiguity, valency and duplicate issues. Correct genuine errors only and keep multiple meanings on one existing card. Record explicit before/after evidence and 91 decisions. Do not create a micro-Review for every 10 cards.

## Phase 3 — Independent full-card QA and runtime import gate: LATER

Independent complete German/Persian release QA + morphologic and sense-routing gates + case-by-case HOLD decisions. Real German-Flashcards-Pro application TSV import and rendered Front/Back must be demonstrated rather than simulated. Failure → `RELEASE_BLOCKED`, never pretend the lesson is approved.

**Global unchanged:** 338/1571 prior G2 form attestations, 340 legacy release HOLD markers, seven exact duplicate groups across corpus (one L02); zero formal full-card release approvals. This L02 Phase1 creates **no new attestations or released cards**.

## LIVE — Phase 2/3 abgeschlossen (2026-11-08); Phase 3 NEXT; NONIMPORT

**Neuer SHA-verifizierter Karten-Owner:** Library `libfile_3f51fa99c0148191b34d7f4fafb5e4de`; SHA256 `2c11f7ab269edae7b07a2c1445845e8f48d88370f919224ec0f216ad6e91e5d3`. Ersetzt als aktuelle Kartendaten den oben aufgeführten historischen L01-Phase3-Owner; Parent bleibt verifizierbar. Archiv: 3.115.061 Bytes, 192 Members, 191 Hashes; Library-Readback/CRC/Hashes PASS.

**Alle 91 L02 Karten wurden in einer einzigen redaktionellen Lektionseinheit geprüft:** 32 mit wirklicher Inhaltsänderung, 59 unverändert nach Prüfung. 91 Dispositionen im JSONL. 27 zusätzliche Wortnetz-Karten mit 60 Sinnblöcken; die drei bestehenden Wortnetze bekommen alle 6 bisher nicht verknüpften Beispiele an ihren passenden Sinn gebunden. 3 neue DE–FA Beispiele; eine `Kastellan`-Dopplung entfernt mit vollständiger Vorher/Nachher-Dokumentation; Beispiele 197→199, null L02-Dubletten. Alle 12 bisher statuslosen Beispiele nun ausdrücklich PENDING, nicht freigegeben.

**11 Duden-scope-limited G2-Form-/Lexikbelege**: `vorbeikommen`, `zerreißen`, `umbauen` (zwei Duden-Homographen), `eintreten`, `dringen`, `Kastellan`, `Kulisse`, `meterdick`, `speisen`, `Fall`, `fortlaufen`; 11 Karten, 80 ohne neuen externen Nachweis. `dringen`: `ist gedrungen` vs `hat gedrungen` nach Bedeutung; `meterdick`: persische Beispiele präzisiert. 338→349 global begrenzt attestiert. Keine komplette Kartenfreigabe daraus ableiten.

**Technische QA ohne Release:** `Tools/qa_L02_phase2_verify_v1.py` überprüft Parent/current: 1571 Karteneinheiten, 1548 Original-Source-Map-Zeilen **byteidentisch**, alle 1480 nicht-L02 Karten **unverändert**; 91 aktuelle Dispositionen. Konservativer Copy/finite-clause-Gate auf 559 Kombinationen: 0 erkannte Fehler; global bleiben 6 exakte Alt-Dubletten außerhalb L02 Release-Hindernisse. 91-Karten Front/Back HTML sowie parsergetestete 91-Zeilen NONIMPORT-TSV im ZIP. **Kein echter German-Flashcards-Pro-Importer-/Rendertest**.

**Phase 3 NEXT:** 91 Karten und 199 DE–FA-Beispiele unabhängig vollständig überprüfen, die 80 offenen Formsachen und 18 kuratierten HOLD-Marker begründet bewerten, den echten App-Import/Renderer testen. Fehlende Evidenz → explizit RELEASE_BLOCKED. Keine 10-Wort-Reviews, keine fingierte Freigabe. Globale 340 ererbte Release-HOLD-Marker, 0 formal genehmigte Karten.
