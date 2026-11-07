# Lexical release policy execution — one gate, no extra editorial rounds

**Status:** new prospective Stage5 candidate route, not automatic migration and not an app release.

**Root cause (2026-11-07):** the active source-first combination policy was already written and source-neutral scanners existed, but scanners were advisory and the governed delivery wrapper certified *format and exact bytes*, not didactic non-copy value. A previously approved Stage4 receipt for an older TSV cannot certify a changed successor. Passing ZIP/JSON/TSV or saving a Git checkpoint was mistakenly treated as broader quality coverage.

## Required new lexical candidate route

Run once after normal Stage3 editing and normal independent Stage4. Do **not** add another editorial phase or inspect historical LOCKED cards by default.

1. Resolve the current owner-authoritative edited TSV and verified parent SHA. For mature series it is the curated CURRENT, not a fresh textbook reimport.
2. Run [the cross-project coverage gate](../../Verification/guard_lexical_rule_coverage_v1.py) against **the exact intended direct-import TSV**. It verifies all active global-policy file pins, invokes neutral/MEM009/relations/taxonomy/didactic scanners and compares *every* Kombinationen/Kollokationen item with examples from **its own card**, including inflected/reshuffled matches. Scanner flags are review prompts, never automatic removals.
3. Attach the existing **independent official Stage4 receipt** for that exact TSV and one compact exact-hash-bound cross-tile review record. Its scope must list all flagged card IDs; only HIGH needs individually reasoned KEEP-with-independent-teaching-value or actual pre-scanned correction; lower risks are handled by the existing independent risk-based review, not new essays or quotas.
4. Only after the gate returns PASS, use the **single candidate publisher** [build_quality_gated_lexical_candidate_v1.py](../../Tools/build_quality_gated_lexical_candidate_v1.py), which runs the unchanged governed format/byte builder after this content gate and writes a separate quality receipt. Missing source, review, policy pin, wrong hash, unresolved HIGH, invalid grammar/typed structure, or failed Stage4 -> stop **before packaging**. A format-only builder/ZIP MUST NEVER be named linguistic/content-accepted or FINAL.

Example:

```bash
python Tools/build_quality_gated_lexical_candidate_v1.py \
  /path/to/approved-four-role-source \
  /path/to/new/LEXICAL-STAGE5-CANDIDATE.zip \
  --receipt /path/to/new/GOVERNED-STAGE5.json \
  --policy-report /path/to/new/LEXICAL-RULE-COVERAGE.json \
  --stage4-receipt /path/to/exact-current-official-stage4.json \
  --cross-tile-review /path/to/exact-current-review.json
```

Cross-tile review JSON shape (producer fills only actual verified facts):
```json
{
 "schema":"gcpk-lexical-cross-tile-acceptance@1.0.0",
 "workstream":"actual-owner-workstream",
 "source_tsv_sha256":"exact-working-TSV-sha256",
 "curated_current_parent_sha256":"64-char-verified-parent-sha256",
 "stage4_receipt_sha256":"official-current-stage4-json-sha256",
 "flagged_card_ids":["all-actual-ids-affected-by-the-automated-scan"],
 "risk_based_independent_review":true,
 "high_decisions":[{"id":"exact-scanner-fingerprint","decision":"KEEP_WITH_SPECIFIC_TEACHING_DELTA","reason":"distinct useful pattern"}]
}
```

The exact current owner decides whether to keep a valid basic combination or replace a low-value example clone. **No mandatory relation count** and **no blanket auto-delete**. An independent reviewer must verify natural German and faithful Persian; code cannot do this alone.

### Evidence and limits

Initial real **read-only** specimen: Menschen A1 Verben R16, 310 cards, 1,240 examples and 2,702 combinations including Kollokationen. The detector found **792 review signals**, including the five photographed `versteigern` examples. Those are not 792 certified errors. The current R16 has no independently accepted Stage4 exact-source receipt for these modifications and remains NONIMPORT.

The central registry contains **22** bindings; exact byte-pin coverage is *not* proof that all 22 rules have been semantically implemented in every existing producer. This launcher is a new fail-closed prospective path. Adapters not yet routed through it cannot claim global adopted/release-ready; legacy direct `build_clean_delivery.py` and `build_governed_clean_delivery_v1.py` remain FORMAT-ONLY for historical/recovery/testing use and are **not** valid proof of lexical quality acceptance. Native Stage6/import/IndexedDB and Stage7 remain separate. Source/LOCKED/SRS/FSRS untouched.

**Next integration obligation:** every independently operated Menschen/Aspekte/Verben/NVV/vocabulary Stage5 producer must use this entrypoint for future accepted lexical outputs; prior releases are preserved until an explicitly authorized successor.
