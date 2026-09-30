# Menschen A1 Verben Repair v3.3.6

Current durable milestone: **Stage6 Runtime & Presentation Acceptance PASS on exact CURRENT v451-R85**.

- Runtime: **German Flashcards Pro v451-R85**, CURRENT = LAST_FULLY_VERIFIED
- Runtime artifact SHA-256: `27da34ebecde9274aa7323a300aad979325914522460b914139e71f966131be4`
- Internal runtime SHA256SUMS: **298/298 PASS**
- Stage5 dataset: **310 cards = 247 Verb + 63 Expression**
- Card type: **310/310 de-vocabulary**
- Presentation contract: **gfp-vocabulary-neutral@1 on 310/310**
- Examples: **1240 DE + 1240 FA + 1240 EN**
- Relations: **768**
- Source audio: **310 refs / 275 unique; zero-audio targets ma1m-lu-0073 and ma1m-lu-0074**
- Import-ready package SHA-256: `ce86e7b3df447a77f6fdff74b8f2cd493804031ad4e4594070b634cdcd8029b7`
- Phase1 import/presentation: **48/48 PASS**
- Phase2 authority roundtrip: **26/26 PASS**
- v451 neutral-envelope regression: **21/21 PASS**
- Combined Stage6 checks: **95/95 PASS**
- Commit manifest: **VERIFIED / 310**
- Runtime index: **310/310**
- Storage: **READY / writesBlocked=false**
- Study / Quick / Typing / Audio all run on the full 310-card library scope.
- Stage6 checkpoint SHA-256: `102dddf34c7ff862c99d07e470c57d8a0fc042113ac924a460afa823a3702e70`
- Post-package: **CRC PASS; manifest 26/26; SHA256SUMS 27/27; JSON 20/20; hygiene PASS**
- Library rematerialization: **PASS exact SHA-256 + byte compare**
- Runtime/UI changed: **NO**

A runtime TSV normalization collapsed one redundant space in the provenance-only Persian source seed of `ma1m-lu-1267`; learner-facing semantic content is unchanged.

The same-profile Windows/Chrome visual/import/reload/PWA/offline acceptance is inherited from exact v451 FINAL because this Stage6 milestone changes content only and does not change runtime/offline/storage/deployment semantics.

Next milestone: **Stage7 exact-final release + post-package verification + re-lock**.
