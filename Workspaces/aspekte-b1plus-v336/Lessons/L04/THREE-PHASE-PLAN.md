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