# OP-02 WIP50 — real mixed-unit Canonical/lexical TSV identity audit

**Date:** 2026-10-29. **Status:** READ-ONLY SOURCE/IMPORT IDENTITY AUDIT, not language QA or CURRENT issuer authorization. No content producer scope granted.

## Actual source bytes (local read-only inspection, not synthetic)

The newest explicit WIP50 local snapshot was inspected **without editing** either original materialized artifact:

| Authority | Actual SHA-256 / source | Observed |
| --- | --- | --- |
| `Aber-Hallo-WIP50-CANONICAL-MASTER.json` | `fe50217d519edbb1c4d5eb5fc4da36faf1f562e859ccfe58b0153dbf684c48aa` | 7,076,256 bytes; JSON `learning_units` length **788** |
| `Aber-Hallo-WIP50-IMPORT.tsv` | `d640179d3fdfa2ecff0681b707519bc6d10ff687aba22482a7e8694aba374a8a` | 12,951,743 bytes; **787** data rows; **23** columns each |

These are the **exact current WIP50 master** hashes in `Workspaces/aber-hallo-listen-tabellen/LATEST.json → wip50_master_files`, source Git blob `f490ba8debb7277f07e1e0accce94364229fb2e9`. Note that `LATEST.json → authority.canonical` retains the earlier SHA `3abbd498...` and is **not** the new WIP50 master. Do not silently select the older path; use explicit WIP50 master role and latest WIP50 receipt.

Full Canonical type histogram, directly computed: `verb=647`, `adjektiv=140`, `grammatische_struktur=1`. The 787 lexical unit IDs, **in their exact canonical order**, equal all 787 TSV card IDs in their exact import order, with no duplicates. TSV `card_type=de-vocabulary` all 787; `category=Verb` exactly 647, `Adjektiv` exactly 140. The nonlexical unit `ahl-lu-0001` `Deklination: Artikel, Negation und Personalpronomen` remains in canonical but does not appear in lexical import. Its **full canonical JSON object digest** (sorted-key compact UTF-8) is `e48b2d97c5f5a191ad1d5bc78c1364252e45355f4462832a8eded51f7948395c`. Thus **788 Canonical vs 787 import is an explicit valid projection scope**, not evidence of a missing vocabulary card.

## Practical OP-01/OP-02 gap resolved as a nonactive diagnostic

The proposed `Verification/verify_stage34_materialized_output.py` from PR36 expects its Stage3 `lexical_cards_total`, Stage4 `deterministic_scanned_units` and full materialized `learning_units` length to agree. **Applying it as-is to mixed WIP50 would falsely require 788 lexical cards**, or require incorrectly dropping one legitimate grammar unit from the Canonical. That original adapter remains explicitly lexical-only and must not be invoked as full mixed-workstream approval.

New separate, reusable **WIP50-layout-specific** `Verification/audit_wip50_mixed_canonical_import_scope.py` is a read-only boundary: given both raw files and their exact externally supplied SHA pins, validates 23-column TSV schema, unique IDs and types, requires 1 explicit grammar-unit exclusion, checks all verb and adjective IDs and order against TSV, category/card type exactness, and surfaces the excluded grammar unit's independently recomputed digest. Fails closed if lexical units are omitted, unknown/grammar units are imported, order changes, category is switched or duplicate IDs appear.

**Every positive result is scoped** `PASS_SCOPED_MIXED_ID_AND_BYTE_PARITY_ONLY`; negative/unknown is `BLOCKED_INVALID_MIXED_SCOPE`. Output explicitly keeps `stage4_semantic_pass=false`, `source_fidelity_verified=false`, `issuer_authenticated=false`, `production_authorized=false`, `performed_writes=false`.

## Explicit limits

- A caller supplying both raw files and expected SHA may self-select matching values; **independent CURRENT issuer trust, cryptographic signature and user approval remain unresolved**. GitHub `main` remains unprotected.
- This audit verifies **identity/scope/order and file hashes**, NOT accurate German/Persian/English meanings, example alignments, source-PDF semantic fidelity or rendering equivalence of every import field.
- No actual independent 788-unit Stage4 review has been executed. The old WIP50 unsigned reviewer worksheet still has 604 stale unit snapshots and zero decisions. Stage5–7 remain not authorized.
- This diagnostic is specifically for *this exact WIP50* mixed type set and header format; it intentionally does not automatically generalize to unknown grammar/Lesen/Schreiben types.
- **No learner cards, PDFs, LOCKED, runtime/UI, Library, workstream LATEST or writer scopes were modified**. All code/tests and this report are NONACTIVE optimization-only.

## Next

Use trusted, workstream-specific **current** authority when eventually authorized for real semantic review; keep 788 total Canonical and 787 lexical-import records distinct. Do not change import or Canonical to force equal counts. Update Stage3/4 callers to choose lexical-only vs mixed scopes explicitly; never infer it from a generic number.
