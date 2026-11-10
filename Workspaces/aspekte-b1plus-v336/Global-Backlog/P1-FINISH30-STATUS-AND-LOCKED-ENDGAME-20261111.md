# Aspekte B1+ — P1 finished (scoped), 11 November 2026

## Scope & evidence

- **Current data owner**: `Aspekte-B1plus-P1-30-CASE-RESOLUTION-10-EDITS-NONIMPORT-20261111.zip`
- ZIP SHA-256: `85fb2a1962424224d50701be17f465bad5bf2a1bd3f8f7b1a368e301b3fb1b6b` · Primary JSONL SHA-256: `09e47577d77cf391ece2463d4984f61f006a8c2aea268522a8cab96b997f5f6d`
- Source-map SHA-256 (unchanged): `c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882`
- 1571 cards; 1548 original source ordinals mapped, all IDs unchanged; 1541 out-of-scope primary card lines byte-identical.
- 30 P1 cases each have an explicit evidence-bearing disposition in the archive, with full before/after; **10 real editorial content edits; 20 legacy risk flags dismissed only after examining current meanings and German–Persian examples**. This is NOT automatic blanket certification.
- 3 new bilingual examples; two prior bilingual example pairs editorially corrected; total 3566 example pairs; three sense blocks created.
- P1 0 / P2 190 / P3 30 = **220 open content HOLD cases**.
- Library readback SHA-256/ZIP CRC/357 manifest entries passed; separate verifier compared old/new primary data and risk ledger.

## Notable content changes

- 653 `Industriezeitalter` and 657 `Maschinenzeitalter` — both **ohne Plural**, rather than an invented unchanged plural. [Duden Industriezeitalter](https://www.duden.de/rechtschreibung/Industriezeitalter) · [Duden Maschinenzeitalter](https://www.duden.de/rechtschreibung/Maschinenzeitalter)
- 944 `anstellen` — two important `sich anstellen` senses added (queueing; acting in a particular manner), each with a German–Persian example. [Duden](https://www.duden.de/rechtschreibung/anstellen)
- 190 `fein` — added idiomatic colloquial positive evaluation as S4 with own example. [Duden](https://www.duden.de/rechtschreibung/fein)
- 482 `neben` — additive meaning `neben + Dativ` clarified on front; locative/directional valency retained.
- 870 `Dienst` — repaired an unnatural Persian rendering of visiting care-service staff.
- 979 `journalistisch` — identified relational non-comparable adjective used adverbially; improved German–Persian example.
- 1210 `ausschließen` — negated `nicht ausschließen, dass` context clarified.
- 1262 `entladen` — marked psychological outburst sense as reflexive `sich entladen`.
- 1303 `Quote` — TV rating is a relative audience share, not an absolute headcount.

## Release remains blocked

These are **case-scoped risk closures**. New examples are PENDING. No complete German–Persian linguistic signoff, no native approved import, no durable storage/restart proof, no right-card multi-sense UI acceptance or SRS preservation is claimed. No forced human reviewer, old publisher CSV recertification, or redoing L01–L10.

## Fixed endgame — no new audit loops

1. **P2 190**: one full 190-case content-first pass. Fix proven grammar/sense/DE–FA defects, explicitly dismiss stale flags after case evidence, preserve all unrelated cards. Record one case ledger and merged Master.
2. **P3 30**: one 30-case final low-risk pass, close genuine legacy-only flags or fix discovered errors, with original count/ID regression.
3. **Release gate**: trusted content authorization, PR41 integration with real Native JSON/ZIP/TSV import in an isolated profile, typed right-card presentation, origin-backed IndexedDB save/restart, SRS preservation; only then promote to importable release.

**No next step may re-open P1 without a documented regression**. App gates are distinct from content quality gates; do not present an isolated browser test as native production acceptance.
