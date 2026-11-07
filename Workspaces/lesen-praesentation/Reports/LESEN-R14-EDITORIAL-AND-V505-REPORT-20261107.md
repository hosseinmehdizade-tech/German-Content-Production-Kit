# Lesen R14 — source-bound p03 trilingual editorial and v505 preentry report

**Date:** 2026-11-07. **Scope:** R13 → R14, 14 units, p03-s01 and p03-s04 only; **not an educational release**.

## Actual editorial changes

- Units: LES-PRES-013, LES-PRES-017, LES-PRES-021, LES-PRES-025, LES-PRES-029, LES-PRES-033, LES-PRES-037, LES-PRES-041, LES-PRES-045, LES-PRES-049, LES-PRES-053, LES-PRES-057, LES-PRES-061, LES-PRES-065.
- Replaced **28 generic German sentences** in 14 p03 sections, and authored aligned full Persian and English translations for each changed section.
- Preserved **28 source-specific middle sentences** (`p03-s02` and `p03-s03`) without rewriting them. Other **54 units**, all 340 existing comprehension questions, 350 vocabulary entries and 669 curated grammar annotations stayed exact.
- The former 14 identical p03 openings `Dem stehen jedoch gewichtige Einwände gegenüber.` and their generic p03-s04 conclusions were removed in those fourteen units.
- Scoped full-text grammar went from **4345 to 4298**: 56 invalid references to removed sentences retired; 95 annotations for the unchanged middle sentences exactly repositioned; **9 manually verified, varied constructions** added. This is **not** a complete native nine-lens grammar generation or completeness certification.

## Whole-pack verification and native code boundary

- Independent structural/source integrity: **13140/13140 checks PASS**, 9/9 adversarial corruptions detected.
- All 4,298 full-text offsets match their exact target substrings and source sentences; exact mappings between 68 source items and v505 runtime entries match.
- Actual unmodified **v505-R141 Wordlinks R3** `01-App/modules/reading-content-import-v38.js` loaded in Node VM: **PASS, 0 errors, 0 warnings**, 7 deliberately broken payloads rejected. Isolated in-memory adapter projection: 68 units, 340 exercises. No browser/IndexedDB transaction performed.
- Candidate runtime: 68 entries, 478 multilingual passages, 340 questions, 350 vocabulary entries, 669 curated grammar, **4,298 scoped exact grammar occurrences**.

## Important unresolved quality issues

- Duplicate p03-s03 general conclusion remains in **41** lessons (`Ein Vorteil auf der einen Seite ...`).
- Duplicate p02-s03 general conclusion remains in **55** lessons (`Dadurch kann ein Nutzen entstehen ...`).
- These exact repetitions are an editorial review queue, **not evidence that all 96 need blanket substitution**. Inspect topic-specific arguments, translations and grammar anchoring before any changes.
- Whole-pack independent German–Persian–English semantic **Stage4 HOLD**. Native full nine-lens grammar engine **NOT RUN**. Browser/IndexedDB **Stage6 NOT RUN**. **Stage7 NOT RELEASED**.
- All future changes start from the curated R14 candidate. Do **not** rewind to source book/PDF. Do not modify app UI or user's SRS/FSRS records.

## Immutable current, parent and candidate

- Original curated v1.3.0 CURRENT ZIP still unchanged, SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.
- Parent R13 master SHA256 `d619d7d9777849a25a154b52574b66a3dd92fc4f4d045e7b4ceb4e0fbc16b30f`; parent R13 runtime SHA256 `628f56e6bab608a6ab5f7a8939eea3a8451f1fbc4a8699bcaeb23a56f10d78a7`.
- R14 **content candidate** `Lesen-Production-Master-v1.3.0-R14-14P03-TRILINGUAL-CANDIDATE.json` SHA256 `40f4eee25d4ea541d33f91f327bc88243ec5e2971419927ae43c2f0035af2568`, 6341544 bytes.
- R14 **v505 runtime preentry candidate** `Lesen-R14-v505-14P03-RUNTIME-PREENTRY-CANDIDATE.json` SHA256 `84b4e1aa8ad6f9299545eb52b2a730474dfc91e635be5cbd843d8e2bca4ea4f3`, 6818121 bytes.
- Report, before/after ledger, independent verifier and deterministic source-aware transport tools accompany these candidates; no temporary artifacts were promoted into CURRENT.