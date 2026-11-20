# OP-02 — v505 exact archive integrity and isolated Chromium replay (2026-11-02)

Status: PASS_SCOPED_PACKAGE_INTEGRITY_AND_EXACT_CODE_REPLAY__NATIVE_STAGE6_BLOCKED. No content, UI, runtime, or release changes.

## Raw package verification
- Original user-uploaded GFP-v505-R141-COMMITTED-STORAGE-ARCHITECTURE-QA-CORRECTED-CANDIDATE(1).zip SHA256 482b285bc4a1364e5595f721ecbf0caddcb95ba0eb2cdf9958d9aa11c889416e; equal official current v505 pin.
- ZIP CRC PASS, 266 archive entries; 265/265 SHA256SUMS.txt entries verified against exact extracted contents; no mismatch/missing.
- 01-App/index.html SHA256 0b7358d2755a80d1563e5b4791f62ec72c6a42279914739d551aef1f4d2a0ea5; matches official v505 component hash.
- In-archive v503 CURRENT language is historical; live root GitHub CURRENT points to v505-R141 (Candidate, not FINAL).

## Extracted package regressions
- Runtime asset references test PASS: 152 refs / 69 cohort resources.
- Shell cohort test PASS: 69 resources / six negative controls.
- Inline JS syntax PASS: four scripts.

## Explicit browser evidence limits
- Direct Chromium navigation to exact localhost and file:// app was blocked by ERR_BLOCKED_BY_ADMINISTRATOR, an environment policy limit, not a demonstrated app defect. No real native app import, IndexedDB or Study/Quick DOM was observed.
- Independently extracted verbatim v505 functions detailKindV339, presentationProjectedDetailsV459, presentationDetailVisibleV458, presentationDetailSectionsV339 and presentationModeConfigV339; ran them in installed Chromium about:blank with stub helpers, source queue snippets and synthetic card wrappers.
- 105 outstanding original queue snippets / 66 cards: 57 bridge into default Study and Quick source-model sections; 48 remain unprojected in both modes when a nonempty partial combination section preempts the bridge. These are not original imported TSV rows.
- Five priority queue IDs: ma1m-lu-1662 1/1, ma1m-lu-1846 2/2, ma1m-lu-1885 0/3, ma1m-lu-2279 1/1, ma1m-lu-2933 0/1; synthetic wrapper only. Hidden combinations override control suppresses section.

## Next verified boundary
- Acquire exact original Menschen A1 V22 source ZIP and TSV, SHA256 74cdbf5b6d0121421fac8235124e738929b9764f3696db532cc54f9509f5757d and 024ee77efbb3675a0720491af1da2286e2186bd00bc83bcbb9dfef22b0656c9a, then native isolated browser import + captured DOM under a permitted origin.
- No Stage5/6/7 PASS, no editorial clearance for 48 missing combination placements, no automatic card mutation, no Git issuer trust claim or release promotion. All 105 remain review-PENDING.
- Detailed local audit and replay JSON are retained with this turn's user artifact; this Git file is a compact metadata handoff only.
