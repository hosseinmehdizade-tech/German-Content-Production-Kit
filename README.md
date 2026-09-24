# German Content Production Kit — active v3.3.2

The active production framework is **v3.3.2 — Menschen Course Export Ready**. GitHub is the compact durability/coordination mirror; exact verified portable artifacts live in ChatGPT Library and are identified by SHA-256 in `PROJECT-STATE.json`.

Current Menschen workstream: `Workspaces/menschen-a1a2b1-memrise/`. **A1-L01 through A1-L17 are LOCKED. A1-L18 Stage 5 is COMPLETE / PASS; Stage 6 Runtime & Presentation Acceptance is next.**

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
