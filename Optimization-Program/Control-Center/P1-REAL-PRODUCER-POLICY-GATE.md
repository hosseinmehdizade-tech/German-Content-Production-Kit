# GFP-OPT P1 — Executable cross-producer policy gate (first scoped implementation)

**Program:** German Flashcards — Continuous Optimization Program `GFP-OPT-2026`
**Controller:** Project Control Center
**Global policy authority:** [exact pinned v1.0.0 registry](../../Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json)
**Concrete governed binding:** `stage5_neutral_validator` → `Verification/validate_unified_vocabulary_projection_v1_1_0.py` (Git blob `b6d27c0b98f44cd8b0ffad325710f24f76da95e1`).

## What now executes

[One shared CLI](../../Verification/verify_global_policy_real_producers_v1.py) resolves the active versioned central policy registry, validates its Git blob and the **exact central validator implementation**, and checks every byte of the actual ZIP and actual native 23-column TSV from each named owner-specific [profile](Profiles/P1-NEUTRAL-STAGE5-REAL-PRODUCERS-v1.json). It rejects wrong archive hash, CRC, missing/duplicate members, traversal/symlink paths, wrong source, malformed envelope, non-JSON learner-facing `details`, stale policy pins, unsafe presentation overrides, repeated card IDs and fake current/stage promotion. No imported ZIP/member is extracted or rewritten.

One source-independent rule is run against two independently generated **real archive formats**, not a copied synthetic envelope: archived `250 Verben` R8 official Stage5 and `Menschen A1 Verben` R10 Stage5. They have different internal archive layouts, source fields, input editor policies, provenance and category distributions, but share the same neutral Stage5 output contract. The local independent [real-byte format receipt](../Verification/OP01-OP02-P1-TWO-REAL-PRODUCER-FORMAT-20261105.json) saw **292 + 310 = 602 actual TSV rows** with CRC/SHA/neutral/details/recursive presentation check PASS. That local mirror is NOT the same as an official CLI run and does not replace it. GitHub CI tests source-neutral code with generated synthetic archives **only**, so never label GitHub results as private Library ZIP rehash.

### Example: exact real archive command

```bash
python -B Verification/verify_global_policy_real_producers_v1.py \
  --archive 'producer:250-verben-v18-r8-stage5=/your/exact/250-Verben-Lexical-Enrichment-v1.8-R8-STAGE5-OFFICIAL-CLEAN-DELIVERY-20261105.zip' \
  --archive 'producer:menschen-a1-verben-r10-stage5=/your/exact/Menschen-A1-Verben-R10-STAGE5-CONTENT-ACCEPTED-FOUR-MODES-20261105.zip' \
  --report /your/write-once/P1-REAL-PRODUCER-RESULT.json
```

The CLI fails closed if either source archive is absent or has been replaced by different bytes. `--allow-partial` runs an explicitly incomplete scope and lists omitted registered producer profiles. `--report` must be a **new** JSON path, never the input ZIP.

## Adoption is not a blanket producer PASS

The [authoritative roadmap](../CONTROL-CENTER-UNIFIED-GOVERNANCE-ROADMAP-v1.0.0.md) still prioritizes **P1**. Current achieved scope is an executable registry-bound **Stage5 neutral format** gate and two independent historic real-output shape witnesses, *not* automatic registration into every source’s producer, not source-first semantics for combinations, not per-workstream Stage4 acceptance, and not app runtime/browser Stage6.

The original 15 pinned policy bindings remain immutable. The 34-workspace inventory is a navigation catalog: two real source **families** represented here must never be mistaken for 2 newly certified Git workspaces, nor can the other families be called compliant without actual producer evidence. The next P1 engineering stage is adding safe opt-in/required invocation points to actual eligible native builders **without changing their source or card data** and then updating the typed adoption matrix with real-currentness proof.

**User safety:** no current/LOCKED rewrite, no flashcard edits, no app runtime/UI/FSRS/SRS changes, no release promotion or automatic cleanup of Library.
