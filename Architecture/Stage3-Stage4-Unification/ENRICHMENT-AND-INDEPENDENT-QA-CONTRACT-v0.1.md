# Stage3 integrated enrichment / Stage4 independent QA — compatibility draft v0.1

**Status: PROPOSED / NOT ACTIVE.** This is a design and test contract, **not** a replacement for `Prompt/ACTIVE-PROMPT.txt` or historical `Stage3A/3B/3C/4` authorities. Derived from the 2026-10-27 GitHub versions of `README.md`, `Prompt/START-PROMPT-v3.3.6.md`, the lexical and didactic Kombinationen policies, the linguistic AI-review override, and the edit-apply / lean recovery policies. Source workstreams remain independent.

## Intended pipeline, without shortcuts

`Stage1 original ingestion → Stage2 identity/source closure → Stage3 integrated source-hash-bound enrichment → Stage4 independent risk-based linguistic challenge → Stage5 lossless projection/anti-bypass → Stage6 CURRENT runtime acceptance → Stage7 controlled final delivery`.

The Stage3 author/team must finish or explicitly HOLD all *applicable* facets **in one card-level record**, while keeping the existing evidence and 3A/3B/3C disposition lineage. Stage3 is **not** Stage4 and cannot self-certify it. Stage4 evaluates the entire exact Stage3 source content and is independently methoded from production, with complete deterministic screening and an explicit semantic/adversarial challenge of risk targets and representative non-flagged material. It must not merely repeat Stage3 creation.

## Stage3 unified facets

| Facet | Expected Stage3 work | Stage4 challenge |
|---|---|---|
| `identity` | lemma / lexical unit, scope, stable IDs and source labels | collision/reuse and source-faithfulness |
| `sense` | sense inventory and semantic distinctions | polysemy, non-source senses, wrong referents |
| `translations` | German/Persian/English equivalence where applicable | completeness, meaning and register |
| `examples` | source-exact / curated example choice, German + translations, level, realistic context | naturalness, grammatical correctness, sense/translation match |
| `morphosyntax` | POS, inflection, gender, case, Rektion, verb frames and tense patterns when applicable | morphology, government and governed cases |
| `relations` | synonyms, antonyms, graph identity and sense-bounded links | semantic accuracy, misleading similarity |
| `combinations` | source/curated typed Kollokation, Rektion, NVV and fixed phrases; every displayed item shows a **new learner benefit** relative to examples and other combos | repeated material, misleading collocations, fake source evidence |
| `provenance` | source locator, immutable raw facts, citation kind, curated provenance and lineage | false provenance, unsupported evidence, source-order drift |
| `didactics` | level, usefulness, ambiguity reduction, learner-visible editorial clarity | errors and missed/duplicated teaching value |

For lexical cards all nine facets get a `DONE`, `NA_WITH_REASON` or `HELD` disposition. A facet can be `NA_WITH_REASON` only with a nonempty reason and applicability proof. `combinations` may have **zero** visible items with `CLOSED_NO_FORCE` and a pedagogical explanation. There is **no forced number** of combinations. Keep backend types/provenance, and keep the single current visible label **Kombinationen**. Non-lexical Grammar/Lesen/Schreiben keep their own source and QA contracts unless they emit independent lexical cards.

## Stage3 authoring boundary

- Source is immutable; only current mutable workstream bytes may be edited, subject to CAS/source SHA verification. Historical LOCKED/FINAL content is read-only, and any retrofit creates a successor.
- Distinguish `SOURCE_EXACT`, `SOURCE_ATTESTED`, `CURATED_PEDAGOGICAL` and `PARENT_GENERATED_EXAMPLE`. The last **never** counts as independent source evidence.
- Every Stage3 dossier binds `input_sha256`, `output_sha256`, `source_authority`, `stage3_method`, full per-facet decision, count of unresolved holds and a source-edit application receipt. A report without verified output bytes is **not** completed Stage3. The dry-run preflight also requires `lexical_cards_total`, all nine `facet_card_coverage` totals equaling that total, and `source_lineage_receipt`; these metadata counters are **necessary but not sufficient** until checked against actual card IDs and source bytes in a pilot.
- Legacy checkpoints retain their original JSON schemas/paths. Crosswalk lives in a **separate** file; no mutation of previous Stage3A/3B/3C.
- If unresolved holds exist, a Stage3 candidate may be reviewable but is **not** ready for Stage4 PASS / Stage5.

## Stage4 final independent audit boundary

- Bind Stage4 `reviewed_output_sha256` to the exact Stage3 output SHA; mismatch makes the review stale.
- `independent_method` must differ from `stage3_method`; document AI method, adversarial second pass, source challenge, scope, and risk disposition. Never call model QA a human signature.
- Deterministic screening covers the **whole** applicable dataset. A scoped semantic review is explicitly marked `SCOPED` and cannot certify the parent Stage4.
- `deterministic_scanned_units` must equal `lexical_cards_total`; an independent semantic/adversarial sample must be nonempty, carry method evidence, and reconcile `risk_queue_total == risk_queue_closed` with `risk_queue_open == 0`. Metadata counts alone do **not** prove a real language audit. The nonactive compatibility validator also requires an exact `unit_sha256_by_id` map for all lexical IDs, one reasoned and source/evidence-bound `unit_dispositions` entry per ID, and a detected `seeded_negative_control` tied to an existing ID. In the current draft, `HOLD_WITH_SPECIFIC_EVIDENCE` and `CORRECT_WITH_BEFORE_AFTER` cannot be treated as final without a separately verified closure/post-edit CAS receipt. A perfectly complete *synthetic* ledger is still not linguistic proof or a permission to publish. Every detected/source-risk queue item must be dispositioned (`REPAIR_APPLIED_AND_REVALIDATED`, `KEEP_WITH_EVIDENCE`, `HOLD`, etc.). Any open HOLD or unverified source facts block Stage4 PASS.
- Repairs reopen Stage3 provenance/coverage and invalidate stale Stage4 evidence. Re-run exact SHA-bound independent review after changes.
- Stage4 PASS **alone** is not Stage5 import-readiness, CURRENT runtime Stage6 PASS, Stage7 final, or Library publish approval. Those gates remain required.

## Rollout and compatibility

1. **Discovery (now):** conflict matrix and adapters tested against representative historical checkpoints, including *Menschen A2 L24* Stage3C/Stage4, *250 Verben* active Stage4 WIP, and *Aber Hallo* latest Stage4 OPEN.
2. **Contract dry run (now):** validate fictitious Stage3/Stage4 dossiers, unchanged legacy checkpoint structure, and known block conditions. A test PASS means **schema/compatibility only**, not linguistic accuracy or Stage4 PASS.
3. **Pilot (later, after checkpoint-bound migration validation):** choose one new or mutable bounded lexical workstream, fill actual Stage3 facets from source, run independent Stage4, and compare parity against old Stage3/4 gates. Do not touch current content files during the dry run.
4. **Promotion (gated):** explicit user approval for structural changes that affect existing writers/consumers; exact current backup, regression suite, consistency receipts, and rollback path. Active prompt and project state may change only after these.
5. **Storage:** preserve needed R57 backup proof and old Stage evidence; never delete Project Source files based only on earlier *Checkpoints* hashes or filename/size. Keep Library cleanup separately authorized and evidence-based.

This document intentionally leaves Stage5–7 and app appearance untouched.
