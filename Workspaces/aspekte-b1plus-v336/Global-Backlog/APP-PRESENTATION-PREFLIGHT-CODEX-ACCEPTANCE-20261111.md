# Aspekte B1+ — App preflight, exact-current 1571-card projection (2026-11-11)

**QA only · NONIMPORT · no current app source/learner data changes · no new language review loop.**

## Source of truth

Content ZIP SHA-256: `302c50d61d23990f487a4d34114b9d49074e7fe5213b08af6778c5233ecd1d90`  
Primary JSONL SHA-256: `b0ebab61cfbb9a4a2f625316e421fd9bb7cf5a4a82c1d13432683bb409e86e80`  
Source map SHA-256: `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882`

This is **still** the current curated Master pointed to by `LATEST.json` and `CHECKPOINT.json`. Do not replace it with a generated QA fixture.

## Concrete result saved in Library

`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Reports/Aspekte-B1plus-APP-PRESENTATION-PREFLIGHT-NONIMPORT-20261111.zip`  
Library ID: `libfile_15acc87540488191b61bf9e5a715e3b4`  
Exact ZIP SHA-256: `b3609b93f1ecb9f26106677196a9bd67a090631fce858f20548ec94975cd1418`, 530,977 bytes, 8 members / 7 checked SHA256 manifest entries. Library readback exact-byte match.

The archive contains:
- **1,571-card typed Presentation QA JSONL fixture** (not Native German Content 3.1.3, not importable)
- Machine-readable preflight report and **14-item acceptance matrix**
- Reproducible SHA-pinned Python builder, 8 negative mutation checks, Codex implementation handoff and a fail-closed nonimport source receipt.

## Measured right-card data, no fabricated content

| Measured structure | Current |
|---|---:|
| Cards | 1,571 |
| German–Persian example pairs | 3,607 |
| Cards with no structured sense network | 855 |
| Cards with one structured sense | 419 |
| Cards with 2+ senses | 297 |
| Total structured senses | 1,124 |
| Examples without structured sense link | 1,786 |
| Structured senses without their own example | 11 |
| Explicit example associated with multiple senses | 1 (source ordinal 363) |

**Conversion rule:** keep 855 cards' Persian meanings and 1,786 examples as GENERAL; do not invent a Wortnetz just to fill fields. Keep complete raw typed semantic networks and their per-sense relation arrays on the other 716 cards. Keep the one real dual-routed DE/FA example (source ordinal 363 `alle / alles / aller-`) linked to S1 and S2; preserve a single payload. Do not infer links by matching text.

All old 1,571 `requires_independent_semantic_and_morphology_QA` metadata flags are provenance, not a new independent human-review gate. All 1,571 `import_ready=false` and `formal_release_approved=false`. 359 historical risk HOLD cases had scoped decisions, **not global semantic signoff**.

## Acceptance matrix: 4 PASS / 3 BLOCKED / 7 NOT_TESTED

PASS: current owner SHA+manifest, stable IDs and mapping, typed QA mapping with 3,607 examples and two-sense case, 8 negative projector mutations.

BLOCKED: authorized exact owner-controlled release manifest, full PR #41 native index + SW/integrity/CI integration, user acceptance and release decision.

NOT_TESTED: real successful imported TSV, Native JSON, ZIP import; native right-card rendering; origin-backed IndexedDB persistence after reload; preserved SRS history; backup/restoration and atomic rollback.

## App code handoff, not a deployment

Current app reference: v505-R141 WORDLINKS_FRONTBACK_R3, exact base branch `candidate/v505-r141-wordlinks-r3-exact-20261107`, commit `02b83543e46aebaa6fc345818930406b1607a83c`. [Draft PR #41](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/pull/41) has the nonprod ingress guard modules and a hash-pinned patch builder **but does not patch current `01-App/index.html`**.

The review branch's **20/20 guard checks + 10/10 isolated Preview/Submit checks + 6/6 nested-marker checks** are about NONIMPORT rejection, not native durable success. Other repo-wide CI checks failed. Editable release markers are not trusted source authentication.

**Next action:** Codex/app owner should implement a separately reviewable full native adapter + trusted owner-controlled exact-byte allowlist/signed digest, preserve `sense_ids` arrays, test real right-card Presentation and genuine IndexedDB writes/readback/restarts/SRS in a safe test profile. Require no reset of current learner data and a rollback test. Only a user-approved release decision can promote NONIMPORT.

Stop criteria: no repeated lessons/P1/P2/P3, no fake Wortnetz, no auto-approval via removing markers, no claim that this QA JSONL archive is an import file.
