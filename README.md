# German Content Production Kit — active v3.3.2

The active production framework is **v3.3.2 — Menschen Course Export Ready**. GitHub is the compact durability/coordination mirror; exact verified portable artifacts live in ChatGPT Library and are identified by SHA-256 in `PROJECT-STATE.json`.

Current Menschen workstream: `Workspaces/menschen-a1a2b1-memrise/`. **A1-L01 through A1-L17 are LOCKED. A1-L18 Stage 1/2 is next.**

A1-L17 Stage1/2:
- source lesson: `A1-L17 — Wer will Popstar werden?`
- source rows: **118** (`1407..1524`)
- source audio: **118/118 present**, zero missing, zero multi-audio rows
- Stage2: **147 distinct canonical lesson identities = 144 new + 3 exact locked reuses**
- locked reuses: `ma1m-lu-0042` (gut), `ma1m-lu-0935` (ankommen), `ma1m-lu-0936` (auf etw. ankommen)
- new stable IDs: `ma1m-lu-1997..ma1m-lu-2140`
- Stage1/2 validator: **22/22 PASS**
- package verification: **PASS**
- Library rematerialization: exact SHA-256 match
- 77 targets retain explicit Stage3 review flags where source polysemy, wording, naturalness or normalization still needs evidence review

Stage1/2 artifact: `Menschen-A1-L17-v3.3.2-Stage1-2-CHECKPOINT.zip`
SHA-256: `388a20e0ccd54da89fec7a252c12ad2019de6909a872609313cbe7cb084b9599`

**A1-L17 Stage 3 — Evidence & Enrichment: COMPLETE / PASS.**

- **147/147** targets complete: **144 new + 3 exact locked reuses**
- **588** exact DE examples, each with FA + EN
- **75 senses + 72 expressions**
- **64** evidence-backed relations; **84** review resolutions; **147** evidence claims
- locked reuses: `ma1m-lu-0042`, `ma1m-lu-0935`, `ma1m-lu-0936` — exact semantic core and four examples preserved
- final Stage3 checkpoint: `Menschen-A1-L17-v3.3.2-Stage3-COMPLETE-CHECKPOINT.zip`
- SHA-256: `f203f476c8002fb202cfca4abb5864f458c30916855858dede239967f1186f2a`
- fresh validator / manifest rehash / package hygiene / Library rematerialization: **PASS**
- next: **Stage 4 — Linguistic & Lexical QA**


**A1-L17 Stage 4 — Linguistic & Lexical QA: COMPLETE / PASS.**

- **33/33** custom QA checks PASS across **147** targets
- **56** bounded repairs: 36 expression-type profile normalizations, 4 profile-metadata completions, 9 source-reference normalizations, 7 translation-linguistic repairs
- source course order/identity preserved; no German example regeneration; L01-L16 remain untouched/LOCKED
- locked reuses `ma1m-lu-0042`, `ma1m-lu-0935`, `ma1m-lu-0936`: semantic core + four examples preserved exactly
- official bundle validator: **147/147 exact-4, 0 warnings**
- profile / reference-registry / reference-availability validators: **PASS**
- framework pytest: **47/47 PASS**
- checkpoint: `Menschen-A1-L17-v3.3.2-Stage4-CHECKPOINT.zip`
- SHA-256: `81ab47d713b11bd1643a08a32d3643576252c5b0a623132ea77ee94f76f3b58c`
- Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage 5 — Delivery Projection**


**A1-L17 Stage 5 — Delivery Projection: COMPLETE / PASS.**

- **147** projected cards = 144 new + 3 exact locked reuses
- card types: **124 de-vocabulary + 23 german-verb**
- examples: **588 DE + 588 FA + 588 EN**; relations: **64**
- source audio: **148 target refs / 119 unique**, zero missing targets; source occurrence map **118/118** rows with audio
- projection/loss-parity QA: **172/172 PASS**
- direct-import dataset: `A1-L17-UNIVERSAL-v2.tsv`, SHA-256 `2a878f73ba3ed7acb091f5a0dc3bf779306be29c2da57b03274b20f71bdcd100`
- Stage 5 is runtime-version agnostic; Stage 6 must resolve Flashcards CURRENT at execution time
- checkpoint: `Menschen-A1-L17-v3.3.2-Stage5-CHECKPOINT.zip`, SHA-256 `4f5cbafd0bb9fa6bfb059c06e5e705d34d5f94f080f6742077447815a190d859`
- Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage 6 — Runtime & Presentation Acceptance**


**A1-L17 Stage 6 — Runtime & Presentation Acceptance: PASS_WITH_ENVIRONMENT_BOUNDARY.**

- resolved **CURRENT = GFP v428-R62**; v423-R57 used only as regression reference
- exact CURRENT organized delivery SHA-256 verified: `73beff1ea0da24bc35daa1e0ef0ffbf56f6cd2965e45ecd2fe235e972dc3e6e3`
- exact Stage5 outer candidate direct import on v428: **21/21 PASS**
- L17 runtime + four-mode presentation acceptance: **33/33 PASS**
- persistence/runtime index: **147/147**; Universal authority roundtrip: **147/147**
- cumulative identity L01-L17: **12/12 PASS; 2140 unique = prior 1996 + 144 new; expected 3 reuses only**
- source audio refs preserved (**148 refs / 119 unique**); source-MP3 playback is explicitly unsupported by CURRENT and Audio practice uses browser TTS
- checkpoint: `Menschen-A1-L17-v3.3.2-Stage6-GFP-v428-CHECKPOINT.zip`, SHA-256 `430ce28b9ec95cf4056152008b6b15952306ef88303d3ee89dafcdf348140e13`
- Library rematerialization: **PASS — exact SHA-256 match**
- boundary: v428 still requires its project-level fresh Windows/Chrome persistence+restart+offline/service-worker smoke because storage semantics changed
- next: **Stage 7 — final LOCKED release + exact-final direct import**


**A1-L17 Stage 7 — Release & Post-Package Verification: LOCKED / PASS_WITH_ENVIRONMENT_BOUNDARY.**

- final immutable bundle: `Menschen-A1-L17-v3.3.2-GFP-v428-LOCKED.zip`
- SHA-256: `66a8db008c7400f4827423a8ca96df55f873c3ac86bf8baf35d68d293816fb87`
- final package integrity / manifest rehash / hygiene: **PASS** (52 manifest entries; no pycache/pyc)
- exact-final direct import on CURRENT GFP v428-R62: **21/21 PASS**
- exact-final four-mode runtime/presentation: **33/33 PASS**
- standalone persistence: **147/147 VERIFIED**
- cumulative identity/collision: **12/12 PASS; 2140 unique through L17; 144 new + expected 3 reuses**
- Library rematerialization: **PASS — exact SHA-256 match**
- content state: **LOCKED**; runtime-level environment boundary remains only because v428 still needs its project-level fresh Windows/Chrome offline/storage smoke
- next: **A1-L18 Stage 1 — Source & Inventory + Stage 2 — Canonicalization**
