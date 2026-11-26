# OP-02 V24 / exact CURRENT v505 read-only continuity audit (2026-11-02)

**Scope:** PROCESS QA only; no learner/card edits, releases, UI/runtime mutation or library imports. THIS IS NOT a native Stage6 PASS.

## Exact user-supplied portable inputs
- Menschen-A1-V24 complete delivery ZIP SHA256: `19a9edb447286e4d5bb796a882da471cb666f39f81acfcc0c0b9c69a937d19ff`.
- Separate v505-R141 current app ZIP SHA256: `482b285bc4a1364e5595f721ecbf0caddcb95ba0eb2cdf9958d9aa11c889416e`; byte-equal to V24 bundle's `App/EXACT-v505-R141-ORIGINAL.zip`.
- V24 ZIP: CRC PASS, 302 members, 300/300 SHA256SUMS checks PASS, 300/300 MANIFEST sizes/hashes PASS; two self-reference control files naturally excluded from SHA list.
- V24 import TSV SHA256: `3ff2cd60f7d22fb989f0d4e9e885949b0bc4a91f4b77fd6192701d1315ba0b5e`; identical to official Stage5 ZIP internal TSV. Official Stage5 inner ZIP SHA256 `bf1220eaa7199d89eb7b2aeca39373e18d3da7885dbb4dfd80f548be812e9bf5`.

## Direct V24 content checks
- 2,997 rows / 2,997 distinct IDs / 23 TSV columns / 24 lessons. Both `deck` and `source` are `Menschen A1` for every row.
- Every card has exactly 4 examples, totaling 11,988; Persian and English text present in each, checking both `translations` array and object variants.
- `kombinationen_v1`: 2,803 object cards with 1,878 items plus 194 list cards, including 119 nonempty lists with 302 items; total 2,180.
- Package documentation claims precisely 2,894 `source` changes from V23 and 22 untouched fields; original V23 TSV not supplied in this turn so direct parent diff is not claimed.

## OP02 source-to-view continuity
- Independently compared all 105 historical V22 unresolved queue units with the original **V24** TSV. 105/105 exact `de`, `fa`, `en` and item ordinal matches; zero mismatches, 66 affected card IDs.
- 57 still have source-model Auto-Bridge potential; **48 on 27 cards still have a pre-existing partial physical Kombinationen section**, which v505's unchanged `presentationProjectedDetailsV459` short-circuits.
- For those 48, German text occurs exactly in a different physical section on 35 `Verwandte Wörter` items and 3 `Kollokationen` items, with no exact other-section German match for 10. This does NOT establish learner-visible FA/EN pairing.
- Priority cases `ma1m-lu-1662`, `-1846`, `-2279` remain bridge candidates, and `-1885`, `-2933` remain conflicts. No unreviewed bulk append permitted.

## Acceptance boundaries
- Bundle's official Stage5 report says PASS; Stage7 **file packaging** passes, but native browser import, actual Study/Quick DOM and SRS/IndexedDB reload remain NOT RUN. Current V24 delivery is intact and no new test is a prerequisite to receiving it.
- Do not import `Reports/L09-127-REFERENCE-ONLY-DO-NOT-IMPORT.tsv` alongside the full import. No auto-import/replace/delete/reset progress or mutation of LOCKED, A2/B1 or original source.
- Independently review the 48 source-bound display/semantic placement cases and validate actual native isolated Study/Quick only on a permitted browser origin. Keep OP-01 trusted-issuer governance separate.
