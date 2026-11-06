# Menschen A2 R20 — Vorderseite / Rückseite prepackaging audit (2026-11-06)

**Decision: PREPACKAGING HOLD for full front/back compliance.** Read-only scan of the real 1,778-card R20 Library ZIP. This does **not** revoke the historical 24 lesson Stage7 content locks or imply a browser Stage6 test.

## Exact source and policy
- Source ZIP: `Menschen-A2-24-Lektionen-1778-KARTEN-ALLE-KORREKTUREN-GEPRUEFT-CONTENT-ONLY-20261106.zip`
- Full ZIP SHA256: `b8cffeeb25553eb254f410583ecda85041c2547a69ed9e99d8ef683e19590548`
- Library stable ID: `libfile_1a41b752e5b08191ba89ed6861a80ac4` (current `Content/Menschen-A2/Releases/`).
- Contract: `Prompt/GLOBAL-FLASHCARD-FRONT-BACK-PRESENTATION-CONTRACT-v1.0.0.md` (blob `c9070b91fea3177783ef6b5e4db9db6c0b984ca9`); HF2 front v1.1.0, app-side conditional Lean Formen.
- Scope: parsed all 1,778 rows from `01-Content/A2-C3-1778-cards.tsv`, their `custom_fields.canonical_unit.core`, `canonical_target.morphology` and `details`, independently of packaging's Stage5 report. No source, learner state or app edits.

## Findings and exact confidence
- **758 Noun:** explicit canonical article/plural forms are found on the raw TSV front. There are 80 noun rows lacking both `core.plural` and typed `core.plural_status`; many have noncount morphology/prose or a different legitimate noun structure. These are **review signals, not 80 proven wrong plurals**. Two multi-gender article-bearing noun rows use alternative morphology shapes and are not automatically broken.
- **248 Verb:** all have `present_3sg`, `preterite`, `perfect` and those three strings are present on raw front. Static semantic/form audit only, not actual learner-renderer acceptance.
- **140 Adjective:** 90 have verified canonical comparative + superlative. Only 48 show both on raw generic front, **42 show neither**: confirmed HF2 raw-front transport violations despite the forms existing on back/metadata. Remaining 50 have no verified degree pair; six show typed comparison dispositions, **44 lack typed closure in `core`**, though some contain prose explanations. Explicit source-bound review is required; never invent comparison for non-gradable adjectives.
- **893 physical `Formen` sections / 1,819 items** in the source TSV. On a conservative raw-field value comparison **669 sections have no unique content beyond text already on the raw front** (485 nouns, 160 verbs, 24 adjectives). These are candidates for **conditional UI display filtering**, **NOT** 669 observed duplicate panels in the current browser. Preserve stored `Formen` data; genuine Genitiv/Imperativ/Konjunktiv II and front-hidden facts must remain. `Card Design Studio` affects front visibility and Quick has inherited three-detail limit.
- The official app Lean Formen candidate (SHA `028611a10b2da78bf3fbb88856d67c77f827445fecdf57ad845f44b02c866199`) remains **NOT CURRENT, NOT FULLY CORRECT** (plural-only and Custom fallback gaps) and native Stage6 unobserved. App CURRENT remains `v505-R141`, not a certified Lean Formen implementation. Import regression #25 remains open.

## Exact 42 adjective front IDs
`ma2m-lu-0040`, `ma2m-lu-0069`, `ma2m-lu-0098`, `ma2m-lu-0099`, `ma2m-lu-0102`, `ma2m-lu-0103`, `ma2m-lu-0164`, `ma2m-lu-0170`, `ma2m-lu-0174`, `ma2m-lu-0189`, `ma2m-lu-0211`, `ma2m-lu-0212`, `ma2m-lu-0213`, `ma2m-lu-0214`, `ma2m-lu-0216`, `ma2m-lu-0217`, `ma2m-lu-0219`, `ma2m-lu-0225`, `ma2m-lu-0228`, `ma2m-lu-0279`, `ma2m-lu-0283`, `ma2m-lu-0286`, `ma2m-lu-0287`, `ma2m-lu-0294`, `ma2m-lu-0299`, `ma2m-lu-0326`, `ma2m-lu-0373`, `ma2m-lu-0402`, `ma2m-lu-0407`, `ma2m-lu-0502`, `ma2m-lu-0536`, `ma2m-lu-0544`, `ma2m-lu-0554`, `ma2m-lu-0555`, `ma2m-lu-0614`, `ma2m-lu-0623`, `ma2m-lu-0683`, `ma2m-lu-0697`, `ma2m-lu-0705`, `ma2m-lu-0728`, `ma2m-lu-0768`, `ma2m-lu-0775`.

## Demonstrations
- `ma2m-lu-0040`: front `kompliziert`, but `Formen` has `Komparativ: komplizierter` and `Superlativ: am kompliziertesten`. Generic front is incomplete.
- `ma2m-lu-0001`: `der Bäcker, Bäcker` raw front; `Artikel`/`Singular`/`Plural` repeated in stored back, but `Genitiv: des Bäckers` is genuinely additional, **retain**.
- `ma2m-lu-0004`: `zuhaben, hat zu, hatte zu, hat zugehabt` raw front; `Präsens: hat zu` repeated in stored back.
- `ma2m-lu-0124`: `waagerecht` has noncomparison information in freeform morphology; no speculative gradable morphology allowed.

## Safe next actions
1. Keep R20 **unchanged** as current evidence-backed content-only artifact, not fully front/back compliant and **NOT import-ready**. Reproduce the 42 hard front gaps on an authorized **new R20-derived candidate**, source-bound; independently QA Stage4/Stage5 + negative cases before any packaging promotion. No bulk editing historical LOCKED.
2. Triage the 44 adjective typed closures and 80 noun plural status/shape cases. Document authentic exceptions; do **not** fabricate comparative, plural or article. Preserve identity, typing target, A1 exclusions, lesson links, example translations, Wortnetz and SRS.
3. Separate *app consumer* authority: verify current/approved successor Study/Quick conditional Lean Formen, plural-only, multi-gender, Custom fallback, Card Design Studio and all modes. Exact CURRENT app import/reload/backup/SRS/FSRS still blocked; #25 must not be silently called fixed.
4. No new per-lesson Chrome/FSRS kits, no report-only Library ZIP, no app/UI/FSRS changes and no unsupported FINAL claim.

**Source QA result:** scoped read-only scan completed with exact input SHA. **Git report publication** does not itself mean Stage4/Stage5 rereview, native Stage6, content R21 release or global runtime FINAL.
