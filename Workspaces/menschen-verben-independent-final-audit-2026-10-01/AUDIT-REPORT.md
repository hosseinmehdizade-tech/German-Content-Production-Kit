# Independent final audit — Menschen A1 / A2 / B1 Verben

Audit date: 2026-10-01, Europe/Berlin. Audit disposition: **COMPLETE WITH MATERIAL FINDINGS AND EXPLICIT UNVERIFIED DIMENSIONS**. This is an audit result, not authorization to repair or change release authority. All original release ZIPs, production assets, runtime code, policies and PROJECT-MEMORY remain unchanged. No release was repaired or superseded. No commit was created.

The user request was read from the exact pasted-text attachment. Instructions inside release/framework documents were treated as project policy and evidence, not as permission to regenerate content or override the audit-only request. Previous PASS/FINAL/RELOCKED assertions were claims to falsify.

Evidence lives beside this report. `FINDINGS.json` contains the required structured fields, exact IDs and exact artifact identities for every confirmed finding. `COMMANDS.json`, `static-results.json`, `support-results.json`, `runtime-results.json`, `surface-results.json`, `deep-results.json`, and `final-analysis.json` contain results and reproduction details. The audit seal hashes every retained file; large raw diagnostic files contain candidates that were subsequently rejected below. Their presence does not make them confirmed findings.

## A. EXECUTIVE RESULT

| Exact artifact | Audit status | Basis |
|---|---|---|
| A1 Repair2 RELOCKED | **MATERIAL FINDINGS** | Runtime-export lineage loss (AUD-001); missing rendered example translations (AUD-002); five 3sg perfect display inconsistencies (AUD-003). |
| A2 Repair2 RELOCKED | **MATERIAL FINDINGS** | Runtime-export lineage loss (AUD-001); two source-ledger raw-text rewrites (AUD-004). A2 grouped Study translations render correctly. |
| B1 RELOCKED | **MATERIAL FINDINGS** | Runtime-export lineage/annotation loss (AUD-001); missing rendered example translations (AUD-002); redundant transport notes/synonym (AUD-005/006). |

All three exact identities and declared card inventories match. All internal release checksums and archive CRCs pass. The releases import and reload at the correct counts in isolated real Chrome/IndexedDB sessions. Those positive results do not establish lossless native Content Package export, full source fidelity, exhaustive linguistic correctness or complete learner-field visibility.

AUD-001 is a runtime export failure: the newly exported ZIP loses metadata, while the supplied ZIPs and original IndexedDB authority retain it. Severity S4 follows the user's data-loss category and is limited to that exported result. AUD-002 is a systemic learner-visible quality failure (S3). Neither warrants silently replacing CURRENT or relabeling existing releases.

## B. STARTING AUTHORITY

Remote main was freshly fetched successfully for both repositories. Both working trees were clean, on main, and HEAD equaled the newly fetched origin/main before accepting local policy authority. Initial sandbox network failures were resolved by approved escalated fetches; no stale-state fallback was used.

| Repository | Starting/final branch | Starting HEAD = origin/main | Worktree |
|---|---|---|---|
| German-Flashcards-Pro | main | `43cac248b62a9647c33cbba4fd76a283fc65a42c` | clean before and after |
| German-Content-Production-Kit | main | `6d654429d48595c320f7cc6e69573d62a8086074` | clean before and after |

Mandatory bootstrap/state/memory/operating/safety/Git/currentness/pin files and relevant workstreams were inspected. Saved JSON copies bind this audit to that state. Lessons Learned / Failure Prevention hardening is present: completed upstream hardening commits 056ccdc and df4e593 are followed by synchronized receipt/handoff commits in these starting heads. Memory schemas are `gfp-project-memory@1.0.0` and `gcpk-project-memory@1.0.0`, status ACTIVE_MANDATORY_READ, updated 2026-10-01, with additive `incident-prevention@1.0.0` prevention policy. No memory was overwritten or promoted during this audit.

Resolved framework: **v3.3.6**, entrypoint `Prompt/START-PROMPT-v3.3.6.md`; master `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.3.6.md`, SHA-256 `4cc68b5f42b1e38fd6d8ff9860832eb2bb6e76f85ca31d276724e65f896b1948`. Exact portable framework candidate was independently hashed: `61ecccdd1ae0819ae7e15b5d3335bc576dcb896a393765c257687b900ec3915c`. Semantic contract gfp-german-language-content@3.1.3; presentation policy carried forward from v3.3.5; v3.3.6 source-agnostic completeness remains active.

Resolved CURRENT = LAST_FULLY_VERIFIED = development base = mirror target = **v451-R85**. Exact organized runtime portable filename is `German-Flashcards-Pro-v451-R85-ORGANIZED-DELIVERY-CANDIDATE-CONTROL-CORRECTED.zip`, SHA-256 `27da34ebecde9274aa7323a300aad979325914522460b914139e71f966131be4`, 3,263,186 bytes. Its 298 checksum entries verify. Each supplied release has 71/71 identical 01-App runtime files against both the Git runtime and this portable authority. Historical and current-runtime findings therefore share the same tested bytes; there is no newer-runtime compatibility claim or runtime downgrade.

## C. ARTIFACT IDENTITY TABLE

The supplied local filenames contain **(1)**. These exact files were selected; unnumbered similarly named files were not substituted. The user-stated expected identity is the byte hash, and the (1) filenames match it.

| Release | Exact supplied filename | Calculated SHA-256 = expected SHA-256 | Bytes | Match |
|---|---|---|---:|---|
| A1 | `German-Flashcards-Pro-v451-R85-Menschen-A1-Verben-v3.3.6-Repair2-RELOCKED (1).zip` | `6b00aa750b182403bc6cd0cb33d45feca354d811501833cb9fa0960f1af4956c` | 4,431,550 | YES |
| A2 | `German-Flashcards-Pro-v451-R85-Menschen-A2-Verben-v3.3.6-Repair2-RELOCKED (1).zip` | `6fc8ce3de42c3914856c8e4225a1c1b842aa7d7379b1e7a3c8707ab862a19366` | 4,120,910 | YES |
| B1 | `German-Flashcards-Pro-v451-R85-Menschen-B1-Verben-v3.3.6-RELOCKED (1).zip` | `ed2d61a01abcbc27791c80519a4bccefa0325a008fc5ebbf3e1042739a523c57` | 5,232,381 | YES |

Exact paths used:

- C:\Users\hosse\Downloads\German-Flashcards-Pro-v451-R85-Menschen-A1-Verben-v3.3.6-Repair2-RELOCKED (1).zip
- C:\Users\hosse\Downloads\German-Flashcards-Pro-v451-R85-Menschen-A2-Verben-v3.3.6-Repair2-RELOCKED (1).zip
- C:\Users\hosse\Downloads\German-Flashcards-Pro-v451-R85-Menschen-B1-Verben-v3.3.6-RELOCKED (1).zip

All three original hashes and sizes were checked again after testing; unchanged. ZIP CRC, duplicate-path, traversal, malformed JSON, ragged table, cache/temporary contamination and unexpected zero-length file scans found zero errors. A1 has 377 members /330 files; A2 319 members /319 files; B1 328 members /328 files. SHA256SUMS coverage is all files except the checksum manifest itself: A1 329/329, A2 318/318, B1 327/327 verified. Historical runtime fixtures/tools are part of the organized runtime package; intentional nested IMPORT-READY ZIPs are not stale release contamination.

Nested exact imports actually tested:

| Release | Nested ZIP SHA-256 | Exact inner TSV SHA-256 |
|---|---|---|
| A1 | `f64f9f2a2b5f6e7b9eb708a4855ed4a5d72aef80b8fc160d8e3c3b759f8e3685` | `d46a3dd7aa7294db0970af50e79d45bc6ed075c52a799da932c6aa56b98179f4` |
| A2 | `c53d7188e62d9666f25a2dc8e25094d042a8f18a8543c2a8418636e91c4f7198` | `eddb353208857e5bf84edce8f43c5ff2dcce533dd4533aba09e94b352d83d195` |
| B1 | `f198db975fc68723b92d1327447b3eeacc94c6a1412e7c279abd8fe1481f1f8e` | `1815dfcacf02dc9f08df3f6cad5060db7a46b3c8c7e1bbf3cca8f683972eec3a` |

Inner TSV bytes equal the corresponding outer content TSV. Nested import file paths and members are preserved in static-results.json. Direct import of the entire organized release wrapper was not tested; the documented content import artifact inside it was tested without reconstruction.

## D. INVENTORY TABLE

Counts come from actual TSV rows and canonical/projection payloads, not inherited report totals. Delta is actual minus claim. Example counts below are per language (DE = FA = EN).

| Dimension | A1 claimed → actual (delta) | A2 claimed → actual (delta) | B1 claimed → actual (delta) |
|---|---|---|---|
| Cards | 310 →310 (0) | 292 →292 (0) | 395 →395 (0) |
| Verbs | 247 →247 (0) | 228 →228 (0) | 279 →279 (0) |
| Expressions | 63 →63 (0) | 64 →64 (0) | 116 →116 (0) |
| Examples per DE/FA/EN | packaged 1240 →1240 (0) | 1168 →1168 (0) | 1580 →1580 (0) |
| Canonical relation records | packaged 768 →768 (0) | 1205 →1205 (0) | 2526 →2526 (0) |
| vnext relation groups | packaged 732 →732 (0) | packaged 930 →930 (0) | 1446 →1446 (0) |
| vnext relation items inside groups | 768 | 1205 | 2526 |
| source_audio_refs occurrences | packaged 310 →310 (0) | 0 →0 (0) | 439 →439 (0) |
| Unique audio filenames | 275 | 0 | 400 |

Total 997 cards, 754 Verbs, 243 Expressions, 3988 trilingual example groups /11964 language texts. All 997 card_type values are de-vocabulary. A2's 1205 canonical relations were counted in its projected canonical_relations: its source canonical artifact uses native learning_units and is not the same split relation-file layout as A1/B1. B1's 1446 vnext claim counts relation **groups**, not individual edges: all 2526 records are represented as items. Comparing 2526 to 1446 as if they were the same unit would be a false discrepancy.

## E. SOURCE COMPLETENESS

| Release | Registered packaged occurrences | Dispositions | Accounted active target IDs | Missing occurrence/disposition/active target |
|---|---:|---|---:|---|
| A1 | 312 | 312 ACTIVE | 310 | 0 /0 /0 |
| A2 | 336 | 335 ACTIVE, 1 EXCLUDED | 292 | 0 /0 /0 |
| B1 | 441 | 441 ACTIVE | 395 | 0 /0 /0 |

A1 has two additional active occurrences mapped to existing targets. A2 has 43 additional active occurrences mapped to existing targets and explicit exclusion ma2-occ-0286-00. B1 has 46 additional active occurrences mapped to existing targets; retired polysemy IDs were consolidated into surviving lexical identities rather than retained as duplicate cards. These are occurrence-to-target many-to-one mappings, not duplicate active card IDs. The closure validators verify the full actual ID/disposition sets, not just matching totals.

Independent source reach: A2's 11 actual screenshot image hashes match the current registered manifest. The recovered 297-row raw inventory maps to all 297 source-order values in the 336 occurrence ledger; no missing source order was found. Raw-text comparison found six changed source orders (16,70,130,154,242,272); the tense rewrites at 70/154 were independently confirmed visually against hashed screenshots and are AUD-004. Whitespace, besass→besaß and the explanatory append at 242 are separately recorded, not automatically treated as invented targets. Source images 01,03,06 were visually inspected; a complete independent image-by-image transcription audit was not performed.

B1's exact registered legacy source ZIP was available and verified (`c10633dedfae0820531b03bf57de1ffa37562028131136214329a13cd115ef8a`). Its raw inventory hash is `d44aac790090a59fbcb9e6d921fa9cd2c63e580cfa1669ceb742a2d119298a82`; all 406 legacy RAW-B1 IDs are referenced by current occurrence legacy_source_record_ids. This supports legacy row coverage, not fresh verification of current Memrise row contents or audio. Current B1 registered Memrise CSV hash `52f8bb896f5aa1c8f878aeb0ea74ef07ddbeee75261af89dfb2fcad624fc1222` was not available as exact bytes. A1's locked source snapshot hash `333d3829f078f3ddaf5224fd28548c92ec21db454c2d79b7e302c99a318ee4c9` is declared in the package, but its exact registered raw source was not available for independent byte-to-occurrence comparison. An unrelated local A1 inventory was not substituted.

Thus packaged normalized occurrence/identity closure is verified for all levels. Raw source completeness/order/meaning/audio fidelity beyond these boundaries is **UNVERIFIED**, especially A1/current B1. General German knowledge was not used as source evidence. Existing VERIFIED source ledger labels and enrichment closure dispositions remain production claims unless independently checked here.

## F. STRUCTURAL FINDINGS (severity order)


### AUD-001 — S4 — Runtime Content Package export loses authority metadata (CROSS-LEVEL)

The exported TSV omits all three named top-level custom fields on every card: A1 310, A2 292, B1 395. B1 also omits annotations and provenance from all 1580 canonical_unit example copies. Re-import does not restore them. A2 loses the explicit empty source_audio_refs array; its original audio count remains zero. IDs, counts, primary meanings and separate canonical_examples survive.

**Expected:** Content Package export must hydrate durable authority before serialization and preserve source/audio/membership lineage and canonical annotations.

**Cause/boundary:** index.html lines 3423–3445 intentionally compacts CARDS; buildContentPackageV352 lines 12410–12412 serializes CARDS rather than the rich IndexedDB authority. B1 compactCanonicalUnitV425 removes example annotations/provenance. UI exportContentPackageV352 calls this same builder. Original IndexedDB authority remains intact.

**Packaging:** YES: runtime code already has this behavior in all supplied archives and CURRENT. Original release packaging did not corrupt its input content. The subsequent runtime-created Content Package introduces the loss.

**Detection / earliest gate:** The new audit detects it. Current lineage_errors catches membership/audio removal when explicitly applied, but is not a native ZIP export integration test; it does not deeply compare B1 annotations. Additional-gates.json records its transport-selector conflicts and its A1 baseline false failures. Runtime integration acceptance after compaction/reload, then Stage6 actual export/re-import gate. Confidence: HIGH. Evidence: final-analysis.json package_export, runtime-results.json package_reimport_protected_semantic_parity, *-runtime-export-package.zip, *-export.json and *-package-reimport.json. Exact scope and reproduction are in FINDINGS.json; AUD-001/002 use exhaustive per-level ID lists.

### AUD-002 — S3 — Example translations absent from learner-facing Study renderer (A1/B1)

A1 310 cards /1240 groups and B1 395 cards /1580 groups render four DE rows per card but zero FA/EN translation nodes and zero stable example IDs. Model counts alone still equal four. A2 renders 1168 groups with 2336 FA/EN nodes and stable IDs; first three groups are visible and fourth is paginated.

**Expected:** Study renderer must expose the supplied nested example translations through its supported example-language behavior, without converting grouped examples into unilingual text.

**Cause/boundary:** A1 rich customFields renders 1240 translated groups, while compact cards render zero because presentation_examples is stripped and the split v411 canonical_examples representation is not adapted into grouped presentation. B1 renders zero even with rich fields: its deep-copy canonical_unit and de/fa/en projection groups do not match the grouped text/translations adapter shape. No CSS hiding explanation is needed: the nodes are absent.

**Packaging:** YES: supplied projection/runtime representation interaction predates outer packaging. NO: unchanged production runtime and imported content reproduce it.

**Detection / earliest gate:** Packaged acceptance checks validate data/group counts and selected models without verifying translation-bearing DOM. Audit adds those assertions. Stage5 adapter/presentation closure for each native representation; Stage6 visible rendered translation test. Confidence: HIGH. Evidence: surface-results.json, A1-study-back-dom.json, B1-study-back-dom.json, *-rich-vs-compact-render.json, *-study-render-screenshot.png. Exact scope and reproduction are in FINDINGS.json; AUD-001/002 use exhaustive per-level ID lists.

### AUD-003 — S2 — Inconsistent third-person singular perfect principal part (A1)

Five exact forms are listed in G.

**Expected:** A three-part principal-form display uses matching third-person singular values: kostet/kostete/hat gekostet, etc.

**Cause/boundary:** For these five canonical lexemes, perfect is absent while auxiliary=haben and participle_ii are present. The projection uses auxiliary plus participle without inflecting the auxiliary. Existing slot-presence checks accept the result.

**Packaging:** YES: the five strings are already in the exact TSV projection before runtime import. NO: archived checksums correctly cover the defective projection.

**Detection / earliest gate:** Current morphology gate and packaged defect regression check nonempty slots, so they pass. They do not verify finite-form agreement. Stage3 explicit canonical perfect or Stage5 morphology fallback; Stage6 value/convention check. Confidence: HIGH. Evidence: static-results.json A1 morphology_bridge, A1-native-front-render.json, A1-study-render-screenshot.png, AUDIT-REPORT.md G. Exact scope and reproduction are in FINDINGS.json; AUD-001/002 use exhaustive per-level ID lists.

### AUD-004 — S2 — Source raw evidence rewritten during normalization (A2)

ma2-occ-0070-01 raw_text has fasziniert in place of screenshot faszinierte; ma2-occ-0154-01 has schmeckt ab in place of screenshot schmeckte ab. Exact before/after strings and image hashes are in FINDINGS.json.

**Expected:** Preserve screenshot-attested raw_text exactly; put enriched present and past forms in normalized/canonical morphology.

**Cause/boundary:** The Stage1 source adapter reconstructs raw_text from repaired legacy lineage rather than preserving the screenshot transcription. Both correct present and past forms remain in learner-facing canonical morphology; this is an evidence-fidelity issue, not a wrong A2 learner form.

**Packaging:** YES: occurrence ledger already contains the replacements before outer packaging. NO.

**Detection / earliest gate:** Source/identity/enrichment gates accept a structurally complete VERIFIED occurrence without comparing its raw_text to independently hashed source bytes. All three official gates pass. Stage1 source ingestion; immutable raw-text binding plus explicit normalized_text separation. Confidence: HIGH. Evidence: final-analysis.json raw_source_comparison.A2, source-evidence/A2/A2-source-03.png row11, source-evidence/A2/A2-source-06.png row17. Exact scope and reproduction are in FINDINGS.json; AUD-001/002 use exhaustive per-level ID lists.

### AUD-005 — S1 — Definition duplicated in transport notes (B1)

395/395 notes duplicate their definition. Current static gate rejects all 395. Runtime suppresses the redundant notes section: zero rendered duplicate notes.

**Expected:** Do not copy generated German definition into a separate generated notes field.

**Cause/boundary:** Definition was copied into transport notes before packaging; renderer removes equal text from presentation.

**Packaging:** YES. NO.

**Detection / earliest gate:** Current static projection gate detects it; historical visible-note assertions can pass because the renderer suppresses it. Stage5 projection gate before package relock. Confidence: HIGH. Evidence: gate-09.txt, static-results.json B1 duplicate_definition_notes, B1-runtime-models.json. Exact scope and reproduction are in FINDINGS.json; AUD-001/002 use exhaustive per-level ID lists.

### AUD-006 — S1 — Repeated synonym in transport projection (B1)

related contains [nachdenken, nachdenken, nachsinnen], and the Synonyme projection repeats nachdenken. Renderer and authority exporter deduplicate it. Canonical relation records have distinct identities/scopes; no automatic deletion of canonical relations is warranted.

**Expected:** Do not repeat identical synonym display text on a card.

**Cause/boundary:** Projection flattened two relation records into repeated surface text without deduplicating the display list.

**Packaging:** YES. NO.

**Detection / earliest gate:** Static audit catches it; current generic preflight does not reject duplicate relation surface text. Stage5 relation-to-display projection. Confidence: HIGH. Evidence: static-results.json B1 duplicate_relation_surface, B1-rows.json mb1m-lu-0200, deep-results.json initial_export_differences. Exact scope and reproduction are in FINDINGS.json; AUD-001/002 use exhaustive per-level ID lists.

## G. MORPHOLOGY / VERB-FRONT RESULTS

| Release | Structural three-slot presence | Native production front HTML contains all three values | Linguistic agreement coverage |
|---|---|---|---|
| A1 | 247/247 | 247/247 | Five inconsistent 3sg perfect values; exhaustive lexical correctness unverified |
| A2 | 228/228 | 228/228 | Bridge structure matches all 228; exhaustive lexical correctness unverified |
| B1 | 279/279 | 279/279 | Bridge structure matches all 279; exhaustive lexical correctness unverified |

The x/247, x/228 and x/279 totals verify structural/rendered value availability, not that each value is linguistically correct. A1's 242 direct canonical bridges match; the five fallback values below are visible on the production front. All 754 native front outputs are retained in *-native-front-render.json.

| A1 ID | Verb | Actual visible perfect | Expected 3sg perfect |
|---|---|---|---|
| ma1m-lu-0308 | kosten | haben gekostet | hat gekostet |
| ma1m-lu-0335 | helfen | haben geholfen | hat geholfen |
| ma1m-lu-0339 | brauchen | haben gebraucht | hat gebraucht |
| ma1m-lu-0340 | finden | haben gefunden | hat gefunden |
| ma1m-lu-0341 | sagen | haben gesagt | hat gesagt |

These strings can be grammatical plural forms in a sentence; the defect is mixing a plural/infinitive-form auxiliary with third-person singular principal parts. It is not a claim that every use of haben geholfen is ungrammatical. External lexical corroboration: [Duden helfen conjugation](https://www.duden.de/konjugation/helfen), [brauchen](https://www.duden.de/konjugation/brauchen), [finden](https://www.duden.de/konjugation/finden), [sagen](https://www.duden.de/konjugation/sagen), [kosten (betragen)](https://www.duden.de/rechtschreibung/kosten_betragen).

## H. LEAKAGE RESULTS

For the defined token scans over actual learner-facing front/detail/example projections and Study HTML on all 997 cards: literal unintended REKTION=0; known internal role tokens=0; known schema tokens=0; confirmed placeholders=0; learner-visible presentation-selector text=0; confirmed debug text=0. The label **Rektion** plus actual governed patterns is legitimate. A scan hit on “previously unknown” in a B1 English example was ordinary language and rejected as a placeholder finding.

Original package neutral-envelope/hidden-selector gates pass for all three datasets. New import-event metadata includes importProvenance.schemaProfile=universal-v2; the current generic prevention checker calls that a forbidden nested selector. This is a policy/transport-metadata conflict, not evidence that it selected a verb-specific renderer or appeared to learners. It is retained as INFO in additional-gates.json, and requires policy clarification before any repair. Zero confirmed leakage means zero confirmed matches under these scans, not a proof that arbitrary unenumerated strings cannot leak.

## I. DUPLICATION RESULTS

Duplicate active IDs=0 in each release; exact (front,back,category) duplicate cards=0 in each release. Normalized headword/category candidates: A1 schaffen (ma1m-lu-1969 /1970) and A2 hängen (ma2-lu-0020 /0021). Review confirms distinct strong/weak identities: schaffen schuf/geschaffen vs schaffte/geschafft; hängen transitive hängte/gehängt vs intransitive hing/gehangen. A2 screenshot 01 supports the distinction. B1 has no duplicate in that exact-normalization candidate class. Broader semantic-equivalence review remains partial.

Duplicate generated definition notes in **transport**: A1 0, A2 0, B1 395. Rendered duplicate notes: 0/0/0. B1 AUD-005 is therefore static redundancy/gate failure, not a visible repeated definition. A1 has five reused DE example texts across different related targets (10 occurrences), fully listed in final-analysis.json; no within-card repeated DE groups were found. A2/B1 repeated canonical DE text groups=0. Reuse across a base verb and its construction can be valid, so these five are INFO, not confirmed semantic duplicate cards. Canonical example IDs remain distinct and structural annotation scans pass.

Duplicate canonical relation identity/target keys under the implemented comparison=0. One repeated synonym **surface** on B1 mb1m-lu-0200 is AUD-006; renderer deduplicates it. Cross-level repeated lexemes are expected course membership, not automatically duplicate errors.

## J. LINGUISTIC REVIEW

**Objective:** five A1 finite-perfect principal-part inconsistencies (AUD-003); two A2 raw-source tense rewrites (AUD-004, evidence issue); A1/B1 absent rendered translations (AUD-002, presentation issue). No objectively material DE/FA/EN meaning or example-translation error was established in the targeted trilingual sample.

Automated checks cover all 3988 DE groups and their 3988 FA +3988 EN nonempty translations, grouping/IDs and annotation segment consistency. Human linguistic review covered the exact 24 cards in targeted-review-ids.json (eight per level), all 96 associated trilingual example groups, plus the five A1 morphology findings and the explicit duplicate/homograph/source discrepancy targets. Larger lexical packets were generated, but that is not a claim that every packet row was manually validated. This sampling cannot certify all 997 definitions, all 11964 texts or all synonyms as materially correct.

**STYLE / UNCERTAIN items, not confirmed defects:** A2 ma2-lu-0126 sich fühlen ↔ sich befinden is sense/context conditional; B1 mb1m-lu-0265 anmachen has flirt-register neighbours flirten/schäkern/aufreißen whose strength differs; B1 mb1m-lu-0337 handeln contains topic-sense relations that are not substitutable in every other sense; B1 mb1m-lu-0001 fourth FA example renders noch somewhat literally, but the advice is preserved. These warrant focused linguistic review before editing, not automatic relation deletion or mistranslation labels.

## K. RELATION AUDIT

All actual relation arrays were checked for IDs, required structure, source/target references where internal, and projection item counts. No unresolved internal relation targets or broken canonical relation identity were confirmed. External string-valued synonyms are not dangling internal IDs merely because no card has that title.

A1 768 records: RELATED75, REKTION273, SYNONYM254, WORD_FAMILY66, COLLOCATION49, ANTONYM23, NVV28. A2 1205: SYNONYM246, RELATED142, REKTION307, COLLOCATION412, WORD_FAMILY60, NVV14, ANTONYM24. B1 2526: REKTION400, SYNONYM933, RELATED22, ANTONYM15, COLLOCATION637, WORD_FAMILY252, COMPONENT251, NVV16. B1 vnext has 1446 groups containing all 2526 items; no count-based dropping is established. A2 vnext 930 groups/1205 items, A1 732/768.

Canonical and projected relation integrity is structurally supported. A2 original canonical learning_units does not contain an independently packaged split relation authority file, so projected canonical_relations are the counted layer. Semantic synonym/antonym fitness, register and substitution are reviewed only for the targeted sample; full linguistic correctness remains UNVERIFIED. AUD-006 is a display-list duplication, not proof that two distinct canonical relation records should be merged.

## L. AUDIO AUDIT

A1 source_audio_refs: 310 occurrences, 275 unique filenames, zero-audio ma1m-lu-0073 /0074. A2: zero source_audio_refs on all 292, consistent with screenshot authority; no audio was fabricated. B1: **439 occurrences**, **400 unique filenames**, zero-audio **mb1m-lu-0030** and **mb1m-lu-0363**, matching the declared projection count and known source dispositions. Multiple memberships/targets can share a filename, so unique count need not equal occurrence count.

Reference objects, preserved locators and map structure were checked. Exact source MP3 bytes and current registered source CSV were unavailable: audible speech correctness, file existence at the original source, file hash, audio-to-target identity and the source legitimacy of the two zero-audio cases are **UNVERIFIED independently**. The two zero targets agree with packaged evidence/current checkpoint, not a fresh raw-source/audio observation. Audio-mode router scopes succeeded, but that proves neither file playback nor voice accuracy. AUD-001 loses top-level source_audio_refs in newly exported packages (310 A1 /439 B1 occurrences; A2 explicit empty arrays disappear). Surviving other canonical payloads may still contain related evidence; the contract nevertheless loses these exact fields.

## M. PRESENTATION / RENDERER AUDIT

All original rows have neutral de-vocabulary identity and neutral envelope; lexical category/entry_type remains semantically Verb/Expression rather than being rewritten to renderer identity. Study back HTML on all 997 avoids legacy v217 geometry classes. Geometry style parameters are the same neutral contract across levels. No source_schema_profile-to-renderer routing divergence was established in the tested Study path.

All 754 production Study verb-front HTML outputs contain present/preterite/perfect values and definitions. All 997 model fronts have German definitions. A1/B1 translation-node failure is AUD-002; A2 has 2336 translation nodes across 1168 grouped examples, with three examples visible on page1 and fourth on page2. The supplementary browser mounts production renderer output under actual CSS in a disposable context; screenshots are **render-output QA mounts**, not screenshots claiming every card was reached through the scheduled Study UI. Actual Study/Quick/Typing/Audio router launches accept the full dataset scopes. End-to-end every mode's reveal, pagination click, keyboard, rating, filter/edit and mobile layout flows were not exhaustively exercised.

Practice model example group counts: Study4, Quick2, Typing3, Audio3 for every card. This verifies configured counts, not translation payload correctness. Required empty-field hiding, all relation sections in every practice DOM, expression structure interaction, mobile scroll geometry and English toggle behavior outside the audited Study HTML remain partially/unverified. A pre-existing English hidden setting alone would be legitimate; AUD-002 instead has no translation nodes to reveal.

## N. ROUNDTRIP / RUNTIME RESULTS

Real Chrome executable C:/Program Files/Google/Chrome/Application/chrome.exe; Playwright Node runtime; isolated ephemeral browser contexts; localhost HTTP serving the exact extracted runtime; real IndexedDB. No user profile/storage was touched. Service workers blocked; no offline/service-worker acceptance claim. Readiness is a bounded awaited loop requiring both active count and commit manifest VERIFIED with the exact count. The initial Promise/truthiness probe was invalid and replaced.

All three: fresh count0 → nested exact ZIP import → verified 310/292/395 → page reload → same verified counts. No page errors captured in the primary runner. IndexedDB-backed **authority export** returns all IDs and rich protected canonical/source/audio/membership fields. Authority TSV → clean-context import → authority re-export preserves the checked protected semantic keys (all 997). It is not byte-equal: import-event time/file/sidecar evidence and dataBuildId/validatorVersion change; plain TSV lacks a sidecar, so promptVersion is reset to runtime default v3.1.7 on all 997. That metadata change is not a lexical-content loss, but standalone TSV must not be described as retaining verified original package build authority.

Original TSV→authority export also normalizes presentation example representations, whitespace and learning-contract structures; A1 ma1m-lu-1267 raw seed double-space is collapsed; B1 mb1m-lu-0200 related/details is deduplicated. Rich protected canonical content survives the plain-TSV reimport comparisons. These representation differences were not used as generic “all cards lost” findings.

Native Content Package ZIP → clean-context reimport: IDs/count and prompt v3.3.6 preserved; protected parity **FAIL** due AUD-001. Inspection of the actual exported ZIP proves fields are missing before the importer sees it. B1 canonical_unit example annotations/provenance copies are removed even though separate canonical_examples remain preserved. Do not claim all canonical annotations everywhere were destroyed.

Historical v451-R85 and present CURRENT are byte-identical, so these results cover both for this date. Earlier persisted-import PASS claims are compatible with the verified imports; any broad “lossless roundtrip” interpretation extending to the default native Content Package exporter is unsupported by the original harness and falsified here. No complete browser-process restart, signed mobile runtime or remote hosted runtime was tested.

## O. TEST / HARNESS AUDIT

Packaged A1/A2/B1 Stage7 phase1/phase2 and A1 defect-regression scripts were inspected, not accepted based on their names. They use hard-coded Linux Chromium/path/output assumptions and Python Playwright; that dependency was unavailable locally. They were not falsely reported as executed. Equivalent scoped Node checks used exact hashes/bytes and real Chrome/IDB. Fake/emulated IndexedDB evidence in inherited reports remains a distinct environment boundary.

The original bounded manifest polling awaits page.evaluate and is not inherently the Promise/truthiness error encountered in this audit's first draft. Some inherited browser evidence is one-run, platform-specific or model/export-row-only. A1's defect regression verifies nonempty core slots rather than valid finite forms. A2/B1 “phase2 roundtrip” checks inspect universalAuthorityRows export; they do not import the **native default exported Content Package ZIP**. Canonical translation/count assertions validate retained data, not actual FA/EN DOM nodes. B1 phase1 does not establish a transport-notes invariant. These blind spots permit AUD-001/002/003 while expected count checks pass.

New audit false-evidence controls: first async readiness draft treated an async waitForFunction result incorrectly and observed empty generation; rejected and rerun with awaited active/manifest readiness. First DOM draft selected [data-example-id], which falsely returned zero rows on A1/B1 and missed A2 pagination; corrected to renderer group classes and separate node-presence vs first-page visibility. Corrected A2 passes. Schema mismatch (A2 learning_units), console encoding, Git ownership and initial sandbox network failures were local harness/environment issues, not release findings. Raw static candidate membership_parity=395 compared B1 canonical original supplemental membership to enriched course_memberships; this compares different layers and was rejected. “previously unknown” placeholder candidate was also rejected. Look at final FINDINGS.json rather than treating every diagnostic candidate as confirmed.

Current gates executed: runtime currentness policy PASS; app prevention suite 9 tests PASS; kit memory PASS; kit prevention suite 21 tests PASS; package preflight all3 PASS; projection A1/A2 PASS; B1 projection FAIL with 395 duplicate definition notes. Nine official source-occurrence/identity/enrichment validators PASS. Passing enrichment completeness verifies declared closed dispositions and hash-bound dimensions, not independent lexical truth or raw screenshot fidelity.

Five disposable negative fixtures were correctly rejected: duplicate active ID, literal learner REKTION, hidden presentation selector, missing canonical unit lineage, cache contamination. Additional current lineage checks against actual exported data reject source/audio losses, but baseline A1 is already rejected for absent canonical_unit despite its valid split canonical_target representation; B1 baseline is rejected for notes. New importProvenance.schemaProfile also triggers forbidden nested-selector complaints. Count these gate boundary/conflict observations separately; they are not proof that runtime uses a hidden selector for geometry.

The Node audit programs use exit0 for a completed audit execution even when result assertions fail. This report reads JSON assertion statuses explicitly; exit0 is not a PASS. Child official/preflight gate exit codes are recorded. Late-commit timeout, missing occurrence, dropped translation, duplicate example and deliberate orphan relation negative fixtures beyond the five above were not all injected: recommended under R, not claimed tested.

## P. CROSS-LEVEL CONSISTENCY

All3 share runtime, card family, four trilingual data groups and semantic/presentation separation. Source/membership/audio differences are legitimate: A1 and B1 Memrise lineage, A2 screenshots and intentional zero audio. A1 split v411 canonical objects; A2 native learning_units/renderer-compatible canonical_unit; B1 deep-copy target envelope. The representation differences explain why identical count-based gates are insufficient: A2 renders grouped translations, A1 loses them upon compaction, B1 cannot adapt its richer source group shape. All3 default runtime ZIP export uses compact CARDS and loses cold metadata. Generic prevention must cover each representation without forcing unrelated schema conversion merely for uniformity.

## Q. PREVENTION GAPS

Existing policy/gate presence is not enough. Missing integration coverage: native export after compaction/reload, rendered translation-bearing nodes and stable IDs, exact finite morphology values, and raw occurrence-text binding to immutable sources. Static notes prevention exists now and successfully catches B1; integration/history did not apply that invariant at release creation. Current lineage gate can detect some missing fields but conflates canonical_unit-only authority and transport schema metadata with presentation selectors; running it unqualified across these three representations would produce misleading failures.

## R. RECOMMENDED NEW TESTS / GATES

1. Real-origin import/reload → actual UI Content Package export → ZIP inspection → clean-context reimport → protected deep parity by ID. Assert all source refs/memberships/audio arrays, canonical annotations/provenance, examples/relations and build lineage, including intentionally empty arrays. Use runtime-owned hydration before export. Keep count assertions, but do not use them as parity.
2. Per-native-schema renderer regression: all cards, production Study HTML, grouped DE/FA/EN nodes and stable IDs; visible front values; reveal/pager/toggle interaction with computed visibility; include A1 rich-versus-compact and B1 deep-copy envelopes. Add Quick/Typing/Audio DOM checks according to configured visibility rules.
3. Morphology fallback fixture with auxiliary haben + participle but no explicit perfect. Assert third-person singular conjugation and explicit alternative handling; compare headword/sense, not a universal “all verbs use haben” rule. Negatives: wrong auxiliary/participle/separable/reflexive placement.
4. Stage1 source raw-text immutable binding: independently hashed screenshot/transcription/CSV, explicit normalized field and amendment ledger. Fail VERIFIED raw claims whose bytes are reconstructed from enriched forms; inject the 70/154 tense substitutions as negatives.
5. Apply existing duplicate-definition-note gate to exact Stage5 TSV and exact final bytes; deduplicate relation display strings without erasing distinct canonical relation scopes.
6. Make lineage validation schema-aware; accept supported split/native/deep-copy authority, compare protected nested fields, and explicitly distinguish transport-profile provenance from renderer identity. Add self-parity baselines so valid A1 does not fail by shape alone.
7. Add adversarial source target without disposition, orphan relation, dropped translation, duplicate example and delayed async commit fixtures; bounded awaited polling must fail late/partial commits. Gate success must not be emitted from only a resolved Promise object, stale report or stage fixture.

These are recommendations. No production tests/gates or content repairs were implemented. Audit-local scripts are evidence tooling only.

## S. PROJECT-MEMORY CANDIDATES

Promote after review: AUD-001 compact-runtime data is not export authority; require rich hydration and actual ZIP roundtrip. AUD-002 retained trilingual arrays/counts are not proof of rendered translations; validate every native schema after compaction. AUD-003 nonempty morphology fallback is not finite-form correctness. AUD-004 raw evidence must not be reconstructed from normalized/enriched forms. Each crosses a reusable stage boundary and deserves durable scope/trigger/detection/prevention evidence, while retaining existing incident IDs/policies. No memory changes or promotions occurred during this audit. AUD-005 aligns with an existing gate; link workstream evidence instead of creating redundant generic memory.

## T. LOCAL-ONLY INCIDENTS

Keep in audit/workstream history: first-draft async probe, DOM selector/pagination false failures, A2 schema handling correction, Windows UTF-8 stdout, Git safe.directory command scoping, sandbox network retry. An inline import of the current prevention module created two __pycache__ files in kit Verification; the final Git check caught them. Only those generated files and the resulting empty cache directory were removed within the verified workspace, then final-analysis.py was rerun and both repository statuses were checked clean. These were audit-tool side effects and corrected local probes, not production content incidents. One synonym repetition and uncertain stylistic relations/translations need bounded workstream disposition, not a broad cross-project prohibition. Rejected membership/placeholder candidates remain recorded to prevent later misreading of raw diagnostics.

## U. REPAIR RECOMMENDATION — NOT EXECUTED

Repair is warranted, with separate bounded scopes and explicit user authorization after review:

| Finding | Source content | Projection/package | Runtime | Required post-repair evidence |
|---|---|---|---|---|
| AUD-001 all3 | No new source meanings required | Re-export test outputs only initially; later new package authority only through authorized release process | Hydrate exact persisted authority for default Content Package export; preserve cold/deep-copy data | Real ZIP roundtrip all997, protected deep parity, reload, original-source/audio lineage, stable IDs |
| AUD-002 A1/B1 | Existing translations retained; do not regenerate | Native adapter/projection repair if required by supported runtime contract | Handle grouped examples under compaction and B1 envelope; preserve visible UI layout | All2820 groups FA/EN DOM nodes, stable IDs, reveal/paging, all modes, semantic parity |
| AUD-003 A1 five IDs | Explicit canonical perfect enrichment or controlled finite-form derivation; raw source untouched | Fix five projected perfect values and regeneration only if later authorized | Runtime-only fallback correction only if that is the chosen contract owner | Exact five values, all247 fronts, canonical/projection/runtime agreement, no ID/count drift |
| AUD-004 A2 two raw fields | Restore source-attested raw_text; canonical correct morphology stays | Rebind occurrence/closure/checksum evidence if later authorized | None indicated | Exact screenshot-byte lineage, raw/normalized separation, all297 source orders/336 dispositions |
| AUD-005/006 B1 | None indicated | Remove redundant transport notes; unique synonym display projection; do not blindly delete canonical relations | Existing suppression works | Current static projection gate, all395 rendered note checks, protected relation parity |

Do not solve an existing runtime bug by repacking the same defective runtime and calling it repaired. Decide the contract owner during an authorized bounded repair; preserve CURRENT/LAST_FULLY_VERIFIED policy until the required validation/release process changes it. Do not downgrade A2 Repair2 to Repair1. Keep raw source identity, lexical IDs, audio references and existing example translations intact. No Repair, relock, UI modification or release creation has begun.

## V. EXACT COMMANDS / TESTS RUN

The full executable paths, cwd, argument arrays, targets, output files and child exit statuses are in **COMMANDS.json**, support-results.json, deep-results.json and final-analysis.json. The audit scripts beside this report are executable reproduction definitions. PYTHON below resolves to the bundled dependencies/python/python.exe; NODE to dependencies/node/bin/node.exe. Framework validators target the exact extracted package source files, not current workstream substitutes.

| Command / target | Result | Exit |
|---|---|---:|
| git fetch origin main, each repository (approved network retry) | fresh remote main resolved | 0 |
| PYTHON -B German-Flashcards-Pro/03-Tests/test-runtime-currentness-policy.py | PASS | 0 |
| PYTHON -B German-Flashcards-Pro/03-Tests/test-prevention-gates.py | 9 tests PASS | 0 |
| PYTHON -B Verification/prevention_preflight.py memory (kit cwd) | PASS | 0 |
| PYTHON -B Verification/test_prevention_preflight.py (kit cwd) | 21 tests PASS | 0 |
| PYTHON -B Verification/prevention_preflight.py package EXACT_ZIP, each level | all3 PASS | 0 each |
| PYTHON -B Verification/prevention_preflight.py projection EXACT_TSV | A1/A2 PASS; B1 duplicate notes rejected | 0 /0 /1 |
| PYTHON -B framework/Verification/validate_source_occurrences_v1_0_0.py EXACT_OCCURRENCES | all3 PASS | 0 each |
| PYTHON -B framework/Verification/validate_identity_closure_v1_0_0.py EXACT_OCCURRENCES EXACT_IDENTITY --canonical EXACT_CANONICAL | all3 PASS | 0 each |
| PYTHON -B framework/Verification/validate_enrichment_completeness_v1_0_0.py EXACT_MATRIX --policy EXACT_POLICY --canonical EXACT_CANONICAL | all3 PASS; 4776/4508/6157 closed cells, 0 unresolved | 0 each |
| NODE Audit-Menschen-Final-2026-10-01/runtime_audit.cjs | completed; ZIP semantic parity FAIL all3; import/reload and protected authority TSV parity pass | 0 execution |
| NODE Audit-Menschen-Final-2026-10-01/runtime_surface_audit.cjs | completed; translations FAIL A1/B1, A2 pass; front values all754 pass | 0 execution |
| PYTHON -B Audit-Menschen-Final-2026-10-01/final_analysis.py | exported ZIP byte losses confirmed; original hashes/Git unchanged | 0 |

Other audit scripts/inline probes and their boundaries are indexed in COMMANDS.json. Initial failed local drafts (async, schema, encoding, Git ownership) do not enter accepted evidence. Original Python Playwright Stage7 scripts were inspected but not run. No test result was inherited solely from a cached PASS report. Shell exit0 for an audit runner does not imply assertion PASS; recorded JSON assertions govern this report.

## W. UNEXECUTED / BLOCKED CHECKS

- Exact current registered raw Memrise source/CSV comparison for A1 and B1; original audio bytes/file hashes/playback-to-card identity. No Library/Project source retrieval connector was available; local similarly named material was not used as a replacement.
- Complete independent transcription of all A2/B1 screenshots. A2 hashes/order coverage and three inspected images support the specifically reported findings, not a claim of full image transcription.
- Exhaustive human linguistic review of all997 definitions/FA/EN meanings, all3988 trilingual example groups and all4499 canonical relation records. Structural closure is complete; semantic truth is sampled.
- Original platform-specific Python Playwright acceptance scripts: unavailable Python Playwright. Node real-origin checks were executed within the stated replacement scope, without treating unavailable historical harnesses as PASS.
- Offline/service-worker behavior, complete browser-process restart, mobile/signed Android, real user persistent profile, remote hosted runtime, entire wrapper ZIP direct import.
- End-to-end every learner field and interaction in every practice mode, all filters/search/edit/review scheduling/rating/Word Explorer flows, mobile layout and pagination/toggle clicks. Mode routing/model counts and production Study render HTML are tested; they do not cover these flows.
- All adversarial negative types beyond the five executed fixtures; neither deliberate late commit nor dropped-translation fixture was run as a gate-negative test.

No whole-release VERIFIED CLEAN or unrestricted linguistic/source PASS is claimed. Material findings are decisive despite the above incomplete dimensions.

## X. GIT STATUS / PERSISTENCE

Production repositories remain clean on the starting commits and main branches, still equal to their fetched origin/main refs. Audit artifacts were created only under `C:/Users/hosse/Documents/German-Flashcards-Workspace/Audit-Menschen-Final-2026-10-01`, outside both repositories. They include scripts, exact-byte extraction directories, source evidence copies, raw/accepted JSON results, gate logs, disposable fixtures, runtime-produced TSV/ZIP outputs, rendered QA screenshots, this report, FINDINGS/COMMANDS/checkpoint/index and the audit hash seal. The generated outputs are **AUDIT EVIDENCE — NOT NEW RELEASES**. No production content/runtime/policy file changed. Two temporary audit-generated Python cache files were removed before the final clean Git check (see T). No commit, push, memory promotion, release authority update or repair occurred. The final source ZIP hash verification is in final-analysis.json.

Git persistence status: **LOCAL_DURABLE_AUDIT_ONLY / NOT_COMMITTED / NOT_PUSHED**. Audit evidence is locally durable and hash-sealed, not remotely synchronized. The original remote release authority remains separate and unchanged. The audit index and SHA256SUMS-AUDIT.txt provide the complete created-file inventory. The report itself is included in the seal; the seal's own hash is in AUDIT-SEAL.json.

Audit is complete. Stop here for Hossein's review and explicit authorization of any next step.

