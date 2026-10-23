# NVV independent read-only content review — 2026-10-23

Status: **STRUCTURAL_FULL_CORPUS_PASS / INDEPENDENT_FULL_SEMANTIC_AUDIT_NOT_COMPLETE**.

- Locked artifact: `German-Flashcards-Pro-v465-R99-Nomen-Verb-Verbindungen-v3.3.6-LOCKED-CONTENT.zip` SHA-256 `917ba9561245deea32cc3be1095af0185858d3d45d8eb7ff40e4a7b4c361771f`.
- Exact source: `nomen_verb_verbindungen(1).pdf` SHA-256 `a817dab76f9e78e896f596bd37b66168f04e995fd68203c045c7d87437ac258d`.
- Read-only structural and source/provenance checks executed on actual locked ZIP: 2492/2492 cards, 9968/9968 DE/FA/EN triplets, 2476 source occurrences, 0 orphan IDs, 0 TSV/canonical parity mismatches, 0 exact duplicate sentences.
- Source native-PDF row presence: 2475 exact and 1 documented PDF line wrap (`dah-nvv-occ-02249`, PDF physical page 24).
- 59 rough heuristic flags are **not** 59 confirmed language errors; false-positive patterns include grammatical relative pronouns and compound auxiliaries. Do not auto-repair from heuristic alerts.
- Curated editorial examples requiring a reviewed successor (no locked-byte mutations):
  1. `dah-nvv-exp-00766`, FA example 1, tautology “متهم به جعل امضا متهم شد”.
  2. `dah-nvv-exp-00870`, FA example 1, unnatural “تهدیدهای بلند” for loud voiced threats.
  3. `dah-nvv-exp-01252-a`, FA example 1, redundant/unclear “نتیجهٔ ضعیف نتیجهٔ لازم را گرفت”.
  4. `dah-nvv-exp-00545`, FA example 1, redundant “خدمت دولتی، خدمت را ترک کرد”.
  5. `dah-nvv-exp-00207`, FA example 3, “بازسازی داخلی” can mislead for corporate `interne Umstrukturierung`.
  6. `dah-nvv-exp-01906`, EN example 3, less idiomatic “vote for in the ballot”.
- Blank CEFR and lesson fields and all empty lexical relation links are inherited policy/closed-no-force choices, not newly verified semantic completeness.
- Independent card-by-card human-style evaluation of all 9968 examples was **not** accomplished in this review; prior Stage4 full-audit evidence is historical, separate.
- The local report and machine-readable evidence were packaged into `NVV-CONTENT-AUDIT-2026-10-23.zip` SHA-256 `048a284d5498a9d2b95beccec1d437ec32bdc31ac8347da045441baa231e1c38`; deliver on user-facing artifact surface, not Git binary transport.
- Recommended: preserve exact locked artifacts and source references. Adjudicate findings; only then build a separate reviewed successor and conduct a traceable independent semantic audit of remaining cards if full independent linguistic certification is required. Do not relabel the existing LOCKED content as rejected or silently mutate it.

No source, card, checkpoint, or runtime file was modified as part of this review.
