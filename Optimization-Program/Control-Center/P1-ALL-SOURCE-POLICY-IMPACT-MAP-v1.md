# GFP-OPT P1 — Central Policy Impact and Adoption Eligibility Map v1

**Program:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`).
**Management:** Project Control Center.
**Machine-readable profile:** [P1-ALL-FAMILY-APPLICABILITY-v1.json](Profiles/P1-ALL-FAMILY-APPLICABILITY-v1.json).
**Executable impact planner:** [Tools/plan_central_policy_impact_v1.py](../../Tools/plan_central_policy_impact_v1.py).
**Evidence status:** **Candidate policy impact + historical source-format witnesses. NOT native integration or any new Stage/FINAL pass.**

## Goal: one user decision, predictable affected owners

A cross-source instruction is made once in the global policy registry. The system first finds exactly which source families, Git workspaces and workstreams **might be affected** based on a source-domain profile, before editing anything. A producer can then apply a compatible new rule only at its **next authorized mutable boundary** with a source-specific adapter and independently checked real output. This makes the common instruction discoverable without duplicating it in every conversation while avoiding silent changes to older content.

The original [registry](../../Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json) has **15 version-pinned bindings**. Their paths, Git blob SHAs and stage/scope tags remain the authority. The planner checks them as well as exact canonical Git blobs of the project catalog, earlier adoption snapshot and historic real-output witness metadata. A registry change or unknown scope **blocks execution pending review**; it does not silently waive QA or write to content.

## Actual project inventory (no double-counting)

| Different entity types | Count | Meaning |
| --- | ---: | --- |
| Library content families | **21** | Source domain owners, including Grammar, Lesen/Schreiben, lexical, mixed and visual work |
| Git workspace directories | **34** | Separate workspaces; many are revisions/QA of the same owner rather than independent producer families |
| Root project workstreams | **17** | Other state/index pointers, each mapped to a content family |
| Existing central policy bindings | **15** | Normative version-pinned policies and technical gates |
| Explicit QA-only Git workspaces | **3** | Resume/quality work; **not counted as direct producers** |

The manually scoped source-domain family baseline is:

| Proposed domain / required adapter | Families | Rule |
| --- | ---: | --- |
| Lexical source candidate | **12** | Can be a candidate for lexical and neutral Stage5 gates; actual field/schema and authoring mutability must be checked |
| Mixed source with split profiles | **2** | Aber Hallo and Menschen Portfolio require content/producer-role split |
| Grammar | **3** | Grammar-specific schema; only explicitly extracted lexical suboutputs could use vocabulary rules |
| Reading / writing | **1 + 1** | Separate Lesen/Schreiben QA and native output profiles |
| Visual / picture cards | **1** | Image/caption-specific contract and provenance checks |
| Generic Vocabulary / imported material | **1** | Real native generic producer and current authority unresolved |

These are **engineering candidate classifications based on the catalog**, *not* linguistic validation of source books or assertion of actual output schema.

## Machine-readable impact types (every rule × every source)

The planner evaluates **315 binding–family candidates** (15 × 21), **510 binding–Git-workspace navigational views** (15 × 34), and **255 binding–root-workstream navigational views** (15 × 17). They intentionally overlap; **never add them into 1,080 separate producers**.

Status examples:
- `ROUTED_PROSPECTIVE_NO_EXECUTION_PROOF`: normatively routed on a new source task; not an observed adapter invocation.
- `LEXICAL_CANDIDATE_FIELD_LEVEL_PROOF_REQUIRED`: potentially related vocabulary policy; exact existing fields and mutability need examination.
- `SPLIT_SOURCE_PROFILE_REQUIRED`: mixed sources need independent field/suboutput scope.
- `DOMAIN_ADAPTER_REQUIRED_NO_FORCED_LEXICAL_SCHEMA`: grammar, Lesen/Schreiben or media source must not be coerced into ordinary vocabulary.
- `HISTORICAL_FORMAT_WITNESS_NOT_CURRENT_OR_ADOPTED`: 250 Verben and Menschen A1 Verben archived format checks are genuine *historical shape evidence* only.
- `QA_WORKSPACE_NOT_DIRECT_PRODUCER`: QA workspace is not an authoring producer.
- `NATIVE_GENERIC_OUTPUT_MISSING`: native generic Vocabulary output is unresolved; any Stage5 adapter claim must remain blocked.

**History preserved:** archived 250 Verben R8 (292 rows) and Menschen A1 Verben R10 (310 rows) have separately verified original ZIP/member SHA and structure from [the prior local real-byte receipt](../Verification/OP01-OP02-P1-TWO-REAL-PRODUCER-FORMAT-20261105.json). This is **not** a new CI recheck of private Library ZIPs and **not** source-to-card linguistic Stage4. The [governed official Stage5 launcher](../../Tools/build_governed_clean_delivery_v1.py) is implemented and synthetic-end-to-end tested, but no eligible source family has yet submitted an actual, current, independently accepted production receipt through it.

### How future chats can query exactly one decision

```bash
# Overview: all active bindings and honest impact states
python -B Tools/plan_central_policy_impact_v1.py --summary

# Candidate impact of a change to the active combinations rule
python -B Tools/plan_central_policy_impact_v1.py \
  --binding kombinationen_source_first

# Exact Stage5 neutral gate candidates, not a claim of actual adoption
python -B Tools/plan_central_policy_impact_v1.py \
  --binding stage5_neutral_validator

# Only one family + its related Git workspaces and root workstreams
python -B Tools/plan_central_policy_impact_v1.py \
  --binding lexical_relation_display \
  --family family:menschen-a1-verben

# Write-once evidence report: cannot replace a prior report
python -B Tools/plan_central_policy_impact_v1.py \
  --summary --write-once-report /new/path/p1-impact-report.json
```

For each policy, the result includes exact policy paths, stage numbers, source-family statuses, inherited workspace/root impact and next action. An exact Git-blob mismatch, changed project count, missing family profile, unknown policy scope, falsified Stage status, undocumented QA workspace or historical witness manipulation fails closed. The GitHub workflow [`gfp-opt-p1-central-policy-impact.yml`](../../.github/workflows/gfp-opt-p1-central-policy-impact.yml) creates downloadable scoped **candidate-only** full matrix artifacts on Ubuntu and Windows and runs adversarial checks.

## Required remaining real adoption steps — P1 is still OPEN

1. Resolve one affected **source owner's** latest validated portable package and precise native producer/output schema. Never assume the old Git checkout is CURRENT, and do not let the project catalog substitute for a source-specific CHECKPOINT.
2. At an explicitly authorized future mutable Stage5 publication, route compatible neutral vocabulary families through `Tools/build_governed_clean_delivery_v1.py`; other source profiles need their **own** adapters. Source/LOCKED/current cards remain unchanged unless separately authorized.
3. Check exact actual four roles, active central policy version and full output package bytes; receive a write-once source-specific governed receipt and independent remote Git/Library readback. A missing direct producer invocation is **NOT ADOPTED**, regardless of a README statement.
4. Add only that source's scoped adoption claim with the precise policy binding, native producer, source/output SHA, applicable stage and QA test; do **not** mark all 34 workspaces or 21 families PASS.
5. Feed these typed per-source updates into the future holistic dashboard (P3). The dashboard must distinguish policy applicability, adapter availability, real-current execution, remaining HOLDs and Stage4–7 acceptance.

**Safety:** no automatic global bulk edits, fabricated senses or source evidence, no app UI/runtime/FSRS/SRS modification, no blanket PASS, no deletion of private Library files.
