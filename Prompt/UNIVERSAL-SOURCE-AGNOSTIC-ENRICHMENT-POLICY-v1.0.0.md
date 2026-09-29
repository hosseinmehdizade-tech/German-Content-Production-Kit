# Universal Source-Agnostic Enrichment Policy v1.0.0

Mandatory for new or reopened lexical production under Content Production Kit v3.3.6+.

1. Different source formats use different adapters only until universal source occurrences exist.
2. Stage 1 preserves source truth; it does not enrich.
3. Stage 2B closes identity before expensive enrichment.
4. Stage 3A creates the whole-dataset richness matrix before the first enrichment edit.
5. Stage 3B works unresolved semantic gaps and persists accepted/rejected candidates.
6. Stage 3C requires 100% final disposition of applicable cells.
7. Final states are `VERIFIED_PRESENT`, justified `CLOSED_NO_FORCE`, or policy-permitted `NOT_APPLICABLE`.
8. Blank, unreviewed, blocked, conflicted or deferred cells are not PASS.
9. Search follows available field-authority routes and stops when a safe claim is proven or applicable routes are exhausted; no density chasing.
10. Stage 4 independently re-audits the exact canonical/evidence state.
11. Stage 5 reruns completeness/identity gates and binds them to the exact canonical hash.
12. Rejected candidates are durable negative knowledge unless evidence/policy changes.
13. Change-impact fingerprints invalidate only dependent stages.
14. Historical LOCKED artifacts are immutable; repairs are delta successors.

The exact contracts, schemas, default lexical dimension policy, validators, templates and v3.3.6 builder are normative in the verified portable authority recorded in PROJECT-STATE.json.
