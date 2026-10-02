# DK Visual Dictionary → Unified Vocabulary Integration Pre-Design Audit

Status: **PASS_WITH_REQUIRED_ARCHITECTURE_DECISIONS**  
Date: 2026-10-02  
App CURRENT inspected: **v454-R88**  
Content framework: **v3.3.6 / gfp-german-language-content@3.1.3**

## Decision

Do **not** expand the legacy Bildkarten-only content model before the unified-vocabulary integration contract is fixed.

The target architecture is:

```text
Source Book Occurrence
        ↓
Canonical Lexical Target (Sense / Expression)
        ├── Source Membership(s): book / section / lesson / page
        ├── Semantic data: morphology / examples / relations / provenance
        └── Media Link(s) → Media Asset Registry
                         ↓
                 normal de-vocabulary projection
                         ↓
        Wortdetails / Wortnetz / Search / Practice / Review
                         ↓
               optional Visual Practice mode
```

## Current app capabilities that must be preserved

Current lexical runtime already resolves dynamic ordinary vocabulary through stable semantic target IDs and supports:
- Wortdetails: Übersicht, Beispiele, Wortnetz, Grammatik, Quellen
- explicit sense/expression disambiguation
- contextual word navigation from Wortschatz / Grammatik / Lesen
- dynamic lexical relations and reverse links
- relation families including COMPONENT, WORD_FAMILY, NVV, COLLOCATION, REKTION, SYNONYM, ANTONYM and RELATED
- shared example/search/source projection
- ordinary vocabulary projection through `de-vocabulary` + `gfp-vocabulary-neutral@1`
- rich authority with compact runtime projection and point hydration

Therefore DK entries should become ordinary lexical targets/cards, not a second semantic island.

## Required semantic identity rule

A visual item is not identified by spelling alone.

Correct identity:
```text
target_id = one lexical Sense or Expression
```

Examples:
- `die Bank` financial institution ≠ `die Bank` bench.
- A source occurrence in DK and one in Menschen may reuse the same target_id only when semantic identity is explicitly verified.
- If the same target occurs in multiple books/lessons, memberships multiply; the lexical target does not.

## Required data separation

### 1. Canonical lexical target
Owned by the canonical content pipeline. Holds linguistic truth: headword, POS/type, meaning, morphology, examples, relations, provenance.

### 2. Source membership / occurrence
Book-specific structure:
- source_id
- book_id
- section_id
- lesson_id
- page / locator
- source-visible German
- source English gloss
- source order

A lexical target may have many memberships.

### 3. Media asset registry
Must be separate from the current canonical LearningUnit object because the v3.1.3 schema is closed (`additionalProperties:false`) and has no media field.

Suggested minimum media record:
- asset_id
- media_type
- master_path / runtime_path
- mime / dimensions / hash
- visual_class (object, part, action, scene, property, diagram)
- rights_status
- generation/source provenance
- QA status

### 4. Target-media link
Links image semantics to one target/sense:
- target_id
- asset_id
- role (primary_visual, alternate_visual, contextual_visual, diagram)
- membership_id optional
- applicability / sense note
- primary flag

This prevents a picture from being incorrectly attached to every homographic sense.

## Runtime projection rule

New DK vocabulary should project as ordinary `de-vocabulary` with the current neutral presentation contract.

Important bridge fields already used by the app:
- `vnext_target_id`
- `vnext_target_type`
- `vnext_definition_de`
- `vnext_translation_fa`
- `vnext_translation_en`
- `vnext_structure`
- `vnext_relations`
- `vnext_source_refs`
- `canonical_unit`
- source/course membership metadata

The image should be referenced by media ID/ref; image bytes should not become duplicated semantic-card payload.

## Wortfamilie / Wortnetz compatibility

The current app lexical graph can render and reverse-index `WORD_FAMILY`, `NVV`, `COLLOCATION`, `REKTION`, `SYNONYM`, `ANTONYM`, `RELATED` and `COMPONENT` relation groups from projected `vnext_relations` / structure.

However, the canonical v3.1.3 base `connections.kind` enum is narrower and does not directly contain every runtime graph relation type, including WORD_FAMILY.

Therefore:
- do not inject unsupported values into canonical `connections.kind`;
- define/evolve a verified semantic-relation overlay or future contract revision;
- Stage 5 projection must preserve relation semantics losslessly into runtime `vnext_relations`.

This is a real compatibility item to close before bulk DK enrichment.

## Practice / SRS boundary

The visual mode must reuse the same lexical/card identity.

Default safe behavior for the first unified implementation:
- Cards/Audio/Writing/Quick continue using existing owners.
- Visual practice is an additional presentation/practice mode over the same target/card.
- Visual practice must **not silently create a second FSRS schedule**.
- Visual practice must **not silently mutate existing recognition/production/listening/spelling evidence** until an explicit evidence policy defines whether visual recall maps to an existing skill or a new skill.

A later explicit decision may add a `visual_recognition` skill signal, but that is an adaptive/practice contract change and needs dedicated tests.

## Review / Fehler / adaptive compatibility

Because visual items reuse the existing lexical/card identity:
- favorites/starred state can remain attached to the existing card;
- review state stays single-owner;
- Fehler/targeted-review references can continue to identify the same card/target;
- future adaptive recommendations can reference the same target without creating a visual duplicate.

No second scheduler, second mastery store or second semantic resolver should be introduced.

## Library / Book hierarchy

Book structure is a membership/navigation layer, not lexical identity.

Recommended hierarchy:
```text
Bibliothek
  → Buch
    → Abschnitt
      → Lektion
        → target memberships
```

The same target may appear in multiple lessons/books without cloning the lexical target.

## Source-image boundary

Reference crops from the supplied DK PDF may be used as source-analysis assets inside the private production workstream.

Redistributable runtime media must carry an explicit rights status. Source-reference imagery and release-ready media are separate asset states.

## Pre-production gates

Before bulk image generation/extraction:
1. inventory all source occurrences and assign stable occurrence IDs;
2. resolve target identity/sense before attaching final media;
3. define media registry + target-media-link schemas;
4. define relation overlay/bridge for full Wortnetz/Wortfamilie parity;
5. define source/book/section/lesson membership schema;
6. define visual-practice scheduling/evidence semantics;
7. run a mixed pilot across easy and hard visual classes;
8. only then freeze the Visual Source standard and scale production.

## Outcome

The project should treat "Bildkarten" as a **visual capability of normal vocabulary**, not a separate vocabulary authority.

Legacy Bildkarten storage/runtime can remain temporarily for compatibility, but no new bulk DK authority should be built on top of it. Migration/retirement must be a later bounded runtime milestone with explicit UI approval.
