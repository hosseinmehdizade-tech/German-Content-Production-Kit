# Architecture Decisions

## Why Dynamic Examples

تعداد Example policy یک Dataset است، نه shape یک Learning Unit. Array داینامیک اجازه می‌دهد targetهای ۲، ۴، ۵ یا ۸ بدون شکستن Schema استفاده شوند.

## Why paired DE → FA + EN translations

هر Example یک واحد معنایی است. Translation باید به همان جملهٔ آلمانی وصل باشد تا context، sense و identity در Practice از هم جدا نشوند.

## Why English gloss is separate

Gloss معادل کوتاه Learning Unit است؛ sentence translation یک proposition کامل را ترجمه می‌کند. ادغام آن‌ها هم داده و هم UI آینده را مبهم می‌کند.

## Why Stable Example IDs

Sentence Practice و SRS آینده باید جمله را پس از edit یا reorder همان واحد قبلی بدانند. بنابراین ID یک‌بار allocate می‌شود و از text/hash/order مستقل است.

## Why Clean-Slate

هیچ progress مهمی روی محتوای قبلی وجود ندارد و Datasetها از نو تولید می‌شوند. پس Canonical Architecture فقط نیازهای آینده را حمل می‌کند و هیچ Adapter یا preservation policy مربوط به دادهٔ قبلی ندارد.

## Why Unified Connections

NVV، collocation، pattern و fixed expression همگی رابطهٔ Unit با یک ترکیب آلمانی‌اند. `connections[]` آن‌ها را در یک collection عمومی با `kind` معنایی ذخیره می‌کند.

## Why semantic type is not a visual section

`kind=nvv` یا `kind=collocation` به معنی Box جدا نیست. Presentation می‌تواند همه را زیر «Verbindungen» نمایش دهد، filter کند یا grouping دیگری انتخاب کند.

## Why primary type differs from a connection

اگر عبارت خود هدف یادگیری باشد، `type=nomen_verb_verbindung` می‌گیرد. همان عبارت در Card یک Nomen می‌تواند فقط یک `connection` باشد. هویت اصلی و رابطهٔ جانبی یکی نیستند.

## Why Profile-driven example count

Profile سطح، زبان‌ها، Count و override هر Type را می‌داند. General Schema و Type Rule نباید Dataset policy را حدس بزنند.

در Profile واقعی Menschen A1 فعلاً تصمیم Dataset-level مستندی برای تفاوت count میان Typeها وجود ندارد؛ بنابراین همهٔ Typeها policy پیش‌فرض را می‌گیرند. قابلیت `by_type` در قرارداد Profile و Architecture Proof فعال باقی می‌ماند.

## Why Nomen number requirements are conditional

`plural_only` شکل عددی Nomen را صریح می‌کند: مقدار `false` وجود `singular` و مقدار `true` وجود `plural` را لازم می‌کند. `plural` برای Nomen عادی optional است تا واژه‌های بدون Plural مفید به placeholder یا صورت ساختگی نیاز نداشته باشند.

## Why phrase function is optional

همهٔ redemittelها، phraseها، idiomها، redewendungها، collocationها و Nomen-Verb-Verbindungها یک learner-facing `function` مستقل و طبیعی ندارند. Family عمومی آن را optional می‌گذارد؛ Dataset Profile تخصصی می‌تواند فقط در صورت وجود نیاز واقعی همان field تعریف‌شده را required کند.

## Why Type Rules are typed

نام field به‌تنهایی قرارداد نیست. هر field نوع، nullable بودن، enum، item type و object shape دارد؛ Validator value واقعی را بررسی می‌کند.

## Why grouped Type Rules

Typeهایی با shape واقعاً مشترک یک Rule family دارند. این composition از Schemaهای مصنوعی و duplicate جلوگیری می‌کند، در حالی که `applies_to` هویت هر Type را روشن نگه می‌دارد.

## Why Content generation stays outside Flashcards Pro

Translation، Example، morphology و correction تصمیم زبانی‌اند. Runtime فقط render/practice می‌کند تا محتوای ناقص را پنهانی اختراع یا تغییر ندهد.

## Why Presentation and Practice are separate

Content facts، Presentation layout و Practice behavior نرخ تغییر و مسئولیت متفاوت دارند. هیچ row count، geometry، reveal rule یا mode در Content Contract نیست.


## ADR — Approved Source Registry vs Run Verification
A Registry entry means the source is approved for specific roles/claims; it does not prove the source was accessed in a content-generation run. Provenance must record run-level verification separately. This prevents fabricated source evidence.

## ADR — Claim authority is role-scoped
A bilingual Persian resource can validate Persian lexical/translation claims but not German grammar/rection/morphology. German grammar claims require German authority roles. DE↔EN claims use dedicated bilingual/learner references.


## ADR — Semantic canonical is not the delivery transport

Canonical JSON optimizes for linguistic truth, stable identity, rich examples, translations and provenance. Flashcards Pro imports a Universal-v2 TSV envelope. Treating these as the same artifact creates false “final” claims. v3.1.3 therefore keeps Canonical JSON authoritative and adds a lossless delivery adapter.

## ADR — Lossless transport backstop

Current runtime presentation structures are simpler than the semantic model. Every Universal-v2 row therefore stores the complete original Learning Unit under `custom_fields.canonical_unit`. This allows current UI projection without deleting future-use data.

## ADR — Artifact compatibility and live runtime readiness are separate axes (v3.1.4)

The v3.1.3 model still allowed a clean/isolated Runtime PASS to be interpreted as “ready in the user's browser”. The 30-card pilot disproved that: the file parsed correctly while the live v343 persistence layer was recovery-locked and transactional commit rolled back.

Therefore:

- `APP_COMPATIBLE` is an artifact/version claim proved in an isolated writable Runtime matrix.
- `RUNTIME_PREFLIGHT_PASS` / `RUNTIME_BLOCKED` are live-session claims and require evidence from the actual browser/library.
- `IMPORT_VERIFIED` is a post-action claim requiring transactional persistent commit plus reload/reopen survival.
- `IMPORT_READY` is deprecated because it collapses these different truths into one ambiguous label.
- An existing non-empty library is mandatory in compatibility testing; clean-library-only tests are insufficient.
- A write-blocked/recovery state must fail closed without mutating the prior library. That behavior validates safety, not import success.


## ADR — v3.1.5: fixed alignment, profile-driven translation requirement
FA/EN translations are children of the same German Example when present. This association is invariant. Whether FA and/or EN are required is owned by the Dataset Profile, not the General Contract.

## ADR — v3.1.5: learner-facing Rektion needs dedicated Evidence
A non-empty `details.rection` is an educational claim and must be backed by an explicit verified `rection` provenance claim. A generic `grammar` claim cannot silently authorize it.
