# Lesen – Präsentation B2–C1 · R9 scoped p04 rewrite and v505 preentry

**Date:** 2026-11-07 · **Owner:** `family:lesen` / `Workspaces/lesen-praesentation`  
**Status:** **R9 CONTENT + RUNTIME CANDIDATES; EXACT STRUCTURAL QA PASS, NATIVE v505 PREENTRY PASS; FORMAL STAGE4/6/7 HOLD**.

## Authority and non-destructive scope

The immutable/source-owner **CURATED_CURRENT** remains `Lesen-Praesentation-B2-C1-v1.3.0-CONTENT-PRODUCTION-DELIVERY.zip`, SHA-256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` (Library `libfile_9b768265ff3c8191aca371baa38551d7`). R8 content master SHA-256 `f3e22d1f62aa78590f44ccfe358a9240319a99c9d8a1f39fc8a1ee81ac6d4cf2` and R8 runtime SHA-256 `da770588aee670e60cf985dbfdcfd4fe0715847b43822f214ce90ba27bba4608` are the exact parent inputs. Original textbook PDF is read-only provenance, not the working editorial authority.

**R9 content master (candidate):** `Lesen-Production-Master-v1.3.0-R9-10P04-TRILINGUAL-CANDIDATE.json`, SHA-256 `52667254d47987e5f4c4146078fd2c8204e80152de3268cd0eb599fc0c2f8171`, 6,579,557 bytes.  
**R9 v505 transport (candidate):** `Lesen-R9-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json`, SHA-256 `115a988c339f6fa392091727a7aab10f4456d6b7e04e7678492867e785e5aa59`, 7,083,068 bytes.  
Neither file replaces CURRENT; no new cumulative release ZIP is made.

## Editorial changes — ten actual lessons, no blanket substitution

Lessons `LES-PRES-011` through `LES-PRES-020`: 10 p04 reading sections revised. For each: paragraph-leading **generic** sentence replaced by a claim grounded in the existing p02/p03/p05; subject-specific middle `p04-s02` preserved exactly; generic third sentence replaced by a concrete lesson-specific conclusion or recommendation. This is 20 edited German sentences and 10 complete revised p04 German/Persian/English sections.

| Unit | Topic and differentiated argument |
|---|---|
| 011 | Tuition: balance funding, who bears the cost, and equal access |
| 012 | Physical education: varied abilities, individual progress and inclusive assessment |
| 013 | Tourism: short visits vs actual intercultural understanding and local culture |
| 014 | Literature: compulsory reading, engagement and language difficulty levels |
| 015 | Study choice: limits of labor-market forecasts alongside motivation |
| 016 | Social media: online vs face-to-face relationships and platform algorithms |
| 017 | Early STEM: curiosity, safe mistakes and avoiding early selection pressure |
| 018 | Children’s praise: specific feedback vs dependence on external approval |
| 019 | Inventions: usefulness, accessibility and unintended long-term consequences |
| 020 | Distance learning: flexibility, student support and self-organization |

The full **before/after text for DE–FA–EN**, source-owner topic references, grammar changes and per-unit hashes are in `LESEN-R9-10P04-EDITORIAL-AND-GRAMMAR-LEDGER.json`. These are authored editorial interpretations grounded in the *current* content, **not literal transcriptions from the original PDF** and not independent certified semantic QA.

## Grammar anchor disposition (critical)

- Before R9: 4,620 fulltext grammar occurrences.
- **60 old occurrences invalidated** because they pointed into replaced p04-s01 or p04-s03 text; none were silently moved to unrelated material.
- **32 preserved p04-s02 occurrences accurately re-offset** after the new s01 sentence. The sentence, target and grammar evidence are unchanged.
- **10 new, manually checked scoped occurrences** of Konjunktiv II `sollte`/`sollten` added in p04-s03. These are explicitly marked `annotation_source=editorial_scoped_r9`, *not* the legacy grammar generator.
- **Five existing curated p04-s03 Konjunktiv II annotations** retargeted to the new sentence with honest `editorial_retarget_r9` source attribution; all 669 curated annotation identities remain present and verifiable.
- Result: **4,570** exact full-text occurrences, each matched against its actual DE section text and sentence. **The original nine-lens grammar engine has NOT been rerun**, so no full pattern-completeness certification is claimed; this is a gap recorded for later native regeneration.

## Independent QA and exact current-app preentry

`verify_r9_independent.py` ran 13,519 separate structural/semantic-linkage *structural* assertions with **zero failures**. Nine adversarial file corruptions were detected. It verified: all 68 owner units, 58 byte-identical unaffected units; all 478 exact DE–FA–EN sections and Runtime mappings; stable 340 Q/A IDs and payload; 350 vocabulary entries; 669 curated grammar annotations; all 4,570 occurrence offsets; 10 newly authored p04 sections; all original p04-s02 sentences; entry/payload SHA integrity and counts. This QA proves transport integrity and target alignment, **not linguistic correctness or translation nuance at independent Stage4 depth**.

The exact `reading-content-import-v38.js` from `GFP-v505-R141-WORDLINKS-FRONT-BACK-R3` (module SHA-256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`) returns **PASS with zero warnings**, reports 68 units, 478 passages, 340 questions, 478 FA and 478 EN translations and 4,570 anchored full-text grammar matches. Seven deliberately corrupted runtime variants are rejected; an isolated **in-memory** projection reads 68 units/340 exercises. This is **only native source preentry validation**; **no Chromium browser/IndexedDB transaction, persistence/reload or installed-user profile test** was executed. Stage6 is `NOT_RUN`, not PASS.

## Remaining scope and next checkpoint

Generic p04 text beginning `Entscheidend ist deshalb die konkrete Ausgestaltung.` fell from **55** to **45** lessons. The next bounded editorial batch can address 021–030, but only after independently checking local topic context and when exact grammar anchors can be safely maintained. Other generic p01/p02/p03/p06/p07 passages, q05 rubrics, incomplete native grammar regeneration, holistic DE–FA–EN Stage4, browser import Stage6 and final Stage7 remain unresolved. Do not promote or delete earlier candidate/Current artifacts automatically; keep app UI and user SRS/FSRS unchanged.

**Durable pointers:** `Workspaces/lesen-praesentation/QUALITY-REVIEW-CHECKPOINT-R9-20261107.json`, the owner `ARTIFACT-REGISTER.json`, and `Optimization-Program/Control-Center/LESEN-CONTENT-CURRENTNESS-PIN-20261107.json#review_r9`. Library route is `/Flasch kart/German-Content-Production-Kit/Content/Lesen/` (`Candidates`, `Reports`, `Checkpoints`, `Tools`).