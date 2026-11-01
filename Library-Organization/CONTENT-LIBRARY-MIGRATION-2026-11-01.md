# Content Library project-folder migration — 2026-11-01

Status: PARTIAL, NOT FINAL. No deletion or LOCKED/CURRENT/FINAL movement.
Project root: `/Flasch kart/German-Content-Production-Kit/Content`.

Verified moves this turn:
- 18 historical 250-Verben review reports moved into the project's Imported-Legacy/Historical-Review.
- Two NVV historical review folders (nine files) moved into NVV Imported-Legacy/Historical-Review.
- Created folders for Menschen-A2-Verben, Menschen-Portfolio, Grammatik-Aktiv-A1-C1, and Bildkarten-Piloten.
- Corrected v3.3.6 portable prompt Library locator in GitHub (commit 81dd5f65bcd2adc25e1a52b9b07d530d86836822).

Read-only inventory: Checkpoints contains 2,847 files, 3,340,989,726 bytes. Git references many old paths; these files must NOT be bulk moved.
Current contains three subfolders, Final contains two files; both stay in place.
Review has **0 files** after the verified third batch. Active WIP27 review and scoped policy/validator are retained in explicit project folders.
Library storage limit was reached: prefer moves over duplicates.

Batch 2 — 2026-11-01, independently verified (nine historical files):
- Moved WIP3–WIP6 and WIP24–WIP26 report files, plus two earlier didactic reports; 9/9 move API successes.
- Raw-byte files were materialized before and after: 9/9 exact SHA-256 AND byte-equality PASS; aggregate 38,354 bytes.
- All nine stable Library file IDs were preserved. Historical-Review now contains 27 files (18 first-batch + 9 second-batch), and Review contains 3 files.
- Exact old/new prefix, name, stable ID, file byte size and SHA-256 for each move are persisted in `Library-Organization/CONTENT-PROJECT-FOLDERS.json → legacy_library_path_resolution.moved_review_250verben_batch2`.
- Git's immutable historical milestone paths were not mass rewritten. Stable Library IDs resolve first, with an explicit relocation ledger for pathname fallback.
- The latest WIP27 report and the v1.2.0 policy/validator are ACTIVE references; they remain unmoved pending a separate active pointer audit.
- No deletion, source card edit, LOCKED/CURRENT/FINAL or protected Checkpoints mutation. No Stage4–7 promotion.

Batch 3 — 2026-11-01, active Review triage and relocation:
- Verified the three remaining files in live Review; read active WIP27 workstream LATEST and milestone: all three are referenced there by stable Library IDs, not hardcoded old Review paths.
- Git main code search found no direct Review pathname references for these three; original Git policy and validator under `Prompt/` and `Verification/` remain unchanged.
- Created `Content/250-Verben-mit-Praepositionen/Active-Review` for the WIP27 report and `Active-Contracts` for the HF2 v1.2.0 policy and Python validator.
- Moved all 3 by stable library_file_id, re-listed old/new directories and rematerialized all 3 files. Exact raw bytes, SHA-256 and persistent IDs: 3/3 PASS, 11,804 bytes. Old Review contains 0 files.
- Exact per-file old/new paths, stable IDs and SHA-256 recorded in `Library-Organization/CONTENT-PROJECT-FOLDERS.json`; active WIP27 milestone and LATEST were not modified. This is a Library organization pass, **not** WIP27 Stage4/5/6/7 promotion.

Protected Checkpoints inventory — full read-only scan completed:
- 15 paginated name-ascending reads: 2,847 files / 3,340,989,726 bytes; 2,847 distinct stable Library IDs, zero duplicates, zero missing-size records.
- File types: 1,701 ZIPs, 900 JSONs, 179 .sha256 sidecars and other text/scripts. Grouped by a cautious **filename-only heuristic**; 78 ambiguous files remain UNCLASSIFIED for ownership purposes.
- Prior reported counts and bytes matched exactly. Two important pinned checkpoint filenames/Library IDs were located, but this scan did not rehash all 2,847 archive bytes or trace all Git dependencies.
- Compact machine-readable report: `Library-Organization/PROTECTED-CHECKPOINTS-INVENTORY-2026-11-01.json` (live Git readback verified).
- `Current`: three subfolders unchanged. `Final`: two files unchanged. `Checkpoints`: all 2,847 files remain unmoved.
- Nothing deleted, overwritten, LOCKED/CURRENT/FINAL-promoted or source-modified. Do not infer duplicate/safe-to-remove status from filename, size, or version alone.

Previous next action (now partially completed): exact active dependency graph for high-value Checkpoints (Git workstream LATEST + receipts + stable Library ID + verified raw SHA/backup); only then select safe individual relocations. This migration is still PARTIAL, NOT FINAL.


Selected protected Checkpoints exact binary dependency audit — 2026-11-01:
- Materialized and independently SHA-256 hashed 4 live Library ZIPs: 250-Verben WIP25, WIP26, WIP27 and Content Production Kit v3.3.6. Four outer archive identities and ZIP CRC PASS, with 957/957 internal file checksums PASS (234+246+252+225). The framework's 37 additional ZIP entries are directories, not unhashed files.
- WIP26 embedded parent ZIP SHA exactly matches tested WIP25; WIP27 parent matches tested WIP26. WIP25 records a WIP24 parent not materialized in this round. Three versions have different outer hashes and distinct embedded QA/evidence; no byte-identical outer ZIP duplicates proven.
- Historical Milestone Google Drive backups were referenced by ID but *not* independently downloaded or SHA verified in this turn. Any global OP-05 duplicate/deletion decision remains BLOCKED pending both-native-copy proofs and explicit approval.
- Durable exact binary dependency report: `Library-Organization/ACTIVE-CHECKPOINT-DEPENDENCY-2026-11-01.json` (Git readback PASS).
- No Checkpoints moved, deleted or overwritten; content workstream LATEST, LOCKED, CURRENT, FINAL and app/runtime unchanged. Selected scope is 4/2847 archives, not a global inventory quality certification.

Next: exact byte audit of the missing WIP24 parent, then compare independently named Library copy candidates with both native file identities and backup/retention checks. Never delete based only on filename, size, or similar internal ZIP members. Migration remains PARTIAL, NOT FINAL.
