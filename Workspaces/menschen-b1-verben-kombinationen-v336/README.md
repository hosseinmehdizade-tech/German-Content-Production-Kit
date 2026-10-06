# Menschen B1 Verben — Kombinationen successor (v3.3.6)

Current state: **Stage4 INDEPENDENT REAUDIT FAIL — 9 Kombinationen evidence-binding defects require bounded provenance repair**.

Immutable root parent: `Menschen-B1-Verben-v3.3.6-Repair2-GFP-v456-RELOCKED.zip`  
SHA-256: `588f0ef9ef81668383c7186936472584f1063bccb5a888c8ff75a9526343261a`

This successor retrofits the active lexical **Kombinationen** learner-facing contract without mutating the accepted Repair2 canonical authority.

Completed cumulative batches:
- Batch01 `mb1m-lu-0001..mb1m-lu-0020`: 20 active cards / 98 items.
- Batch02 `mb1m-lu-0021..mb1m-lu-0040`: 17 active cards / 80 items.
- Batch03 `mb1m-lu-0041..mb1m-lu-0060`: 17 active cards / 83 items.
- Batch04 `mb1m-lu-0061..mb1m-lu-0080`: 18 active cards / 90 items.
- Batch05 `mb1m-lu-0081..mb1m-lu-0100`: 19 active cards / 98 items.
- Batch06 `mb1m-lu-0101..mb1m-lu-0120`: 17 active cards / 82 items.
- Batch07 `mb1m-lu-0121..mb1m-lu-0140`: 19 active cards / 99 items.
- Batch08 `mb1m-lu-0141..mb1m-lu-0160`: 16 active cards / 91 items.
- Batch09 `mb1m-lu-0161..mb1m-lu-0180`: 16 active cards / 95 items.
- Batch10 `mb1m-lu-0181..mb1m-lu-0200`: 15 active cards / 84 items.
- Batch11 `mb1m-lu-0201..mb1m-lu-0220`: 15 active cards / 79 items.
- Batch12 `mb1m-lu-0221..mb1m-lu-0240`: 17 active cards / 85 items.
- Batch13 `mb1m-lu-0241..mb1m-lu-0260`: 15 active cards / 86 items; absent IDs 0245, 0250, 0252, 0256, 0259.
- Batch14 `mb1m-lu-0261..mb1m-lu-0280`: 15 active cards / 79 items; absent IDs 0271, 0273, 0274, 0278, 0279.
- Batch15 `mb1m-lu-0281..mb1m-lu-0300`: 16 active cards / 86 items; absent IDs 0284, 0298, 0299, 0300.
- Batch16 `mb1m-lu-0301..mb1m-lu-0320`: 15 active cards / 84 items; absent IDs 0305, 0310, 0313, 0315, 0317.
- Batch17 `mb1m-lu-0321..mb1m-lu-0340`: 18 active cards / 95 items; absent IDs 0334, 0339.
- Batch18 `mb1m-lu-0341..mb1m-lu-0360`: 15 active cards / 85 items; absent IDs 0342, 0343, 0348, 0351, 0354.
- Batch19 `mb1m-lu-0361..mb1m-lu-0380`: 16 active cards / 89 items; absent IDs 0364, 0370, 0375, 0377.
- Batch20 `mb1m-lu-0381..mb1m-lu-0400`: 13 active cards / 68 items; absent IDs 0381, 0384, 0386, 0387, 0389, 0390, 0392.
- Batch21 `mb1m-lu-0401..mb1m-lu-0420`: 16 active cards / 92 items; absent IDs 0403, 0406, 0407, 0419.
- Batch22 `mb1m-lu-0421..mb1m-lu-0440`: 15 active cards / 89 items; absent IDs 0421, 0424, 0427, 0433, 0437.
- Batch23 `mb1m-lu-0441..mb1m-lu-0460`: 18 active cards / 106 items; absent IDs 0442, 0451.
- Batch24 `mb1m-lu-0461..mb1m-lu-0480`: 16 active cards / 94 items; absent IDs 0461, 0467, 0469, 0474.
- Batch25 `mb1m-lu-0481..mb1m-lu-0500`: 1 active card / 6 items; only `mb1m-lu-0481` exists in this nominal range.

Current cumulative coverage: **395/395 cards**, **2123 accepted Kombinationen items**, **0 cards remaining**.

Invariant: exactly one learner-visible `Kombinationen` section on processed cards; no separate visible Rektion/Kollokationen/NVV sections; backend kind/provenance, canonical relations, examples and source lineage remain preserved. No hard density quota is used.

Latest accepted artifact: `Menschen-B1-Verben-v3.3.6-Kombinationen-Stage3C-DISPOSITION-CLOSURE-ACCEPTED.zip`  
SHA-256: `4715a43019c0e99d91f0f256938655e7dd2063ec172b61951c100976da5bedc7`

Library rematerialization of the ACCEPTED artifact is byte-identical and SHA-256 exact.

Stage3C closure: **6552/6552 dimension cells final; 5105 VERIFIED_PRESENT; 1447 CLOSED_NO_FORCE; 0 unresolved.** Kombinationen overlay: **395/395 VERIFIED_PRESENT, 2123 accepted items**. The Stage3C TSV is byte-identical to Batch25.

Next: **bounded provenance-only repair of the 9 Stage4 findings**, then Stage3C reclosure and Stage4 rerun. Do not start Stage5 yet.

Stage3B completion gate: **395/395 cards have exactly one learner-visible `Kombinationen`; 0/395 retain separate visible Rektion/Kollokationen/NVV; all 395 dispositions are `VERIFIED_PRESENT`.**


Official v3.3.6 Stage3C validators: enrichment completeness **PASS** (395 targets / 6552 cells / 0 unresolved); candidate ledger **PASS** (6114 candidates / 0 deferred at closure).


## Stage4 independent reaudit finding

Stage4 recomputed the exact Stage3C authority independently. Structural/source/identity/completeness validators PASS, but the semantic evidence-binding gate found **9 incorrect parent relation references** on otherwise-correct Kombinationen learner text:

- mb1m-lu-0007: relation mb1m-r1p2-b0001-013 -> mb1m-r1p2-b0001-014
- mb1m-lu-0008: relation mb1m-r1p2-b0001-015 -> mb1m-r1p2-b0001-017
- mb1m-lu-0009: relation mb1m-r1p2-b0001-018 -> mb1m-r1p2-b0001-021
- mb1m-lu-0010: relation mb1m-r1p2-b0001-021 -> mb1m-r1p2-b0001-024
- mb1m-lu-0011: relation mb1m-r1p2-b0001-024 -> mb1m-r1p2-b0001-027
- mb1m-lu-0012: relation mb1m-r1p2-b0001-027 -> mb1m-r1p2-b0001-030
- mb1m-lu-0013: relation mb1m-r1p2-b0001-030 -> mb1m-r1p2-b0001-032
- mb1m-lu-0014 item 1: relation mb1m-r1p2-b0001-033 -> mb1m-r1p2-b0001-035
- mb1m-lu-0014 item 2: relation mb1m-r1p2-b0001-032 -> mb1m-r1p2-b0001-034

No DE/FA/EN learner text or immutable canonical relation needs to change. Stage5 is blocked until these 9 evidence_refs and their matching Stage3C candidate-ledger refs are repaired, Stage3C is reclosed on the new exact hashes, and Stage4 is rerun.

## Stage3C Repair1 reclosure

Status: **PASS — provenance-only repair/reclosure**.

The independent Stage4 audit found 9 wrong neighboring canonical relation bindings. Repair1 changes only those 9 Kombinationen evidence refs across 8 cards and mirrors the same 9 refs in the accepted candidate ledger. Learner-visible DE/FA/EN text, details, canonical objects/relations/examples, IDs, order, lessons and decks are unchanged. 387/387 non-target TSV rows remain byte-identical to the previous Stage3C.

Post-repair: **2123/2123 evidence bindings PASS**, **6552/6552 disposition cells FINAL**, **0 unresolved**, official completeness and candidate-ledger closure validators **PASS**.

Latest accepted artifact: `Menschen-B1-Verben-v3.3.6-Kombinationen-Stage3C-Repair1-DISPOSITION-CLOSURE-ACCEPTED.zip`  
SHA-256: `357531af0f4719e4e1db0587dbba1c5e1b85d14e2511bac9ff3cb25f0307dbce`

Next: **rerun Stage4 independently from the exact Repair1 ACCEPTED bytes**. Stage5 remains blocked until that Stage4 rerun passes.
