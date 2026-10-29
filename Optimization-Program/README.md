# German Flashcards — Continuous Optimization Program

**Program ID:** GFP-OPT-2026 | **Created:** 2026-10-29 | **Status:** ACTIVE (coordination only)
**Main GitHub tracking issue:** [#25 — Cross-Repo Optimization](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/issues/25)
**Machine-readable one-page snapshot:** [STATE.json](./STATE.json)

## What this covers
- [German-Flashcards-Pro](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro): CURRENT app/runtime, importer, storage, tests, packaging, performance, usability **without unapproved visible UI changes**.
- [German-Content-Production-Kit](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit): source ingestion, source-fidelity, Stage 1–7, Grammar, Vocabulary, Menschen, Lesen, Schreiben, NVV, enrichment, linguistic QA, output and content packaging.
- Library: archive growth, duplication, safe recovery/retention; **no automatic deletion**.

**Purpose:** Deliver more actual high-quality learning content with less overhead. This is a cross-repository *optimization program*, not a new content workstream, app version, framework authority or substitute for workstream checkpoints.

## Mission and continuation invariants — 2026-10-29 (USER CORRECTION)

**ACTIVE, supersedes the contradictory "Scoped optimization cycle handoff" below.** This program's user-established purpose is optimizing the **workflow, rules, policy precedence, stage pipeline, content production system, QA, engineering efficiency, packaging and cross-repository process**. This is NOT a content-generation chat. The user explicitly corrected an unauthorized switch to Menschen B1 after an assistant called a scoped audit closed. The correction is durable and binding for all agents that re-read bootstrap/policy.

- **Bare `ادامه بده` / `continue` / Tampermonkey repetition = continue THIS optimization mission** and its still-open OP-01/OP-02 work. Never interpret assistant suggestions, past answers, automated prompts, state labels such as `SCOPED_CLOSED`, an external content LATEST, or a terminal milestone as user permission to start editing lesson/vocabulary data.
- OP-01 **policy precedence and conflict resolution** and OP-02 **Stage 1-7 workflow/compatibility improvements** remain the central tasks. OP-03/04/06/07 scoped CI results stand as verified evidence, but they do not close OP-01/02 or authorize a mission shift. OP-05 remains gated on exact Library byte evidence and user deletion consent.
- Content workstreams (Menschen, Verben, Grammar, Vocabulary, Lesen, Schreiben, NVV) may be opened **READ-ONLY** for concrete process tests. Never silently edit, create a successor content ZIP, import, or advance their LATEST/checkpoint under a generic optimization `continue`. Their independent content work remains valid and separately authoritative.
- **Switch domains only on an explicit user command/confirmation**, e.g., "Now produce Menschen B1 content." "Continue" is not such a command, even if an assistant previously suggested switching. The original project mission and explicit subsequent user correction outrank assistant-authored handoff text.
- If optimization is truly blocked, document the precise blocker and proceed to the next safe optimization action; never substitute easier content work as a fallback. Do not declare global closure while OP-01/02 are incomplete. Preserve UI, source, LOCKED, exact runtime and Git CAS rules.
- This mission continuity rule is mirrored in both repositories' `PROJECT-BOOTSTRAP.md` and `EXECUTION-OUTCOME-EFFICIENCY-POLICY.json`; machine state is `Optimization-Program/STATE.json`. The previous Menschen B1 content edits, if persisted, are independent historical work and must not be counted toward optimization deliverables.

**Regression decision examples:** `optimization + continue → OP-01/OP-02`; `optimization + assistant "go produce content" + continue → OP-01/OP-02`; `optimization + OP-05 blocked + continue → other OP item`; `explicit user "switch to Menschen B1 production" → permitted independent content work`; `Menschen production + continue → same Menschen stream`.

## Thirty-second startup for any chat / agent

**Fast path (OP-04):** Read [RESUME-ROUTES.json](./RESUME-ROUTES.json) to locate the exact workstream files without loading the 1.05 MB root PROJECT-STATE in the chat. This is a generated **navigation directory only**, not a replacement for the root state, source manifests, current portable artifacts or LATEST receipts. For a named workstream, fetch its accessible LATEST and cited milestone receipt first; if neither exists, inspect the tracked CHECKPOINT and portable authority. Entries marked `tracked:false` are missing **in the Git checkout only**, not proof that Library/source bytes are missing. Always re-resolve newer user uploads and Flashcards CURRENT when integration matters.

**Known diagnostic:** GitHub's line-range file reader returned an empty body for the 1,050,584-byte Content Kit `PROJECT-STATE.json`, but GitHub's Contents API returned parseable JSON. The snapshot's root `updated_at` is 2026-10-14; do not treat it as newer than later workstream LATEST/receipts. Route inventory is verified by `python -B Tools/build_resume_routes.py --check`; regeneration uses the same command without `--check`. Do not produce a ZIP just to change routes.
1. Read **this README + [STATE.json](./STATE.json)** and [issue #25](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/issues/25). Only the latest verified durable data counts.
2. Read both repositories' `PROJECT-BOOTSTRAP.md` and `PROJECT-STATE.json` first for substantive work, as required by the project; do **not** fetch huge full state/history if a targeted field, compact pointer or exact source can resolve it.
3. For the specific task, resolve authoritative app CURRENT pin or content workstream `LATEST.json` / `CHECKPOINT.json`, new user-supplied newest artifact, and required source/manifest. A program summary never overrides an exact package SHA, workstream currentness or a later verified artifact.
4. Work on one meaningful bounded optimization outcome; edit/test real source where safe. Do not create another issue/report/ZIP just to record routine activity.
5. At a **validated meaningful milestone**, update only affected source workstream plus this one `STATE.json` (and issue #25 only for milestone decisions or blockers). Record links and exact next action; sync Git with existing bounded rules.
6. Library `/German-Flashcards-Optimization/` has a **small read-only navigation snapshot**. Git is the living tracker; Library is NOT a second mutable progress authority.

## Roadmap / Arbeitspakete

| ID | Scope | Starting state / exit condition |
| --- | --- | --- |
| OP-01 | Policy consolidation + precedence | Existing v3.3.6 and many overrides; produce conflict dispositions and one lean decision graph, not a fresh overlay |
| OP-02 | Stage1–7 integrated enrichment | Existing Stage3/Stage4 pilot and 12-conflict matrix are PROPOSED; validate compatibility, user-authorize migration, independent Stage4 untouched |
| OP-03 | ZIP/builders and retention guard | `Tools/content_package_guard.py` exists; discover all callsites/bypasses and enforce negative tests (initial priority) |
| OP-04 | Currentness and restart index | Large Content `PROJECT-STATE.json` returned empty in a partial remote fetch; diagnose tool limitation vs file health, build small index without competing authority |
| OP-05 | Library storage + dedupe | SHA+dependency inventory; no deletion or overwrite before reversible verified recovery and explicit approval |
| OP-06 | Flashcards runtime efficiency | Respect CURRENT pin, existing importer/persistence/QA and stable UI; measure avoidable tool/workflow overhead |
| OP-07 | Cross-project QA and measured rollout | Demonstrate full real-data acceptance, source parity and measured before/after improvement before promotion |

### Current facts / caveats (snapshot 2026-10-29)
- Git snapshot: Flashcards Pro `v486-R120`; Content Kit active `v3.3.6`. Always re-resolve actual CURRENT and new supplied artifact.
- Existing architecture work: `Architecture/Stage3-Stage4-Unification/`. Its proposal and conflict matrix are **not active**.
- `250 Verben` tracked second-pass progress as 95/431 visible combinations in the corresponding 2026-10-29 readiness snapshot: 336 remaining, not full Stage4 PASS. This is **not** a reason to rerun the whole unrelated audit here.
- The packaging guard is present in code, but complete producer coverage has not been demonstrated.

## What must not happen
- No cloned governance: **one progress snapshot in Git**, a single stable epic (#25), existing exact workstream checkpoints, one lightweight Library navigation copy.
- No historical ZIP churn to prove a no-op; no Git binary transport; no unbounded retries.
- No re-auditing closed cases without a changed dependency/source/hash. No false full PASS from scoped checks.
- No destructive source/LOCKED edits or Library deletions; preserve all recovery evidence.
- No content architecture migration, policy promotion, or visible UI change without the required approval and rollback verification.

## How to update STATE.json
Change only substantive status/count/evidence after verified work. Each work package has `status`, `last_evidence`, `next_action` and `blocker`. Keep history in existing Git commits/issue comments; avoid adding one file per session.
No arbitrary percentage scores or fictional elapsed-time/savings numbers. Never claim Git-backed VERIFIED unless actual write and readback have succeeded.

**Deutscher Leitsatz:** *Weniger Verwaltung, bessere Lerninhalte, nachvollziehbare Ergebnisse.*


## Scoped optimization cycle handoff — 2026-10-29

**SUPERSEDED HISTORICAL HANDOFF:** An earlier assistant declared the bounded optimization pass closed and attempted to redirect ordinary `ادامه بده` to content. This redirect was rejected by the user and is NOT ACTIVE. Preserve the scoped CI PASS evidence below, but keep the main optimization mission active until user-authorized completion. This is **not** a global Stage1–7 content PASS, a release, or a declaration that every OP ticket is complete. Do not reopen this coordination audit just to generate another report.

| Package | Verified exit / remaining boundary |
| --- | --- |
| OP-01 | Existing `EDIT-APPLY-VERIFICATION-CONTRACT.json` is `ACTIVE_USER_REAFFIRMED` and `EXECUTION-OUTCOME-EFFICIENCY-POLICY.json` is `ENFORCED`. Global writer-by-writer enforcement and final conflict consolidation are not proven; address only when a specific affected current editor/writer needs it. |
| OP-02 | Stage3–Stage4 metadata-compatibility CI is green **for proposed metadata compatibility**, not Stage5/6/7 global acceptance. Structural migration is explicitly deferred pending authority/compatibility/approval evidence. No contract promotion. |
| OP-03 | Existing safe ZIP builder regressions PASS; old exceptional builders remain frozen until separately examined. |
| OP-04 | Generated 17-workstream route index + missing-path flags and Windows/Linux CI PASS. Index does not replace exact LATEST/CHECKPOINT / user artifact. |
| OP-05 | Library native-item raw bytes are unavailable for verifying two independently named copies; same size/name is NOT a duplicate proof. Zero files deleted; conditional upper bound ≠ reclaimable storage. Exact B1 13-part Google Drive backup is independently recoverable. HOLD until a file-ID-bound exact hash readback and specific deletion approval. |
| OP-06 | CURRENT `v486-R120` unchanged. Chromium cache and CI contract tests PASS; full CURRENT engineering CI [40801533977](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/actions/runs/40801533977) PASS. The first cold-cache run took 7m02s (workflow created→updated) versus historical median ~5m39s; **no speedup established**. Only evaluate a future natural cache-hit run, don't trigger bulk rebuilds for statistics. |
| OP-07 | Cross-repo **scoped evidence review** completed: app CURRENT gate, app ZIP Ubuntu/Windows, content ZIP Ubuntu/Windows, route Ubuntu/Windows, Stage3/4 compatibility Ubuntu/Windows all PASS. It does not verify every content workstream or qualify a new final release. |

**Scope-preserving resume:** continue OP-01/OP-02 process improvements even when other OP items are complete/gated. Exact new Library SHA, failed CI, authorized migration and user requests are additional triggers, NOT prerequisites for continued optimization. Producing lesson/card content requires its own explicit user instruction; a generic `ادامه بده` here is NEVER such authorization. Never skip the mandatory two-repository startup when relevant, never downgrade a newer user artifact, and preserve LOCKED/source and the established UI.

**Evidence pointers:** App CURRENT [40801533977](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/actions/runs/40801533977), app ZIP [40801533968](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/actions/runs/40801533968), content ZIP [40799073055](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40799073055), routes [40802536961](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40802536961), metadata compatibility [40802480438](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40802480438). Machine state below and issue #25 retain exact status, not a fictional all-green result.
