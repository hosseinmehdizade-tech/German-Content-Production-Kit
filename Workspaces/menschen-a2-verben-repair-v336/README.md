# Menschen A2 Verben Repair v3.3.6

Current durable milestone: **Stage7 exact-final acceptance BLOCKED — content is NOT re-locked yet**.

- Exact CURRENT runtime remains **v451-R85 VERIFIED/FINAL**.
- Exact Stage7 candidate SHA-256: `b6c28251625348122bdcb32e4b0df2b7074b44b67e9f097ecd6812f0ae866bfa`.
- Static post-package verification: CRC PASS; root SHA256SUMS **324/324 PASS**; **71/71** runtime files byte-identical to v451; dataset/import package hashes PASS.
- Phase1 exact-final import preview/provenance/structural checks: **9/9 PASS** through import permission.
- 292-card publication occurred, but the commit manifest was sampled at **PUBLISHED_PENDING_VERIFY** before the normal asynchronous transition to **VERIFIED**.
- The exact-final contract requires VERIFIED. The gate was not weakened and Stage7 was stopped.
- This is classified as a **test-harness timing boundary**, not evidence of content or runtime corruption.
- Per execution-safety policy, after one corrected retry no further retry loop was run in this turn.
- Candidate bytes are preserved in Library and must **not be rebuilt** before resume.
- Visible UI change: **none**.

Next: rerun the same candidate with an explicit wait for manifest VERIFIED; then Phase2 roundtrip + v451 envelope regression + final post-package verification. Promote the same bytes to RELOCKED only if all gates pass.
