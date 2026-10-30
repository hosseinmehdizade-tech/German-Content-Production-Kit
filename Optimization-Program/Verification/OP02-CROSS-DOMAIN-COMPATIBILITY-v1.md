# OP-02 — Cross-domain source/receipt compatibility probe (NONACTIVE)

**Scope:** Process optimization only; NO content source, learner card, source
ZIP, LOCKED state, CURRENT pointer, official Stage4–7 or app changes. The
stable typed v1 pilot is kept intact. This is a read-only feasibility gate.

## Grounded real metadata models and their incompatible assumptions

| Workstream | Source authority | Recorded QA stage and shape | Required contract style |
| --- | --- | --- | --- |
| Aber Hallo (Grammar) | Two original PDF sources, fixed source IDs/SHA256 | WIP64 receipt; 823 attested + 158 held = 981 governed patterns; 788 units, 787 lexical cards; Stage4 OPEN | WIP/parent/portable-ZIP lineage, source hash order, changed-card ID ledger |
| Menschen B1 | RAR5 Memrise audio archive + CSV export, independently pinned hashes and 9109 CSV rows | Current B1 checkpoint's B1 L01 inventory: 126 rows and 126 audio refs; 24 lessons; lesson stage structure heterogeneous | Course/lesson/source inventory and audio reference integrity; NOT a grammar WIP ZIP/981-pattern receipt |
| Lesen Präsentation | One PDF, registered source SHA256, 76 pages and 68 topics | Stage1 PASS inventory; Stages2–7 NOT_STARTED; source map held as Git evidence, no learner-content ZIP | Stage1 evidence and source topic/ID mapping; no fabricated portable release |

These facts were read from source manifests/checkpoints in the main
repository. In particular, native source formats are **not all PDFs**;
native workstream CURRENTs are not interchangeable. No external
source correction was inferred. The grammar WIP64 test reconstructs
a **synthetic historical LATEST** from the real WIP64 receipt so
later producer WIPs cannot silently change a historical test.
Other workstreams are read-only current source/checkpoint snapshots;
no content edits occur.

## Existing typed-v1 findings

The previous `gcpk-content-milestone-typed@1` pilot assumes a portable
WIP ZIP, source PDF list and a shared 981 pattern universe. Applying it
directly to Menschen B1 or Lesen would either invent missing objects,
mislabel audio/CSV as PDF, or promote Stage1 source inventory to an
unearned content release. Those are **real contract incompatibilities**,
not data errors to auto-fix.

## Read-only validation and trust/rollback

`Verification/audit_op02_cross_domain_shadow.py` explicitly pins three
distinct source identities and exercises each native shape separately.
It tests original source SHA ordering, lesson RAR/CSV/audio inventory
binding, reading Stage1-only claims, grammar parent and ZIP roles,
count conservation and changed ID ledger.

The evaluator always returns FALSE for issuer authentication,
original source bytes, original ZIP bytes, linguistic Stage4,
Stages5–7, production activation and writer permission.
A separate rollback diagnostic takes expected preimage,
expected postimage and observed remote head SHA; stale/concurrent
posts are blocked and no mutation method is exposed.
This does **not** enforce Git branch protection or create a
real rollback. The earlier OP01/OP02 trust root decision remains active.

## Decision before real multi-domain adoption (not approved here)

Prefer a future common **envelope + typed domain-specific payload +
separately pinned trusted source/profile policy**, but do not force
the old grammar-specific v1 fields onto the course/audio or
source-inventory streams. A proposed v2 must preserve real Stage1–7
distinctions, exact source and parent provenance, immutable LOCKED,
unresolved QA holds, and original source modalities.

Full rollout needs: (1) named producer and versioned consent,
(2) source-appropriate adapters and exact binary readbacks,
(3) trusted issuer outside PR-provided metadata, (4) Stage4
semantic review and Stage5–7 applicable gates, (5) CAS/rollback
with independently verified previous/current identities, and
(6) explicit, safe owner-authorized migration/rollback.
Do not activate from a green synthetic CI job.
