# Project Control Center v1 — Phase 1

This is a read-only project identity catalog and live Git-index navigation report, not a new content authority or an app UI change.

The catalog MASTER-PROJECT-CATALOG-v1.json records 21 observed Library content families, 34 Git workspace directories and 17 root workstream mappings. It does not contain stage status or accept any content.

Run python Tools/build_project_control_center_v1.py --check --output-dir control-center-output to produce CONTROL-CENTER.json and CONTROL-CENTER.md. The Project Control Center GitHub Actions workflow publishes both as downloadable build artifacts and displays the Markdown table in the job summary.

The exact Git index is the only input to the generated snapshot. LATEST.json takes priority over CHECKPOINT.json for a navigation hint, but the underlying source artifact, milestone receipts and SHA must be checked independently. New user-confirmed artifacts can supersede Git. Central PROJECT-STATE.json is a potentially stale summary.

New unregistered workspaces, missing pointers, and unavailable checkpoint paths are reported as metadata issues, not invented stage completion or missing user source. This tool never modifies cards, content, LOCKED files, source, app runtime, UI, or FSRS/SRS.

Future phases: dependency graph; source-specific adapter and semantic QA adoption; duplicate artifact lifecycle and release reproducibility. Do not claim entire-project PASS from this first phase.
