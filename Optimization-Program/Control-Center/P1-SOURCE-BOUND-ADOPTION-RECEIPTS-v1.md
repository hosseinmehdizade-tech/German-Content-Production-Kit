# GFP-OPT P1 — Source-bound native policy adoption receipt v1

**Program:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`)
**Controller:** Project Control Center
**Scope:** exact native Stage5 governed builder receipt + actual complete ZIP + actual source inputs + Git-blob-pinned named-workstream `LATEST.json` comparison. **No new content production, source edits or stage promotions in this optimization task.**

## Why this milestone exists

The [15-policy impact map](P1-ALL-SOURCE-POLICY-IMPACT-MAP-v1.md) determines which projects *might* need a new rule. The [governed native Stage5 launcher](../../Tools/build_governed_clean_delivery_v1.py) can enforce an exact versioned Stage5 rule and write a byte-bound receipt. But **those two facts alone are not proof that any named producer has used the new controlled route**.

New [`Verification/verify_governed_source_adoption_v1.py`](../../Verification/verify_governed_source_adoption_v1.py) independently replays this chain:

```text
Exact family ID + exact workspace ID
              ↓
Git-blob-pinned 21-family catalog and source-domain profiles
              ↓
Four actual source files (TSV, Canonical, source map, QA)
              ↓
An ACTUAL receipt issued by the governed native Stage5 launcher
              ↓
The exact output ZIP: CRC, all internal SHA256SUMS,
embedded TSV SHA and neutral-policy replay
              ↓
A Git-blob-pinned named workstream LATEST.json in the checkout
whose status, archive name, SHA and bytes match the ZIP
              ↓
Write-once LOCAL VERIFIED CANDIDATE receipt
              ↓
INDEPENDENT remote Git main and Library byte readback still REQUIRED
before source-level policy adoption/acceptance can be claimed
```

Only lexical-source candidates whose actual native output follows the standard four-role neutral Stage5 envelope are eligible for this verifier. A generic imported Vocabulary project, grammar, Lesen, Schreiben, media and mixed output do not acquire a Stage5 vocabulary schema just because a catalog says they are in a policy scope.

## Example on a new, source-owner-approved Stage5 workstream publication

```bash
python -B Verification/verify_governed_source_adoption_v1.py \
  --family-id family:250-verben-mit-praepositionen \
  --workspace-id workspace:250-verben-mit-praepositionen-lexical-enrichment-v1 \
  --latest-git-blob <exact_GitHub_main_LATEST_blob_from_external_readback> \
  --workspace-root /path/to/exact/Git/repository/checkout \
  --source-dir /path/to/the/four/authorized/Stage5/source-files \
  --archive /path/to/the/new/official-governed-Stage5.zip \
  --native-receipt /path/to/official/governed-Stage5-RECEIPT.json \
  --new-report /safe/outside/the/source/ADOPTION-CANDIDATE.json
```

The tool refuses an existing report, outputs written into the source/workspace tree, a non-Stage5 workstream `LATEST`, wrong family-workspace owner, wrong policy/validator/builder blob, changed source bytes, missing/forged governed receipt, mismatched output, or a stale/incorrect LATEST file. The report contains its own SHA-based evidence and **cannot assert remote/current formal adoption**; passing a local Git SHA or forging a local LATEST is not equivalent to independent remote branch readback.

**Prior source Stage4/Stage5 certificates remain source-owned** and cannot be rewritten by the optimization lane; this tool does not check source-to-card semantics or Stage6 IndexedDB. It never edits the original, LOCKED, source cards or app runtime/UI/SRS/FSRS.

## Real-source negative control: 250 Verben R8 is not retroactively adopted

[Actual R8 diagnostic](../Verification/P1-250-VERBEN-R8-LEGACY-NONADOPTION-DIAGNOSTIC-20261105.json) checked the *real bytes* of `250-Verben-Lexical-Enrichment-v1.8-R8-STAGE5-OFFICIAL-CLEAN-DELIVERY-20261105.zip` stored locally from the Library:

- Exact complete archive SHA256: `63ae8f2a3a8d2ec5dff94798db3ed060a0b4e43b1cc2699e540beb1393882e5c`
- Exact ZIP size **3,856,786 bytes**, CRC **PASS**, **30 members**.
- Actual 250 Verben import TSV SHA256 `d23a5b9865d9e35b7ec24fa4f94fe8d94ee9f65fb990f8da7ffed41c75435191`; the **five** nested CLEAN-DELIVERY SHA256SUMS entries were independently checked and passed. This recheck did **not** rerun the full outer archive 29-entry manifest.
- The GitHub `Workspaces/250-verben-mit-praepositionen-lexical-enrichment-v1/LATEST.json` latest readback blob `074c4eef64fec30ab9f7b63ae227fbede8ba8e65` refers to this same ZIP SHA/size and an existing R8 Stage5 receipt.
- **Legacy R8 has no new GFP-OPT governed-launcher invocation receipt.** Existing source-specific official Stage4/5 receipt statuses remain undisturbed. **Do not mark the new policy-consumption path ADOPTED for this historical R8 artifact.**
- The Library's current remote bytes were *not* independently read back again in this turn; the existing `LATEST` record reports a previous historical readback.

## CI and remaining work

[`Verification/tests/test_governed_source_adoption_v1.py`](../../Verification/tests/test_governed_source_adoption_v1.py) exercises the *real original* native Stage5 builder and its governed launcher with **synthetic** four-role data + a deliberately synthetic local LATEST pointer on both Ubuntu and Windows. It checks modified sources, forged schema/Stage status, wrong family/workspace, mismatched hashes, missing receipt, altered output and write-once behavior. CI does NOT read private user Library ZIPs or make independent GitHub-main readback calls.

**NEXT P1:** secure the cross-repository remote adoption finalizer: compare the exact live Git `main` LATEST blob and Library content SHA/size with the generated local candidate, require source-owner approval and independent stage evidence, and only then update a per-producer policy adoption receipt. Also add non-neutral domain adapters separately. The holistic P3 dashboard must report `ROUTED`, `ELIGIBLE`, `LOCAL_VERIFIED`, `REMOTE_VERIFIED`, and `ADOPTED` as distinct statuses.
