# Aber Hallo — Runtime Authority Reconciliation — 2026-10-08

## Verdict

**CONTENT LOCK PRESERVED / RUNTIME REBASE REQUIRED.**

The portable Library contains a later Stage7 artifact that closed the original v465 grammar-ingestion blocker by bundling the one Aber Hallo grammar unit into a v466/R100 successor. That artifact is real and internally coherent, but its runtime bytes are **not** the same v466/R100 runtime that subsequently became project CURRENT and LAST_FULLY_VERIFIED.

Therefore the Aber Hallo content remains locked, while the old integrated runtime package must not be treated as the current development/integration base.

## Verified portable Stage7 content artifact

- Artifact: `German-Flashcards-Pro-v466-R100-Aber-Hallo-v3.3.6-LOCKED-CONTENT.zip`
- SHA-256: `799ae7fce8c10965b62fb1288f1e1494617a575249aef6abe63af6955a47f175`
- Size: 6,956,424 bytes
- ZIP members: 383
- Duplicate members: 0
- CRC: PASS
- Root SHA256SUMS: 382/382 PASS
- Content: 787 lexical cards (647 verbs, 140 adjectives) + 1 grammar unit
- Grammar extension: `ahl-lu-0001`, title `Deklination: Artikel, Negation und Personalpronomen`, 4/4 examples, 0 exercises
- Grammar baseline: original 168 units / 346 exercises preserved; extension makes 169 units / 346 exercises

Exact Library materialization was independently re-hashed in this reconciliation turn and matched the recorded outer SHA-256.

## Runtime identity mismatch

Historical Aber-Hallo integrated package labeled **v466-R100**:
- index/app SHA-256: `cafb71d29f59f8ac74326cc875cfedcbbdcefed23145cfe562be07077cd4d00c`
- service-worker SHA-256: `12843e5cbd8dc51e03fdab544f9c51b7062d6d554babf229734df40ae7687792`
- grammar bundled runtime SHA-256: `6677fbac5fb799c5b27dd601a67c14d297f0f55a5254475a49787c32728fdcbd`
- runtime files: 72
- `modules/pomodoro-runtime-v466.js`: absent

Project CURRENT / LAST_FULLY_VERIFIED **v466-R100**:
- organized artifact SHA-256: `506fcdd4d062550a907ef6ef58d3a3fa185ee850631977d40145d6c7100861a8`
- index/app SHA-256: `f99fecf1587f4fc93d59f1321a3ef347917068602a3f81a4c74f72843dfe4194`
- service-worker SHA-256: `2d3a06abd1ad0d4b2799182e37b4f04c940c0a8e8530d8133bffc7861d754efa`
- runtime files: 73
- `modules/pomodoro-runtime-v466.js`: present, SHA-256 `5c7573c03cf80379e5fa730aa521bdf8629bf6bb86cb4ce195683396c9331de9`

Direct runtime-tree comparison found five logical differences:
1. `index.html`
2. `German-Flashcards-Pro-v466.html`
3. `service-worker.js`
4. `modules/grammar-bundled-runtime-v2.js`
5. `modules/pomodoro-runtime-v466.js` (missing from the historical Aber-Hallo package)

The historical package therefore belongs to an earlier parallel v466 lineage and cannot supersede the later Pomodoro-modularized v466 CURRENT.

## Authority decision

- Do **not** reopen or regenerate the 787 lexical cards.
- Do **not** discard the tested grammar extension.
- Do **not** downgrade CURRENT to the historical Aber-Hallo v466 runtime.
- Rebase only the tested grammar extension onto exact CURRENT/LAST_FULLY_VERIFIED v466-R100.
- Because runtime-reachable grammar bytes change, the rebased integration must use the next runtime identity, **v467-R101**, not reuse v466-R100.
- Preserve the existing UI/UX; no layout/CSS redesign is authorized or required.

## Next milestone

Create a v467-R101 successor from exact CURRENT v466-R100, transplant the already-tested grammar extension into `grammar.runtime.v2`, preserve the Pomodoro module and all other current runtime bytes, reseal the shell/version cohort, run exact Stage6/runtime regressions and package verification, then produce the Stage7 locked Aber-Hallo release only after those gates pass.

The prior v466 Stage7 artifact remains immutable historical evidence for content/grammar integration, not the current runtime base.
