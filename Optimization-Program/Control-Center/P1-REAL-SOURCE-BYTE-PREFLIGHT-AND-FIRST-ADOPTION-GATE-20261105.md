# GFP-OPT P1 — Real Library bytes verified; new governed producer adoption still blocked

**Date:** 2026-11-05  
**Scope:** Read-only user-Library materialization of two existing official Stage 5 artifacts, validated against actual code and source-owner Git pins. No new output publication or Stage acceptance.

## Evidence — independently executed on the real archives

Detailed immutable source/role SHA-256 ledger: [P1 real Library byte preflight](../Verification/P1-REAL-LIBRARY-BYTE-READONLY-PREFLIGHT-20261105.json).

| Source owner | Provider-backed Library raw ZIP SHA-256 | Real TSV rows | Live native neutral validator | Negative controls |
| --- | --- | ---: | --- | --- |
| 250 Verben Lexical Enrichment R8 | `63ae8f2a3a8d2ec5dff94798db3ed060a0b4e43b1cc2699e540beb1393882e5c` | 292 | PASS, 0 format errors | Changed card_type and malformed details rejected |
| Nomen-Verb-Verbindungen B01 native Stage 5 | `fc7fb3cb005372c3254ae475d9c3637dc9f7ce439813c52ce7e74b009d800cbd` | 2,492 | PASS, 0 format errors | Changed card_type and malformed details rejected |

For each independently materialized archive: outer SHA-256 matches the Git source-owner record, archive CRC is valid, four named role members match their embedded SHA256SUMS (8/8). **Actual validator Git blob `b6d27c0b98f44cd8b0ffad325710f24f76da95e1`** was extracted from the pinned, source-owned, byte-authenticated R8 package; code was then executed independently on both actual complete direct-import TSVs. Positive first-card probes passed. Four intentionally malformed, in-memory copies were rejected. Neither original ZIP changed.

This proves **existing real artifact integrity and neutral format**, NOT newly invoking `Tools/build_governed_clean_delivery_v1.py`, not Stage4 semantics, and not source-currentness for all workstreams. CI does not inherit private Library raw bytes simply because this tool invocation succeeded.

## Source-specific adoption decision

**250 Verben:** R8 source owner records an official 292-card Stage4 and Stage5, and the exact historical `LATEST.json` Git blob `074c4eef64fec30ab9f7b63ae227fbede8ba8e65` points to the archived bytes. But R8 is already packaged, so re-wrapping or copying it would create a duplicate without a **new source-owned governed invocation**. Candidate for a *future* newly approved Stage5 boundary, not for retroactive ADOPTED.

**NVV:** real 2,492-card Stage5 transport passes format tests, but the source owner's Stage4 approval is limited to the **first 100 B01 cards** (87 accepted enrichments); the remaining 2,392 cannot be marked newly Stage4-approved. Its official native build record `c52200ee4b4455d3bec42c59d2410b55e4671593` explicitly records governed wrapper `NOT_EXECUTED`. **Never** claim 2,492-row semantic approval or infer new P1 producer ADOPTED.

**Grammar:** separate branch checkpoint historical navigation only; not part of this lexical native pilot.

## Required next safe execution

1. Select one *new* source-owner-approved Stage5 publication boundary. Verify that the accepted source is newer than all known Library/Git candidates, and keep source/LOCKED immutability.
2. Use its original four separately named input files and the exact pinned active `stage5_neutral_validator` and `stage5_clean_builder` through `Tools/build_governed_clean_delivery_v1.py` (not a past ZIP). Produce a unique write-once governed receipt with before/after role hashes and no import/UI operation.
3. Independently replay the new ZIP and receipt, then verify exact NEW GitHub-main LATEST and the actual provider-backed Library archive bytes. Require source-owner Stage QA; record a reviewed new adoption ledger version.
4. Only after those proofs can that one source-specific producer be marked `ADOPTED`. The existing version-1 ledger must remain **0** until then. OP01 trusted writer activation and OP05 duplicate cleanup stay separately held.

**Non-claims:** No new ZIP created, no real governed producer invoked, no PDF originals rehashed to establish latest source, no Stage4–7 approval re-issued, no app/FSRS/IndexedDB/UI mutations, no Library deletion, no library upload.

**Outcome:** `PASS_REAL_SOURCE_LIBRARY_BYTES_AND_NEGATIVE_CONTROLS__PRODUCTION_ADOPTION_HOLD`.
