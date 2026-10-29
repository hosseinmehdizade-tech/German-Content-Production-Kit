# OP-02: Stage4 exact-snapshot rebaseline + independent review-receipt contract v0.1

**NONACTIVE / read-only proposal — no learner data mutation or production authority.** Implements process validation for one real workstream's future separately approved review, without manufacturing a replacement worksheet or spoofing an issuer.

## Observed WIP50 authority, held open

The independently fetched **real WIP50** binary authorities are:

| Pin | Exact SHA256 |
| --- | --- |
| WIP50 recovery ZIP | `a558055dbddda45d5d3040fb096bf28eb8f51e2c0863f5634c445094decfc96b` |
| Canonical, 788 units | `fe50217d519edbb1c4d5eb5fc4da36faf1f562e859ccfe58b0153dbf684c48aa` |
| Import TSV | `d640179d3fdfa2ecff0681b707519bc6d10ff687aba22482a7e8694aba374a8a` |
| Packaged **old unsigned** Stage4 worksheet | `30486336c3f920aee70f8f4ee4adbc6ee2991033ed2ed9921cf64e29bcc3116d` |
| Registered source A1–A2 PDF | `4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3` |
| Registered source B1–C2 PDF | `ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04` |

Independent current-worksheet freshness check: **604 of 788 units drift**, with **zero original reviewer decisions**. Field deltas overlap: Kombinationen 513, lexical relations 198, Rektion 10, Persian meaning 1, English example 1. This is a stale review baseline, **not a claim that 604 words are linguistically wrong**. Existing reviewer sheet is not approved for Stage4.

## Proposed rebaseline and receipt lifecycle (not executed)

1. Resolve exact frozen `LATEST.json` Git commit and authenticated user-approved workstream scope, plus independently read back raw bytes and hashes of Canonical, TSV, both original PDFs and ZIP. Check CAS and a single writer. User's generic `ادامه بده` in optimization chat is **not** content-workstream approval.
2. Independently authorized content-workstream operator generates a **successor reviewer worksheet** from exact Canonical projection of all 788 IDs and all 12 frozen fields; record new worksheet SHA, reference the original 2 PDFs and pinned Import SHA. **Never replace** the older unsigned file or edit WIP50 directly in this optimization mission.
3. A distinct independent-method second-pass reviewer (documented source/DE/FA/EN, rection, relations, combinations, examples) issues per-unit evidence with a stable ID, whole-unit semantic-normalized SHA, source PDF ID + page, reviewer identity, method, disposition and evidence locator. Snapshot hashes and worksheet pin are immutable inside receipt. Repeated IDs or stale hashes -> BLOCKED. Reviewed + unreviewed = 788 and disposition counts must equal reviewed unique IDs. Pending is valid as **partial in-progress**, not a false PASS.
4. Corrections require separate, verified **post-edit bytes**, stable ID before/after diff, permission for exact mutable target, scoped dependent QA, Git CAS and remote readback. The receipt's own word `corrected` is not proof of application. Changing Canonical requires **new snapshot/rebaseline**, not retroactive sheet signoff.
5. Independently authenticate the **issuer and approval context** outside the artifact itself (e.g., reviewed protected Git policy with required trusted reviewer, verified signature with separately pinned trusted key, issuer-specific approved scope and same exact commit). Same Git username, arbitrary `approved=true` inside receipt, matching checksum or a commit title saying CAS is **not** enough. Current connector does not provide signature verification/independent user approval; this remains an explicit blocker.
6. Only after all gates, and separately authorized content workstream production, consider genuine Stage4 then Stage5 four-role uniquely bound clean ZIP, Stage6 CURRENT v486 importer and Stage7 final regression. Do not auto-activate the builder or grant OP01 scopes from this process proposal.

## Nonactive code and explicit limits

`Verification/audit_stage4_snapshot_review_receipt.py` checks an externally **provided** anchor, raw Canonical/TSV/PDF/worksheet hashes, the already proposed worksheet freshness rule, complete Canonical IDs and per-unit canonicalized whole-object digests, foreign-source page bounds, reviewer-method string, evidence reference, no self-identified same producer/reviewer, one disposition per unique review, disjoint review conservation and snapshot replay. Valid full synthetic receipt returns `COMPLETE_RECEIPT_STRUCTURE_ONLY_NOT_SIGNED_OFF`, with `stage4_semantic_pass=false`, `issuer_authenticated=false`, `production_authorized=false`, `performed_writes=false`. Partial returns `OPEN_PARTIAL_REVIEW_NOT_SIGNED_OFF`. Malformed/tampered/stale returns `BLOCKED_REVIEW_RECEIPT_BINDING`.

**Critically**: The supplied anchor itself is not authenticated by the code, and a distinct *string* in `reviewer_id` does not cryptographically authenticate the person/model. No positive structural status asserts real independent reviewer or actual semantic correctness. The intentionally conservative v0.1 blocks `corrected` receipts pending a separately verified applied-bytes/CAS extension.

CI exercises only synthetic cases, with no fetch, actual source workstream edits, issuer signing, content generation, rebaseline write, Library changes, or UI/runtime modifications. Before any production connection require independent credential/key/issuer decision, explicit scope approval, verified actual current revision, and a genuine separate Stage4 independent method.
