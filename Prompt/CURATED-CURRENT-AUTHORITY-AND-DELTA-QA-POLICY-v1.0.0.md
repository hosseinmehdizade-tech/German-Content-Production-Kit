# Curated Current Authority & Delta-Based QA Policy v1.0.0

**Status:** ACTIVE USER DIRECTIVE — 2026-11-06; prospective work on all existing and future content workstreams.
**Owner:** German Flashcards — Continuous Optimization Program / Project Control Center.
**Mission:** Build the best reviewed learning material, not a literal reprint of an old textbook or CSV. The original source is immutable **historical evidence**, not a veto over months of accepted editorial improvements.

## 1. Resolve two different roles; do not confuse them

- **ORIGINAL_SOURCE (read-only provenance):** the user's initial PDF/CSV/TSV/RAR/audio, source-quoted example and original lexical inventory. Keep immutable IDs, locators and raw hashes for history, licensing, attribution and recovery. Do not silently overwrite it.
- **CURATED_CURRENT (the working authority):** the **latest independently identified, readable, exact-hash-verified, user-approved or validated** project-local final/current TSV/CSV/JSON (including a reconstructible active current bundle with vetted deltas) named in the owner project Library directory and its `LATEST.json`/`CHECKPOINT.json` or a newer explicit user-supplied artifact. Validated acceptance includes editorial additions, deletions, rearrangements, translations and sense/usage improvements; **these are intentional changes, not source-fidelity defects**.
- **NEXT_CURATED (editable successor):** an authorized new revision of CURATED_CURRENT. Preserve the baseline, IDs/SRS and accepted decisions; write a compact changed-ID delta and review evidence. Historical `LOCKED`/FINAL stays immutable, new approved changes become a separately named successor.
- Resolve the current role using `WORKSTREAM-RESUME-CURRENTNESS-POLICY.json`: explicitly user-designated newer verified artifact > newest verified portable owner artifact > exact workstream `LATEST` plus hash-bound receipt > nonconflicting `CHECKPOINT` > root summary. *Newest filename/date alone is not authority*. If an indicated final TSV/CSV cannot be found or verified, `HOLD_AUTHORITY_UNRESOLVED`; **do not silently retreat to the old textbook or regenerate 3 months of work**. Use the original only when this is genuinely a **NEW_SOURCE_INTAKE** without an accepted curated successor, or for bounded repair/reconstruction.
- Keep Menschen A1/A2/B1, Aspekte B1+/B2/C1, independent Verben, NVV, other lexical streams, and app/user data separate. A cross-project duplicate comparison must use each other project's **verified accepted current/final** dataset, not obsolete original vocabulary snapshots.

## 2. Source fidelity: narrow its meaning

A source comparison is **permitted** only when there is a concrete purpose:
1. **Exact attribution:** a field explicitly labeled `SOURCE_EXACT` / quoted verbatim from a book must be checked against that book; if edited, relabel it `CURATED_EDITORIAL`, do not force it back to book wording.
2. **Unresolved material identity or contradiction:** specific high-risk `HOLD` on sense, spelling, provenance, examples, missing audio/ID or suspected accidental corruption; review **only affected records/dependencies**.
3. **New source ingestion** (before a vetted current dataset exists), user-requested literal transcription or approved recovery of broken/missing current evidence.
4. **Critical data migration/lineage disputes:** ensure stable IDs, current content and accepted membership are not accidentally lost, rather than requiring every original row back.

**Forbidden default behavior:** reimporting old source inventories; requiring every final word to exist in the book; restoring user-deleted words simply because the original contained them; deleting new user-curated words because they are absent from the source; rerunning full word-by-word original-versus-current comparison at every lesson/final/release; describing an intentional accepted addition/removal as failure; discarding 3-month edits to satisfy a literal equality test. A report's "missing from source" is not automatically an issue in mature curated output. Reopening a previously accepted decision requires a **new concrete defect or explicit user request**.

The separate language-evidence rule still matters: morphology, German grammatical correctness, idiomaticity, DE/FA(/EN) sense agreement, useful combinations and relations must be defensible using current linguistic evidence. **"Source-first" for enrichment means consult available reliable evidence and owner-accepted content; it does not mean copy the publisher's old inventory as the compulsory final card list.** Do not fabricate dictionary references, form data or QA outcomes.

## 3. Fast safe review: current -> delta -> affected dependencies

1. Read exact current owner artifact and its last accepted decision/QA receipts; verify hashes, stable IDs, lesson ownership, path and recoverability. Avoid blindly treating old sources or stale root summaries as current.
2. Compare against the **immediate last accepted curated revision**, not the initial book. Classify `ADDED`, `REMOVED`, `MODIFIED`, `UNCHANGED`, `CONFLICT/HOLD` by stable card ID and editorial scope. No need to produce full intermediate ZIPs just to record comparisons. If there is no accepted predecessor, treat the first verified curated baseline as a baseline **without retroactive demand for all historical edits**.
3. Review **changed records and affected dependencies** (same-sense links, translations, examples, duplicate clusters, morphology, relation targets, section presentation, lesson memberships). Expand to the whole affected family if a systemic error is demonstrated. Reuse previous valid Stage4 decisions; do not redo independently accepted work simply for a new date.
4. For **new** NEXT_CURATED deletions/merges, require recorded user decision or verified semantic/technical justification; reject accidental silent disappearance, lost IDs, lost translation fields, SRS mapping or cross-workstream leakage. Previously accepted historical additions/removals in the verified current baseline remain accepted; lack of a three-month-old per-item ledger is not an invitation to re-audit the book.
5. Run a **full current-state structural and consistency gate** at Stage5/7 where required: parse TSV/JSON, IDs unique, no accidental loss in current->next transition, sections/formats valid, correct noun/verb/adjective front and conditional back, language completeness and references/graph intact. This is **not** a full original-source equality audit. Run real app runtime Stage6 when required; a static content QA cannot fake Stage6.
6. Persist a compact receipt: `owner`, `current_sha256`, `next_sha256` when applicable, `baseline_authority`, counts by delta type, approved decisions and affected QA scope, remaining HOLDs, original source locator if relevant. At meaningful milestones use a single current working artifact + light receipt, not repetitive full ZIPs.

## 4. Stage 1–7 precedence / compatibility

This prospective overlay **changes the meaning of source authority for already curated work**; it does not waive active Stage gates or rewrite the version-pinned `Prompt/SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`:
- **Stage 1 (Source):** new source: inventory its original faithfully. Mature curated resume: validate CURATED_CURRENT and inherit existing verified Stage1/source provenance; **do not re-inventory the textbook** without a concrete new source or corruption incident.
- **Stage 2 (Canonical):** use accepted current lexical/sense IDs; review only new/modified units, duplicates and dependencies. Do not resurrect removed source words.
- **Stage 3 (Enrichment):** enrich curated content, retain source labels accurately, honor source-first linguistic evidence and no forced quotas; no demand that newly added cards occur in the original.
- **Stage 4 (Linguistic QA):** preserve accepted prior coverage, review deltas and unresolved/high-risk areas with independent methods per active policy. An incomplete historical Stage4 remains incomplete for genuinely unreviewed scope; do not declare PASS merely from a delta test.
- **Stage 5 (Delivery):** project exact approved curated cards (including additions/removals), verify format/full CURRENT state, no dropping fields or silent reversion to old source count.
- **Stage 6 (Runtime):** verify correct app import/display/IDs and persistence only at required boundaries, not every punctuation edit.
- **Stage 7 (Release):** verify final curated TSV/JSON, complete package/hash, recoverability, status and tested runtime. Historical raw files may remain for provenance; **matching old book rows is not a final acceptance criterion**.

**Precedence:** user-selected validated CURRENT + exact project-specific accepted successor decisions > stale original lexical inventory for learner-facing selection. Explicit `SOURCE_EXACT` provenance truth, source immutability, original copyrights, stable identity/FSRS/SRS, independent language QA, conflict/hold safety, and source-specific formal release requirements remain protected. If an already-active pipeline validator insists on full raw-row equality for a mature curated successor, mark `POLICY_CONFLICT_HOLD`, identify the concrete gate and propose a bounded native adapter correction; **never bypass a failing tool, counterfeit a PASS, or mutate a historical immutable file to make a gate green**.

## 5. Automatic routing without manual reminders

Every new/resumed eligible content workstream must resolve this contract from `Prompt/ACTIVE-PROMPT.txt` -> `Prompt/START-PROMPT-v3.3.6.md` -> `Prompt/GLOBAL-POLICY-SYNCHRONIZATION-v1.0.0.md` -> `Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json` -> owner-local verified current/final. Do not ask the user to remind you to use final TSVs instead of discarded source files. Newly created workspaces inherit this same rule. Keep source-specific acceptance evidence; central routing alone does **not** prove each producer adapter has adopted delta-based QA.

This policy is an **execution-time rule, not background automation**. It does not retroactively edit all existing cards, erase original sources, delete files, alter app UI/SRS or grant Stage4–7 PASS. Record a genuine implementation status for each applicable workstream when actual native runs are verified.
