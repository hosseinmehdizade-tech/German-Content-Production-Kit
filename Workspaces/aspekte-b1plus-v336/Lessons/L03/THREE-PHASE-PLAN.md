# Aspekte B1+ · Lektion 03 — verbindlicher Drei-Phasen-Plan

**Stand: 2026-11-08 · Phase 1/3 DONE (vollständige Struktur- und Risikoinventur); Phase 2 NEXT; NONIMPORT**

## Authority & scope

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
