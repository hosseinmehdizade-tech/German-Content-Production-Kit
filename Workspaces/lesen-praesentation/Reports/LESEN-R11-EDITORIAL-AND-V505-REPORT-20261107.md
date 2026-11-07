# Lesen — R11 editorial QA and v505 preentry (2026-11-07)

**Status:** scoped editorial Candidate / HOLD. **Not a released app content pack and not independent semantic Stage4 or browser IndexedDB Stage6.**

## Authorities and scope

- Curated **CURRENT**, unchanged: `Lesen-Praesentation-B2-C1-v1.3.0-CONTENT-PRODUCTION-DELIVERY.zip`, SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.
- Read-only R10 parent CONTENT: SHA256 `4be5bf368b23a1a46bae2d28686b3d4f9336ac01d98c2c1449ab19df81b9509a`; parent v505 PREENTRY runtime SHA256 `e2e5d395679f772f7ec4cf845da4af2aadb148f3362b3ed3955ed76d280e9aa3`.
- R11 CONTENT Candidate `Lesen-Production-Master-v1.3.0-R11-9P04-TRILINGUAL-CANDIDATE.json`, SHA256 `8a0bf2d16ce51b39501e5b6bc26b912cb47d9a4a14c0f42699e6b49b4ba3e3fe`, 6,497,683 bytes.
- R11 v505 PREENTRY runtime Candidate `Lesen-R11-v505-9P04-RUNTIME-PREENTRY-CANDIDATE.json`, SHA256 `ecc79df87f851f1196b4b6799c4b7b671ecaf77c089dc620e89ef497224730a2`, 6,991,952 bytes.

## Editorial decisions

The nominal batch was lessons 031–040. Lesson **035** had already received a meaningful topic-specific p04 edit in R2, so it was preserved **exactly**. Nine p04 sections needed a revision. The middle German sentence, anchored to the underlying topic, was preserved verbatim; only first and third German sentences and the **whole** Persian and English translations were revised. All other 59 master units are unchanged. Existing 340 questions, 350 vocabulary targets, and 669 curated grammar annotation IDs were preserved.

| Unit | Topic | Fields edited |
|---|---|---|
| LES-PRES-031 | Smartphones als Bildungsmedien | p04-s01 + p04-s03; FA/EN |
| LES-PRES-032 | Roboter im Alltag – Hilfe oder Bedrohung? | p04-s01 + p04-s03; FA/EN |
| LES-PRES-033 | Musikunterricht in der Schule | p04-s01 + p04-s03; FA/EN |
| LES-PRES-034 | Soziale Medien in Ausbildung und Karriere | p04-s01 + p04-s03; FA/EN |
| LES-PRES-036 | Gesunde Ernährung als Thema in der Schule | p04-s01 + p04-s03; FA/EN |
| LES-PRES-037 | Pädagogische Fähigkeiten an Schule und Hochschule | p04-s01 + p04-s03; FA/EN |
| LES-PRES-038 | Steigende Studierendenzahlen und Bildungsqualität | p04-s01 + p04-s03; FA/EN |
| LES-PRES-039 | Sollten junge Erwachsene zu Hause Wohnkosten mittragen? | p04-s01 + p04-s03; FA/EN |
| LES-PRES-040 | Sollten Lehrende Autoritätspersonen sein? | p04-s01 + p04-s03; FA/EN |

Example, `LES-PRES-031` (*Smartphones als Bildungsmedien*):

> Im Unterricht ist nicht das Smartphone selbst die Lernmethode, sondern der Auftrag, für den es eingesetzt wird. Wenn klare Regeln, begrenzte Einsatzphasen und konkrete Lernaufträge vereinbart werden, lässt sich ein Teil des Konflikts entschärfen. Lehrkräfte könnten die Geräte für gezielte Recherchen freigeben und sie während längerer Konzentrationsphasen weglegen lassen.

Topic grounding uses the accepted R10 p02/p03/p05 sections: benefit of mobile tools versus notifications/distraction and classroom phases. Corresponding FA and EN are included in the Candidate and complete before/after ledger.

**Remaining generic p04 count:** 26 (was 35); 29 of the original 55 have now received scoped editorial rewrites in R9–R11. Other generic language elsewhere, such as boilerplate in p01/p02/p03/p06/p07 and rubrics for personal-opinion q05, is outside this batch and may still need quality review. Preserving p04-s02 avoids unverified grammar loss but leaves some common structural phrasing to assess later.

## Grammar impacts (scoped, not full native grammar engine)

- Full-text grammar occurrences: **4520 → 4475**.
- **54** obsolete exact anchors tied to removed p04-s01/s03 contexts were retired; none were force-matched to new text.
- **22** anchors of untouched p04-s02 remain valid; **22** changed offsets due to new s01 lengths.
- **9** explicit attested Konjunktiv-II spans were added (`könnten`, `sollten`, `wäre`, `müssten`, depending on actual sentence).
- **5** curated `g07` annotations pointing at the old third sentence were redirected to the exact revised third sentence.
- The 9-lens grammar extraction source was **not** available for a full rebuild, and no claim of full grammatical coverage or independent Stage4 is made.

## QA evidence

- Independently implemented source↔runtime structural verification: **13,974 checks, 0 failures**; 9/9 adversarial independent probes correctly rejected.
- Original current v505 `reading-content-import-v38.js` source module SHA256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`: baseline and R11 candidates both **PASS**, candidate **zero warnings**, **7/7** corrupted pack probes rejected.
- Isolated *in-memory* projection: **68 units / 340 exercises**; **NO actual browser IndexedDB transaction, persistence, reload, or user profile import**.
- Native validator counts: 68 entries, 478 passages with FA and EN, 340 questions, 350 vocabulary, 4475 full-text grammar occurrences.
- Current app v505-R141 Wordlinks R3 was **not changed**. No SRS/FSRS, UI, source original PDF, or other workstream modification.

## Hold gates and next bounded unit of work

Independent multilingual **Stage4 HOLD**, full nine-lens grammar rerun **NOT_RUN**, native user-independent browser/IndexedDB **Stage6 NOT_RUN**, Stage7 **NOT_RELEASED**. The appropriate next editorial batch is p04 lessons **041–050**, again preserve already accepted sections and perform exact DE/FA/EN/grammar checks rather than a blind replacement.

**Files in owner Library:** `Content/Lesen/Candidates/` (two Candidate JSONs), `Reports/` (before/after ledger and QA), `Tools/` (reproducible source-specific scripts), and `Checkpoints/`. Canonical Git owner: `Workspaces/lesen-praesentation`.