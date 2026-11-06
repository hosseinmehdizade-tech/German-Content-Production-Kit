# Aspekte B2 · Kapitel 1 R44 — scoped HOLD/MEM-009 delta review (NONIMPORT)

**Date:** 2026-11-06 · **Owner:** Aspekte B2 only · **Authority:** R42 curated current + R43 158-unit preview, NOT the historical coursebook. **Method:** one additional AI editorial review and exact-structure checks; **not independent human/second-model semantic signoff**.

## Verified current inputs and mechanical checks

- `Current/L01-CANONICAL-WORKING-NONIMPORT.csv`: 160 rows; SHA256 `9da4568db9edc592429d35d2ddac4a91fb5369cfff1a5782ce1ce5ef74b88d0b`.
- `Current/L01-158-UNIT-CARD-PREVIEW-NONIMPORT.csv`: 158 distinct draft IDs and distinct fronts; SHA256 `720154fe304c990aeec4dc7b69c70bc36fa22784f8e769d7f208d2724b0b50c3`.
- `Reports/L01-R39-17-HOLD-DECISION-LEDGER.csv`: 17 retained legacy release HOLDs; SHA256 `4ef2c9b345d9a84d5e6ddc370a1be509c39ee323ac37cc769c884cee93868b69`.
- Every preview unit has a nonempty DE front/FA back and 2 paired German+Persian draft examples; all 158 have `export_importable=FALSE` and `linguistic_release_approved=FALSE`.
- All 160 curated source ordinals covered by 158 preview ordinals plus two documented noncard objects #1630/#1660; #1586 has two typed units, #1640 and #1641 one shared unit; no current/source/app/FSRS/SRS edits.
- MEM-009: no automatic splitting for multiple **meanings**; separate grammatical lexical targets at #1586 are a source-specific identity exception. #1647 two senses stay on ONE card. Missing one example per individual sense is INFO, not a release failure. Flat untyped glosses cannot prove internal meaning-to-example anchors.

## One substantive new cross-level lexical-identity risk

**#1575 `ständig`: R43 B2 previews a *new adjective card* while the B1 current accepted content is tagged *adverb* `mb1m-lu-1040`.** Duden lists the dictionary lemma `ständig` as **Adjektiv** and illustrates both attributive `ständige` and adverbial `ständig` uses under the same lemma. Under MEM-009, this is not automatically two separate stable lexical review identities. **New R44 disposition: `IDENTITY_HOLD` pending B1 actual-card identity and approved one-card handling.** Do not automatically publish the second B2 card or modify B1. Evidence: https://www.duden.de/rechtschreibung/staendig ; Duden usage examples include both the adverbial and attributive frames. Even if other sources classify adverbial use as an adverb, that alone is insufficient to assert two independent review identities.

**#1616 `die Art`:** the B2 candidate `Fragen jeglicher Art` is a productive combination of the same noun recognized in A2 CONTENT_ONLY. A separate B2 lexical card is not automatically justified by this phrase. **`IDENTITY_HOLD`** pending current app-card evidence and explicit lexical-target distinction. Neither A2 content-only nor earlier source occurrence is an app-import proof.

## 17 legacy rows — one-by-one current draft dispositions

| Ordinal | R44 editorial disposition | What is known / action before release |
|---:|---|---|
| 1556 | `EDITORIAL_PROVISIONAL` | B2 abenteuerlich stand-alone adjective remains; no exact accepted prior verified. **Next:** retain draft; absent A1 proof does not justify deletion; final independent DE/FA QA open. |
| 1575 | `IDENTITY_HOLD` | same lexical adjective in attributive/adverbial contexts; do not automatically create second card for B1 ständig. **Next:** Duden marks ständig Adjektiv and gives both ständig Ärger and ständige Nörgelei; reconcile B1 accepted card ID before selecting one-card enrichment. |
| 1586 | `EDITORIAL_PROVISIONAL` | one source cell has adjective vielsprachig + noun die Mehrsprachigkeit. **Next:** two grammatical learner targets already represented as 2 R43 draft units; preserve one immutable source ordinal. |
| 1588 | `EDITORIAL_PROVISIONAL` | Vielsprachigkeit noun kept with contextual usage label, not automatic antonym/synonym merge. **Next:** no universal sense distinction claimed; review final context tag. |
| 1609 | `EDITORIAL_PROVISIONAL` | entscheidend adjective is not identical to old B1 im Voraus entscheidend phrase. **Next:** retain stand-alone adjective draft; no automatic earlier-phrase suppression. |
| 1610 | `EDITORIAL_PROVISIONAL` | geteilt + in + Akk. stative-result example and geteilter Meinung sein remain as two usages. **Next:** participle plus idiom in one preview, no split for polysemy. |
| 1611 | `EDITORIAL_PROVISIONAL` | hilfreich bei + Dat. and hilfreich für + Akk. both recorded. **Next:** examples support separate frames; final language QA still required. |
| 1616 | `IDENTITY_HOLD` | A2 die Art exact standalone lemma is CONTENT_ONLY; phrase Fragen jeglicher Art is semantically compositional. **Next:** confirm whether existing die Art learner card is imported and whether phrase is a registered distinct fixed-expression target; avoid automatic second same-lemma review identity. |
| 1630 | `IDENTITY_HOLD` | B1 accepted-content intolerant same adjective sense, user-reported import only. **Next:** verify live B1 ID or user-approved identity reuse; retain full non-card sidecar; do not delete source. |
| 1640 | `EDITORIAL_PROVISIONAL` | canonical Migrantenfamilie draft covers source IDs 1640 and 1641. **Next:** no original source ID or example history deleted. |
| 1641 | `EDITORIAL_PROVISIONAL` | exact duplicate source row retained as second provenance ordinal. **Next:** single draft card for same noun/meaning; no second review identity. |
| 1647 | `EDITORIAL_PROVISIONAL` | Ausländerquote has share/percentage and prescribed-quota senses. **Next:** one card, both senses; contextual examples provided, no per-sense example quota imposed. |
| 1660 | `TARGET_LINK_HOLD` | gekommen is Partizip II of kommen, not independent lemma. **Next:** resolve link to actual prior kommen learner unit; do not mint standalone gekommen verb card. |
| 1671 | `EDITORIAL_PROVISIONAL` | zerreißen transitive hat vs intransitive ist usage. **Next:** one lemma with two contexts; B1+ nonimport source occurrence not duplicate accepted-card proof. |
| 1675 | `EDITORIAL_PROVISIONAL` | einig + constructions not simple obligatory in + Dat. frame. **Next:** sich einig sein / in einer Frage einig sein retained. |
| 1693 | `EDITORIAL_PROVISIONAL` | Juryvorsitz denotes office not person. **Next:** correct noun gloss kept; source semantic ambiguity not imported. |
| 1697 | `EDITORIAL_PROVISIONAL` | Kinokasse independent noun not proved accepted elsewhere. **Next:** keep draft; embedded old phrase not a standalone accepted learner-card ID. |

## Decision states and nonclaims

- **13/17** original HOLDs now have *traceable draft design dispositions*, not semantic release approval.
- **4/17** retain explicit lexical-target identity/link blockers (#1575, #1616, #1630, #1660), rather than treating a source-word spelling overlap as proven duplication.
- **17/17** legacy formal release HOLDs remain open: editorial dispositions are not final independent German–Persian QA or app/SRS identity verification. This is not an assertion that 13 have been formally cleared.
- R43 remains the authoritative unchanged learner-facing **draft**; no added/deleted cards, no `Stage2=PASS`, no Stage3–Stage7, no import, no published flashcards. R25 L05 global portable checkpoint remains unchanged.
- Next bounded action: verify the four existing-card/link identities and make an authorized *delta-only* revision of the affected R43 units, then independent bilingual QA of changed/dependent examples and the remaining 13 editorial candidates. Do **not** rerun an old textbook inventory or full historical source fidelity scan.

### Audit receipt

`count_preview=158; count_R42_source=160; count_legacy_HOLD=17; draft_disposition=13; identity_or_link_HOLD=4; importable_count=0; preview_sha256=720154fe304c990aeec4dc7b69c70bc36fa22784f8e769d7f208d2724b0b50c3; source_mutations=0`