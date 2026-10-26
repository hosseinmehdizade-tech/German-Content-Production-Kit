# Kombinationen – Didactic Added-Value Gate v1.0.0

Status: ACTIVE prospective QA overlay; effective 2026-10-26.
Framework: v3.3.6 + Prompt/LEXICAL-KOMBINATIONEN-ENRICHMENT-POLICY-v1.0.0.md (kept intact).
Full portable implementation: /German-Content-Production-Kit/Checkpoints/German-Content-Kit-Kombinationen-Didactic-Quality-System-v1.0.0-2026-10-26.zip
Exact ZIP SHA256: d6d558584559c85dcd3d9702e53387f029d676332a926bef8de1094ddc404501
Tested scanner: 02-Tools/audit_kombinationen_mehrwert.py; SHA256 819dd89dee95280f9c69985c51328b66d4073a78cf0abfb78f53972c597a9962.
Full policy: 01-Policy/KOMBINATIONEN-DIDACTIC-MEHRWERT-GATE-v1.0.0.md inside the verified portable ZIP.

## Required cross-workstream behavior

1. Applies to all lexical cards, not only verbs/Menschen: lexical verbs, nouns, adjectives, adverbs, expressions, Menschen lesson lexical cards, irregular verbs, 250 verbs with prepositions, Aber Hallo lexical records, Bildkarten. Source NVV, Grammar, Lesen and Schreiben only if they produce standalone learner-facing lexical combinations. Preserve independent workstream authorities.
2. Before Stage3B select or generate a Kombination, inspect ALL currently learner-visible senses, DE/FA/EN examples, related terms, and existing same-card combinations. Do not repeat an example just to create another item.
3. Each displayed candidate requires concrete, recorded teaching_delta: governed case/preposition, collocation, fixed phrase, sense-specific object, register, realistic reusable context, lexical pattern or meaningful contrast. Non-obvious useful source-exact phrases may appear in both examples and combinations ONLY with an explicit learner-benefit reason; overlap is a flag, NOT automatically an error.
4. NEVER require 4–6, 5, or any other item count per card; no default fill. Justified CLOSED_NO_FORCE and zero visible items are valid. Do not fabricate phrases, evidence, translations or source locators.
5. Never treat PARENT_GENERATED_EXAMPLE as independent source evidence. Always tag exact kind/provenance, sense, DE/FA/EN and reviewed source evidence; manually authored patterns remain CURATED_PEDAGOGICAL.
6. On the exact current TSV/ZIP run the didactic preflight. Flags include normalized placeholder variants (jdn. vs jemanden), within-card duplicate, bare lemma, exact example span, lexical overlap and short/generic phrases. The scanner is an ADVISORY risk detector, not an AI linguistic or dictionary certification.
7. Adjudicate every flag as KEEP_WITH_REASON, CORRECT (apply now to mutable current bytes), REMOVE (apply now), or HOLD_SOURCE. Record exact source SHA256, stable card ID, original phrase, matching rule, teaching delta/justification and evidence. The scanner --gate accepts only dispositions bound to the exact current SHA; re-run on new edited bytes. Unreviewed flags block this supplemental didactic gate.
8. Run independent-method AI linguistic Stage4 review of retained items across DE/FA/EN: sense, valency, semantic appropriateness, register, naturalness, translation, evidence and distinct learning value. Risk flags handled does NOT mean official Stage4 PASS. Official Stage3C/4/5 verification and CURRENT Stage6/Stage7 remain required.
9. Re-audit all already completed lexical content workstreams, using newest exact portable authorities and per-stream LATEST. Build risk ledgers and safe non-destructive successors to LOCKED or user FINAL artifacts; never mutate original raw sources or lesson IDs/order/example text without source-approved separate repair. No UI change, mass automatic deletions, cross-workstream overwrite or density restocking.
10. One complete content-production ZIP per corrected workstream only after applicable official gates; no series of micro-edit ZIPs. Keep old immutable releases available as regression references.

## Pilot, not final verification

B1 original FINAL: 395 cards, 2123 combinations; WIP5 mutable: 395 cards, 873. Scanner flagged respectively 505 versus 148 review candidates; NOT equivalent to 505/148 errors. Historic A1 Verben: 310/310, 1934 accepted combinations with five-per-card patterns in some batches; A2 Verben: 292 cards, 1426 combinations in recorded checkpoint, but current R152 context is nonfinal. Neither A1 nor A2 has been scanned with this new tool in the pilot.

This is a mandatory prospective compatibility overlay, not a rewrite of the immutable full v3.3.6 master prompt or a claim that all historical files have been corrected.
