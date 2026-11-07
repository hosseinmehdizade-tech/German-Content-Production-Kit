# Lesen — R7 editorial and v505 pre-entry verification · 2026-11-07

**Owner:** `family:lesen` / `Workspaces/lesen-praesentation`. **Current protected:** v1.3.0 original ZIP SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`, unchanged; original not rebuilt from textbook.

## Material edited

- Exactly lessons `LES-PRES-031` through `LES-PRES-050` were reviewed against their existing curated German source passages, not original PDF.
- **58 prompts** and **57 model answers** on q01–q03 changed, respecting approved exceptions: lesson 035 q02+q03 already good and untouched, lesson 043 q03 previous corrected answer preserved while question sharpened.
- **48 other lessons**, every passage across **478** sections, German sentences, FA/EN translations, 340 question IDs, CEFR and metadata, 4,620 anchored full-text grammar occurrences and 669 curated grammar records all remain unchanged. Question q04/q05 unchanged.
- Learner-facing unique question prompts: q01 **51/68**, q02 **53/68**, q03 **52/68**, q04 **68/68**. Remaining generic prompts q01 18, q02 16, q03 17; not all 68 readings have full semantic QA.

## Quality evidence and limits

- Independent code `verify_r7_independent.py` checked **7144** structural invariants, **0 failures**, and **9/9** adversarial mutations rejected. Read-only independent QA, not specialist linguistic assessment.
- The *actual current v505-R141 Wordlinks R3* `reading-content-import-v38.js` module was executed under isolated Node VM against the **exact** R7 candidate: `validate` PASS with **zero warnings**, six corrupt candidate mutations rejected, and in-memory projection PASS for 68 units / 340 exercises. This **does not** call browser IndexedDB, import into an installed app or certify Stage6.
- Original native nine-lens grammar producer not rerun; full independent DE–FA–EN semantic Stage4 remains **HOLD**, as do browser Stage6 and release Stage7.
- No changes to user app UI, app runtime code, SOURCE/LOCKED, current content ZIP, SRS or FSRS. No historical cleanup/deletion.

## Byte authorities

| Artifact | SHA256 | Size |
|---|---|---:|
| R6 content parent | `3a727fc2575b5c041808803b6a97d2a77239aa3089f6bf88570c39e959d26f5c` | retained |
| R7 edited content | `f472a6260b29f7112bfdf71894f1004957ade61d8ec9bc842992f5a6e4c718d9` | 6,621,867 bytes |
| R7 v505 preentry runtime | `043126b22cc256a911ec9697888b5f944a4520ddb3e22ef74de423abc3c9c6b3` | 7,130,508 bytes |

**Do not promote these R7 candidates to CURRENT solely from successful tests.** Next scoped batch: lessons 051–068; afterwards independent language QA and actual disposable-browser import.