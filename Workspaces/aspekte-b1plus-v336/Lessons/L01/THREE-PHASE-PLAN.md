# Aspekte B1+ · L01 · Drei-Phasen-Plan

**Stand 2026-11-08 — Phase 3/3 evaluated, release BLOCKED; NONIMPORT.**

## Source of truth
The current learner-data owner remains the SHA-verified L05 Phase3 Library ZIP (`libfile_8e25215035b48191a9481393e7856510`), SHA256 `b5e470617bd72a34e6ab6236ba3232d247d2a1ee0a45f35126e5c7beed6e41f6`. It contains 1,571 provisional learner cards and 1,548 original-source mapping rows. **No learner data edited in Phase 1.** Never restart from the textbook or original raw CSV.

## Phase 1 / Ganzlektion-Audit — DONE
- **90 cards corresponding to 71 source rows (ordinals 1–71), no missing rows.** The exact source map confirms that ordinals **14/15** are merged as collocations into `der Kontakt`, ordinal **57** into `greifen`, and external ordinal **733** is cross-linked to the established L01 card `Darauf kommt's an`. Do not split valid G1 consolidations or count 733 as an additional L01 source row.
- **139 DE–FA example pairs, all explicitly pending independent semantic QA.** 24 cards have no examples. 6 forms already attestations with specific scope; 84 have no independent attestation. 42 cards carry curated HOLD markers. 3 cards currently have sense-based semantic networks with 4 existing blocks.
- 67 semicolon-based possible multiple-sense cases without networks are candidates only: semicolons are not proof of faulty content or mandatory multi-sense routing.
- Two complete-sentence Fronts, ordinals 60 and 61, require a decision whether to keep an intentional sentence card or route sentence to a lexical card. No silent deletion. 0 exact duplicate DE examples within L01, 0 empty DE–FA pairs, no redundant Back Formen.
- **Priorities: P1=49 / P2=41 / P3=0**, purely editorial sorting, not approval or proof of faults. Per-card decision queue (90 JSONL records) available as attached local artifact. Audit and its sha-verified input owner are described in `Lessons/L01/PHASE1-90-CARD-AUDIT.json`.

## Phase 2 / Gesamtkorrektur — NEXT
Review **all 90 cards** in ONE lesson correction milestone, first P1 then P2; give all 139 bilingual example pairs an editorial language decision. Only fix demonstrated lexical/grammar errors, preserve main/secondary meanings in one card, add sense-specific examples when pedagogically necessary, validate case/prepositions. Evaluate 24 zero-example cards, 42 HOLD markers, 67 ambiguous-sense candidates, and two sentence Fronts. Keep the 14/15/57 consolidations and 733 cross-lesson link. Write one before/after ledger for substantive changes; no 10-word Reviews.

## Phase 3 / QA und Freigabe — AFTER Phase2
Run independent **full-card DE–FA / morphological** checks on the whole lesson; enforce global source-map, example, noncopy, sense and no-back-Formen gates. Check *actual* app importer and rendered cards, not just an offline HTML/TSV projection. Publish only independently approved units, otherwise mark explicit RELEASE_BLOCKED. Current project 0 full-card approvals, 340 historical global release HOLDs, no proven app import.

**Control policy:** whole lesson, at most three milestone stages; each stage must represent real work, and no fake release approval.

## AKTUELLER VERBINDLICHER STAND — L01 Phase 2/3 DONE (2026-11-08)

**Der oben genannte L05-Owner ist nur die historische PHASE1-Basis.** Neuester kuratierter Daten-Owner ist **L01 PHASE2**:
Library `libfile_7fa4ce8f2df4819197d1a894598e9035`, SHA256 `3060b35afb9779e8f88ee7064ec4f7ff0d35b7218f1fa0888cfa9dd6063dd9d7`, 3.051.031 Bytes; exakter Library-Readback PASS, ZIP-CRC PASS und alle 172 SHA256-Member-Hashes PASS. Alle 1.548 Source-Map-Zeilen unverändert; keine Karten aus anderen Lektionen verändert.

**Phase1:** Gesamtprüfung 90/90 Karten aus 71 Originalzeilen, inkl. bestätigter Zusammenführungen 14/15/57 und Cross-Lesson-Verknüpfung 18→733. DONE.

**Phase2:** 90/90 Karten mit begründeter redaktioneller Entscheidung — **55 echte inhaltliche Kartenänderungen**, 35 kontrolliert ohne Textänderung. **30 neu verfasste DE–FA-Beispielpaare**, also **139→169 Beispiele**, **24→0 Karten ohne Beispiel**; **33 Karten mit neuem Sinnnetz / 62 neue Sinnblöcke** und **65 explizite Beispiel-zu-Sinn-Verknüpfungen**. 1 kontextspezifische FA-Beispielübersetzung verbessert. Beide Original-Satzkarten (`Der Vater schimpfte mit dem Kind.`, `Das Glas hat einen Sprung.`) unter Wahrung der Original-Quellbelege ausdrücklich klassifiziert statt blind gelöscht. `aushängen` mit zwei bisherigen Formen und zwei Bedeutungen nicht überschrieben. Keine erzwungenen Synonyme/Antonyme. In den **499 gesamten Kombinationen** erkannte der Noncopy-/finite-clause-Gate null Probleme (Heuristik hat Grenzen); L01 0 exakte lokale Beispieldubletten, außerhalb bleiben 7 globale Alt-Dubletten.

**Phase3 NEXT:** alle 90 Karten vollständige DE/FA- und Grammatik-QA unabhängig absichern; 84 fehlende externe G2-Formatteste entweder nachweisen oder regelbasiert begründet klären; 42 kuratierte HOLD-Karten differenziert prüfen; reale App-TSV-Import- und Front/Back-Anzeige tatsächlich testen. Die 30 neuen Beispiele und 62 Sinnblöcke sind hochwertige redaktionelle Kandidaten, **noch nicht unabhängig freigegeben**. Bei offenen Blockern als `RELEASE_BLOCKED` abschließen und zum nächsten vollen Unterricht wechseln; keine 10-Wort-Reviews.

**Aktuell weiterhin NONIMPORT, global 0 vollständige Kartenfreigaben; 340 Release-HOLDs.** Berichtsquelle: `Lessons/L01/PHASE2-COMPLETE-90-CARDS-REPORT.json`; QA-Skript, vollständiges Vorher/Nachher-Ledger, alle 90 Dispositionen und QA-HTML im aktuellen Library-ZIP.

## Phase 3/3 — Release-Gate evaluated: BLOCKED (2026-11-08)

**The three-phase L01 cycle has now been evaluated for all 90 cards. This does not mean 90 cards are export-approved.** Phase1 90/90 audited, Phase2 90/90 editorial decisions (55 cards actually edited), Phase3 fail-closed QA over 90 cards, resulting in **90/90 BLOCKED / 0 formally approved**. Do not restart numbered ten-word Review loops.

- Starting point L01 Phase2 owner SHA256 `3060b35afb9779e8f88ee7064ec4f7ff0d35b7218f1fa0888cfa9dd6063dd9d7`. Current master is L01 Phase3 owner `libfile_d5a43c53f89c81919d8eb6d071a7a60a`, SHA256 `dccda4967101f6c0ec4b3df49f3f9e050fd56c4bf20b14be3805899c3e9d8522`, 3,092,241 bytes and 184 ZIP members. Library upload, exact SHA256 byte-readback, ZIP CRC and 183 internal member hashes verified.
- Genuine source-preserving card improvements: eight previously missing **example→specific-sense links** completed for four current cards `Kontakt`, `behindert`, `aushängen`, `Aberglaube`; **73/73 examples** within L01 networked cards now sense-routed. The other L01 cards without Wortnetz are not automatically erroneous. One marginal figurative `umkreisen` example was replaced with a natural Duden-supported subject `Gedanken`; `weitgehend` front comparative/superlative wording was made clearer.
- Four additional **dictionary-scoped front form checks**: `heißen` (Duden), `umkreisen` (Duden), strong/intransitive and weak/transitive `aushängen` (separate Duden homographs), `weitgehend` / `weitestgehend` (Duden). L01 G2 verified 6→10, still **80** without independent scoped G2 form evidence (not necessarily 80 errors); global 334→338 verified, 1233 outstanding.
- **Release still blocked** by all 90 lacking independent full German–Persian example/card approval and a verified real `German-Flashcards-Pro` import/render receipt. 42 inherited L01 curated HOLD markers remain explicit. **Offline** candidate TSV with 90 rows passed parser roundtrip but is not an app import; full 1571-card QA-only projection passed without field loss. Corpus-wide finite-clause/noncopy heuristic detected 0 of 499 combination items; global exact duplicate-example release check still **FAIL (7 preexisting duplicates outside L01)**.
- Current owner ZIP includes the 90-card final gate ledger, before/after source-backed changes, actual runnable gate and provisional HTML/TSV, with all other lesson card content and 1548 source-map rows unchanged. All cards remain `NONIMPORT`. GitHub decision report `Lessons/L01/PHASE3-RELEASE-BLOCKED-90-CARDS-REPORT-20261108.json`.
- **Next production unit is L02 Phase1/3**, a whole lesson, from the L01-Phase3-current SHA owner. L01 release-blocking dependencies remain in the control plane until genuine independent DE/FA QA and actual app runtime import/render are possible. No 10-word micro-Reviews and no fabricated approval flags.
