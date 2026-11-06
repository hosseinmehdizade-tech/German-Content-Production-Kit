# Aspekte C1 — Stage 1 / Lower-source provenance and scoped global same-headword screen

**Status: PASS_SCOPE_ONLY — NOT STAGE1 PASS; zero learner cards.** 2026-11-06.

## Deutsch
- **Menschen A1/A2/B1 original user corpus: PASS:** 9,109 data records in the authenticated full-audio export; original RAR SHA-256 `a2ffb791c29ddaa43e27bb944f430bff6896dc3156115f8989eee3056d5471c1`; CSV SHA-256 `52f8bb896f5aa1c8f878aeb0ea74ef07ddbeee75261af89dfb2fcad624fc1222`. The source RAR and ZIP are held separately in the original reference Library and not replicated into the C1 package.
- **Aspekte B1+/B2 original 3,275 records: NOT AUTHENTICATED:** the 2, single-size, original-named root Library CSV candidates are indexed, but raw-byte materialization was denied and file reading failed. We did not assert their SHA. Its registered original SHA-256 is `09478483886661527b24bf00d9c375234d5877ac9189f01f1aa6ec467b85e0f1`. Independently authenticated sanitized B1+ 1,548 and B2 1,726 = 3,274 records, not 3,275. Missing original ordinal 3,275 remains a blocker.
- PDF SHA-256 `b05c90320ad75dc19be12a374087830bd2c379206a5711e604a6aea699e189cf`; all 3,270 original PDF first-word page-coordinate anchors independently reverified with zero mismatches.
- Independently reproduced **1,490** historical cross-level source triples (headword, Persian definition, example) without mismatch: **979** from original Menschen and **511** from verified sanitized B1+/B2. Historical row positions include four leading Memrise metadata rows.
- Of 2,219 C1 items previously marked candidate NEW, **68** strict same-normalized-headword hits to earlier levels are queued for a semantic test. **43** are already present in either the old 24 Menschen or old 40 B1/B2 targeted queues; **25** were not in either of those two queues (this is not a claim that they were never covered anywhere else).
- This batch includes **41 distinct DE/FA scoped semantic review proposals**, comprised of 18 high-priority and 25 new-outside-targeted-queues proposals with 2 overlapping IDs. Each case preserves exact C1 expression, examples, crosslevel witness and German/Persian rationale. All decisions are **provisional**: no `KEEP`, `DROP`, `MERGE` or learner-card approval.
- The earlier 465-case historical decision ledger remains as-is; the nine tracked source/context HOLDs remain open, and the 1,051 non-NEW preflight flags are not globally adjudicated.
- Releasing Stage 1 requires original 3,275-byte baseline authentication plus full sense-, construction-, and idiom-level global resolution across 3,270 C1 occurrences, followed by independent semantic QA.

## فارسی
منبع کامل Menschen با هش اصلی مستقل تأیید شد؛ اما فایل کامل ۳۲۷۵ردیفی Aspekte به‌رغم مشاهدهٔ نام در Library اجازهٔ خواندن بایت‌ها را نداد. تعداد ۶۸ برخورد صرفاً از نوع سرواژهٔ یکسان است و به‌معنای تکرار معنایی نیست. ۴۱ تحلیل آلمانی–فارسی در صف تصمیم‌گیری هستند و هیچ موردی نهایی یا قابل انتشار نشده است. Stage 1 همچنان IN_PROGRESS است.

## Evidence
See accompanying `STAGE1-ORIGINAL-MENSCHEN-9109-ASPEKTE-3274-SOURCE-AUTH-20261106.json`, `STAGE1-1490-PRIOR-WITNESS-EXACT-TRIPLET-AUDIT-20261106.json`, `STAGE1-68-NEW-EXACT-HEADWORD-COLLISION-QUEUE-20261106.jsonl`, `STAGE1-41-UNIQUE-SCOPED-SEMANTIC-REVIEW-PROPOSALS-20261106.jsonl`, and independent scoped QA.