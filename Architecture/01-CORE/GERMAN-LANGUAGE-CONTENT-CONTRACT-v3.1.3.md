# German Language Content Contract v3.1.3

Contract ID: `gfp-german-language-content@3.1.3`

## 1. Authority boundaries

```text
CONTENT CONTRACT
≠ DATASET PROFILE
≠ TYPE RULES
≠ PRESENTATION SETTINGS
≠ PRACTICE SETTINGS
```

General Contract shape و invariantهای جهانی را تعیین می‌کند. Profile policy یک Dataset را می‌دهد. Type Rule value shape مربوط به نوع را تعیین می‌کند. Presentation و Practice فقط مصرف‌کننده‌اند.

## 2. Canonical dataset

```json
{
  "contract_version": "3.1.3",
  "profile_id": "architecture-proof@1.0.0",
  "learning_units": []
}
```

## 3. Canonical Learning Unit

```json
{
  "id": "CARD-ID",
  "type": "verb",
  "headword": "...",
  "persian_meaning": "...",
  "english_gloss": "...",
  "definition_de": "...",
  "senses": [],
  "core": {},
  "details": {},
  "connections": [],
  "examples": [],
  "metadata": {},
  "provenance": {}
}
```

Global required fields فقط `id`, `type`, `headword`, `core`, `examples`, `metadata`, `provenance` هستند. `persian_meaning`, `english_gloss`, `definition_de`, `senses`, `details` و `connections` در General Contract optional هستند؛ Profile یا Type Rule می‌تواند requirement را افزایش دهد. Placeholder برای دادهٔ غایب تولید نشود.

`type` identifier توسعه‌پذیر lowercase است. Type آینده با Rule جدید یا Generic Rule کار می‌کند و Canonical Schema را تغییر نمی‌دهد.

## 4. Dynamic rich examples

هیچ numbered/fixed Example field در Canonical Model وجود ندارد. `examples[]` هیچ count limit در Schema ندارد. Count و per-Type override فقط از Profile resolve می‌شوند.

هر Example:

```json
{
  "id": "CARD-ID-ex-001",
  "lang": "de-DE",
  "text": "Das hängt vom Wetter ab.",
  "order": 1,
  "sense_id": "sense-01",
  "translations": [
    {"lang": "fa-IR", "text": "این به آب‌وهوا بستگی دارد."},
    {"lang": "en-US", "text": "It depends on the weather."}
  ]
}
```

Translationها باید همان meaning/sense جملهٔ آلمانی را طبیعی منتقل کنند، اطلاعات تازه نیفزایند و omission جدی نداشته باشند. زبان‌های required را Profile تعیین می‌کند؛ General Contract سه‌زبانه بودن همهٔ Datasetهای آینده را فرض نمی‌کند.

## 5. English separation

`english_gloss` معادل کوتاه Learning Unit است. Translation انگلیسی جمله فقط داخل Example مربوط قرار می‌گیرد. English sentence با context مستقل جای sentence translation را نمی‌گیرد.

## 6. Stable Example identity

- ID یک‌بار allocate و persist می‌شود.
- Edit text/translation و reorder ID را تغییر نمی‌دهد.
- ID از hash، text content یا current order مشتق نمی‌شود.
- Duplicate ID در Dataset ممنوع است.
- Retired ID بدون تصمیم هویتی صریح reuse نمی‌شود.
- Example تازه serial استفاده‌نشده می‌گیرد.

`metadata.retired_example_ids` و previous-snapshot validation برای جلوگیری از reuse آینده‌اند؛ هیچ داده یا ID پیشین در معماری الزام نشده است.

## 7. Sense registry

Unit چندمعنایی می‌تواند registry زیر را داشته باشد:

```json
{"id":"sense-01","meaning_fa":"...","gloss_en":"...","definition_de":"..."}
```

`sense_id` یک reference پایدار است، نه index. اگر Example یا Connection از آن استفاده کند باید در همان Unit وجود داشته باشد. Unit تک‌معنایی به registry نیاز ندارد.

## 8. Unified connections

```json
{
  "text": "eine Entscheidung treffen",
  "kind": "nvv",
  "sense_id": "sense-01"
}
```

Allowed kindها: `collocation`, `nvv`, `pattern`, `fixed_expression`, `prepositional_pattern`, `common_combination`, `other`.

Kind فقط semantics را ثبت می‌کند. هیچ kind یک Box، column، order یا visibility را تحمیل نمی‌کند. Presentation می‌تواند connectionهای مختلف را در یک Section مشترک render کند.

اگر خود expression هدف اصلی است، Type اصلی مانند `nomen_verb_verbindung` می‌گیرد. وجود همان text در connections یک Unit دیگر فقط رابطهٔ جانبی است.

## 9. Typed Type Rules

هر `core` و `details` field یک Field Spec دارد: type، required، nullable، enum، array items یا object properties. Validator value واقعی را بررسی می‌کند. Profile می‌تواند fieldهای typed اختیاری را برای Dataset/Type مشخص required کند، ولی field ناشناخته نمی‌سازد.

Type Rule هیچ CEFR، language، Example count یا UI rule ندارد. Typeهای دارای shape مشترک می‌توانند یک Rule family با `applies_to` چندگانه داشته باشند.

Requirementهای learner-facing باید از semantics بیایند، نه از یکسان‌سازی shape. در Nomen، `plural_only=false` وجود `singular` و `plural_only=true` وجود `plural` را الزام می‌کند؛ `plural` برای Nomen عادی optional است. در Phrase family عمومی نیز `function` optional است و فقط Profile دارای تصمیم واقعی می‌تواند آن را required کند.

## 10. Dataset Profile

Profile مالک CEFR، Dataset tags، allowed types، required Unit fields، definition policy، source/translation languages، default Example count، per-Type override، source policy، linguistic strictness و typed field requirementهای اضافی است.

Count resolution:

```text
effective policy = examples.default overlaid by examples.by_type[type]
```

نبود override به معنی استفاده از default است.

## 11. Provenance

`provenance.sources[]` فقط Evidence واقعی Run را نگه می‌دارد: `source_id`, `source_kind`, `what_was_verified`, `verification_status` و locator/date اختیاری. Source Registry مجاز بودن منبع، roles، allowed claims و independence group را تعیین می‌کند. `approved` با `verified` یکی نیست. Profile برای هر Claim حداقل verified source و در حالت risky حداقل independence group را تعیین می‌کند.

## 12. Responsibility boundary

Content Preparation مسئول headword، meaning/gloss/definition، morphology/rection، German examples، translationهای required، connections، sense mapping، IDs، validation و provenance است.

Flashcards Pro فقط Render، Word/Sentence/Mixed، Flashcard/Quick/Writing/Audio، visibility، direction، SRS، TTS، navigation، filtering و sorting را انجام می‌دهد. تولید Example/Translation، حدس Meaning و correction زبانی در Runtime ممنوع است.

## 13. Validation and evidence

Schema meta-validation، structural/profile/type validation، linguistic audit و provenance verification gateهای جدا هستند. هیچ gate اجرا‌نشده PASS نیست.

## 14. Presentation independence

Content Contract هیچ layout، row count، Card height، reveal policy، Practice mode یا visual section تعیین نمی‌کند. Arrayهای `examples` و `connections` صرفاً داده‌اند.

## 15. Delivery / Transport boundary (v3.1.3 semantic + v3.1.4 runtime-status overlay)

Semantic Canonical Dataset این Contract منبع حقیقت است، اما لزوماً فایل Import مستقیم Runtime نیست.

```text
Semantic Canonical JSON
        ↓ lossless adapter
Delivery Transport Artifact
        ↓ target runtime importer
Runtime Card Model
```

برای German Flashcards Pro مقصد رسمی delivery برابر است با:

- Runtime content contract: `gfp-german-learning-content@1.0.0`
- Transport: `gfp-universal-card@2.0`
- Schema profile: `universal-v2`
- Base envelope: 23 ستون رسمی Universal v2

قواعد:

1. Canonical JSON باید حتی بعد از ساخت Transport artifact حفظ شود.
2. Adapter حق حذف Learning Unit، Example، Translation، Connection، Sense، typed field یا Provenance را ندارد.
3. اگر Runtime یک fact را به‌صورت native نمایش نمی‌دهد، آن fact باید losslessly در `custom_fields.canonical_unit` یا bridge field مستند حفظ شود.
4. `connections.kind` semantic است؛ NVV و Collocation در Transport نباید merge معنایی شوند.
5. Valid بودن Canonical JSON به‌تنهایی Import-readiness را ثابت نمی‌کند.
6. Valid بودن TSV به‌تنهایی Runtime import verification را ثابت نمی‌کند.
7. Runtime-status vocabulary از Master Prompt v3.1.4 می‌آید و فقط delivery/finality governance را override می‌کند؛ semantic shape این Contract تغییر نمی‌کند.
8. Isolated Runtime PASS فقط می‌تواند `APP_COMPATIBLE` را ثابت کند؛ وضعیت live browser جداگانه `CURRENT_RUNTIME_NOT_VERIFIED`, `RUNTIME_PREFLIGHT_PASS` یا `RUNTIME_BLOCKED` است.
9. موفقیت واقعی Import فقط با `IMPORT_VERIFIED` پس از transactional persistent commit + reload/reopen مجاز است. Label مبهم `IMPORT_READY` deprecated/ممنوع است.
10. Artifact نهایی Flashcards Pro باید همراه `BUILD-METADATA.json` با SHA-256 دقیق TSV تحویل شود تا Runtime بتواند provenance را Verify کند.
11. Mapping رسمی در `FLASHCARDS-PRO-UNIVERSAL-v2-DELIVERY-SPEC.md` تعریف می‌شود و Presentation/UI حق بازنویسی semantic source-of-truth را ندارد.
