# SOURCE POLICY v3.1.5

## هدف
این لایه منابع مجاز و قواعد Evidence را از Canonical Learning Unit جدا می‌کند. `approved` بودن یک منبع فقط یعنی استفاده از آن مجاز است؛ `verified` یعنی همان منبع در همان Run واقعاً بررسی شده است. این دو هرگز مترادف نیستند.

## سلسله‌مراتب نقش‌ها
- **DE→DE / German sense:** Duden و DWDS منابع اصلی معنی/کاربرد هستند.
- **Grammar / Rektion / Morphology:** grammis و منابع معتبر آلمانی اولویت دارند؛ منبع فارسی/دوزبانه مرجع نهایی این Claimها نیست.
- **DE↔FA:** Langenscheidt Deutsch–Persisch منبع اصلی دوزبانه؛ Wort.ir و B-Amooz منابع مقایسه‌ای/ثانویه؛ PONS Persisch–Deutsch/Deutsch–Persisch منبع ثانویه.
- **DE↔EN:** Langenscheidt، PONS و Collins منابع اصلی؛ Cambridge و Oxford Learner’s منابع تکمیلی مستقل برای sense/wording/usage.

## قانون Evidence
1. هیچ Source فقط به‌خاطر حضور در Registry `verified` نیست.
2. اگر منبع در Run باز/بررسی نشده، `verification_status=unverified|blocked|not_found` ثبت شود.
3. Claim فقط وقتی به یک Source نسبت داده شود که آن Source در `allowed_claims` همان Claim را پشتیبانی کند.
4. Source فارسی/DE↔FA حق نهایی‌سازی `grammar`, `rection`, `morphology`, `orthography` را ندارد.
5. برای Claimهای معمول Profile می‌تواند حداقل یک Source verified بخواهد.
6. اگر `risk_flags` شامل ambiguous/multi-sense/disputed/high-risk باشد، Claim requirement می‌تواند حداقل دو **independence_group** مستقل بخواهد.
7. Collins و Langenscheidt DE↔EN برای شمارش استقلال به‌صورت محافظه‌کارانه در یک lineage گروه‌بندی شده‌اند؛ PONS/Cambridge/Oxford مستقل شمرده می‌شوند.

## Sentence Translation
DE Example منبع است و FA/EN ترجمه طبیعی همان جمله‌اند. Dictionaryها برای anchor کردن Sense/Gloss و QA واژگانی استفاده می‌شوند. اگر ترجمه دقیق جمله مستقیماً در منبع بررسی نشده، نباید `persian_example_translation` یا `english_example_translation` به‌عنوان verified claim ثبت شود. Linguistic Audit مرحله‌ای جداست.

## Learner-facing field → Evidence binding
وجود یک field آموزشی به‌معنی تأیید خودکار آن نیست. برای fieldهای حساس، Validator باید presence داده را به Claim اختصاصی متصل کند.

- اگر `details.rection` غیرخالی است، حداقل یک Source verified با Claim صریح `rection` لازم است.
- Claim عمومی `grammar` به‌تنهایی برای Rektion کافی نیست.
- `grammis` مرجع ترجیحی Rektion است. `Duden` فقط وقتی می‌تواند Claim `rection` بدهد که همان entry/grammar/examples واقعاً pattern مورد استفاده را صریحاً پشتیبانی کند.
- DE↔FA sourceها همچنان حق تأیید نهایی Rektion را ندارند.
- نبود Evidence اختصاصی باید Fail/Review ایجاد کند؛ هرگز Evidence از روی مقدار موجود در Card استنتاج نشود.

## Translation requirement vs alignment
- Source sentence آلمانی anchor هر Example است.
- FA/EN اگر وجود داشته باشند، ترجمه همان DE و عضو همان Example Group هستند.
- required بودن FA یا EN فقط Profile-driven است؛ General Contract هیچ زبان ترجمه‌ای را برای تمام Datasetهای آینده hard-code نمی‌کند.
