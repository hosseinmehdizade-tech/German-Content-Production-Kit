# Lesen – R6: 20-lesson evidence-based question repair and v505 pre-entry (2026-11-07)

**Owner:** `family:lesen` / `Workspaces/lesen-praesentation`.  **Candidate only; no publication or content CURRENT change.**

## Real outcome

Reworked **60 explicit German question/answer pairs**: q01, q02 and q03 in every unit **LES-PRES-011..030**. These were authored individually, using the exact CURATED_CURRENT-derived R5 passage texts (p01/p06 for main claim, p02 for concrete details and p03 for counterarguments). Old generic wording replaced with a lesson-specific question and a concise, defensible model answer. Full per-pair before/after and the specific unchanged source passages are stored in `LESEN-R6-60Q-SEMANTIC-EVIDENCE-20261107.json`.

Two examples:
- **011 Studiengebühren:** “Welchen Ausgleich zwischen Hochschulfinanzierung und Zugang zum Studium fordert der Text?” → “Hochschulen müssen dauerhaft gut finanziert werden, doch das Studium soll grundsätzlich unabhängig von der finanziellen Lage einer Familie zugänglich bleiben.” (`p01`, `p06`)
- **018 Kinder loben:** “Wie unterscheidet der Text hilfreiche Anerkennung von übertriebenem Kinderlob?” → “Kinder brauchen ehrliche Anerkennung, aber kein künstliches Dauerlob; auch kritische Rückmeldungen gehören zur Entwicklung.” (`p01`, `p06`)

Prompt diversity by position increased from **11 / 14 / 13 / 68 unique** at R5 to **31 / 34 / 33 / 68 unique** at R6 for q01/q02/q03/q04. The repeated leading groups now comprise 38, 35, 36 literal duplicate prompts respectively; more than these literal repeats, the program contains multiple templated paragraph bodies and generally repetitive argumentation.

## Byte-pinned lineage and scope

- **Existing immutable CURATED_CURRENT:** v1.3.0 content ZIP SHA `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` (`libfile_9b768265ff3c8191aca371baa38551d7`) — unchanged.
- **R5 master parent:** SHA `6371522e011333c836969ae2983c69ecbc259743632a6b44226b3bc5ef7ab764`.
- **R5 v505 Runtime parent:** SHA `cf66efa8ae1376116b8f9e68e0090b71d47ea964ce2f65c57034df609df5f943`.
- **R6 master candidate:** SHA `3a727fc2575b5c041808803b6a97d2a77239aa3089f6bf88570c39e959d26f5c`, 6,621,789 bytes.
- **R6 v505 Runtime pre-entry candidate:** SHA `3843634a8300f16a14e192c3ecef04b3e83b7dcad9631a84162495ce307ea625`, 7,128,566 bytes.
- **Change isolation:** 20 candidate content units / 60 q01..q03 prompt+answer pairs changed. Remaining 48 units and all q04/q05 unchanged. All **478 reading sections, 68/68 DE/FA/EN passage collections, vocabulary, grammar records, sentence identities, 340 question IDs and 4620 exact grammar offsets** are inherited unchanged. The q05 opinion exercise intentionally has no source-section evidence; its approved original behavior was preserved.

## Actual tests performed

- Independent structural and exact-delta tests: **6,738 checks, 0 failures**, plus **7/7 correctly rejected adversarial mutations** (missing Persian, wrong grammar offset, false question identity, invalid evidence, runtime tampering, missing answer, unauthorized passage change).
- Source-native **exact CURRENT v505 Wordlinks R3 reading-content-import-v38.js** validated R6 Runtime: **PASS**, **0 warnings** and 68 entries / 478 sections / 340 questions / 350 vocabulary entries / 4620 full-text grammar annotations. Its **6/6 corrupt-pack probes** were rejected; in-memory isolated projection passed. This is **NOT** a real browser import or IndexedDB persistence test.
- Semantic editorial review uses the actual R5 text of each unit and a source-anchored AI pass, but **does not constitute independent holistic Stage4 linguistic and translation certification**. Q/A text has no standalone FA or EN translations; the DE–FA–EN reading bodies were kept byte-stable in their JSON structures.

## Explicit HOLDs

1. **Remaining generic q01/q02/q03** for other units and other repetitive question/paragraph templates, including approximately 55 generic p04 passages.
2. **Whole-dataset German–Persian–English semantic Stage4** and independent adversarial linguistic QA are not complete.
3. Original full native nine-lens grammar generator has not been rerun. Keeping 4620 exact positional anchors does **not** prove the grammar explanations are linguistically impeccable.
4. Browser/IndexedDB native Stage6, data-preservation and installed-app acceptance **NOT_RUN** due to environment boundary; Stage7 not released.

## Recovery and next action

Keep R5 content and pre-entry runtime as historical independent recovery candidates; keep v1.3.0 Current immutable. Continue with **units 031..050**, q01–q03 where still generic, but avoid rewriting already individually corrected 035, 043 and preserve approved exceptions. Fix high-risk semantic defects before broad text templating; if actual passage wording is revised, update translations and all affected grammar offsets in the same reviewed candidate. No repetition-only Library ZIP or automated deletions. The source owner's `QUALITY-REVIEW-CHECKPOINT-R6-20261107.json` is the next resume authority; legacy separate Stage1–7 `CHECKPOINT.json` remains unchanged.