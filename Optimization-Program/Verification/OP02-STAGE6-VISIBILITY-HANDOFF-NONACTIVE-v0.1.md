# OP-02 — Stage5 accepted items → Stage6 visibility evidence handoff (NONACTIVE)

**Scope:** Continuous Optimization / read-only reviewer preparation. **Not an activated Stage5/Stage6 gate, a content correction, a UI change, an authorized import, or a release.** The generator's successful queue creation still **returns exit code 2** because all generated review findings remain unresolved; a CI step must never equate a generated queue with Stage6 PASS.

## Grounded original input

- Original Menschen A1 V22 Stage5 clean-content ZIP, exact whole-archive SHA256 `74cdbf5b6d0121421fac8235124e738929b9764f3696db532cc54f9509f5757d`.
- The independent in-archive source-to-view scanner validates 2,997 rows / 23 Universal columns and the exact per-card accepted-combination ledger.
- Source ledger 2,180 / physical bilingual `details.Kombinationen` 2,075. Thus **105 unresolved items** across 66 cards: 57 on 39 cards require the exact-current runtime auto-bridge proof; 48 on 27 cards have a partial pre-existing `Kombinationen` section and require source-bound placement + runtime review. These are not retroactive deletion findings or Stage5 automatic failures.
- The 105-entry original V22 queue is kept in the user Library under `/German-Content-Production-Kit/Optimization-Program/Stage45-A1-V21-V22/`. This proposal does not commit raw learner text into the Git proposal branch.

## Reproduction / trust boundary

```
python Verification/build_op02_visibility_review_queue.py \
  --zip <EXACT_ORIGINAL_V22_STAGE5_ZIP> \
  --sha256 74cdbf5b6d0121421fac8235124e738929b9764f3696db532cc54f9509f5757d \
  --output <NEW_NONEXISTING_REVIEW_QUEUE.json>
```

The generator reopens and validates the **original ZIP**, not a supplied saved report; enforces whole-ZIP hash, bounded/path-safe archive member inventory and CRC, source ledger↔TSV identities/order/DE/FA/EN, physical bilingual display and monotonic order. It derives a SHA256 per missing source unit from exact card ID, lesson, original ordinal and full accepted item. Missing source IDs remain `null`; no fabricated ID or reviewer signature. It creates output with exclusive-write semantics and rejects overwriting existing outputs or source ZIP.

Each unit is PENDING, with `runtime_evidence`, `source_semantic_evidence`, `independent_adversarial_evidence` set to `null`; `auto_edit_authorized=false`. In a future *separate authorized process*, a reviewer may add evidence to a distinct immutable source-bound receipt after checking real originals and exact CURRENT runtime. **Editing the generated queue to write “PASS” is not valid approval.** Nothing here validates a free-form approval string or upgrades official Stage5/6/7 states.

## Required independent checkpoints before moving further

1. Resolve the newest official `German-Flashcards-Pro/RUNTIME-AUTHORITY-PIN.json` **at test time**. It was v505-R141 nonfinal when this shadow audit was produced, but may advance. Never substitute historical Git `01-App` v486 as CURRENT. Exact CURRENT ZIP and `index.html` SHA256 readback required.
2. Import original V22 TSV into an isolated exact-CURRENT browser profile (no user data mutation), verify persisted authority and DOM in Study and Quick, and record whether each of the 105 accepted items appears with the intended DE/FA and in which section. English/source metadata visibility is a separate didactic decision; no invention.
3. Have a source-grounded semantic review determine where combinations versus related words/collocations belong, with independently verified adversarial evidence. **Do not automatically insert 48 into Details**: items can overlap `Verwandte Wörter` or `Kollokationen`, and duplicates would be user-visible.
4. Check exact source hashes, unit hashes and all dispositions. Only a new explicit **reviewed and source/current-runtime-bound** contract may reduce the unresolved count; the immutable generated PENDING-only queue is not such a contract.
5. Execute formal Stage5 anti-bypass with documented exceptions, then independently Stage6 and Stage7; never infer global PASS from synthetic CI or document presence.

**Active program remains** OP-01/OP-02. OP-01 writer scope is `DENY_ALL`; Git branch/issuer protection and independent trust root are unresolved. Keep this artifact and PR **DRAFT/NONACTIVE**, preserve original user content, UI and workstream LATEST.