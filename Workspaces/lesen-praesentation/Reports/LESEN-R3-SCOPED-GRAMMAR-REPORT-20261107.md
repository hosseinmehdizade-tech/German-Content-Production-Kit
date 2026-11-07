# Lesen B2–C1 — R3 scoped grammar and DE–FA–EN review (2026-11-07)

**Status:** source-owner R3 **CANDIDATE / HOLD**, not CURRENT, not fully Stage4, not an importable v505 runtime and not FINAL. The immutable v1.3.0 Library ZIP remains authoritative for current portable content (SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`). Parent R2 SHA256 `bbeec4c3823879b5037c3669edbc41f2a441662312887f84a8f0ee9bb2e61549`.

## Real changes against R2

- Added **45 explicit, exact-offset, DE/FA-explained grammar occurrences** in revised sentences of units **035 (17), 051 (18), 059 (10)**.
- Corrected **7 historical annotation problems** in those three units: the false temporal-past explanation for comparative `als es zunächst scheint` in all three; extended the truncated `Wenn digitale Betreuung` annotation to its complete clause; eliminated `wichtiger` falsely tagged as an adjective *declension*; excluded two occurrences of `Damit wird deutlich` falsely tagged as subordinate clauses.
- Removed old 34 unattested R1 spans remain absent; it would be wrong to recreate grammar for words removed from the revised text just to restore a numerical quota.
- The complete master now has **4620 occurrences** (R2 had 4,578). No text, translation, question or vocabulary was changed in R3; **65 other units remained byte-equivalent as their JSON records**, and the 68 unit / 340 question identities remain.
- Nine edited DE/FA/EN sections were read separately for claim parity; scoped AI review found no blocking mismatch. Full independent whole-pack semantic Stage4 was **not** performed. A natural Persian general singular for German plural in unit 035 p04 is noted as a nonliteral-number translation, not silently called exact literal parity.

## Evidence and limitations

- Independent read-only verifier **30/30 PASS**, including 4 adversarial negative cases for malformed offsets, targets, sentences and sections. New ledger identifies all 45 exact spans and 7 corrections. Counts are regenerated from actual JSON, not assumed.
- The historical `reading_fulltext_grammar_v1` generator was **not present in this retrieved source package** and **was not rerun**. R3 is a source-exact curated overlay, **not** exhaustive nine-lens coverage. Source-affected grammar Stage4 remains HOLD, and unreviewed baseline issues are not retroactively resolved.
- No R3 compiled runtime exists. v505 pre-entry PASS from the previous turn applied only to *historical v1.3.0 runtime*, not R3; native browser Stage6 is NOT RUN. No app UI or learner data/FSRS/SRS changed.

## Next bounded outcome

1. Locate/restore the real registered compiler and fulltext derivation implementation, or build a grammar analyzer with independently justified coverage for all changed sentences (not a fake 34-for-34 replacement). Validate label semantics as well as offsets.
2. Run independent adversarial multilingual review on the affected three units and confirm the full 68-unit curated-current consistency; preserve 55 remaining templated lessons as an explicit follow-up queue.
3. Only then build **a separate Lesen Runtime v505 pack** and execute native isolated browser import; maintain original immutable current until actual release acceptance.

**Persisted owner:** `Workspaces/lesen-praesentation`; Library `/Flasch kart/German-Content-Production-Kit/Content/Lesen/Candidates` for candidate; `/Reports`, `/Checkpoints`, `/Tools` for compact QA and source. No report-only ZIP.