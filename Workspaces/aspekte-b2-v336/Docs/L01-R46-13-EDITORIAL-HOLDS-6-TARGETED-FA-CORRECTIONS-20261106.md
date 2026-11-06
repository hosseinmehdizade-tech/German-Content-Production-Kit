# Aspekte B2 — Kapitel 1 R46 · gezielte DE–FA-Korrekturen (NONIMPORT)

**Stand:** 2026-11-06 · **Owner:** Aspekte B2 · **Ausgangsbasis:** verifiziertes R45-CURRENT (158 draft units). Keine Rückprüfung gegen altes Lehrbuch/Original-CSV und keine Änderungen an früheren Lernkarten.

## Tatsächliches Ergebnis

- **13/13 verbleibende R44-Editor-Fälle gezielt gelesen**; **6 präzise Textkorrekturen** an **6 existierenden Einheiten** in neuer R46-Arbeits-CSV vorgenommen, 7 Einheiten unverändert. R45 bleibt historischer Parent.
- Änderungen beschränken sich auf persische Beispiele und die didaktische Reihenfolge zweier bereits dokumentierter Bedeutungen; keine neue Vokabel, keine zusätzlichen / verlorenen Bedeutungen, kein neues Karten-ID.
- **158/158** Entwurfseinheiten haben einzigartige IDs, komplette zwei deutsche+persische Beispielsatzpaare und **export_importable=FALSE**, **linguistic_release_approved=FALSE**.
- **160/160** frühere R43-Quellordinals sind durch 158 draft units plus 2 bereits vorhandene NONCARD-Facetten abgedeckt, einschließlich #1586 split, #1640/#1641 shared unit.
- Die vier bereits bekannten Identity-Gates #1575, #1616, #1630, #1660 bleiben offen; alle **17/17 formalen Release-HOLDs** bleiben formal offen, auch wenn editoriale Empfehlungen vorliegen.

## Konkrete Verbesserungen

| B2-Ordinal | Korrigiertes Feld | Präziser Grund |
|---:|---|---|
| #1556 *abenteuerlich* | Beispiel 2 FA | *gut durchdacht* bedeutet gut überlegt/wohlüberlegt, nicht bloß „geprüft“; persische Aussage daran angepasst |
| #1609 *entscheidend* | Beispiel 2 FA | idiomatische, klarere natürliche persische Konstruktion „نقش تعیین‌کننده‌ای دارد“ |
| #1647 *Ausländerquote* | Rückseite FA | Anteil/Prozentsatz vor regulatorischer Quotenbedeutung; beide zuvor belegten Sinne bleiben auf einer Karte |
| #1675 *einig* | Beispiel 2 FA | vergangene Zeit *brauchten* statt gegenwartszeitlichem „نیاز دارند“ |
| #1693 *Juryvorsitz* | Beispiel 1 FA | *Vorgänger* im Juryleitungskontext präzisiert, Amt bleibt vom Amtsträger abgegrenzt |
| #1697 *Kinokasse* | Beispiel 1 FA | *noch* als „هنوز“, nicht erzwungen „zwei weitere“; natürlichere Ausdrucksweise |

## Unveränderte, gezielt geprüfte R44-Editorial-Fälle

#1586 (zwei echte POS-Lexeme), #1588 (näherliegendes Synonym, eigener lexikalischer Eintrag), #1610 (Partizip + Idiom), #1611 (bei + Dat./für + Akk.), #1640 + #1641 (ein Lernziel mit zwei Quellordinals), #1671 (transitiv **hat** / intransitiv **ist** zerrissen). Das sind in dieser Runde keine unabhängigen finalen Freigaben. Für #1610 ist die Verbindung *in mehrere Teile geteilt* nicht mit der historischen source-only Angabe *in + Dat.* zu verwechseln. 

## QA-Hinweis

Diese Runde ist **ein begrenztes KI-Lektorats- und Struktur-QA**, kein unabhängiger menschlicher oder separates-Modell-Semantik-PASS, kein Stage-2-Gesamt-PASS und kein Stage3–7/Import. Nur die 6 wirklich geänderten Felder und betroffene semantische Abhängigkeiten wurden erneut bearbeitet. Die 4 Identitätsfälle werden nicht durch bloße Schreibgleichheit entschieden. Alte bestätigte Korrekturen werden nicht an Lehrbuchquellen zurückgebunden.

## Dateien / Rückverfolgbarkeit

- `Current/L01-CURRENT-158-UNIT-REVIEW-R46-NONIMPORT.csv` — neue aktuelle **Arbeitsdatei**, SHA256 `fee234ca18900327da7fe24233e9d62fdbc5e7643610c592e81a4cb0a1b5994f`.
- `Reports/L01-R46-6-LINGUISTIC-DELTA.csv` — exakt 6 old→new Feldänderungen.
- `Reports/L01-R46-EDITORIAL-QA-RECEIPT.json` — Hashes, 13 Editorial-HOLDs, 4 Identity-HOLDs, Stage- und QA-Grenzen.
- Unveränderte Eltern: R45-NONCARD (`c74442d8fef409391a2789d06b4abbe13c39b01922c685215a7f0008dda2a10d`); R43-Coverage (`d1bd551c71306247eaedd71de6827c0e4cb4e5b619f8977a184dfa37b71f9bea`); R45-158-Preview (`1ed02a6943b2840aa7ac152d578bd79c409c4fd714a2eaa970e92394e6414ebd`).
- Library/GitHub Currentness: `LATEST.json.latest_scoped_current` verweist auf R46 **erst nach** nachweislich erfolgreichen Datei-Uploads und readback. Globaler Portable Checkpoint **L05 R25 unverändert**.

**Nächster Inhaltsschritt:** 4 bestehende Identity-HOLDs oder separat überprüfbare deutsche/persische Qualitätsprobleme beheben; keine vollständige Altquellen-Wort-für-Wort-Prüfung, keine erzwungenen Sinnbeispielquoten. 