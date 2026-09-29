# CHANGELOG v3.3.6

- Added universal source-adapter boundary for PDF/image/text/CSV/TSV/Memrise/archive/audio/DOCX/XLSX/web and future readable sources.
- Added mandatory Stage 2B Identity Closure.
- Split Stage 3 into 3A full richness baseline, 3B gap-driven evidence enrichment and 3C 100% disposition closure.
- Added explicit final/non-final dimension states and first-class `CLOSED_NO_FORCE`.
- Added durable candidate ledger and bounded evidence-search stopping rules.
- Added dependency-scoped invalidation to avoid repeated full regeneration.
- Added independent Stage 4 completeness re-audit and all-zero-dimension exception guard.
- Added source-occurrence, identity-closure, candidate-ledger and enrichment-completeness validators in the portable authority.
- Added v3.3.6 clean-delivery builder with completeness anti-bypass.
- Carried forward v3.3.5 neutral `de-vocabulary` / `gfp-vocabulary-neutral@1` presentation unchanged.
- Historical locked artifacts are not rewritten.
