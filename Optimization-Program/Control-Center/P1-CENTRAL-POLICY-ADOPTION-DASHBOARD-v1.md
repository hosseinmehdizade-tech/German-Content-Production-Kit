# GFP-OPT — Unified source-policy adoption ledger & Control Center status

**Program:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`)  
**Management:** Project Control Center  
**Authority:** [central policy registry](../../Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json) and [user-directed roadmap](../CONTROL-CENTER-UNIFIED-GOVERNANCE-ROADMAP-v1.0.0.md).

## The missing system-wide management view

The [project identity catalog](MASTER-PROJECT-CATALOG-v1.json) records **21 source families, 34 Git workspace directories and 17 root workstreams**. The [P1 policy impact engine](../../Tools/plan_central_policy_impact_v1.py) routes **15 pinned rules** to **315 candidate rule-family combinations**, without claiming that any native builder used them. The [existing Git-index Control Center](../../Tools/build_project_control_center_v1.py) gives navigation and latest source checkpoint/status hints. These components are now JOINED by the new [policy-adoption status report generator](../../Tools/build_policy_adoption_control_center_v1.py), using the exact [scoped evidence ledger](POLICY-ADOPTION-EVIDENCE-LEDGER-v1.json).

One generated report shows **every source family's domain**, potential rule scope, known Git Workspace status hints, historical actual-byte evidence if present, explicit current adoption state and actionable engineering next step. The report is read-only and cannot promote historical receipts.

### Two report outputs

```bash
python -B Tools/build_policy_adoption_control_center_v1.py \
  --output-dir gfp-opt-policy-adoption-output

# One family, with explicit "filtered" label; global counts remain honest
python -B Tools/build_policy_adoption_control_center_v1.py \
  --family-id family:menschen-a1-verben \
  --output-dir gfp-opt-menschen-a1-policy-output
```

Each new destination is exclusive/write-once, and outputs `POLICY-ADOPTION-STATUS.json` and `POLICY-ADOPTION-STATUS.md`. Content, source, `LOCKED`, workstream `LATEST`, current App, learner data and FSRS/SRS are never edited.

The [GitHub Actions workflow](../../.github/workflows/gfp-opt-policy-adoption-control-center.yml) executes the same pipeline on Ubuntu and Windows after relevant policy, source-workspace or Control Center metadata changes. It publishes both JSON and Markdown as downloadable build artifacts and a readable GitHub job summary. **The generated reports are Git-index status snapshots, not live GitHub/Library provider proof.**

### Current adoption truth

| Evidence tier | Meaning | Initial entries |
| --- | --- | ---: |
| `ROUTED_ONLY` | Central policy version is available as a prospective instruction | 21 families (source-specific applicability varies) |
| `HISTORICAL_FORMAT_WITNESS_ONLY` | Actual prior cards showed an appropriate structural format, not policy invocation | 250 Verben and Menschen A1 Verben |
| `HISTORICAL_BYTES_MATCH_NO_GOVERNED_RECEIPT` | Previously materialized authentic GitHub + Library files agreed, but produced by the OLD builder | 250 Verben R8 |
| `GOVERNED_LOCAL_EVIDENCE_HELD` | Future eligible source's official governed builder and exact local evidence matched | No registered real producer |
| `REMOTE_BYTES_MATCH_PROVIDER_OR_OWNER_HOLD` | Future independent byte check agrees; provider identity/owner/stage proof still incomplete | No registered real producer |
| `ADOPTED` | Owner-authorized native policy adoption backed by a future reviewed admission record | **0** |

The [real source R8 readback receipt](../Verification/P1-REAL-LIVE-CONNECTOR-R8-NONADOPTION-20261105.json) is pinned to Git blob `b2ef4b4f25762480e29654db06360c4327074e06`, archive SHA `63ae8f2a3a8d2ec5dff94798db3ed060a0b4e43b1cc2699e540beb1393882e5c` and its old workspace `LATEST` blob. If its `LATEST` later moves to a newer content release, the dashboard flags the old anchor as historical rather than erroneously failing every unrelated CI or silently overwriting that release.

### Guardrails and adoption workflow

The ledger **does not grant Stage4, formal Stage5, Stage6, Stage7, CURRENT or FINAL**. The v1 schema explicitly disallows any formal adoption claim until a separate source-owner-approved promotion procedure with the following data is implemented and verified:

1. A new explicitly authorized editable producer boundary and newest user-confirmed source/current portable artifact; separate original/LOCKED protection.
2. Exact central policy and native builder Git blob versions, actual source domain profile and 4-role neutral Stage5 envelope **only where applicable**. Grammar, Lesen, Schreiben, visual and mixed sources require their own domain-specific adapters.
3. Actual official governed native producer invocation, its source-owned write-once receipt, full original and ZIP bytes, policy replay and reproducible QA.
4. Independent live GitHub `main` LATEST, provider-authenticated ChatGPT Library record/materialization, SHA/size/CRC, source-owner confirmation, linguistic Stage4 where applicable and stage-specific acceptance before a **new version** of this ledger can mark that named producer `ADOPTED`.
5. No background cross-chat push, no silent retroactive bulk content rewrite and no app UI/runtime/FSRS/SRS migration.

The current adoption count must be **zero** until such a verified promotion is submitted. The dashboard separates the system's readiness to **find an affected producer** from the stronger claim that it **ran a rule**.

## Next engineering milestone

P1 remains active: add the first safe, source-owned real producer invocation and a strictly typed reviewed adoption v2 ledger using independently authentic provider receipts. In parallel, create non-neutral profiles for Grammar, Lesen, Schreiben and mixed/media outputs. P3 can reuse this dashboard's typed family statuses and next actions rather than building another arbitrary archive-audit report.
