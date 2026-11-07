# Lesen R16 — topic-grounded p02/p03 conclusions, 2026-11-07

## Result and scope
- **Authoritative parent**: R15 Library content `libfile_4e9ee6f0ef388191a6a26302b70c4af4`, SHA `efa0fa9ece712f3a045ef47c802efe9230fe1baa366cb43e7f3ba5a8573e4c67`.
- **Curated CURRENT**: original v1.3.0 ZIP SHA `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` unchanged. R16 is a candidate, NOT current/final.
- 13 lessons changed: 025–034 and 036–038. Lesson 035 explicitly preserved because the content was already repaired.
- 22 **German** generic concluding sentences changed in `p02` and `p03`; 55 other lesson objects were byte-equivalent at the JSON-data level, all 340 question identities and 350 vocabulary entries unchanged. The 44 existing Persian/English concluding translations of those 22 sections were **preserved verbatim**, because they already reflected each lesson's specific argument. German was improved to align with them and the preceding German sentences. No fabricated translation edits were claimed.
- All original p02/p03 first two sentences and their FA/EN translations retained exactly.
- 70 invalid obsolete grammar occurrences on removed German endings retired; ten existing curated Relativsatz samples retargeted to **actual** newly written relative clauses; ten narrow/manual full-text relative-clause occurrences added with exact offsets and explicit non-native provenance. Overall 4,220 -> **4,160** occurrences; all 669 curated grammar identities and 68 lesson identities preserved. Native full nine-lens extraction **not rerun**.
- Repeated generic conclusions still remain: **p02=28, p03=21** (49 sentences across possibly overlapping lessons). These are a review queue; do not mass-replace by template.

## Illustrative evidence
- **025, good study organization**: `Realistische Lernpläne schaffen Freiräume, die auf Dauer konzentriertes Arbeiten und höhere Produktivität ermöglichen.` The pre-existing FA/EN translations already said productivity improves over time.
- **026, film vs book**: `Was den Film schnell zugänglich macht, kann zugleich einen Teil der eigenen Vorstellung beim Lesen verdrängen.` This now reflects the approved translation's explicit tradeoff.
- **031, smartphones as educational media**: `Das gleiche Gerät, das spontan beim Lernen hilft, kann durch Benachrichtigungen zugleich die Konzentration stören.` The German now makes the educational benefit/distraction contrast explicit.
- **035, devices at school**: entirely unchanged; already had source-grounded conclusions from R2.

## Tests and limitations
- Independent read-only source/runtime QA: **12672 checks, 0 errors**, 9/9 adversarial mutations detected.
- Exact real v505 `reading-content-import-v38.js` source pre-entry validator: PASS, **zero warnings**, 7/7 broken packs rejected. In-memory projection: 68 lessons and 340 exercises. **NO browser or IndexedDB Stage6 run.**
- Runtime is a scoped, verified delta transport, not a native compiler re-execution or an app release.
- AI-scoped source/translation alignment was reviewed in this batch; **independent holistic Stage4** for all 68 lessons is **HOLD**, native complete nine-lens engine **NOT_RERUN**, browser Stage6 **NOT_RUN**, release Stage7 **NOT_RELEASED**.
- No source-PDF restoration, no app UI, FSRS/SRS, installed user-data or other content-family changes. No automatic deletion.

## File identities
- R16 master: `Lesen-Production-Master-v1.3.0-R16-22CONCLUSIONS-TRILINGUAL-CANDIDATE.json`, SHA256 `0b31f21ed6cd65b2562d3806e58269294196d161b05ba87cc7af35e3ab87ffa5`, 6,218,622 bytes.
- R16 v505 runtime: `Lesen-R16-v505-22CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json`, SHA256 `afec137c5868eb26051c913e3dedefcc848a4a932d5e4cf23e5e21409516f641`, 6,682,538 bytes.
- Detailed before/after with actual already-existing FA/EN end translations: `LESEN-R16-22CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json`.
- Independent QA: `LESEN-R16-INDEPENDENT-SOURCE-QA.json`.
- Exact importer QA: `LESEN-R16-v505-NATIVE-PREENTRY.json`.
- Reproducible scripts: `build_r16.py`, `build_r16_runtime.py`, `verify_r16_independent.py`, `verify_v505_r16_preentry.js`.

## Next
Review next source-grounded batches of generic conclusions, for example 039–052, excluding already-specialized conclusions. In parallel conduct a genuinely independent trilingual editorial quality audit on each lesson, preserving current curated authority; Stage4 must not be inferred from structural PASS. Keep source-owner canonical `Workspaces/lesen-praesentation` and one final release ZIP only after all release gates.