# German Language Content Architecture — Prompt/Delivery Gate v3.1.5

Release status: **Claim-Coverage + Runtime-State-Aware Prompt/Delivery Freeze Candidate**

این Package معماری Clean-Slate تولید محتوای آلمانی برای German Flashcards Pro را تعریف می‌کند. **Semantic contract در این release همچنان `gfp-german-language-content@3.1.3` است**؛ v3.1.5 علاوه بر Runtime-State Gate قبلی، claim-coverage را harden می‌کند: learner-facing Rektion بدون Evidence اختصاصی `rection` Final نمی‌شود. Translation alignment ثابت است، اما required بودن FA/EN همچنان Profile-driven است.

## Runtime composition

```text
General Content Contract
        + Dataset Profile
        + matching typed Type Rule
        + Source Data
        = Canonical Learning Units
```

Presentation و Practice مصرف‌کنندهٔ downstream هستند. آن‌ها اجازهٔ تولید ترجمه، Example، Meaning یا اصلاح زبانی ندارند.

## Package map

- `01-CORE/`: Contract عمومی، Master Prompt و Flashcards Pro Universal-v2 Delivery Spec.
- `02-SCHEMAS/`: Schemaهای semantic قبلی + `RUNTIME-IMPORT-EVIDENCE-SCHEMA.json` برای claimهای Runtime.
- `03-PROFILES/`: Menschen A1، Independent B1 و Profile اثبات معماری.
- `03-SOURCES/`: Approved Source Registry برای DE→DE، DE↔FA و DE↔EN.
- `04-TYPE-RULES/`: Type Ruleهای typed برای تمام خانواده‌های اصلی.
- `05-SAMPLES/`: نمونهٔ canonical شامل ۱۰ Learning Unit و چند Type.
- `06-VALIDATION/`: Validator عملیاتی، Meta-validator، Delivery builder/validator، Runtime-evidence validator و تست‌های مثبت/منفی.
- `07-QA/`: Evidence واقعی، گزارش‌ها و Self-review.

## Canonical invariants

- `examples[]` داینامیک است و Count فقط از Profile می‌آید.
- هر Example یک source آلمانی و translationهای همان جمله را نگه می‌دارد.
- `english_gloss` در Learning Unit و English sentence translation در Example است.
- Example ID از متن یا order مشتق نمی‌شود.
- `connections[]` نوع معنایی NVV/Collocation/Pattern را نگه می‌دارد، ولی Section بصری تحمیل نمی‌کند.
- Type Ruleها نوع واقعی value، enum، array item و object shape را تعیین می‌کنند.
- Menschen A1 فقط یک Profile است.

## Validation

از ریشهٔ Package:

```powershell
python 06-VALIDATION/validate_content.py --dataset 05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json --profile 03-PROFILES/ARCHITECTURE-PROOF.json --type-rules 04-TYPE-RULES --source-registry 03-SOURCES/SOURCE-REGISTRY.json
python -m unittest discover -s 06-VALIDATION/tests -p "test_*.py" -v
python 06-VALIDATION/meta_validate_schemas.py --package-root .
```

Meta-validation به `jsonschema>=4.25,<5` نیاز دارد؛ نسخهٔ دقیق استفاده‌شده در Evidence ثبت می‌شود.

## Scope boundary

این release کد Runtime/UI را تغییر نمی‌دهد؛ فقط **claim boundary** را اصلاح می‌کند. نتیجهٔ یک harness ایزوله ممکن است `APP_COMPATIBLE` باشد، اما وضعیت live browser جداست. بدون live preflight، current runtime status باید `CURRENT_RUNTIME_NOT_VERIFIED` بماند؛ در recovery/read-only/write-block حالت `RUNTIME_BLOCKED` استفاده می‌شود.


## Flashcards Pro delivery

برای تحویل مستقیم به Flashcards Pro، Canonical JSON به‌تنهایی فایل کاربر نیست. مسیر رسمی:

```text
Canonical JSON → Universal-v2 TSV → BUILD-METADATA.json → Target Runtime verification
```

دستور نمونه:

```powershell
python 06-VALIDATION/build_flashcards_pro_universal_v2.py --dataset 05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json --profile 03-PROFILES/ARCHITECTURE-PROOF.json --output 05-SAMPLES/DELIVERY-EXAMPLE/UNIVERSAL-v2-SAMPLE.tsv --metadata 05-SAMPLES/DELIVERY-EXAMPLE/BUILD-METADATA.json
python 06-VALIDATION/validate_flashcards_pro_universal_v2.py 05-SAMPLES/DELIVERY-EXAMPLE/UNIVERSAL-v2-SAMPLE.tsv --canonical 05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json --metadata 05-SAMPLES/DELIVERY-EXAMPLE/BUILD-METADATA.json
```

Runtime claimها با `06-VALIDATION/validate_runtime_import_evidence.py` و Schema جدید بررسی می‌شوند. Evidence ایزوله حق ادعای وضعیت current browser را ندارد.

Canonical PASS = `CONTENT_VALIDATED`. TSV parity PASS = `TRANSPORT_VALIDATED`. Isolated app matrix PASS = `APP_COMPATIBLE`. Live browser preflight جداگانه `RUNTIME_PREFLIGHT_PASS` یا `RUNTIME_BLOCKED` می‌دهد. بعد از commit واقعی + reload، `IMPORT_VERIFIED` مجاز است. `IMPORT_READY` از v3.1.4 deprecated/ممنوع است.

## Source Policy
- DE→DE: Duden, DWDS, grammis با نقش‌های صریح.
- DE↔FA: Langenscheidt، Wort.ir، B-Amooz و PONS Persisch.
- DE↔EN: Langenscheidt، PONS، Collins، Cambridge و Oxford Learner’s.
- `approved` بودن Registry با `verification_status=verified` در یک Run فرق دارد.
- Claimهای grammar/rection/morphology را منابع فارسی نمی‌توانند تأیید کنند.
- Profileهای production برای german_sense، persian_gloss و english_gloss source requirement تعریف می‌کنند و در Risk حالت استقلال منبع را سخت‌گیرانه‌تر می‌کنند.


## v3.1.5
Adds presence-sensitive provenance coverage for learner-facing Rektion and makes explicit that translation alignment is fixed while language requiredness is Profile-driven.
