# German Content Production Kit — active v3.3.2

The active production framework is **v3.3.2 — Menschen Course Export Ready**. GitHub is the compact durability/coordination mirror; exact verified portable artifacts live in ChatGPT Library and are identified by SHA-256 in `PROJECT-STATE.json`.

Current Menschen workstream: `Workspaces/menschen-a1a2b1-memrise/`. **A1-L01 through A1-L20 are LOCKED. A1-L21 Stage 3 is COMPLETE PASS: 148/148 new targets enriched + 3 locked reuses ready = 151/151 lesson identities; Stage4 Linguistic & Lexical QA is next.**

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


**A1-L18 Stage 1/2 — Source & Inventory + Canonicalization: COMPLETE / PASS.**

- source lesson: `A1-L18 — Geben_Sie_ihm_doch_diesen_Tee!`
- source rows: **132** (`1525..1656`); source audio **130 refs / 130 unique**, exactly two source gaps at rows **1533** and **1654**, zero multi-audio rows
- supplied RAR membership: **130/130 referenced MP3 filenames present**; missing source audio was preserved, not invented
- Stage2: **177 distinct canonical identities = 177 new + 0 locked reuses**
- semantic target mix: **101 senses + 76 expressions**
- new stable IDs: `ma1m-lu-2141..ma1m-lu-2317`
- **109** targets carry explicit Stage3 review flags; broad/polysemous or malformed source material was split/normalized explicitly rather than silently overwritten
- independent validator: **14/14 PASS**; package manifest/hygiene: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage1-2-CHECKPOINT.zip`, SHA-256 `a0be554f2c27cb8dfbb6206f06fa4fa7656fcc0c8317f5bfe68d6574cc02a8ae`
- Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage 3 — Evidence & Enrichment in bounded batches**


**A1-L18 Stage 3 — Batch0001: PASS.**

- target range: `ma1m-lu-2141..ma1m-lu-2160` = **20/177** Stage3 targets complete
- **8 senses + 12 expressions**; **80 exact DE examples**, each with independent FA + EN
- **9 evidence-backed relations**, **15 review resolutions**, **20 evidence claims**
- missing source audio for the Fieber source gap remains preserved; no audio invented
- local + fresh-extract validator: **PASS**; manifest rehash/hygiene: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0001-CHECKPOINT.zip`, SHA-256 `1d5a383614d6afa5de53372b3b05fc3a7579e017be593094b7f51654fcfca127`
- Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage3 Batch0002 starting at ma1m-lu-2161**


**A1-L18 Stage 3 — Batch0002: PASS.**

- target range: `ma1m-lu-2161..ma1m-lu-2180`; cumulative **40/177** Stage3 targets complete
- cumulative: **18 senses + 22 expressions**, **160 exact DE examples** with independent FA + EN
- cumulative **20 evidence-backed relations**, **32 review resolutions**, **40 evidence claims**
- key polysemy kept separate: `einnehmen` medicine vs money/revenue vs physical-space senses; `Praxis` experience vs practice premises; `Körper` living-body vs physical-object branches
- local + fresh-extract validator: **PASS**; manifest rehash/hygiene: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0002-CHECKPOINT.zip`, SHA-256 `a2931e294b648edb32971ddcd20987c1be8834f17933af0a75dd1cf1d95928b2`
- Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage3 Batch0003 starting at ma1m-lu-2181**


**A1-L18 Stage 3 — Batch0003: PASS.**

- target range: `ma1m-lu-2181..ma1m-lu-2200`; cumulative **60/177** Stage3 targets complete
- cumulative: **29 senses + 31 expressions**, **240 exact DE examples** with independent FA + EN
- cumulative **32 evidence-backed relations**, **55 review resolutions**, **60 evidence claims**
- source-seed mismatches for `Das Auge isst mit!`, `Kapsel` and `Bein` were preserved in provenance and corrected only at the learner-meaning layer; no source row was silently rewritten
- local + fresh-extract Stage3 validator, manifest rehash, package hygiene and Library rematerialization: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0003-CHECKPOINT.zip`, SHA-256 `281e9b6fd7bff385fb80a00a0187489bbc6c64497139b972d59fbc4c049ecdf2`
- full Stage4 bundle/profile normalization is intentionally not claimed during Stage3
- next: **Stage3 Batch0004 starting at ma1m-lu-2201**


**A1-L18 Stage 3 — Batch0004: PASS.**

- target range: `ma1m-lu-2201..ma1m-lu-2220`; cumulative **80/177** Stage3 targets complete
- cumulative: **39 senses + 41 expressions**, **320 exact DE examples** with independent FA + EN
- cumulative **46 evidence-backed relations**, **75 review resolutions**, **80 evidence claims**
- key reviews: `Brust` scoped to the health/chest sense; `wehtun` Dative rection recorded; three `Glied` senses kept separate; inherited malformed/wrong-sense examples retained only in audit; `rechter Arm` Persian seed corrected at learner layer; `jdn. auf den Arm nehmen` verified against the idiom authority
- local + fresh-extract Stage3 validator, manifest rehash, package hygiene and Library rematerialization: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0004-CHECKPOINT.zip`, SHA-256 `6afe37898e7004648e15c11b614a5d4a94ef643dfa282e2334ef88fe75137bef`
- full Stage4 bundle/profile normalization is intentionally not claimed during Stage3
- next: **Stage3 Batch0005 starting at ma1m-lu-2221**


**A1-L18 Stage 3 — Batch0005: PASS.**

- target range: `ma1m-lu-2221..ma1m-lu-2240`; cumulative **100/177** Stage3 targets complete
- cumulative: **53 senses + 47 expressions**, **400 exact DE examples** with independent FA + EN
- cumulative **65 evidence-backed relations**, **92 review resolutions**, **100 evidence claims**
- source-fidelity repairs: Fingerring FA seed corrected only at learner layer; malformed/mixed/wrong-target source examples for Hand, Nasenloch and Rücken retained in audit but excluded from final examples; learner morphology normalized to `das Nasenloch, Nasenlöcher`; `sich die Nase putzen` records the Dative-reflexive pattern
- local + fresh-extract Stage3 validator, manifest rehash, package hygiene and Library rematerialization: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0005-CHECKPOINT.zip`, SHA-256 `c4fbfc6256f9814dc5b0df64bc38cf52c4a9c8b260676c3ca7085350b5c19e05`
- full Stage4 bundle/profile normalization is intentionally not claimed during Stage3
- next: **Stage3 Batch0006 starting at ma1m-lu-2241**


**A1-L18 Stage 3 — Batch0006: PASS.**

- target range: `ma1m-lu-2241..ma1m-lu-2260`; cumulative **120/177** Stage3 targets complete
- cumulative: **68 senses + 52 expressions**, **480 exact DE examples** with independent FA + EN
- cumulative **77 evidence-backed relations**, **112 review resolutions**, **120 evidence claims**
- source-fidelity repairs: `Arsch` register resolved to Duden **derb**; `Po`/ `Gesäß` kept separate; source capitalization issues in `Zunge` and `bleiben` preserved in audit while learner examples are corrected; `drin/draußen` shared-row FA/example mismatches remain provenance-visible; `Schnupfen` action gloss removed from learner noun meaning; `Kraut` scoped to the herb sense; Persian `doch` metanote excluded from German examples
- local + fresh-extract Stage3 validator, manifest rehash, package hygiene and Library rematerialization: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0006-CHECKPOINT.zip`, SHA-256 `1e1d1f9993658909322cc72c9d067c5689d97683b61faaf96c1c798a123954cf`
- full Stage4 bundle/profile normalization is intentionally not claimed during Stage3
- next: **Stage3 Batch0007 starting at ma1m-lu-2261**


**A1-L18 Stage 3 — Batch0007: PASS.**

- target range: `ma1m-lu-2261..ma1m-lu-2280`; cumulative **140/177** Stage3 targets complete
- cumulative: **79 senses + 61 expressions**, **560 exact DE examples** with independent FA + EN
- cumulative **90 evidence-backed relations**, **138 review resolutions**, **140 evidence claims**
- source-fidelity repairs: `Ratschlag geben/erteilen` normalized with a Dative person; `Spiritus` is separated from the false plural `Spirituosen` while conflicting raw Persian evidence stays visible; conjunction/adverb `damit` remain separate; `Du tust mir leid!` is resolved to the sympathy sense; malformed or wrong-target source examples for `Lebensmittel liefern`, `verschieden sein`, and `jdm. vorkommen` remain audit-only
- local + fresh-extract Stage3 validator, manifest rehash, package hygiene and Library rematerialization: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0007-CHECKPOINT.zip`, SHA-256 `c62a461506147936c37cb33dc1bb3ca9d1fd5c44642a26bba0e0b0f0d827df84`
- full Stage4 bundle/profile normalization is intentionally not claimed during Stage3
- next: **Stage3 Batch0008 starting at ma1m-lu-2281**


**A1-L18 Stage 3 — Batch0008: PASS.**

- target range: `ma1m-lu-2281..ma1m-lu-2300`; cumulative **160/177** Stage3 targets complete
- cumulative: **89 senses + 71 expressions**, **640 exact DE examples** with independent FA + EN
- cumulative **107 evidence-backed relations**, **165 review resolutions**, **160 evidence claims**
- source-fidelity repairs: `Tipp` is narrowed from the raw FA hint/warning mix to evidence-backed hint/advice; `das Heilen` stays nominalized while the verbal source example remains audit-only; formal `Sie` imperatives receive formal Persian learner translations; `Furz/furzen` = **derb**, `Pupser` = **familiär**, `rülpsen` = **umgangssprachlich**; `Bauch leicht gespannt` is retained as the course phrase with an explicit registered-reference limitation rather than silently rewritten
- local + fresh-extract Stage3 validator **27/27 PASS**, manifest rehash, package hygiene and Library rematerialization: **PASS**
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0008-CHECKPOINT.zip`, SHA-256 `3584690dbf329059a34a3ac4973d49b7e598c785955169f595fd12bf21d92b8d`
- full Stage4 bundle/profile normalization is intentionally not claimed during Stage3
- next: **Stage3 Batch0009 starting at ma1m-lu-2301**


**A1-L18 Stage 3 — Batch0009: PASS.**

- target range: `ma1m-lu-2301..ma1m-lu-2317`; cumulative **177/177** Stage3 targets complete
- cumulative: **101 senses + 76 expressions**, **708 exact DE examples** with independent FA + EN
- cumulative **124 evidence-backed relations**, **183 review resolutions**, **177 evidence claims**
- final source-fidelity reviews include separated `Schulter/Schultergelenk` scopes, learner-layer repair of the malformed `Zehe` source example, foot/ankle scoping for `Knöchel`, Duden-backed register split for `pinkeln/pissen/scheißen`, and explicit preservation of the `Wer hat hier geschissen?` source/reference conflict
- Batch0009 checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-Batch0009-CHECKPOINT.zip`, SHA-256 `6d0ed062953fbaac1b2760b564ab9d3c2f3c32e21d6323873d5cb692aeaf174d`
- Library rematerialization: **PASS — exact SHA-256 match**


**A1-L18 Stage 3 — Evidence & Enrichment: COMPLETE / PASS.**

- **177/177** targets complete across Batches0001-0009 = **101 senses + 76 expressions**
- **708** exact DE examples, each with FA + EN
- **124** evidence-backed relations; **183** review resolutions; **177** evidence claims
- source rows **132** (`1525..1656`) and source audio lineage preserved; known no-audio rows **1533** and **1654** remain explicit and no audio was invented
- Stage3 complete validator: **35/35 PASS**; manifest rehash and package hygiene **PASS**
- final Stage3 checkpoint: `Menschen-A1-L18-v3.3.2-Stage3-COMPLETE-CHECKPOINT.zip`
- SHA-256: `abd1e83fe2c0d0a32804673058c91cf182dd7d4491d99b5c56307d7a425d38e8`
- Library rematerialization: **PASS — exact SHA-256 match**
- full Stage4 linguistic/profile normalization is not claimed here; next: **Stage 4 — Linguistic & Lexical QA**


**A1-L18 Stage 4 — Linguistic & Lexical QA: COMPLETE / PASS.**

- **46/46** custom QA checks PASS across **177** targets; **0 advisory warnings**
- official bundle validator: **177/177 exact-4 examples, 0 warnings**; profile, reference registry and reference availability validators: **PASS**
- framework regression: **47/47 pytest PASS**
- **48 bounded repairs**: 21 expression-type profile normalizations, 3 registered-source completions, 11 source-reference normalizations, 12 example linguistic repairs, 1 target translation cleanup
- all **180 active review-flag instances** are closed by the **183 Stage3 resolution records**; unresolved: **0**
- source audio lineage preserved: **174 target occurrence refs / 130 unique**; the three split targets without audio remain `ma1m-lu-2151`, `ma1m-lu-2152`, and `ma1m-lu-2315`; no audio invented
- the Menschen/Duden semantic conflict for `Wer hat hier geschissen?` remains explicit rather than silently reconciled
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage4-CHECKPOINT.zip`, SHA-256 `63f093f01f40920581d2e721396960d39b0fdb432fe68e48ef563d9f4733df39`
- fresh-extract manifest/hygiene/custom QA and Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage 5 — Delivery Projection**


**A1-L18 Stage 5 — Delivery Projection: COMPLETE / PASS.**

- **177/177** canonical identities projected 1:1 to Universal v2; **161 de-vocabulary + 16 german-verb**
- **708 DE + 708 FA + 708 EN** examples; **124/124 relations** preserved
- projection/loss-parity QA: **207/207 PASS**; fresh-extract validator: **13/13 PASS**
- direct-import dataset: `A1-L18-UNIVERSAL-v2.tsv`, SHA-256 `e7ef42cd1c471e1dcc52d08594ea50cbc0ee48845843f2e2f229281ea7e82fff`
- projected cards SHA-256: `ef87c1a0bc992e19dc3ac9fe9d571166b258189dbf32b2ee3cc7cea57500f36b`
- source audio lineage: **174 target refs / 130 unique**; zero-audio split targets `ma1m-lu-2151`, `ma1m-lu-2152`, `ma1m-lu-2315`; source gaps **1533/1654** preserved, no audio invented
- Stage5 parity QA caught and fixed a projection-helper gap for value-backed relations (`value.form` / `value.pattern`); final relation parity is **124/124**
- runtime binding intentionally remains **RESOLVE_CURRENT_AT_STAGE6**; no historical v428/v423 runtime was baked into Stage5
- checkpoint: `Menschen-A1-L18-v3.3.2-Stage5-CHECKPOINT.zip`, SHA-256 `ce52f1b11f1286bae31f94a7df8a2bd4d9eef303e730abe616b8bea26f390c86`
- manifest rehash, package hygiene and Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage 6 — resolve CURRENT Flashcards runtime, then exact import/roundtrip/persistence/four-mode presentation acceptance**


**A1-L18 Stage 6 — Runtime & Presentation Acceptance: PASS_WITH_ENVIRONMENT_BOUNDARY.**

- CURRENT resolved at execution: **GFP v430/R64**, organized artifact SHA-256 `518011abceb63e52c2cfe0739c7383df1fa62fae7ce4c8f71196079e73128913`; LAST_FULLY_VERIFIED remains v423/R57 and was not used as the integration base
- current organized package internal checksum rehash: **262/262 PASS**
- exact Stage5 outer ZIP direct import: **21/21 PASS**; runtime/presentation acceptance: **33/33 PASS**
- **177/177** Universal-v2 authority roundtrip and runtime index; commit manifest VERIFIED under the deterministic IndexedDB test boundary
- **161 de-vocabulary + 16 german-verb**, exact four-example presentation by mode (study=4, quick=2, typing=3, audio=3)
- **124/124 relation items** with 124 unique relation IDs preserved
- source audio lineage: **174 refs / 130 unique**; current Audio practice uses browser TTS and does not consume source MP3 files
- cumulative identity through L18: **12/12 PASS; 2317 unique; 177 new L18; no reuses/collisions**
- Stage6 checkpoint: `Menschen-A1-L18-v3.3.2-Stage6-GFP-v430-CHECKPOINT.zip`, SHA-256 `3cc789c9f24aa9b0ba33a4ff6491becdfe3e4a63a5fd7546be6671014ca5d2d8`
- fresh-extract validator **24/24 PASS**, manifest/package hygiene PASS, Library rematerialization exact SHA match
- v430 itself still has a separate real-profile environment boundary: exact-package same-profile Windows/Chrome responsiveness + Backup Vault + persistence + restart + offline/service-worker smoke is required before the runtime can be FINAL/VERIFIED
- next: **Stage 7 — exact-final A1-L18 LOCKED package + post-package import verification on CURRENT v430**


**A1-L18 Stage 7 — LOCKED / exact-final PASS_WITH_ENVIRONMENT_BOUNDARY.**

- exact final outer artifact: `Menschen-A1-L18-v3.3.2-GFP-v430-LOCKED.zip`
- SHA-256: `0c1cfece23cee4a50be538e64ff9d45a094adda7bf2744efda707bd72bd72b0d`
- direct exact-final import/runtime presentation on CURRENT **GFP v430/R64**: **33/33 PASS**
- commit manifest/runtime index/Universal authority: **177/177 PASS** under deterministic IndexedDB test boundary
- cumulative identity L01-L18: **2317 unique cards**, **177 new L18**, **0 reuses/collisions**
- final package manifest rehash: **52/52 PASS**; package hygiene **PASS_NO_PYCACHE_PYC**
- Library rematerialization: **PASS — exact SHA-256 match**
- content state: **LOCKED**
- separate runtime boundary remains: v430 still needs the same-profile Windows/Chrome responsiveness + Backup Vault + persistence + restart + offline/service-worker smoke before the runtime itself can be FINAL/VERIFIED
- next: **A1-L19 Stage1/2**


**A1-L19 Stage 1/2 — Source & Inventory + Canonicalization: COMPLETE / PASS.**

- source lesson: `A1-L19 — Der hatte doch keinen Bauch!`
- source rows: **91** (`1657..1747`); source audio **90 refs / 90 unique**, exactly one source gap at row **1728**, zero multi-audio rows
- supplied RAR membership: **90/90 referenced MP3 filenames present**; missing source audio was preserved, not invented
- Stage2 mappings: **124 source→target mappings**, **123 distinct lesson canonical identities**
- identities: **119 new + 4 exact locked reuses** (`ma1m-lu-0180`, `ma1m-lu-1495`, `ma1m-lu-1920`, `ma1m-lu-1922`); one repeated in-lesson identity merged
- new target mix: **54 senses + 65 expressions**; new stable IDs `ma1m-lu-2318..ma1m-lu-2436`
- **92** identities carry explicit Stage3 review flags; malformed, broad or semantically conflicting source seeds remain visible in provenance rather than being silently rewritten
- independent fresh-extract validator: **16/16 PASS**; manifest rehash **17/17 PASS**; package hygiene PASS
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage1-2-CHECKPOINT.zip`, SHA-256 `6ef4000a6f2f97a51d44bad1fa19605758434c8243677eef7e90208cd99d8a0f`
- Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage3 Batch0001 from ma1m-lu-2318**, while locked reuses remain immutable


**A1-L19 Stage 3 — Batch0001: PASS.**

- new target range: `ma1m-lu-2318..ma1m-lu-2337` = **20/119 new targets enriched**
- **4/4 locked reuses** remain immutable and ready; therefore **24/123 lesson identities** are ready
- batch mix: **9 senses + 11 expressions**, **80 exact DE examples** with independent FA + EN
- **18 evidence-backed relations**, **18 review resolutions**, **20 evidence claims**
- important source-fidelity reviews: `schwarzes Haar` FA corrected only at learner layer; `wellig/gewellt` narrowed from broad “curly” to “wavy”; `glatt` scoped to the hair sense and its malformed source example kept audit-only; wrong-target source examples for `dunkles Haar`, `weißes Haar`, and `Blondine` were not reused as learner examples
- `dickes Haar` remains the explicit Menschen course phrase; an exact standalone registered-Duden collocation was not found in the reviewed excerpt, so no fabricated reference claim was added
- fresh-extract Stage3 validator **31/31 PASS**; manifest rehash **23/23 PASS**; package hygiene and Library rematerialization PASS
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage3-Batch0001-CHECKPOINT.zip`, SHA-256 `bd3e945e679ed48365b5648bd774b68a4d35102ca2d4f932b13b92020796c764`
- full Stage4 linguistic/profile normalization is intentionally not claimed during Stage3
- next: **Stage3 Batch0002 from ma1m-lu-2338**


**A1-L19 Stage 3 — Batch0002: PASS.**

- new target range: `ma1m-lu-2338..ma1m-lu-2357`; cumulative **40/119 new targets enriched**
- **4/4 locked reuses** remain immutable; **44/123 lesson identities** are ready
- cumulative **20 senses + 20 expressions**, **160 exact DE examples** with independent FA + EN
- cumulative **39 evidence-backed relations**, **44 review resolutions**, **40 evidence claims**
- key reviews: `hübsch` appearance sense narrowed; `dünn/dick` scoped to body/stature; `so` bound to its concluding discourse use; `mit jdm. freundlich umgehen` records **mit + Dativ**; `garstig` and `ausgelassen` remain distinct learner senses; `jdn. glücklich machen` records the Akkusativ person slot
- exact standalone `flacher Bauch` was not located in the reviewed registered Duden excerpt; the Menschen course phrase is retained with an explicit limitation instead of fabricated attestation
- fresh-extract validator **56/56 PASS**, manifest rehash **28/28 PASS**, package hygiene and Library rematerialization: **PASS**
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage3-Batch0002-CHECKPOINT.zip`, SHA-256 `3bba6ba8dcf1e5f050f8da4e9c5966409a5608a8ddcd7511311438ccd328f867`
- full Stage4 linguistic/profile normalization is intentionally not claimed during Stage3
- next: **Stage3 Batch0003 from ma1m-lu-2358**


Batch0002 authority reconciliation: duplicate portable candidates were resolved to the richer evidence-backed **39 relations / 44 review resolutions / 56-of-56 fresh validation** state. Canonical Library bytes were re-materialized with exact SHA-256 `3bba6ba8dcf1e5f050f8da4e9c5966409a5608a8ddcd7511311438ccd328f867`; locked reuses were not regenerated.


**A1-L19 Stage 3 — Batch0003: PASS.**

- new target range: `ma1m-lu-2358..ma1m-lu-2377`; cumulative **60/119 new targets enriched**
- **4/4 locked reuses** carried unchanged; **64/123 lesson identities ready**
- cumulative mix: **34 senses + 26 expressions**, **240 exact DE examples** with independent FA + EN
- cumulative **54 evidence-backed relations**, **67 review resolutions**, **60 evidence claims**
- key reviews: `Das kommt mir komisch vor.` is aligned to the strange/odd sense; `aussuchen` preserves optional Dativ + Akkusativ; `sich beschweren` records `bei + Dativ` and `über + Akkusativ`; raw `vergass` remains provenance while learner morphology uses standard `vergaß`
- locked `traurig stimmen`, `komisch`, and `seltsam` identities are referenced by relations but were **not regenerated**
- fresh-extract Stage3 validator **78/78 PASS**; manifest rehash **33/33 PASS**; package hygiene and Library rematerialization PASS
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage3-Batch0003-CHECKPOINT.zip`, SHA-256 `4ef6b7fafcab7336d91cf7a680e43e6765285a8fff6420b9e81339f930bb9ef6`
- Stage4 is intentionally not claimed during Stage3
- next: **Stage3 Batch0004 from ma1m-lu-2378**

**A1-L19 Stage 3 — Batch0004: PASS.**

- new target range: `ma1m-lu-2378..ma1m-lu-2397`; cumulative **80/119 new targets enriched**
- **4/4 locked reuses** remain immutable; **84/123 lesson identities** are ready
- cumulative **41 senses + 39 expressions**, **320 exact DE examples** with independent FA + EN
- cumulative **68 evidence-backed relations**, **97 review resolutions**, **80 evidence claims**
- key reviews: `erkennen` vs. `auseinanderhalten` are kept separate; `sich entschuldigen` records `bei + Dativ` and `für + Akkusativ`; `Sag mal!` gets a pragmatic learner-layer Persian repair while raw source remains in provenance; `lügen` vs. `Lügen erzählen` and the two `raten` senses remain separate; `Stimmt!`, `Hier stimmt etwas nicht!`, and `Da stimmt etwas nicht!` remain distinct redemittel
- fresh-extract Stage3 validator **129/129 PASS**; manifest rehash **40/40 PASS**; package hygiene and exact Library rematerialization: **PASS**
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage3-Batch0004-CHECKPOINT.zip`, SHA-256 `9b223a3775b80e6149040f568101231693febbe6983bf99ef51852da354bd0ba`
- Stage4 is intentionally not claimed during Stage3
- next: **Stage3 Batch0005 from `ma1m-lu-2398`**



**A1-L19 Stage 3 — Batch0005: PASS.**

- target range: `ma1m-lu-2398..ma1m-lu-2417`; cumulative **100/119 new targets enriched**
- **4/4 locked reuses** remain immutable; **104/123 lesson identities** are ready
- cumulative **48 senses + 52 expressions**, **400 exact DE examples** with independent FA + EN
- cumulative **78 evidence-backed relations**, **121 review resolutions**, **100 evidence claims**
- key reviews: `Wahnsinn!` is scoped to the informal/emotive exclamation rather than a clinical sense; raw `verzögerter Reaktion` is preserved in provenance while learner morphology uses `verzögerte Reaktion`; no-audio source row 1728 stays explicit and no audio is invented; `über vergangens sprechen` is normalized only at learner layer to `über Vergangenes sprechen`; person-vs-neuter `Neue` identities remain separate; `Zeitschrift` and magazine-sense `Magazin` remain distinct
- exact full registered-reference attestation was **not** located for `Wer schweigt, stimmt zu.` or standalone `Ach komm!`; both source phrases are preserved with explicit reference limitations rather than fabricated claims
- fresh-extract Stage3 validator **156/156 PASS**; manifest rehash **47/47 PASS**; package hygiene and exact Library rematerialization **PASS**
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage3-Batch0005-CHECKPOINT.zip`, SHA-256 `294bf13e4be283621ec3c163d553078f6f616200356efe357d94c41e532a35f5`
- Stage4 is intentionally not claimed during Stage3
- next: **Stage3 Batch0006 from `ma1m-lu-2418`**


**A1-L19 Stage 3 — Batch0006: PASS.**

- target range: `ma1m-lu-2418..ma1m-lu-2436`; cumulative **119/119 new targets enriched**
- **4/4 locked reuses** remain immutable; **123/123 lesson identities** are ready
- cumulative **54 senses + 65 expressions**, **476 exact DE examples** with independent FA + EN
- cumulative **90 evidence-backed relations**, **148 review resolutions**, **119 evidence claims**
- final batch reviews cover discourse/pragmatic forms, colloquial viewing expressions, surprise reactions, person-status vocabulary, shaving/beard phrasing and source-form normalization without rewriting raw provenance
- latest-batch validator **175/175 PASS**; manifest rehash **54/54 PASS**; package hygiene and exact Library rematerialization **PASS**
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage3-Batch0006-CHECKPOINT.zip`, SHA-256 `4ffb30343d93e190b8e4037ae6c4d4268297ce5ba1bff68fc6a159a50b27e054`


**A1-L19 Stage 3 — Evidence & Enrichment: COMPLETE / PASS.**

- **119/119 new targets** complete across Batches0001-0006; **4/4 locked reuses** preserved unchanged; **123/123 lesson identities** ready
- final mix: **54 senses + 65 expressions**; **476 exact DE examples**, each with FA + EN
- **90** evidence-backed relations; **148** review resolutions; **119** evidence claims
- source rows **91** (`1657..1747`) and **90** source-audio refs preserved; known no-audio row **1728** remains explicit and no audio was invented
- Stage3 complete validator **38/38 PASS**; manifest rehash **57/57 PASS**; package hygiene **PASS_NO_PYCACHE_PYC**
- final Stage3 checkpoint: `Menschen-A1-L19-v3.3.2-Stage3-COMPLETE-CHECKPOINT.zip`, SHA-256 `321e8380cf384f65546be1ed90f4290b5ffe35f0f6aa7098c048b84a572e6d89`
- Library rematerialization: **PASS — exact SHA-256 match**
- next: **Stage 4 — Linguistic & Lexical QA**


**A1-L19 Stage 4 — Linguistic & Lexical QA: COMPLETE / PASS.**

- **39/39** custom QA checks PASS across **123** lesson identities; **0 warnings**
- final canonical bundle: **57 senses + 66 expressions**, **57 lexemes**, **492 DE/FA/EN examples**, **91 relations**
- all **125 active review-flag instances** are closed; unresolved: **0**
- **61 bounded Stage4 operations**: 23 expression-type profile normalizations, 4 exact locked-reuse integrations, 34 profile-metadata completions
- the four locked reuse identities preserve their exact semantic core and exact four examples while receiving only A1-L19 membership/audio/review/topic lineage metadata
- source audio lineage: **126 target occurrence refs / 93 unique**; the single zero-audio target remains `ma1m-lu-2409` from source row 1728; no audio invented
- official bundle validator: **123/123 exact-4 examples, 0 warnings**; profile, reference registry and reference availability validators: **PASS**
- framework regression: **47/47 pytest PASS**
- manifest rehash: **34/34 PASS**; package hygiene: **PASS_NO_PYCACHE_PYC**
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage4-CHECKPOINT.zip`, SHA-256 `5ea0d183dff6034f64f1987ed6af01203c41afcc0d5626e198dd0ae388b9cc6e`
- Library rematerialization: **PASS — exact SHA-256 match**
- registered-reference limitations for `dickes Haar`, `flacher Bauch`, `Wer schweigt, stimmt zu.`, `Ach komm!`, `Das gibt's doch nicht!`, predicative `single`, and `Promi` remain explicit rather than being silently overstated
- next: **Stage 5 — Delivery Projection**; runtime binding remains **RESOLVE_CURRENT_AT_STAGE6**


**A1-L19 Stage 5 — Delivery Projection: COMPLETE / PASS.**

- **123/123** Stage4 identities projected 1:1 to Universal v2: **110 de-vocabulary + 13 german-verb**
- categories: **66 Expression, 29 Adjective, 14 Noun, 13 Verb, 1 Adverb**
- **492 DE + 492 FA + 492 EN** examples; **91/91 relations** preserved
- all four locked reuses retain their historical course memberships; **A1-L19 is the primary delivery lesson on 123/123 projected cards**
- source audio lineage: **126 target refs / 93 unique**; only `ma1m-lu-2409` has no target audio; source row **1728** remains the explicit source gap
- direct-import dataset: `A1-L19-UNIVERSAL-v2.tsv`, SHA-256 `e3a9d6bb1ebe9e4a1db0d93d86900e6f15751ded863aec2e30bf8c8f78c9f0e7`
- projected cards SHA-256: `81d7fc6bda2f1c8062542a3a12603a350d1bcbede4ff9d486d608b47d2b6759e`
- projection/fresh-extract validator: **157/157 PASS**; manifest rehash **44/44 PASS**; package hygiene and exact Library rematerialization **PASS**
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage5-CHECKPOINT.zip`, SHA-256 `4370f99ca66344f3eeee9449dc865b498776dc542e47ba4febb47b7b5ce8426a`
- runtime binding remains intentionally **RESOLVE_CURRENT_AT_STAGE6**; no historical runtime was baked into Stage5
- next: **Stage 6 — resolve CURRENT German Flashcards Pro runtime, then exact import/roundtrip/persistence/four-mode presentation acceptance**


**A1-L19 Stage 6 — PREFLIGHT: BLOCKED on exact CURRENT v432/R66 portable runtime.**

- CURRENT freshly resolved: **GFP v432/R66**; LAST_FULLY_VERIFIED remains **v423/R57** and is regression-only
- required exact runtime artifact: `German-Flashcards-Pro-v432-R66-ORGANIZED-DELIVERY-CANDIDATE.zip`, SHA-256 `370ae746045cb0301b37e60a709e7c3a4ca324aa43037fffa867e0bacac63d47`
- Git `main/01-App` is recorded as **EXACT_V432_R66**, but the exact portable ZIP is **not available on an accessible ChatGPT Library/conversation surface**
- policy therefore forbids downgrade to v430/v423 and forbids claiming final Stage6 PASS from Git source alone
- safe preflight completed: Stage5 authority **123 cards PASS**; cumulative identity **12/12 PASS, 2436 unique through L19**; **119 new + 4 expected locked reuses**; exact-v432 test prepared
- preflight checkpoint: `Menschen-A1-L19-v3.3.2-Stage6-PREFLIGHT-GFP-v432-BLOCKED-CHECKPOINT.zip`, SHA-256 `0a2e028f05f04faf141b53fa48be6e08d70c554ff7565464e1d393076a614506`
- Library rematerialization: **PASS — exact SHA-256 match**
- **NOT claimed:** direct-import PASS, presentation PASS, persistence PASS, Universal roundtrip PASS, or final Stage6 PASS
- next: make the exact pinned v432/R66 portable ZIP available, verify its SHA-256, then resume the prepared Stage6 acceptance


**A1-L19 Stage 6 — Runtime & Presentation Acceptance: PASS_WITH_ENVIRONMENT_BOUNDARY.**

- exact CURRENT runtime: **GFP v432/R66**; outer SHA-256 `370ae746045cb0301b37e60a709e7c3a4ca324aa43037fffa867e0bacac63d47` verified against the runtime pin
- exact runtime archive is now persisted in Library and exact-rematerialized; no downgrade to v430/v423 was used
- organized runtime internal rehash: **177/177 PASS**
- exact Stage5 outer ZIP direct import: **21/21 PASS**; runtime/presentation acceptance: **33/33 PASS**
- **123/123** commit manifest, runtime index and Universal-v2 authority roundtrip PASS under the deterministic IndexedDB test boundary
- type projection: **110 de-vocabulary + 13 german-verb**; examples by mode: study=4, quick=2, typing=3, audio=3
- relations: **91/91**; source-audio lineage: **126 occurrence refs / 93 unique**; `ma1m-lu-2409` remains the explicit zero-audio target
- cumulative identity through L19: **12/12 PASS; 2436 unique; 119 new L19 + 4 expected locked reuses**
- Stage6 fresh validator: **24/24 PASS**; package manifest rehash **56/56 PASS**; package hygiene and Library rematerialization **PASS**
- checkpoint: `Menschen-A1-L19-v3.3.2-Stage6-GFP-v432-CHECKPOINT.zip`, SHA-256 `f3b74328e390489869caec427b5a6c1ff0895b26c6a60c75984cddbcb779b2a2`
- separate runtime boundary remains: Fresh exact-package same-profile Windows/Chrome v432 rapid-interaction + persistence + browser restart + offline/service-worker smoke remains required before runtime FINAL/VERIFIED.
- next: **Stage 7 — exact-final A1-L19 LOCKED package + post-package import/presentation verification on CURRENT v432**


**A1-L19 Stage 7 — LOCKED / exact-final PASS_WITH_ENVIRONMENT_BOUNDARY.**

- exact final outer artifact: `Menschen-A1-L19-v3.3.2-GFP-v432-LOCKED.zip`
- SHA-256: `99ccb0fc2a2536335eb5bbcd8e492c8a01cb0093add074424d44a17a0d9e697d`
- exact-final import/runtime/presentation on CURRENT **GFP v432/R66**: **33/33 PASS**
- commit manifest/runtime index/Universal authority: **123/123 PASS** under deterministic IndexedDB test boundary
- card types: **110 de-vocabulary + 13 german-verb**; relations **91/91**; source-audio lineage **126 refs / 93 unique**
- cumulative identity L01-L19: **12/12 PASS; 2436 unique; 119 new L19 + 4 expected locked reuses**
- final package manifest rehash: **55/55 PASS**; package hygiene **PASS_NO_PYCACHE_PYC**
- Library rematerialization: **PASS — exact SHA-256 match**
- content state: **LOCKED**
- separate runtime boundary remains: Content A1-L19 is LOCKED. Separate runtime-level v432 same-profile Windows/Chrome rapid-interaction + persistence + browser restart + offline/service-worker smoke remains required before v432 itself can be FINAL/VERIFIED.
- next: **A1-L20 Stage1/2**
