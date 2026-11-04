# Related Sections — Source-neutral producer and QA contract v1.1.0

**Status:** ACTIVE prospective producer policy (2026-11-04); supersedes only the *operational ambiguity* of v1.0.0, preserving every v1.0 safety rule. Applies to all future **mutable** lexical Stage3 passes in Menschen A1/A2/B1, independent Verben, NVV, generic Vocabulary and other source adapters. This is an OP-01/OP-02 **process optimization**, not authorization to edit any card. Do not silently re-open LOCKED material or change app UI, learner progress, typed graph, Stage4/5/6/7 or framework v3.3.6.

## 1. One evidence/sense decision per learner-visible item

Record `card_id`, registered source and locator, source SHA / source excerpt identity, German surface, exact sense, language/profile where required, role, teaching delta, linked target ID if **already resolved**, and decision in the *existing one-pass Stage3 ledger*. Reuse the same Stage3A/B/C decision for one source fact; no new manual gate. Valid decisions: `VERIFIED_PRESENT`, `CLOSED_NO_FORCE` (explain why no useful relation), `NOT_APPLICABLE`, `HOLD` (specific uncertainty). No quota or compulsory `Verwandte Wörter` content.

Classification order is **not a blind text classifier**. For each candidate ask:

1. Is it an already established **complete sentence or Redemittel** with a legitimate independent expression-card or example profile? Keep that profile, not automatic Beispiel promotion.
2. Is it **concrete reusable** `Kombinationen`/NVV (including useful adjective+noun, verb-object, fixed patterns)? Follow registered source-first v1.2, structured DE/FA/EN and teaching delta; do not turn bare Rektion into phrases.
3. Is it independently evidenced **derivational word family**? `Wortfamilie`; shared spelling, grammatical form or topic is insufficient.
4. Is it **sense-substitutable**? `Synonyme`; a related but nonsubstitutable word is not a synonym, and register differences need recorded scope.
5. Is it an evidenced **sense-specific opposite**? `Antonyme`; do not derive antonymy from `un-` or other prefix heuristics.
6. Is it a **genuine thematic/semantic association** that is none of the above? `Verwandte Wörter`, with non-equivalence clear. Existing `RELATED` edges are retained as-is until a separate authorized evidence-based graph correction.
7. If two roles remain plausible, retain provenance and `HOLD`; never infer type from punctuation, morphological similarity, LLM confidence, or presence of a hyperlink.

A verified `WORD_FAMILY`, `SYNONYM`, `ANTONYM` edge can suggest a section only for an **existing exact target ID** and **exact target surface**. The edge is *evidence to inspect*, not automatic proof of semantically correct type. A freeform family member without target may remain visible after source review; **never invent a graph edge**. Typed Wortnetz relations and learner-facing details remain distinct views of one fact.

## 2. Duplicate and identifier policy

- Before comparing, use only Unicode **NFC** and whitespace collapse for **machine-exact surface**. Do not lower-case, fold `ß` to `ss`, strip punctuation or infer spelling/morphology; these can change meaning. A near-match may be suggested for semantic review but must never be an auto-deletion.
- Compare within the **same card** across visible `Verwandt` / `Verwandte Wörter`, `Wortfamilie`, `Synonyme`, `Antonyme`, `Kombinationen`, `Beispiele`, `Redemittel`, `Rektion`, and accepted backend `kombinationen_v1/v336`. Do not treat the same structured Kombinationen item in two synchronized backend/visible representations as two learner tiles.
- An exactly repeated learner surface in two distinct sections is a **risk signal**. Keep only one visible copy by default *after source/sense verification*. The exception needs an explicit independent didactic benefit, provenance and a Stage4 disposition. Never delete original source, translated example or graph.
- A raw internal `target_id` displayed as German (`ma1m-lu-...` and exact known IDs) is a strong QA defect; do not replace it by a guessed lemma. The link belongs in typed navigation/Wortnetz; the visible lemma requires exact target and independent evidence.
- A full sentence in `Verwandt` is **HOLD/review**, not permission to append it to examples, change the source example set or create translated examples. If it is an independent expression card, keep its target identity and link.
- `Custom` must not absorb known typed sections; this is a **runtime/serializer issue**, separate from content policy. Preserve the user-approved right-side section order (`Verwandte Wörter` after Antonyme, before Formen) without visible UI changes.

## 3. Machine-readable preflight v1.1 (read-only)

`python Verification/audit_related_sections_taxonomy_v1_1.py CURRENT.tsv --output related-advisory.json`

Also accepts an explicitly normalized JSON object `{ "cards": [ { "id": "...", "front": "...", "details": [...], "examples": [...], "canonical_relations": [...] } ] }`. The TSV is the existing import presentation format, **not** a substitute for exact Stage3 canonical evidence. `custom_fields` may carry `canonical_unit`, `canonical_relations`, `kombinationen_v1/v336`. The tool reports file SHA256 and itemwise codes:

- `HIGH` exact structural anomalies: raw internal IDs, cross-tile same-surface duplicates, repeated related members, or contradictory pretyped exact target roles.
- `MEDIUM` *review opportunities*: sentence-like related text or an established exact typed target whose section should be reviewed; never automatic moves.
- malformed JSON, duplicate JSON keys, duplicate IDs or unsafe structures → **error** and no content output.

Default diagnostic **exit 0 despite findings** to avoid false Stage4 approval/block. `--fail-on-high` optionally returns 1 for a *separately opt-in per-workstream* CI preflight; invalid input returns 2. It does not award Stage3C, Stage4, Stage5, Stage6 or Stage7 PASS; no user data or source can be mutated. Exact duplicate/opaque IDs are machine flags; correctness of German meanings, source locators and translations still needs independent risk-based Stage4.

No broad mandatory production CI rollout until each active adapter's schema compatibility, known healthy sample, source SHA, non-empty finding attribution and negative controls are verified. To avoid rebuilding per-card ZIPs, reuse the one-pass ledger + one compact advisory report at reviewable milestones.

## 4. Stage boundary and ownership

- Stage1: preserve raw source and locator; no category inference from OCR or importer.
- Stage2: close source occurrence, sense, stable identity and target ID before any WordFamily graph suggestion.
- Stage3: the **same** one-pass enrichment decision assigns exact didactic role and evidence; invoke the new diagnostic as a nonmutating preflight on the verified projection when available.
- Stage4: independently challenge all CRITICAL/HIGH semantic risks, use active risk-based v1.0.1 deterministic sampling for lower risks and adversarial second-method review. Existing graph type, exact string or a scanner flag never equals linguistic approval.
- Stage5: project approved typed/visible fields without invented type coercions, duplication or translation metadata loss. Test source-vs-projection diff; enforce the existing source-agnostic completeness gate.
- Stage6/7: resolve exact CURRENT app only when integration matters; maintain immutable source, card IDs, Wortnetz/SRS and prior releases. No UI change authorized here.

**Compatibility:** retain v1.0.0 for historic audit replay. The A1 V25 and V25-R1 derived candidates are read-only **fixtures** in the Optimization Program; they are not current or import-ready. The generic QA tool must not call source-specific repair scripts or write any A1/A2/B1/Verben/NVV content workstream `LATEST`/`CHECKPOINT`.