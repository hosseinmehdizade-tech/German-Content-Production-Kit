# Menschen A1 — finite Stage 4 closeout contract (2026-10-30)

**Status:** ACTIVE WORKSTREAM EXECUTION PLAN — not a Stage 4 PASS; not a new content release.  
**Exact content baseline:** C46N editable TSV SHA-256 `4643d959c03e43ea49d5bfdea2b159d37c7e00419c48913bd920df908a8808cb`.  
**Latest QA scanner:** corrected C46M dual example-schema overlay, rescan on C46N = 889 heuristic flag occurrences (not 889 errors).  
**Approved rules:** `LINGUISTIC-QA-AUTHORITY-POLICY.json`, `Prompt/KOMBINATIONEN-DIDACTIC-MEHRWERT-GATE-v1.0.0.md`, `EDIT-APPLY-VERIFICATION-CONTRACT.json`, `EXECUTION-OUTCOME-EFFICIENCY-POLICY.json`.

## Why the previous cycle was non-terminating

The first-pass 2,997-card / 11,988 trilingual example-set work, scoped second-pass combination checks, scanner flags, source-protection decisions and formal Stage 4 acceptance were conflated. Every child TSV hash changed the scanner input, so previous reviewed expressions appeared as "unreviewed" again. The earlier scanner also missed legacy `text_de` examples, and incorrect delimiter splitting generated a false positive. Zero raw heuristic flags is **not** a valid acceptance criterion.

## One finite review universe — no more full restarts

1. **Freeze the exact C46N snapshot as review baseline.** Preserve original source, all LOCKED releases, C48 parallel identity-repair branch, UI and SRS. Approved repairs are recorded as exact deltas with before/after hashes; they do not void unrelated accepted reviews.
2. **Build ONE cumulative acceptance ledger**, keyed by stable card ID + normalized German combination + relevant semantic/sense/source signature + referenced example signature + active rule version. Include both review target and evidence; deduplicate multiple scanner rules for the same item. Each row must have a disposition (`KEEP_WITH_REASON`, `CORRECT_APPLIED`, `CLOSED_NO_FORCE`, or `HOLD_WITH_SPECIFIC_EVIDENCE`), reviewer pass, source provenance, teaching_delta where displayed, changed-row dependency, and cited material. No blanket source-protected = didactic PASS.
3. **Import and validate prior decisions** from C44W–C46N only where their relevant card/item semantic fingerprint is unchanged. Do not re-review unaffected items solely because the TSV-wide SHA changed. Track any evidence conflicts as explicit finite cases.
4. **Review gaps, not 11,988 examples from scratch.** Verify that all 2,997 cards / 11,988 DE–FA–EN sets have documented first-pass evidence. Run a separately documented **adversarial second pass** on systemic error families, high-risk source/sense/translation/valency mismatches, changed dependencies, and source identity issues, with seeded negative controls. The current linguistic policy does not require a blind repeated full-corpus reading for each new ZIP.
5. **Resolve blocking holds**: exact present C46N eight new source/register holds, inherited holds including source-form cases and the historical source/visible projections, current HIGH alerts, and the separate C48 source-identity repairs where relevant. Recompute current unique unresolved cases from the ledger — do not add historic queue sizes or call every scanner warning open work.
6. **Pass Stage 4 exactly once** only when the canonical ledger covers the declared review universe, all critical source/HIGH holds are resolved, independent adversarial review and deterministic source/ID/translation/projection/negative-control tests pass, and any allowed bounded noncritical holds are explicitly disclosed. Otherwise report exact unique unresolved cases with IDs and evidence, not generic "full independent review pending".
7. **Then** carry out Stage 5 content delivery, Stage 6 import/presentation check against exact CURRENT app runtime (no UI changes without approval), and Stage 7 single organized release ZIP, with independent hash and round-trip verification.

## Reporting discipline

No further C46-series micro-successor ZIP merely to increment an audit count. Provide a **single cumulative acceptance ledger and closure dashboard**: reviewed/accepted/applied/held unique targets, first-pass example evidence, adversarial second-pass evidence, critical blockers by exact ID, status of Stage 4/5/6/7. Every continued session resumes that same ledger. Raw scanner alerts remain advisory and can legitimately be nonzero after PASS.

**Current truthful state:** C46N technical integrity verified; first-pass scope reported complete; formal consolidated second-pass/Stage 4 acceptance not yet demonstrated; Stage 5/6/7 NOT RUN; import_allowed = false. This contract changes the workflow, **not** the user data, import authorization or release status.
