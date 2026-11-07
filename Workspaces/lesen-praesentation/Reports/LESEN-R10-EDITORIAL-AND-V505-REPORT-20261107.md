# Lesen – R10 trilingual p04 editorial batch / v505 source-preentry evidence (2026-11-07)

**Project owner** `family:lesen`, canonical `Workspaces/lesen-praesentation`.

## Authority and outcome

- Editorial authority before edit: R9 content JSON SHA256 `52667254d47987e5f4c4146078fd2c8204e80152de3268cd0eb599fc0c2f8171`; Runtime R9 SHA256 `115a988c339f6fa392091727a7aab10f4456d6b7e04e7678492867e785e5aa59`.
- R10 CONTENT candidate `Lesen-Production-Master-v1.3.0-R10-10P04-TRILINGUAL-CANDIDATE.json`: SHA256 `4be5bf368b23a1a46bae2d28686b3d4f9336ac01d98c2c1449ab19df81b9509a`, **6,536,484 bytes**.
- R10 v505 preentry Runtime candidate `Lesen-R10-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json`: SHA256 `e2e5d395679f772f7ec4cf845da4af2aadb148f3362b3ed3955ed76d280e9aa3`, **7,035,158 bytes**.
- **Neither is CURRENT nor release-ready**. Current curated source-owner v1.3.0 ZIP SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` stays unchanged.

## 10 lesson-specific corrections

Lessons `LES-PRES-021` through `LES-PRES-030`: Alumni associations; school crafts; professional development; home/library study; learning organization; films/books; parental preparation for university; foreign-language learning; adapting historical literature; studying at a prestigious university. For every lesson the generic p04 opening and ending are replaced by **two topic-grounded German sentences**, and the complete Persian and English p04 translations are rewritten accordingly. The original topic-specific `p04-s02` is preserved verbatim in all ten. Editorial basis is existing R9 `p02`, `p03`, `p05` and `p04-s02`—not the historical unedited PDF.

### Illustrative comparison

**LES-PRES-021** new p04 starts: `Ein Alumni-Verein hilft beim Berufseinstieg nur dann wirklich, wenn Kontakte nicht zum Privileg gut vernetzter Absolventen werden.` The ending addresses deliberate inclusion of graduates with limited network access; the middle sentence about open, transparent entry-level offers is unchanged. Both FA and EN reflect these claims.

**LES-PRES-028** new p04 starts: `Beim Sprachenlernen ist nicht Fehlerfreiheit der wichtigste Maßstab, sondern ob man die Sprache tatsächlich anwendet.` The ending proposes brief speaking opportunities and feedback without equating mistakes with lack of talent. This is consistent with the section's existing discussion of small, real-world learning goals.

## Grammar/identity conservation

- Fulltext occurrences: **4,570 → 4,520**. Exactly 60 obsolete anchors in changed s01/s03 are explicitly invalidated; 29 exact old `p04-s02` anchors are retained and shifted to new section-relative offsets; 10 new, explicitly author-reviewed Konjunktiv-II `sollten` advice annotations were created. Six existing curated `g07` annotations retargeted to new full s03. All 669 curated grammar records preserved, all 340 question IDs and Q/A, all 350 vocabulary targets untouched.
- 58 unrelated units are unchanged byte-equivalently at JSON object level, the 478 reading passages and sections retain exact stable IDs and membership, and the original ten p04 middle sentences remain verbatim.
- **No claim** that the legacy native nine-lens grammar extractor ran; no claim of full coverage of new sentences (additional unmarked valid grammar may exist).

## Independent and source-native technical QA

- Independent R9-vs-R10 content/runtime proof: **13,539 / 13,539 structural assertions pass; zero failures**, with all nine intentionally corrupted variants rejected.
- Exact v505-R141 Wordlinks R3 `reading-content-import-v38.js` module SHA256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc` reports **PASS, zero warnings**, 68 reading units, 478 trilingual passages, 340 questions, 350 vocabulary, 4,520 fulltext grammar items. Seven deliberate corrupted runtime variants are rejected. A disposable in-memory record passes validation/projection (68/340); **no browser database transaction was performed**.
- Cross-lingual text was authored and manually self-compared against the existing lesson claims, but has **NOT received independent adversarial linguistic Stage4 acceptance**.

## Remaining blockers and next work

Exactly **35** p04 sections still begin with the generic template `Entscheidend ist deshalb die konkrete Ausgestaltung.` Stage4 full multilingual/editorial independent QA is HOLD; native complete nine-lens grammar re-derivation is not run; browser IndexedDB/import/persistence Stage6 is NOT RUN; Stage7 release is NOT FINAL. Next bounded lesson batch should start `LES-PRES-031..040`, keeping already revised source-owner units and all user SRS/FSRS/app UI untouched.

**Recovery**: Original CURRENT v1.3.0, R9 source + runtime, R10 source and runtime remain separate. No Library cleanup, no source PDF reinstatement, no app/runtime code mutation.