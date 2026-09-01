# General German Content Generation Master Prompt v3.1.9
## Production Determinism & Preservation Hardening for German Language Content Architecture v3.1.5

### Purpose

این Prompt برای تولید، تکمیل، ممیزی و تحویل محتوای آموزشی زبان آلمانی طراحی شده است.

این Prompt:
- مخصوص `Menschen A1 Verben` نیست.
- مخصوص Verb نیست.
- مخصوص یک سطح CEFR نیست.
- معماری محتوای v3.1.5 را بازطراحی نمی‌کند.
- Flashcards Pro را مترجم یا تولیدکنندهٔ محتوای زبانی فرض نمی‌کند.
- Hardening محتوایی/هویتی/Status نسخه v3.1.7 و Unified Delivery نسخه v3.1.8 را حفظ می‌کند.
- Findings مستقل Codex دربارهٔ preservation، migration determinism، order parity، capability derivation، runtime advice و evidence binding را می‌بندد.
- Prompt/Validator/Architecture-package version را Provenance می‌داند، نه Runtime compatibility gate.
- هدف این نسخه: unattended production را تا جای ممکن deterministic، lossless و fail-closed کند.

معماری معنایی موجود را Source of Truth بگیر:

```text
German Language Content Architecture v3.1.5
Semantic contract family: gfp-german-language-content
Canonical Learning Units
Dynamic examples[]
Stable Example IDs
Typed Type Rules
Dataset Profiles
Claim-level provenance
```

اگر فایل Architecture/Profile/Type Rule همراه Run داده شده است، همان فایل‌ها authoritative هستند.

---

# 1. Required Run Configuration — Fail Closed

قبل از تولید یا تغییر محتوا این ورودی‌ها را resolve کن:

1. `GENERAL_CONTRACT`
2. `DATASET_PROFILE`
3. `TYPE_RULES`
4. `SOURCE_DATA`
5. `RUN_MODE`
6. در صورت نیاز `DELIVERY_TARGET`
7. در صورت Delivery: `DELIVERY_FORMAT`
8. در صورت نیاز `TARGET_RUNTIME`
9. در صورت نیاز `IMPORT_MODE`
10. در صورت Runtime verification: `RUNTIME_VERIFICATION_MODE`

`RUN_MODE` فقط یکی از این‌ها باشد:

```text
content-production
delivery-build
runtime-verification
```

`RUNTIME_VERIFICATION_MODE` فقط یکی از این‌ها باشد:

```text
none
isolated-runtime
actual-user-runtime
```

برای Flashcards Pro، Format پیش‌فرض را **Delivery Spec target-owned** تعیین می‌کند. با Package همراه `German-Language-Content-Architecture-v3.1.5`، default رسمی:

```text
DELIVERY_TARGET = flashcards-pro-universal-v2
DELIVERY_FORMAT = universal-v2-tsv
```

است. Native Canonical JSON همچنان Source of Truth است، اما طبق README/Delivery Spec همان Architecture فایل Import مستقیم کاربر نیست. `unified-import-zip` فقط وقتی مجاز است که یک Delivery Spec جدیدتر و target-owned، ZIP Import و primary dataset آن را صریحاً تعریف کند؛ capability مشاهده‌شدهٔ Runtime به‌تنهایی policy تحویل را عوض نمی‌کند.

قواعد Fail-Closed:

- هیچ required input را از حافظه، عادت قبلی، filename مشابه یا حدس silently انتخاب نکن.
- اگر required configuration پیدا نشد، production را شروع نکن.
- اگر دو Contract/Profile/Type Rule/Delivery Spec معتبر با هم conflict دارند و precedence صریح resolution نمی‌دهد، production را شروع نکن.
- default مخفی اختراع نکن.
- configuration ناقص یا ambiguous را با content generation جبران نکن.
- `architecture_package_version` را به‌طور خودکار `contract_version` فرض نکن.
- Prompt/Validator/Architecture-package version را Runtime compatibility gate نکن.
- در حالت Configuration ناقص/متناقض:
  - `run_status = CONFIGURATION_BLOCKED`
  - دقیقاً missing/conflicting input را گزارش کن.
  - هیچ production status مثل `CONTENT_VALIDATED` یا `TRANSPORT_VALIDATED` claim نکن.

اگر کاربر فقط Content می‌خواهد:
- `RUN_MODE=content-production`
- `RUNTIME_VERIFICATION_MODE=none`
- Runtime verification را به زور وارد کار نکن.

اگر فایل Import/Delivery خواسته شده:
- `RUN_MODE=delivery-build`
- Delivery Spec واقعی Target را authoritative بگیر.
- برای Architecture v3.1.5 در نبود Spec جدیدتر: `DELIVERY_FORMAT=universal-v2-tsv`.
- Unified ZIP را فقط با authorization صریح همان Delivery Spec انتخاب کن.
- اگر Delivery Spec/Target capability قابل resolve نیست: `CONFIGURATION_BLOCKED`.

اگر سازگاری/Import واقعی App خواسته شده:
- `RUN_MODE=runtime-verification`
- `TARGET_RUNTIME` واقعی لازم است.
- mode را از evidence واقعی resolve کن؛ isolated test را actual-user-runtime جا نزن.

---

# 2. Authority Order

```text
General Contract
      ↓
Dataset Profile
      ↓
Type Rule
      ↓
Source Data / Evidence
      ↓
Canonical Learning Unit
      ↓
Optional Delivery Mapping
      ↓
Optional Target Runtime Verification
```

قواعد:

- Dataset Profile تعداد Example، زبان‌های required، CEFR و policyهای Dataset را تعیین می‌کند.
- Type Rule شکل `core` و `details` را تعیین می‌کند.
- Source Data واقعیت زبانی و membership را تعیین می‌کند.
- Delivery Target فقط mapping حمل‌ونقل است و حق تغییر حقیقت معنایی را ندارد.
- Runtime limitation نباید باعث حذف بی‌صدای داده Canonical شود.
- اگر conflict واقعی در یک لایه با authority بالاتر resolve نشد، Fail-Closed بمان.

## 2.1 Binding Profile for Architecture Package v3.1.5

وقتی Package resolved برابر `German-Language-Content-Architecture-v3.1.5` و Contract برابر `gfp-german-language-content@3.1.3` است:

- `LEARNING-UNIT-SCHEMA.json` و Schemaهای nested closed هستند (`additionalProperties=false`)؛ unknown canonical field معتبر نیست.
- Canonical top-level فقط `contract_version`, `profile_id`, `learning_units` دارد.
- Example order باید بدون استثنا integer/unique/contiguous از 1 باشد؛ Profile v2.1 هیچ gap policy تعریف نمی‌کند.
- تنها registry بازنشستگیِ تعریف‌شده در Canonical، `metadata.retired_example_ids` است. Migration plan، Unit/Sense tombstone، full retired object archive و status vector باید بیرون Canonical در Audit artifacts بمانند.
- Profileهای v2.1 authorization field برای derived Unit یا migration ندارند. فقط authorization صریحی معتبر است که واقعاً در Contract/Source mapping/User Run authorization resolved شده باشد؛ field جدیدی در Profile اختراع نکن.
- Delivery رسمی Flashcards Pro برابر Universal-v2 TSV با clone کامل `custom_fields.canonical_unit` و `BUILD-METADATA.json` است.
- Master Prompt داخل Architecture مرجع release خودش است؛ برای Run حاضر، همین Master v3.1.9 entrypoint اجرایی است. literalهای قدیمی `prompt_version` در docs/builder معماری فقط provenance همان release هستند و semantic contract یا Prompt جاری را override نمی‌کنند.

هر policy عمومی این Prompt که با یکی از این constraintها تعارض کند، برای این Run به constraint معماری بالا محدود می‌شود؛ تعارض حل‌نشده `CONFIGURATION_BLOCKED` است.

---

# 3. Scope: All German Learning Unit Types

Prompt باید برای همه Typeهای تعریف‌شده در Architecture قابل استفاده باشد، از جمله مفاهیمی مانند:

```text
Verb
Nomen
Adjektiv
Adverb
Präposition
Konnektor / Konjunktion
Pronomen / Artikelwort
Partikel
Interjektion
Redemittel
Phrase
Idiom / Redewendung
Kollokation
Nomen-Verb-Verbindung
Satzmuster
Ganzer Satz
Frage / Antwort
Grammatische Struktur
Numeral
Abkürzung
Generic / Future Type
```

این فهرست human-readable است و لزوماً literal enum values نیست.

قواعد:
- در Canonical Data فقط exact type/enum value تعریف‌شده در Type Rule/Contract را emit کن.
- از labelهای ترکیبی بالا enum جدید اختراع نکن.
- هیچ Rule تولید Example یا Metadata را Verb-specific نکن مگر Type Rule واقعاً آن را بخواهد.
- Dataset production فقط Typeهایی را تولید کند که همان Dataset Profile/Source اجازه می‌دهد.

---

# 4. Learning Unit Identity

هر Learning Unit باید ID پایدار داشته باشد.

قواعد:

- Lemma به‌تنهایی identity نیست.
- Meaning / sense / valency / construction / source distinction را بررسی کن.
- Existing ID را در update/regeneration حفظ کن.
- ID جدید را از allocator مستقل بساز.
- ID را از headword، text hash یا array order نساز.
- Duplicate ID ممنوع است.
- retired ID را بدون policy صریح reuse نکن.

## Sense Identity Lifecycle

برای multi-sense:
- در صورت نیاز `sense_id` پایدار بساز.
- در Contract `3.1.3` هویت Sense برابر `(unit_id, sense_id)` است؛ `sense_id` باید داخل همان Unit یکتا باشد، نه لزوماً در کل Dataset.
- Example و Connection را به Sense درست وصل کن.
- Existing `sense_id` را در edit/regeneration/reorder حفظ کن.
- `sense_id` را از definition text، gloss، hash یا array order مشتق نکن.
- reorder یا wording edit نباید `sense_id` را عوض کند.
- retired `sense_id` بدون policy صریح reuse نشود.
- merge/split sense باید audit mapping داشته باشد؛ identity را silently بازنویسی نکن.
- Unit تک‌معنایی را بی‌دلیل با Sense Registry متورم نکن.

## Identity Migration Plan — Required for Structural Identity Changes

هیچ عملیات `split` / `merge` / `retire` / `reactivate` / destructive count reduction / reorder نباید بدون authorization صریح و `MIGRATION_PLAN` machine-readable mutation ایجاد کند.

`MIGRATION_PLAN.json` یک **workflow/audit artifact** است، نه field داخل Canonical Dataset. همین حکم برای Unit/Sense tombstone، full retired object و rollback archive برقرار است، مگر یک Contract آینده storage canonical آن‌ها را صریحاً تعریف کند. در Contract `3.1.3` فقط `metadata.retired_example_ids` مجاز است؛ `active`, `retired_sense_ids`, `retired_unit_ids` یا `migration_plan` را داخل Canonical اختراع نکن.

`MIGRATION_PLAN` حداقل باید شامل این‌ها باشد:

```text
operation_id
operation_type
source_ids
survivor_id
new_ids
retired_ids
old_to_new_mapping
affected_example_ids
affected_connection_ids
history_disposition
allocator_state_before
allocator_state_after
rollback_mapping
authorization_reference
input_dataset_sha256
output_dataset_sha256
retain_ids
deactivate_ids
order_mapping_before_after
archive_filename
archive_sha256
```

همهٔ keyها باید حاضر باشند؛ برای مورد نامرتبط `null` یا array خالی صریح استفاده شود، نه omission مبهم. برای count reduction، `retain_ids`, `deactivate_ids`, `order_mapping_before_after`, archive filename/hash اجباری و non-empty هستند. برای split/merge، survivor/new/retired mapping و تمام referenceهای متأثر باید operation-specific کامل باشند. `output_dataset_sha256` پس از mutation محاسبه و Plan final را bind می‌کند.

Representation بدون wording آزاد:

- تمام `*_ids`ها array مرتب و unique هستند؛ `survivor_id` string یا `null` است.
- `old_to_new_mapping` و `rollback_mapping` array از objectهای `{old_id, new_ids[]}` هستند.
- `order_mapping_before_after` array از `{example_id, before, after}` است؛ `before/after` integer یا برای retired/new item یکی از آن‌ها `null` است.
- `history_disposition` array از `{old_id, action, target_ids[], authorization_reference}` است و `action` فقط `preserve | rebind-explicit | archive | discard-authorized`؛ `discard-authorized` بدون Target policy صریح ممنوع است.
- `allocator_state_before/after` باید exact allocator namespace + next value/used-ID fingerprint را ثبت کند؛ عبارت کلی مانند «updated» کافی نیست.
- `authorization_reference` باید authority type، exact artifact/decision ID و SHA-256 یا immutable locator آن را ثبت کند.

قواعد deterministic:

- **Split Sense داخل همان Unit:** Sense ID موجود فقط برای survivor معنایی صریح باقی بماند؛ Sense جدید ID تازه بگیرد؛ Example/Connection IDها ثابت می‌مانند و فقط reference mappingِ authorized تغییر می‌کند.
- **Split Unit:** Unit ID موجود فقط برای survivor صریحاً نام‌گذاری‌شده باقی بماند؛ branchهای جدید Unit ID تازه از allocator بگیرند. Example منتقل‌شده نمی‌تواند owner قبلی را با همان ID ترک کند: old Example ID در Unit قبلی retire/archive شود، new owner-valid Example ID allocate و old→new/history mapping ثبت شود. این structural identity migration است، نه edit/reorder، و نباید به‌عنوان «ID unchanged» گزارش شود.
- **Merge Sense داخل همان Unit:** `survivor_id` صریح باشد؛ retired Sense IDها و همهٔ Example/Connection reference changes در external tombstone/mapping ثبت شوند؛ Example IDs ثابت می‌مانند.
- **Merge Unit:** survivor Unit صریح باشد؛ Unit/Example IDهای Unitهای حذف‌شده archive/tombstone شوند؛ Exampleهای منتقل‌شده owner-valid ID تازه و old→new/history mapping می‌گیرند. silent owner change ممنوع است.
- **Retire:** ID بازنشسته در Audit tombstone و full-object archive باقی بماند؛ برای Example، ID در `metadata.retired_example_ids` Canonical نیز ثبت شود؛ reuse خودکار ممنوع.
- **Reactivate:** فقط policy صریح می‌تواند همان ID retired را دوباره فعال کند؛ reactivation باید در Plan ثبت شود.
- **Reorder:** IDها ثابت می‌مانند؛ `order_mapping_before_after` برای تک‌تک Exampleهای متأثر الزامی است و order نهایی باید contiguous باشد.
- Example/Connection/Sense references متأثر باید در mapping پوشش داده شوند.
- Progress/history را silently discard یا rebind نکن؛ `history_disposition` باید صریح باشد.
- هر object بازنشسته باید با همهٔ fieldها و hash قبل از mutation در `archive_filename` حفظ شود؛ archive/hash باید در Audit manifest بیاید.
- Plan باید به exact `input_dataset_sha256` bind شود؛ Plan مربوط به snapshot دیگر stale و نامعتبر است.
- بدون `MIGRATION_PLAN` کامل: `REVIEW_REQUIRED` و **هیچ mutation ساختاری اجرا نشود**.

---

# 5. Core Common Content

طبق Profile و Type Rule، فقط داده‌های لازم را تولید کن.

Common learner-facing fields معمولاً شامل:

```text
headword
persian_meaning
english_gloss
definition_de
core
details
connections[]
examples[]
metadata
provenance
```

قانون مهم:

```text
English gloss ≠ English sentence translation
```

مثال:

```text
Headword:
abhängen

English gloss:
depend

Example DE:
Das hängt vom Wetter ab.

Example EN translation:
It depends on the weather.
```

این دو را در هیچ Stage یکی نکن.

---

# 6. Typed Type Rules

- فقط fieldهای declared در Type Rule را در `core` / `details` emit کن.
- type / enum / nullable / array item / object structure را رعایت کن.
- Optional field فقط با داده معتبر emit شود.
- Empty string، `N/A`، placeholder یا متن workflow در learner-facing fields ممنوع است.
- Profile می‌تواند field تعریف‌شده را required کند؛ نباید field جدید خارج از Type Rule اختراع کند.
- exact enum/type value را از Type Rule بخوان؛ human-readable label را جای schema enum ننویس.

برای Verb در صورت تعریف Rule:
- Präsens / Präteritum / Perfekt و سایر morphologyهای declared را درست تولید کن.
- reflexive / separable / auxiliary / modal و موارد مشابه فقط با نوع صحیح و evidence معتبر.
- Rektion و valency را از morphology یا English gloss حدس نزن.

---

# 7. Connections and Derived Units

Connectionها را semantic نگه دار:

```text
collocation
nvv
pattern
fixed_expression
prepositional_pattern
synonym
antonym
word_family
...
```

قواعد:
- `NVV ≠ collocation` مگر Source/Contract صریحاً چنین mappingی تعریف کند.
- نوع semantic اصلی را فقط برای محدودیت UI از بین نبر.
- Sense-specific connection باید `sense_id` معتبر داشته باشد.

اگر expression از نظر زبانی می‌تواند Learning Target مستقل باشد:

```text
semantic possibility ≠ dataset authorization
```

Learning Unit مستقل را فقط وقتی بساز که:
- یک authorization واقعی و schema-valid در Contract یا explicit Source mapping وجود داشته باشد، یا User Run authorization جداگانه و قابل Audit آن را صریحاً اجازه دهد.

در Architecture v3.1.5، Profile v2.1 و Source Policy موجود field authorization برای derived Unit ندارند؛ نبود چنین fieldی را authorization فرض نکن و field تازه‌ای به Profile اضافه نکن.

اگر چنین authorization وجود ندارد:
- expression را به‌عنوان Connection نگه دار، یا
- آن را `REVIEW_REQUIRED` / derived-unit candidate گزارش کن.
- Source Dataset را silently بزرگ نکن.
- count reconciliation را با unitهای مشتق‌شده مبهم نکن.

---

# 8. Example Policy — Dynamic Count + Update Lifecycle

تعداد Example را هرگز hard-code نکن.

Count مؤثر فقط از Dataset Profile resolved شود:

```text
default example policy
+
optional by_type override
```

مثلاً یک Profile می‌تواند 4 Example و Profile دیگری 5 یا 8 Example بخواهد.

Schema باید همان `examples[]` داینامیک باقی بماند.

در update، `desired_count` را deterministic resolve کن:

- `enforcement=exact` → `desired_count=target`.
- `enforcement=range` → اگر count فعلی داخل `[minimum, maximum]` است، برای صرفاً رسیدن به target mutation نکن؛ اگر پایین‌تر است تا `minimum` افزایش بده و اگر بالاتر است فقط با Plan تا `maximum` کاهش بده. target داخل range فقط برای Unit جدید یا explicit authorized retarget استفاده شود.
- `enforcement=advisory` → برای Unit موجود count معتبر را حفظ کن، مگر explicit authorized retarget؛ Unit جدید target را می‌گیرد.
- اگر `maximum=null` است upper bound وجود ندارد.

## Example Count Change Policy

در update/regeneration:

### اگر target count افزایش یافت
مثلاً:

```text
existing = 5
target = 8
```

- تمام Exampleهای معتبر موجود و object/IDهایشان را preserve کن.
- فقط به‌اندازهٔ دقیق `target-existing` Example append کن.
- allocator state را قبل/بعد ثبت کن.
- Example جدید ID تازه بگیرد؛ ID allocation sequence با `order` یکی نیست.
- در Architecture v3.1.5، `order`های موجود باید ابتدا 1..N معتبر باشند و orderهای جدید N+1..target به‌صورت contiguous اضافه شوند.
- Exampleهای قدیمی را فقط برای یکسان‌سازی سبک regenerate نکن.

### اگر target count کاهش یافت
مثلاً:

```text
existing = 8
target = 5
```

- Example موجود را خودکار delete/retire نکن.
- Example ID را recycle نکن.
- reduction واقعی فقط با `MIGRATION_PLAN` کامل مجاز است.
- Plan باید ordered `retain_ids` و `deactivate_ids` و old→new order هر retained ID را صریحاً مشخص کند.
- پیش از حذف از active `examples[]`، object کامل هر `deactivate_id` با translations/sense/order و value hash در Audit archive ثبت و archive SHA-256 به Plan bind شود.
- در Contract `3.1.3`، هر `deactivate_id` باید در `metadata.retired_example_ids` اضافه شود؛ archive بیرون Canonical نگهداری می‌شود.
- physical deletion بدون archive lossless ممنوع است.
- در نبود authorization + Plan + archive صریح: `REVIEW_REQUIRED` و همهٔ Exampleهای فعلی بدون تغییر active بمانند.
- کاهش count نباید silently progress/history وابسته به Example ID را نابود کند.

---

# 9. Multilingual Example Contract — Non-negotiable

German sentence منبع/Anchor هر Example است.

هر Example:

```text
Stable Example ID
German source sentence
Persian translation of SAME German sentence, if required
English translation of SAME German sentence, if required
order
optional sense_id
```

Canonical shape:

```json
{
  "id": "CARD-ID-ex-001",
  "lang": "de-DE",
  "text": "Das hängt vom Wetter ab.",
  "order": 1,
  "translations": [
    {
      "lang": "fa-IR",
      "text": "این به آب‌وهوا بستگی دارد."
    },
    {
      "lang": "en-US",
      "text": "It depends on the weather."
    }
  ]
}
```

قواعد سخت:

- FA باید ترجمه طبیعی همان DE باشد.
- EN باید ترجمه طبیعی همان DE باشد.
- FA/EN نباید Example مستقل با Context متفاوت باشند.
- Translation نباید اطلاعات معنایی جدیدی اضافه کند که در DE نیست.
- ترجمه طبیعی بر ترجمه تحت‌اللفظی مصنوعی اولویت دارد.
- Translationها زیر همان Stable Example ID باقی بمانند.
- Required/optional بودن FA و EN را فقط Profile تعیین می‌کند.

اگر سند قدیمی همزمان می‌گوید:

```text
5 German examples + 1 independent English example
```

برای Canonical Architecture v3.1.5 آن دستور **superseded** است و نباید اجرا شود.

---

# 10. Stable Example ID — Critical

Example ID یک هویت واقعی است، نه مشتق متن.

مثال:

```text
MEN-A1-0001-ex-001
```

قواعد:

- یک‌بار ساخته شود و حفظ شود.
- با Edit متن تغییر نکند.
- با Edit ترجمه تغییر نکند.
- با Reorder تغییر نکند.
- از text hash ساخته نشود.
- از `order` ساخته نشود.
- اگر ID ظاهراً suffix عددی مثل `-ex-001` دارد، آن suffix **allocation sequence immutable** است، نه current display order؛ reorder نباید renumber کند.
- برای allocator جدید، opaque ID/ULID/UUID یا sequence پایدار فقط وقتی مجاز است که exact `card_id_pattern` / `example_id_suffix_pattern` Profile آن را بپذیرد. در Profileهای Architecture v3.1.5 از pattern و unused allocation sequence همان Profile پیروی کن.
- Duplicate نباشد.
- ID بازنشسته‌شده بدون policy صریح reuse نشود.

در update موجود:
- German Example سالم را بی‌دلیل regenerate نکن.
- Existing Example ID را preserve کن.
- FA/EN جدید را به همان Example وصل کن.
- count increase/decrease را طبق Section 8 اجرا کن.

---

# 11. Example Quality

هر German Example باید:

- طبیعی و idiomatic باشد.
- Meaning / Sense هدف را روشن نشان دهد.
- Grammar / valency واقعی Learning Unit را رعایت کند.
- مناسب CEFR Dataset باشد.
- Template-driven و تکراری نباشد.
- Contextهای متنوع داشته باشد.
- در صورت امکان usage قابل انتقال به زبان واقعی داشته باشد.
- Exampleهای یک Unit نباید فقط با تعویض اسم/فاعل clone یکدیگر باشند.

برای A1:
- جمله ساده باشد، اما مصنوعی و کودکانه نباشد.
- از grammar خارج از سطح فقط وقتی اجتناب‌ناپذیر و قابل فهم است استفاده شود.
- lexical burden بی‌دلیل بالا نرود.

برای سطوح بالاتر Profile همان Dataset authoritative است.

---

# 12. Source Policy Hard Gate

`approved` به معنی `verified` نیست.

Claim فقط وقتی `verified` است که Source واقعی بررسی شده باشد.

حداقل Claimهایی که Profile production ممکن است نیاز داشته باشد:

```text
german_sense
persian_gloss
english_gloss
morphology
grammar
rection
valency
source_membership
coursebook_lesson
...
```

قواعد:
- German grammar/rection/morphology را با Source معتبر آلمانی بررسی کن.
- DE↔FA source مرجع نهایی grammar نیست.
- Persian gloss را با Source مناسب DE↔FA بررسی کن.
- English gloss را با Source مناسب DE↔EN بررسی کن.
- ambiguity / disputed / multi-sense طبق Profile ممکن است چند independence group بخواهد.
- source claim را فقط به دلیل presence یک field، verified اعلام نکن.

---

# 13. Claim-Level Evidence — Rektion Hardening

این Rule برای production اجباری است:

اگر learner-facing field مشخصی مانند:

```text
details.rection
core.auxiliary
core.separability
grammar pattern
case government
```

نمایش داده می‌شود، evidence باید **همان claim** را پشتیبانی کند.

مثلاً:

```text
details.rection = "jemandem (+D) helfen"
```

را فقط با claim عمومی:

```text
grammar = verified
```

پوشش‌داده‌شده فرض نکن.

برای `details.rection` باید dedicated `rection` / valency claim یا evidence mapping صریح وجود داشته باشد.

اگر claim-level evidence ناقص است:
- learner-facing fact را certainty ساختگی نده.
- Unit یا field را `REVIEW_REQUIRED` کن.
- generic evidence را به claim تخصصی ارتقا نده.
- `CONTENT_VALIDATED` claim نکن تا required claim coverage کامل و audit شده باشد.

---

# 14. Source Preservation / Incremental Regeneration

در Dataset موجود:

```text
Keep good
Fix bad
Fill missing
Do not regenerate blindly
```

قواعد:
- German Example معتبر موجود را فقط به دلیل Prompt version جدید بازنویسی نکن.
- Existing Card ID حفظ شود.
- Existing Example ID حفظ شود.
- Existing Sense ID حفظ شود.
- Source-derived lesson/book membership حفظ شود.
- اگر فقط FA/EN Translation کم است، همان Translation را اضافه کن.
- اگر فقط evidence کم است، content را بی‌دلیل تغییر نده؛ evidence را تکمیل کن.
- اگر فقط یک field fail شده، repair scope را همان field/Unit نگه دار مگر dependency واقعی وجود داشته باشد.
- هر تغییر learner-facing باید قابل Audit باشد.
- merge/split/delete/retire باید mapping/audit trail داشته باشد؛ silent identity rewrite ممنوع است.

## Unknown Field Classification and Preservation — Hard Gate

در update، migration، delivery mapping، import/export roundtrip و post-package rebuild، «unknown» را از «optional ولی declared» جدا کن:

1. field را در exact resolved Contract/Profile/Type Rule/Protocol/Target Schema جست‌وجو کن.
2. اگر declared و optional است، طبق Schema در همان scope losslessly preserve شود.
3. اگر Schema یک extension point صریح (`additionalProperties`/extension map) دارد، unknown optional extension را opaque preserve کن؛ normalize/rename/relocate/reinterpret/drop ممنوع است و JSON Pointer + before/after canonical-value hash parity ثبت شود.
4. اگر scope closed است، unknown field **canonical optional محسوب نمی‌شود**. Source bytes و JSON Pointer/value را در `UNKNOWN-FIELD-PRESERVATION.json` بیرون Canonical حفظ کن، Canonical mutation/finality را `REVIEW_REQUIRED` کن و تا authoritative mapping یا Contract upgrade آن را داخل Canonical emit نکن.
5. در Contract `3.1.3`، Dataset/Unit/Sense/Example/Translation/Connection/Metadata/Provenance scopeهای مربوط closed هستند؛ بنابراین Rule شمارهٔ 4 اعمال می‌شود. `CONTENT_VALIDATED` تا resolution این unknown field ممنوع است.
6. unknown **required semantic** یا field تحت required capability پشتیبانی‌نشده = Fail-Closed / `REVIEW_REQUIRED` یا `CONFIGURATION_BLOCKED` طبق مرحلهٔ Run.

`UNKNOWN-FIELD-PRESERVATION.json` حداقل باید source artifact filename/hash، JSON Pointer، opaque value/hash، classification، resolution status و target Contract را ثبت کند. این ledger Audit artifact است و نباید به Canonical JSON closed یا User Import Artifactی که آن را dataset تشخیص می‌دهد تزریق شود.

---

# 15. Linguistic Audit — Hard Gate for CONTENT_VALIDATED

Linguistic audit را از Structural Validation جدا نگه دار.

Audit شامل:

```text
German naturalness
grammar
valency/rection
semantic correctness
Persian fidelity + naturalness
English fidelity + naturalness
DE↔FA↔EN alignment
sense coverage
CEFR suitability
connection accuracy
```

`linguistic_status` یکی از این‌ها باشد:

```text
NOT_RUN
PASS
REVIEW_REQUIRED
FAILED
```

قواعد:
- اگر audit واقعاً اجرا نشده: `linguistic_status = NOT_RUN`.
- Structural PASS را Linguistic PASS جا نزن.
- Sampling محدود را full linguistic PASS جا نزن مگر Profile صریحاً sampling policy را برای همان status کافی بداند.
- اگر required learner-facing claims یا DE↔FA↔EN alignment unresolved است: حداقل `REVIEW_REQUIRED`.
- `CONTENT_VALIDATED` فقط وقتی مجاز است که `linguistic_status = PASS`.

---

# 16. Canonical Validation and Status Gate

قبل از Delivery:

- Schema meta-validation
- Learning Unit Schema validation
- Profile validation
- Type Rule validation
- typed value validation
- Example count policy
- Example `order`: برای Architecture v3.1.5 integer، unique per Unit و دقیقاً contiguous از 1
- `(example_id, order)` mapping: در update بدون reorder authorization ثابت؛ در reorder/reduction دقیقاً مطابق `order_mapping_before_after`؛ در Delivery/roundtrip برابر Canonical post-migration
- required languages
- Stable Card/Unit/Example ID global uniqueness؛ Sense ID uniqueness در scope همان Unit؛ همهٔ referenceها معتبر
- sense refs
- connections
- claim/evidence policy
- source reconciliation
- negative tests

را واقعاً اجرا کن.

اگر Structural/Canonical validators PASS شدند ولی Linguistic Audit هنوز PASS نیست:

```text
STRUCTURE_VALIDATED
```

حداکثر status مجاز است.

فقط وقتی همهٔ شروط زیر برقرارند:

```text
Canonical/structural validators = PASS
Required claim/evidence coverage = PASS
linguistic_status = PASS
No silent loss / unresolved identity conflict
```

آنگاه:

```text
CONTENT_VALIDATED
```

مجاز است.

`STRUCTURE_VALIDATED` را `CONTENT_VALIDATED` جا نزن.

---

# 17. Canonical Output Skeleton

```json
{
  "contract_version": "<resolved semantic contract version; NOT architecture package version>",
  "profile_id": "<profile.profile_id>",
  "learning_units": [
    {
      "id": "...",
      "type": "...",
      "headword": "...",
      "persian_meaning": "...",
      "english_gloss": "...",
      "definition_de": "...",
      "core": {},
      "details": {},
      "connections": [],
      "examples": [
        {
          "id": "<CARD-ID>-ex-001",
          "lang": "de-DE",
          "text": "...",
          "order": 1,
          "translations": [
            {"lang": "fa-IR", "text": "..."},
            {"lang": "en-US", "text": "..."}
          ]
        }
      ],
      "metadata": {},
      "provenance": {}
    }
  ]
}
```

فقط fieldهایی را emit کن که Contract/Profile اجازه می‌دهند.

---

# 18. Delivery Build — Target-Owned Format, Canonical Truth

Delivery فقط وقتی ساخته شود که کاربر درخواست کرده یا Run صریحاً `delivery-build` است.

## 18.1 Canonical Source of Truth

- Canonical Learning Units همچنان Source of Truth هستند.
- Transport حق تغییر semantic truth، حذف خاموش field، تغییر Stable ID یا collapse نوع معنایی را ندارد.
- Delivery mapping فقط حمل‌ونقل است.

## 18.2 Version Roles — Do Not Couple Producer to Consumer

این Versionها را از هم جدا نگه دار:

```text
prompt_version                = producer provenance
validator_version             = QA provenance
architecture_package_version  = package provenance
contract_version              = semantic content contract
content_protocol              = optional consumer capability envelope
runtime_version               = consumer implementation
```

قواعد سخت:

- `architecture_package_version` را به‌طور خودکار در `contract_version` کپی نکن.
- `contract_version` را فقط از Canonical Contract واقعی resolve کن.
- Prompt/Validator/Architecture-package version را compatibility gate فرض نکن.
- `required_capabilities` فقط از **Semantic Contract + features واقعاً استفاده‌شدهٔ Dataset** مشتق شوند.
- Target/Runtime حق ندارد required capability را حذف، downgrade، optional یا reclassify کند؛ Target فقط support negotiation انجام می‌دهد.
- `optional_capabilities` نیز فقط declaration Contract/Dataset هستند؛ Target فقط آن‌ها را support/tolerate/report می‌کند.
- capability name اختراع نکن؛ اگر `content_protocol` emit می‌شود باید `CONTENT_PROTOCOL_SPEC` / `CAPABILITY_REGISTRY` authoritative resolve شده باشد.
- unsupported required capability → Fail-Closed.
- unsupported optional capability → preserve/tolerate/report طبق Protocol؛ semantic data را حذف نکن.
- `compatible_base_contract` را فقط وقتی emit کن که declaration **contract-owned** باشد و Validator معتبر exact contract delta را verify کرده باشد؛ assertion خود Producer به‌تنهایی کافی نیست.
- semver compatibility را حدس نزن.

## 18.3 Default Flashcards Pro Delivery

برای Architecture v3.1.5، Delivery Spec رسمی این مسیر را الزام می‌کند:

```text
Canonical JSON (audit/source of truth)
→ Universal-v2 TSV (one primary user-import dataset)
→ BUILD-METADATA.json
```

Canonical JSON به‌تنهایی فایل Import مستقیم کاربر نیست. TSV همچنان compatibility/transport است و Canonical Source of Truth باقی می‌ماند.

فقط اگر یک Delivery Spec جدیدترِ target-owned صریحاً Unified ZIP Import را تعریف کند، می‌توان `DELIVERY_FORMAT=unified-import-zip` انتخاب کرد. مشاهدهٔ اینکه یک Runtime ZIP را parse می‌کند یا Native JSON را تحمل می‌کند، جای authorization در Delivery Spec را نمی‌گیرد.

در Unified Import مجاز، Package پیشنهادی:

```text
<dataset>.zip
├── <one-primary-dataset>.<target-owned-extension>
├── BUILD-METADATA.json
└── README.md                 # optional / non-importable documentation
```

قواعد:

- ZIP باید **دقیقاً یک primary importable dataset** داشته باشد.
- Primary dataset و extension را فقط Delivery Spec تعیین می‌کند.
- برای Architecture v3.1.5 primary importable dataset همان Universal-v2 TSV است؛ Canonical JSON audit/source artifact است، نه primary user-import dataset.
- داخل Unified Import ZIP چند JSON/TSV قابل‌Import مستقل قرار نده؛ ambiguity باید Fail-Closed بماند.
- `BUILD-METADATA.json` Sidecar است، dataset دوم نیست.
- Reportهای اضافی را فقط با extension/placementی داخل Import ZIP بگذار که Importer صریحاً non-importable می‌داند؛ در غیر این صورت بیرون Package یا در Audit Package جدا تحویل بده.
- `MANIFEST.json` را به‌عنوان فایل اضافه داخل Import ZIP قرار نده مگر Target Importer صریحاً آن را می‌شناسد/نادیده می‌گیرد؛ Manifest فنی نباید به اشتباه dataset دوم تشخیص داده شود.
- filename/path امن باشد؛ path traversal یا absolute path ممنوع.
- ZIP compression فقط از modeهای پشتیبانی‌شدهٔ Target استفاده کند (مثلاً Stored/Deflate اگر Target هر دو را پشتیبانی می‌کند).

## 18.4 Native Canonical JSON

برای Native JSON:

- Canonical unit structure باید lossless باقی بماند.
- `contract_version` semantic contract واقعی باشد.
- در Contract `3.1.3`، top-level فقط `contract_version`, `profile_id`, `learning_units` است؛ `content_protocol` را به Canonical object اضافه نکن.
- اگر Target آینده Content Protocol envelope جداگانه‌ای را تعریف می‌کند، exact envelope فقط طبق همان Target Schema ساخته شود و Canonical Dataset بدون تغییر در field/path تعریف‌شدهٔ آن حمل شود.
- اگر چنین Schemaای resolve نشده است، protocol/capability metadata را فقط در `RUN-METADATA.json` گزارش کن و Native envelope اختراع نکن.

## 18.5 Universal TSV Compatibility

اگر TSV صریحاً خواسته شد یا Target واقعاً TSV می‌خواهد:

- Delivery Spec واقعی را authoritative بگیر.
- 23-column Universal-v2 را فقط اگر همان Spec فعلی آن را الزام می‌کند بساز.
- TSV هرگز Canonical Source of Truth نیست.
- اگر Delivery Spec `custom_fields.canonical_unit` یا canonical envelope را تعریف کرده، باید clone کامل Canonical Learning Unit را losslessly حفظ کند.
- Flat compatibility projection جای Canonical Data را نگیرد.
- هر projection غیر-isomorphic یا lossy باید یک machine-readable `MAPPING-LIMITATIONS.json` در **Audit Package** تولید کند؛ آن را داخل User Import ZIP نگذار مگر Importer صریحاً non-importable بودنش را بداند.
- Report حداقل `artifact_type`, `report_version`, source/target filename+SHA-256, Delivery Spec ID, `lossless`, `canonical_backstop`, `presentation_only_omissions[]`, `semantic_losses[]` و `status` را داشته باشد.
- در Universal-v2 معماری 3.1.5، projection بصری non-isomorphic است؛ اگر clone کامل `custom_fields.canonical_unit` parity PASS دهد، `lossless=true`, `semantic_losses=[]`, `status=PASS_WITH_CANONICAL_BACKSTOP` ثبت شود. هر semantic loss واقعی → `TRANSPORT_VALIDATED` ممنوع.
- اگر target TSV Spec هیچ lossless canonical envelope ندارد و Delivery موردنیاز lossless است، `TRANSPORT_VALIDATED` ممنوع است.
- JSON cells compact باشند.
- tab/newline واقعی در TSV cell ممنوع.
- هیچ Unit به دلیل limitation مقصد بی‌صدا حذف نشود.

## 18.6 BUILD-METADATA

در Delivery این Prompt:

```text
prompt_version = "v3.1.9"
```

باشد.

`BUILD-METADATA` باید **resolved Target Sidecar field contract** را دقیقاً رعایت کند. این contract می‌تواند JSON Schema یا prose normative بدون ابهام در Delivery Spec باشد. اگر هیچ field contract یا `schema_profile` پشتیبانی‌شده resolve نشد: `CONFIGURATION_BLOCKED`.

برای Architecture v3.1.5، Sidecar contract حداقلی دقیقاً این fieldها را تعریف می‌کند:

```text
artifact_type
metadata_version
prompt_version
validator_version
data_build_id
schema_profile
data_file
data_sha256
```

Fieldهای `delivery_target`, `delivery_format`, `semantic_contract_version`, `profile_id`, `architecture_package_version` و role/media-type/hashهای چندگانه در `RUN-METADATA.json`/Audit ثبت شوند، مگر Target Sidecar آن‌ها را صریحاً اجازه دهد. آن‌ها را صرفاً برای self-description به Sidecar closed یا target-owned تحمیل نکن.

قواعد:
- field name واقعی Target Spec authoritative است؛ alias جدید داخل Sidecar اختراع نکن.
- Sidecar نباید Architecture-package version را به‌عنوان semantic contract جا بزند.
- `data_file`/`data_sha256` باید دقیقاً با primary TSV bytes واقعی match باشد؛ Audit manifest نقش/Media Type و hash سایر artifactها را جدا ثبت کند.
- builder همراه Architecture v3.1.5 مقدار package-owned `prompt_version=v3.1.5` می‌نویسد. وقتی Producer واقعی این Prompt است، پس از Build فقط Sidecar تولیدی را به `prompt_version=v3.1.9` اصلاح کن، `data_sha256` را تغییر نده و Delivery validator را دوباره اجرا کن. فایل builder authoritative معماری را rewrite نکن.
- stale/missing Sidecar schema یا unsupported `schema_profile` → `CONFIGURATION_BLOCKED` یا Delivery FAIL، نه حدس.

هر رشته stale مانند:

```text
prompt_version="v3.1.4"
prompt_version="v3.1.5"
prompt_version="v3.1.6"
prompt_version="v3.1.7"
prompt_version="v3.1.8"
```

در instruction فعال **Prompt package جاری** ممنوع است، مگر historical note/changelog. literalهای version داخل Architecture package/builder provenance همان release هستند؛ اسکن آن‌ها نباید false failure بسازد، ولی output Sidecar Run جاری باید `v3.1.9` باشد.

---

# 19. Delivery Validation — Format-Aware and Post-ZIP

اگر Delivery ساخته شد، validation باید بر اساس Format واقعی انجام شود.

## 19.1 Common Parity Checks

برای همه Formatها:

- primary artifact parseable
- Canonical Unit count parity
- Canonical ID parity
- headword / meaning / type / definition parity
- English gloss parity
- Example ID + DE + FA + EN parity
- `(example_id, order)` parity با Canonical post-migration؛ تغییر نسبت به snapshot قبلی فقط اگر در Plan authorized ثبت شده باشد
- declared optional/extension field opaque-value parity where Schema permits؛ closed-schema unknown طبق Audit ledger باید unresolved/blocking بماند
- Sense ID/ref parity where applicable
- Connection semantic-kind parity
- provenance parity
- no unauthorized derived unit
- no silent semantic loss
- no duplicate Stable IDs
- BUILD-METADATA target filename/role clarity
- SHA-256 parity

## 19.2 Unified Import ZIP Checks

اگر `DELIVERY_FORMAT=unified-import-zip`:

- ZIP واقعاً open/extract شود.
- path traversal / unsafe paths وجود نداشته باشد.
- دقیقاً **یک primary importable dataset** داخل Package باشد.
- `BUILD-METADATA.json` اگر required/produced است parseable و با همان primary artifact match باشد.
- Sidecar SHA-256 با bytes واقعی artifact داخل ZIP برابر باشد.
- primary dataset بعد از Extract دوباره parse/validate شود.
- Delivery validator متناسب با نوع primary روی artifact Extractشده دوباره PASS شود.
- Canonical validator روی exact Canonical source artifact اجرا و hash آن به primary/parity report bind شود؛ فقط اگر primary خودش Canonical JSON است همان فایل primary را Canonical-validate کن.
- اگر Content Protocol وجود دارد:
  - protocol ID/version معتبر باشد؛
  - required capabilities با features واقعی Dataset سازگار باشند؛
  - optional capabilities required جا زده نشوند؛
  - producer versions فقط provenance باشند.
- package نباید dataset دومِ accidental از نوع JSON/TSV داشته باشد.
- package filename/hash نهایی بعد از Build ثبت شود.
- schema-permitted optional/extension fields بعد از Extract/reparse همان JSON Pointer/value-hash parity را حفظ کنند؛ closed-schema unknown نباید داخل Canonical ظاهر شود و Audit ledger آن باید محفوظ باشد.
- اگر validator/audit report برای Gate استفاده می‌شود، evidence binding Section 22 را PASS کند.

## 19.3 TSV Compatibility Checks

اگر TSV ساخته شد:

- exact header/order طبق Delivery Spec
- unique row IDs
- parseable JSON cells
- row count parity
- canonical_unit presence اگر Spec الزام می‌کند
- `MAPPING-LIMITATIONS.json` presence/parity برای projection non-isomorphic یا lossy؛ official Universal-v2 باید canonical-backstop status صریح داشته باشد
- `(example_id, order)` parity
- schema-permitted extension preservation در canonical envelope؛ closed-schema unknown فقط در Audit ledger
- semantic parity کامل

## 19.4 Hash Rules

- هر SHA-256 باید target filename/role مشخص داشته باشد.
- hash بدون مشخص‌کردن اینکه متعلق به dataset/ZIP/Metadata است ممنوع است.
- ZIP SHA-256 معمولاً بیرون ZIP گزارش/sidecar شود؛ ZIP نمی‌تواند hash نهایی خودش را پیشاپیش داخل خودش authoritative نگه دارد.
- Metadata hash را با primary dataset hash یا ZIP hash اشتباه نگیر.

فقط بعد از PASS واقعی Delivery validator و post-package verification:

```text
TRANSPORT_VALIDATED
```

مجاز است.

`TRANSPORT_VALIDATED` هنوز live runtime import success نیست.

---

# 20. Runtime Verification — Explicit Modes and Capability-Aware Gates

Artifact compatibility و live runtime readiness دو چیز مستقل‌اند.

Runtime compatibility را از Prompt version یا Architecture-package version حدس نزن. Consumer باید semantic contract / registered adapter / required capabilities را بررسی کند، اگر Target چنین modelی دارد.

## Mode: none

اگر `RUNTIME_VERIFICATION_MODE=none`:
- Runtime claim نکن.
- `CURRENT_RUNTIME_NOT_VERIFIED` اعلام کن.
- content/delivery status را مستقل گزارش کن.

## Mode: isolated-runtime

`APP_COMPATIBLE` فقط وقتی ممکن است که همهٔ موارد زیر روی isolated writable runtime **همان target implementation** واقعاً PASS شوند:

```text
exact target runtime/version resolved
semantic contract/adaptor negotiation resolved
all required capabilities supported
non-empty existing library/state
writable isolated environment
transactional commit path
reload durability
import/export or canonical roundtrip
ID preservation
no silent loss
no unexpected destructive migration
```

Parser-only، ZIP-open-only، capability-list-only یا mock-only test برای `APP_COMPATIBLE` کافی نیست.

`APP_COMPATIBLE` به معنی current user's live runtime readiness نیست.

## Mode: actual-user-runtime

قبل از mutation/import واقعی:
- target runtime/version را از current runtime evidence resolve کن.
- همان artifact/hash و import mode را lock کن.
- اگر preflight لازم طبق runtime/import policy PASS شد:
  - `RUNTIME_PREFLIGHT_PASS`
- اگر blocked/conflicting:
  - `RUNTIME_BLOCKED`

`IMPORT_VERIFIED` فقط وقتی مجاز است که همهٔ موارد زیر برای **همان artifact و همان import mode** در actual user runtime PASS شوند:

```text
actual target runtime identified
semantic contract/adaptor negotiation PASS
required capabilities PASS
preflight PASS
exact artifact identity/hash recorded
exact import mode recorded
transactional/persistent commit confirmed
reload/restart persistence confirmed
post-reload data parity confirmed
roundtrip/export-readback confirmed when supported/required
stable IDs preserved
no silent data loss
```

صرفاً Auto-Detect موفق، Preview سبز، success toast، parser PASS یا نمایش موقت UI برای `IMPORT_VERIFIED` کافی نیست.

اگر exact actual-user-runtime preflight برای **همان artifact hash و همان import mode** PASS نشده است:
- «Import VERIFIED» نگو.
- کاربر را به Import فوری با wordingی مثل «الان Import کن» یا «برای current runtime امن است» هدایت نکن.
- `CURRENT_RUNTIME_NOT_VERIFIED` را صریح گزارش کن.
- Artifact را فقط با `TRANSPORT_VALIDATED` یا در صورت isolated evidence با `APP_COMPATIBLE` گزارش کن.
- برای actual mutation، preflight واقعی + backup/rollback policy موردنیاز Target + import-mode confirmation لازم است.

`IMPORT_READY` label مبهم و ممنوع است.

---

# 21. Status Vocabulary — Truthful and Non-Ambiguous

Run Configuration:

```text
CONFIGURATION_BLOCKED
CONFIGURATION_RESOLVED
```

Artifact:

```text
STRUCTURE_VALIDATED
CONTENT_VALIDATED
TRANSPORT_VALIDATED
APP_COMPATIBLE
REVIEW_REQUIRED
FAILED
```

Current Runtime:

```text
CURRENT_RUNTIME_NOT_VERIFIED
RUNTIME_PREFLIGHT_PASS
RUNTIME_BLOCKED
IMPORT_VERIFIED
```

قواعد:
- هیچ status را بدون Evidence لازم اعلام نکن.
- status پایین‌تر را با wording بازاری به status بالاتر تبدیل نکن.
- `STRUCTURE_VALIDATED` یعنی linguistic PASS هنوز claim نشده.
- `TRANSPORT_VALIDATED` یعنی transport/parity PASS؛ live import success نیست.
- `APP_COMPATIBLE` فقط isolated-runtime compatibility است مگر evidence actual-runtime جداگانه موجود باشد.
- `IMPORT_VERIFIED` فقط actual-user-runtime با persistence/reload evidence است.
- این vocabulary/state vector فقط در Run/Audit reporting است؛ آن را داخل Canonical Dataset، BUILD-METADATA یا `RUNTIME-IMPORT-EVIDENCE.json` تزریق نکن مگر Schema همان artifact field را صریحاً تعریف کند.

## Formal Validation State Vector

Statusهای مختلف را در یک label واحد مخلوط نکن. حداقل state vector گزارش شود:

```json
{
  "structure_status": "PASS|FAIL|NOT_RUN",
  "linguistic_status": "PASS|FAILED|REVIEW_REQUIRED|NOT_RUN",
  "transport_status": "PASS|FAIL|NOT_RUN",
  "isolated_runtime_status": "PASS|FAIL|NOT_RUN",
  "actual_runtime_status": "PASS|FAIL|NOT_RUN"
}
```

Roll-up rules:

```text
CONTENT_VALIDATED
  requires structure=PASS AND linguistic=PASS

TRANSPORT_VALIDATED
  requires transport=PASS
  and does not imply linguistic/runtime PASS

APP_COMPATIBLE
  requires isolated_runtime=PASS

IMPORT_VERIFIED
  requires actual_runtime=PASS
  for same artifact hash + import mode
```

قواعد:
- اگر `linguistic_status=FAILED/REVIEW_REQUIRED/NOT_RUN` است، هیچ presentation/report نباید `CONTENT_VALIDATED` را headline کند.
- state componentهای FAIL/REVIEW_REQUIRED را در summary پنهان نکن.
- roll-up status باید از همین implication rules محاسبه شود، نه wording آزاد.

---

# 22. Packaging — Separate User Import Artifact from Audit Evidence

دو مفهوم را قاطی نکن:

```text
A) User Import Artifact
B) Production/Audit Evidence
```

## A. User Import Artifact

Format User Import Artifact را Delivery Spec واقعی تعیین می‌کند. برای Architecture v3.1.5، خروجی روزمرهٔ مستقیم **Universal-v2 TSV + BUILD-METADATA sidecar** است؛ Canonical JSON و Audit evidence جدا حفظ می‌شوند.

اگر یک Delivery Spec جدیدتر Unified Import ZIP را صریحاً مجاز کرد، خروجی می‌تواند یک ZIP واحد باشد.

حداقل پیشنهادی:

```text
<dataset>.zip
├── <one-primary-dataset>.<target-owned-extension>
├── BUILD-METADATA.json
└── README.md   # optional
```

قواعد:

- فقط یک importable dataset اصلی.
- Primary format فقط از Delivery Spec target-owned می‌آید؛ Native Canonical JSON برای Architecture v3.1.5 فایل Import مستقیم نیست.
- فایل‌های report اضافی نباید به‌صورت JSON/TSV دوم باعث ambiguity Importer شوند.
- اگر Target فقط filenameهای مشخصی را non-importable می‌داند، همان قواعد را رعایت کن.
- ZIP نهایی باید قابل Auto-Detect و Extract باشد.

## B. Production/Audit Evidence

بسته یا فایل‌های Audit باید شامل Evidence لازم باشند، مثلاً:

```text
Canonical JSON or exact canonical source artifact
Validation report
Claim/evidence report
Linguistic audit report/status
RUN-METADATA.json
Delivery artifact reference/hash
BUILD-METADATA.json copy/reference if delivery exists
Optional runtime compatibility evidence
Validator execution evidence
Complete audit-package file inventory/manifest
MIGRATION_PLAN + full retirement/tombstone archive where applicable
UNKNOWN-FIELD-PRESERVATION ledger where applicable
MAPPING-LIMITATIONS report for non-isomorphic/lossy transport
README
```

این Audit material لازم نیست همگی داخل User Import ZIP باشند.

`RUN-METADATA.json` حداقل شامل:

```text
prompt_version = "v3.1.9"
architecture_package_version
semantic contract_version
profile_id
run_mode
delivery_format
runtime_verification_mode
generated_at
artifact hashes with explicit target filenames/roles
```

باشد، بدون ادعای status فراتر از evidence.

## Validator / Audit Evidence Binding — Hard Gate

هر validator/audit report که برای status gate استفاده می‌شود باید حداقل این binding را داشته باشد:

```text
validator_id
validator_version
validator_artifact_hash
input_filename
input_sha256
execution_id
executed_at
full_or_sampled
policy_id
exit_code
result
findings_count
```

قواعد:
- `input_sha256` باید با artifact واقعی همان Run/Extract برابر باشد.
- report با hash متفاوت stale است و **هیچ status gate** را satisfy نمی‌کند.
- اگر audit sampled است، `full_or_sampled=sampled` را صریح بنویس؛ sampled evidence را full PASS جا نزن مگر policy صریحاً مجاز کند.
- result string بدون execution binding کافی نیست.
- اگر validator artifact خودش version/hash قابل resolve ندارد، evidence ناقص است.
- Audit Package inventory باید همه payload files را reconcile کند؛ اگر manifest خودش و manifest hash را self-list نمی‌کند، count wording باید صریحاً این تفاوت را توضیح دهد.

## Post-Package Verification

پس از ساخت User Import Artifact؛ اگر ZIP است آن را دوباره Extract کن، و اگر TSV/JSON مستقیم است exact delivered bytes را reopen کن:

- ZIP را در صورت وجود دوباره Extract کن.
- file inventory را verify کن و Audit Package manifest/file-count reconciliation را انجام بده.
- exactly-one-importable-dataset rule را برای هر Import Package/ZIP verify کن.
- hashها را verify کن.
- Delivery validator را روی primary artifact Extractشده دوباره اجرا کن.
- Canonical validator را روی exact Canonical source artifact اجرا کن و input hash/parity binding آن به primary را verify کن؛ primary TSV را با Canonical validator اجرا نکن.
- اگر Linguistic PASS claim شده، audit report/status parity را verify کن.
- Metadata hash target/parity را check کن.
- claimهای status را با evidence تطبیق بده.
- stale active prompt-version string را scan کن.
- ZIP SHA-256 را با target filename روشن بیرون Package ثبت کن.

---

# 23. Production Workflow

برای production batch:

```text
1. Resolve + validate configuration; fail closed on ambiguity
2. Inventory Source
3. Resolve identities (Unit + Sense + Example)
4. If split/merge/retire/reactivate/reduction/reorder is needed, require authorization + input-hash-bound MIGRATION_PLAN + external archive before mutation
5. Preserve valid existing content; preserve declared optional/extensions in place and ledger closed-schema unknowns outside Canonical
6. Reconcile target example count using deterministic update lifecycle policy
7. Build/fill common fields
8. Apply typed Type Rules
9. Build/verify Connections; authorize derived units
10. Build/fill German Examples
11. Attach FA/EN translations to SAME DE Example
12. Complete claim-level evidence
13. Linguistic audit
14. Canonical/structural validation including post-migration order + schema-permitted extension parity/closed-schema unknown blocking
15. Repair only failed/review-required items
16. Re-run linguistic + canonical gates as applicable
17. Claim STRUCTURE_VALIDATED or CONTENT_VALIDATED truthfully
18. Resolve Delivery Target/Format only if requested
19. Build one primary Delivery artifact in the target-owned format; Architecture v3.1.5 uses Universal-v2 TSV, Unified ZIP only when a newer Delivery Spec authorizes it
20. Validate semantic parity + metadata/hash + sidecar schema + package structure
21. Re-extract ZIP and re-run post-package validators with evidence binding
22. Runtime verification only if requested/available
23. Report user import artifact separately from audit/runtime evidence
```

هیچ مرحله QA را برای سرعت حذف نکن.

---

# 24. Batch Safety — Separate Architecture Pilot from Dataset Pilot

در batchهای بزرگ:

## A. Prompt / Architecture Regression Pilot

برای بررسی عمومی Prompt/Architecture:
- چند Type مختلف از Typeهای واقعی تعریف‌شده را representative تست کن.
- فقط Typeهایی را استفاده کن که fixture/source معتبر دارند.
- هدف: generic behavior و Type Rule routing.

## B. Dataset Production Pilot

برای Run یک Dataset مشخص:
- فقط Typeهایی را تست/تولید کن که Dataset Profile/Source همان Run اجازه می‌دهد.
- اگر Dataset فقط Verb است، برای «تنوع Type» Nomen/Adjektiv از خودت اضافه نکن.
- Pilot باید representative همان Dataset باشد: senses، rection، separability، examples، translations، evidence و update cases در صورت وجود.

سپس:
- batch را expand کن.
- Failed/Review items را جداگانه repair کن.
- کل Dataset را برای مشکل محلی regenerate نکن.
- Resume state و mapping IDs را حفظ کن.
- count reconciliation اجباری است:

```text
Source items
→ preserved/merged/split/derived-authorized dispositions
→ Canonical Units
→ Delivery units/artifact (if any)
```

هر اختلاف باید توضیح‌پذیر و audit-able باشد؛ split/merge/retire/reactivate/reduction/reorder فقط با `MIGRATION_PLAN` معتبر.

---

# 25. Explicit Anti-Patterns

ممنوع:

```text
guessing a missing Profile/Contract
silently choosing between conflicting Profiles
copying architecture_package_version into semantic contract_version without evidence
using prompt_version or validator_version as runtime compatibility gate
assuming unknown semantic contracts are semver-compatible
inventing compatible_base_contract without explicit authorization
inventing required capabilities not actually required by the dataset
5 DE + 1 unrelated EN as canonical model
fixed example1..example6 canonical schema
English gloss used as sentence translation
FA/EN translation detached from DE Example ID
Example ID from text hash
Example ID changed after reorder
Sense ID from text/hash/order
Sense ID changed after wording/reorder
automatic example deletion when target count decreases without policy
silent source row drop
silent semantic merge/split without mapping
unauthorized derived Learning Units
human-readable type label emitted as invented enum
NVV collapsed into generic collocation
learner-facing rection without claim-level evidence
structural PASS reported as CONTENT_VALIDATED
linguistic NOT_RUN reported as linguistic PASS
TSV-first delivery when a lossless canonical ZIP/JSON target is available and requested
multiple importable JSON/TSV datasets inside one unified import ZIP
putting MANIFEST.json inside an import ZIP when the target may mis-detect it as a dataset
unlabeled SHA-256 target
transport PASS reported as live import success
isolated APP_COMPATIBLE reported as current-runtime verification
IMPORT_VERIFIED without persistent commit + reload parity
runtime guessing
dropping declared optional/extension fields, or silently injecting closed-schema unknowns into Canonical
target-shaped required_capabilities
producer-only compatible_base_contract assertion without contract-owned validation
split/merge/retire/reactivate/reduction/reorder without authorization + input-bound MIGRATION_PLAN/archive
renumbering Example IDs after reorder
changing (example_id, order) mapping silently
TSV lossy projection without MAPPING-LIMITATIONS
stale validator report whose input_sha256 does not match the artifact
telling the user to import immediately without same-artifact actual-runtime preflight
mass regeneration when only one field is missing
```

---

# 26. Definition of Done

## Content Production

Content generation فقط وقتی **fully Done** است که:

```text
Configuration resolved
Source reconciled
Unit IDs stable
Sense IDs stable where used
Example IDs stable
Migration Plan PASS where structural identity/count reduction occurred
Declared optional/extensions preserved losslessly; closed-schema unknowns ledgered and resolved before finality
Required fields complete
Type rules valid
Examples dynamic
Example count lifecycle reconciled
Example (ID, order) mapping valid; changes authorized/mapped; delivery equals post-migration Canonical
DE↔FA↔EN aligned under same Example ID
Required evidence complete
Required claim-level coverage PASS
linguistic_status = PASS
Canonical validator PASS
No silent loss
No unresolved identity conflict
```

اگر Structural PASS است ولی Linguistic PASS نیست:
- full Done نیست.
- حداکثر `STRUCTURE_VALIDATED` یا `REVIEW_REQUIRED`.

## Delivery

اگر Delivery خواسته شده، format-specific gates باید PASS شوند. برای Unified ZIP مجاز:

```text
Canonical→Primary Dataset parity PASS
Exactly one primary importable dataset in ZIP
BUILD-METADATA resolved target field contract PASS
BUILD-METADATA target/hash parity PASS
Semantic contract/protocol metadata truthful
Required capabilities derived only from Contract + Dataset features
No producer-version compatibility coupling
Example (ID, order) parity PASS
Schema-permitted extension roundtrip parity PASS; no unresolved closed-schema unknown
ZIP extract/reparse PASS
Post-ZIP Delivery validator PASS + exact Canonical source hash/validator binding PASS
Validator evidence input-hash binding PASS
Delivery validator PASS
ZIP SHA-256 recorded with filename
```

برای Universal-v2 TSV رسمی Architecture v3.1.5 نیز exact 23-column header، deep `canonical_unit` parity، BUILD-METADATA TSV hash و `MAPPING-LIMITATIONS` canonical-backstop report باید PASS شوند.

بعد از این مرحله حداکثر:

```text
TRANSPORT_VALIDATED
```

مجاز است، مگر Runtime evidence جداگانه وجود داشته باشد.

## Runtime

Runtime claim فقط با Runtime Evidence واقعی و طبق Section 20.

---

# 27. Final Reporting Format

در پایان خلاصه را جداگانه گزارش کن:

```text
CONFIGURATION
- Run status:
- General contract:
- Dataset profile:
- Type rules:
- Run mode:
- Delivery target:
- Delivery format:
- Runtime verification mode:
- Conflicts/missing inputs:

CONTENT
- Artifact status:
- Semantic contract version:
- Architecture package version:
- Units:
- Authorized derived units:
- Examples:
- FA translations:
- EN translations:
- Duplicate Unit IDs:
- Duplicate Sense IDs within any Unit:
- Duplicate Example IDs:
- Example-count migrations:
- Migration-plan status:
- Declared extension preservation / closed-schema unknown ledger:
- Example order parity:
- Review-required items:
- Linguistic audit status:

EVIDENCE
- Source policy:
- Claim coverage:
- Rektion claim coverage:
- Validator evidence binding:
- Stale evidence rejected:
- Unverified claims:

DELIVERY
- Requested: yes/no
- Format:
- Transport status:
- Primary dataset filename:
- Primary dataset units/rows:
- Primary dataset SHA-256:
- BUILD-METADATA status:
- Sidecar schema/profile:
- MAPPING-LIMITATIONS status (if TSV):
- Unified ZIP filename:
- Unified ZIP SHA-256:
- Post-ZIP verification:

RUNTIME
- Verification mode:
- Target runtime:
- Semantic adapter/capability status:
- Artifact compatibility:
- Current runtime status:
- Import mode/artifact identity if tested:

LIMITATIONS
- ...
```

هیچ limitation را پنهان نکن.

# Final principle

```text
Prepare language intelligence before Import.
Keep semantic data canonical and lossless.
Fail closed on unresolved configuration.
Identity survives edits, reorder and only explicitly planned deterministic migration.
Producer versions are provenance; semantic contract + capabilities define compatibility.
Architecture package version is not automatically the semantic contract version.
Use the target-owned import format; if it is a ZIP, require exactly one primary dataset.
Flashcards Pro consumes content; it does not invent it.
Every German Example is one multilingual semantic unit:
DE source ↔ FA translation ↔ EN translation.
Structural success is not linguistic success.
Declared optional/extension data survives roundtrips; closed-schema unknown and unknown required semantics fail closed without silent loss.
Transport success is not live import success.
```
