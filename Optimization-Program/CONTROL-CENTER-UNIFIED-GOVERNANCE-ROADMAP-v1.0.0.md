# GFP-OPT-2026 — Unified Governance & Project Control Center Roadmap v1.0.0

**Official program name:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`).
**Central management component:** Project Control Center.
**User decision:** 2026-11-05. **Mission:** one centrally governed instruction, consistently and provably applied to every *applicable* source/workstream at its next authorized boundary, with better coordination and less repetitive prompting.
**Machine-readable authority:** [CONTROL-CENTER-UNIFIED-GOVERNANCE-ROADMAP-v1.0.0.json](CONTROL-CENTER-UNIFIED-GOVERNANCE-ROADMAP-v1.0.0.json).
**Git issue:** [Cross-Repo Optimization #25](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/issues/25).
**Status:** ACTIVE ROADMAP; implementation and source-by-source adoption are NOT globally complete.

## Why this replaces repeated one-project micro-audits

The overall mission is **system engineering**, not producing cards or repeatedly proving that one historical Aber Hallo ZIP has a correct CRC. The successful source-specific audits (Phase1–8) remain valid evidence, but repeating them without a concrete new blocker is a poor allocation of time while central producer-policy enforcement remains incomplete.

A rule such as "source-first, varied, genuinely useful Kombinationen; no cloned examples or artificial quotas" should be defined ONCE centrally. Grammar, verbal valency and lexical combinations have legitimate source-specific differences: **unified governance and schema discipline does not mean identical content or forced fields**.

### The single-decision-to-all-applicable-sources contract

1. **Decide once:** register the user decision, named policy scope, applicability and exceptions; version it, keep prior rules for exact historical replay. Global policy source-of-truth remains [GLOBAL-POLICY-REGISTRY-v1.0.0.json](../Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json) and its [resolver](../Prompt/GLOBAL-POLICY-SYNCHRONIZATION-v1.0.0.md). Do not silently mutate blob-pinned policy documents in place.
2. **Determine impact:** use [MASTER-PROJECT-CATALOG-v1.json](Control-Center/MASTER-PROJECT-CATALOG-v1.json) and prospective ownership/dependency graph. Baseline inventory: **21 Library families, 34 Git workspaces and 17 root workstreams**, with **15 pinned active policies**. Inventory `\neq` verified adoption.
3. **Resolve source profiles:** each source's exact user files, immutable originals and LOCKED history are authoritative. Domain-specific grammar/lexical/Lesen/Schreiben adapters preserve real semantics; incompatible rules produce `POLICY_CONFLICT_HOLD`.
4. **Implement executable producer/consumer hooks:** actual builders, projectors, validators and downstream app import/display contracts must consume the resolved policy or clearly declare `NOT_APPLICABLE`. Static text and a synthetic adapter PASS alone do **not** establish real-producer conformance.
5. **Test real outputs:** per applicable producer, test exact source identity, actual current artifact SHA, output fields, all valid/invalid examples, cross-stage field parity and negative cases. No unsupported `Stage4`/browser `Stage6`/`FINAL` claims.
6. **Progressively adopt at a safe edit boundary:** active new/authorized mutable passes must read latest policy; prior LOCKED cards do not get auto-rewritten. Update a source-specific adoption receipt only after real adapter/QA proof; blocked sources stay visibly blocked.
7. **Report centrally:** exact owners, versions, latest checkpoints, policy applicability, adoption, HOLDs, errors, next action and reproducible proof. A newer user-validated artifact outranks stale Git metadata; other chats refresh only when they resume and read startup files.

## Order of work — not seven arbitrary audit rounds

| Priority | Work package | Evidence-based deliverable | Status |
| --- | --- | --- | --- |
| **P0** | Durable startup and direction in both Git repositories | This MD+JSON, both project bootstraps, active content START-PROMPT, optimization README/state route, CI regression | **Implement first** |
| **P1** | **Executable global policy propagation** (OP-01/OP-02) | A policy change → affected owners → source profiles → real adapter hook + regression tests + adoption ledger | **Next work** |
| **P2** | Native cross-source producer/consumer conformance | Actual A1/A2/B1, Aspekte, Verben/NVV, Grammar and Vocabulary exports; preserve source profiles; report blockers | Open |
| **P3** | Whole-project management dashboard | Last exact authority, status, actionable work, error/HOLD, owner and supersession, not merely SHA labels | Parallel safe read-only |
| **P4** | Safe parallel production and automated checks | Single-writer/CAS publication, expected SHA, Git PR/CI/readback; no stale overwrite; explicit permission model | Needs gates |
| **P5** | Release/package/Library lifecycle | One reproducible organized release ZIP; source/tests/docs/tools/report, no arbitrary duplicates or deletions | Scoped |
| **P6** | Adoption coverage and feedback | Measured producer-by-producer implementation, real QA, conflicts, open bugs and next action | Progressive |

**Prioritization rule:** continue P1/OP-01/OP-02 when no new user-specific target is named. Do **not** drift into another isolated Aber Hallo lineage audit merely because ZIPs exist. Resume an existing named content task only within that task's explicit scope. If a technical block occurs, move to the next safe central-process milestone, not an unrelated content project.

## What was already built versus what is missing

**Historical capabilities (scoped only):** source catalog, project graph, policy registry/version pinning, navigational dashboard, 250 Verben/NVV source proofs and Aber Hallo lineage attestations (Phase1–8). These are **not** a global policy execution engine, live cross-chat synchronization or 34/34 real-producer PASS.

**Known gaps:** native producer adapters and full real output checks remain uneven; previous B1 L19 produced 145 historically malformed `details` fields and its separate content workstream must own any repair; generic Vocabulary native output needs authority resolution; recent working Aber Hallo revisions and stage boundaries remain separate from the Optimization Program. The protected Git writer/authorization model is not universally enforced; an opt-in scoped writer does not prevent every direct GitHub API edit. A future user-approved UI change requires explicit consent.

## Startup / future chats / concurrent writers

For every relevant new or resumed chat:

- Read the two repository `PROJECT-BOOTSTRAP.md` and `PROJECT-STATE.json` files first. If this chat concerns governance/process/consistency, also read **this roadmap JSON and MD**, `Optimization-Program/README.md`, `Optimization-Program/STATE.json`, and the exact active policy registry. A content chat then reads its own source-specific LATEST/checkpoint and applies relevant policies.
- `ادامه بده` in the optimization mission means **P1 first, then next unblocked central objective**. It never means "edit Menschen/Aber Hallo cards" or "promote an app release" without a separate user instruction.
- If a second chat commits a newer authority while this chat works, re-fetch Git pointer at write time and use exact CAS/readback; do not overwrite independent workstreams.
- The roadmap is discoverable by future chats that execute the required bootstrap. It does **not** directly rewrite running chats, push a message to them, give autonomous background permissions, or auto-update all old content.

## Acceptance standard and reporting vocabulary

States must be explicitly typed: `NOT_ROUTED`, `ROUTED_ONLY`, `ADAPTER_IMPLEMENTED_SYNTHETIC`, `REAL_OUTPUT_PARITY_VERIFIED`, `QA_GATE_ENFORCED_AT_ELIGIBLE_BOUNDARY`, `BLOCKED_CONFLICT_OR_SOURCE`, `NOT_APPLICABLE`. Never label a producer `ADOPTED` because its README mentions a policy. For central process changes publish the exact paths/commit, tests on both supported OS, source scope, no-content-write proof and what is still OPEN.

**Next executable engineering task:** choose a concrete policy already pinned in the central registry (e.g. source-first Kombinationen v1.2), build an executable producer-level policy consumption/parity contract, and independently run it against at least two different native producer outputs **read-only**. Only then mark those named producers as real-output verified, not the full family inventory.

---
**فارسی — خلاصه الزام‌آور:** اسم برنامه `German Flashcards — Continuous Optimization Program` و جزء مدیریتی آن `Project Control Center` است. از این به بعد اول موتور اجرایی قوانین سراسری و پایش واقعی اجرای آن‌ها در منابع مختلف تکمیل می‌شود؛ گزارش‌گیری تاریخی یک منبع، جایگزین این هدف نیست. هر قانون باید یک‌بار تعریف، برای منابع مرتبط اعمال، با داده واقعی آزمایش، و وضعیت هر پروژه از مرکز قابل پیگیری باشد. داده‌های `LOCKED`، فایل‌های اصلی، اپ، FSRS/SRS و وضعیت‌های Stage بدون مجوز و مدرک تغییر نمی‌کنند.
