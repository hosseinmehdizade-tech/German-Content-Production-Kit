# Codex Remediation Matrix — v3.1.9

This file records how the independent Codex findings against v3.1.7/v3.1.8 were addressed.

| Codex Finding | Severity | v3.1.9 Resolution |
|---|---:|---|
| Unknown optional fields can be silently dropped | HIGH | Declared extensions are preserved in place; Contract 3.1.3 closed-schema unknowns are preserved in an external ledger and block Canonical finality |
| Split/merge/retire/count migration not deterministic | HIGH | Added mandatory `MIGRATION_PLAN` and deterministic survivor/retirement/allocator rules |
| Example order missing from parity | HIGH | Added order validation + `(example_id, order)` parity |
| v3.1.8 weakened live-import advice | HIGH regression | Restored same-artifact actual-runtime preflight requirement before immediate import guidance |
| Required capabilities could be target-shaped | HIGH | Capabilities derive only from Contract + Dataset features; Target only negotiates |
| `compatible_base_contract` producer assertion too weak | HIGH | Requires contract-owned declaration + validator verification |
| Unified ZIP sidecar underspecified | MEDIUM | Bound Sidecar to the target-owned field contract; Architecture v3.1.5 uses its exact eight fields |
| TSV projection transparency weakened | MEDIUM | Added machine-readable `MAPPING-LIMITATIONS` and losslessness gate |
| Post-package evidence not mechanically bound | MEDIUM | Added validator artifact/input hash execution binding |
| Status model not formal enough | MEDIUM | Added orthogonal state vector + roll-up implication rules |
| Example ID `-ex-001` looks ordinal | LOW | Clarified immutable allocation sequence ≠ order |
| Repetition creates drift risk | LOW | Start Prompt rewritten as a compact invariant-oriented summary; Master remains normative |

## Architecture-grounded follow-up

The final candidate was independently cross-checked against the actual `German-Language-Content-Architecture-v3.1.5` package. Architecture files were not rewritten. Independent evidence belongs to the Production Kit verification/audit report; this matrix is not itself authority.
