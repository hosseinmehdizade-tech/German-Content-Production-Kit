# Bounded Menschen Verben repair — acceptance report

Started 2026-10-03; acceptance recorded 2026-10-04. A1 and A2 are RELOCKED for this bounded repair. B1 is CANDIDATE/BLOCKED because a required CURRENT Wortnetz presentation assertion fails. AUD-003, AUD-004 and AUD-005 are closed; AUD-006 transport is repaired but full learner-visible closure remains open.

**A. Starting authority**

Both repositories used `main`. App starting/fetched HEAD: `32659a6eda14851f8443a14a0781708c3c13e030`; untracked `06-Runtime/` preserved. Content kit starting HEAD: `cab6ae364b7dc24f724bc7eb684959d722d4ffa4`; first fetched remote: `268b434e273fb0f39a0fb4ffd90131fcd3d3675c`, fast-forwarded cleanly. Before persistence it advanced to `3867ecb56d0a854cbd51d349bc980ddc68854d13`; those parallel NVV/AberHallo/Memrise changes were fast-forwarded and preserved. No app source change.

Framework v3.3.6 exact portable SHA: `61ecccdd1ae0819ae7e15b5d3335bc576dcb896a393765c257687b900ec3915c`. CURRENT resolved again at acceptance: v455-R89, ZIP SHA `d571005eee6a5445d31569ed55c106ac754a42ba1736bad978c26d152e9bae2e`, 3,334,128 bytes, entry SHA `9d3d7f2e7e6a8d45b14900595e6415d3fa6f7c643db30ddbc21e9e85d3ee2d07`. LAST_FULLY_VERIFIED remains v451-R85.

**B. Immutable parents**

| Level | Supplied filename | SHA-256 | Bytes |
|---|---|---|---:|
| A1 | German-Flashcards-Pro-v451-R85-Menschen-A1-Verben-v3.3.6-Repair2-RELOCKED (1).zip | `6b00aa750b182403bc6cd0cb33d45feca354d811501833cb9fa0960f1af4956c` | 4431550 |
| A2 | German-Flashcards-Pro-v451-R85-Menschen-A2-Verben-v3.3.6-Repair2-RELOCKED (1).zip | `6fc8ce3de42c3914856c8e4225a1c1b842aa7d7379b1e7a3c8707ab862a19366` | 4120910 |
| B1 | German-Flashcards-Pro-v451-R85-Menschen-B1-Verben-v3.3.6-RELOCKED (1).zip | `ed2d61a01abcbc27791c80519a4bccefa0325a008fc5ebbf3e1042739a523c57` | 5232381 |

Original Downloads files remain byte-identical. The `(1)` suffix belongs to the supplied filename; hashes resolve authority without name substitution.

**C. AUD-003 — CLOSED**

| A1 ID | Verb | Visible before | After |
|---|---|---|---|
| ma1m-lu-0308 | kosten | haben gekostet | hat gekostet |
| ma1m-lu-0335 | helfen | haben geholfen | hat geholfen |
| ma1m-lu-0339 | brauchen | haben gebraucht | hat gebraucht |
| ma1m-lu-0340 | finden | haben gefunden | hat gefunden |
| ma1m-lu-0341 | sagen | haben gesagt | hat gesagt |

Owner: explicit canonical `lexemes[].morphology.perfect` and matching `senses[].structure.morphology.perfect`; ten absent leaves added. Stage5 mirrors `custom_fields.perfect`, `canonical_lexeme.morphology.perfect`, `canonical_target.structure.morphology.perfect`, `vnext_morphology.perfect`, `vnext_structure.morphology.perfect`. Canonical hash references rebound on all 310 cards and dependent closure/matrix/ledger. All 247 Verb fronts pass; other 242 morphology outputs unchanged. Raw source, Präteritum, meanings, examples, translations, relations and IDs unchanged.

**D. AUD-004 — CLOSED**

| Occurrence | Exact raw before | Exact raw after | Attested locator |
|---|---|---|---|
| ma2-occ-0070-01 | faszinieren [+A], fasziniert, hat fasziniert | faszinieren [+A], faszinierte, hat fasziniert | source order 70; screenshot 03; row 11 |
| ma2-occ-0154-01 | abschmecken [+A], schmeckt ab, hat abgeschmeckt | abschmecken [+A], schmeckte ab, hat abgeschmeckt | source order 154; screenshot 06; row 17 |

Exact audit images were recovered, visually inspected and matched the registered source manifest: `A2-source-03.png`, SHA `992ae7ab387fc3a06820220b3adf443a10d3cee50c06f71fd31215f7ef315db7`; `A2-source-06.png`, SHA `6cd3121852d1386ba1ade5ac8d4127c805bba4c65e2b627b2af59d8ff8119ee7`. Both stay unchanged. Immutable binding receipt SHA: `dc434393d10d36a9cae86dc510a1b8d9972474ec057e0daec1985f1b1dbfceda`.

Only two `occurrences[].raw_text` leaves changed. Occurrence IDs, 336 ledger dispositions, source order closure, provenance and normalized morphology remain unchanged. A2 canonical JSON and TSV retain exact parent bytes. Dependent occurrence/binding hashes, closure/matrix identity and package checksums refreshed.

**E. AUD-005 — CLOSED**

B1 generated duplicate definition notes: 395 before, 0 after. Only top-level transport `notes` changed to empty on those 395 stable IDs; each original note equaled its definition. All 395 definitions remain in canonical/custom authority and render on CURRENT. No legitimate distinct note was removed. Existing duplicate-note gate passed Stage5 and exact packaged TSV. Renderer suppression unchanged.

**F. AUD-006 — PARTIAL / PRESENTATION BLOCKED**

`mb1m-lu-0200` transport `related` and `details[title=Synonyme].items`: `[nachdenken, nachdenken, nachsinnen]` → `[nachdenken, nachsinnen]`; surface count 3 → 2. Canonical relation records remain 2,526 → 2,526; vnext groups 1,446 → 1,446 with 2,526 items. B1 canonical JSON and every custom_fields object remain exact parent bytes/semantics. Distinct target-backed and value-only synonym IDs/scopes are retained.

Required actual Word Details/Wortnetz check reveals two visible “nachdenken” values despite clean transport: one target-backed node and one value-only chip. CURRENT `relationItems()` keys by type + target_id + title, so preserved canonical records remain separate display rows. “nachsinnen” remains. B1 Study currently exposes only English in its details panel; this was recorded rather than treated as proof of relation display. See `B1-PRESENTATION-BLOCKER.json` and `RELATION-PRESENTATION-ACCEPTANCE.json`. No canonical evidence was deleted to force a display PASS, and no runtime architecture/UI work was added. Full AUD-006 closure is not claimed.

**G. Deterministic differential**

Full explicit leaves/IDs/before/after values: `A1-DIFFERENTIAL.json`, `A2-DIFFERENTIAL.json`, `B1-DIFFERENTIAL.json`. A1: ten canonical perfect additions, 25 projection leaves on five semantic IDs, 310 dependent canonical-hash leaves. A2: two occurrence raw leaves, zero canonical/TSV changes. B1: 395 note leaves and two transport relation display columns on mb1m-lu-0200; zero canonical/custom authority changes. All stable ID sets and row order unchanged. Unknown fields, source membership/audio/provenance, examples, relation authority and explicitly excluded STYLE/UNCERTAIN records compare equal. Legitimate A1 schaffen and A2 hängen identities stay distinct. Unexpected content changes: NONE. The additional runtime finding is separately recorded.

**H. Gates and adversarial fixtures**

Updated `Verification/prevention_preflight.py` uses the new bounded finite-perfect/display gate and accepts the parent-established A1 split authority without schema homogenization. New `Verification/bounded_content_preflight.py` validates controlled haben→hat / sein→ist heads, explicit bridge agreement, identical display strings and pinned raw transcription/image/locator binding. It never applies a universal haben rule or deletes structured relation records.

Exact executed commands and results are in `GATE-RESULTS.json` and `INDEPENDENT-POSTPACKAGE-REAUDIT.json`. Reproduction from original workspace root:

```text
python -B Content-Repair-2026-10-03/run_gates.py
python -B German-Content-Production-Kit/Verification/test_prevention_preflight.py
python -B German-Content-Production-Kit/Verification/bounded_content_preflight.py self-test
python -B Content-Repair-2026-10-03/reaudit_packages.py
node German-Flashcards-Pro/03-Tests/test-aud001-aud002-exact.cjs Content-Repair-2026-10-03 Content-Repair-2026-10-03/runtime/GFP-v455-R89
node Content-Repair-2026-10-03/runtime_content_reaudit.cjs
node Content-Repair-2026-10-03/relation_view.cjs
```

Five official v3.3.6 validators per level: source occurrences, identity closure, enrichment candidates, completeness and neutral projection — PASS before packaging and on fresh extraction. Current memory/checkpoint/projection/lineage/package and app currentness/prevention gates passed. New bounded self-test: six rejecting fixtures (nonfinite/mismatched sein, repeated related, repeated Synonyme, changed raw text, moved locator), plus valid sein and distinct structured scope positives. Existing prevention suite: 23 tests PASS, including split authority loss rejection and finite-perfect/display regression. Existing AUD001/AUD002 exact suite rejects lost protected fields, mutable provenance mismatches and absent translation/stable-ID nodes. These are contractual checks, not exhaustive linguistic certification.

**I. CURRENT runtime acceptance**

Exact v455-R89 bytes; real Chrome, localhost HTTP and isolated IndexedDB profiles. All three actual ZIP imports, exact counts, VERIFIED commit/reload, native Study flip/reveal, DE/FA/EN toggles, example pagination and cross-card reset passed. All 3,988 trilingual groups checked in actual DOM. Actual default UI Content Package export and clean-profile reimport preserve every protected custom authority field and bound per-card lineage. AUD-001 and AUD-002 remain CLOSED / REGRESSION PASS.

All 754 Verb fronts structurally pass, 997 definitions visible, zero unintended notes/internal tokens/literal REKTION on Study, neutral Verb/Expression geometry consistent across levels. Search and full editor open/cancel pass. Relation presentation samples A1 helfen and A2 abschmecken pass; B1 Wortnetz synonym uniqueness fails as described in F. No user library edited by these isolated tests.

**J. Successor artifacts**

| Level | Filename | SHA-256 | Bytes | Status |
|---|---|---|---:|---|
| A1 | Menschen-A1-Verben-v3.3.6-Repair3-GFP-v455-RELOCKED.zip | `99d1f27d1beb91a69c2160ba2e7f2accf364779017cb346f39a9843c28a034dd` | 802281 | RELOCKED_BOUNDED_CONTENT_REPAIR |
| A2 | Menschen-A2-Verben-v3.3.6-Repair3-GFP-v455-RELOCKED.zip | `30abc51f98762e6b47d8e2b3bea7e99d629f84c7a5c4bcf3f3d4234e3d84bc84` | 610180 | RELOCKED_BOUNDED_CONTENT_REPAIR |
| B1 | Menschen-B1-Verben-v3.3.6-Repair2-GFP-v455-CANDIDATE.zip | `588f0ef9ef81668383c7186936472584f1063bccb5a888c8ff75a9526343261a` | 1422286 | CANDIDATE_BLOCKED_AUD006_RUNTIME_PRESENTATION |

A1/A2 Repair3 follows their Repair2→Repair3 workstream successor policy. B1 Repair2 follows its relocked Repair1 lineage. A1/A2 accepted names are byte-identical copies of the exact tested candidates; no repackaging after acceptance. Embedded package CANDIDATE control is the immutable build snapshot; final bounded content status comes from this external acceptance sidecar. Runtime overall release finality remains separate. Portable ZIPs contain content and self-checking lineage/control, without obsolete bundled v451 runtime. ZIPs remain outside Git.

**K. Inventory parity**

| Level | Cards | Verb | Expression | Example groups | Canonical relations | vnext groups/items | Audio occurrences |
|---|---:|---:|---:|---:|---:|---|---:|
| A1 | 310 | 247 | 63 | 1240 | 768 | 732/768 | 310 |
| A2 | 292 | 228 | 64 | 1168 | 1205 | 930/1205 | 0 |
| B1 | 395 | 279 | 116 | 1580 | 2526 | 1446/2526 | 439 |

All counts unchanged. B1 zero-audio IDs mb1m-lu-0030 and mb1m-lu-0363 remain zero. A1/A2 inherited audio authority preserved; no fabricated/relinked audio.

**L. Exact package verification**

Independent direct original-ZIP versus successor-ZIP re-audit restored only whitelisted deltas and compared all other content fields. Fresh extraction reran official gates, projection, lineage and hygiene. Full SHA256SUMS coverage: A1 17 files, A2 16 files, B1 15 files. All JSON parsed, native BUILD-METADATA TSV hashes and manifest roles/canonical hashes match. Zero duplicate ZIP members, malformed checksums, caches/pyc/temp/junk, stale old repair evidence or nested obsolete runtime releases. Outer SHA verified before exact import and again under final accepted filenames. Package checks PASS for all three; B1 runtime presentation still blocks relock.

**M. Project memory**

Added CP-MEM-007 for finite principal-form correctness beyond slot nonemptiness; CP-MEM-008 for attested raw evidence separated from normalization with pinned binding. Linked AUD-005 evidence to existing CP-MEM-003 without rewriting its sealed decision. AUD-006 and native Wortnetz behavior remain local checkpoint evidence. Existing memory seals, independent audit evidence and concurrent NVV memory preserved. Gates explicitly state their controlled/attested scope and the remaining human/source/runtime boundaries.

**N. Git persistence**

Compact content checkpoint, artifact identities, deterministic differentials, small acceptance summaries, replay scripts and prevention/memory updates are staged for content Git sync. ZIPs/screenshots/large authority/runtime test dumps stay outside Git. App source and app remote remain unchanged at `32659a6eda14851f8443a14a0781708c3c13e030`. Actual content commit/remote verification receipt is recorded in `GIT-PERSISTENCE.json` after sync; until then persistence is PENDING.

**O. Unexecuted / blocked boundaries**

B1 final/relocked status and full AUD-006 closure are BLOCKED by measured CURRENT Wortnetz duplicate display. Resolving that native projection requires a separately pinned runtime correction and renewed exact B1 acceptance; a content-only canonical deletion would violate scope/authority preservation. Current runtime v455 overall same-profile/offline/PWA finality remains pending in its existing runtime workstream; this content task does not promote LAST_FULLY_VERIFIED. Exhaustive human linguistic review of all 997 definitions, 3,988 example groups and relation semantics was not performed. Search/editor acceptance used relevant samples and open/cancel; it does not certify every editing workflow. Library upload was not performed; provided local immutable artifacts are the delivery surface.

**P. Finding disposition**

| Finding | Disposition |
|---|---|
| AUD-001 | CLOSED / REGRESSION PASS |
| AUD-002 | CLOSED / REGRESSION PASS |
| AUD-003 | CLOSED — exact five forms and unaffected morphology parity |
| AUD-004 | CLOSED — attested raw strings and immutable source binding |
| AUD-005 | CLOSED — 395→0 redundant notes; 395 definitions preserved |
| AUD-006 | TRANSPORT REPAIRED / RUNTIME PRESENTATION BLOCKED — canonical evidence preserved |

Stop at this durable bounded checkpoint. Do not start another level, broad linguistic cleanup, UI redesign or unrelated workstream. Resume only the recorded B1 presentation blocker when scope permits.

Actual-defect negative replay also passed: all five defective A1 parent perfects rejected; both A2 original raw strings rejected against the attested binding; B1 original 395 duplicate notes plus two display fields rejected (397 findings). Repaired projections accepted. See REGRESSION-NEGATIVE-RESULTS.json.

Visual sample check: native Study screenshots were recaptured after CSS transitions finished and inspected. A1 helfen and A2 abschmecken retain the established card layout, neutral columns and relation sections; B1 native deep-copy Study details retain the observed English-only panel. Wortnetz duplicate remains the explicit B1 blocker. Candidate/package bytes did not change during harness corrections.
