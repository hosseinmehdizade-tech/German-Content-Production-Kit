# Aspekte B1+ · Lektion 03 — verbindlicher Drei-Phasen-Plan

**Stand: 2026-11-08 · Phase 2/3 DONE (reale sinnbezogene Gesamtkorrektur); Phase 3 QA/Release NEXT; NONIMPORT**


## AKTUELL: Phase 2/3 WHOLE-LESSON EDITORIAL DONE — maßgeblicher Owner

**Neueste kuratierte Karten-Quelle**: L03 Phase2 ZIP in der B1+-Library `libfile_0854bc8cdc548191942e8e2656355a02`, SHA256 `5141503a0b1a7a70e4a4286e04d9f72ce0fa1b928f72bb1e34aca90e42fd5539`, 3.292.988 Bytes, 213 Mitglieder / 212 SHA256-Manifestprüfungen; vollständiger Library-Byte-Readback und ZIP-CRC PASS. Der unten genannte L02-Phase3-Owner ist **nur** der unverändert verifizierte Parent, nicht mehr der gültige aktuelle Owner. Nicht zum Original-Curriculum zurücksetzen.

**Eine vollständige Lektionseinheit**: alle **194/194** Karten mit nachvollziehbarer struktureller Einzelentscheidung, davon **60 echte Inhalts- oder QA-Metadaten-Änderungen** und **134 strukturell geprüft ohne Änderung**, **43** neue Wortnetz-Karten mit **96** Sinnblöcken, **95 neue nach Bedeutung gebundene zweisprachige Kombinationen**, **154** neu gesetzte Beispiel→Sinn-Links. Die bestehenden 13 Wortnetz-Karten haben ihre 26 bislang unzugeordneten Beispiele nun eindeutig gebunden. Vier neue, eigenständig formulierte DE–FA-Beispiele, L03 432→436 Paare, **26** bisher ohne Status nun explizit PENDING und **9** Wörter mit auf ihren genauen Formumfang begrenzter Duden-Attestierung (L03 3→12, global G2 357→366). Diese 9 Wörter sind `ruhen`, `verraten`, `verschenken`, `geraten`, `übergehen`, `ausscheiden`, `verfügen`, `weitsichtig`, `zusprechen`. Besonders trennbares `übergehen: ist übergegangen` vs. untrennbares `übergehen: hat übergangen`; `ausscheiden` mit `ist` (intransitiv) und `hat` (transitiv).

**Strenge Lerninhaltsprüfung:** vier problematische neue Kombinationen, die wortgleich als längerer Teil eines Beispiels auftauchten, wurden vor Veröffentlichung der ZIP korrigiert. Anschließend drei konservative Kontrollskripte für corpusweit **656 Kombinationen** PASS (0 gemeldete Kopien, vollendete Sätze oder finite Satzverdachtsfälle). Die Wörter mit ganzen Aussagen (`Bloß kein Stress!`, `Lachen ist die beste Medizin.`, `Es ist ganz natürlich, dass …`) wurden als Phrase/Satzmuster klassifiziert, nicht als falsche Substantiv- oder Verbkarten. Alle 194 L03-Lernkärtchen samt **436** Beispielen im QA-only HTML: jedes DE-Beispiel exakt einmal unter seinem Sinn oder bei Worten ohne Sinnnetz; 194 TSV-Kandidatenzeilen offline wieder eingelesen. Der echte App-Importer **wurde nicht getestet**.

**Bewahrungs- und Release-Gate:** alle 1.548 ursprünglichen Source-Map-Zeilen **byteidentisch**; 1.571 Karten samt IDs erhalten, jede Karte außerhalb L03 unverändert. Bestätigte Originalzuordnung 206/207 und Verknüpfung 296↔36 ebenfalls erhalten. **41 L03 kuratierte HOLDs** bewusst nicht gelöscht, **182 L03-Formen** noch ohne individuellen Duden-Beleg (nicht zwingend Fehler), global noch **sechs exakte in-card Beispiel-Dubletten außerhalb L03**. Der strenge Release-Gate ergab erwartungsgemäß **194/194 RELEASE_BLOCKED**, wegen fehlender kompletter QA-Freigabe und fehlendem echten German-Flashcards-Pro Import/Render-Receipt. Keine Fälschung von Freigabe-Flags; **0 vollständige Karten freigegeben**.

**Reproduzierbarkeit:** im ZIP `Lessons/L03/L03-PHASE2-194-CARDS-CONTENT-REPORT.json`, `Lessons/L03/L03-PHASE2-BEFORE-AFTER-EDITS.json`, vollständige 194-Karten-Dispositionsliste, ausführbares Elternvergleich-Skript, HTML QA und NONIMPORT TSV. GitHub Receipt `Lessons/L03/PHASE2-194-CARD-EDITORIAL-RECEIPT.json`, Quellskript `Tools/build_L03_phase2_v1.py`, Differenz-Checker `Tools/qa_L03_phase2_parent_diff_v1.py`. Keine neuen 10er-Review-Milestones.

**Phase 3/3 verbindlich NEXT:** den Sprachinhalt aller 194 Karten gezielt freigabeprüfen, ohne einen externen Dritten zu verlangen oder nur Statusfelder maschinell freizuschalten; 182 offene G2-Nachweise nach Bedarf regelbasiert/lexikalisch klären, 41 kuratierte HOLDs mit Fallbegründung entscheiden und möglichst den **echten** App-Importer samt Darstellung testen. Falls Release-Gates nicht erfüllt: als eindeutige BLOCKED-Entscheidung beenden und nächste ganze Lektion starten. Änderungen nur nach nachgewiesenem Sachmangel, keine Wiederholung der 194-Karten-Phase2.

## Historischer Phase1-Stand / Authority & scope (nicht mehr aktueller Owner)

- **Aktueller Kuratierungs-Owner bleibt unverändert:** Das aus der B1+-Library SHA-geprüfte L02-Phase3-ZIP, SHA256 `39caaa7bab3b32b9e220a9c39ac2854942a12e4735cd584d52fd8b695c86f5a3`, Library `libfile_58465ea42efc8191a4176d2e56497528`. **Kein** Rückfall zur ursprünglichen Lehrbuch-/CSV-Datei und **kein** Neubau von Karten in Phase 1.
- **194 bestehende L03-Lernkarten** entsprechen **195 ursprünglichen Source-Ordinals 163–357**. Ordinal 207 ist bereits mit Karte 206 **`einander nahestehen`** zusammengeführt und daher nicht verloren. Die Karte **`beschäftigt mit + Dativ`** (296) enthält außerdem die beabsichtigte Cross-Lesson-Quellenverknüpfung zu Ordinal **36**. Alle 195 Source-Rows sind verknüpft, und die vollständige Projektmap bleibt mit **1548** Originalzeilen und **1571** Karten erhalten.
- **194/194** strukturell inventarisiert und mit einzelnen Entscheidungen/Prioritäten erfasst: **P1 54**, **P2 46**, **P3 94**. Diese Risikobewertung ist **keine** Behauptung, dass jede P1/P2-Karte fehlerhaft sei oder dass P3 bereits freigegeben sei.

## Befunde der gesamten Lektion

- **432 deutsche/persische Beispielpaare**, keine leeren DE/FA-Textfelder, keine Karten ohne Beispiele, 0 exakte innerhalb derselben L03-Karte doppelte DE-Beispiele. **26 Beispiele ohne QA-Status** auf **23 Karten**, **402** mit PENDING, **2** mit älterer, *nur scoped* QA und **2** mit alternativer Pending-Markierung. Statuslücken in Phase 2 schließen, ohne automatisch `APPROVED` zu setzen.
- **Nur 3/194 Karten besitzen bereits extern belegte G2-Formatteste**, **191/194** fehlen noch solcher Belege. Fehlender Beleg ist **nicht** gleich falsche Flexion. Bereits belegte Ordinals: **167 `der Rat`**, **253 `umgehen`** und **326 `der Anteil`**.
- **41 alte Inhalts-HOLD-Marker** in L03; diese sind unabhängig von fehlendem G2-Beleg pro Fall zu bewerten und dürfen nicht pauschal als erledigt gelten.
- Bestehendes, bedeutungsgebundenes Wortnetz in **13 Karten / 19 Sinnblöcken**. Dort fehlen **26 Beispiel→Sinn-Zuordnungen in 13 Karten**, unter anderem `der Rat`, `also`, `beziehungsweise`, `der Anteil`, `immer mehr`. **Sinn zuerst prüfen**, dann bei eindeutiger Semantik richtig verbinden; niemals blind automatisch zuordnen.
- **`Bloß kein Stress!`** (Ordinal 301) ist ein ganzer Ausdruck und muss als Satz-/Wendungskarte validiert werden, statt ihn reflexhaft zu einem einzelnen Lemma umzuformen.
- **76 mehrdeutige/Rektions-/Register-Prüfhinweise** (keine automatischen Fehlerentscheidungen). Eine Aufzählung durch persische Semikolons kann *Synonyme* und nicht verschiedene Bedeutungen meinen: **keine Pflicht zur sinnlosen Wortnetz-Aufspaltung**.
- Im gesamten Korpus außerhalb L03 bestehen **6 historische exakte DE-Beispieldubletten**; strenger Release-Gate bleibt bei deren Existenz BLOCKED.

## Phase 2/3 — one whole-lesson editorial pass, NEXT

1. **Alle 194 Karten** einmal als ganze Lektion sprachlich kontrollieren: korrekte DE-Lemmaform und Vorderseiten-Flexion (nötigenfalls extern/regelorientiert belegen), alle bestehenden und fehlenden Bedeutungen, natürliche Deutsch–Persisch-Übersetzungen, Beispielqualität und Trennung der Wortnetz-Sinne nur wenn semantisch gerechtfertigt.
2. **P1 54** vor **P2 46** vor **P3 94**, jedoch jede Karte in derselben Phase abschließend redaktionell disponieren. Die **26 QA-Status-Lücken**, **26 fehlende Beispiel→Sinn-Routen**, **41 HOLDs** und die Kartenformat-Frage für `Bloß kein Stress!` ausdrücklich dokumentieren. Keine 10-Karten-Review-Schleifen.
3. Identische Quelle/IDs, schon kuratierte Mehrfachbedeutungen und die 206/207- und 296/36-Quellbeziehungen **verlustfrei bewahren**. Jede echte Änderung mit `before/after`/Ordinal dokumentieren, **unveränderte** Karten nicht als bearbeitete Inhaltskorrekturen zählen. Release- und App-Import-Flags bleiben vor Phase 3 `false`.
4. Eine **einzige aktualisierte L03-Owner-ZIP**, alle 194 Dispositionen, QA-Ergebnisse, Front/Back-Preview und ein validierbares Change-Ledger erzeugen und in Library sowie GitHub synchronisieren.

## Phase 3/3 — independent content QA and real runtime gate

- Alle 194 Karten auf deutsche/persische Bedeutungen, Grammatik/Valenz, Beispiele, passende `Synonyme`/`Antonyme`/`Kombinationen`, Satzmuster und Front/Back prüfen; kontrollierte, belastbare G2-Formregeln und tatsächliche Sonderfälle getrennt festhalten.
- Automatisierten globalen Noncopy-/Finite-Clause-Test und strenges Dubletten-Release-Gate durchführen, anschließend den **echten German-Flashcards-Pro-Importer/Renderer** prüfen, nicht nur HTML oder TSV offline parsen. Fehlende App-Verbindung ist ein expliziter BLOCKER.
- Einzelne Karten nur bei allen erfüllten Gates als released markieren, sonst `RELEASE_BLOCKED` mit per-card Gründen. Keine Schein-Freigabe, kein blindes Entfernen aller HOLD-Marker.

**Reporting:** Pro Nachricht nur tatsächliche Fortschritte, Stufe, Zahlen, persistenter Owner/SHA, verbleibende Blocker und nächster Schritt; keine zusätzlichen Review-Mikrobatches.
