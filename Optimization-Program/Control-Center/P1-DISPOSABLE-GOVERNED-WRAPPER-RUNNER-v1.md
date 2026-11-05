# GFP-OPT P1 — Disposable governed-wrapper source replay

## Scope

This executable tool bridges the previously Library-byte-attested historical
Stage5 archives and the actual centrally pinned governed entrypoint. It never
publishes a new release, changes user cards, or grants CURRENT / FINAL status.

The runner requires an explicit expected archive SHA256 and exact official
clean-delivery prefix, validates ZIP CRC, rejects duplicate/traversal/oversize
archive entries, reads the official four-role manifest, and validates each
source member against its original SHA256SUMS. It copies only these four source
roles into a new disposable temporary directory. It does not extract arbitrary
archive entries or alter the archived original.

In optional --run-governed mode it imports the checked-in
Tools/build_governed_clean_delivery_v1.py and calls its real builder and
validator. The generated ZIP and governed invocation receipt are stored
inside TemporaryDirectory and deleted before the command returns. Two negative
copies (wrong card_type, malformed details) must fail without creating ZIPs
or receipts.

## Existing real Library source commands

250 Verben R8 historical 292-row input:

    python -B Tools/rehearse_existing_stage5_archive_v1.py \
      --archive "/path/to/250-Verben-Lexical-Enrichment-v1.8-R8-STAGE5-OFFICIAL-CLEAN-DELIVERY-20261105.zip" \
      --sha256 63ae8f2a3a8d2ec5dff94798db3ed060a0b4e43b1cc2699e540beb1393882e5c \
      --prefix "02-Content/CLEAN-DELIVERY/" --run-governed

NVV B01 historical 2,492-row input:

    python -B Tools/rehearse_existing_stage5_archive_v1.py \
      --archive "/path/to/NVV-R6.1-STAGE5-CLEAN-NATIVE-MILESTONE-20261105.zip" \
      --sha256 fc7fb3cb005372c3254ae475d9c3637dc9f7ce439813c52ce7e74b009d800cbd \
      --prefix "CONTENT-DELIVERY/" --run-governed

Without --run-governed, the actual user Library raw bytes were independently
checked with the equivalent preflight logic in the current conversation:
both ZIPs have verified original hashes, all eight source-role hashes matched
and all 2,784 rows were counted. **This is not evidence that the real governed
wrapper has already executed on those private archived bytes.**

## CI and source authority

The checked-in CI workflow runs synthetic source files only through the
actual pinned governed wrapper on Ubuntu and Windows. Real personal Library
archives are NEVER copied into GitHub CI. The tests deny zip tampering,
path traversal, duplicate entries and malformed source before accepting a
temporary receipt.

Even if --run-governed succeeds against these **old** byte-certified archives,
it is explicitly a disposable rehearsal, not the first authorized new
producer invocation. Existing R8 is a prior official Stage5; NVV's Stage4
acceptance scope is its first 100 B01 rows, not all 2,492 transport rows.
No existing archive can be retrospectively labeled P1 ADOPTED.

## Formal adoption gate remains open

A genuine NEW source-owner-authorized Stage5 boundary must supply its approved
source roles; invoke the exact centrally governed builder; retain a unique
write-once source-specific receipt; independently verify the new GitHub-main
LATEST and provider-backed Library output archive; pass source QA and a reviewed
future adoption ledger v2. No app UI, IndexedDB, SRS or FSRS changes are
authorized by this tool. OP01 trust and OP05 cleanup gates remain separate.

Formal P1 newly ADOPTED producers: **ZERO**.
