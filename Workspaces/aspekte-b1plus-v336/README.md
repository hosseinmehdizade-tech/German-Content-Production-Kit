# Aspekte B1+ — Status 2026-11-06

## G2 lexical morphology Batch03 — 98 cumulative checks, 51 new, 3 front corrections (2026-11-07)

**Roadmap gate G2 remains ACTIVE; NO import / NO release.** The same [ROADMAP-TEMP.md](ROADMAP-TEMP.md) was updated *in place* to v0.6 in GitHub and Library (same Library ID `libfile_01c5b33ec05881918a21b124acf5eac8`, byte-exact verified SHA256 `32492897c471b5e53bbb556c973bbbff181a3587c8a8d7888caf9b36358d595b`).

- **51 additional individual Duden-backed lexical-grammar form checks**, with every exact page URL retained in the QA register: 33 from older Pass04's 256 forms and 18 from G2's 65 newer source-split lexemes. **98/321 cumulative** (72 older + 26 newer), **223 still pending** (184 older + 39 newer). This is specifically part-of-speech and German inflection scope, *not* bilingual/whole-card verification.
- **Three actual corrected learner-facing front views** (total 12 real front corrections across G2 lexical batches):
  - Source ordinal **460** `der Scheich`: keep both Duden plurals `Scheichs` / `Scheiche`, with an explicit sense-bound note that some title use has no plural.
  - Ordinal **483** `der Prinz / die Prinzessin`: weak masculine singular `den Prinzen` (Akk.) and `des Prinzen` (Gen.) added while retaining the one lexical-family card.
  - Ordinal **504** `der Dozent / die Dozentin`: weak masculine singular `den Dozenten` (Akk.) and `des Dozenten` (Gen.) added, keeping feminine forms.
- **Strict full-object assertion:** all **1,571 original preview IDs** and **1,548 source ordinal links** persist; all Persian senses, all DE–FA example arrays, all source text and existing 47 QA ledger entries are untouched. Only three intended front display strings plus explicit metadata on 51 reviewed entries were introduced; no source/master change, no redundant `Formen` on preview backs.
- **Source and form/sense discipline:** Duden checks grammar only; source remains the user's *current edited B1+ CSV* and existing curated project ZIPs, never newly re-extracted textbook PDF. Plural differences for title vs person and other sense-dependent usages remain G4 semantic QA questions. Zero cards have full DE–FA signoff; all 340 HOLDs stay blocked. No final app import file.
- **Library sidecar:** `Reports/Aspekte-B1plus-G2-LEXICAL-BATCH03-98-CUMULATIVE-51-NEW-3-CORRECTIONS-NONIMPORT-20261107.zip`. SHA256 `b74757b60ecdb18b8f07645883111a2358ecc389076f6e4b5a09e02ffe5e14f3`; 410,370 bytes, nine ZIP members, eight verified manifest hashes, exact-byte Library readback and ZIP CRC pass.
- [Batch03 metadata receipt](Reports/G2-LEXICAL-BATCH03-51-NEW-98-CUMULATIVE-3-FRONT-CORRECTIONS-RECEIPT-20261107.json). **Next:** 184 old + 39 new wordform cases to finish G2, then the acceptance gate before starting G3. Stage G4 full semantic/example verification and G5 real app render/import remain outstanding.

## G2 lexical morphology Batch02 — 47 cumulative form checks and 7 new front fixes (2026-11-07)

**Active Gate:** G2 / 6. Current one-file [temporary roadmap](ROADMAP-TEMP.md) is v0.5, updated in place in GitHub and Library. Baseline remains the current user-curated B1+ source CSV, never a new obsolete textbook extraction.

- Independent Duden-backed **form-specific** review for **20 additional source headwords**; cumulative **47 / 321** checks against the targeted Pass04+G2 morphology proposals (older 39 / 256; new split 8 / 65). **274** checks remain (217 old; 57 new).
- Exactly **7 learner-facing front proposals edited** in this batch; 9 actual front corrections over both lexical batches. Ordinals: **371 Spieltrieb**, **375 Geselligkeit**, **379 Lust**, **381 Motorik**, **385 Soziologe/Soziologin**, **401 Schach**, **415 Paradies**. Duden-supported plural behavior was recorded by sense where appropriate; Soziologe's weak singular declension was made explicit. These are grammar/front corrections, **not** independent bilingual semantic or complete-card approvals.
- Current **1,571** nonimport learner view IDs and **1,548** exact source-row links retained; no original source, Persian meanings or bilingual example arrays changed. Six of this batch's cases have sense-specific follow-up flags for Gate G4, and four from the earlier lexical batch remain marked.
- All **340 HOLDs remain blocked**, **0** formally approved cards, no import TSV, G3 not started.
- Verified private Library sidecar: `Reports/Aspekte-B1plus-G2-LEXICAL-BATCH02-47-CUMULATIVE-20-NEW-7-CORRECTIONS-NONIMPORT-20261107.zip` SHA256 `8c121ae271d68a0b707c3028902782d23384ffde40060789f9cba72f7703fd69`, **406,744 bytes**, **9** ZIP members, **8** verified manifest hashes; exact-byte Library readback and CRC passed.
- [Batch02 receipt](Reports/G2-LEXICAL-BATCH02-20-NEW-47-CUMULATIVE-7-FRONT-FIXES-RECEIPT-20261107.json). Next: 217 older + 57 newly split individual forms, then decide G2 formal closure and only then move to G3.

## G2 lexical morphology Batch01 — 27 specific form checks, 2 front fixes (2026-11-07)

**Gate G2 remains ACTIVE / NONIMPORT.** This sidecar extends the latest 1,571 view G2 source-row ledger and preserves all 1,548 source ordinals. It does not replace the parent master or edit the dedicated user vocabulary CSV.

- Of **321 targeted source-derived front-form proposals** (256 older Pass04 cases + 65 G2 source-split lexeme candidates), **27 individual forms** were checked against specific Duden entries for the relevant part of speech, declension, conjugation or valid inflection: 19 older and eight new. **294** still require individual lexical form verification (237 older + 57 new). A form-specific Duden match is not whole-card QA, semantic duplicate resolution, bilingual example signoff or an app release approval.
- Exactly **two actual user-facing front candidate fixes**: ordinal 516 `der Albtraum` now also retains accepted spelling `Alptraum` and `Alpträume`; ordinal 778 `Hektar` now distinguishes both `das/der Hektar`, the noun plural `Hektare`, and count-unit form `10 Hektar` with `ha`. The old source's `der` spelling was not discarded.
- **Four separate meaning-sensitive risks** were explicitly flagged but not falsely approved: G2 source ordinal 404 `virtuell`, 666 `zufällig`, 418 `endlos`, 714 `das Kaffeeservice`. The first three retain the user-source degree candidates pending sense-specific usage QA; no plural was invented for `Kaffeeservice`, whose Duden entry confirmed its gender but did not explicitly state a plural.
- Independent structural before/after assertions proved **all 1,571 existing provisional learner-view IDs**, all **1,548 source links**, exact source-to-card map bytes, all Persian meanings, all German–Persian example arrays, source identity, and back-side redundant-`Formen` suppression unchanged. Only the two cited front display strings and explicit QA metadata changed.
- All **340 HOLDs remain blocked**. Formally approved learner cards: **0**. Import TSV or Stage5 release: **not started**.
- Verified Library package: `Content/Aspekte-B1plus/Reports/Aspekte-B1plus-G2-LEXICAL-BATCH01-27-VERIFIED-2-CORRECTED-1571-PREVIEWS-NONIMPORT-20261107.zip`; SHA256 `b4cd7ebd0ceda144fd3abdaa70583d2cdf1accf338399f436a59850f04fd7d63`; 404,130 bytes; eight ZIP members; seven verified internal manifest hashes; exact Library byte readback + CRC pass.
- **Current one-file roadmap:** [ROADMAP-TEMP.md](ROADMAP-TEMP.md) updated *in place* to **v0.4** in GitHub and Library, same library file ID `libfile_01c5b33ec05881918a21b124acf5eac8`, SHA256 `337e2c07c91f94e9597906f0f843914d6b6f01e2446f2874438a9f254113ab34`.
- [G2 lexical Batch01 receipt](Reports/G2-LEXICAL-BATCH01-27-FORMS-2-CORRECTIONS-RECEIPT-20261107.json). **Next:** continue targeted individual lexical verification of 294 remaining form cases, then finish morphology Gate G2; only afterward proceed to G3 overlays, G4 DE–FA meanings/examples, G5 crosslevel TSV/app-card QA and G6 release.

## G2 independent split-lexeme morphology front proposals and G1 form-family corrections — 2026-11-07

**Roadmap version 0.3, G2 ACTIVE (nonimport).** The existing G1 identity-routing ZIP and its 1,573 provisional views were checked against direct German grammatical relations. Two G1 views had represented forms of the same word as independent cards:

- Source ordinal **65** `weitestgehend` was merged as a Duden-attested superlative into the `weitgehend` learner family; `weitergehend` stays a separate semantic candidate pending G4.
- Source ordinal **1256** `die Seeleute` was merged as a Duden-attested plural/collective form into `der Seemann`, retaining the plural's Persian gloss and source-evidence links for G4.

Consequently **1,573 → 1,571 provisional learner views** with **1,548/1,548** source rows mapped. All **67** previously source-split candidate units received an *individual* disposition: **65** surviving independent lexeme units had their front morphology/part-of-speech information directly updated in the candidate views; **two** became same-lemma grammatical-form links. The surviving 65 are classified as 30 nouns, 15 verbs, 15 adjectives, 3 prepositions and 2 adverbs. No existing back-side Persian meanings or source DE–FA examples in surviving views were modified; source examples are still awaiting lexeme-specific G4 review, never blindly assigned to a different lemma.

**Verification boundary:** 30 distinct surviving candidate fronts have a reference URL recorded, and 23 had scope-limited reference pages directly returned in this session. Neither a dictionary link nor a regular morphology transformation means the entire card/word has been independently approved. All 65 front forms remain provisionally staged; earlier 256 source-derived Pass03 forms still need per-word lexicographic review. The infrequent/disputed plural of `das Kaffeeservice` is explicitly kept as an unresolved lexical QA issue without an invented learner-facing plural. Both plural senses of `Schlüsselwort` and `Stichwort` were considered rather than forcing one plural across all senses.

All **340 source HOLDs remain release-blocked**. There are **zero formally approved cards**, no final TSV import and no app release.

Private Library report: `Content/Aspekte-B1plus/Reports/Aspekte-B1plus-G2-67-SPLIT-MORPHOLOGY-2-IDENTITY-REPAIRS-1571-PREVIEWS-NONIMPORT-20261107.zip`.
SHA256 `dbf129adf51f24713596b99cb6e72f559fa3a1336dc680fa9d482844e1df2fdd`, 484,991 bytes, 8 ZIP entries, 7 verified internal SHA256SUMS, byte-exact Library readback and CRC verified.

The **same** [temporary roadmap](ROADMAP-TEMP.md) was overwritten in Library/GitHub in-place at version 0.3 (Library id `libfile_01c5b33ec05881918a21b124acf5eac8`, SHA256 `6fa096b9e9f2aae44be6b328042ead952262ba5601728243f38d22c20955afc9`). [G2 metadata receipt](Reports/G2-67-SPLIT-INFLECTION-2-FORM-FAMILY-MERGES-RECEIPT-20261107.json).

**Next:** G2 individual independent lexicographic verification of 65 new front proposals and 256 older proposals, followed by G3 overlay edits, G4 full DE–FA semantics/examples, G5 actual renderer/TSV import QA and only then G6 release.

## G1 completed for the current B1+ source corpus — 2026-11-07

**Current work gate:** G2 ACTIVE. The same [temporary roadmap](ROADMAP-TEMP.md) was updated in place to v0.2; the Library mirror remains at `Aspekte-B1plus/Plans/ROADMAP-TEMP.md` with the same library file id, SHA256 `f5fa4d26c2a821fd6f332a74069ba4528cbf71b560eee187d0e70fcfd7db99b4`.

A source-to-learner-unit **content routing patch** has been applied to the existing Pass04 1,544 provisional preview views and verified against all **1,548 source CSV rows**: **1,573 provisional learner units** now have stable identities, with zero missing source links. All original source ordinals, attested examples, and source meanings are preserved. A provisional learner-unit view count is not the final import count and is not a release claim.

This corrected an important earlier underestimate: the 20-source-row Gate2B review is a subset; **120** multi-signal source records were classified after scanning the actual candidate corpus, including **110** existing preview fronts and **35** original source headwords with spaced slash separators (overlapping). **31** shared source rows with genuinely different lexemes were split into linked learner targets. **59** male/female paired word forms stay within one lexical-family card, as do two same-lemma gender alternatives. Source rows 14, 15 and 57 are linked as collocation evidence to existing Kontakt or greifen headwords; two independent targets with other existing primary cards (`beschäftigt` ordinal 296 and `Wohlstand` ordinal 405) were linked instead of duplicated.

All **seven** official same-lemma duplicate pairs are linked to single provisional headword targets. Pass04 already linked three; G1 linked the remaining **four** (18+733, 761+762, 1085+1086, 1240+1241). The earlier independently linked 206+207 pair also remains preserved. No source rows were dropped.

**G2/G4 dependency:** the new split yields **67** learner-unit views whose independent morphology and lexeme-specific bilingual examples are *not yet checked*. Their original combined source examples remain in the evidence field, not shown under an arbitrary separate lemma. No morphology guesses or fabricated examples were added. All **340 HOLDs remain release-blocked**, and **zero** cards have formal approval.

Verified private Library sidecar: `Reports/Aspekte-B1plus-G1-CARD-IDENTITY-ROUTING-1548-SOURCE-ROWS-NONIMPORT-20261107.zip`, SHA256 `ee2487479b5e2cc9feb308aeff9397d94e2102ba8cce3bd0237b2ba6174efc0e`, 427,830 bytes, seven ZIP members, six SHA256 manifest entries, exact-byte Library readback and CRC PASS. [G1 receipt](Reports/G1-IDENTITY-ROUTING-1548-SOURCE-1573-VIEWS-RECEIPT-20261107.json).

**Next:** G2 first verifies individual German morphology of all 67 new lemma targets and 256 Pass03 source-derived form proposals, then G3 overlays, G4 bilingual semantic example QA, G5 final crosslevel TSV sense/render test, and G6 only after formal HOLD release signoff.

## Temporary six-gate roadmap and compulsory progress footer (2026-11-07)

**[ROADMAP-TEMP.md](ROADMAP-TEMP.md)** is the single in-place working roadmap for finishing Aspekte B1+. Its exact-byte Library mirror is at `Content/Aspekte-B1plus/Plans/ROADMAP-TEMP.md` (SHA256 `729a7bfe8c5c896a88e23a97c2a62e21655444582f61c1efb5a10a2a6bb250b3`). The same paths are linked in `LATEST.json` and `CHECKPOINT.json`.

Current gate: **G1 / 6 — source row → learner card identity and duplicate routing**. Next actions: 20 multi-lexeme source rows and seven exact candidate headword-repeat groups. G2 morphology, G3 overlay reconciliation, G4 full DE–FA semantic QA, G5 crosslevel TSV/app rendering/import testing, G6 formal release and temporary-file cleanup follow in order. Gate status changes only after measurable acceptance criteria pass; no invented overall completion percentage. Stage4 QA Pass04 is still NONIMPORT, with 1,544 provisional preview views and 1,548 preserved source rows, all 340 HOLDs blocked, zero approved cards.

**Required behavior for all further B1+-related replies:** first read the roadmap and current GitHub/Library checkpoint; after any actual work update the SAME roadmap file in GitHub and Library (do not fork dated roadmaps), and finish the reply with a short Persian roadmap progress summary: current gate, this turn's measured change or explicit zero change, current blockers, one next action, formal approvals/HOLD release count. No progress credit for reports alone.

**CURRENT STAGE4 CONTENT COVERAGE (2026-11-06): 10/10 lessons, 340/340 unique HOLD source records and 383/383 distinct archived overlays have individual editorial content rulings. All 340 HOLDs remain RELEASE-BLOCKED. Zero cards have independent final QA approval. This is a NONIMPORT state, not Stage5/6/7.**

**Stage 4 / Gate2D Part05 complete (scoping only, nonimport).** The project vocabulary comes only from the user's B1+ CSV.

## Verified counts
- Source-only B1+ rows across 10 lessons: **1,548**.
- Stage3 drafts and Stage4 first-pass reviews: **1,548 / 1,548**.
- Individual P2 semantic/comparator scopes: **250 / 250**, including 50 in Part05.
- Distinct HOLD rows scoped: **340 / 340**; formally released **0**. All HOLDs remain blocked.
- Earlier editorial overlays: **383**, still unapproved.
- Part05 additionally proposes **22** German–Persian example pairs; none authorized for import.
- Exact lemma check against actual final Menschen A2 (1,778) and B1 (3,089) TSVs found **das Umfeld** in B1 (ordinal 1337), not an automatic duplicate decision.
- Independent final-card QA incomplete. Stages 5–7 have not started; zero published cards.

## Private Library baseline
`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B1plus/Current/Aspekte-B1plus-STAGE4-FINAL-QA-GATE2D-PART05-250-P2-INDIVIDUAL-REVIEWS-NONIMPORT-20261106.zip`

SHA256: `61c71d2bfc106ceb3355f174e0f68acf12b4fb532b7ffcaf6cd15e2c7b3f75bc`.
Size 3,313,224 bytes; 412 members; 411 checked manifest entries; CRC and Library byte-exact readback passed; previous 403 members retained.

**Curated-current resume readback (2026-11-06):** `LATEST.json` and `CHECKPOINT.json` identify the private Library Gate2D Part05 250-P2-review **NONIMPORT** working ZIP, SHA256 `61c71d2bfc106ceb3355f174e0f68acf12b4fb532b7ffcaf6cd15e2c7b3f75bc` (3,313,224 bytes; 412 ZIP members). Its current materialized Library bytes and ZIP CRC were rechecked; neither this proof nor "FINAL-QA" in the filename makes it a final learner-card TSV or releases 340 HOLDs. On each resume, prefer the newest independently verified owner-local curated editorial successor to stale initial CSV; check changed lesson decisions and their dependencies only, plus remaining semantic/release gates. `Prompt/CURATED-CURRENT-AUTHORITY-AND-DELTA-QA-POLICY-v1.0.0.md` controls the source-versus-curated distinction. No user words were restored/removed by this routing check.

## Open gates
- Resolve the actual semantic and duplicate decisions on all 340 HOLDs and approve or reject 383 editorial overlays.
- Use the **final TSVs in their project folders**, not stale textbooks, for comparison. Verify A1/C1 and context-level matches.
- Enforce article/plural, verb forms, adjective comparisons on front, no redundant back-side Formen.
- Complete independent bilingual QA against the **accepted current B1+ editorial content**, and inspect original source only for bounded exact-attribution, disputed provenance or corruption cases. Do **not** restart whole-book/raw-CSV fidelity auditing or vocabulary extraction from historical files.
- No import or release until these checks pass.

See [LATEST.json](LATEST.json), [CHECKPOINT.json](CHECKPOINT.json), and [Part05 metadata](Reports/STAGE4-QA-GATE2D-PART05-METADATA-RECEIPT-20261106.json).

## Stage 4 final editorial content decisions — Lesson 1 (2026-11-06)

- All **25 L01 HOLD source rows** received explicit content and learner-target dispositions in a 49,277-byte private report stored in the B1+ Library `Reports` directory.
- **9** previous editorial overlays were reviewed and superseded by explicit content decisions; **51** source-contained targets specified, **13** new DE–FA examples and **2** translation corrections.
- 5 exact lemma hits against actual final Menschen A2 content were identified but **not** automatically removed. A1/B1 and sense-level comparisons are not fully signed off.
- Main Gate2D Part05 ZIP baseline is **unchanged**. **All 340 HOLDs still release-blocked**, **zero formally approved cards**, no import.
- Next: complete the **18 HOLD editorial content rulings in L02**; then L03–L10. Run final QA and front morphology/back Formen contract before publication.

Private report SHA256: `d1100805558e826946c4110c3c9a12a9dffd1b7f6f1e8e5a5ec31708cc845c5c`.
Private report Library id: `libfile_62cb235c1c1c8191b663df956a0e730f`.

## Stage4 editorial adjudication — Kapitel 2 Wohnwelten (2026-11-06)

- **18/18 L02 HOLD source rows** now have specific source-preserving content and morphological decisions (additional **28 contextual sense facets** under those existing entries).
- **14** prior L02 editorial overlays individually reviewed. **1 old proposal rejected as written:** figurative harsh film criticism was incorrectly assigned to `zerreißen` rather than `verreißen`; the latter is only a dictionary distinction, **not** an added source headword.
- **12** contextual bilingual example pairs proposed. One Duden-confirmed adjective correction: `menschenscheu — menschenscheuer — am menschenscheuesten`; also `meterdick` and two forms of `umbauen` reviewed.
- Field-level exact matching of all 18 archived Stage3 source rows to the sanitized B1+ CSV passed. **0** exact primary-lemma matches against 1,778 cards in the **issued final Menschen A2 TSV** for the 18 entries. Full B1/A1/C1 semantic comparisons pending.
- **43/340** editorial content decisions cumulatively (L01 25 + L02 18), **297** yet to receive editorial content decisions. **All 340 HOLDs remain blocked for release**, all 383 historical overlays still require final-card signoff, **0 formally approved cards**.
- Private Library sidecar: `Reports/Aspekte-B1plus-STAGE4-L02-18-HOLD-EDITORIAL-DISPOSITIONS-NONIMPORT-20261106.zip`. SHA256: `11900e3983978ce53ea7baa373ed10971d0eec956c54bc5e8b45fb74a91445f7`. Readback SHA256 + CRC + 6 manifest hashes verified. The Gate2D Part05 master archive remains unchanged.
- Next: complete L03 editorial decisions in one coherent lesson-scoped batch. Do not repeat source extraction or auto-drop by simple lemma match.

## Stage4 editorial content rulings — Kapitel 3 (2026-11-06)

- **42/42** L03 HOLDs have distinct proposed content rulings, preserving every original CSV source row.
- **44** prior editorial overlays in L03 were individually routed: 23 on HOLD source rows and 21 on other L03 rows.
- **26** additional German–Persian example pairs are proposals, not approved or importable cards.
- Source-row parity checked against sanitized B1+ CSV and saved Stage3 records; original source and parent master ZIP untouched.
- Actual issued Menschen A2 final collection of **1,778** cards yielded **0 exact primary-lemma matches** for these 42 items (narrow check only). A1/B1/C1 crosslevel sense comparison not complete.
- Grammar details include separable/inseparable `umgehen`, the two auxiliary patterns of `ausscheiden`, nuanced singular/plural of `Köstlichkeit`, and the potential cross-row shared lemma `nahestehen` at source ordinals 206 and 207.
- Cumulative **85/340** HOLD content rulings (L01 25 + L02 18 + L03 42); **255** remain. All **340/340** still release-blocked, and **67/383** earlier overlays content-reviewed.
- Verified Library sidecar (8 manifest entries, 9 ZIP members, SHA256+CRC+readback): `Reports/Aspekte-B1plus-STAGE4-L03-42-HOLD-44-OVERLAY-EDITORIAL-DISPOSITIONS-NONIMPORT-20261106.zip`.
- Sidecar SHA256: `a3e3bb4ee3fba31ccfe2a48b3731797c535e26e9eb3e8cd675296d453d68fca7`.
- Main Gate2D Part05 master ZIP stays unchanged; **zero** cards formally approved for release.
- Next: Kapitel 4 editorial content decisions, then full-card independent QA and final crosslevel semantic adjudication.

## Stage4 editorial dispositions — Kapitel 4 Viel Spaß! (2026-11-06)

- 158 original B1+ source rows reconciled with the existing Stage3 L04 draft: exact field-level source parity checked, original CSV and parent master ZIP unchanged.
- **31/31 L04 source HOLDs** have detailed **nonimport content dispositions**, including full source verbatim rows, corrected contextual Persian glosses, proposed front morphology and grammatical constructions.
- **62/62 previous L04 editorial overlays** individually reviewed; **12 require revision before independent QA**. No old overlay auto-approved as a final card.
- **32** additional context-specific DE–FA example pairs proposed, no release signoff.
- A2 authoritative **1,778-card final release TSV** strict front-lemma precheck found an overlap for **stehen** (source ordinal 487, A2 card `ma2m-lu-0087`). The meaning **stehen für + Akk.** requires sense-based comparison; no deletion authorized.
- Provenance links 442/443 (same source **schätzen**) consolidated as a single proposed lexical base while retaining both source ordinals and their example evidence. Separate meanings kept for entfallen, Karte, würfeln, Dokumentation and neben.
- Source gloss risks include national ≠ nationalistisch, Wasserrauschen ≠ flowing water, Familienbetrieb ≠ 'family jobs'; bound irgend- and Partizip I ermordend are explicitly special-case, not silent new lemmas.
- Cumulative **116/340 HOLD content dispositions**, **129/383 previous overlay reviews** across lessons 01–04. **All 340 HOLDs remain release-blocked**, zero final approved/import-ready cards.
- Private Library report: `Reports/Aspekte-B1plus-STAGE4-L04-31-HOLD-62-OVERLAY-EDITORIAL-DISPOSITIONS-NONIMPORT-20261106.zip`.
- ZIP: 57,597 bytes; 9 members, 8 SHA256 manifest entries; Library exact-byte SHA256 + CRC + manifest verified; SHA256 `edc080d4485265cdb26ad1851cb751df3827fe0682e4912fe21ebeaf107e4844`.
- See [L04 GitHub metadata receipt](Reports/STAGE4-L04-EDITORIAL-CONTENT-DECISIONS-RECEIPT-20261106.json). Next **Kapitel 5**, then remaining lesson content decisions and final bilingual/morphology/crosslevel QA before any release.

## Stage4 editorial dispositions — Kapitel 5 Alles will gelernt sein (2026-11-06)

- **156/156** lesson Stage3 source records have exact-field parity against the dedicated B1+ sanitized CSV. Source data and the current Gate2D Part05 master ZIP are unchanged.
- **29/29** L05 HOLD records now have individualized content/sense/grammar decisions; **all distinct senses of each lemma remain grouped within one source-aligned card proposal**. Only the exact duplicate row 611 links to base row 610; neither source occurrence was deleted.
- **44/44** earlier L05 editorial overlays individually reviewed; **22 flagged for revision before final-card QA**.
- **44** new contextual German–Persian example pairs proposed, with independent QA still pending.
- Real final Menschen A2 **1,778-card release TSV** checked for exact base lemma matches. `die Teilnahme` (source ordinal 546; A2 `ma2m-lu-1274`) is a match but has not been approved as a semantic duplicate because B1+ has additional usage domains.
- Full Menschen B1 final TSV was not programmatically available in this run (returned 43 MB path was not present on disk). A1/C1 final comparator checks remain pending. Do not infer zero overlap from a missing file.
- Front morphology proposals include article/plural or verb inflections; avoid duplicate `Formen` on the back when already on the front. That contract has **not yet passed independent app-card QA**.
- Cumulative **145/340** HOLD content rulings after lessons 01–05. **195** require content rulings. **173/383** editorial overlays reviewed. **All 340 HOLDs remain release-blocked** and **zero** final approved cards.
- Verified private Library sidecar: `Reports/Aspekte-B1plus-STAGE4-L05-29-HOLD-44-OVERLAY-EDITORIAL-DISPOSITIONS-NONIMPORT-20261106.zip` (36,783 bytes, 8 ZIP members, 7 SHA256 entries, exact-byte Library readback and CRC passed).
- Sidecar SHA256: `1b50588e8a355068e675b2c45ce948a0493f8dba29dd93fcddc20593f9f35065`.
- See [L05 GitHub metadata receipt](Reports/STAGE4-L05-EDITORIAL-CONTENT-DECISIONS-RECEIPT-20261106.json). Next Kapitel 6, then L07–L10 and independent comprehensive full-card QA before import.

## Stage 4 editorial decisions — Kapitel 6 Berufsbilder (2026-11-06)

- Original 175 source rows from L06 (ordinals 672–846) checked against sanitized user CSV, all original Stage3 source records exact-field aligned; **no primary source or master ZIP mutation**.
- **32/32** official L06 HOLD rows received individual contextual semantic/grammar decisions. **47/47** official L06 overlay proposals were individually reviewed; **4** need revision and **1** earlier morphology form-order rewrite for `verlegen` was rejected as written. Other overlay content stays proposed, not final-card approved.
- **17** additional bilingual German–Persian example pairs drafted (nonimport). They fill omitted meanings of `Protokoll`, `verlegen`, `Besprechung`, `Netz`, `Lebenslauf`, and other specified source headwords.
- Distinct senses remain on **one card per lemma**; distinct lexemes sharing one source row (e.g. `Service` and `Kaffeeservice`) may have linked learning targets without deleting any source record. Exact duplicate source occurrences `Darauf kommt's an` (733 → 18) and `einhalten` (762 → 761) are linked rather than independently published.
- Genuine final Menschen A2 1,778-card TSV read from its dedicated release ZIP; narrow exact-normalized-lemma check found `Lebenslauf` (A2 `ma2m-lu-1568`, B1+ source ordinal 747). This is **not** an approved semantic duplicate. The B1 43MB TSV could not be accessed on working filesystem and was not asserted as checked; final A1/C1 semantic checks remain open.
- Major bilingual content corrections: `Menschenkenntnis` ≠ academic anthropology, `Fachwissen` ≠ generic experience, `Arbeitszeugnis` ≠ generic recommendation letter, `Ringelpullunder` is sleeveless, `weitaus` is an intensifier, and use of `irre` about psychiatric patients is dated/stigmatizing.
- Cumulative **177/340** HOLD content rulings and **220/383** prior-overlay content reviews for L01–L06. **163** HOLDs and **163** old overlays still need content rulings. **ALL 340 HOLDs remain release-blocked; 0 final approved cards.**
- Verified private Library report: `Reports/Aspekte-B1plus-STAGE4-L06-32-HOLD-47-OVERLAY-EDITORIAL-DISPOSITIONS-NONIMPORT-20261106.zip`; SHA256 `48eafb1926c18d4bfba7480d98eff61b0ff0cc7b6d6018192df497da68107059`; 26,701 bytes; 9 ZIP members, 8 SHA256 entries, CRC and byte-exact Library readback pass.
- [Private report metadata receipt](Reports/STAGE4-L06-EDITORIAL-CONTENT-DECISIONS-RECEIPT-20261106.json). Next lesson: **Kapitel 7 Für immer und ewig**; independent QA, final TSV comparators, morphological front and conditional back Forms suppression are outstanding.

## Stage4 editorial decisions — Kapitel 7 Für immer und ewig (2026-11-06)

- **153/153** original source records exactly matched the saved Stage3 L07 source evidence and the sanitized B1+ CSV; neither source rows nor the verified Part05 master ZIP were mutated.
- **37/37** official L07 source HOLDs received individualized DE–FA content decisions, grouping multiple meanings of one lemma in the same proposed card and keeping distinct lexemes on the same source row linked rather than silently dropped.
- **32/32** prior official Stage4 overlays on L07 records received individually authored content review outcomes. This is not independent release approval.
- **39** additional contextual DE–FA examples proposed; examples and release candidates still require independent whole-card QA.
- Source corrections: `verzeihen` is forgiving, not apologizing; `millionenfach` means millions of times, not precisely one million; `das Liebe` is not a normal independent noun; use `die Liebe` and greeting `Alles Liebe!`. Related meanings for `der Teil` vs `das Teil`, `verschlingen`, `ausgelassen` and two adverbs `jemals / niemals` are retained in appropriately structured proposed cards.
- Final Menschen A2 release of **1,778** cards was used only for exact primary-lemma screening; primary headword overlaps are `halten` and `der Versuch`, with related expressions `Verzeihen Sie!` and `außer Dienst`. No semantic duplicate was approved, no B1/A1/C1 final semantic crosslevel QA is complete.
- Cumulative **214/340** HOLDs have L01–L07 lesson-level content dispositions; **126** remain. **252/383** old editorial overlays reviewed; **131** remain. Every one of the 340 HOLDs stays release-blocked and **0** cards formally approved.
- Private Library sidecar: `Reports/Aspekte-B1plus-STAGE4-L07-37-HOLD-32-OVERLAY-EDITORIAL-DISPOSITIONS-NONIMPORT-20261106.zip`.
- Report SHA256: `faf64ed1b7b8d0fea2fa723f503169af51de40aeba837741d2181f41a1260795`; size **42,190** bytes, **10 ZIP members** and **9** SHA256 manifest entries; verified byte-exact Library readback and CRC PASS.
- [L07 GitHub metadata receipt](Reports/STAGE4-L07-EDITORIAL-CONTENT-DECISIONS-RECEIPT-20261106.json). Next Kapitel 8, then L09–L10 and independent full-card QA before import.

## Stage4 editorial decisions — Kapitel 8 Kaufen, kaufen, kaufen (2026-11-06)

- Exact source parity: **157/157** source rows with authoritative B1+ sanitized CSV and the archived L08 Stage3 draft. Original source and verified master ZIP unchanged.
- **38/38** source HOLDs received individual proposed DE–FA sense, front morphology, rationale and disposition; **34/34** official L08 overlay proposals received individually authored content review.
- **36** additional DE–FA example pairs proposed; these are not independent QA-approved cards.
- Cases: `umschreiben` separable `schrieb um/umgeschrieben` for rewriting vs inseparable `umschrieb/umschrieben` for paraphrasing, `abkaufen` separable, `Zoom` der/das with plural Zooms, `Milliarde` 10^9 distinct from `Billion` 10^12, source duplicate `Panorama` ordinals 1085 and 1086 linked with both original rows retained.
- Strict exact-lemma comparator on real released Menschen A2 **1778-card** TSV: `Größe` (A2 `ma2m-lu-0117`) and `bestellen` (A2 `ma2m-lu-0597`) flagged; **no final semantic duplicate/deletion decision**. 43MB B1 final TSV connector materialization not present on runtime filesystem; A1/C1 final semantic comparator QA pending.
- Cumulative **252/340** HOLD content dispositions, **286/383** earlier overlays reviewed after L01–L08; **88 HOLD** content rulings and **97 overlay** reviews remain. **All 340 HOLDs retain release block**; 0 formally approved cards and no import.
- Private Library sidecar: `Reports/Aspekte-B1plus-STAGE4-L08-38-HOLD-34-OVERLAY-EDITORIAL-DISPOSITIONS-NONIMPORT-20261106.zip`.
- SHA256 `cbe583eaecd016a961dafc8a65e47ca7bf5b713deb860fdd376cb323bd2aab2d`; 42,546 bytes; 10 ZIP members; CRC, 9 SHA256 manifest entries and byte-exact Library readback verified.
- [L08 GitHub metadata receipt](Reports/STAGE4-L08-EDITORIAL-CONTENT-DECISIONS-RECEIPT-20261106.json). Next Kapitel 9, Kapitel 10, then crosslevel final-card QA, front morphology and conditional back Formen suppression.

## Stage4 editorial content rulings — Kapitel 9 Endlich Urlaub (2026-11-06)

- **185/185** original L09 source records exactly matched the user's dedicated sanitized B1+ CSV and saved Stage3 full source records. Source SHA256 `cca32df935397a81367b38f9b51ee33aac357ea135947a131b712969f0339033`. Master Part05 SHA256 `61c71d2bfc106ceb3355f174e0f68acf12b4fb532b7ffcaf6cd15e2c7b3f75bc` remains unchanged.
- **43/43** L09 HOLD records received individualized content decisions, including one-card-per-lemma polysemy, morphology and German–Persian nuance. **36/36** prior L09 official overlays independently examined as source-preserving editorial proposals.
- **41** new contextual DE–FA example pairs proposed; **none** has final independent full-card QA/signoff.
- Source ordinals **1240 and 1241** both `zurückhaben`: one proposed base lexical card linked to both original source occurrences, with both source records and examples retained.
- Key decisions: `Andenken` mass remembrance vs countable souvenir, `Handlung` act vs plot vs outdated shop, `Pension` lodging vs retirement payment, `Seemann` vs plural `Seeleute`, `Flieger` aircraft vs aviator, and professional `Assessor` distinct from ordinary evaluator.
- Correct front-side verb forms: `zurücklegen – legte zurück – hat zurückgelegt`; `anführen – führte an – hat angeführt`; `entladen – entlud – hat entladen`. Recheck final lexicographic/morphological candidates independently before approval.
- The actual **1778-card final Menschen A2 TSV** was compared for a strict normalized primary lemma against these 43 rows; **0 exact matches** found. This is only a string test, NOT semantic duplicate clearance. Final B1/A1/C1 primary project TSV sense checks still pending.
- Cumulative **295/340** HOLD editorial content rulings and **322/383** prior overlay content reviews. Remaining **45 HOLDs and 61 overlays**, concentrated in Kapitel 10. All **340 HOLDs still release-blocked**, no cards formally approved or importable.
- Verified private Library sidecar: `Reports/Aspekte-B1plus-STAGE4-L09-43-HOLD-36-OVERLAY-EDITORIAL-DISPOSITIONS-NONIMPORT-20261106.zip`; SHA256 `b7e567349d186104dca68b924b4ad7afc59cc6070632203d96da808bd2f31279`; 45,382 bytes, 10 ZIP members, 9 SHA256 checks and exact byte readback/CRC passed.
- [L09 metadata receipt](Reports/STAGE4-L09-EDITORIAL-CONTENT-DECISIONS-RECEIPT-20261106.json). Next: Kapitel 10, then final morphological front/back Formen and independent full-card bilingual QA, without reopening obsolete textbook extraction.

## Kapitel 10 and L01 gap reconciliation — Stage4 content review coverage

- All **207** L10 Stage3 records were compared exactly with the user-owned sanitized B1+ CSV, no source/parent master rewrite.
- **45/45** blocked L10 source records received individualized semantic and morphology *content proposals*, with all senses of the same lemma kept together and distinct co-listed words retained as linked learning targets.
- **57/57** official L10 editorial overlays were individually reviewed; a prior summary had mistakenly called them 61. The other **four** were missed in L01: source ordinals **4, 34, 39, 54**, and are now reviewed in the attached closure register.
- The audited union of **nine actual previous lesson sidecar ZIPs**, the L10 45-HOLD/57-overlay layer and those four L01 records is exactly **340/340 unique official HOLD ordinals and 383/383 unique official overlay ordinals**, with no overlap or omissions.
- The L10 layer adds **28** proposed German–Persian example pairs. Its content decisions are not final linguistically certified cards.
- Source ordinals 1451/1452 share `Baumstamm`: retain both source links under one proposed base card. `Hochwasser`/`Überschwemmung` and `Wasserknappheit`/`Wassermangel` remain distinct lexical targets while sharing their original source-row provenance.
- All release gates remain closed: **340/340 HOLDs still blocked**, **0** import-ready/approved cards, **383** prior overlays *content-reviewed but not formally released*, full independent DE–FA QA and front morphological rules/back `Formen` suppression pending. Use actual final project TSVs for sense-level comparator checks; do not restart outdated publisher-source extraction.
- Private L10 Library sidecar: `Reports/Aspekte-B1plus-STAGE4-L10-45-HOLD-57-OVERLAY-L01-4-GAP-CLOSURE-NONIMPORT-20261106.zip`.
- Private sidecar SHA256 `8ef5e0f6c93cacf8bca5113d9f9529bcff548a35b2a1701bd0681a6870d99cfc`; **51,225 bytes**, **13 ZIP members**, **12 SHA256 manifest entries**; verified exact-byte Library readback, CRC and all manifest hashes.
- The original Part05 1,548-row master remains at the same verified Library SHA256 `61c71d2bfc106ceb3355f174e0f68acf12b4fb532b7ffcaf6cd15e2c7b3f75bc`.
- [Coverage receipt](Reports/STAGE4-L10-ALL-340-HOLD-383-OVERLAY-CONTENT-COVERAGE-RECEIPT-20261106.json). **Next: independent full-card semantic, morphology, Persian translation, sense-level duplicate review and final formal release approval—not more broad source scoping.**

## Independent Stage4 QA Pass01 — 2026-11-06

**This is an initial independent QA preflight and targeted issue review, NOT independent completion/signoff of every card.** Stage3 source drafts remain unchanged; all 340 HOLDs remain release blocked.

- Verified structural coverage of **1,548/1,548** Stage3 candidate entries; all five source-identifying fields exactly match the dedicated current sanitized B1+ CSV. This is bounded provenance checking, not obsolete textbook reconstruction.
- All **3,098** draft bilingual example pairs are nonempty; all **1,548** candidate entries contain at least two complete DE–FA pairs. This does **not** validate the correctness of their German or Persian semantics.
- **357** stored candidate morphology fields explicitly contain outdated/unverified source-form placeholders. These cannot appear verbatim on the learner-facing card front.
- All 1,548 Stage3 objects lack a finalized back-of-card render field, so the project-wide suppression of a redundant `Formen` section cannot yet be independently confirmed.
- Existing all-lesson content decisions reconciled by source ordinal: **340/340 HOLDs and 383/383 overlays**, with **no missing original decisions**. Review coverage does not mean release approval.
- **41** targeted issue-dimensional card reviews on existing source rows: **33 corrective content requirements** plus **8 duplicate-occurrence linkage actions**. Produced **37 actually patched but NONIMPORT front/back previews** by collapsing four source-duplicate pairs, without dropping any original source record. All 37 previews place contextual forms on front and deliberately omit back-side `Formen`; these mockups do not prove complete final app rendering.
- Drafted **26** additional German–Persian example pairs on the same attested B1+ headwords; all proposals still need final semantic QA.
- Exactly **7** identical normalized candidate headword pairs across the 1,548 entries were flagged for sense/provenance review; do not auto-remove them.
- **0** formally approved cards, all **340 HOLDs blocked**, **no import TSV**. Whole-project semantic verification of 1,548 effective learner cards, final cross-level TSV sense comparison, and front/back app layout QA remain open.

**Verified private QA ZIP:** `Content/Aspekte-B1plus/Reports/Aspekte-B1plus-STAGE4-INDEPENDENT-CARD-QA-PASS01-1548-STRUCTURAL-41-TARGETED-NONIMPORT-20261106.zip`.

SHA256: `6d0900f5935961d5c7667d864a6959dc57b0a72d8c257cc75a0a526233d8620c`; 198,860 bytes, 14 ZIP members, 13 verified SHA256 manifest entries; exact-byte Library readback and CRC pass.

[QA Pass01 metadata receipt](Reports/STAGE4-INDEPENDENT-CARD-QA-PASS01-METADATA-RECEIPT-20261106.json). **Next:** merge accepted curated lesson decisions and issue-specific patches into one single effective-card view, fix 357 morphology placeholders, provide actual front/back render fields, independently review all bilingual meanings and duplicates, then sign off HOLDs before any import.

## Independent Stage4 QA Pass02 — canonical provisional views

**Nonimport only.** Stage4 QA Pass02 combines all **10 verified lesson editorial sidecars** with current Pass01 targeted patches, creating one canonical *provisional* view, without mutating master/source or treating any card as approved.

- **1,548 / 1,548** source rows matched current sanitized B1+ CSV fields verbatim. **340** HOLD content rulings and **383** historic overlay content reviews linked by actual source ordinal. No source word was deleted.
- A provisional **1,544-card-view set** (not final learner-card count) was assembled by linking exactly **4** existing source-duplicate pairs with their original source ordinals retained. Three additional same-headword pairs remain for final sense/provenance review. Distinct lemmas within a source record still require separate learner-target routing; multiple senses of one lemma remain grouped.
- All **357** Stage3 morphology source-verification placeholders were detected and hidden from learner-facing preview fronts. **68** received a specific provisional replacement from lesson rulings or targeted patches, but **289** still lack an adequate proposed morphological front; these are flagged, not guessed or invented. Proposals are not independently certified.
- The preview backs include Persian sense proposals and bilingual example candidates **without duplicated `Formen` blocks**. This verifies these preview fields, not the final app renderer.
- **248** older overlay content reviews had no machine-applicable delta; their reviewed status is linked, but no change was invented. **63** old overlays are rejected or need rewrite. These risk flags can overlap each other and the morphology cases: the distinct blocker register has **498 source rows**.
- Current effective source-row views contain **3,140** existing bilingual example pairs (L01 curated drafts included) plus **273** deduplicated extra proposals, all awaiting actual German/Persian semantic QA. Non-empty examples are not proof of correctness.
- Source and ten lesson sidecars remain unmodified; the master Part05 SHA256 is `61c71d2bfc106ceb3355f174e0f68acf12b4fb532b7ffcaf6cd15e2c7b3f75bc`. All **340 HOLDs are still release-blocked**, zero cards formally approved, and no Stage5 import TSV created.
- Verified private Library ZIP: `Reports/Aspekte-B1plus-STAGE4-QA-PASS02-1544-CANONICAL-PREVIEWS-1548-ROW-PARITY-NONIMPORT-20261106.zip`.
- ZIP SHA256 `16d15fa6be183937b4d0d8a219c9cd2e820b46f1bc1f0a55dd2f22137267863d`; 432,600 bytes, 7 members, 6 manifest SHA256 entries; byte-exact Library readback and CRC verified.
- [QA Pass02 metadata receipt](Reports/STAGE4-INDEPENDENT-CARD-QA-PASS02-CANONICAL-PREVIEWS-METADATA-RECEIPT-20261106.json). **Next:** repair blocker source rows, independently verify all DE–FA examples and front morphology; use final actual TSVs for cross-level sense matching and test real app front/back rendering before any HOLD release.

## Independent Stage4 QA Pass03 — morphology recovery (nonimport)

Pass03 addressed only the **289** morphology placeholders remaining after Pass02, all originating in **L04–L06**. It relied on the verified current user CSV and Pass02 previews, not outdated book-source audits or dictionary-based new headword discovery.

- Generated **256 conservative source-derived morphology proposals**, of which **240 actually changed the displayed front** and **16 correctly classified invariable phrases/adverbs needing no inflection table.** This is a content proposal count, **not 256 independently approved inflections**.
- The 256 proposals comprise source-explicit regular or zero/singular-only noun plurals, marked umlaut plurals, source-attested masculine/feminine pairs, 24 verb paradigms (including explicit separable source forms where provided) and source-explicit adjective degrees. Every change is linked to the exact original source ordinal.
- **33** unresolved cases remain without a sufficiently safe morphological proposal, including **3 sentence-as-headword identity cases** and 30 adjectival/other form concerns. No arbitrary comparative or irregular form was generated for these.
- Verified preservation of **1,544** provisional view IDs, **1,548** original source-ordinal links, all Persian sense drafts, all original and supplemental German–Persian example pairs, and all back-side `Formen` suppression fields. Original master and Pass02 package are unchanged.
- Prior Pass02 **498 possible blocker source rows** has **not** been recomputed after this one-dimensional pass. Remaining issues also include the **248** older overlay reviews lacking machine-applicable deltas, **63** rejected/rewrite overlay flags (categories overlap), and independent semantic, lexicographic and real-app-render QA.
- All **340 source HOLDs remain release-blocked**, **zero** cards approved, no import TSV or Stage5 release. All 256 form proposals are deliberately marked **pending independent lexicographic QA**.
- Private Library: `Reports/Aspekte-B1plus-STAGE4-QA-PASS03-1544-PREVIEWS-289-MORPHOLOGY-REVIEW-NONIMPORT-20261106.zip`.
- SHA256: `c428a4887239b11d95070bfb5357b5da14b25653ede50ac116e53609e28959ce`; **447,660 bytes**, **8 ZIP members**, **7 SHA256 manifest entries**, exact-byte Library readback, CRC and manifest verified.
- [Pass03 metadata receipt](Reports/STAGE4-INDEPENDENT-QA-PASS03-MORPHOLOGY-RECOVERY-METADATA-RECEIPT-20261106.json). Next: independently validate these proposed inflections and 33 open forms/identity entries, then multilingual example semantics, overlays and final app front/back QA.

## Independent Stage4 QA Pass04 — morphology rules and 33 remaining cases (nonimport)

**Purpose.** Review the 256 morphology proposals previously reconstructed in Pass03 with independently coded source-rule checks, and individually classify/repair all 33 entries for which Pass03 lacked a safe proposed front. This pass does not restart original textbook extraction or change the 1,548 source rows.

- **256/256 Pass03 source-to-front transformations passed an independently implemented structural/grammar-rule audit** against the current curated B1+ headwords. **This is not word-by-word lexicographic verification of all 256 words.** Distinguish structural source-evidence checks from individual dictionary signoff.
- **33/33 previously unresolved source rows received individual editorial morphology/identity dispositions**; 13 have specific dictionary reference URLs for their grammatical classifications or forms. The 3 complete sentences (ordinals 417, 473, 505) remain sentence learning units with no artificial lemma inflections.
- The ordinal adjective forms `drittgrößte`/`zweitschönste` are already rank superlatives, rather than plain graded adjective positives. Invariant adverbs and contextual participles are distinguished from attributive adjectival endings; no fictitious comparatives were generated.
- **New substantive correction:** `das Tempo` in source ordinal **572** also permits plural **Tempos** in addition to **Tempi**. Verified with Duden, the provisional front now displays `das Tempo — Pl. Tempos / Tempi`.
- Exactly **34** front preview fields changed (33 individual manual decisions plus the Tempo plural fix); **1,544 provisional preview cards and all 1,548 source ordinal identities** retained. No back-side meanings, Persian translations, German–Persian examples, source provenance, duplicate links or original master files were modified.
- All source morphology exceptions now have an explicit proposal/routing decision, but **final individual lexicographic signoff for most of the 256 remains open**, as do the 19 male/female paired-lexeme rows and one row with two distinct lexemes that will affect eventual card-unit routing.
- **340/340 HOLDs remain release-blocked**, zero formal card approvals; semantic and bilingual example QA, older overlay rewrite risks, final comparator TSVs and real app front/back render validation remain open. No Stage5 import TSV.
- Verified private Library sidecar: `Reports/Aspekte-B1plus-STAGE4-QA-PASS04-256-RULE-AUDIT-33-MANUAL-RESOLUTIONS-NONIMPORT-20261106.zip`. SHA256 `efd83a16807ae3639074e2dcdc5b087fdebf91b3a46d482d8dd4ab897e522904`; 366,141 bytes; seven members, six internal manifest SHA256 hashes; exact byte readback and ZIP CRC passed.
- [Pass04 QA metadata receipt](Reports/STAGE4-QA-PASS04-256-RULE-AUDIT-33-MANUAL-DISPOSITIONS-RECEIPT-20261106.json). Next focus is targeted **word-level lexicographic validation** of the remaining source-derived forms, then distinct-lexeme routing and full semantic/renderer QA. No new obsolete-source searches.
