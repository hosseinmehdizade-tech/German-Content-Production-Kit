# Aspekte B1+ — Gate08: actual exact-current v505-R141 multisense source fix on Draft PR #41

**2026-11-11 · NONPROD only · no main app modifications · no importer release approval.**

## What was delivered (code, not another abstract audit)

Created an exact-source, reviewable [nonproduction patch](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/blob/candidate/b1plus-preimport-guards-review-20261110/08-Release-Tools/B1Plus-Nonprod/GATE08-PRESERVE-MULTISENSE-EXACT-CURRENT-NONPROD.patch) and [regression test](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/blob/candidate/b1plus-preimport-guards-review-20261110/08-Release-Tools/B1Plus-Nonprod/test_exact_source_multisense.cjs) in the already-existing [Draft PR #41](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/pull/41). It operates against the actual **v505-R141** current `01-App/index.html` SHA `f38877d7ff39ad24294303125ae60d77955c251768fffa059cf7452a0a3aef26`; it does **not** change that tracked file.

Four precise source modifications: (1) preserve source `sense_ids` in canonical normalizer, (2) preserve `sense_ids` in compact runtime rich-example projection, (3) do not consider rich examples covered by canonical fallback when distinct sense links are absent, and (4) enrich presentation canonical associations **only** when the rich example has exactly one source ID and matches exact ID/text/language/DE–FA translations with compatible scalar sense, without overwriting conflicting canonical links.

## Repro and verification

- Real B1+ source ordinal 363: `alle / alles / aller-`, example `Alle waren da, aber nicht alles hat funktioniert.`, `sense_ids=[S1,S2]` in original. **Before** source projection drops S2; **after** source projection retains both. Duplicate IDs, conflicting Persian translation, incorrect ID, incompatible sense and other negative conditions are tested.
- Local Node source-exact harness: **15/15 PASS** (including before-state reproduction and negative checks).
- GitHub [Gate08 workflow](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/actions/runs/42934103308) completed **SUCCESS**, applying the patch only to a disposable copy and verifying the original hash remains unchanged.
- Exact candidate temporary index SHA: `76edb04b8c97ac08efd44263e52704b8aa722c49e8a08b242c3ed5be7a3a3052`.
- Exact patch SHA: `65bd86545c2a275ab71021f2e728e057eb98bcf0bbdc49ebb2590e94239b9083`.
- Library evidence ZIP: `libfile_b55d5676e6808191b54dc9a0973c6029`, SHA `35b39c3a0a2e241e3962e492fd67371ea1cbb8cb06fa30cbf82146d9a2f3ec83`, 8 members / 7 SHA manifest entries. Library exact readback PASS.
- The canonical content Master is **unchanged**, ZIP SHA `302c50d61d23990f487a4d34114b9d49074e7fe5213b08af6778c5233ecd1d90`, primary SHA `b0ebab61cfbb9a4a2f625316e421fd9bb7cf5a4a82c1d13432683bb409e86e80`, all 1571 cards and 3607 bilingual examples.

## Broader red CI: two distinct blockers, not an excuse to merge

- [CURRENT engineering and artifact gate](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/actions/runs/42934103252) **FAILED** at portability SHA contract: the workflow expected older v503-R137 portable hashes while the app PR checks out actual v505-R141.
- [OP-03 Immutable ZIP publication](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/actions/runs/42934103293) **FAILED** on Ubuntu and Windows because `03-Tests/test_release_archive_publish.py` imports `archive_publish_transaction` which the checked-out `08-Release-Tools/release_contract_lib.py` does not export.
- Current dedicated nonprod guard workflow also green, but that is **not** the overall release gate.

## Release still blocked

Chromium local HTTP navigation is administratively blocked (verified: `net::ERR_BLOCKED_BY_ADMINISTRATOR`). There was no real stable-origin successful TSV/JSON/ZIP import, no actual right-card UI acceptance, no IndexedDB write/reload, no SRS retention, no backup/rollback and no owner-controlled trusted manifest approval.

Next productive work **belongs in app integration**: review/apply Gate08 source patch to a separately reviewable candidate alongside PR41 ingress guards; fix the two broader CI contracts without blindly overwriting current hashes or bypassing gates; test exact release package under a real supported HTTP(S) origin and isolated learner profile; explicitly approve exact content digest only if end-to-end acceptance passes. Do not re-open lessons/P1/P2/P3.

**No merge, app release, learner data mutation, or import of the NONIMPORT content is authorized.**
