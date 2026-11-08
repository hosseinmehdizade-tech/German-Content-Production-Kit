# Lesen — grammar reference currentness gate (v1, 2026-11-08)

**State:** owner-scoped prospective prevention contract, attached to the verified R32 recovery package. It is **not yet embedded automatically into every historical Lesen producer or app import**. No UI, FSRS/SRS, runtime or existing CURRENT content mutation.

## Failure fixed

During editorial improvements from R18–R30, text and IDs changed while 63 curated grammar annotations still pointed at deleted phrases, with 30 downstream learner-facing exercise quotes also stale. Fourteen comparative `als` constructions were incorrectly marked temporal, and 12 more curated samples were category-invalid. R31 independently caught 89 grammar errors and four DE/FA/EN discourse conflicts. R32 corrected the exact evidence cohort while retaining 669 curated annotation IDs and 3,548 fulltext occurrences.

## Minimum mandatory read-only gate for any new/edited Lesen master

1. Use the **exact current owner candidate** identified by `LATEST.json` and hash receipts, never the original publisher PDF as a substitute.
2. Validate every curated grammar annotation's `section_id`, `sentence_id`, and exact `target_text` together against the **current** German sentence, not merely a preserved ID.
3. Validate every quoted excerpt in `grammar_tasks[].prompt_de` against the actual current lesson and updated annotation. If an annotation moves or changes category, revise the learner-visible exercise and DE/FA explanations in the same transaction.
4. Check all `full_text_occurrences[]` positions as **section-relative character offsets**. A valid offset is not enough: test category truth for comparative `als`, passive, attributive adjective endings, and whether `damit` introduces an actual purpose clause or is a pronominal adverb.
5. When changing a German causal/concessive connector, compare current p02–p07 argumentation with the existing Persian and English translations before choosing which side to edit. Re-anchor every affected grammar marker. Do not auto-overwrite translations that were already faithful.
6. Rerun an independent delta/preservation verifier, genuine exact-current v505 JavaScript native-source preentry, negative mutations and deterministic replay. No evidence of independent wholepack Stage4 may be inferred from these technical successes.

## Reproducible reviewed reference

The exact verified source Python tool is `04-Tools/gate_reading_grammar_currentness_v1.py` inside the R32 ZIP pinned in `QUALITY-REVIEW-CHECKPOINT-R32-20261108.json` and `LATEST.json`.

After extracting that owner ZIP:

```bash
python 04-Tools/gate_reading_grammar_currentness_v1.py 01-Content/R30-PARENT-MASTER.json
# Expected FAIL: 117 findings, including 63 stale anchors and 30 stale exercise quotes

python 04-Tools/gate_reading_grammar_currentness_v1.py 01-Content/Lesen-Production-Master-v1.3.0-R32-GRAMMAR-LOGIC-REPAIR-CANDIDATE.json
# Expected scoped PASS: zero defects

python 04-Tools/verify_portable_r32.py
# Expected exact R32 cleanroom PASS
```

Future Lesen candidate producers **must call an equivalent or the exact version-pinned gate before technical acceptance** and preserve a readback-proof QA receipt. If such integration is not present, the producer remains `PREVENTION_GATE_NOT_WIRED`; merely linking this document does not prove enforced integration. The current read-only tool covers exact anchors, task quotes, section offsets and known false labels. It does not replace independent human/linguistic Stage4, exhaustive native nine-lens grammar extraction, real Chrome/IndexedDB Stage6, or Stage7.

## Lineage and safety

R32 Library ZIP SHA256 `4ac8410d866c385e09d15006659248f006adf8d24334328f9a53c8d3f31846fc`; stable Library ID `libfile_471aabe9561c8191b3ae7362c062ca4f`. Parent R30 and failed R31 independent audit remain immutable recovery and evidence authorities; original curated v1.3.0 CURRENT unchanged.
