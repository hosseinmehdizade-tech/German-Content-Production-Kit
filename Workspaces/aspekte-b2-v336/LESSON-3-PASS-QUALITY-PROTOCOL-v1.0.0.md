# Aspekte B2 — Mandatory three-pass lesson execution protocol v1.0.0

**Decision:** user directive, 2026-11-07. **Status:** ACTIVE for all subsequent work on Aspekte B2. **Scope:** all 10 lessons and their ongoing curated work; no retroactive reset of already accepted work.

## The governing rule

Complete each lesson with **at most THREE user-visible execution passes / milestones**. A pass is a substantial, whole-lesson work package, not a single micro-edit or a renamed multi-stage loop. **Do not sacrifice content quality to fit the number three.** Conduct all necessary checks and corrections within the assigned pass; do not publish faulty cards, counterfeit independent QA, skip mandatory gates, or claim a release without real native evidence.

The seven established *technical* Stages 1–7 are **not removed**. The three passes are a batching/orchestration discipline for the existing stages and their real acceptance gates. Reporting must identify which formal technical stages actually passed and which remain blocked.

### PASS 1 — Complete lesson production (Stage 2 + Stage 3 content; inherit verified Stage 1)

- Resolve the latest byte-verified owner-local **CURATED_CURRENT**, not an obsolete textbook or historical original inventory. Resume deltas; preserve accepted edits, IDs, sense inventory, source-lineage and user intent. The older CSV is only initial historical provenance unless narrowly needed to repair a concrete problem.
- Process **100% of lesson rows**, not 12-row or 20-row mini-batches reported as milestone completions. Produce one editable full-lesson draft with all needed meanings, Persian equivalents, examples, appropriate morphology, Rektion, collocations, synonyms/antonyms where verified, and clear typed handling of duplicates, fixed expressions and inflected forms.
- **One verified lexical target = one card with all accepted meanings**; only split for independently justified different lexical identity (e.g. genuinely distinct POS/registered construction). Per-sense examples are helpful but not a compulsory quota; avoid fabricated filler. Example DE/FA alignment and correct semantic attachment matter more than counts.
- Cross-project comparison uses only actual verified accepted/current card data from each other project; no rebuilding discarded originals or presuming app/SRS identity from a candidate content file.
- End Pass 1 with **one complete working lesson artifact** and a compact unresolved-issue queue. If a source item cannot safely become a card, retain an explicit noncard/HOLD record and do not silently delete it.

### PASS 2 — Rigorous, independent QA and correction (Stage 4; revisit affected Stage 2/3 only)

- Inspect **every card**: headword/POS, spelling, noun gender/plural, verb forms/separability/Rektion, accepted meanings, all DE/FA example pairs, natural idiomatic Persian, context-sensitive synonyms/antonyms/collocations, duplicate/sense overlap, missing or lost data, cross-level accepted identities and broken relations.
- Use an **actually independent review method or reviewer** where the active release policy requires independence. One AI model reading and then re-reading its own drafts is **not** certified independent QA. State accurately which checks are mechanical, editorial AI, external lexicographic corroboration or independently signed off.
- Fix defects inside this pass, then rerun structural/full-scope QA plus targeted rechecks on edited fields and dependencies. No repeated R-number reports for tiny edits. Summarize only material fixes, verified checks, residual HOLDs and exact blockers in **one QA receipt**.
- Never fail merely for absent *per-meaning* example; the per-card and independently applicable language/format rules still apply.

### PASS 3 — Delivery, safety gates and exact final disposition (Stages 5, 6 and 7 as applicable)

- Produce one full-lesson native import deliverable **only after the relevant Stage 2–4 gates genuinely pass**; check content projection, schema, stable IDs, no accidental loss from curated CURRENT, DE/FA correctness, links and source-to-unit coverage. Preserve SRS/review histories; no automatic app import or deletion.
- Run actual required native app/runtime persistence, import display and SRS identity checks for Stage 6 when such tooling and authorization exist; structural tests are **not** a substitute. Verify delivery bytes/hash, integrity, recoverability, manifest and final Stage 7 state. Final card count and import permission must reflect evidence.
- One of two truthful dispositions: **RELEASED** (all required gates passed), or **BLOCKED / PARTIAL_ACCEPTED_NONIMPORT** with *only concrete, unresolved high-risk items and missing evidence*, not another chain of extra pseudo-stages. Make a compact actionable queue for future user authorization or new external evidence, then progress to the next lesson without re-auditing the whole finished content.

## Hard efficiency controls

1. **Maximum three reported execution milestones per lesson**, never a hundred `RXX` turns. Existing versions R01–R47 are history, not mandatory work to repeat.
2. **One mutable full-lesson working artifact**, one compact QA receipt, one final deliverable/disposition. Use parent SHA and edited-card-ID delta; preserve historical accepted checkpoints, but no micro-ZIPs or repeated archival snapshots on every correction.
3. **Quality outranks the three-pass target:** if unresolved material risk prevents release, label BLOCKED rather than skipping QA or making a fourth automatic round. Work inside the current pass as needed; a genuine later new fact or explicit user instruction may authorize a separately scoped successor, not a retroactive fake PASS.
4. Do not call work COMPLETE when only AI first/second pass coverage exists. Do not count draft cards as released/importable. A lesson may have full draft coverage and **zero released cards**.
5. Owner-local file lifecycle: write only into Aspekte-B2 Library/GitHub scope, keep versioned current/hash receipts discoverable; no deletions/merges of learner cards or changes to personal SRS without explicit appropriate authorization.
6. Keep reports short and decision-oriented. For every milestone show: `lesson`, `pass 1/2/3`, `rows total/covered`, `draft/approved/importable cards`, `QA evidence`, `open concrete blockers`, `paths/hashes`, `next lesson/action`.
7. The user should **not** need to repeat this instruction. `README.md` and `LATEST.json` must route each resumed session to this policy before executing.

## Immediate resumption (2026-11-07)

- **L01:** current R47 full provisional preview: 160 source ordinals -> 158 draft cards + 2 preserved non-card objects; 17 legacy release HOLDs incl. four identity/link cases. Treat Pass 1 *draft coverage* as completed; Pass 2 independent release QA is **not approved**; Pass 3 **NOT STARTED**. Do not restart or reopen original textbook. Finish genuinely blocking QA within Pass 2 or carry precise BLOCKED status and continue.
- **L02:** current R15 first 12/108 draft units; R14 validated 108-row curated editorial overlay. Pass 1 **INCOMPLETE (96 units remain)**. The next substantial work package must produce the entire remaining 96 in the **same Pass 1**, not another 12-unit milestone. No Stage 4/5/6/7 claims.
- **L03–L05:** already have substantial AI source-unit/editorial coverage, but not complete final card sets or approved language QA. Reuse it as input to their own Pass 1, never force a second initial-source audit.
- **L06–L10:** unstarted; process each lesson using the same three-pass arrangement.
- **Global checkpoint:** R25/L05 remains historical valid portable checkpoint; latest scoped L01 and L02 current previews are distinct. Nothing here edits B1, A1, A2, imports app cards, or certifies a release.

**Precedence:** explicit user 3-pass process limit > old micro-round habits; existing seven technical quality gates, accepted-current authority, one-card/multiple-meaning rule, safety and immutable source/SRS constraints remain mandatory. In any conflict, declare a concrete BLOCKED gate, never fake validation.