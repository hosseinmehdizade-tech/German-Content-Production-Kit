# OP-01/OP-02 — related category taxonomy v1.1.0 optimization milestone

**2026-11-04. Scope: production rules and read-only QA only.** User explicitly prohibited mission drift to card production. Prior A1 V25/V25-R1 content ZIPs were unrelated to this optimization mission and are not optimization deliverables.

## Changes
- New active `Prompt/RELATED-SECTIONS-TAXONOMY-POLICY-v1.1.0.md`: role precedence with sense/evidence, strict Unicode NFC/whitespace identity (no ß/case/punctuation coercion), genuine `RELATED` semantics, explicit HOLD, verified target ID only, no raw ID display, no duplicate learner tiles without teaching delta.
- Reusable source-neutral diagnostic `Verification/audit_related_sections_taxonomy_v1_1.py`, TSV and normalized JSON inputs, SHA-bound report and optional opt-in HIGH-only exit. No writer and no Stage4 automatic approval.
- Synthetic regression suite `Verification/tests/test_audit_related_sections_taxonomy_v1_1.py` spanning A1/A2/B1/Verben/NVV/Vocabulary input shapes; structural and linguistic negative controls; no card editing.
- Active prompt and global lexical policy pointer updated; historical v1.0 retained intact. This is a safe source-policy update, not a full producer adapter rollout or app UI change.

## Local QA evidence and limits
- 46/46 source-neutral synthetic unit tests PASS, including 6 corpus-name profiles, negative controls for semantic near matches, sentence-like text, opaque IDs, typed graph conflict, bilingual parsing, malformed TSV/JSON, nonmutation and CLI return codes.
- Real **read-only** fixture: source-derived Menschen A1 V25-R1 TSV (2997 cards) from Library-authenticated archive ZIP SHA256 `46d741a88e596f9c9b2bccc6a89fb2a3f42389ff6a3b091b313a2a61eac46e42`; extracted TSV unchanged and scanned in local sandbox. 973 related items; 1 HIGH exact duplicate surface in related+combination (`ma1m-lu-0913`, `internationaler Flughafen`) and 31 MEDIUM sentence-like flags. These are **advisory signals**, not a linguistic verdict, not edits, not baseline corrections. No data mutations, no Stage4 PASS.
- Exact source currentness, independent human linguistics, actual app CURRENT/Stage6, full all-adapter consumer parity and GitHub CI across OS are **not verified** by this local diagnostic. Source adapter-specific mapping beyond canonical target schema needs per-workstream integration proof.

## Rollout contract
1. Producers read the v1.1 policy during existing one-pass lexical authoring; use `VERIFIED_PRESENT`, documented `CLOSED_NO_FORCE`, `NOT_APPLICABLE` or `HOLD` rather than forcing a relation.
2. Run read-only diagnostic on exact current eligible editable projection; inspect itemwise HIGH and semantic MEDIUM risks. No mass retroactive LOCKED rewrite.
3. Independently run the active Stage4 risk-based acceptance separately and keep Stage5/6/7 unchanged.
4. Before any CI gate, independently verify real adapter schema, registered source, no false positives and release-compatible report; then opt in per workstream. UI placement unchanged.

## No-go
No new content package, no A1/A2/B1 learning-card writes, no existing content LATEST/LOCKED/SRS/runtime mutation, no blanket category retyping and no final quality promotion.