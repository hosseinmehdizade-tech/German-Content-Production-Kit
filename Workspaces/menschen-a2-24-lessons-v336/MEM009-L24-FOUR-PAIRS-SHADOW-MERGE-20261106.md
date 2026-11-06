# A2 L24: four one-card/multiple-meaning shadow candidates

**Status:** `SHADOW_CONTENT_COMPOSITES_VERIFIED__NONIMPORT__NO_FSRS_MIGRATION`  
**User decision:** `PROJECT-MEMORY.json#MEM-009-MULTI-MEANING-ONE-CARD` + `Prompt/MEM-009-ONE-CARD-MULTI-MEANING-EXAMPLES-CLARIFICATION-20261106.md`.  
**Scope:** A2 L24 four known exact noun-front duplicates only. **Do not change** current content, cards, source/LOCKED, user-owned SRS/FSRS or app CURRENT.

## Exact current parent (re-read from Library)

- Library: `/Flasch kart/German-Content-Production-Kit/Content/Menschen-A2/Current/Menschen-A2-R21-R2-R1-1778-Karten-CONTENT-ONLY-KORRIGIERTE-LINKS-UND-ANLEITUNG-20261106.zip`
- Archive SHA-256: `774b8b620d57a0ad64b20490f8b3fa6aa4f015f1edf3e08e31a78c040222d2f5`; ZIP CRC PASS.
- Current TSV `01-Content/A2-C3-1778-cards.tsv` SHA-256: `ca913c691889466dbdd807e8b8fa9b82dd5b914f73bde00c076d2ece21cf2f4c`. **1,778 cards / 1,778 unique stable IDs**.
- `01-Content/A2-C3-1829-source-output-map.tsv`: **1,829 current course-membership edges**. Current direct-import authorization **FALSE**; native app Stage6 **NOT RUN**. Source owner workstream LATEST remains unchanged.

## One persistent SHADOW proposal (NOT current)

- Library: `/Flasch kart/German-Content-Production-Kit/Content/Menschen-A2/Reports/A2-L24-MEM009-4-COMPOSITE-CARDS-SHADOW-NONIMPORT-20261106.json`
- Library returned file_id: `file_00000000491c81f4a1b635fcfecdeb96`; library_file_id: `libfile_ad7ca4fa55e88191a5adde49696cef16`.
- Exact 52,177-byte **JSON** file SHA-256: `778eb4fa750727bd5498be1016f940354bc66718f57ec51ae7c56c33285ba430`. Read back from Library and byte-for-byte compared successfully. It is intentionally **not the Universal v2 cards format**, not a ZIP and is not importable.

| One future lexical card | Source IDs, still intact | Accepted meaning pair | Content represented in SHADOW |
|---|---|---|---|
| die Erinnerung | `ma2m-lu-1685` / `1686` | memory / memento | 2 sense records, 8 DE/FA/EN examples, 2 sense-specific combinations |
| das Haus | `ma2m-lu-1706` / `1707` | building / family-dynasty | 2 senses, 8 examples, 2 combinations |
| der Schluss | `ma2m-lu-1731` / `1732` | ending / inference | 2 senses, 8 examples, 2 combinations |
| das Blatt | `ma2m-lu-1769` / `1770` | leaf / sheet of paper | 2 senses, 8 examples, 2 combinations |

**Verified structural conservation of represented lexical content:** all **8 distinct accepted Persian meaning glosses**, 8 source DE definitions / EN glosses, 32 original example IDs and DE+FA+EN example sets (4 per original sense record), all 8 original bilingual Kombinationen and their stable item IDs, the matched noun morphology, audio references and two original source identities for each group are included or exact source-pinned. Select one *existing* example per meaning (8 of 32) as a **presentation preference only**; all remaining 24 examples are retained in the SHADOW. No forced one-example-per-sense quota.

**Explicit dependencies:** zero occurrences of the eight source card IDs inside other cards' `examples/related/opposites/details/custom_fields/notes` in this exact current TSV. All eight IDs **do** occur independently in the L24 read-only lesson roster and source-output membership map; a real successor must rebuild these plus canonical units/manifests/checksums and independent graph parity. Same-front candidate discovery is NOT an automatic merge. `ihr` and `Ihr` are intentionally distinct.

**Only a future authorized projection:** if the four 2-to-1 groups were actually consolidated, the unique A2 card count would become **1,774**, and deduplicated L24 membership edges would bring **1,829 → 1,825**. These are projected counts, **not an accomplished edit**.

## Exact unresolved safety decision — cannot silently choose an SRS identity

Each group still has **two separate existing card IDs**. A single final learner card requires deciding what to do with **both** independent review histories and restoring all original user data. Do not arbitrarily keep the first ID, mint a replacement, delete the second, or copy a fabricated review timestamp. The app's historical Phase37 dynamic-content contract states that card IDs cannot be renamed in place and that review state is preserved on replace only when semantic identity remains the same; cross-card FSRS-history consolidation is **not established**. The SHADOW therefore has `planned_final_card_id=null`, `planned_retired_card_id=null` and `srs_fsrs_identity_migration_proven=false`.

**Future owner-specific acceptance boundary** (not performed): (1) verify newer CURRENT A2 and actual user/imported-card identity before touching any mutable data; (2) independently approve exact DE/FA/EN semantic grouping and no-loss full canonical graph/metadata projection; (3) approve/prove an app-owner migration policy with verified backup, two-ID lineage, repeatable rollback and *real* native browser/IndexedDB/FSRS regression; (4) create one versioned 1,774-card native successor with updated membership map and full source/Stage5 parity; (5) perform Stage6 and Stage7 gates before final import/publication. If no safe SRS migration exists, **HOLD** official merging; never sacrifice learning history for a lower card count.

**Completion of this milestone:** Four **nonimport shadow composites** created and persisted with a byte-exact Library readback and source-bound structural checks. **Not** a Stage4 linguistic sign-off, real governed Stage5 importable output, native app Stage6, Stage7, or universal MEM-009 rollout. No new content ZIP, duplicate checkpoint or historical book re-audit created.

**2026-11-07 app-owner blocker handoff:** [German-Flashcards-Pro issue #38](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/issues/38) is OPEN. Independent exact-parent recheck again verified ZIP/TSV/canonical SHA-256, ZIP CRC, 1,778/1,778 current cards, 1,829 membership edges, all eight IDs in source-map, and 32/32 examples plus 8/8 combinations, with **zero changed-source discrepancies**. Real user review state is **NOT AVAILABLE** here; no safe two-distinct-FSRS-histories-to-one-active-schedule proof. This is an app CURRENT v505-R141 identity/persistence-owner gate, NOT another editorial/source review queue. **PHYSICAL_MERGE_AND_IMPORT_HOLD**; keep immutable original, Library SHADOW and unchanged A2 LATEST. No new ZIP, app CURRENT/SRS mutation or release promotion.
