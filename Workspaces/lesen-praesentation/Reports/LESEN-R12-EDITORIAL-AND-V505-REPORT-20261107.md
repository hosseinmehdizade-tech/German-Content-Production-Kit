# Lesen R12 — 10 multilingual p04 repairs, 041–050 · Scoped editorial & v505 preentry report

**2026-11-07 · Candidate-only. No CURATED_CURRENT promotion.**

## Sources and authority

- Parent content: R11 source-owner curated candidate SHA256 `8a0bf2d16ce51b39501e5b6bc26b912cb47d9a4a14c0f42699e6b49b4ba3e3fe`, preserved immutable.
- Parent runtime: R11 v505 preentry candidate SHA256 `ecc79df87f851f1196b4b6799c4b7b671ecaf77c089dc620e89ef497224730a2`, preserved immutable.
- **R12 content**: `Lesen-Production-Master-v1.3.0-R12-10P04-TRILINGUAL-CANDIDATE.json` · SHA256 `a41224ae7a054a959c942afb0b13fcb7d686c76fc27131ec813a9272dad6e7d2` · 6,453,548 bytes.
- **R12 Runtime v505 preentry**: `Lesen-R12-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json` · SHA256 `e08844a19137a1edece8deb9f39e036df7b4777de2e54db4312e0ab14c3bcd86` · 6,942,875 bytes.
- Original curated portable v1.3.0 CURRENT ZIP remains unchanged SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.

## Actual content edits

- **10 lessons 041–050**, ten p04 DE/FA/EN sections changed; **20 German sentences** (`p04-s01`, `p04-s03`) newly authored per lesson. All original `p04-s02` topic-specific sentences remain byte-identical.
- Full before/after plus source evidence references in `LESEN-R12-10P04-TRILINGUAL-GRAMMAR-LEDGER.json`; scoped trilingual claims in `LESEN-R12-TRILINGUAL-SCOPED-REVIEW.json`.
- Examples: Lesson 043 addresses accessible PDF files, rooms and fair examination conditions; 048 differentiates patient experience from scientifically proven medical efficacy; 050 contrasts durable influence with short-lived social-media attention.
- Remaining **16 of the original 55 generic p04 starts**; original 340 question IDs/model answers, 350 vocabulary rows and 58 other units untouched. The preserved p04-s02 sentence pattern still recurs and should receive a subsequent semantic quality review rather than automatic blanket rewrite.

## Grammar, translation and source constraints

- Source-owner grammar occurrences **4475 → 4425**: 60 old p04-s01/s03 context-specific spans invalidated, 41 original p04-s02 spans accurately reanchored, 10 explicit manually confirmed Konjunktiv-II occurrences added, 5 curated `g07` text references retargeted. Original 669 curated grammar entries remain. All 4,425 spans match exact `start`/`end` offsets in the current German p-section text.
- DE/FA/EN paragraphs were revised jointly. This is a scoped model editorial check, **not an independently certified linguistic Stage4**. Notes for the 10 lessons preserve original p02/p03/p05 framing; no claim of reading a newer publisher file.
- **Original nine-lens grammar source engine not rerun.** Manual annotations are labeled `editorial_scoped_r12`; no automatic grammar completeness claim.

## Verifications

- **Independent source-structure QA 13,940/13,940 PASS**, zero failures, with **9/9 adversarial variants rejected**. The suite checks 68-unit identity/order, question IDs and evidence, all 478 passage texts + FA/EN, grammar offsets/curated references, 58 immutable units, 10 exact section deltas, and v505 mapping/hash contracts.
- **Exact current v505 JS import-source validator PASS, zero warnings; 7/7 invalid runtimes rejected**, isolated in-memory projection 68 units and 340 exercises. `reading-content-import-v38.js` SHA256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`.
- **No browser/IndexedDB transaction or real-app import performed.** Stage6 = `NOT_RUN`; Stage7 = `NOT_RELEASED`.

## Next bounded work

Review remaining templated p04 lessons **051–068**, preserving previously edited 051 and 059; then audit repeated p01–p03/p05–p07 framing, evidence-based question-answer coherence and complete trilingual semantics. Do not promote CURRENT or claim Stage4/6/7 until independently proven. Keep App UI and SRS/FSRS entirely untouched.