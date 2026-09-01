# Start Prompt — Use German Content Architecture v3.1.5 with Master Prompt v3.1.9

این فایل را همراه Package معماری `German-Language-Content-Architecture-v3.1.5` و Source Dataset به مدل بده.

## دستور

از `CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md` به‌عنوان Master Prompt استفاده کن.

Architecture v3.1.5 را بازطراحی نکن.

برای Run فعلی Configuration را Fail-Closed resolve کن:
- required input را حدس نزن؛
- conflict را silently resolve نکن؛
- `architecture_package_version` را خودکار `contract_version` فرض نکن؛
- Prompt/Validator/Architecture-package version را compatibility gate نکن؛
- اگر Configuration کامل/بدون ابهام نیست، `CONFIGURATION_BLOCKED` و توقف Production.

## Critical invariants

1. **German Example Anchor** — هر FA/EN ترجمهٔ طبیعی همان DE و زیر همان Stable Example ID باشد.
2. **Gloss ≠ Translation** — English gloss کلمه با English sentence translation یکی نیست.
3. **Dynamic Examples** — count فقط از Dataset Profile؛ schema همچنان `examples[]`.
4. **Stable Identity** — Unit/Sense/Example ID با edit/reorder عوض نشود؛ suffix عددی Example ID، allocation sequence است نه order.
5. **Deterministic Migration** — split/merge/retire/reactivate/count reduction/reorder فقط با authorization و `MIGRATION_PLAN` کامل؛ Plan و tombstone/archiveها workflow artifact بیرون Canonical JSON هستند، مگر Contract صریحاً storage دیگری تعریف کند. در غیر این صورت `REVIEW_REQUIRED` و no mutation.
6. **Count Increase** — Existing Example objects/IDs حفظ؛ فقط delta append؛ allocator state ثبت.
7. **Count Decrease** — بدون resolved enforcement + ordered retain/deactivate/order mapping + full retirement archive هیچ delete/retire؛ در Contract `3.1.3` IDهای حذف‌شده در `metadata.retired_example_ids` ثبت شوند و objectهای کامل در Audit archive بمانند.
8. **Unknown Field Safety** — ابتدا field را با Schema resolved طبقه‌بندی کن. در closed Schemaهای Contract `3.1.3`، unknown field canonical معتبر نیست: source bytes/value را در Audit ledger حفظ کن، Canonical mutation/finality را Fail-Closed متوقف کن و field را داخل Canonical اختراع نکن. Preservation درجا فقط در envelopeای مجاز است که Schema/Protocol صریحاً extension را اجازه دهد؛ unknown required semantics همیشه Fail-Closed است.
9. **Example Order** — در Architecture v3.1.5، `order` همیشه integer/unique/contiguous از 1 است. Reorder مجاز ID را عوض نمی‌کند، ولی old→new order mapping باید در Plan ثبت شود؛ Delivery/roundtrip باید `(example_id, order)` Canonical پس از تغییر را عیناً حفظ کند.
10. **Derived Units** — فقط با authorization صریح Dataset/Profile/Source.
11. **Claim-Level Evidence** — `details.rection` و learner-facing grammar facts evidence مخصوص همان claim داشته باشند.
12. **Linguistic Gate** — `CONTENT_VALIDATED` فقط با `linguistic_status=PASS` + canonical/claim gates.
13. **Capability Derivation** — required/optional capabilities فقط از Semantic Contract + features واقعی Dataset؛ Target فقط negotiation می‌کند.
14. **Compatible Base Contract** — فقط declaration contract-owned + validator-verified؛ Producer assertion یا semver guess کافی نیست.
15. **Target-Owned Delivery** — با Architecture v3.1.5، مسیر رسمی Flashcards Pro برابر Canonical JSON → Universal-v2 TSV + BUILD-METADATA است. Native JSON یا Unified Import ZIP را فقط وقتی primary کن که یک Delivery Spec جدیدترِ target-owned صریحاً آن را مجاز کند. هر Import ZIP مجاز باید دقیقاً یک primary importable dataset داشته باشد.
16. **Sidecar Contract** — `BUILD-METADATA.json` باید field contract واقعی Target را رعایت کند. برای Delivery Spec معماری 3.1.5 همان هشت field حداقلی Spec authoritative است و `prompt_version="v3.1.9"` provenance Producer جاری را ثبت می‌کند؛ metadata اضافی در Audit/RUN-METADATA بماند مگر Sidecar اجازه دهد.
17. **TSV** — فقط compatibility/interoperability و هرگز Canonical نیست؛ projection غیر-isomorphic باید machine-readable `MAPPING-LIMITATIONS` داشته باشد، حتی اگر `canonical_unit` آن را lossless کند.
18. **Post-Package** — Artifact واقعی را Extract/reopen کن؛ inventory + hash + validator متناسب با نوع primary + canonical-source binding + `(example_id,order)` + schema-permitted extension parity را دوباره اجرا کن.
19. **Evidence Binding** — validator/audit report فقط وقتی gate را satisfy می‌کند که `input_sha256` با artifact واقعی همان Run برابر باشد.
20. **Runtime Status** — isolated PASS را current-runtime PASS جا نزن.
21. **Live Import Advice** — بدون actual-user-runtime preflight برای همان artifact hash/import mode، کاربر را به Import فوری هدایت نکن و `CURRENT_RUNTIME_NOT_VERIFIED` گزارش کن.
22. **IMPORT_VERIFIED** — فقط actual runtime + same artifact/mode + persistent commit + reload parity.
23. **Status Vector** — structure/linguistic/transport/isolated-runtime/actual-runtime را جدا گزارش کن.
24. **No mass regeneration** — Keep good / Fix bad / Fill missing.
25. **Dataset Pilot** — فقط Typeهای مجاز همان Dataset؛ multi-Type فقط regression pilot عمومی.

اگر سند قدیمی `5 DE + 1 independent English example` را دیدی، برای Canonical v3.1.5 آن دستور superseded است.

کار را agentic تا پایان مراحل قابل اجرا ادامه بده؛ QA را حذف نکن، limitation را پنهان نکن و هیچ PASS را بدون evidence واقعی claim نکن.

اگر Run به `CONTENT_VALIDATED` رسید و Delivery خواسته شد، خروجی روزمرهٔ نهایی را دقیقاً با Format تعریف‌شدهٔ Delivery Spec بساز؛ برای Architecture v3.1.5 این خروجی Universal-v2 TSV + BUILD-METADATA است. فقط در Targetی که Unified ZIP را صریحاً تعریف کرده یک ZIP قابل Drop/Auto-Detect بساز؛ Audit evidence را جدا نگه دار تا Import Artifact ambiguous نشود.
