# Flashcards Pro Universal v2 Delivery Spec

Delivery profile: `flashcards-pro-universal-v2@1.0.1`

Semantic source contract: `gfp-german-language-content@3.1.3`

Runtime content contract: `gfp-german-learning-content@1.0.0`

Transport contract: `gfp-universal-card@2.0` / schema profile `universal-v2`

Prompt/runtime-gate release: `v3.1.4` (semantic source contract remains `3.1.3`; transport field mapping is unchanged).

## Purpose

این Spec فقط Adapter/Transport را تعریف می‌کند. Semantic Canonical JSON منبع حقیقت است و TSV یک projection سازگار با Flashcards Pro است. Adapter حق حذف fact، merge کردن sense یا تغییر نوع semantic Connection را ندارد.

## Mandatory base header

اولین 23 ستون باید دقیقاً این‌ها باشند:

```text
id	card_type	domain	category	source	level	lesson	deck	front	back	front_label	back_label	front_lang	back_lang	typing_target	examples	related	opposites	details	custom_fields	tags	notes	order
```

## Base mapping

| Universal field | Canonical source / rule |
|---|---|
| `id` | `unit.id` |
| `card_type` | default `de-vocabulary`; use another existing Universal type only if semantically exact |
| `domain` | `German` |
| `category` | canonical `unit.type` or a deterministic display label derived from it |
| `source` | `profile.dataset.title`, falling back to `profile.dataset.id` |
| `level` | `profile.cefr` when present |
| `lesson` | explicit source/dataset metadata only; otherwise empty |
| `deck` | explicit source/dataset metadata only; otherwise empty |
| `front` | `unit.headword` |
| `back` | for German→Persian production profile: `unit.persian_meaning` |
| `front_label` | `Deutsch` |
| `back_label` | `فارسی` for `fa-IR` target |
| `front_lang` | `profile.languages.source.lang` |
| `back_lang` | selected target translation language, normally `fa-IR` |
| `typing_target` | `front-core` unless target type requires another Universal target |
| `examples` | runtime presentation projection; see below |
| `related` | synonyms/semantically related items only when Canonical data declares them |
| `opposites` | antonyms only when Canonical data declares them |
| `details` | display sections derived losslessly from typed core/details/connections |
| `custom_fields` | full semantic bridge and canonical payload |
| `tags` | `unit.metadata.tags`, semicolon-separated |
| `notes` | review/import note only; never fabricate linguistic content |
| `order` | `unit.metadata.unit_order` when present |

## Entry type mapping

Canonical type is never discarded. `custom_fields.canonical_entry_type` always stores it. `custom_fields.entry_type` uses the spelling best understood by current Flashcards Pro presentation logic:

```text
verb -> verb
nomen -> noun
adjektiv -> adjective
adverb -> adverb
praeposition -> preposition
konnektor | konjunktion -> conjunction
pronomen -> pronoun
artikelwort -> artikelwort
partikel -> particle
interjektion -> interjection
redemittel | phrase -> phrase
idiom | redewendung -> idiom
kollokation -> collocation
nomen_verb_verbindung -> nvv
satzmuster -> sentence_pattern
satz -> sentence
frage_antwort -> qa
grammatische_struktur -> grammar_structure
numeral -> numeral
abkuerzung -> abbreviation
generic -> custom
```

## `custom_fields` mandatory bridge

Every row MUST include at least:

```json
{
  "entry_type": "verb",
  "canonical_entry_type": "verb",
  "learning_unit_id": "MEN-A1-00001",
  "semantic_identity": "MEN-A1-00001",
  "german_learning_contract": "gfp-german-learning-content@1.0.0",
  "semantic_contract": "gfp-german-language-content@3.1.3",
  "source_profile_id": "menschen-a1@2.1.0",
  "german_definition": "...",
  "english": "...",
  "canonical_unit": {}
}
```

`canonical_unit` is a complete deep copy of the Learning Unit. This is the lossless backstop and parity source.

## Verb presentation bridge

When available, verb values are also copied into names currently consumed by Flashcards Pro:

- `present` ← `core.present_3sg`
- `preterite` ← `core.preterite_3sg`
- `perfect` ← `core.perfect`
- `participle_ii` ← `core.participle_ii`
- `auxiliary` ← `core.auxiliary`
- `reflexive` / `is_reflexive` ← `core.reflexive`
- `is_separable` ← true only when canonical separability is `separable`
- `rection` ← readable joined projection of canonical `details.rection`

These are presentation aliases; `canonical_unit` remains authoritative.

## Examples

Canonical form remains:

```json
{
  "id":"...-ex-001",
  "lang":"de-DE",
  "text":"...",
  "order":1,
  "translations":[...]
}
```

Runtime `examples` is a JSON array of objects accepted by Universal v2. The default projection emits every canonical German source example and, when an English translation exists, an English presentation entry after the German entries. Persian sentence translations are preserved in `custom_fields.canonical_unit` and are not forced into the current visual Example list.

No canonical Example or translation may be lost because the Runtime projection is simpler.

## Connections

`connections[]` is authoritative. For display, Adapter groups items into `details` sections such as `NVV`, `Kollokationen`, `Muster` or `Verbindungen`. The `kind` value remains intact in `custom_fields.canonical_unit`; NVV and Collocation must never become the same semantic value.

## Provenance sidecar

Final delivery should include `BUILD-METADATA.json` with at least:

```json
{
  "artifact_type":"gfp-data-build-metadata",
  "metadata_version":"1.0",
  "prompt_version":"v3.1.5",
  "validator_version":"v3.1.5",
  "data_build_id":"...",
  "schema_profile":"universal-v2",
  "data_file":"...tsv",
  "data_sha256":"<64 hex>"
}
```

The SHA-256 must be computed from the exact TSV bytes delivered to the user.

## Finality rule — v3.1.5

A structurally valid TSV is only `TRANSPORT_VALIDATED`.

A successful import/roundtrip in an isolated writable copy of the target app may establish `APP_COMPATIBLE`, but it does **not** establish that the user's current browser session is writable. A live runtime can still be blocked by recovery, degraded read-only mode, writer ownership, stale-writer/CAS protection, pending commits, or persistence failure.

Before telling the user to import **now**, the current runtime must separately pass the live preflight defined by Master Prompt v3.1.4 and earn `RUNTIME_PREFLIGHT_PASS`. If the live runtime is write-blocked, use `RUNTIME_BLOCKED` without blaming the TSV.

After a real current-runtime import, only a verified transactional commit that survives reload/reopen may be called `IMPORT_VERIFIED`. The ambiguous label `IMPORT_READY` is deprecated and forbidden.

Any claim beyond `TRANSPORT_VALIDATED` requires machine-readable `RUNTIME-IMPORT-EVIDENCE.json` conforming to `02-SCHEMAS/RUNTIME-IMPORT-EVIDENCE-SCHEMA.json`.
