# GFP-OPT P1 — Independent remote main + Library byte readback v1

**Program:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`)
**Controller:** Project Control Center
**Stage:** P1 still OPEN. This is an evidence gate, not a content producer, app modification or blanket policy propagation.
**Implementation:** [`Verification/verify_remote_policy_adoption_v1.py`](../../Verification/verify_remote_policy_adoption_v1.py)

## What the new finalizer verifies, independently

1. Resolve the **named lexical family and workspace** from exact blob-pinned global catalog and applicability profiles. Do not coerce Grammar, Lesen, Schreiben, visual, generic Vocabulary or mixed sources into vocabulary Stage5.
2. Fetch the actual **GitHub REST `main` HEAD commit SHA**, and fetch that workstream's `LATEST.json` via `contents/<path>?ref=<immutable head sha>`. Validate API-returned Git blob SHA against decoded raw JSON, workstream ID and recognized Stage5 status.
3. Replay the local source-owned prior gate using **the actual four source-role files, the official new governed Stage5 receipt, full ZIP CRC, every inner SHA256SUMS entry, embedded TSV and the exact centrally pinned validator + builder**. The input LATEST is written temporarily from the actual remote GitHub response, not read from a potentially forged checkout.
4. Compare a **separate materialized Library file copy** against the actual produced ZIP: SHA256, file name, byte length, CRC, and the `libfile_*` ID and Library path declared by GitHub `LATEST.json`. Distinguish the Library record ID from the materialized `file_*` ID.
5. Fetch `main` HEAD again. If it moved during the readback, fail closed and require a new full evaluation.
6. Return `PASS_LIVE_GITHUB_MAIN_AND_SEPARATE_LIBRARY_COPY_BYTE_PARITY__ADOPTION_HELD` and a write-once scoped report outside source/Git trees. The report **never** asserts `ADOPTED`, CURRENT, Stage4, formal Stage5 acceptance, actual native-browser Stage6, Stage7 or FINAL.

This is a stronger and more specific gate than a README declaration, a synthetic validator test, a historical matching ZIP hash, or a user's local file path. It is also *deliberately not* a source-owner approval mechanism.

## Important provider-authentication boundary

This CLI **can independently query GitHub** using HTTPS REST (optional `GITHUB_TOKEN` from environment; no token stored in a report). **It cannot log in to ChatGPT Library itself.** The copy and `file_*` / `libfile_*` metadata must be materialized through an authorized Library connector by the operator. The CLI checks their *byte agreement* against the exact authenticated GitHub pointer, but **cannot cryptographically attest that the operator-supplied copy really came from Library**.

Therefore the status remains `ADOPTION_HELD` until an **independently verified Library provider retrieval**, source-owner approved currentness and semantic/stage QA are supplied and persisted. Do not label a pass from this code as final remote provenance or 34/34 policy adoption.

## Run on a NEW authorized native producer artifact

```bash
# Preconditions: explicit eligible source-owner authorization and a new
# governed builder ZIP + native receipt already produced by the source workstream.
# The Library copy should be independently downloaded/materialized from
# the exact provider record in its live source LATEST.
python -B Verification/verify_remote_policy_adoption_v1.py \
  --family-id family:250-verben-mit-praepositionen \
  --workspace-id workspace:250-verben-mit-praepositionen-lexical-enrichment-v1 \
  --source-dir /actual/source-owner/approved/Stage5-four-inputs \
  --governed-zip /actual/new/governed-output.zip \
  --native-receipt /actual/new/write-once-governed-receipt.json \
  --library-copy /materialized/provider-copy-of-that-output.zip \
  --library-file-id file_0000... \
  --library-record-id libfile_0000... \
  --library-path '/Flasch kart/German-Content-Production-Kit/Content/.../governed-output.zip' \
  --new-report /separate/handoff/new-remote-byte-evidence.json
```

GitHub's LIVE `main` is mandatory; local fake `LATEST` files are ignored. The report uses **exclusive create** and cannot replace the original receipt, source, local checkout or a previous report. GitHub branch movement, source mismatch, forged native receipt, wrong provider ID, wrong ZIP hash, or any altered metadata fails closed.

CI [`gfp-opt-p1-independent-remote-adoption.yml`](../../.github/workflows/gfp-opt-p1-independent-remote-adoption.yml) tests the genuine governed/native builder against **synthetic sources** with stub GitHub REST and separately copied fake Library bytes. This tests the decision logic, not live provider authentication. The main GitHub / Library connector output must be independently acquired for an actual source.

## Fresh real connector readback on historical 250 Verben R8

The [actual new real-byte report](../Verification/P1-REAL-LIVE-CONNECTOR-R8-NONADOPTION-20261105.json) documents a **fresh** ChatGPT Library connector `files.list + files.materialize(raw_file)` and new GitHub `main` source `LATEST.json` readback, with independent full archive SHA256, size, CRC and TSV member SHA checks:

- Library record: `libfile_4d5d9f93546c8191b68333affcdf54bb`, original file `file_00000000552081f49aabbe90ab503306`
- GitHub main `LATEST.json` Git blob: `074c4eef64fec30ab9f7b63ae227fbede8ba8e65`
- Actual ZIP digest: `63ae8f2a3a8d2ec5dff94798db3ed060a0b4e43b1cc2699e540beb1393882e5c` at **3,856,786 bytes**; CRC PASS, **30** members
- Native clean TSV digest: `d23a5b9865d9e35b7ec24fa4f94fe8d94ee9f65fb990f8da7ffed41c75435191`
- The GitHub LATEST and exact freshly materialized Library bytes agree. **Nevertheless, R8 was built under the earlier clean-delivery process and has NO receipt issued by the new GFP-OPT governed-launcher path**. It must remain **historically valid, NOT newly ADOPTED**, and it is **not** a new Stage6/7 app release.

This real-world negative case is an essential Control Center guard: **two independent remote copies matching is necessary, but insufficient to certify a rule was used by a newly governed producer.**

## Next actions / publication

- Continue P1 with named **future source-owner authorized** real governed Stage5 runs; verify remote byte parity after publication and obtain independent Library connector provenance.
- Add a separately authorized, reviewable **producer adoption ledger entry** only after owner/source authority, exact policy version, current/source fidelity and proper Stage evidence. This finalizer deliberately refuses blanket `ADOPTED`.
- Extend the concept to source-specific, *non-neutral* adapters for Grammar, Lesen, Schreiben and visual/mixed workstreams. Keep provenance, stage and immutable history boundaries independent.
- Feed the typed statuses to P3 dashboard: `ROUTED`, `ELIGIBLE`, `GOVERNED_BUILD_OUTPUT`, `REMOTE_BYTES_MATCH`, `PROVIDER_AUTH_HOLD`, `SOURCE_OWNER_QA_HOLD`, `ADOPTED` only when the full chain is separately authorized and confirmed.
