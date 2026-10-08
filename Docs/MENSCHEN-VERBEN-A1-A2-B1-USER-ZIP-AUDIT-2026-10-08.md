# Menschen A1 / A2 / B1 Verben — user-uploaded ZIP independent integrity audit (2026-10-08)

Status: **TECHNICAL_INTEGRITY_PASS / VERSION_SCOPE_NOT_UNIFORM**. This audit does not modify original bytes, promote content runtime-currentness, or claim new linguistic or live runtime acceptance.

## A1 consolidated original exact match
- Uploaded name: `Menschen-A1-Verben-v3.3.6-FINAL-CONSOLIDATED-CONTENT-PACKAGE(1).zip` (`(1)` suffix is a download-name duplicate only).
- ZIP bytes 2,556,294, SHA256 `0cc8d64711e74764d428170a22db4d09188ee27c38e7770a09c45fee1b27603f`. **Exact** SHA and size of historical `Menschen-A1-Verben-v3.3.6-FINAL-CONSOLIDATED-VERIFICATION.json` PASS artifact.
- 62 entries, ZIP CRC PASS, nested SHA256 ledgers 21/21 + 34/34, root SHA256 ledger 61/61, JSON parse PASS, manifest member SHA and sizes PASS.
- Active import TSV: `Current-Repair2-Content/CONTENT-DELIVERY/A1-VERBEN-UNIVERSAL-v2.tsv`, SHA256 `d46a3dd7aa7294db0970af50e79d45bc6ed075c52a799da932c6aa56b98179f4`.
- 310 active cards = 247 Verb + 63 Expression; 1240 German examples each with FA+EN; 23 TSV columns; all unique IDs/orders; 0 unified Kombinationen sections. Legacy separate Rektion/Kollokationen/Nomen-Verb-Verbindungen remain in current historical archive. Valid historical content backup, **not proven current after active Kombinationen overlay**.

## A2 consolidated original exact match
- Uploaded name: `Menschen-A2-Verben-v3.3.6-FINAL-CONSOLIDATED-CONTENT-PACKAGE(1).zip`.
- ZIP bytes 955,677, SHA256 `fb240cd05fe7ec99e2816fff8e4337dde0b7fdac2dc9f6f21caf8ddaab4d2332`. **Exact** SHA and size of historical `FINAL-CONSOLIDATED-VERIFICATION.json` PASS artifact.
- 37 entries; ZIP CRC PASS; nested SHA256 ledgers 15/15 +16/16 and root 36/36 PASS; JSON reparse/manifest PASS.
- Active TSV: `Current-Content-Final/A2-VERBEN-UNIVERSAL-v2-KOMBINATIONEN-BATCH15-ACCEPTED.tsv`, SHA256 `facc902209744736979a923a4c61a764402d479beaa3938e741f6170e0174abd`.
- 292 cards = 228 Verb +64 Expression, 1168 DE/FA/EN examples, 292 unified Kombinationen sections with 1439 items. Unique `order` values run 1..297 with five stable gaps (177,203,266,286,292), no duplicates. This is not alone proof of a defect. **Runtime acceptance is explicitly NOT_RUN** in this archive.

## B1 valid source content, not the complete integrated final release
- Uploaded `Menschen-B1-Verben-v3.3.6-Kombinationen.zip`: 1,737,143 bytes, SHA256 `864dbfaab1a87d318488a9c241bc801ce629413a15bdcb854cff0cdc413ac48e`; 13 ZIP entries incl root dir, CRC and 10/10 SHA256 ledger PASS; JSON parse and 23-column TSV PASS.
- 395 active = 279 Verb + 116 Expression; 1580 DE examples with FA+EN; 395 unified Kombinationen sections, 2123 items.
- Active Stage5 TSV SHA256 `469d21a0d26db81f90b0e4dbaeca6aa9e9e19bc12a93d54eb9e17792cdebdee6` and canonical SHA256 `f5213fc8dee198f58904e41ac3b6bc09dd9e334cef07abb4ef713ae6cd8e08db` **exactly match** `Workspaces/menschen-b1-verben-kombinationen-v336/CHECKPOINT.json` Stage7 Repair1.
- The actual historical **integrated** final artifact is `German-Flashcards-Pro-v465-R99-Menschen-B1-Verben-v3.3.6-Kombinationen-Repair1-RELOCKED.zip` (5,170,700 bytes; 360 entries; SHA256 `3ef8d7599f72ada99e72ad2de0c719cb685eda766de9806d62eae8ea9aaa14b0`). The user-uploaded content ZIP is **not** byte-identical to that outer integrated release; do not mislabel it.

## Backup and acceptance boundaries
- These three user-uploaded ZIPs are available locally in that review session, but **not yet proven uploaded to or remotely restored from Google Drive**. Do not mark `RECOVERABLE_VERIFIED` for a Drive copy without actual remote readback and SHA comparison.
- New `CONTENT-OUTPUT-DELIVERY-POLICY.json` v2.0.0 (2026-10-08) calls for a complete portable content-production handoff, without bundling the app. Existing historical archives should stay immutable; no repackaging overwrites them. B1 13-member content-only Stage5 ZIP cannot be treated as the complete new-policy handoff merely because its canonical/import core is verified.
- This audit is structural/cryptographic/source-artifact parity. It does **not** reperform independent linguistic adjudication for each example/meaning, or import on the current runtime (which must be resolved separately).

See also `Docs/ARTIFACT-RECOVERABILITY-INCIDENT-2026-10-08.md`.
