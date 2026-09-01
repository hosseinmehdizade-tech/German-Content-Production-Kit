# Validation Rules

## Operational validator

`validate_content.py` بدون dependency خارجی این موارد را بررسی می‌کند:

- Learning Unit/Card ID، type، headword و Profile field requirements
- resolve شدن exact یا Generic Type Rule
- value type واقعی تمام `core`/`details` fieldها
- nullable، enum، length/range، array items/uniqueness و object properties
- conditional Type requirements و Profile-added typed requirements
- ساختار و kind مجاز `connections[]` و sense reference آن
- Example ID، source language، text، order، duplicate ID و retired-ID reuse
- required translation languages از Profile
- valid language-tag shape و duplicate translation language
- Sense Registry و `sense_id`
- default Example count و per-Type overlay
- provenance source count/kind/verified policy
- previous snapshot identity برای edit/reorder

## Schema validator

`meta_validate_schemas.py` با `jsonschema` Draft 2020-12:

1. هر چهار Schema را با `Draft202012Validator.check_schema` Meta-Validate می‌کند.
2. تمام Profileها را با Profile Schema Validate می‌کند.
3. تمام Type Ruleها را با Type Rule Schema Validate می‌کند.
4. Sample را با Learning Unit Schema و registry حاوی Connection Schema Validate می‌کند.

## Count resolution

```text
effective = copy(profile.examples.default)
effective.update(profile.examples.by_type.get(unit.type, {}))
```

General Learning Unit Schema روی `examples` هیچ min/max ندارد.

## Claim boundary

Structural/typed PASS صحت type، identity، policy و references را ثابت می‌کند؛ German naturalness، translation fidelity، CEFR و source truth نیاز به audit جدا دارند. Status اجرا‌نشده `NOT_RUN` است.

## Flashcards Pro delivery validation (semantic 3.1.3 / prompt gate v3.1.4)

`build_flashcards_pro_universal_v2.py` Canonical Dataset را به Universal-v2 TSV losslessly project می‌کند و `BUILD-METADATA.json` با SHA-256 دقیق فایل می‌سازد.

`validate_flashcards_pro_universal_v2.py` این موارد را Gate می‌کند:

- exact 23-column Universal-v2 base envelope
- required IDs/front/back/card type
- JSON cell integrity
- row-count parity
- exact `custom_fields.canonical_unit` deep-copy parity
- headword/Persian meaning/type/definition/English gloss parity
- semantic/runtime contract markers
- BUILD-METADATA filename + SHA-256 parity

این Validator فقط `TRANSPORT_VALIDATED` را ثابت می‌کند.

`validate_runtime_import_evidence.py` claimهای بعدی را Gate می‌کند:

- `APP_COMPATIBLE`: نیازمند scenario موفق `ready-existing-library`، `write-blocked-fail-closed` و `reload-durability` است.
- isolated-runtime حق claim `RUNTIME_PREFLIGHT_PASS`, `RUNTIME_BLOCKED` یا `IMPORT_VERIFIED` ندارد.
- `RUNTIME_PREFLIGHT_PASS`: فقط actual-user-runtime با `READY`, `writes_blocked=false`, `can_write=true`, writer authority و بدون unresolved recovery.
- `RUNTIME_BLOCKED`: باید حداقل یک blocking signal واقعی داشته باشد.
- `IMPORT_VERIFIED`: نیازمند `APP_COMPATIBLE` + persistent verified commit + exact expected post-count + reload persistence است.

`IMPORT_READY` از v3.1.4 deprecated و ممنوع است.


## v3.1.5 claim-coverage gate
- `details.rection` غیرخالی در Profileهای نیازمند Source Verification بدون Claim صریح verified `rection` از یک German authority با `SOURCE_FIELD_CLAIM_MIN` رد می‌شود.
- `grammar` به‌تنهایی substitute برای `rection` نیست.
- Translation requiredness همچنان فقط Profile-driven است؛ alignment DE↔FA/EN invariant جداگانه است.
