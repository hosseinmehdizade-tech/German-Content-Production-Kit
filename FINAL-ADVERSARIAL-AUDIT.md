# Final Architecture-Grounded Adversarial Audit — Prompt v3.1.9

## Verdict

**Final audited candidate: READY**

The package as received was **not** ready: four production-relevant contradictions remained. They were repaired in the executable `START-PROMPT-v3.1.9.md` and `CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md`, then independently re-tested. No Architecture v3.1.5 file was rewritten.

This verdict means the Prompt + Architecture workflow is ready to govern large unattended batches. It does not pre-validate the linguistic content of a future Dataset. Every Run must still earn its own source, linguistic, canonical, transport and Runtime statuses.

## Independent authority and evidence used

- Executable Prompt: `Prompt/START-PROMPT-v3.1.9.md` and `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md`.
- Semantic authority: `Architecture/01-CORE/GERMAN-LANGUAGE-CONTENT-CONTRACT-v3.1.3.md`.
- Canonical/Profile/Type authority: `Architecture/02-SCHEMAS/*`, `Architecture/03-PROFILES/*`, `Architecture/04-TYPE-RULES/*`.
- Delivery authority: `Architecture/01-CORE/FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md` and `Architecture/README.md`.
- Real fixture: `Architecture/05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json` with 10 Units / 22 Examples.
- Operational validators and 64 tests under `Architecture/06-VALIDATION/`.
- No PASS/manifest/changelog bundled with either source package was trusted without re-execution or hash comparison.

## Production findings found in the received v3.1.9 candidate and remediated

### BLOCKER — closed-schema unknown fields were treated as valid optional canonical fields

- **Received behavior:** carry every unknown field forward inside Dataset/Unit/Sense/Example/Translation/Connection/Metadata/Provenance.
- **Architecture evidence:** `Architecture/02-SCHEMAS/LEARNING-UNIT-SCHEMA.json:6,34,51,89,114,147,226,253` uses `additionalProperties=false`; operational validation rejects an unknown Example field.
- **Why it mattered:** a model had to choose between violating the Prompt (drop/relocate) and failing the Canonical Schema (preserve in place). No valid `CONTENT_VALIDATED` state existed.
- **Real failure:** an Example with `future_optional` would fail `EXAMPLE_FIELD_UNKNOWN`, while the received Prompt required it to remain in the canonical Example.
- **Regression/common:** new v3.1.9 hardening defect exposed only by the real Architecture package.
- **Applied patch:** `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md`, “Binding Profile” and “Unknown Field Classification and Preservation”. Declared optional/extensions survive in schema-permitted locations; closed-schema unknown values survive in an external hash-bound ledger and block Canonical finality until mapped/upgraded.

### BLOCKER — default Native-JSON/Unified-ZIP contradicted the official Architecture delivery path

- **Received behavior:** Native Canonical JSON was the default primary import dataset in a Unified ZIP; the sample also inserted `content_protocol` at canonical top level.
- **Architecture evidence:** `Architecture/README.md:59-69` specifies Canonical JSON → Universal-v2 TSV → BUILD-METADATA; the canonical top-level Schema permits only `contract_version`, `profile_id`, `learning_units`.
- **Why it mattered:** the default output could be schema-invalid and not be the user-import format defined by the only authoritative Delivery Spec.
- **Real failure:** a Canonical JSON containing `content_protocol` fails Schema; a ZIP importer authorization was inferred from Runtime capability rather than target-owned delivery policy.
- **Regression/common:** Unified Delivery regression relative to Architecture-grounded v3.1.7 semantics.
- **Applied patch:** `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md`, §§1, 2.1, 18.3-18.4, 22; and Start invariant 15. Architecture v3.1.5 now deterministically selects Universal-v2 TSV. Unified ZIP/Native primary requires a newer target-owned Delivery Spec.

### HIGH — migration storage, Unit split ownership and order parity were incomplete

- **Received behavior:** `MIGRATION_PLAN`, tombstones and deactivate concepts had no storage boundary; `(example_id, order)` was required to remain equal even when an authorized reorder/reduction necessarily changes order; Unit split did not define owner-prefixed Example ID handling.
- **Architecture evidence:** only `metadata.retired_example_ids` exists canonically (`LEARNING-UNIT-SCHEMA.json:135-142`); previous-snapshot validator rejects Example owner change (`validate_content.py:266-283`); order is always contiguous (`validate_content.py:519-522`).
- **Why it mattered:** an agent could invent forbidden canonical fields, silently move an Example ID to a new Unit, or report a legitimate authorized reorder as parity failure.
- **Real failure:** moving `ARCH-0004-ex-002` to `ARCH-0011` under its old ID violates both owner pattern and identity comparison.
- **Regression/common:** v3.1.9 remediation was partial as received; the underlying Architecture intentionally does not define Unit/Sense tombstone storage.
- **Applied patch:** external input/output-hash-bound Plan, exact operation structures, full retirement archives, scoped Sense identity, explicit old→new Example migration for cross-Unit split/merge, and before/after order mappings. Transport parity is now against the post-migration Canonical snapshot.

### HIGH — Sidecar requirements invented target fields and conflicted with the supplied builder

- **Received behavior:** required a generic `primary_data_file.*`, delivery target/format, contract and profile fields in BUILD-METADATA although the target Spec defines eight different fields.
- **Architecture evidence:** `Architecture/01-CORE/FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md:139-156`; builder emits those fields and stamps its bundled Prompt version.
- **Why it mattered:** an otherwise valid official TSV could be blocked or receive target-unknown fields. The Architecture package itself also contains historical `prompt_version` literals v3.1.4 and v3.1.5.
- **Real failure:** official builder output would fail the received Prompt’s extra Sidecar minimum despite passing the official Delivery validator.
- **Regression/common:** v3.1.8/v3.1.9 delivery-layer issue plus a shared Architecture provenance inconsistency.
- **Applied patch:** exact target-owned field contract; extra provenance moved to `RUN-METADATA`; generated Sidecar `prompt_version` is corrected to v3.1.9 and delivery validation reruns, without changing the Architecture builder or TSV hash.

### MEDIUM — Sense identity scope and Profile order semantics were underspecified

- **Received behavior:** could be read as globally unique Sense IDs and as allowing order gaps if a Profile permits them.
- **Architecture evidence:** Sense references are Unit-local; Profile v2.1 has no gap policy; validator always requires `1..N`.
- **Applied patch:** Sense identity is `(unit_id, sense_id)`; v3.1.5 order is always contiguous; future exceptions require an actual future Schema/Profile field.

### Architecture package inconsistencies contained by the current entrypoint

The Architecture package is internally hash-consistent and its executable validation suite passes. Two documentation/provenance ambiguities remain in the unchanged Architecture payload:

1. its internal Master requests `prompt_version=v3.1.4`, while Delivery Spec/builder use v3.1.5;
2. README shorthand says “Canonical PASS = CONTENT_VALIDATED”, while `validate_content.py` correctly reports `linguistic_status=NOT_RUN` and performs no linguistic audit.

Prompt v3.1.9 resolves both without changing semantic Architecture: actual producer provenance is v3.1.9, and `CONTENT_VALIDATED` requires structural + claim/evidence + explicit Linguistic PASS. These are not remaining blockers when the documented Kit entrypoint is used.

## Previous Finding matrix

| Previous Finding | v3.1.9 Status | FIXED / PARTIAL / NOT FIXED | Evidence |
|---|---|---|---|
| Unknown optional field preservation | Declared extensions preserved in place; closed-schema unknown value preserved externally and blocks finality | FIXED after audit patch | Master §§2.1, 14 |
| Deterministic `MIGRATION_PLAN` | Exact required keys, typed representations, authorization, input/output hashes, allocator state, rollback and archive binding | FIXED after audit patch | Master §4 |
| split / merge / retire / reactivate | Sense-vs-Unit operations and owner-changing Example migration are explicit; tombstones stay external | FIXED after audit patch | Master §4 |
| Example count `5→8` and `8→5` | Enforcement semantics defined; increase appends delta; decrease uses full archive + retired IDs | FIXED after audit patch | Master §8; Red-Team results |
| `(example_id, order)` parity | Stable unless authorized Plan changes it; Delivery equals post-migration Canonical | FIXED after audit patch | Master §§4, 16, 19 |
| Stable Unit / Sense / Example IDs | Edits/reorder preserve IDs; structural owner migration is mapped, never silent; Sense scope clarified | FIXED | Master §§4, 10 |
| live-runtime preflight before Import advice | Same artifact hash + import mode + actual Runtime preflight required | FIXED | Start 21; Master §20 |
| required capabilities only from Contract + Dataset features | Target only negotiates; it cannot shape/downgrade requirements | FIXED | Master §18.2 |
| `compatible_base_contract` contract-owned + validator-verified | Producer assertion/semver inference forbidden | FIXED | Master §18.2 |
| BUILD-METADATA / Sidecar schema | Bound to exact target-owned field contract; v3.1.5 eight fields | FIXED after audit patch | Master §18.6; Delivery Spec §Provenance sidecar |
| TSV `MAPPING-LIMITATIONS` | Audit JSON contract defined; official TSV records PASS_WITH_CANONICAL_BACKSTOP | FIXED | Master §§18.5, 19.3 |
| validator evidence `input_sha256` | Exact validator artifact/input/execution binding required; stale hash satisfies no gate | FIXED | Master §22 |
| Formal status state machine | Orthogonal five-component vector + fixed roll-ups; external reporting scope | FIXED | Master §21 |
| architecture vs semantic contract versions | Provenance roles remain independent; current Contract resolved from Contract file | FIXED | Start 14-16; Master §§2.1, 18.2 |
| DE↔FA↔EN under Stable Example ID | Translation requiredness remains Profile-driven; alignment remains one Example unit | FIXED | Start 20; Master §9; Contract §§4-5 |
| `CONTENT_VALIDATED` only after Linguistic PASS | Explicit hard implication, not inferred from structural validator | FIXED | Master §§15-16, 21 |
| Unified ZIP exactly one primary | Enforced whenever a target-owned Spec authorizes an Import ZIP; not misapplied to the Production Kit wrapper | FIXED | Master §§18.3, 19.2, 22 |

## Architecture cross-check

| Area | Result | Evidence / reasoning |
|---|---|---|
| Canonical Schema | PASS | No extra canonical top-level or nested workflow fields; closed unknowns block |
| Dataset Profiles | PASS | Count enforcement uses exact/range/advisory semantics; no invented gap/derived/migration profile field |
| Type Rules | PASS | Only declared core/details fields emitted; all shipped Type Rules passed the operational suite |
| Stable IDs | PASS | Global Unit/Example uniqueness and Unit-scoped Sense identity match validator behavior |
| Status fields | PASS | State vector and migration/status data are external Audit reporting, not canonical or Runtime-evidence fields |
| Source policy | PASS | Derived Units require explicit authorization and still pass normal source/claim gates |
| Canonical truth | PASS | Native Canonical JSON remains semantic source; TSV remains adapter/compatibility transport |
| Delivery | PASS | Official v3.1.5 Universal-v2 TSV path, 23 columns, exact deep `canonical_unit`, exact TSV hash |
| Extra hardening | Allowed | Archives, ledgers, MAPPING-LIMITATIONS and evidence binding are workflow/Audit artifacts; they do not alter Architecture semantics |
| Over-restriction | No production blocker | Unattended destructive migrations are deliberately blocked without full audit data; valid non-destructive canonical content is not rejected beyond Architecture gates |

## Red-Team scenarios

| Scenario | Required final behavior | Deterministic? | Executed result |
|---|---|---:|---|
| 5 examples → 8 | For exact desired 8, preserve five objects/IDs and append exactly three owner-valid IDs, orders 6..8 | Yes | Structural PASS; old objects byte/value-equal in test model |
| 8 → 5 | Authorized input-bound Plan; retain/deactivate/order map; full archive; retired IDs; Canonical + archive lossless | Yes | Structural PASS with three retired IDs and archive hash |
| reorder examples | Keep IDs; explicit before/after order map; final 1..N; transport equals new Canonical | Yes | Structural PASS |
| edit German Example | Edit text under same ID/order | Yes | Structural PASS; ID preserved |
| edit FA/EN translation | Edit translation inside same Example object/ID | Yes | Structural PASS; ID preserved |
| split multi-sense source record | Named Unit survivor; new Unit ID; moved Example old ID retired/archived and new owner-valid ID allocated | Yes | Structural PASS with explicit `ARCH-0004-ex-002 → ARCH-0011-ex-001` mapping |
| merge two Senses | Explicit Sense survivor; external tombstone; reference remap; same-Unit Example IDs preserved | Yes | Structural PASS |
| retire/reactivate Sense | External tombstone/archive; no dangling refs; same scoped Sense ID only with explicit policy; retired Example IDs never reused | Yes | Unauthorized path = REVIEW_REQUIRED/no mutation |
| unknown optional field | Closed canonical scope rejects it; external ledger preserves exact source value; no CONTENT_VALIDATED | Yes | `EXAMPLE_FIELD_UNKNOWN` observed |
| unknown required capability | Reject invented or unsupported requirement; no compatibility/import claim | Yes | CONFIGURATION_BLOCKED/REVIEW_REQUIRED |
| Prompt version new, Contract fixed | Change producer provenance only; Contract remains 3.1.3 | Yes | Decoupled |
| Architecture package new, Contract fixed | Change package provenance only; Contract remains resolved 3.1.3 | Yes | Decoupled |
| ZIP with two importable datasets | Reject before Runtime mutation | Yes | Scanner found 2; fail-closed path PASS |
| stale validator report | Hash mismatch satisfies no gate | Yes | Binding mismatch observed |
| Linguistic FAILED, Transport PASS | TRANSPORT_VALIDATED may remain true; CONTENT_VALIDATED false; failure visible | Yes | State-vector outcome verified |
| isolated PASS, no actual reload | At most APP_COMPATIBLE; CURRENT_RUNTIME_NOT_VERIFIED; no IMPORT_VERIFIED/import-now advice | Yes | State-vector outcome verified |

Machine-readable details: `Verification/RED-TEAM-RESULTS.json`.

## Final invariant matrix

| Invariant | Final v3.1.9 + Architecture v3.1.5 | Regression? | Evidence |
|---|---|---:|---|
| Configuration fail-closed | Missing/conflicting authority blocks production | No | Master §1 |
| Source preservation | Keep-good/fix-bad/fill-missing; unknown values ledgered without schema violation | No | Master §§13-14 |
| Stable Unit IDs | Preserve except explicit structural mapping | No | Master §4 |
| Stable Sense IDs | Preserve `(unit_id,sense_id)` except explicit mapping | No | Master §4 |
| Stable Example IDs | Preserve edit/reorder; owner migration requires retire/new mapping | No | Master §§4,10 |
| Dynamic `examples[]` | Count only from Profile; Schema remains unbounded array | No | Contract §4; Master §8 |
| Count migration | Enforcement-aware, archived and deterministic | No | Master §8 |
| Multilingual alignment | DE anchor with Profile-required FA/EN under same ID | No | Master §9 |
| Claim-level evidence | Dedicated claims such as Rektion remain gated | No | Master §13 |
| Linguistic gate | Required for CONTENT_VALIDATED | No | Master §§15-16,21 |
| Derived-unit authorization | No silent growth; no invented Profile field | No | Master §7 / Binding Profile |
| Canonical source of truth | Canonical JSON remains truth; TSV is transport | No | Master §§18.1,18.5 |
| Delivery losslessness | Exact deep `canonical_unit` plus parity and mapping report | No | Delivery Spec; Master §§18-19 |
| Runtime decoupling | Producer/package versions are not compatibility gates | No | Master §18.2 |
| Status truthfulness | Orthogonal vector; no cross-axis implication | No | Master §21 |
| ZIP ambiguity prevention | Exactly one importable primary when ZIP is authorized | No | Master §19.2 |
| Post-package verification | Reopen/extract, inventory, hashes and type-correct validators rerun | No | Master §22 |

## Independent execution results

- Architecture supplied manifest: 66/66 payload files independently matched size and SHA-256.
- JSON Schema meta-validation: 6 schemas and 19 instances, Draft 2020-12, PASS with `jsonschema 4.26.0`.
- Architecture tests: 64 run, 64 PASS.
- Canonical fixture: structural/type/source-policy PASS, 10 Units, 22 Examples; `linguistic_status=NOT_RUN` was preserved and was **not** promoted to CONTENT_VALIDATED.
- Universal-v2 build: 10 rows; delivery validator PASS; exact TSV hash matched BUILD-METADATA after producer provenance was changed to v3.1.9.
- Red-Team: 16/16 expected outcomes PASS.
- Prompt static Architecture cross-check: 25/25 PASS.

## Final answer

**Yes. After the audit patches recorded above, Prompt v3.1.9 together with German Language Content Architecture v3.1.5 is READY for large unattended production batches.**

Use only the documented entrypoint. Do not treat the Production Kit wrapper as a Flashcards data-import ZIP, and do not treat its package verification as linguistic or current-Runtime evidence for a future Dataset.
