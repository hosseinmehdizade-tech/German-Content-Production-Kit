# GFP-OPT P1 — First native nonlexical adapter: actual Lesen Stage1 derived-byte replay

**Program:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`)  
**Component:** Project Control Center  
**Status:** **Actual native Git-derived data validation implemented. Source PDF binary/currentness, new producer Stage2+ and full policy adoption NOT verified.**

## Why this is a real improvement over shadow-only routing

Until now the eight nonlexical source profiles only mapped **who would need an adapter**. The new [independent native Lesen Stage1 replay](../../Verification/replay_lesen_stage1_native_v1.py) actually reads the existing **real, tracked Git blobs** for `Workspaces/lesen-praesentation`, computes original derived-file SHA-256 and tests the native reading data contract. This is not a synthetic illustration or a vocabulary TSV coercion.

It reads:
- `SOURCE-REGISTRY.json`, exact `presentation-topics-b2-c1` source identity and published source SHA;
- `00-source/SOURCE-MANIFEST.json` (reading-specific source role and non-verbatim runtime policy);
- `01-inventory/SOURCE-INVENTORY.json` and `STABLE-ID-MAP.json`;
- `01-inventory/INVENTORY-QA.json`, whose pinned SHA256 of both preceding actual files is recomputed;
- the native `CHECKPOINT.json`, which already records Stage1 PASS and Stages2–7 NOT_STARTED.

The replay **independently reconstructs** the native contract from those bytes:

| Source-derived invariant | Replayed evidence |
| --- | ---: |
| Source-ordered topics and unique stable IDs | **68** |
| PDF page-accounting records, no omissions or duplicate page numbers | **76** |
| Continuation pages assigned to their original topic | **6** |
| Explicit blank pages | **1** (page 3) |
| Duplicate occurrences (not another new topic) | **1** (page 69 from page 68) |
| Unnumbered distinct topic starts | **1** (page 35) |
| Native ID-map exact agreement with inventory | all **68** |
| Source identity/manifest/QA/Checkpoint cross-consistency | exact Git-index data |

Source numbering is deliberately **not** required to be unique: repeated number tokens in the original topic headings are preserved as source metadata, not force-renumbered. The SHA256 recorded in the original Stage1 QA is compared to the *actual* Git-derived file bytes, and the checkpoint's original seven-stage boundary must remain unchanged.

## Strict proof limits

This new tool certifies only **`PASS_ACTUAL_GIT_READING_STAGE1_DERIVED_BYTES_AND_STRUCTURE_REPLAY_ONLY`**. It does not download or re-extract the original copyrighted `Präsentation.pdf`, which is intentionally outside Git. The original source SHA is known from the registry and previous source manifest, **not independently rehashed here**. It does not certify semantic/source fidelity beyond derived structural QA, user-later source precedence, any Stage2 rewriting, Stage4 linguistic quality, Stage5 delivery, Stage6 app browser or Stage7 release. Nor does it prove any producer has consumed a new governing policy at an authorized mutable boundary; **policy `ADOPTED` remains zero**.

This distinction avoids an incorrect `PASS` when only Git metadata survives, and ensures later source modifications fail closed until native derived evidence is internally consistent.

## Central integration and test

The [nonlexical source preflight](../../Tools/build_domain_adapter_preflight_v1.py) now calls this real byte replay for **family:lesen** and embeds its proof, actual tracked Git blobs, counts and unchanged acceptance limits. The **existing** [unified policy-adoption dashboard](../../Tools/build_policy_adoption_control_center_v1.py) includes that same proof under the Lesen family and explicitly labels all other nonlexical producers as SHADOW/HOLD. No second authority or unrelated duplicate dashboard was introduced.

Run in the Content Kit checkout:

```bash
python -B Verification/replay_lesen_stage1_native_v1.py \
  --summary --new-report /new/external/path/reading-stage1.json

python -B Tools/build_domain_adapter_preflight_v1.py \
  --summary --output /new/external/path/domain-preflight.json

python -B Tools/build_policy_adoption_control_center_v1.py \
  --output-dir /new/external/path/control-center
```

The three existing/source-specific GitHub Actions workflows run this on **Ubuntu and Windows**. The native [25 adversarial tests](../../Verification/tests/test_lesen_native_stage1_replay_v1.py) deliberately mutate page membership, topic order, source identity, old QA SHA, NFC source headings, duplicate occurrences and Stage2/Stage4 claims; they must fail. All outputs are write-once and outside protected Content Kit directories.

## Safe next action

1. To mark Lesen **source PDF bytes independently reverified**, obtain the real, current source-owned original PDF and compare it to the registry SHA (and any explicitly newer user-supplied source); do not infer from its filename or regenerate the PDF.
2. Implement separate native **Stage2 reading canonical** producer at the workstream's approved mutable boundary with a source-specific typed output and independently checked QA, not a vocabulary clean delivery clone.
3. Resolve the remaining five root CHECKPOINT metadata HOLDs by locating each owner's actual newest valid authority. Never create, silently redirect or overwrite Checkpoint files to make the dashboard green.
4. Add Grammar and Schreiben adapters only when their own source/currentness and producer contracts are available. No source/LOCKED/card or app/UI/FSRS modifications in this optimization branch.

**Governance:** source-owned immutable checkpoint authority, Git index snapshots and independent QA have separate responsibilities. `PASS` for the derived Stage1 replay is **not** a producer release, formal adoption or source CURRENT.
