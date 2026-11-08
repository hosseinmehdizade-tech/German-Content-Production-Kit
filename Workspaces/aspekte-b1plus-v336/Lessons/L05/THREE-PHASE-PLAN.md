# Aspekte B1+ L05 — verbindlicher Drei-Phasen-Plan

**Stand: 2026-11-08 · Phase 2/3 abgeschlossen (redaktionell); Phase 3 offen; NONIMPORT.**

## Phase 1 / Gesamtprüfung — DONE
Alle 155 Lernkarten (156 originale Source-Zeilen; 610/611 sind als bestehende Lern-Einheit korrekt verknüpft) einmal vollständig mit strukturierter Prioritätsliste auditiert. Die 155 Entscheidungen der Vorstufe bleiben nachvollziehbar.

## Phase 2 / Gesamtkorrektur — DONE (redaktionell, nicht unabhängige Freigabe)
- **155/155 Karten** wurden redaktionell auf Wortbedeutung, Vorderseiten-Formen, Bilingualität und Nutzung überprüft und in **einem einzigen, auf die ganze Lektion bezogenen Lauf** entschieden.
- **30 Karten** bekamen tatsächliche Änderungen des Lerninhalts, **125 Karten** wurden ohne Textänderung weitergeführt. **44 Vorher/Nachher-Feldänderungen**, **21 zusätzliche Karten mit strukturierter Bedeutungsaufteilung / 56 neue Sinnblöcke**, **7 neue DE–FA-Beispielpaare**; bestehende akzeptierte Bedeutungen in derselben Karte belassen.
- **384** Beispielpaare der Lektion wurden redaktionell gesichtet, jedoch **0 unabhängig freigegeben**. Vorherige scoped Formattestierungen **106**, fehlende **49**, ohne automatisches Schlussfolgern, dass alle 49 falsch sind.
- **28** vorhandene L05-HOLD-Marker bewusst nicht stillschweigend freigegeben.
- Vorhandene Source-Map (1548 Zeilen) **byteidentisch**, L05-Originalbezüge (156) erhalten; alle anderen Karten außerhalb L05 unverändert.
- **437** Kombinationen corpusweit auf exakte Beispielkopie/konservativ erkannte vollständige Sätze kontrolliert: 0 erkannt; 7 alte exakte Beispieldubletten außerhalb L05 bleiben. **1571 Front/Back-Vorschauen** wurden als NONIMPORT-Testprojektion ohne Feldverlust geprüft.
- Aktueller **Library-Owner**: `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Reports/Aspekte-B1plus-L05-PHASE2-WHOLE-LESSON-155-CARDS-CORRECTED-NONIMPORT-20261108.zip` (SHA256 `e7e2a1c6437043b929fef601f69e4742a7e368c81d80706585f04f9b7e9de493`). Darin liegen Kartenledger, Vorher/Nachher, Berichte, die dynamische 155-Karten-HTML-Vorschau und ein ausführbarer QA-Validator. Library-Byte-Readback/ZIP-CRC/155 Mitglied-Hashes PASS.
- GitHub report: `Lessons/L05/PHASE2-COMPLETE-155-CARDS-REPORT.json`.

## Phase 3 / Unabhängige Endprüfung & Export — NEXT, noch NICHT fertig
1. **Alle 155 Karten unabhängig** auf Deutsch–Persisch-Sinn, Grammatik, Beispiele, Relationsgenauigkeit und bestehende QA-HOLDs überprüfen; dabei 49 Formen ohne unabhängige Attestierung und 28 alte HOLD-Marker ausdrücklich entscheiden. **Kein stilles Passen durch Software-Erfolg**.
2. Automatischen ganzen Lektionsgate (incl. Wortnetz/Kollokations-Nichtkopie, Beispiel-Integrity, Source-Links, Front-only Formen) auf zuletzt bearbeitetem Owner ausführen.
3. Echte App-Import-/TSV- und gerenderte Front/Back-Probe. Ohne angebundenen/prüfbaren Importer Veröffentlichung blockieren und offene Fälle klar benennen. Für endgültig freigegebene Karten tatsächliche Exportergebnisse erzeugen.
4. Ein Abschlussbericht pro Lektion, kein Wiederbeginn mit Review18/Review19 und zehn Karten pro Antwort.

## Unveränderte globale Schranken
G2 extern attestiert **331/1571**, 1240 ohne externe Attestierung; global 340 HOLDs und 7 alte Beispieldubletten, alle vollständigen G4-Release-Freigaben weiterhin 0. **G5 echte App-Importprüfung PENDING, G6 BLOCKED, keine importierbare Freigabe.**

Die drei Phasen sind Meilensteine, keine automatische Garantie, dass jedes problematische Wort in drei mechanischen Schritten genehmigt werden kann. Offene Wörter dürfen nach Phase 3 begründet HOLD bleiben, dürfen aber nicht zu neuen zehnwörtigen Review-Zyklen zurückfallen.


## Phase 3 / Release-Gate ausgewertet — 2026-11-08 · Ergebnis BLOCKED, nicht freigegeben

- **Phase 3 wurde für alle 155 Karten als expliziter, fail-closed Release-Gate ausgeführt**, nicht als neue 10-Wort-Review. Ergebnis **0 von 155 freigabefähig**. Das ist eine dokumentierte Sperrentscheidung, kein falscher Abschluss als importierbares Deck.
- **140 echte neue DE–FA-Beispiel-zu-Sinn-Verknüpfungen** über 46 Wortnetz-Karten; jetzt **151** vorhandene eindeutige Verknüpfungen bei 384 Beispielen der Lektion. **Ein** Beispiel `sich verständigen` bleibt wegen doppeldeutiger Aussage explizit ungeklärt; keine erzwungene Bedeutungszuordnung.
- **Drei neue unabhängige Duden-Formnachweise** inkl. korrigierter sichtbarer Front: `die Muse – die Musen`, `der/die Gesprächspartner/in` mit je eigenem Plural, `das Kraftfutter – die Kraftfutter` (Genitiv ebenfalls). G2 von **106 auf 109 in L05**, global **331 auf 334**; L05 **46** Formnachweise offen.
- **28 alte kuratierte L05-HOLD-Marker bleiben erhalten**; 7 alte Beispiel-Dubletten in anderen Lektionen weiterhin Release-Sperren. Weitere Freigabe-Hindernisse: noch **nicht unabhängig final abgenommene zweisprachige Beispiele in allen 155 Karten** sowie fehlender echter `German-Flashcards-Pro`-Import-/Rendertest. Diese Bereiche wurden nicht künstlich auf PASS gesetzt.
- Konservative Kollokations-/Satzstruktur-Prüfung über 1571 Karten/437 Kombinationen PASS, exakte Dubletten-Release-Prüfung **FAIL (7)** wie gewünscht; 1571-Karten HTML-QA-Projektion PASS, 155-Zeilen-TSV-Offline-Roundtrip PASS, **kein echter App-Import**. Der strenge L05-Release-Gate endet mit Status **BLOCKED** und fehlercode 1; dadurch kann nicht versehentlich veröffentlicht werden.
- Current nonimport Owner: Library `libfile_8e25215035b48191a9481393e7856510`, SHA256 `b5e470617bd72a34e6ab6236ba3232d247d2a1ee0a45f35126e5c7beed6e41f6`; 2.995.170 Bytes, 167 ZIP-Member, 166 SHA-Checks, Library exact readback/CRC PASS.
- GitHub report: `Lessons/L05/PHASE3-155-CARD-RELEASE-GATE-BLOCKERS-20261108.json`. Reusable strict gate: `Tools/qa_lesson_release_gate_v1.py`. Vollständige 155-Karten-Entscheidungen, Sachstand und nicht-freigegebenes TSV/HTML im Owner-Archiv.
- **Phasenabschluss der Lektion:** (1) AUDIT DONE, (2) EDITORIAL DONE, (3) RELEASE GATE EVALUATED → **BLOCKED**. Diese Lektion nicht durch Review18 usw. erneut anfangen. Auflösung der expliziten Release-Abhängigkeiten bleibt ein eigener Freigabevorgang, sobald echte App-Tests und unabhängige sprachliche Abnahmen möglich sind. **Nächste allgemeine Produktionslektion: L01 Phase1**, nicht L05-Vokabeln in 10er-Stücken.
