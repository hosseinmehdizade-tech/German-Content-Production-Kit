# OP-02 — Stage4→Stage5 teaching_delta lossless-projection contract v0.1

**Status: NONACTIVE_VERSIONED_DRY_RUN / PROPOSAL ONLY — 2026-10-29.**

**Code:** Verification/validate_stage45_teaching_delta_parity.py.
**Synthetic tests:** Verification/tests-v3.3.6/test_stage45_teaching_delta_parity.py.
**Existing authorities remain active:** Prompt/ACTIVE-PROMPT.txt,
Prompt/LEXICAL-KOMBINATIONEN-ENRICHMENT-POLICY-v1.0.0.md,
Prompt/KOMBINATIONEN-DIDACTIC-MEHRWERT-GATE-v1.0.0.md,
LINGUISTIC-QA-AUTHORITY-POLICY.json and all current Stage4–Stage7 rules.

No active prompt, import writer, package format, runtime, UI or protected
content is changed by this proposed compatibility gate.

## Gap

The current Tools/build_clean_delivery.py verifies the neutral TSV card
envelope, import projection validator, packaging intent, hashes and optional
local applied-edit proof; it is **not a per-item Stage4→Stage5 pedagogical
lineage checker**. The active lexical policy requires retaining backend
Kombinationen type and provenance, while the 2026-10-26 added-value overlay
requires a justified teaching_delta for any retained candidate and independent
Stage4 review. A deterministic semantic-loss check can prevent omissions in
Stage5, but it cannot decide whether German expressions are genuinely useful.

The historical 2026-10-18 Menschen A2-L24 Stage4 archive contains 64 visible
combinations with 0 explicit item-level teaching_delta and 2 missing
provenance fields. Those observations are **read-only historical regressions**
and DO NOT mean that historical content violated a later prospective policy.
The prior 64-item shadow report is preserved unchanged in Library.

## Opt-in sidecar and precise byte universe

Four independent inputs are required:

1. External nonactive sidecar with schema
   gcpk-stage45-teaching-delta-parity@1 and status
   NONACTIVE_VERSIONED_DRY_RUN; exact SHA256 for Stage4 JSON bytes,
   Stage4 AI linguistic review-receipt bytes and Stage5 direct import TSV
   bytes; plus a registered source-authority SHA256.
2. Stage4 JSON: source_authority_sha256 + ordered cards array. Each lexical
   card carries stable id, semantic category, combination_disposition,
   kombinationen (ordered array), and optionally combination_close_reason.
3. Stage4 separately stored AI review receipt: exact reviewed Stage4 SHA256
   and source SHA256, explicit FULL exact-content coverage, distinct authoring
   and independent challenge methods, risk_queue_open=0, card count, and
   **one KEEP_WITH_REASON reviewed hash for each displayed combination**.
4. Stage5 direct import TSV: id, front, back, card_type, category,
   custom_fields columns. custom_fields is strict JSON and contains
   presentation_contract gfp-vocabulary-neutral@1 and an ordered
   kombinationen array. Each item object must match the exact Stage4 item
   object, including DE/FA/EN, kind, provenance, teaching_delta and other
   backend metadata.

These fields are a *proposed future adapter profile*, not a declaration that
all historical/current workstreams already use the JSON shape or store each
metadata field inside current TSV custom_fields. A future adoption needs a
versioned, exact-authority crosswalk without rewriting old data.

## Deterministic enforcement

- SHA256 of all three supplied files must equal independent sidecar hashes.
  Source authority identity and Stage4 review's source hash must match.
- Full card-ID universe and order must be preserved. Extra, missing,
  duplicate, reordered or untracked cards block this dry-run.
- Every visible Kombination has stable item_id, DE/FA/EN translations,
  internal kind, an honestly typed provenance and an explicit teaching_delta
  with recognized benefit kind and a nonempty explanation.
- REGISTERED_SOURCE/SOURCE_EXACT/SOURCE_ATTESTED require named source ID,
  locator and source digest **as recorded claims**. That is not independent
  original-source byte verification. PARENT_GENERATED_EXAMPLE may not claim
  a registered source locator.
- Every displayed item must have exactly one matching Stage4 reviewed
  disposition with unchanged SHA256 and explicit KEEP_WITH_REASON. Missing,
  stale or phantom dispositions block the parity result.
- Stage5's ordered combination objects must equal Stage4 exactly. Dropping
  teaching_delta, type, provenance, Persian/English translation or a whole
  item, even while preserving the front text or count, is a failure.
- A card with no useful combinations is valid if combination_disposition is
  CLOSED_NO_FORCE and the reason is nonempty. **No fixed number** per card
  is enforced. This preserves the active policy and prevents filler.
- Neutral card_type de-vocabulary and
  presentation_contract gfp-vocabulary-neutral@1 are preserved; the active
  Flashcards UI retains its existing learner-visible **Kombinationen**
  section. No redesign or new user-facing taxonomy is authorized.

## Status semantics and non-claims

PASS_SCOPED_DETERMINISTIC_PARITY_ONLY means the tested byte snapshots,
claimed Stage4 review receipt and exact Stage5 custom_fields obey this
prospective transformation profile. It **does not** substantiate the
linguistic quality or independent origin of that review; an invented review
receipt could meet the structural schema. The full AI adversarial review
must separately challenge meaning, morphology, valency, register, source
fidelity, translations, redundancy and actual learner benefit.

The test does not call the production Stage5 builder, materialize real work
stream CURRENT data, test actual source extraction, prove the importer
interprets every nested field, render v486-R120 in a live browser, or approve
Stage6/Stage7. Those remain separate mandatory acceptance gates.

The gate currently runs **only** with synthetic fixtures on Ubuntu/Windows
and uses no private user source material in Git. All old ZIPs, LOCKED parent
content, source manuscripts, workstream LATEST, Library archive records and
the app/current UI stay unchanged.

Production integration requires separate explicit user authorization for
writer/schema change, newest exact source/CURRENT resolution, preserved
original backup, Git/Library CAS, reversible rollout, independent review
and established Stage5–7 regression/acceptance. Do not enable this profile
automatically or treat a bare "ادامه بده" as permission for content migration.
