# German Content Production Kit v3.1.9

```text
Start here:
Prompt/START-PROMPT-v3.1.9.md
```

این ZIP یک wrapper برای استفاده در ChatGPT/Codex است تا Prompt و Architecture را یک‌جا در اختیار داشته باشید. این فایل **Flashcards Pro data-import ZIP نیست** و نباید مستقیماً داخل Runtime Import شود؛ وجود Schemaها، Sample JSON و Sample TSVهای متعدد در این wrapper عمدی است و با exactly-one-primary rule مربوط به User Import Artifact فرق دارد.

## اجزای مستقل

| Component | Version / role |
|---|---|
| Prompt | `prompt_version = v3.1.9` — producer/workflow provenance |
| Architecture package | `architecture_package_version = v3.1.5` — package provenance |
| Semantic contract | `contract_version = 3.1.3` / `gfp-german-language-content@3.1.3` — canonical semantics |
| Architecture validator | `validator_version = 2.2.0` for canonical validator; other validators are bound by file hash in Run evidence |

این Versionها مستقل‌اند. هیچ‌کدام را از دیگری derive یا equal فرض نکن.

## Authority map

- `Prompt/START-PROMPT-v3.1.9.md` entrypoint است.
- `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md` workflow اجرایی و guardrailهای production است.
- `Architecture/01-CORE/GERMAN-LANGUAGE-CONTENT-CONTRACT-v3.1.3.md` semantic contract است.
- `Architecture/02-SCHEMAS/`, `03-PROFILES/`, `04-TYPE-RULES/` shape/policy/type authority هستند.
- `Architecture/01-CORE/FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md` delivery authority برای Architecture v3.1.5 است.
- `Architecture/01-CORE/CONTENT-GENERATION-MASTER-PROMPT-v3.1.5.md` سند bundled release قبلی است؛ برای Run حاضر entrypoint v3.1.9 را override نمی‌کند.

## استفاده

1. همین ZIP را به ChatGPT/Codex بدهید.
2. بگویید از entrypoint بالا شروع کند و همهٔ فایل‌های authoritative لازم را از پوشهٔ Architecture resolve کند.
3. Source Dataset واقعی و Dataset Profile موردنظر را مشخص/ضمیمه کنید.
4. اگر Delivery می‌خواهید، Target/Format را resolve کنید. با Architecture v3.1.5 مسیر رسمی Flashcards Pro، Universal-v2 TSV + BUILD-METADATA است؛ Unified Import ZIP فقط با Delivery Spec جدیدتر و صریح مجاز است.
5. statusهای Content/Transport/isolated Runtime/current Runtime را جدا نگه دارید.

## Audit and verification

- `FINAL-ADVERSARIAL-AUDIT.md` گزارش مستقل، Findings، matrixها و ۱۶ سناریوی Red-Team است.
- `PRODUCTION-KIT-MANIFEST.json` SHA-256 همهٔ payloadها را به‌جز خود Manifest ثبت می‌کند؛ exclusion برای جلوگیری از self-hash recursion صریح است.
- `PRODUCTION-KIT-VERIFICATION.json` نتیجهٔ inventory/hash/entrypoint/post-extract gate را ثبت می‌کند.
- `Verification/` evidenceهای machine-readable و خروجی کامل ۶۴ تست را نگه می‌دارد.

Architecture payload بدون rewrite کپی شده است. Prompt payload شامل patchهای final architecture-grounded audit است.
