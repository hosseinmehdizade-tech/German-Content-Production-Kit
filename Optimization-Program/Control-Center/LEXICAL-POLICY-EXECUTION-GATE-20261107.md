# Lexical release policy execution — one gate, no extra editorial rounds

**Status:** new prospective Stage5 candidate route, not automatic migration and not an app release.

**Root cause (2026-11-07):** the active source-first combination policy was already written and source-neutral scanners existed, but scanners were advisory and the governed delivery wrapper certified *format and exact bytes*, not didactic non-copy value. A previously approved Stage4 receipt for an older TSV cannot certify a changed successor. Passing ZIP/JSON/TSV or saving a Git checkpoint was mistakenly treated as broader quality coverage.

## Required new lexical candidate route

Run once after normal Stage3 editing and normal independent Stage4. Do **not** add another editorial phase or inspect historical LOCKED cards by default.

1. Resolve the current owner-authoritative edited TSV and verified parent SHA. For mature series it is the curated CURRENT, not a fresh textbook reimport.
2. Run [the cross-project coverage gate](../../Verification/guard_lexical_rule_coverage_v1.py) against **the exact intended direct-import TSV**. It verifies all active global-policy file pins, invokes neutral/MEM009/relations/taxonomy/didactic scanners and compares *every* Kombinationen/Kollokationen item with examples from **its own card**, including inflected/reshuffled matches. Scanner flags are review prompts, never automatic removals.
### Right-side cross-section assurance (2026-11-08; prospective)

The same exact-TSV preflight now treats HIGH related-section taxonomy findings as review obligations alongside Kombinationen/Kollokationen ↔ Beispiele overlap. These include an opaque internal target ID displayed as German, duplicate content across Verwandte Wörter and Synonyme/Antonyme/Wortfamilie/Kombinationen/Beispiele/Rektion, conflicting existing typed roles, invisible formatting controls and repeated related entries. No automatic semantic moves or deletion. The existing \`flagged_card_ids\` in the SAME cross-tile Stage4 review must cover affected card IDs from **both** scanners; a reviewer may preserve an exact cross-section duplicate only with a specifically justified distinct teaching purpose. Opaque IDs, invisible control characters, repeated within-related items and conflicting pretyped roles require source correction and cannot be waived as useful pedagogical variety.

A high finding still present in the exact candidate TSV may NOT be marked \`CORRECTED_IN_EXACT_SOURCE\`; correction must remove the same fingerprint from a new exact-source scan. Unknown/stale or duplicate HIGH decision IDs are rejected. The unchanged single review and existing Stage4 still govern; no extra manual QA round, no arbitrary collocation quota, no historical card rewrite. This is a prospective executable content gate for routes that actually call the quality-gated Stage5 launcher, NOT proof that every native producer has already adopted it or that native app Stage6/FINAL passed.

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

## Canonical family Stage5 integration (2026-11-08)

The official candidate launcher now **requires** `--family-id family:<registered-name>` (for example `family:menschen-a1-verben`). The exact same-card review must identify the canonical Git owner and contain the currently attested parent SHA from `CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json`. Missing owner, wrong family, wrong accepted parent, absent content QA or Stage4 evidence blocks **before ZIP**. The router lists 21 families but does **not** invent current authority for families whose source is still unaudited; Aspekte B1+, B2, C1 therefore intentionally HOLD until their native owner currentness is attested. The canonical route must be refreshed with independently verified current evidence if an approved newer source supersedes its snapshot; do not restore old source.

`Tools/build_quality_gated_front_stage5_v1.py` now performs existing source-attested front morphology validation, then passes **Stage5 acceptance** through that same quality- and owner-gated launcher rather than directly through the historical format-only builder. Invoke with all five new evidence arguments: `--family-id`, `--stage4-receipt`, `--cross-tile-review`, `--receipt`, `--policy-report`. Distinct recovery / explicitly requested archival copies retain original non-semantic packaging. `final_delivery` and `validated_major_checkpoint` from this front wrapper are not a substitute for independent release approval and are blocked here.

**Scope and honesty:** this closes a concrete bypass in the native front/transport adapter and makes the shared canonical-family candidate route enforce source ownership. It does not automatically convert every historical direct caller of `build_clean_delivery.py` into a content-approved producer; that pinned builder remains independently callable for **format-only, replay and recovery**. A producer that has not been actively migrated/tested is **NOT ADOPTED** even when it exists in the routing table. Future Stage5 content acceptance must explicitly use the strict launcher and its actual proof; native app Stage6 and Stage7 remain separate.
