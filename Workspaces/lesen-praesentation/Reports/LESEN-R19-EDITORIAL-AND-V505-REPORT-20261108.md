# Lesen R19 — zehn begründete eigene Positionen (p06-s02, Lektionen 011–020)

**Stand 08.11.2026:** scoped editorial + structural QA **PASS**; **R19 CANDIDATE**, nicht CURRENT, nicht FINAL.

## Autorität und Änderungen

- Parent ist das nutzerkuratierte **R18**, nicht ein älteres Lehrbuch. Master SHA `bfd469d4027f59d97cb25baabbefd79b0576f47f13acdc965f82850fc8a63c37`.
- 10 identische, sehr generische Schluss-Sätze der eigenen Position (`p06-s02`) in **LES-PRES-011–020** durch konkret zum Unterrichtsthema passende DE-Sätze ersetzt; jeweilige `p06-s01` und alle anderen Abschnitte unverändert.
- **8 FA/EN-Absatzpaare** im genauen Schlussteil angepasst; die in 018 (ehrliches, konkretes Lob/Kritik) und 020 (Bedürfnisse und Studienqualität) bereits sinnvollen Übersetzungen **unverändert** übernommen.
- 58 von 68 Master-Einträgen und exakt dieselben 58 Runtime-Einträge unberührt. 340 Fragen, 350 Vokabeleinträge, 669 kuratierte Grammatikreferenzen erhalten.
- 48 identische ursprüngliche `p06-s02` verbleiben. Andere wiederholte Muster in p01/p07 noch nicht ganzheitlich verbessert.

## Belegbares Beispiel

**Lektion 018 — Wie viel Lob brauchen Kinder?**

- **Vorher DE:** Wichtig ist, dass die Entscheidung nachvollziehbar begründet wird und nicht allein auf Gewohnheit, Idealvorstellungen oder kurzfristigen Eindrücken beruht.
- **Jetzt DE:** Deshalb sollten sowohl Lob als auch Kritik ehrlich, konkret und auf die Entwicklung des Kindes ausgerichtet sein.
- **FA bereits passend, unverändert:** مهم این است که تحسین و نقد هر دو صادقانه، مشخص و با هدف کمک به رشد کودک باشند.
- **EN bereits passend, unverändert:** Both praise and criticism should be sincere, specific, and aimed at helping the child grow.

Alle 10 vorher/nachher DE/FA/EN-Paare stehen im JSON-Ledger `LESEN-R19-10P06-EDITORIAL-GRAMMAR-LEDGER.json`, SHA `e799debf5af8fa72ba2a349072faa7e52b2ec7d67076badcde4be70d34de2b56`.

## Grammatik — ehrliche Scope-Abgrenzung

- Vorher 4041 gültige Fulltext-Vorkommen. 40 ursprüngliche Marker an den ersetzten generischen `p06-s02`-Sätzen entfernt; 10 neue am real vorliegenden Satzbau kontrolliert annotiert (u.a. **damit, wenn, ob, weil, um … zu, sollte/sollten**).
- **Jetzt 4011 exakt positionierte Vorkommen** im Master **und** im abgeleiteten v505-Runtime. Die übrigen Marker und alle 669 kuratierten Grammatik-IDs unverändert.
- Neuannotationen tragen klar `R19_MANUAL_SCOPED_EDITORIAL`; **der ursprüngliche 9-Linsen-Generator wurde NICHT neu ausgeführt**. Geerbte historische Wortzählungsmetadaten wurden nicht pauschal überschrieben. Master 001 hat unverändert neun statt sieben Abschnitte; die unabhängige QA akzeptiert das nach Parent-Abgleich.

## Read-only und v505-Prüfung

- Unabhängige lesende Quell-/Runtimeprüfung: **15,569 / 15,569 PASS**, 0 Fehler; **9/9 mutierte Testfälle abgewiesen**.
- Exakt dieselbe Datei `reading-content-import-v38.js` wie im gepinnten v505-App-ZIP, SHA `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`: **PASS, null Warnungen**, **10/10 gezielt defekte Runtime-Payloads abgelehnt**.
- Isolierte In-Memory-Projektion **68 Lerneinheiten / 340 Aufgaben** erfolgreich, 478 Textabschnitte in DE/FA/EN. **Keine echte Browser-IndexedDB-Transaktion:** Stage6 ist weiterhin **NOT_RUN**.
- Vollständige unabhängige semantische DE/FA/EN Stage4 **HOLD**; Release Stage7 **NOT_RELEASED**.

## Kandidaten, SHA-256 und Ablage

- Content: `Lesen-Production-Master-v1.3.0-R19-10P06-TRILINGUAL-CANDIDATE.json`, `1a1fa9be4f61dd34a04264050cf12531168cd75920517f3d9315780b11acf4ff`, 6,093,368 Bytes; Library `libfile_74cb63a2ec84819191908243c70bcd16`. **Post-upload SHA256 und Byte-CMP PASS.**
- Runtime: `Lesen-R19-v505-10P06-RUNTIME-PREENTRY-CANDIDATE.json`, `365b774d8478bd98f6e111cafa66677abc1688cad76674102f6061109825254f`, 6,542,312 Bytes; Library `libfile_8e980e361f14819180b059014e63e3d5`. **Post-upload SHA256 und Byte-CMP PASS.**
- Unverändertes CURATED CURRENT ZIP v1.3.0 SHA `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.

## Weiter

Die **48** verbleibenden `p06-s02` nach Qualität und Sinn, nicht bloß automatischer Variation, in begrenzten Gruppen bearbeiten. Weitere Qualitätsrisiken in Einleitungen/Synthesen (p01/p07) und vollständige Sprachprüfung pro 68 Lerneinheiten separat priorisieren. Keine UI-, FSRS-, Fortschritts- oder andere Familienänderung.