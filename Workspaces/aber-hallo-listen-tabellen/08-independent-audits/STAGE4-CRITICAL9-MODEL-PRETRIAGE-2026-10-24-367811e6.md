# Aber Hallo — critical 9 model evidence pre-triage (2026-10-24)

**Scope:** Read-only, source-exact, model-supported reviewer preparation. `Stage4 BLOCKED`: 0/788 qualified independent reviewer decisions. This receipt does **not** advance Stage4, Stage5, Stage6, or Stage7, does not replace their official gates, and is not an expert signature.

## Reproducible result
- Original registered PDF SHA-256: A1–A2 `4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3`; B1–C2 `ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04`.
- Pinned source / imported working bytes: Canonical `3abbd4984e5cdb69551230c2fb6c1373e559b78e2a5f132eb3f53fb9aa8d180d`; Import `1814139ee65ed0690a1f199b3a29f6eea0af2bbb042018e7b3ceedfdbdf71eef`.
- Pinned critical dossier `308d221b351f988819222235022245dab891af64044176b77d15b4a8b36c0151`; reviewer sheet `aad1780aeb1f080f47ee600137aca03167fe4ee2eaf9d9b4ec4c2e10c2b6e454`; V2 source evidence `8aa2ef7a89b0d0bceb29052c6d08e1b141974ab125405be784211d78b2690ecb`.
- Rechecked 9/9 critical cases, **12/12 PDF-headword-page locators**, **36/36 German examples identical to reviewer worksheet**. No changes to active Canonical/Import, source PDFs or LOCKED historical release.
- Reran independent Stage4 validator v1.1 with exact working authority: 788/788 unsigned, **0 validation errors**, **3,148/3,148 source-evidence mappings**, **0 mismatches**, **0 frozen content edits**, expected return code 1/status `BLOCKED_INDEPENDENT_STAGE4_UNFINISHED`.

## Per-card MODEL hypotheses — qualified review REQUIRED
| ID | Lemma | Proposed independent-review topic | Original PDF page |
|---|---|---|---|
| ahl-lu-0377 | bestimmen | Original source sentence uses inanimate Raumluft + `über`; Duden distinguishes deciding over from influencing. Do not replace source original. | 17 |
| ahl-lu-0488 | leiden | Source attests `um dich leiden`; source-vs-standard valency dispute; Duden supports `an`/`unter` for common patterns. Hold learner-facing `um` for expert. | 19 |
| ahl-lu-0063 | schwellen | Several teaching examples use `anschwellen`; annotate distinct prefixed lemma rather than silently recasting source ID. | 8 |
| ahl-lu-0173 | zusagen | Separate promise/assurance from pleasing someone as sense groups. | 11, 13 |
| ahl-lu-0210 | machen | Label different constructions: offer; `sich aus ... machen`; `sich an die Arbeit machen`. | 12, 19 |
| ahl-lu-0238 | vormachen | Distinguish demonstrate versus deceive. | 13 |
| ahl-lu-0276 | verweisen | Distinguish `jdn. des Landes/Feldes verweisen` from `auf etw. verweisen`; distinct valency. | 14, 22 |
| ahl-lu-0278 | würdigen | Distinguish achievement recognition from `keines Blickes/einer Antwort würdigen`. | 14 |
| ahl-lu-0290 | abmelden | Selected source uses reflexive `sich abmelden`; base lemma also has nonreflexive uses. Require per-sense schema review. | 15 |

Dictionary context (not source substitution): `https://www.duden.de/rechtschreibung/{bestimmen,leiden,schwellen_wachsen,zusagen,machen,vormachen,verweisen,wuerdigen,abmelden}`.

## Durable scoped receipts
- Detailed human-readable local report: `Aber-Hallo-Stage4-Critical-Nine-Model-Pretriage-2026-10-24.md` SHA-256 `0bec9527d0b39b8ecac47800721007a93f6b4d72ea37512402da9e0a3d4b3e6a` (conversation artifact, NOT assumed in Git).
- Detailed structured local evidence: `Aber-Hallo-Stage4-Critical-Nine-Model-Pretriage-2026-10-24.json` SHA-256 `367811e6f12c63d34cc9bfbf0c14def2c4f5cd44b1a65d6b2f935a81d18ccf56` (conversation artifact).
- `LATEST.json` and `CHECKPOINT.json` intentionally untouched; historical `Stage7 PASS` is for the old LOCKED release only. New Stage4 independent qualified review remains pending for all 788.

## Next
An actual qualified independent reviewer decides and signs the 788-unit V2 worksheet and nine key semantic/source cases. Validator v1.1 and manual competence/independence checks must pass before changes are committed to a versioned working successor and official Stages 5–7 are rerun on exact CURRENT Flashcards runtime.
