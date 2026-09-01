# Changelog — Prompt v3.1.9

## Status

Prompt-only hardening. No redesign of German Language Content Architecture v3.1.5.

Base: `CONTENT-GENERATION-MASTER-PROMPT-v3.1.8.md`

Trigger: independent Codex adversarial audit of v3.1.7 vs v3.1.8.

## Changes

### Final Architecture-grounded audit patch

The executable Start/Master prompts were cross-checked against the actual Architecture v3.1.5 schemas, profiles, validators, fixture and Universal-v2 Delivery Spec. The final candidate additionally:

- treats unknown fields in Contract 3.1.3 closed schemas as blocking canonical input while preserving their exact source value in an external Audit ledger;
- scopes migration plans/tombstones/archives outside Canonical JSON and defines Unit-split owner-ID remapping;
- defines count enforcement semantics, lossless retirement archives and explicit before/after order mappings;
- scopes Sense identity to `(unit_id, sense_id)`;
- uses the Architecture v3.1.5 official Canonical JSON → Universal-v2 TSV delivery path instead of assuming Native-JSON/Unified-ZIP authorization;
- forbids `content_protocol` in the Contract 3.1.3 canonical top level;
- binds BUILD-METADATA to the eight-field target-owned Delivery Spec contract and records other provenance in Audit metadata;
- keeps `MAPPING-LIMITATIONS.json`, migration archives and unknown-field ledgers out of an Import ZIP unless the target explicitly treats them as non-importable.

1. **Unknown Field Preservation — Hard Gate**
   - Declared optional/extension fields are preserved losslessly in schema-permitted scopes.
   - Closed-schema unknown values are preserved losslessly in an external Audit ledger and block Canonical finality until mapped/upgraded.
   - Unknown required semantics fail closed.
   - Added JSON Pointer + before/after value-hash audit requirement when extensions exist.

2. **Deterministic MIGRATION_PLAN**
   - Split/merge/retire/reactivate/destructive count reduction require a complete migration plan before mutation.
   - Plan binds survivor/new/retired IDs, old→new mapping, references, history disposition, allocator state and rollback.

3. **Deterministic Example Count Migration**
   - Increase preserves objects/IDs and appends exactly the delta.
   - Reduction requires ordered retain/deactivate IDs and a non-destructive archival/tombstone policy.
   - Without policy + plan: REVIEW_REQUIRED and no mutation.

4. **Example Order Parity**
   - `order` must be integer/unique and profile-compliant.
   - `(example_id, order)` parity is validated across canonical/delivery/post-ZIP roundtrips.

5. **Example ID Ordinal Clarification**
   - Numeric suffixes are immutable allocation sequence, not display order.
   - Reorder may never renumber IDs.

6. **Capability Derivation Hardening**
   - Required/optional capabilities derive only from Semantic Contract + actual Dataset features.
   - Target only negotiates support; it cannot downgrade requirements.
   - Capability registry/spec must be authoritative.
   - `compatible_base_contract` must be contract-owned and validator-verified.

7. **Restored Live Runtime Advice Guardrail**
   - Without same-artifact actual-runtime preflight, do not instruct the user to import immediately or describe current-runtime safety.
   - Report `CURRENT_RUNTIME_NOT_VERIFIED`.

8. **Normative Sidecar Requirements**
   - BUILD-METADATA must follow the resolved target-owned Sidecar field contract.
   - Architecture v3.1.5 uses its exact eight required fields; extra provenance stays in Audit metadata unless the target permits it.

9. **TSV Mapping Transparency**
   - TSV is explicitly non-canonical.
   - Lossy/non-isomorphic projection requires machine-readable `MAPPING-LIMITATIONS`.
   - Lossless transport status is forbidden when a required lossless envelope is unavailable.

10. **Validator Evidence Binding**
    - Status-bearing reports must bind validator identity/hash, exact input filename/hash, execution ID/time, policy, sampling mode, exit code, result and findings count.
    - Stale report hashes cannot satisfy gates.

11. **Formal Status State Vector**
    - Structure, linguistic, transport, isolated-runtime and actual-runtime statuses are reported separately.
    - Roll-up statuses use fixed implication rules.

12. **Audit Package Reconciliation**
    - Complete payload inventory/manifest reconciliation restored.
    - Manifest self-listing/count wording must be explicit.

13. **Prompt Version**
    - Active generation metadata is now `prompt_version="v3.1.9"`.

## Non-goals

- No Architecture v3.1.5 redesign.
- No change to the core DE↔FA↔EN semantic model.
- No claim that a dataset is linguistically validated.
- No claim that a live user runtime has been verified.
