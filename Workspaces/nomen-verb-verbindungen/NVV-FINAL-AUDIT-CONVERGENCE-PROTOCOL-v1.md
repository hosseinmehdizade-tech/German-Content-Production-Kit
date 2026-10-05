# NVV Final Comprehensive Audit Convergence Protocol v1

Status: ACTIVE — explicitly approved 2026-10-05  
Decision: `MEM-NVV-003-FINAL-COMPREHENSIVE-AUDIT-CONVERGENCE`

## Frozen baseline
- Parent artifact: `NVV-v3.3.6-Stage4-Round10-SystemicSweep-S9-EnglishIdiomaticity-12REPAIRS-PASS-CHECKPOINT.zip`
- Parent artifact SHA-256: `8a1199b8e88d4f063184e989205987e24d4c22e63d93f1d7c4a008142a3a762b`
- Frozen learner-core SHA-256: `1ccc2e98906eee23f3aea313e4f3a48fbf182c7677a97b20dbfa3d9d4a5f7153`
- Targets: 2492
- Rule: learner content is immutable during the full audit. Findings are logged only.

## Phase A — one real full-corpus audit
Review all 2492 targets exactly once on the frozen S9 core using the same all-dimension rubric:
1. source/canonical identity and source-surface fidelity;
2. German definition correctness, naturalness, sense coverage and register;
3. Persian meaning correctness, naturalness, valency/directionality and register;
4. English gloss correctness, idiomaticity, sense coverage and register;
5. structure/valency/case/preposition evidence;
6. all four DE examples for grammar, idiomaticity, target-bearing use, diversity and sense fit;
7. all four FA examples for faithful/natural alignment and role/tense/modality preservation;
8. all four EN examples for faithful/idiomatic alignment and role/tense/modality preservation;
9. row-level DE/FA/EN cross-language alignment;
10. example diversity and template/calque artifacts.

Default atomic shard is 100 targets; final shard is 92. Do not apply repairs before 2492/2492 is audited.

## Phase B — one bounded batch repair
After full coverage, adjudicate all logged findings and apply all confirmed repairs in one bounded repair wave. Recompute affected Stage3C closure evidence and produce one repaired successor. Adequate content is not rewritten merely for style uniformity.

## Phase C — bounded verification
- Re-audit 100% of changed targets and every changed learner field/example row.
- Run a corpus-wide root-cause sweep for each recurrent defect family.
- Verify a deterministic stratified sample of at least 500 unchanged targets from the exact repaired core.
- Five position bands contribute 100 clean unchanged targets each; within each band, quotas are proportional across `fvg`, `idiom_redewendung`, and `general_nvv`.
- Ranking inside each stratum is SHA-256(`final_repaired_core_sha256 + "|" + expression_id`), ascending.
- If a sampled target needs repair, it moves to the changed set, is repaired + reverified, and is replaced from the same stratum until 500 unchanged targets remain clean.
- A recurrent family triggers a corpus-wide family sweep, not another 2492-target restart.
- If the unchanged sample exposes more than 25 confirmed defects, Stage4 blocks for process review rather than claiming convergence.

## Stage4 close gate
Stage4 can close when:
- 2492/2492 full audit is complete;
- every confirmed finding is closed;
- source/identity/structure invariants pass;
- official v3.3.6 closure remains PASS with 0 unresolved cells;
- 100% changed-target verification passes;
- every recurrent family is exhausted;
- 500 deterministic stratified unchanged targets are independently clean;
- no unresolved BLOCKER or MAJOR finding remains.

The former requirement for two consecutive full 2492-target clean passes is superseded only for this scoped final-convergence phase.
