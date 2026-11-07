# Lesen B2–C1 — R5 question-level editorial successor (2026-11-07)

**Owner:** `family:lesen` / `Workspaces/lesen-praesentation` (canonical family route).  
**Result:** SOURCE-AWARE QUESTION REVISION + PRE-ENTRY v505 VALIDATION PASS. **NOT** formal Stage4, browser Stage6, Stage7, or CURRENT promotion.

## Exact parent and successor identities

| Role | File / SHA-256 | State |
|---|---|---|
| Immutable curated CURRENT | v1.3.0 ZIP — `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` | UNCHANGED |
| R3 accepted candidate parent | R3 three-unit grammar content — `2b7e29acb973d34e878f76df5135be740c0819934b457265a1fd281ca97c2a8e` | Candidate only |
| R4 verified runtime parent | R3→v505 compiled JSON — `53b2746c2ed2ee6938773d850ccc8a287f2d81608422a38aba481ef059ebc683` | Pre-entry candidate only |
| **R5 content** | `Lesen-Production-Master-v1.3.0-R5-55Q-CANDIDATE.json` — `6371522e011333c836969ae2983c69ecbc259743632a6b44226b3bc5ef7ab764` | New editorial candidate |
| **R5 v505 runtime** | `Lesen-R5-v505-QUESTION-DELTA-RUNTIME-CANDIDATE.json` — `cf66efa8ae1376116b8f9e68e0090b71d47ea964ce2f65c57034df609df5f943` | New pre-entry candidate |

## Editorial scope completed

- Replaced **55 repeated q04 interpretation prompts and model answers** in `LES-PRES-011..068`, excluding already revised 035/051/059. All **68 q04 prompts are distinct** after this pass. These replacements ask questions specific to the existing passage rather than reusing the generic `Warum spielt die konkrete Ausgestaltung eine so wichtige Rolle?` prompt.
- Corrected **three malformed q03 model answers** (lessons 011, 031, 043), including missing causal-clause constructions. Other q03 prompts are unchanged.
- Unchanged: all **68 unit identities**, all **340 question IDs**, source/legacy identity, **478 reading passages and DE–FA–EN translations**, vocabulary, pedagogy/tasks, entire **4620 fulltext grammar occurrence records**, and all R3 changes in lessons 035/051/059.
- This is a **question-level improvement, not a complete reauthoring** of all 55 lessons. Template-derived passage phrasing and other generic question prompts remain.

### Text-specific examples

**011 Studiengebühren:** `Weshalb gelten einkommensabhängige Beiträge als sozial verträglicher als hohe einheitliche Studiengebühren?` Answer references income, scholarships and the social-access concern already expressed in p04–p05.

**031 Smartphones:** `Unter welchen Voraussetzungen kann das Smartphone im Unterricht ein Lernwerkzeug statt einer Ablenkung sein?` Answer specifies rules, bounded use and concrete study tasks supported in p04.

**048 Alternative Heilmethoden:** `Welche Grenzen müssen alternative Heilmethoden nach dem Text einhalten?` Answer names transparent evidence, limits/risks, and no replacement of necessary medical diagnostics; the content is not expanded beyond the existing passage.

## Independent methods and exact app checks

- Independent read-only verifier: **5828/5828 structural, lineage, question mapping and grammar offset checks PASS**, plus **5/5 adversarial in-memory mutations detected**. Grammar offsets are anchored to **section text**, not each sentence; this is checked on all 4620 occurrences. Preserved atypical type metadata in lesson 007 instead of forcing a uniform type profile.
- Exact current v505 Wordlinks R3 module `reading-content-import-v38.js` checked **R5 runtime PASS, 0 warnings**, and rejected **6/6** deliberately corrupted candidates. In-memory pre-entry projection: 68 readings and 340 exercises. No browser IndexedDB transaction, native on-screen presentation or learner-data reload was tested.
- Original R3 content and R4 runtime are independently SHA pinned, and every R5 compiled entry matches the exact new R5 master. **68/68 unit bodies match R4 exactly**; 55 entries changed only in question prompt/answer strings, and 13 entries remain wholly identical.
- AI-authored first-pass language review was performed against p04/p05 evidence. This is not an independent semantic Stage4 assessment of all rewritten answers, nor a human review. All formal acceptance gates remain distinct.

## Remaining work / non-promotions

1. **Question pedagogy:** 58 common q01 prompts, 55 common q02 prompts and 56 common q03 prompts still need targeted editorial review. q04 is now unique, but **55 p04 sections and further passage text** remain highly templated. Do not label 55 lessons as fully reviewed or complete.
2. **R3 grammar fidelity:** historical native nine-lens generator was not recovered/reexecuted. Grammar spans are exact and preserved but not necessarily semantically correct; curate known suspicious labels in a new independently gated content pass.
3. **Trilingual semantics:** further independent DE–FA–EN review needed for all unchanged texts, plus an adversarial second editorial pass on R5 answers.
4. **App acceptance:** v505 exact source validator PASS is **not** actual browser import/IndexedDB persistence or Stage6. Stage7 final not accepted.
5. **Protection:** no modification to established current v1.3.0 ZIP, user browser, app UI, vocabulary SRS/FSRS or older recovery candidates. No deletion/cleanup performed.

## Resume

At next continuation: read owner `QUALITY-REVIEW-CHECKPOINT-R5-20261107.json`; use the exact R5 candidate Master/Runtime SHA, not the original PDF nor a historical v413 importer. Focus next on q01/q02/q03 and higher-risk language/grammar errors by evidence-driven batch. Do not rewrite all passages automatically just to reduce textual similarity; preserve manual decisions and exact existing anchors.