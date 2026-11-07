# Lesen – Präsentation B2–C1 · R1 quality and v505 compatibility review

**Date:** 2026-11-07  
**Owner:** `family:lesen`, `Workspaces/lesen-praesentation`  
**Immutable CURRENT content ZIP:** `Lesen-Praesentation-B2-C1-v1.3.0-CONTENT-PRODUCTION-DELIVERY.zip`  
**SHA-256:** `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`  
**App CURRENT reference:** v505-R141 Wordlinks R3 ZIP SHA-256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`. 

## Decision: substantive content-quality HOLD, while preserving v1.3.0

This is an independent **read-only** content risk audit covering all 68 master units plus a **narrow human-readable AI semantic spot-check** of German, Persian, and English material in units 035, 051, and 059. This is NOT full semantic Stage4 acceptance, NOT a new learner content version, and not Stage6/7. Do not mistake structural PASS for linguistic/editorial PASS.

### Proven across the 68 current texts

- All **68 units / 340 reading questions** were scanned by the reproducible source-native read-only checker.
- **58 units (`LES-PRES-011` through `LES-PRES-068`)** share a repeated question-template pattern: four identical prompts recur at least 58 times, with `Welches Gegenargument wird genannt?` used 59 times because `LES-PRES-001` also uses it. `LES-PRES-001` is **not** part of the 58-unit template cohort; it shares only that one prompt.
- All master texts contain **1,494 sentence occurrences**, **1,015 distinct exact sentences**; **479 occurrences beyond the first copy** are exact repeats (503 sentence occurrences belong to a repeated group). These repetitions affect the 58 templated units, not the ten earlier individually written units. **Six complete reading-section text groups** occur more than once.
- The identical interpretation question `Warum spielt die konkrete Ausgestaltung eine so wichtige Rolle?` and identical sample answer `Weil die Folgen stark davon abhängen, unter welchen Bedingungen eine Maßnahme umgesetzt wird.` recur in **58** different topics.
- This is a **pedagogical quality risk**: generic prompts are under-specific; identical passages can displace topic-focused argumentation. Repetition alone does not prove an individual sentence grammatically wrong. The exact 58-unit review queue is preserved without any content edit.

### Concrete semantic issues examined in current master

**HIGH, LES-PRES-051, section p02 (technical studies / gender differences).** The German section argues that educational choices are shaped by social expectations, lack of role models, and stereotypes, then concludes `Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.` That German conclusion is *not* entailed by the preceding explanation; it switches unexpectedly to a generic claim about benefit. The corresponding Persian conclusion states `بنابراین تصمیم تحصیلی همیشه صرفاً یک ترجیح فردیِ جدا از محیط نیست.` and the English says `Educational decisions are therefore not always purely individual preferences detached from the surrounding environment.` The FA/EN are topic-specific but are **not translations of the actual German conclusion**. Targeted DE content plus DE–FA–EN alignment correction is required. Do not silently rewrite it without verifying the full paragraph and intended sense.

**HIGH, LES-PRES-051, question q02 and section p03.** Q02 uses `Welche zwei Argumente sprechen im Text für eine positive Bewertung?` about causes of male dominance in technical degrees. "Positive evaluation" is inappropriate for this causal inquiry. Section p03's template counterargument/value language also blurs causal explanation and normative pros/cons. Review whole p02–p04 argument structure, not just q02.

**MEDIUM, LES-PRES-059, section p03 / q02.** The German p03 labels the independent study requirement of on-campus students as `Es besteht die Gefahr, dass auch Präsenzstudierende selbstständig lernen müssen ...`; that is not naturally a *danger*. The template q02 again says `für eine positive Bewertung` without specifying distance-learning independence. Review causal wording and ask a task-specific reading question.

**MEDIUM, LES-PRES-035, question q04.** The generic `Warum spielt die konkrete Ausgestaltung eine so wichtige Rolle?` fails to ask directly about the text's concrete device policies, privacy, support, or equality concerns. The section-specific source text supports a more discriminating question.

### Candidate questions for editorial review — NOT applied to master

| Unit | Replace only after checking source text / evidence | DE proposal |
|---|---|---|
| 051 q02 | Generic positive-rating prompt | *Welche Gründe für die ungleiche Geschlechterverteilung in technischen Studiengängen werden genannt?* |
| 059 q02 | Generic positive-rating prompt | *Welche Anforderungen an die Selbstorganisation und welche Vorteile des Fernstudiums nennt der Text?* |
| 035 q04 | Generic generic implementation prompt | *Welche Bedingungen müssen Schulen erfüllen, damit digitale Geräte den Unterricht sinnvoll unterstützen?* |

These are scoped examples; generating 58 different questions automatically is **not** allowed without checking topic, answer, section evidence, and DE–FA semantics per unit. Existing stable unit and question identities must remain intact across an authorized replacement.

## Exact current-app v505 source validator replay

The actual `01-App/modules/reading-content-import-v38.js` function `validateRuntimePack` was extracted from the exact stored v505-R141 R3 runtime ZIP **without changing its function body**, and run in a disposable Node VM against the exact v1.3.0 embedded `02-Compiled-Runtime/Lesen-Runtime-Pack-v1.0.0.json`:

- **PASS, 0 errors**; 68 entries, 478 passages, 340 questions, 350 vocabulary items, 478 Persian + 478 English passage translations, 4,612 fulltext grammar spans, zero independent `lexical_targets` (vocab is carried in per-reading metadata).
- **One existing warning:** `integrity.payload_sha256` is absent from the inner runtime JSON. The outer delivery ZIP and inner runtime SHA-256 are independently verified; the live validator does not infer payload-integrity PASS from that alone.
- **4 / 4 adversarial input cases correctly rejected** by the exact native function: duplicate reading source ID, blank Persian passage, broken exercise reference list, invalid grammar span offset.
- v505 explicitly regards the **Production Master `lesen.content.v1.3.0` as NOT directly importable**; the importable file is the **compiled `lesen.runtime.v1.0.0` JSON** extracted from the ZIP. Do NOT import the historical v413 inner ZIP as the new curated master.
- Attempted *disposable Chromium* navigation using both `file://` and `http://127.0.0.1` was denied by `ERR_BLOCKED_BY_ADMINISTRATOR`. No import/persistence/UI or installed-user-data validation occurred: **Stage6 NOT_RUN**. Do not mark v505 import fully proven or change user IndexedDB/FSRS/SRS.

## Central decisions, state and next meaningful work

1. Retain the exact v1.3.0 ZIP as `CURRENT_ACTIVE` **editorial baseline**, with an explicit quality-risk HOLD attached. There is **no new current release, no in-place mutation, no `FINAL` promotion**.
2. Perform a bounded source-native editorial repair for the highest-impact units (first 051, 059, 035), with DE/FA/EN alignment and question-to-evidence review; for later 58 units use the same semantic standard, not generic text replacement. After each meaningful batch, compare the actual approved current -> next deltas and run all structural gates again. This is independent of old textbook inventory matching.
3. Continue source-specific runtime compiler verification; once browser testing is available, validate import/reading panel/translation toggle/grammar anchors/questions/IndexedDB nonregression on **exact app CURRENT v505**, NOT old v413/v470.
4. Existing seven-stage Git `CHECKPOINT.json` remains **Stage1 PASS / Stages2–7 NOT_STARTED**. These scoped audit discoveries are stored separately; independent Stage4 quality has **HOLD**, while direct-import validator PASS does not promote Stage6.
5. Apply central `Prompt/ACTIVE-PROMPT.txt` -> `START-PROMPT-v3.3.6.md` -> `GLOBAL-POLICY-REGISTRY-v1.0.0.json` plus curated-current, no-churn, source-native applicability, owner lifecycle. No visible app UI or FSRS/SRS changes, no source/LOCKED deletion and **no report-only ZIP**.

**Evidence siblings:** `LESEN-v1.3.0-68-UNIT-QUALITY-QUEUE-20261107.json`, `LESEN-v1.3.0-58-UNIT-REVIEW-QUEUE.csv`, `LESEN-v1.3.0-v505-PREENTRY-CONTRACT-20261107.json` and read-only `audit_lesen_v13_content_quality.py`.