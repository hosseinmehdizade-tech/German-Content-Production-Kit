# OP-02 — WIP67 real Library ZIP readback: exact bytes PASS, embedded CURRENT BLOCKED

**Classification:** Real binary QA evidence + nonactive reusable archive checker.
**Date:** 2026-10-30. **No learner cards, sources, content WIP successor,
LOCKED release, app/runtime, GitHub security setting or Library artifact
were edited by this optimization work.**

## Materialized original, not an inferred Git sidecar

The Library listing for
`/German-Content-Production-Kit/Checkpoints` returned the exact registered
WIP67 ZIP with Library ID
`libfile_e89cb9d24c308191af2d5874a2739611` and original length
7,993,869 bytes. The raw ZIP was copied read-only to the analysis container.
An independent direct Python zipfile/hashlib inspection of actual bytes found:

- Outer ZIP SHA256:
  `ec0c21d31b20b1850b639a4263b75109bc0795f78d449799bce9768b08e8e275`
  — **exactly** the independent Git LATEST and WIP67 receipt digest.
- 449 ZIP members, zero duplicate paths or symlink/path traversal issues,
  and `ZipFile.testzip() = None`: all CRCs intact.
- All **448** SHA256SUMS entries match the exact ZIP member contents; no
  absent, extra, duplicate or malformed lines. The single omitted
  SHA256SUMS self-entry is expected.
- MANIFEST lists **447** data members excluding itself and SHA256SUMS.
  Every entry name, length and SHA256 matches; exact coverage.
- Embedded two original source PDFs have the exact independently
  registered SHA256 hashes and sizes. The PDF bytes read from inside the
  ZIP were also byte-for-byte compared to the **two user-uploaded source
  PDFs** accessible in this session: 2 of 2 identical, no edits.
- Canonical JSON has 788 learning units. Import TSV has 787 card rows
  with 23 columns, no invalid row widths and no duplicate stable IDs.
  Exactly 3,152 trilingual example records, 1,097 Kombinationen and
  2,878 relation records parse as JSONL.
- Canonical digest
  `a6d6d63fad0f73093051ddd43fd491b6f5c62094288d40379bdd5b59d7b20fc5`,
  import TSV digest
  `3ec31fce4f769b2c1f266c239cf2c63bbcd513da950c7c2685a6a7304e5e047b`.
  All match the external WIP67 LATEST metadata and ZIP's current manifest.

## **Real defect: portable's embedded CURRENT pointer still WIP66**

Current external Git LATEST and the ZIP's own MANIFEST identify WIP67.
However the unambiguously active-named member
`07-Checkpoint-State/CURRENT-WORKSTREAM-POINTER.json` claims:

- `current = WIP66_16_EXACT_LEXICON_861_ATTESTED_120_HOLDS`
- `canonical_sha256 = 0f642168d96529fb32b6a90f3997eb69c9740c8d2f6c1c6d8417ffa2ce02ab74`
- `import_sha256 = 617c13856e2e2a3abfcffe12d6f013959bbedb14a61aec49487ffbbac6153ff4`

These point to the predecessor, **not** the WIP67 actual canonical and
import bytes. All ZIP checksums still pass because the wrong pointer
was consistently included and rehashed at package time. This
demonstrates why ZIP SHA256 integrity does **not** imply publication
metadata coherence or release eligibility.

**Disposition:** binary-byte-integrity PASS, embedded-current contract
BLOCKED, Stage4 OPEN, Stage5/6/7 NOT_RUN, issuer authentication
BLOCKED. Preserve the original WIP67 ZIP unchanged and do not
overwrite workstream LATEST from the optimization mission.

## Reusable, fail-closed prepublish QA mechanism (nonactive)

`Verification/audit_op02_real_archive_pointer.py` accepts an
independently supplied exact expected metadata snapshot + original
ZIP filesystem path. It verifies ZIP hash/size, CRC on every member,
safe paths, exact SHA256SUMS coverage, every MANIFEST file size and
digest, PDF source hashes, canonical/import bytes, card/example/
combination/relation cardinalities and internal current pointer version
plus hashes. **The only scoped green result requires no stale pointer.**

The separate negative tests simulate a complete, internally rehashed
WIP67 archive that nonetheless embeds WIP66. Such an archive MUST
return BLOCKED, not PASS. Synthetic future WIP69 confirms the parser
is not WIP67 hard-coded. Cross-platform CI is *not* a trusted issuer,
and the actual Library ZIP is not placed into GitHub CI.

## Corrective boundary / producer handoff

A separately authorized **producer-owned successor**, if and when
planned, must write current pointer/version/canonical and import hashes
from the *final generated payload* **before** constructing MANIFEST,
SHA256SUMS and outer ZIP, re-run exact-byte audit of the resulting
ZIP, and only then publish/promote with workstream-specific CAS.
Never silently patch the immutable WIP67 ZIP, copy old pointer claims,
declare Stage4 PASS, or restore an older CURRENT version.

The public Content Kit `main` was observed `protected=false`
and GitHub `GET /rulesets` returned `[]`. The writer registry remains
`DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL`. This optimization PR
does not activate issuer checks or change branch protection.
Independent publisher authorization, full AI semantic Stage4 review,
Stage5/6/7 runtime import and any final release remain blocked.

The machine-readable evidence snapshot:
`Optimization-Program/Verification/OP02-WIP67-REAL-BINARY-INTERNAL-POINTER-20261030.json`.
