# Aspekte B2 — All 10 lessons · one independent DE/FA reviewer sheet

**Unreleased (NONIMPORT).** This package is the current *curated* working content, not a textbook re-extraction. 1719 distinct draft units, 3438 paired German–Persian examples, 4886 proposed German collocations, 10 lessons. All reviewer decisions remain UNSIGNED.

## Reviewer instructions

1. Work only in the single CSV; keep `lesson`, `unit_id`, `source_ordinals`, all original German/Persian text, and `focus_code` unchanged. Do not import into any flashcard app.
2. For each row assess German morphology + Persian sense, both examples with Persian translations, and the collocations. Set each of the four `*_verdict` columns to `PASS` or `REVISE`; write any proposed corrections in `reviewer_notes`. Keep the source columns intact, even when proposing corrections.
3. After checking a row, enter reviewer name/id + date and `overall_linguistic_signoff=SIGNED` only if all four section verdicts are `PASS`. Otherwise keep `NOT_SIGNED`.
4. `focus_code` marks prior editorial caution, **not** a claim that the card contains an error. Review all rows, not only those flagged.
5. Return the edited CSV; this sheet will be reconciled against the pinned SHA-256 in the JSON manifest. The presence of a signature is not proof of the user's live app identity/SRS or successful native import/rollback.

**فارسی:** این فایل برای بازبینی مستقل تمام ۱۷۱۹ کارت است. متن اصلی واژه‌ها و مثال‌ها را در همین جدول تغییر ندهید؛ اصلاحات پیشنهادی را فقط در `reviewer_notes` بنویسید. تأیید هر بخش و شناسهٔ بازبین باید واقعی باشد. هیچ کارت فعلاً مجوز انتشار ندارد.

**Safety:** No source CSV was overwritten; no learner SRS was read, imported, or modified. Native v505 browser test and live-card identity remain separate blocked gates.
