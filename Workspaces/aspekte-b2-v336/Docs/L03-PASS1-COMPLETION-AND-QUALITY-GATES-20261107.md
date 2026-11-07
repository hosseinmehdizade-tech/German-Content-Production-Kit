# Aspekte B2 – Kapitel 3: Pass 1/3 – vollständiger redaktioneller Entwurf

**Datum:** 2026-11-07 · **Status:** `PASS1_DRAFT_COMPLETE`, **NOT RELEASED / NONIMPORT**.

## Produktionsumfang

- 186/186 aktuelle kuratierte R17-Redaktionszeilen (#1817–2002) verarbeitet, **ohne** das ursprüngliche Lehrbuch/den historischen CSV-Snapshot erneut zum Inhaltsveto zu machen.
- **186 einmalige vorläufige Kartenidentitäten**, jede mit deutschen und persischen Lerninhalten und **zwei individuell verfassten DE/FA-Beispielpaaren**: **372** Paare. Diese Beispiele sind **redaktionelle KI-Neuschöpfungen**, keine behaupteten Buchzitate.
- Die 23 unveränderten nichtleeren bisherigen `source_example_raw`-Felder bleiben als reine Provenienz erhalten. Die geprüften bisherigen R17-Redaktionsentscheidungen sind weiterhin zugänglich.
- Spezifischer `#1920/#1921`-Fall: *die Datumsangabe* hat **eine Kartenidentität**, zwei ursprüngliche Zeilen mit erhaltener Alias-/Beispielinformation; keine Originalzeile oder Lernhistorie gelöscht.
- `#1933`: *die Projektleitung* und *das Projektmanagement* sind unterschiedliche lexikalische Ziele; **zwei** Entwurfseinheiten unter **einer** ursprünglichen Quellen-ID, jeweils mit Beispielen.
- `#1991`: beschädigte Oberflächenform `resp\t respektvoll ... ektvoll` wurde **ausschließlich im Lernentwurf** zu `respektvoll` korrigiert; das ursprüngliche Zeichenmaterial blieb als Herkunftsbeleg erhalten.
- Eine einzelne lexikalische Einheit behält die akzeptierten Verwendungsweisen und mehrere persische Bedeutungen im selben Kartenentwurf; keine Aufteilung nach Sinnzahl und keine künstlich vervollständigten Antonym- oder Synonymlisten.

## Verifizierbarer struktureller Stand und Grenzen

- 186 Entwurfskarten / 186 verschiedene vorläufige IDs; 186/186 Quellzeilen durch 185 Hauptzeilen + Alias #1921 repräsentiert.
- 372/372 neue Satzpaare enthalten deutsche und persische Texte; 23 alte Quellenbeispiele als Herkunft unverändert; überall `export_importable=FALSE`, `linguistic_release_approved=FALSE`.
- Die automatische Strukturprüfung beweist **keine** idiomatische oder grammatische Richtigkeit. Es wurde **keine unabhängige sprachliche Freigabe** durchgeführt; unbekannte cross-level Live-Card-Identitäten bleiben offen. Stage 2/3 sind nicht formal genehmigt, 0 tatsächlich importierbare Karten.
- *Pass 2* soll sämtliche 186 Karten und 372 Paare unabhängig auf Grammatik (auch Rektion und Kasus), genaue Übersetzung, natürliche Wortwahl, Morphologie, Polysemie und identische ältere akzeptierte Karten prüfen. Besondere priorisierte Risiken: #1835, #1844, #1846, #1890, #1917, #1920/#1921, #1928, #1933, #1970, #1975, #1991, #1997 sowie weitere mit verschobenen Gloss-Labels.
- *Pass 3* erfolgt erst bei wirklichem QA-PASS und erforderlichem technischem Test; ansonsten ordentlicher `BLOCKED_NONIMPORT`-Abschluss **ohne** einen vierten Routine-Pass.

## Artefakte

- `Current/L03-PASS1-186-UNIT-CURATED-DRAFT-NONIMPORT.csv`
- `Reports/L03-PASS1-SOURCE-UNIT-EXCEPTIONS.json`
- `Reports/L03-PASS1-STRUCTURAL-QA-RECEIPT.json`

**Ein einziger vollständiger Produktionspass. Kein neues Mikro-Checkpoint-ZIP. Keine Änderungen an Menschen B1/A2, App, SRS, ursprünglichen Büchern oder historischen B2-R17-Dateien.**