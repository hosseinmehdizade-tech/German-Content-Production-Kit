# OP-02 — Stage4 reviewer worksheet freshness against actual WIP50 (2026-10-29)

**NONACTIVE read-only pipeline QA; no source, learner-card, LOCKED, current LATEST, Library, application or runtime changes.** This is an optimization of Stage4 safety, NOT execution of language corrections or a production release.

## Read-only exact-WIP50 findings

The actual Google Drive-recovered WIP50 ZIP was already independently authenticated:
`a558055dbddda45d5d3040fb096bf28eb8f51e2c0863f5634c445094decfc96b`.
The following actual ZIP members were compared locally across **all 788 units**:

- `02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json` SHA256 `fe50217d519edbb1c4d5eb5fc4da36faf1f562e859ccfe58b0153dbf684c48aa`
- `01-Final-Import/IMPORT.WORKING.tsv` SHA256 `d640179d3fdfa2ecff0681b707519bc6d10ff687aba22482a7e8694aba374a8a`
- `05-QA-Tests/STAGE4-REVIEWER-WORKSHEET-CURRENT-UNSIGNED.csv` SHA256 `30486336c3f920aee70f8f4ee4adbc6ee2991033ed2ed9921cf64e29bcc3116d`

Worksheet rows: **788**; expert_decision populated: **0**; **604/788** unit IDs have at least one exact frozen-field mismatch against current Canonical. Field counts (overlap across units): `kombinationen_json=513`, `relations_json=198`, `rection_json=10`, `meaning_fa=1`, `examples_en_json=1`. The other compared fields are exactly equal: `definition_de`, `gloss_en`, `core_json`, `examples_de_json`, `examples_fa_json`, `headword`, `type`. A few examples of the *kind* of real drift, not linguistic judgments:

- `ahl-lu-0131` / *drohen*: worksheet Persian gloss is shorter than current Canonical.
- `ahl-lu-0275` / *vergewissern*: one English example translation has different wording.
- `ahl-lu-0033` / *erklären*: `rection_json` renders the grammatical pattern differently.
- Many relation and combination differences reflect new or removed objects / metadata, and MUST NOT be auto-classified as linguistic errors without analysis.

The embedded `05-QA-Tests/STAGE4-REVIEW-BOUNDARY.json` already declares `NOT_SIGNED_OFF`, 788 rows and 0 decisions; its historical SHA references are stale relative to WIP50. The embedded `Historical-Parent-Baseline/STAGE4-GATE-CONTRACT-v1.1.json` explicitly pins **older canonical/import/worksheet hashes**; it is historical, not a WIP50 approval mechanism. Do not run it and claim a WIP50 pass. Human-only references in historical artifacts do not override current `EDIT-APPLY-VERIFICATION-CONTRACT.json` permitting documented independent-method AI second-pass signoff; *neither* AI self-attestation nor historical human approval text establishes issuer authority.

## New nonactive tool

`Verification/audit_stage4_current_worksheet_freshness.py` deterministically projects each current Canonical unit to twelve frozen worksheet fields, validates row IDs/order, CSV schema, formula-prefix safety and optional externally supplied exact SHA pins, and enumerates stale units and per-field mismatch counts. It is **read-only**. The only success-like outcome possible is `CURRENT_WORKSHEET_ONLY_STAGE4_REVIEW_NOT_CERTIFIED`, explicitly with `stage4_semantic_pass=false` and `production_authorized=false`; if any field changes it returns `STALE_WORKSHEET_BLOCKS_STAGE4`, if malformed `BLOCKED_INVALID_REVIEW_SNAPSHOT`. Even after a future worksheet refresh it cannot certify independent review or source accuracy.

Example **diagnostic only** (on already SHA-verified exact WIP50 ZIP; never edits ZIP):

```bash
python Verification/audit_stage4_current_worksheet_freshness.py \
  --zip path/to/known-exact-WIP50.zip \
  --expected-canonical-sha256 fe50217d519edbb1c4d5eb5fc4da36faf1f562e859ccfe58b0153dbf684c48aa \
  --expected-worksheet-sha256 30486336c3f920aee70f8f4ee4adbc6ee2991033ed2ed9921cf64e29bcc3116d
```

Synthetic CI tests cover benign unsigned sheet, seven frozen-field mutation types, checksum pin mismatch, duplicate headers, broken JSON, reviewer field injection and non-certification.

## Needed to advance Stage4; not done here

Regenerate a **separately scoped and explicitly authorized** successor reviewer snapshot from the exact current immutable Canonical+Import bytes; pin the baseline and relevant source evidence. Use stable IDs and the preserved two source PDFs. Run independent-method source/DE/FA/EN/relation/rection semantic review for all 788 units, record disjoint decisions and evidence with source locators, apply permitted edits directly to named mutable authority only after scope approval, retest and rebaseline after each actual change, independently verify completed reviewer receipts. This requires separate content-workstream authorization; generic optimization `ادامه بده` does not give it. Stage5/6/7 remain blocked.

**Issuer/signing status:** actual Git author and committed ancestry are observable but independently authenticated authorizer/signature remains UNVERIFIED. This diagnostic supplies no signatures and cannot manufacture authority.
