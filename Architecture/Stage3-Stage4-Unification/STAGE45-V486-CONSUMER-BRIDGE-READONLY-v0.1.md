# OP-02 — Exact CURRENT v486-R120 Stage5→consumer compatibility (v0.1)

**Status: NONACTIVE_VERSIONED_DRY_RUN; read-only engineering contract only.**
Date: 2026-10-29. No active format, UI, runtime, writer, card, source or LOCKED mutation.

## Exact authorities inspected

- German-Flashcards-Pro: committed 01-App/index.html, Git blob
  5fa23796853504eb7a2773dec5fe60d188499385, full-file SHA256
  d00c111743eea695e2f5e7a847b0330a0eb74479fd6733396fa062ac222bdeff,
  exact CURRENT v486-R120, not an older build inferred from version labels.
- Content Kit active v3.3.6 prompt and lexical Kombinationen and
  2026-10-26 didactic added-value policy remain unchanged.
- Earlier NONACTIVE Stage45 candidate validator:
  Verification/validate_stage45_teaching_delta_parity.py. It verifies
  custom_fields.kombinationen item equality to Stage4, but is NOT an app
  rendering/importer acceptance test.

## Observed code-level mismatch, NOT a proven bug in existing learner cards

The actual universalRawFromRow converts TSV custom_fields JSON into
customFields. normalizeCard and neutralVocabularyCustomFieldsV451 generally
preserve this unknown semantic data while enforcing the neutral vocabulary
presentation contract. The runtime cold-field strip set does not include
kombinationen or kombinationen_v1, and so these fields may remain in the
runtime compacted card.

However, presentationProjectedDetailsV459 only projects:
  customFields.kombinationen_v1
     .visible_section = "Kombinationen"
     .items = [{de,fa,...},...]

An alias kombinationenV1 also exists, but has precedence implications.
The renderer does NOT read a bare customFields.kombinationen array to create
the visible section. When the supported view envelope exists it displays
DE and FA; English, provenance and teaching_delta remain hidden metadata.

Moreover, a preexisting nonempty details section called "Kombinationen"
overrides the view envelope even if the details are stale. Legacy headings
"Kollokationen" or "NVV" can create competing visible families.

Hence the earlier proposed Stage45 checksum/deep-equality contract could
PASS yet yield no learner-visible Kombinationen in v486. This is a mismatch
in the PROPOSED production profile, not a demonstrated issue on the user's
existing cards or current live IndexedDB state.

## Nonactive compatibility proposal

For future separately authorized lexical Stage5 conversion only:

1. Preserve complete exact ordered Stage4 item objects in
   custom_fields.kombinationen (DE/FA/EN, item ID, kind, provenance,
   teaching_delta and optional source locator).
2. Additionally provide custom_fields.kombinationen_v1 with
   visible_section "Kombinationen" and ordered items deep-equal to the
   same Stage4 objects. Do not silently strip backend evidence.
3. Reject camel/snake alias coexistence, stale older details titled
   "Kombinationen" and competing collocation/NVV sections without
   adjudication. No automatic deletion or UI redesign.
4. Legitimate CLOSED_NO_FORCE with zero items remains valid without any
   visible section; never impose fixed-density filler.
5. Preserve the established single learner-visible section and v486 UI.

The new companion code is Verification/validate_stage45_v486_consumer_bridge.py
and separate synthetic regressions are
Verification/tests-v3.3.6/test_stage45_v486_consumer_bridge.py.
It requires passing the exact prior Stage45 didactic integrity check,
pins runtime identity and exact Stage5 TSV SHA, then rejects missing/altered
view envelopes, stale detail overrides and competing visible families.

Independent exact-code tests in the app repo:
03-Tests/test-op02-stage45-v486-consumer-bridge.cjs extracts actual committed
v486 universalRawFromRow, neutralVocabularyCustomFieldsV451,
presentationProjectedDetailsV459 and compactRuntimeCardInPlaceV425, running
synthetic input through each function with Node vm on Linux and Windows.
These functions are executed, not merely searched for keyword presence.

## Remaining hard boundaries

- Passing a fabricated Stage4 receipt structurally is NOT a real independent
  linguistic/adversarial AI review; original source semantics must be checked.
- No actual Stage5 builder/run-time import or exact populated-library
  IndexedDB save/reload, export/reimport, or full browser DOM was performed
  here. Stage5/6/7 remain separate required acceptance gates.
- This proposal must NOT be enabled in an active writer, importer or UI
  without explicit approval, newest user-authorized currentness, backup,
  actual bytes, CAS and all source and release gates.
- Historical Menschen A2-L24 Stage3C 9aa0... digest remains unresolved.
  No historical ZIP, original source, LOCKED, workstream LATEST or Library
  record is modified by this OP-02 compatibility work.
- OP-01 production Git writer is still DENY_ALL.

This is an optimization-process dossier, NOT a new Flashcards release or
production content successor.
