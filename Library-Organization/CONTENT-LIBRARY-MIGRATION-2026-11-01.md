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
Review now contains exactly 3 deliberately protected active/contract files: WIP27 governed subtype report, learner-front v1.2.0 policy, and its validator.
Library storage limit was reached: prefer moves over duplicates.

Batch 2 — 2026-11-01, independently verified (nine historical files):
- Moved WIP3–WIP6 and WIP24–WIP26 report files, plus two earlier didactic reports; 9/9 move API successes.
- Raw-byte files were materialized before and after: 9/9 exact SHA-256 AND byte-equality PASS; aggregate 38,354 bytes.
- All nine stable Library file IDs were preserved. Historical-Review now contains 27 files (18 first-batch + 9 second-batch), and Review contains 3 files.
- Exact old/new prefix, name, stable ID, file byte size and SHA-256 for each move are persisted in `Library-Organization/CONTENT-PROJECT-FOLDERS.json → legacy_library_path_resolution.moved_review_250verben_batch2`.
- Git's immutable historical milestone paths were not mass rewritten. Stable Library IDs resolve first, with an explicit relocation ledger for pathname fallback.
- The latest WIP27 report and the v1.2.0 policy/validator are ACTIVE references; they remain unmoved pending a separate active pointer audit.
- No deletion, source card edit, LOCKED/CURRENT/FINAL or protected Checkpoints mutation. No Stage4–7 promotion.

Next: review remaining three active Review files against active Git and Library references, and build only safe per-project manifest/index updates without filling Library with duplicates. Keep 2,847 protected Checkpoints where they are until a verified dependency ledger exists. Overall migration remains PARTIAL, NOT FINAL.
