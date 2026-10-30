# OP-02 — Exact original ZIP pointer lineage, WIP65 → WIP66 → WIP67

**Status:** READ-ONLY REAL BINARY FINDING + NONACTIVE PUBLISHER PREFLIGHT.
No original source, original or successor learner ZIP, workstream
LATEST, LOCKED artifact, application/runtime/UI or GitHub permission
is changed in this optimization branch.

## Historical exact-byte evidence

The **original** WIP65 and WIP66 recovery ZIPs were found at the
registered `/German-Content-Production-Kit/Checkpoints/` Library
folder, copied read-only, and their raw bytes SHA256 matched the exact
registered hashes:

| Original ZIP | Actual SHA256 | Embedded pointer | Main/working canonical & import SHA256 | Pointer SHA256 |
| --- | --- | --- | --- | --- |
| WIP65, 7,869,563 bytes | `db1b8efb89b5492f0d7b6ab52ae8b3de8b595377aa5a400b68452e742c4a5aa2` | WIP65 | MATCH / MATCH | `d2b56cd41a76f33d0b98ace3a1ec7918a8c8d0e38c0482074705fe82064f44fb` |
| WIP66, 7,964,990 bytes | `43f1bd54621aae319e073654b625fd47c3c63dad9ec29e45775f1f53d3c75b1c` | WIP66 | MATCH / MATCH | `2770c722c1b0684168b3f620daa61a56c827718cf6dc8509b7c188d6ed9c7103` |
| WIP67, 7,993,869 bytes | `ec0c21d31b20b1850b639a4263b75109bc0795f78d449799bce9768b08e8e275` | **WIP66** | **MISMATCH / MISMATCH** | `2770c722c1b0684168b3f620daa61a56c827718cf6dc8509b7c188d6ed9c7103` |

Full original member bytes of
`07-Checkpoint-State/CURRENT-WORKSTREAM-POINTER.json` are **identical**
between WIP66 and WIP67 (5,339 bytes; same SHA256). By contrast WIP65
and WIP66 pointers differ, and each matches the respective
canonical and import bytes. This strongly supports one-step **stale
parent pointer reuse** at WIP67 assembly. The precise script or writer
responsible is NOT established; no speculative culprit is asserted.

The original WIP67 ZIP has correct outer hash, 449-member CRC,
448 SHA256SUMS, 447 MANIFEST entries, embedded PDFs and canonical/import
content cardinality. All this coexists with the erroneous pointer.
An integrity PASS without release-metadata role checks is insufficient.

## Independent original-ZIP lineage tool

`Verification/audit_op02_parent_pointer_lineage.py` takes paths of
the two original ZIPs plus an externally supplied exact snapshot:
workstream, CURRENT and parent SHA256, named CURRENT milestone and
parent version. It does not accept self-declared issuer credentials.

It separately reads original ZIP bytes and checks exact SHA256/size
bounds/CRC/duplicates/safe paths, then compares child/parent pointer
member bytes, parent and current WIP versions, their canonical/import
SHA256 (both main and working aliases), and their MANIFEST version and
hash identities.

The CLI reads, prints one diagnostic and exits 2 for any mismatch.
Even a clean result says
`PASS_SCOPED_ORIGINAL_POINTER_LINEAGE_ONLY_NOT_RELEASE` and all
issuer/Stage4/5/6/7/release/writer flags remain false.
The separately supplied pins are **not authenticated** in this
nonactive tool; green CI is not a protected trust anchor.

## Producer-owned next-version recovery protocol (not executed)

1. Resolve the newest CURRENT **immediately** before producer work;
   WIP67 is only the present observed checkpoint. Do not overwrite or
   downgrade a newer CURRENT.
2. If a named successor is created by its **own authorized producer**,
   emit `07-Checkpoint-State/CURRENT-WORKSTREAM-POINTER.json` from
   the *successor's final canonical and import bytes*:
   `current`, `canonical_sha256`, `import_sha256`,
   `working_canonical_sha256`, `working_import_sha256`.
3. Preserve historical `wip66_scoped` evidence as *history*, but
   never reuse the active `current` and top-level current digests.
   Reconcile the `latest_verified_git_status` annotation to factual
   current stage without inventing a Git-backed PASS.
4. Regenerate MANIFEST and SHA256SUMS **after** making the correct
   active pointer, then make the portable ZIP and hash its outer bytes.
   Compare original predecessor and exact successor with the lineage
   guard AND full `Verification/audit_op02_real_archive_pointer.py`.
5. Promotion requires independent CURRENT/issuer authentication,
   source byte verification, single writer/CAS and completed relevant
   Stage4–7 gates. No old artifacts are mutated, and an unapproved
   successor is not published from this optimization workflow.
6. If any prepublish check fails, stop, retain original CURRENT and
   recorded parent bytes intact. Do not report FINAL or artificially
   advance the Stage gates.

## Security boundary

Content Kit main was observed unprotected, with no active rulesets.
OP-01 scope registry remains `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL`.
This tool does not change GitHub permissions or authenticate user approval.
It is purely an independent cross-archive QA adapter; actual publishing
and security architecture decisions remain separately gated.
