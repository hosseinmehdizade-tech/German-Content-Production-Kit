# Lesen R13 – Abschluss der 16 verbliebenen p04-Vorlagenstarts (7 Nov 2026)

**Familie/Owner:** `family:lesen` / `Workspaces/lesen-praesentation`  
**Status:** R13 CONTENT + v505 PREENTRY RUNTIME **CANDIDATES ONLY**, CURRENT v1.3.0 unverändert.

## Tatsächliche Bearbeitung

- R12 Master SHA256 `a41224ae7a054a959c942afb0b13fcb7d686c76fc27131ec813a9272dad6e7d2` als alleinige inhaltliche Arbeitsgrundlage; keine Rücksetzung auf Quellen-PDF.
- Die 16 vormals generischen p04-Abschnitte der Einheiten 052–058 und 060–068 wurden mit **32 individuell verfassten deutschen Sätzen** (je s01/s03) sowie jeweils synchronisierten FA/EN-Abschnitten aktualisiert.
- Alle 16 vorhandenen p04-s02-Sätze und sämtliche 52 weiteren Einheiten unverändert; besonders **051 und 059** mitsamt allen bisherigen Eingriffen geschützt.
- Der konkrete **wörtlich identische** Abschnittsauftakt „Entscheidend ist deshalb die konkrete Ausgestaltung.“ wurde von 16 auf **0** reduziert. Damit wurden 55/55 ursprünglich identifizierte Starts über R9–R13 bearbeitet. Dies ist **keine** Aussage, dass alle 68 Lektionen sprachlich/gehaltlich fertig sind.
- Q01–Q05 und alle 340 Frage-IDs, 350 Wortschatzeinträge sowie 669 kuratierte Grammatik-IDs identisch zu R12.

## Grammatik und Transport

| Kontrollpunkt | Anzahl |
|---|---:|
| Volltextanker R12 | 4425 |
| Kontextabhängige alte Anker s01/s03 entfernt | 96 |
| Exakt re-anchorte alte s02-Anker | 44 |
| Neue manuell belegte KII-Formen | 16 |
| Retargetete kuratierte g07-Verweise | 8 |
| Volltextanker R13 (exakte Offsets) | 4345 |
| Laufzeit-Einträge R13 geändert | 16 |
| Laufzeit-Einträge byteinhaltlich gleich R12 | 52 |

Die native neun-Linsen-Quellgrammatik wurde **nicht** neu ausgeführt. Alte Anker, deren Text gelöscht wurde, wurden dokumentiert entfernt; eine Verringerung der Ankerzahl ist kein Verlustnachweis oder vollständige linguistische Prüfung.

## Testbefund und Grenzen

- Unabhängiger, nur lesender Struktur-/Quellvergleich: **13790 Checks, 0 Fehler**, 9/9 Korruptionsproben korrekt erkannt.
- Die echte JavaScript-Quellvalidierung des aktuellen v505-Moduls `reading-content-import-v38.js` meldet **PASS, 0 Warnungen**, 7/7 negative Fälle erkannt, isolierte In-Memory-Projektion 68/340.
- Browser-/IndexedDB-Import, Wiederladen, User-SRS/FSRS und Integration mit UI **nicht** ausgeführt. **Stage6 NOT_RUN; Stage7 NOT_RELEASED**.
- Eigenständige Vollprüfung der DE–FA–EN-Semantik über alle 68 Einheiten **nicht** abgeschlossen; **Stage4 HOLD**. Bei 14 Einheiten beginnt p03 weiterhin wortgleich mit „Dem stehen jedoch gewichtige Einwände gegenüber.“; weitere repetitive Muster bleiben (einschließlich der vorläufig beibehaltenen p04-s02-Sätze).

## Verifizierbare Dateipins

- Content: `Lesen-Production-Master-v1.3.0-R13-16P04-TRILINGUAL-CANDIDATE.json`, SHA256 `d619d7d9777849a25a154b52574b66a3dd92fc4f4d045e7b4ceb4e0fbc16b30f`, 6381296 bytes.
- Runtime: `Lesen-R13-v505-16P04-RUNTIME-PREENTRY-CANDIDATE.json`, SHA256 `628f56e6bab608a6ab5f7a8939eea3a8451f1fbc4a8699bcaeb23a56f10d78a7`, 6863186 bytes.
- Detailed before/after and grammar: `LESEN-R13-16P04-TRILINGUAL-GRAMMAR-LEDGER.json`.
- Scoped review: `LESEN-R13-TRILINGUAL-SCOPED-REVIEW.json`; QA: `LESEN-R13-INDEPENDENT-STRUCTURAL-QA.json` and `LESEN-R13-v505-NATIVE-PREENTRY.json`.
- Durable candidate registration and Library readback must be checked before GitHub-backed completion is claimed; the source-owner current ZIP has SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.

**Next bounded outcome:** Analyze and repair generic p02/p03 claims without indiscriminately rewriting all sections. Then perform independent trilingual semantic QA and real isolated browser/IndexedDB Stage6 before publication. No UI change and no user review-state modification.