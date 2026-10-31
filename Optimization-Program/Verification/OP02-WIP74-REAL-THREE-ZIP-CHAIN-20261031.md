# OP-02 — Actual original compact three-hop lineage WIP74 → WIP73 → WIP72

**Date:** 2026-10-31. **Authority:** nonactive read-only QA of recovery/working bytes, **not final production approval**. No learner edits, source uploads, original ZIP mutation, workstream LATEST change, issuer activation, writer grant, or app/UI/runtime change.

## Independently obtained byte evidence

The GitHub current `Workspaces/aber-hallo-listen-tabellen/LATEST.json`, blob `94a86f1b7abd2cbc40b36a6438db0d59cbfa7e75`, states `WIP74_FIVE_REKTION_AND_TWO_TRANSLATION_CARDS_APPLIED`, 940/981 externally attested valency patterns and 41 holds, full Stage4 OPEN, Stage5/6/7 NOT_RUN.

Original raw Library artifacts were fetched by file ID, materialized into the isolated read-only analysis area, and actually opened and hashed:

| Original | Exact SHA-256 | Byte size | Members / ZIP CRC |
| --- | --- | ---: | --- |
| WIP74 compact, `libfile_01c73f40bb88819186e7b5a0f4b95adf` | `a8bfac20faf53caaf702f2bac97d353660285faa448ede5d1bafaa6e7689143f` | 1,891,353 | 14 / PASS |
| WIP73 compact, `libfile_cbe0500bf2f4819198fa26e30a15b2f1` | `6b0f29e98e3648b3f0a29921fbc9e7a73322ad83ea009fca16becb74774899a7` | 1,892,783 | 13 / PASS |
| WIP72 full source parent, `libfile_2ca6d2f2be508191971b80761222f18d` | `b41b2a814eed37d87f01f90937ab21ee2976e9f059007c2f091b5d743e4ac225` | 8,056,905 | 484 / PASS |

WIP74 names WIP73's exact outer digest as its *immediate editable parent*, and WIP72's exact digest as the *immutable complete source/history parent*. WIP73 names the identical WIP72 hash as its full parent. WIP74 is not a full standalone delivery and should never be relabeled as such.

Two original source PDF bytes are present in WIP72, **not duplicated** in WIP73/74:
- A1-A2 SHA256 `4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3`;
- B1-C2 SHA256 `ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04`.

The WIP74 archive contains 13/13 matching `SHA256SUMS` records, 12/12 manifest files with exact hash/size/coverage. WIP73 contains 12/12 sums and 11/11 manifest entries. WIP74/WIP73's actual canonical and import digests equal their separately read GitHub checkpoint/current authorities.

**Independent real-data lineage test:** all 788 canonical learning-unit IDs and all 787 lexical import card IDs maintain the same order and exact stable identities across WIP73 and WIP74. Exactly **seven** units and **seven** import TSV rows differ. Within each changed TSV row only zero-based column 19 differs; no unrelated column or unaffected row changes. Exact canonical leaf-path differences classify **five** units as `metadata.rection_qa.patterns[*]`-only and **two** as learner Persian example and Kombinationen translation changes only. That does **not** validate linguistic correctness. The 4-line translation-repair log and 5-line exact-Rektion-evidence log match the declared counts; 41 hold records remain and 3 deterministic risk flags are explicitly **not** Stage4 PASS.

A separately implemented local independent three-original-ZIP read-only audit returned
`PASS_SCOPED_TRIPLE_ZIP_BYTE_LINEAGE_NOT_FINAL`, `errors=[]`, **three original ZIP byte pins matched**, two original PDF bytes matched, seven changed cards/units, five Rektion-only and two translation-only. This verifies the actual byte lineage scoped to the stated inputs. The CI verifier code added in this PR is separately tested on entirely synthetic ZIPs and **must not be represented as a replay on the Library originals**.

## New reusable nonactive fail-closed contract

`Verification/audit_op02_compact_chain_v2.py` requires all **three** raw ZIPs and separately supplied exact outer ZIP, Canonical/TSV and PDF source pins. It validates archive path safety, full CRC, SHA256SUMS and manifest entry coverage/hashes for both compact archives, all immediate/full parent references in checkpoint/source/QA/manifest, actual WIP72 embedded PDF digests, stable TSV IDs/23 columns, 788 canonical IDs, bounded 7-card deltas (5 Rektion-only + 2 translation-only leaf paths), counts/hold continuity, evidence JSONL and explicit Stage4 OPEN / Stage5–7 NOT_RUN declarations. Any inconsistency yields `BLOCKED`.

The schema is deliberately WIP74-specific, not a blanket generic future-WIP release approval. New formats/fields require new review. A clean result is a **scoped recovery-lineage PASS only**; `issuer_authenticated=false`, `stage4_semantic_pass=false`, `stage5_7_authorized=false`, `is_final_release=false` regardless of ZIP success.

PR synthetic negative cases include absent original parent, absent intermediate parent, rehashed parent-reference mismatch, source-manifest drift, spoofed Stage4 PASS, wrong independently supplied SHA, out-of-scope TSV changes and conflicting QA/manifests. No real copyrighted PDF or learner ZIP bytes are uploaded into public GitHub.

## Still-open trust boundary

As previously independently read, Content Kit public `main` lacks branch protection/rulesets, and private Flashcards Pro `main` lacks protection (private rulesets API reported 403 plan restriction). OP01 writer scopes remain `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL` with zero scopes. User-owner approval is required before activating trusted repository enforcement or publisher identity. Main CI remains nonrequired and PR-head defined, never an authenticated issuer. No final Stage4–7 claims.

The WIP74 checkpoint's observed status is **COMPACT_NOT_FINAL**, 940 attested, 41 held. Continue only with producer-authorized future data edits outside this optimization mission and preserve WIP72 full source parent for recovery.
