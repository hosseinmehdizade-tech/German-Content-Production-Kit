# 250 Verben mit Präpositionen — Kombinationen successor

Status: **Stage3B COMPLETE — Batch15 PASS** under German Content Production Kit v3.3.6.

This workstream is an explicit semantic successor to the immutable 292-card LOCKED release. It adopts `Prompt/LEXICAL-KOMBINATIONEN-ENRICHMENT-POLICY-v1.0.0.md` without mutating the historical parent.

Current coverage: **292/292 cards**, **1255 accepted Kombinationen**, **0 Stage3B cards remaining**.

Batch15 covers `usrin-vmp-u-0281..0292`. It changes only `details` + `custom_fields` on those 12 targets; the other **280/280** raw TSV lines are byte-identical to Batch14 ACCEPTED, and prior Batch01–14 rows **280/280** remain byte-identical. Canonical identity, examples, relations and source lineage remain unchanged.

Batch15: **12 cards / 54 accepted items / 54 FA + EN translations / 12/12 one visible Kombinationen section / QA PASS**. Provenance is parent-grounded only: **48 parent-example items + 6 parent-canonical-relation items + 0 curated items**.

Global Stage3B projection: **292/292 cards** have exactly one learner-visible `Kombinationen` section; visible legacy `Rektion` / `Kollokationen` / `Nomen-Verb-Verbindungen` sections are **0**. Backend typing/provenance and preserved parent sections remain structured.

Portable Batch15 artifact:
- `250-Verben-mit-Praepositionen-v3.3.6-Kombinationen-Batch15-usrin-vmp-u-0281-0292-ACCEPTED.zip`
- SHA-256 `f10fd5c20008b3a2564f946d43ea56e49cb62b610a8fdda57d30b17164c3d251`
- Library rematerialization: **PASS_EXACT_SHA256_AND_BYTE_COMPARE**

Stage3B is complete. Next major stage: **Stage3C disposition closure** across all 292 targets. Stage4 must not start until Stage3C explicitly closes every Kombinationen disposition.


## Stage3C disposition closure

- Status: **PASS / COMPLETE**
- Dispositions: **292 VERIFIED_PRESENT / 0 CLOSED_NO_FORCE / 0 NOT_APPLICABLE / 0 unresolved**
- Accepted Kombinationen: **1255**
- Learner-visible projection: **292/292 exactly one Kombinationen; 0 separate Rektion/Kollokationen/NVV**
- Stage3C artifact: `250-Verben-mit-Praepositionen-v3.3.6-Kombinationen-Stage3C-DISPOSITION-CLOSED.zip`
- SHA-256: `663be2a46e608001b6e3bc2ae9f99432d2858bc04c9a037ff0e1983981be6806`
- Library rematerialization: **PASS exact SHA-256 + byte compare**
- Content mutation vs Batch15: **NONE**; accepted TSV byte-identical
- Rejection/non-surfacing memory persisted: **30 records / 31 target instances**
- Next: **Stage4 independent linguistic/provenance/completeness re-audit**.


## Stage4 independent re-audit

- Status: **PASS AFTER BOUNDED REPAIR**
- Input: exact Stage3C CLOSED artifact, SHA-256 `663be2a46e608001b6e3bc2ae9f99432d2858bc04c9a037ff0e1983981be6806`
- Independently reviewed: **292 targets / 1255 Stage3C Kombinationen**
- Removed after Stage4 review: **5** weak/redundant items
- Accepted after repair: **1250**
- Origins: **1154 parent examples + 74 parent canonical relations + 22 curated**
- Dispositions remain: **292 VERIFIED_PRESENT / 0 CLOSED_NO_FORCE / 0 NOT_APPLICABLE / 0 unresolved**
- Projection: **292/292 exactly one Kombinationen section; 0 visible legacy Rektion/Kollokationen/NVV**
- Differential vs Stage3C: **5 rows changed; 287/287 other rows byte-identical; only details + custom_fields changed**
- Canonical identity, examples, relations, IDs/order and source lineage: **UNCHANGED**
- Artifact: `250-Verben-mit-Praepositionen-v3.3.6-Kombinationen-Stage4-INDEPENDENT-REAUDIT-PASS.zip`
- SHA-256: `b254d17d84097ade53854ae541693cbb895bac0d37d5e75b3e7501080fa3d19a`
- Library persistence: **PENDING** because the Library upload bridge returned `container_session_expired` twice; no further retry was made this turn.
- Next: retry exact Stage4 Library persistence/rematerialization, then **Stage5 projection + clean-delivery anti-bypass/package gates**.


## Stage5 projection + clean delivery

- Status: **PASS**
- Stage4 Library durability repaired first: **PASS exact SHA-256 + byte compare**
- Projection: **292/292 `de-vocabulary` + `gfp-vocabulary-neutral@1`**
- Kombinationen: **1250 accepted items**, **292/292 exactly one visible `Kombinationen` section**, **0 visible legacy Rektion/Kollokationen/NVV**
- v3.3.6 clean-delivery builder: **PASS** (source occurrence, identity closure, candidate ledger, enrichment completeness, unified vocabulary)
- Successor projection + lineage preflight: **PASS**
- Stage5 checkpoint: `250-Verben-mit-Praepositionen-v3.3.6-Kombinationen-Stage5-PASS-CHECKPOINT.zip`, SHA-256 `8f472a96fefd2b89716d50de3b3f4cb0896102f03657044cfa21a9966b1d5623`
- Clean delivery: `250-Verben-mit-Praepositionen-v3.3.6-Kombinationen-Stage5-CLEAN-DELIVERY.zip`, SHA-256 `a7f59a910cb468e0bad61136bdedbc024fda88c886d6aa3fc5fb4f361ed8b690`
- Both Library rematerializations: **PASS exact SHA-256 + byte compare**
- Runtime binding: **deferred to Stage6 CURRENT**
- Next: **Stage6 exact CURRENT runtime import/presentation/persistence acceptance; never downgrade.**
