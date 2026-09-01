# German Content Production Kit v3.1.10

```text
Start here:
Prompt/START-PROMPT-v3.1.10.md
```

v3.1.10 یک **Product Content Completeness Hotfix** روی baseline اجرایی v3.1.9 است. Architecture v3.1.5 و semantic contract v3.1.3 تغییر نکرده‌اند. این repository wrapper برای استفاده در ChatGPT/Codex است و **Flashcards Pro data-import ZIP نیست**.

## اجزای مستقل

| Component | Version / role |
|---|---|
| Active Prompt | `v3.1.10` — completeness overlay روی v3.1.9 |
| Base Prompt | `v3.1.9` — producer/workflow baseline |
| Architecture package | `architecture_package_version = v3.1.5` — package provenance |
| Semantic contract | `contract_version = 3.1.3` / `gfp-german-language-content@3.1.3` — canonical semantics |
| Architecture validator | `validator_version = 2.2.0` for canonical validator |
| Product completeness validator | `gfp-content-completeness@1.0.0` |

این Versionها مستقل‌اند. هیچ‌کدام را از دیگری derive یا equal فرض نکن.

## Authority map

- `Prompt/START-PROMPT-v3.1.10.md` entrypoint فعال است.
- `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.10.md` completeness overlay است و v3.1.9 را strengthen می‌کند.
- `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md` workflow baseline اجرایی است.
- `Architecture/01-CORE/GERMAN-LANGUAGE-CONTENT-CONTRACT-v3.1.3.md` semantic contract است.
- `Architecture/02-SCHEMAS/`, `03-PROFILES/`, `04-TYPE-RULES/` shape/policy/type authority هستند.
- `Architecture/01-CORE/FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md` delivery authority برای Architecture v3.1.5 است.
- `Architecture/01-CORE/CONTENT-GENERATION-MASTER-PROMPT-v3.1.5.md` سند bundled release قبلی است و entrypoint جاری را override نمی‌کند.

## Product completeness — v3.1.10

`CONTENT_VALIDATED` دیگر به معنی کامل بودن محتوای قابل نمایش کارت نیست. Gate جداگانهٔ زیر اجباری است:

```text
PRODUCT_CONTENT_COMPLETE
```

برای Menschen A1 Verb rich-card، Profile فعال:

`Prompt/MENSCHEN-A1-CONTENT-COMPLETENESS-v1.0.0.json`

حداقل‌های کلیدی:

- auxiliary / reflexive / separability اجباری؛
- Collocation حداقل 3، هدف 4، preferred max برابر 6؛
- Collocation/Rektion/Synonym/Antonym موجود باید evidence claim متناسب داشته باشد؛
- Synonym/Antonym preferred هستند، نه hard-required؛
- ساختن داده یا evidence برای پر کردن count ممنوع است؛
- legacy `NVV1..NVV6` بدون classification semantic به `nvv` یا `collocation` تبدیل نمی‌شود.

Validator:

```text
Verification/validate_content_completeness_v1_0_0.py
```

Regression suite:

```text
Verification/test_content_completeness_v1_0_0.py
```

## استفاده

1. Repo/Package را به ChatGPT/Codex بدهید و از entrypoint v3.1.10 شروع کنید.
2. Source Dataset واقعی و Dataset Profile موردنظر را resolve کنید.
3. Canonical/structural validation و Linguistic Audit را جدا اجرا کنید.
4. Product Completeness را جدا اجرا کنید؛ PASS قبلی `CONTENT_VALIDATED` برای عبور از این Gate کافی نیست.
5. اگر Delivery می‌خواهید، Target/Format را از Delivery Spec authoritative resolve کنید.
6. statusهای Content / Product Completeness / Transport / isolated Runtime / current Runtime را جدا نگه دارید.

## Audit and verification

- `FINAL-ADVERSARIAL-AUDIT.md` و root `PRODUCTION-KIT-MANIFEST.json` مربوط به baseline کامل v3.1.9 هستند.
- `Verification/PRODUCTION-KIT-HOTFIX-VERIFICATION-v3.1.10.json` evidence افزوده‌شدهٔ v3.1.10 را ثبت می‌کند.
- تا زمانی که full checkout/package دوباره manifest/hash کامل تولید نکرده، root manifest v3.1.9 را به‌عنوان manifest کامل v3.1.10 جا نزن.
- Architecture payload در v3.1.10 rewrite نشده است.
