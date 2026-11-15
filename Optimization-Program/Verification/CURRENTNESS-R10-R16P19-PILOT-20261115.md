# COP status-currentness gate — A1 Verben pilot, 2026-11-15

## Why this exists
A status review initially used the Git source-owner R10 content-final pointer and missed the actual, newer R16-P19 working content in Drive. This is the same pre-Git failure class: root/global pointers or chat recollection selected as present-day work before reading the newest available user artifact.

This patch **adds an executable evidence checker to the existing workstream-resume policy**. It is not an independent semantic Stage4 test, content promotion, additional ZIP, or new source authority.

## Evidence from the real owner file
- Official accepted baseline: R10, 2026-11-06, SHA-256 `790e7a39f2c814b59e3aceccb7cc7a9658d18b8c0980187c3d7af1370a53cd47`, previously verified Drive archive `1FraH6tao4PwPHdQlKfkscJVewS409qL0`. **Not re-downloaded for this pilot.**
- Most recent observed working master: R16-P19, 2026-11-15, exact actual JSON file `Menschen-A1-Verben-R16-P19-STAGE4-SELF-QA-310-Work-Master-NONIMPORT.json`, Drive `1HszAmBPwbPs5Ahg1IIZNoKmYyjJeuiEi`, SHA-256 `5f832f62f5a8dac980d46855bfbc14b41d87d91504abfc1115edadab67be11cb`, **fresh raw byte hashing PASS**.
- Parsed R16-P19 actual content: **310 unique card IDs**. The separate Stage5 receipt records 310 cards and 1,240 examples; Stage5 preflight is not a full installed-app release.
- Old false claim `current_working_id=R10` was **FAIL_STALE_OR_CORRUPT**. Correct split `current_working_id=R16-P19` and `accepted_baseline_id=R10` returned **PASS_OBSERVED_STATUS_CLAIM**, with explicit `R10=METADATA_ONLY` warning.
- Local unit run: **8/8 tests PASS** (old-final-as-current, correct split, missing file, skipped Library discovery, hash mismatch, two active working candidates, unresolved competing candidate, no claim).

## Use

1. Inspect live conversation/Project sources/Library/Drive and source-owner Git LATEST/CHECKPOINT; open the actual working file when accessible. Do not infer from filename/date, root summary, or a successful old Git receipt.
2. Create one short JSON evidence document with schema `gcpk-status-currentness-evidence@1`, workstream, actual provider observations, and observed artifacts. Each artifact has `id`, `role` (`working`, `accepted`, or `historical`), `sha256`, `provider`, `locator`, `active`, and for byte validation a local `path`. Supply the claimed `current_working_id` and `accepted_baseline_id` separately.
3. Run `python Tools/status_currentness_gate_v1.py evidence.json`. Exit 0 = claims match the **observed** evidence. Nonzero = stale, corrupted, ambiguous or insufficient evidence.
4. Run tests with `python -m unittest discover -s Verification -p test_status_currentness_gate_v1.py -v`.

## Honest boundaries
- The checker **does not independently search private providers**; provider discovery must actually be performed by the agent. A faked observation is not verified by this script. No GitHub CI can establish a claim that a user's private Drive/Library has no newer file.
- `PASS_OBSERVED_STATUS_CLAIM` is limited to candidates supplied and actual verified bytes; no unconditional global latest guarantee.
- An accepted baseline already byte-verified in an earlier receipt may be represented as metadata-only; it must be labeled as such in the report.
- Do not promote a new working candidate to `accepted`, `FINAL` or `Stage7` based on this gate.
- If a real current/accepted file is unavailable, report the **specific incomplete evidence**, not an old version as current.
- Run only once at a meaningful status/handoff; no repeat per card, no full Stage4 rerun, and no mutation of content/LOCKED/app/SRS.
- Test pilot first. Do not advertise this as universal automated enforcement until all relevant startup/reporting adapters call the gate and provider enumeration has been evidenced.
