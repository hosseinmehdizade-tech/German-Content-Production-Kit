# Project Control Center v1 — Phase 1

This is a read-only project identity catalog and live Git-index navigation report, not a new content authority or an app UI change.

The catalog MASTER-PROJECT-CATALOG-v1.json records 21 observed Library content families, 34 Git workspace directories and 17 root workstream mappings. It does not contain stage status or accept any content.

Run python Tools/build_project_control_center_v1.py --check --output-dir control-center-output to produce CONTROL-CENTER.json and CONTROL-CENTER.md. The Project Control Center GitHub Actions workflow publishes both as downloadable build artifacts and displays the Markdown table in the job summary.

The exact Git index is the only input to the generated snapshot. LATEST.json takes priority over CHECKPOINT.json for a navigation hint, but the underlying source artifact, milestone receipts and SHA must be checked independently. New user-confirmed artifacts can supersede Git. Central PROJECT-STATE.json is a potentially stale summary.

New unregistered workspaces, missing pointers, and unavailable checkpoint paths are reported as metadata issues, not invented stage completion or missing user source. This tool never modifies cards, content, LOCKED files, source, app runtime, UI, or FSRS/SRS.

Future phases: dependency graph; source-specific adapter and semantic QA adoption; duplicate artifact lifecycle and release reproducibility. Do not claim entire-project PASS from this first phase.

## Scoped historical evidence overlay — 2026-11-05

The [pinned historical evidence registry](EVIDENCE-REGISTRY-v1.json) now links real source/ZIP byte-readback receipts to existing identity namespaces, not to arbitrary folders: one **Git workspace** (250 Verben lexical R7) and one **root-only workstream** (Nomen-Verb-Verbindungen R6.1). The [attested overlay generator](../../Tools/build_attested_evidence_overlay_v1.py) produces a read-only 21-family / 34-Git-workspace / 17-root-workstream report via [Actions](../../.github/workflows/attested-evidence-overlay-v1.yml). Any non-attested workspace remains `NO_REAL_BYTE_ATTESTATION_REGISTERED` with **no** Stage PASS.

The 250 Verben historical R7 independently matched the user PDF, 25-member ZIP, 24/24 manifest entries, unchanged TSV, and exact pinned Stage4 **risk-evidence gate**. The independent NVV historical R6.1 check matched the user PDF, 55-member ZIP, 54/54 root `SHA256SUMS` entries, CRC and TSV content. NVV was not Stage4-reverified here; it has **no registered standalone Git workspace**. Both proofs remain historical and do not assert newest/current user artifact, native Stage6, Stage5 final or Stage7 release.

The GitHub runner validates exact Git-index receipt/profile pins and metadata relations, **not original PDF/Library ZIP binary bytes**. It fails closed on mismatched evidence, provenance hashes, ownership, or false Stage promotion. A new user-validated archive can supersede a historical receipt without deleting or rewriting it.

## Phase 6: three typed evidence records (2026-11-05)

The [historical evidence registry](EVIDENCE-REGISTRY-v1.json) now distinguishes **two full historical source+package byte readbacks** (250 Verben R7 as a real Git workspace; NVV R6.1 as a root-only workstream) from **one SOURCE-ANCHORED HISTORICAL record with a known intermediate lineage gap** (`workspace:aber-hallo-listen-tabellen`).

Aber Hallo's dated [Phase5 receipt](../Verification/CONTROL-CENTER-PHASE5-ABER-HALLO-SOURCE-ANCHOR-20261105.json) identifies two original PDFs byte-matched in a recovery archive, original v3.3.6 base and immutable WIP72 source archive, plus 788 unchanged canonical provenance arrays and 787 TSV identities from WIP72 to WIP92. [Phase4 receipt](../Verification/PHASE4-ABER-HALLO-WIP92-SCOPED-SOURCE-ARCHIVE-READBACK-20261105.json) separately matches the WIP92 compact archive's hashes and valid manifests. The Phase5 internal `phase4_receipt_path` string is stale/nonexistent; only the real Phase4 file, pinned by Git blob in the [new typed profile](Profiles/ABER-HALLO-WIP92-SOURCE-ANCHOR-20261105.json), can be used as evidence. The validator rejects missing/mismatched SHA, incorrect parent, fake Stage4/5/6/7 promotion, false contiguous WIP73–WIP91 edit-chain claims, and changes to the LATEST fingerprint that might be confused with CURRENT.

The classification is **not** a third complete source/ZIP proof: WIP92 excludes original source PDFs and WIP73–WIP91 intermediate archive bytes have not all been replayed. It is **not CURRENT**, Stage4 is **OPEN**, Stage5/6/7 are **NOT RUN**, and no real-browser result or source-to-card semantic acceptance follows from this index. The GitHub workflow reads pinned reports and runs synthetic attack tests, not real PDF/ZIP binary QA. Only navigation/QA metadata and synthetic tests changed; learner cards, workstream LATEST, originals, LOCKED source, runtime/UI and SRS/FSRS remain untouched.
