# German Flashcards — Continuous Optimization Program

**Program ID:** GFP-OPT-2026 | **Created:** 2026-10-29 | **Status:** ACTIVE (coordination only)
**Main GitHub tracking issue:** [#25 — Cross-Repo Optimization](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/issues/25)
**Machine-readable one-page snapshot:** [STATE.json](./STATE.json)

## What this covers
- [German-Flashcards-Pro](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro): CURRENT app/runtime, importer, storage, tests, packaging, performance, usability **without unapproved visible UI changes**.
- [German-Content-Production-Kit](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit): source ingestion, source-fidelity, Stage 1–7, Grammar, Vocabulary, Menschen, Lesen, Schreiben, NVV, enrichment, linguistic QA, output and content packaging.
- Library: archive growth, duplication, safe recovery/retention; **no automatic deletion**.

**Purpose:** Deliver more actual high-quality learning content with less overhead. This is a cross-repository *optimization program*, not a new content workstream, app version, framework authority or substitute for workstream checkpoints.

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
