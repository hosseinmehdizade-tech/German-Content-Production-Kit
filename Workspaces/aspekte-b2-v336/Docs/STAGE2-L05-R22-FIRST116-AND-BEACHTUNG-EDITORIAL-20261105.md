# Aspekte B2 R22 — first half of Lesson05 + Beachtung review

**2026-11-05. Status: Stage1 PASS, Stage2 IN_PROGRESS_NOT_APPROVED, Stage3–7 NOT_STARTED, zero cards.** Only user-supplied B2 CSV supplies lexical inventory; privacy-sanitized SHA256 `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`. The private original raw CSV SHA256 is historical, not rehashed.

## Lesson05 — Wer Wissen schafft, macht Wissenschaft
Source 231 immutable original rows #2187–2417, split 116 + 115. **116 individually annotated German–Persian firstpass reviews #2187–2302**: 89 KEEP_USAGE, 25 FIX/refinement, **two HOLD #2275/#2302**. The 115 rows #2303–2417 remain pending. All source German, Persian, original examples, audio, tags and ordinals unchanged. **Original source examples:** 25 cells with text across L05, 12 in reviewed first half; no new examples in this checkpoint. **0/231 second-method AI-reviewed**, no human signoff.

Key source-specific candidate corrections:
- #2195 `das Quiz`: source `-` correctly permits plural `die Quiz`; colloquial `Quizze` also exists. https://www.duden.de/deklination/substantive/Quiz
- #2199 `an jemandes Lippen hängen`: idiom means listening with rapt attention, not literally hanging off the lips. https://www.duden.de/rechtschreibung/zuhoeren
- #2200 `die Weiche`: railway switch vs animal/human flank have separate senses; original source example `die Weichen stellen` refers to railway sense. https://www.duden.de/rechtschreibung/Weiche_Technik
- #2202 `absolvieren` means to complete a course/test/training; can lead to a degree, not semantically identical with graduating.
- #2211 `heranführen` is separable in finite main clauses, `führte heran`; `an + Akk.` and target object.
- #2223 `sich qualifizieren` to qualify, versus transitive `jemanden qualifizieren` and `als etwas qualifizieren` to classify; source does not distinguish. https://www.duden.de/rechtschreibung/qualifizieren
- #2254 `schwindeln` colloquial telling minor untruths versus impersonal `es schwindelt mir` for dizziness. https://www.duden.de/rechtschreibung/schwindeln
- #2257 `übersehen`: ordinary unseparable `hat übersehen` (overlook, oversee), distinct from colloquial *separable reflexive* `hat sich übergesehen` (tired of seeing something). https://www.duden.de/rechtschreibung/uebersehen_uebersehen and https://www.duden.de/rechtschreibung/uebersehen_uebergesehen
- #2272 `Aufbau`: building/structure in abstract sense generally singular-only; a physical superstructure has plural `Aufbauten`. https://www.duden.de/rechtschreibung/Aufbau
- **#2275 HOLD:** source `Strom ist heute für eine Stunde ausgefallen.` is a full sentence as headword. Preserve one sentence unit with original source ID, never fabricate new source lemma.
- **#2302 HOLD:** original `radioaktiv` duplicates the next segment's #2303 exactly DE+FA. Preserve both source ordinals and do not suppress/delete or generate duplicate cards without explicit pedagogical decision.

## L04 editorial amendment
#2184 original `die Beachtung, -en` retained verbatim; earlier R21 morphology HOLD remains historical and R22 proposes learner display `die Beachtung (kein Pl.)` based on Duden's singular-only ordinary dictionary record https://www.duden.de/rechtschreibung/Beachtung . There are still four *unexecuted* L04 teaching-unit plans [2020,2024,2078,2091]. This is a candidate content correction, **not** release approval.

## Verifiable packaging and gates
Portable B2-only ZIP `/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Checkpoints/Aspekte-B2-STAGE2-L05-R22-FIRST116-BEACHTUNG-RESOLVED-20261105.zip`; SHA256 `6c6a883207cb69a1aa33bb32b5106f53f5e0ac55a085bdd1f30d3d6d499f9e64`, 2221614 bytes, 14 ZIP members and 13 verified member hashes, stable Library ID `libfile_7733562d694c8191bf535afa29b76ba7`; exact Library downloaded bytes match local. In fresh isolated extraction, builder reproduced every file exactly (14/14) and independent test passed 3,655 structural assertions with 15 deliberately corrupted fixtures rejected. CRC and hashes pass. **These establish source preservation, not German/Persian linguistic accuracy or quality of learner-facing examples.**

L01 still has five actual prior accepted/imported card identity gates, L02 requires bilingual example quality acceptance, L03 has three unexecuted source shape plans, and L04 is not released. No cross-workspace/source/app/SRS mutation; Stage2 remains NOT_APPROVED.
