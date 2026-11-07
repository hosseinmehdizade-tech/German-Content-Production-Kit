# Aspekte B2 — Kapitel 2, PASS 1 / 3: vollständige bearbeitbare Kartenproduktion

**Datum:** 2026-11-07 · **Status:** vollständiger *Entwurf*, ausdrücklich **NONIMPORT**. Die Nutzerregel lautet höchstens drei echte Arbeitsblöcke pro Lektion, ohne Absenkung der Qualitätsanforderungen.

## Reale Ergebnisse

- **108 / 108** source-owned, schon redaktionell bearbeitete R14-Wortschatzzeilen (1709–1816) repräsentiert; **110** unterschiedliche Karten-Identitäten als **vorläufiger Vorschlag**, weil **#1727** (`einsprachig` / `monolingual`) und **#1742** (`unterfordern` / `überfordern`) zwei verschiedene lexikalische Einträge in einer Zeile führen.
- Bestehende **12** R15-Entwürfe in sämtlichen ursprünglichen 14 CSV-Feldern unverändert übernommen; **98** ergänzende neue Lerner-Entwürfe für den Rest derselben Lektion tatsächlich mit **196 neuen DE–FA-Beispielpaaren** geschrieben. Total: **220** DE–FA-Beispielpaare.
- Jede der **110** Einheiten enthält deutsche Form, persische akzeptierte Bedeutung(en), zwei vollständige natürliche DE/FA-Satzpaare und redaktionell geprüfte gebräuchliche Kombinationen; gezielte sense-scoped Synonyme/Antonyme nur, wo plausibel und belegt. Falsche Zwangs-Antonyme werden nicht erfunden.
- Redaktionsfelder: Original-R14-Feldangaben/Satzbeispiele für Herkunft erhalten; KI-erstellte Beispiele explizit von ursprünglichen Beispielen getrennt; separate Sense-Zuordnung für mehrdeutige Einheiten, **ohne** mehrere Karten pro Bedeutung.
- Duden-spezifisch gegengeprüfte Sonderfälle: *unterfordern* vs. *überfordern*, *touren* mit `hat/ist`, *stürmen* mit `hat/ist` kontextabhängig, musikalisches *phrasieren*, *Umschulung* Beruf und Schulkontext, gewöhnlich singularische *Gunst*, *smart* clever/elegant.
- Echte Original-R14-HOLDs **#1763 verschuldet** und **#1799 gezeichnet sein** bleiben zur **unabhängigen** semantischen Freigabe sichtbar, nicht wegdefiniert. Redaktioneller Tippfehler **#1805 am poetischstenetisch** ist im Preview zu **am poetischsten** korrigiert, der R14-Beleg blieb unverändert.

## Sicherheit und Grenzen

- PASS 1 strukturelle Readback-Prüfung: Quelle und R15 über SHA256 verifiziert, **108** eindeutige Zeilen, **110** eindeutige neue Lern-IDs, **220** zweisprachige Paare, keine leeren Front/Back/Satzfelder, **110** Kombinationseinträge; beide Doppelzielzeilen haben je **zwei** belegte Ziel-IDs; Import-/Release-Felder durchgehend FALSE.
- Die 12 alten Entwürfe wurden nicht noch einmal umgeschrieben. B1, A2, SRS, ursprüngliche R14-Daten und ältere Checkpoints **nicht verändert**. Keine QUELLE-EXACT-Behauptung für KI-Sätze.
- **Diese Prüfung ist keine unabhängige Sprachfreigabe.** PASS 2 muss alle 110 Karten einschließlich **220** Satzpaaren eigenständig qualitativ prüfen, die fokussierte Prüfqueue bearbeiten und Fehler korrigieren. PASS 3 kann erst nach tatsächlichen technischen und linguistischen Gates eine Importdatei liefern oder muss BLOCKED begründen.

## Aktuelle Arbeitsdateien

- `Current/L02-PASS1-110-UNIT-WORKING-NONIMPORT.csv` (SHA256 `b52649b3c7d68916c5022b9dfc10032a35f5bec79c3cdb1ce4bd2942e3b9948d`)
- `Reports/L02-PASS1-QA-RECEIPT.json`
- `Reports/L02-PASS2-FOCUSED-REVIEW-QUEUE.csv` (16 spezifische Einheiten mit erhöhtem Prüfbedarf, neben der vollständigen Prüfpflicht für 110 Karten).

**PASS 1: COMPLETE DRAFT (NOT RELEASED). PASS 2: PENDING. PASS 3: PENDING.** Keine weiteren Mini-Runden und keine Rückkehr zum alten Buch.