# Menschen Memrise Course Source Contract v1.0.0

## Source columns
The source export columns are `Learnable`, `Definition`, `Audio`, `Beispiel`, `Level tags`, `Progress`, `Learnable meta`.

## Authority and routing
- `Learnable`: authoritative source-visible lexical/course occurrence; preserve verbatim in Stage 1 inventory. Canonicalization may normalize/split only with an explicit decision.
- `Definition`: source-provided Persian seed meaning. Preserve as source evidence, then review against the selected German sense before accepting final `translations.fa`.
- `Beispiel`: source example seed. Preserve in source inventory. It may be used learner-facing only if rights/provenance and linguistic/sense QA allow it; otherwise generate an independent example and retain source lineage.
- `Level tags`: authoritative membership/order metadata for course level/lesson/section. Never infer a different lesson from dictionaries.
- `Audio`: source media reference(s). Preserve all `[sound:...]` values in source order and validate against the supplied archive when available.
- `Progress`: user/SRS runtime state. **Forbidden** from canonical content, evidence claims, projected cards and releases.
- `Learnable meta`: `learnable_id` may be preserved as a source record identity/locator. Distractor choices, reverse choices and study-state fields are **not lexical evidence** and are not imported as learner content.

## Source occurrence vs canonical identity
Each CSV row is a source occurrence. Repeated rows/words across lessons remain separate source memberships but may map to one canonical Sense/Expression when semantic identity truly matches. Never delete the later lesson membership merely because the lexical target already exists.

Canonical targets may therefore carry `course_memberships[]`, each containing at least:
`source_record_id`, `course`, `cefr`, `lesson_id`, `lesson_number`, `lesson_title`, `section`, `source_row_ordinal`, `source_tag`.

One canonical object may have several memberships. Canonical IDs must not be derived from mutable headword text.

## Supplemental source sections
Tags such as `Verben mit Präpositionen`, `Adjektiv`, or thematic supplements are preserved as explicit sections. Do not silently relabel them as numbered Menschen lessons.

## Exact learner content
For Menschen A1/A2/B1 Memrise profiles, every final Sense/Expression requires `definition_de`, Persian meaning, English gloss, and exactly four German examples. Each example requires an independent Persian and English sentence translation.

Synonyms, antonyms, collocations, Rektion, NVV and word-family relations are included only when sense-aligned evidence supports them; absence is reported as coverage, not filled by invention.
