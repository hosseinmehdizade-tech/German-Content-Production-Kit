# GFP-OPT P1 — Governed native Stage5 builder invocation v1

**Program:** German Flashcards — Continuous Optimization Program (`GFP-OPT-2026`)
**Component:** Project Control Center
**Status:** EXECUTABLE OPT-IN PRODUCER ENTRYPOINT; not global adoption, not Stage4/5 acceptance, not app release.

## Problem resolved

The legacy native `Tools/build_clean_delivery.py` already validates direct import TSV, but invokes the neutral validator by a file path, not by proving that the validator and builder bytes are **exactly the active Git-pinned central policy definitions**. A rule implementation could silently drift while building a plausible looking ZIP.

The new **source-neutral, explicitly opted-in production entrypoint** [`Tools/build_governed_clean_delivery_v1.py`](../../Tools/build_governed_clean_delivery_v1.py) runs that **same original official builder unchanged**, with an independently enforced policy boundary:

1. Pin `Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json` to exact historical Git blob `74d24a2e0019a70b37b7f9d0ac83d0c788312ac1`; verify the registry is active and `stage5_neutral_validator` is Stage 5 only.
2. Verify the exact central validator Git blob (`b6d27c0b98f44cd8b0ffad325710f24f76da95e1`) and official native builder blob (`e12d2224c3321564e279bb5892298c35036bf7e9`), accepting Windows CRLF checkout normalization only if the actual canonical Git text blob matches.
3. Select **exactly four** unambiguous Stage5 inputs (one direct-import TSV, one canonical JSON, one source-output map TSV, one QA report). Reject symlinks, overlapping roles, source-inventory files masquerading as import or output inside the input directory.
4. Compute SHA256 for all four, read actual TSV bytes, run the active central validator (UTF-8, unique IDs, required columns, neutral card type, structured `details` if present, valid presentation contract and no forbidden UI selectors).
5. Call `Tools/build_clean_delivery.py` using the existing ZIP guard and Stage5 packaging path, **without altering this historically pinned builder**.
6. Verify original inputs remain byte-identical, output ZIP CRC, all inner `SHA256SUMS`, exact role manifest, every archived selected input SHA, and re-run the **same pinned policy validator** on the exact embedded TSV bytes.
7. Only after all checks succeed, create an exclusive/write-once JSON receipt with the input/output hashes and matched registry + validator + builder pins. No overwrite or automatic promotion to any workstream `LATEST`.

The guarded launcher **only** allows `stage5_acceptance` packaging intent. It deliberately refuses `final_delivery`, `validated_major_checkpoint` and `explicit_user_checkpoint` as a policy-format-only check does not grant those approvals.

## Example for a NEW eligible and user-authorized Stage5 publication

```bash
python -B Tools/build_governed_clean_delivery_v1.py \
  /absolute/path/to/authorized/source-directory \
  /absolute/path/to/new/ACCEPTED-STAGE5-DELIVERY.zip \
  --receipt /absolute/path/to/new/GOVERNED-STAGE5-RECEIPT.json
```

The source directory must contain exactly one each of the native builder's four required input roles, already prepared by that source's own authorized content workstream. The output ZIP and receipt paths must not already exist. The launcher will not create or edit flashcards; it only checks, stages and packages **the authorized input files**.

**Never use this optimization project to produce a successor content ZIP automatically.** The next named content workstream must decide whether its actual current eligible source output fits the neutral Stage5 contract and invoke this launcher at a safe publication boundary.

## Evidence / limits

- New [input gate](../../Verification/check_active_stage5_policy_v1.py) is reusable without a source-family-specific implementation.
- [Native end-to-end tests](../../Verification/tests/test_governed_stage5_invocation_v1.py) exercise the **real original production builder** with synthetic four-role inputs; they inspect a real new ZIP and write-once receipt, and reject drift/invalid inputs. 24 tests on both Ubuntu and Windows.
- Historical independent real-output family witnesses from [P1 first pilot](../Verification/OP01-OP02-P1-TWO-REAL-PRODUCER-FORMAT-20261105.json) remain 250 Verben (292) and Menschen A1 Verben (310) — **these are not newly repackaged, re-reviewed, or automatically promoted by this change.**
- No changes to active registry v1.0.0 or its 15 bindings, native official builder, old source material or LOCKED, learner cards, app runtime/UI or FSRS/SRS. No source-specific CHECKPOINT or LATEST changes.
- A source-specific `REAL_OUTPUT_PARITY_VERIFIED` adoption claim needs an actual new authorized invocation, exact current/source authority and independently verified remote readback. Synthetic CI cannot prove that. The global adoption count does not become 34/34.

**Next central P1 action:** add typed per-source adoption receipts and a catalog-level eligibility/consumption matrix; create safe source-specific launcher invocation wiring for eligible producers, and keep non-neutral and linguistic profiles separate. Broaden adoption only after a real authorized workflow invokes the gate.
