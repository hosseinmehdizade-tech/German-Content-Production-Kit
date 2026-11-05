# GFP-OPT P1 — Root checkpoint triage and cross-domain producer preflight v1

**Program:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`)  
**Component:** Project Control Center  
**Status:** Source-registered, Git-index-based, **SHADOW / DIAGNOSTIC ONLY**. No new source or adapter has passed native policy adoption.

This milestone **extends the existing single dashboard** from [PR #100](P1-CENTRAL-POLICY-ADOPTION-DASHBOARD-v1.md), rather than launching another individual historical ZIP audit.

## Five dashboard issues traced to actual root pointers

The **actual GitHub Actions JSON artifact** from prior [adoption dashboard run](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/42062487931) was downloaded and inspected. All five issues are `ROOT_CHECKPOINT_UNTRACKED`. They do **not** prove a linguistic/content failure and cannot be repaired by fabricating `CHECKPOINT.json`.

| Root workstream key | Untracked declared checkpoint | Action |
| --- | --- | --- |
| `250_verben_mit_praepositionen_deutschweb` | `Workspaces/250-verben-mit-praepositionen-deutschweb/CHECKPOINT.json` | Resolve named source owner's latest valid portable workstream |
| `250_verben_mit_praepositionen_kombinationen` | `Workspaces/250-verben-mit-praepositionen-kombinationen-v336/CHECKPOINT.json` | Resolve named source owner; don't rewrite newer parallel checkpoint |
| `grammar_aktiv_a1_c1` | `Workspaces/grammatik-aktiv-a1-c1/CHECKPOINT.json` | Recover/check source-owned grammar checkpoint, don't mark Stage PASS |
| `nomen_verb_verbindungen` | `Workspaces/nomen-verb-verbindungen/CHECKPOINT.json` | Resolve real root/source handoff before correcting root pointer |
| `unregelmaessige_verben_kombinationen` | `Workspaces/unregelmaessige-verben-kombinationen-v130/CHECKPOINT.json` | Resolve actual branch/checkpoint; preserve independently tracked Unregelmäßige Verben work |

The [existing resume routes](../RESUME-ROUTES.json) **already declare these paths untracked**, so the new read-only preflight can match the five root metadata issues to the same named owners without inventing files. A new/different issue is explicitly `REVIEW`, not blindly folded into one of these five cases.

## Cross-domain profiles are NOT neutral vocabulary schema

The [eight source-domain preflight profiles](Profiles/P1-CROSS-DOMAIN-ADAPTER-PREFLIGHT-v1.json) are bound to exact Git blob identities of the existing source registry, domain catalog, resume route map and [OP02 typed-envelope v2 SHADOW script](../../Verification/audit_op02_typed_envelope_v2.py). The script is **nonactive** and its independent anchor/issuer authentication is not a production gate. It cannot issue Stage4/5/6/7 or card editing authority.

| Family (or shared families) | Source-grounded current metadata observation | Required action |
| --- | --- | --- |
| Grammatik aktiv A1–B1, A1–C1, B2–C1 (3 families) | Two actual registered PDFs with exact source hashes; shared `grammatik-aktiv-a1-c1` native checkpoint is untracked | Verify actual newest source owner/checkpoint, develop grammar-specific producer |
| Aber Hallo Listen/Tabellen | Two registered PDFs; existing **grammar WIP** OP02 v2 contract remains SHADOW, not automatically accepted | Preserve WIP lineage/HOLDs and separate grammar unit/source QA |
| Menschen Portfolio | Registered Memrise RAR audio source; its aggregate portfolio is **not** automatically the Menschen B1 audio lesson producer | Split source-owner and lesson/audio suboutputs |
| Lesen | `Präsentation` PDF registered and `lesen-praesentation/CHECKPOINT.json` tracked; it **reports Stage1 PASS** and Stages2–7 `NOT_STARTED`; existing reading OP02 v2 is SHADOW | Stage2 canonicalization is separate source-owned work, not automatic vocabulary Stage5 |
| Schreiben | No source-owned native writing producer/source in current registry | Register the real source/profile before any adapter or Stage pass |
| Bildkarten (Visual) | No source-specific media-producer authority in this preflight | Register original visual source/caption provenance and media-specific QA |

**All 8 nonlexical family profiles remain non-adopted.** The existing 12 lexical families retain their separate neutral vocabulary candidate gate. The generic Vocabulary family still needs its own actual native source. All 21 family status rows remain in the existing Control Center.

## How to run and verify

```bash
# Read-only independent source-domain and checkpoint diagnosis to an unused external path
python -B Tools/build_domain_adapter_preflight_v1.py \
  --summary --output /external/new/preflight.json

# The existing all-project dashboard includes the same detailed preflight
python -B Tools/build_policy_adoption_control_center_v1.py \
  --output-dir /external/new/control-center-status
```

The [cross-OS GitHub workflow](../../.github/workflows/gfp-opt-p1-cross-domain-preflight.yml) writes a JSON diagnosis as a CI artifact and runs negative tests that reject missing source IDs, changed source SHA, source owner drift, OP02 shadow confusion, fake Stage promotion and fabricated checkpoint repair. The existing [central dashboard CI](../../.github/workflows/gfp-opt-policy-adoption-control-center.yml) now rebuilds after source-registry, OP02 or preflight changes, and its JSON/Markdown includes the eight nonlexical HOLD rows and root-checkpoint diagnostics.

**No new Checkpoint, original PDF, LOCKED data, learning card, App UI, SRS/FSRS, or source release is written.** Existing source-level approvals are not reissued; exact Stage/currentness must be proved separately by the source owner.

## P1 next owner action

For the five root checkpoint paths, resolve the **newest valid user-confirmed/source-owned portable package** and compare live source manifests and Git/Library proof before editing any root pointer. Do not silently replace a historical project path or move a lock. In parallel, implement and independently test at least one actual native Grammar/Lesen/Schreiben producer at a permitted source boundary, then attach source-specific governed receipt and provider-backed evidence. All claims remain `NOT ADOPTED` until that happens.
