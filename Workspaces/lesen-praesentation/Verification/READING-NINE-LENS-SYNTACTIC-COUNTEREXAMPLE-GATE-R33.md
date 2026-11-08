# Lesen — fulltext grammar syntactic counterexamples (R33, 2026-11-08)

**Scope:** additive owner-specific read-only quality gate for *new/changed* Lesen content; it does **not** claim automatic producer adoption, complete German parsing, independent full Stage4, nine-lens producer rerun or Chrome IndexedDB Stage6. The current application, user SRS/FSRS, official curated CURRENT and all historical originals remain immutable.

## Confirmed problem beyond R31/R32

The initial fulltext grammar engine supplied 3,548 correctly located strings, but some were linguistically false. Exact source-backed examples:
- LES-PRES-001 p01 **`zu den`** incorrectly called *Infinitiv mit zu* (actually preposition + dative article).
- LES-PRES-009 p04 **`hinzufügen`** incorrectly called *Infinitiv mit zu* (bare infinitive after `lassen sich`; `hinzu` belongs to lexical verb).
- LES-PRES-003, 007 and 019: *werden* as copular verb and *verloren gehen* falsely called *Passiv*.
- LES-PRES-006, 008, 013 and 024: ordinary accusative articles or Konjunktiv-I reported content falsely called *Relativsatz*.
- LES-PRES-002, 005: real relative clauses had incomplete target spans, sometimes without the finite verb.
- LES-PRES-002 and 021: adjective **`offen`** incorrectly called clause-final finite verb.
- **Fifteen** p01 occurrences of the passive main-clause participle **`diskutiert`** falsely called `Verbposition im Nebensatz`, when the finite verb of the `ob` clause appears **before the comma**, e.g. **`... gehören sollte`**. In lesson 052, the true `ob`-clause finite verb is `wird`; the exact offset distinguishes it from the later main-clause auxiliary.

## Candidate correction and reproducible evidence

R33 **retires nine false fulltext annotations** and **reanchors twenty** to genuine clauses/finite verbs. It retains byte-identical German/Persian/English reading text for all 478 sections, all 340 question records, 350 vocabulary entries and 669 curated grammar IDs; fulltext total **3548 → 3539**. Before/after evidence and exact character offsets in `03-Reports/LESEN-R33-EXACT-GRAMMAR-REPAIR-LEDGER.json` inside the exact R33 ZIP.

- R33 candidate master SHA256 `28e4b00d83b3899b144e908dfded66f35d8f75695c58671cfee2b230a2559c85`; v505 source-preentry runtime SHA256 `cb1086fccbbf054eb1741aaaf96e08d065fc6ca6dda7b114a522f1901a2a926f`.
- Owner Library ZIP `Lesen-R33-SCOPED-NINE-LENS-SYNTAX-REPAIR-CANDIDATE-20261108.zip`, SHA256 `4684e842ccefa5c95b52e2748d23a500718ff10b5c9b64931186b0369ea33ec2`, stable ID `libfile_149314f1a5d88191b5d1377a4fad0338`. Post-upload exact SHA/byte-CMP/CRC, 20/20 member hashes and fresh extracted deterministic replay PASS.
- Run from extracted R33 ZIP:
```bash
python 04-Tools/gate_reading_syntactic_truth_v1.py 01-Content/R32-PARENT-MASTER.json
# expected blocking exit 1 — 29 exact diagnosed source cases

python 04-Tools/gate_reading_syntactic_truth_v1.py 01-Content/Lesen-Production-Master-v1.3.0-R33-GRAMMAR-SEMANTICS-CANDIDATE.json
# expected success exit 0

python 04-Tools/verify_portable_r33.py
# reconstruct and verify exact master/runtime, independently run QA and real v505 JS source module
```

**Prospective rule:** before accepting new Lesen fulltext grammar, check the **truth of grammatical category and syntactic role**, not only whether an offset or target string exists. Repeat this counterexample suite and the R32 curated/grammar-task gate after text edits. A PASS from these narrow tests alone must never be upgraded to complete `Stage4` or nine-lens original-engine acceptance.

**Wiring boundary:** Exact tool source is shipped in R33 Library recovery ZIP. As of this checkpoint, no evidence that all external/legacy authoring adapters invoke this automatically. Do not mark central cross-family adoption until producer binding + deliberate negative regression test proves it.
