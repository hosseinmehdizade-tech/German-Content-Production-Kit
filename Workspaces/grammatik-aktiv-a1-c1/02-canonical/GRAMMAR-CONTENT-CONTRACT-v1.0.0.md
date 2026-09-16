# Grammar Content Contract v1.0.0

Status: **DRAFT FOR PILOT VALIDATION**  
Dataset: `grammatik-aktiv-a1-c1`

This contract defines what “a complete grammar chapter” means before content is allowed into German Flashcards Pro.

## 1. Core model

The model deliberately separates **source chapters** from **canonical grammar concepts**.

### 1.1 Source chapter

A source chapter preserves the book’s own identity and order.

Required fields:

- `source_chapter_id` — stable ID, e.g. `ga-a1b1-ch001`
- `source_book_id`
- `chapter_number`
- `source_title_de`
- `source_subtitle_de` when present
- `source_section_de` / thematic group
- `printed_page_start`
- `printed_page_end` when determinable
- `cefr_labels[]` exactly as supported by the source
- `source_locators[]` including PDF page/printed page references
- `source_inventory_status`
- `concept_ids[]`

A chapter may map to one or more concepts. A concept may be taught in multiple chapters and levels.

### 1.2 Canonical grammar concept

Required fields:

- `concept_id` — stable semantic ID, e.g. `grammar.wechselpraepositionen`
- `canonical_title_de`
- `topic_family`
- `cefr_min`
- `cefr_max`
- `prerequisite_concept_ids[]`
- `related_concept_ids[]`
- `source_chapter_ids[]`
- `skill_tags[]`

Concept identity is semantic. It must not be duplicated merely because the same topic reappears at a higher CEFR level.

### 1.3 Learner lesson

A learner lesson is the structured teaching projection of one source chapter. Required fields:

- `lesson_id`
- `source_chapter_id`
- `concept_ids[]`
- `title_de`
- `cefr_labels[]`
- `short_explanation_de`
- `explanation_de`
- `explanation_fa`
- `learning_goals[]`
- `rules[]`
- `patterns[]`
- `examples[]`
- `exceptions[]`
- `common_errors[]`
- `exercise_ids[]`
- `speaking_tasks[]`
- `linked_object_ids[]`
- `prerequisite_lesson_ids[]`
- `provenance`
- `qa_status`

English support is optional for grammar explanations. German remains the primary learner-facing authority; Persian is the support language.

## 2. Rule object

Each rule is atomic and independently traceable.

Required:

- `rule_id`
- `statement_de`
- `explanation_fa`
- `scope`
- `positive_examples[]`
- `counterexamples[]` when pedagogically useful
- `exception_ids[]`
- `source_refs[]`
- `origin_type`

Allowed `origin_type`:

- `SOURCE_DERIVED` — directly supported by the supplied book, normalized into our wording/data model
- `SOURCE_ADAPTED` — pedagogically rephrased or reorganized from the supplied book
- `GENERATED` — newly created teaching content consistent with the concept
- `EXTERNALLY_VERIFIED` — separately checked against an external authority

Source-derived and generated material must never be silently mixed.

## 3. Pattern / table object

Tables from the books are represented structurally, not as screenshots.

Required:

- `pattern_id`
- `pattern_type`
- `title_de`
- `columns[]`
- `rows[]`
- `notes_de[]`
- `notes_fa[]`
- `source_refs[]`

Typical `pattern_type` values:

- `CONJUGATION`
- `WORD_ORDER`
- `CASE_MATRIX`
- `DECLENSION`
- `TENSE_FORMATION`
- `CONNECTOR_POSITION`
- `TRANSFORMATION`
- `COMPARISON`

## 4. Example object

Required:

- `example_id`
- `text_de`
- `translation_fa`
- `translation_en` optional
- `focus_spans[]` optional
- `concept_ids[]`
- `rule_ids[]`
- `source_refs[]`
- `origin_type`
- `naturalness_status`

Examples copied verbatim from the source are used only when needed and with source provenance. Production should prefer source-adapted or newly generated natural examples rather than reproducing long source exercise material.

## 5. Exception object

Required:

- `exception_id`
- `statement_de`
- `explanation_fa`
- `applies_to_rule_ids[]`
- `examples[]`
- `source_refs[]`

## 6. Common error object

Required:

- `error_id`
- `wrong_example_de`
- `correct_example_de`
- `explanation_de`
- `explanation_fa`
- `skill_tags[]`
- `source_refs[]`
- `origin_type`

Common errors may be source-derived or generated, but origin must be explicit.

## 7. Exercise contract

Every exercise requires:

- `exercise_id`
- `lesson_id`
- `exercise_type`
- `prompt_de`
- `answer_spec`
- `feedback_rules[]`
- `skill_tags[]`
- `target_object_ids[]`
- `difficulty`
- `source_refs[]`
- `origin_type`

### 7.1 Runtime-compatible exercise types already supported by GFP v411 R43

- `MULTIPLE_CHOICE`
- `TRUE_FALSE`
- `FILL_GAP`
- `SHORT_ANSWER`

### 7.2 Canonical exercise types to support in the production master

The canonical layer may additionally contain:

- `ORDER_SENTENCE`
- `TRANSFORM_SENTENCE`
- `ERROR_CORRECTION`
- `CASE_SELECTION`
- `ENDING_SELECTION`
- `CONNECTOR_SELECTION`
- `FORM_BUILDING`
- `MATCHING`
- `FREE_PRODUCTION`
- `SPEAKING_PROMPT`

Unsupported canonical types must never be silently dropped. Stage 5 must either project them losslessly into supported runtime interactions or mark runtime capability as missing and block final release.

## 8. Speaking task contract

Required:

- `speaking_task_id`
- `lesson_id`
- `instruction_de`
- `prompt_items[]`
- `target_structures[]`
- `self_check[]`
- `source_refs[]`
- `origin_type`

Audio files are not required for the canonical grammar lesson to be complete. If audio is later available, it is linked as optional media with provenance.

## 9. Provenance contract

Every lesson, rule, pattern, example, exception, error and exercise must be traceable.

Minimum source reference:

```json
{
  "source_id": "grammatik-aktiv-b2-c1",
  "pdf_page": 62,
  "printed_page": 60,
  "chapter_number": 20,
  "locator_note": "Wechselpräpositionen"
}
```

Generated content uses `origin_type: GENERATED` and still records the source concept/chapter that motivated it.

## 10. Chapter completeness gate

A source chapter may be marked `CONTENT_COMPLETE` only when all applicable checks pass:

1. Stable source chapter identity exists.
2. Chapter title/order/page locator is verified.
3. All major rules/contrasts presented by the source chapter are represented.
4. Tables/patterns that carry unique instructional information are structurally captured.
5. Exceptions/notes that materially change learner behavior are represented.
6. At least three natural learner examples exist for each major rule unless the rule does not justify that count.
7. Common-error coverage exists where pedagogically meaningful.
8. Exercises cover recognition **and** production/transformation where the concept requires it.
9. Every exercise has an answer specification and feedback path.
10. German learner text passes linguistic QA.
11. Persian explanation is present and semantically aligned.
12. Provenance is complete.
13. Cross-links to prerequisite/related concepts are valid.
14. No duplicate semantic concept was created solely because of a new book chapter.
15. Runtime projection status is known; unsupported features are explicitly reported, not dropped.

## 11. Pilot acceptance gate

Before mass-producing all 168 chapters, validate this contract against six deliberately different chapter types:

- simple A1 morphology/conjugation
- A2 case/preposition topic
- B1 clause/relative-clause topic
- B2 word-order topic
- B2/C1 passive/tense-complexity topic
- C1 transformation/nominalization topic

The pilot is a **contract test**, not the final content scope. Once the pilot shows the contract can represent all six without loss or awkward exceptions, the remaining chapter inventory is produced outside the app.

## 12. Runtime projection contract

The production master is richer than the current v411 grammar UI. Stage 5 creates a runtime pack compatible with the intended Flashcards Pro version.

Current observed v411 grammar unit fields include:

- `grammar_unit_id`
- `title`
- `cefr`
- `short_explanation_de`
- `explanation_de`
- `common_errors[]`
- `example_ids[]`
- `exercise_ids[]`
- `linked_object_ids[]`
- `prerequisite_ids[]`
- `skill_tags[]`
- `provenance`

Current observed exercise fields include:

- `exercise_id`
- `exercise_type`
- `prompt_de`
- `answer_spec`
- `feedback_rules[]`
- `skill_tags[]`
- `target_object_ids[]`
- `provenance`

The canonical contract must not be weakened to those fields. Instead a versioned adapter projects canonical grammar content into the exact target runtime. New UI/runtime fields are added only after content production proves they are needed.

## 13. Release rule

The final user delivery is **one structured German Flashcards Pro release ZIP** containing app, content, source lineage, tests, reports, tools and docs in their proper directories. Source-production history remains Git-backed; the final ZIP is not the sole source of truth.
