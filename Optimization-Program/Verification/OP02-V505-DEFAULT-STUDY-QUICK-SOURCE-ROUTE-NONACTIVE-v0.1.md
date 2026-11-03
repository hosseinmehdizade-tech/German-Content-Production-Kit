# OP-02 — Exact CURRENT v505 source-level Study/Quick combination analysis (NONACTIVE)

Scope: Stage5→6 QA optimization and source-only static evidence, **not a browser DOM test**, card transformation, source/editorial approval, or release gate. No UI/runtime code modification is proposed here.

## Authorities and static source limits

- CURRENT v505-R141, nonfinal; app component SHA256 `0b7358d2755a80d1563e5b4791f62ec72c6a42279914739d551aef1f4d2a0ea5`, independently verified against exact candidate Git blob `f416070ded93843ec5370052be251b2ac7919af5` in previous OP-02 checkpoint. Whole portable ZIP SHA is still NOT independently recomputed. Git `main` app mirror remains v486 historical.
- Verified v505 `presentationProjectedDetailsV459` SHA256 `51645e4cfafabcd0370d2659ca75ef5b83bc3ad53049a262a396ba397bcfc378` matches legacy exact projector. `presentationDetailSectionsV339` is a different higher-level v505 function.
- Verified embedded presentation contract `gfpGermanLanguagePresentationContract`: `back.details_order = [english,features,combinations,grammar,...]`, `study.details='full'`, `quick.details='collapsed'` (top 3); `card_design_studio.hidden_sections` can suppress sections when user presentation overrides are present. Actual saved user presentation overrides are unknown. `presentationOverridesV340()` is sourced from `appSettings()?.germanLanguagePresentationOverrides`.
- Source data: original Menschen A1 V22 archive SHA256 `74cdbf5b6d0121421fac8235124e738929b9764f3696db532cc54f9509f5757d`, TSV SHA256 `024ee77efbb3675a0720491af1da2286e2186bd00bc83bcbb9dfef22b0656c9a`. The 105-unit PENDING queue is **recomputed from original archive** and compared field-by-field to the queue input before any classification; no forged source item ID or invented review decision.

## Source-model results

- 105 original unresolved source units from 66 cards remain PENDING.
- 57 on 39 cards: nonempty object-shaped `kombinationen_v1`, correct `visible_section`, and no pre-existing nonempty Details.Kombinationen. The projector generates the combined DE — FA strings; combinations is rank 3 and survives default Study full and Quick collapsed sections, **conditional** on standard per-user overrides. This is source-model exposure, NOT a browser observation.
- 48 on 27 cards: pre-existing nonempty Details.Kombinationen short-circuits the projector. These source items **do not enter the v505 projected Kombinationen section**; they may appear elsewhere but are not source-bound as bilingual combinations. Both Study and Quick have a partial section, but not those items. No bulk auto-append or duplication is approved.
- Cross-check of 119 cards with **302** accepted combinations stored in nonempty *legacy list-shaped* `kombinationen_v1`: each original `canonical_unit` lacks a complete examples array; the versioned `parseCanonicalUnitCandidateV348` requires examples to treat that field as a full canonical content unit. Since a legacy list is rejected by the bridge and there is no full envelope, physical Details are handled by the legacy fallback. Do **not** falsely add those 302 to the missing-from-UI bucket. Actual browser must still verify resulting presentation.

## Red-line guardrails

- All 105 remain open; Stage5 formal full-suite, Stage6 actual native import, Stage7 final delivery NOT passed.
- No claim about the actual complete UI, user presentation settings, language toggle, animation, import transformation, hidden DOM, browser storage or card-specific filtering.
- Scanner creates only an output diagnostic and exits `2` even when the source-side analysis succeeds: a green CLI cannot be mistaken for native Stage6 approval. It refuses to overwrite existing output and checks source ZIP SHA plus the full independently regenerated pending queue. Static JS function identity is externally attested in the previous checkpoint and represented as a fixed source pin, not freshly rehashed from the portable ZIP by this Python script.
- Future acceptance needs exact ORIGINAL CURRENT v505 full release bytes or independently equivalent fully attested source tree, browser Study/Quick isolated-profile native import and captured DOM for five priority IDs then all unresolved cases, explicit source-bound semantic disposition, independent adversarial review, and official Stage5/6/7 gates.