# Lesen – Präsentation B2–C1: central policy alignment / scoped audit (2026-11-07)

**Owner:** `family:lesen` / `Workspaces/lesen-praesentation` · **Editorial portable baseline:** `v1.3.0` (SHA-256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`; 3,653,701 bytes); **Library owner:** `/Flasch kart/German-Content-Production-Kit/Content/Lesen/Current` (`libfile_9b768265ff3c8191aca371baa38551d7`). Independent Library byte-by-byte readback PASS.

## Proven evidence (not a release promotion)

- 10 ZIP members: CRC PASS; manifest 8/8 path, length and SHA PASS; SHA256SUMS 9/9 PASS; bundled `verify_package.py` PASS.
- Stable master, compiled runtime and source map: **68/68 IDs** aligned (`LES-PRES-001..068`), no duplicate IDs, **478** sections, **340** questions, **350** vocabulary entries, **669** curated grammar records and **4,612** reported full-text annotations.
- Complete nonempty DE/FA/EN titles **68/68**; FA/EN reading sections **478/478** and FA/EN vocabulary glosses **350/350**. Question evidence section IDs and curated grammar target/section anchors checked; **zero structural issues**.
- Historical packaged QA and full-text-grammar QA list PASS; this pass has NOT independently completed adversarial linguistic quality/semantic German–Persian–English Stage4, nor run actual native v505 import/render/persistence.
- Original `Präsentation.pdf` is within the ZIP and SHA-bound. Historical v413 external import ZIP is kept for recovery only; it is NOT the newer v1.3.0 curated authority.

## Central rules: adoption decision by applicability

| Rule | Lesen scope | Required disposition / evidence boundary |
|---|---|---|
| Currentness and Curated Current / Delta QA | **ACTIVE** for mature Lesen master | v1.3.0 master is the byte-verified working content baseline, original PDF only immutable topic provenance. Future edits compare current->delta; do not rebuild book text or restore removed material. User acceptance/final-app import still separate. |
| Seven-stage workflow | **ACTIVE** owner-specific | Git checkpoint Stage1 PASS, Stages2–7 NOT_STARTED in that *separate* Git reproduction workstream. Existing portable master/runtime does not retroactively promote Git stages. |
| Global policy registry and Project Control Center | **ACTIVE routing**, native adoption not proved | Resolve active Prompt/START-PROMPT and registry each new pass; `family:lesen` already exists in 21-family catalog. Register only a scoped control-center navigation pin; don't alter the 10-family dynamic curated registry or its statistics. |
| DE/FA/EN semantic and risk-based linguistic QA | **APPLICABLE, NOT PROVEN** | Evaluate new/modified texts and exercises, translation quality, tone, grammar classifications, factual examples; AI second-pass not misrepresented as human. No full Stage4 PASS now. |
| Lexical front/headword Formen, senses, Synonyme/Antonyme, Wortfamilie, Kombinationen/Rektion | **CONDITIONAL** only for vocab-to-flashcard conversion | Reading 350 vocab records are **not** standard 8-line or neutral-card TSV. Do not coerce reading JSON into lexical schema; if exporting new cards later, use sense-correct canonical mapping and evidence-based forms, no invented front/relation entries. |
| Lesen runtime import, rendering and SRS separation | **ACTIVE gate, NOT_RUN** | Current app is v505-R141 Wordlinks R3 per app live pin (NOT v470 embedded in historical ZIP). Need exact v1.3.0 compiler/transport acceptance, translation toggles, question/grammar anchors, persistence, performance, and non-regression without SRS mutation. |
| File lifecycle / anti-churn | **ACTIVE** | One owner-scoped Current artifact and compact Git-ledger reports; original, v413 history and existing copies preserved. No deletion; old root copies are possible duplicate candidates only until SHA, dependencies, recovery and owner approval. |
| UI/UX preservation | **ACTIVE** | No change to visible application appearance, imported user data, cards, IndexedDB or FSRS/SRS. |

## Concrete blockers / next bounded outcome

1. **Runtime mapping:** v1.3.0 master reports `FULLTEXT_GRAMMAR_READY_APP_MAPPING_PENDING`; current app is v505-R141, not v470 from October handoff. Test source-derived exact master/compiled-runtime adapters against current app without repackaging an older v413 runtime as modern authority.
2. **Content confidence:** structural completeness is not independent DE/FA/EN semantic review; scope a genuine adversarial linguistic second pass on current changed/at-risk units and learner-facing classification before advertising Stage4.
3. **Formal stages:** do not falsely turn older portable QA into separate Git Stage2–7 PASS. Provide stage-specific source-owner outputs and proofs at any authorized production milestone.
4. **Storage:** safely created `Current`, `Checkpoints`, `Reports`, `Docs`, `Source` under existing Lesen owner folder; no original/source/legacy file deletion. Keep compact manifest and exact portable SHA in owner pointers. No new report-only ZIP.

## Authority and safe continuation

Load: both repository `PROJECT-BOOTSTRAP.md` + `PROJECT-STATE.json` -> Content Kit `README.md` -> `Prompt/ACTIVE-PROMPT.txt` -> `START-PROMPT-v3.3.6.md` -> `GLOBAL-POLICY-REGISTRY-v1.0.0.json` -> owner `CHECKPOINT.json`, **owner `CURRENT-ARTIFACT.json` and `ARTIFACT-REGISTER.json`** -> runtime live `RUNTIME-AUTHORITY-PIN.json`. The project-specific usable master is inside the portable owner Current ZIP. The 76-page historical source is provenance, not replacement for edited texts. Zero generic UI or SRS edits.