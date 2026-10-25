> **ACTIVE 2026-10-25 NVV SUCCESSOR (user-approved AI linguistic review)**: Latest editable content is **NOT** the historical October 7 LOCKED file, nor the earlier same-day technical-only TSV package. Current portable WIP: `NVV-STAGE4-2026-10-25-AI-66-REVIEW-22-CARD-REPAIRS-WIP.zip` (SHA-256 `db1af6436b82c0372d2af6349bc3f07c62b2c832ad254966e66466a4cfb48dc1`). Includes 2,492 cards, 9,968 trilingual examples, 66 candidate reviews (**37 KEEP / 22 PATCH / 7 HOLD**) and case82 identity HOLD. Library path `/German-Content-Production-Kit/Checkpoints/NVV-STAGE4-2026-10-25-AI-66-REVIEW-22-CARD-REPAIRS-WIP.zip`; [Google Drive](https://drive.google.com/file/d/1--w_FDoDVAYor0v4nGoSSuL4Fbui9lq1/view). The `nvv-production/Workspaces/nomen-verb-verbindungen/08-lean-working/CURRENT.json` and `NVV-2026-10-25-AI-66-REVIEW-MILESTONE.json` take precedence for this active successor. **No external human specialist signoff required** per `main/LINGUISTIC-QA-AUTHORITY-POLICY.json`; full Stage4 / Stage5/6/7 are NOT FINAL. All older reports/releases remain immutable historical references.

# German Content Production Kit — NVV workstream branch

> Branch-local workstream source/receipts. **Global framework, policies and current runtime authority are on `main`**. Do not use historical branch metadata to override newer verified portable artifacts.

## ACTIVE — current NVV successor (2026-10-25)

**Newer editable NVV successor is ACTIVE, Stage4 IN PROGRESS, not FINAL and not content-locked.** Do not select the historical 2026-10-07 LOCKED archive as the latest working content.

- Source: 2,476 occurrences; 2,492 stable card identities; 9,968 DE/FA/EN example triples.
- Current working canonical SHA-256: `214c7cab33de609826755bcaf0eecc118e226eeaf84be7ce39fbef724bc8ad9f`.
- Explicit **versioned** 2026-10-25 TSV successor SHA-256: `150a9a10be10ccfa0f6f78c8dcd50a8c0a63c9cdfed46776eadbe705def2eb0c`. This is NOT a same-byte recovery of the older TSV whose SHA was `3a963cbf...`.
- Portable technical successor: `NVV-STAGE4-2026-10-25-VERSIONED-TSV-SUCCESSOR-WIP.zip`, SHA-256 `9bd2fe659ee39c883e601f05e30c8b8f2a0816f47c32b0fbc6acbadae651bb12`, stored in Google Drive and ChatGPT Library.
- Technical QA: 2,492-card canonical/TSV parity PASS; **linguistic Stage4 and Stage5/6/7 final acceptance NOT YET PASS**.
- Latest technical receipt: `Workspaces/nomen-verb-verbindungen/08-lean-working/NVV-2026-10-25-VERSIONED-TSV-SUCCESSOR-TECHNICAL-QA.json` on `nvv-production`.
- The runtime target must be resolved dynamically from **main** CURRENT runtime at integration time; never pin to an older v465/v485 merely because a historical report mentions it.

## ACTIVE — linguistic review authority (user-approved 2026-10-25)

**No external qualified-human linguist, independent third-party specialist, signed reviewer identity, or external expert approval is mandatory to progress or close NvV Stage4.**

The higher-priority cross-project authority is **`main/LINGUISTIC-QA-AUTHORITY-POLICY.json`**, invoked through **`main/PROJECT-BOOTSTRAP.md`** and **`main/Prompt/START-PROMPT-v3.3.6.md`**. This rule covers all content workstreams, not only NVV.

- ChatGPT does fully documented, source-grounded linguistic QA and a separated adversarial second pass; the user adjudicates consequential questions where needed. No routine signature/questionnaire.
- Explicitly disposition all inherited 66 NVV legacy specialist-review items, plus the distinct remaining case, by **AI review with evidence**, preserving original issues and stable IDs. Do not automatically mark any unresolved issue PASS.
- Missing outside-human signoff **is no longer a blocker by itself**. Defects, absent source evidence, uncompleted source/semantic audit and failed deterministic QA may still block.
- **Never label AI review as independent external human approval.**
- `Stage4 PASS` requires actually passing the re-audit + technical gates; policy change alone is not `Stage4 PASS`.
- Older immutable reports, frozen audit baselines, original source, LOCKED release and prior receipts remain unchanged. A historical term such as `QUALIFIED_EXPERT_HOLD` is a *legacy queue label*, not a current staff requirement.

Workstream-local policy/authority handoff: `Workspaces/nomen-verb-verbindungen/08-lean-working/REVIEW-AUTHORITY-CURRENT.json`.

## Historical LOCKED predecessor — not current successor

The standalone NVV **2026-10-07 predecessor** remains Stage7 content-locked and immutable:

- Release: `German-Flashcards-Pro-v465-R99-Nomen-Verb-Verbindungen-v3.3.6-LOCKED-CONTENT.zip`
- SHA-256: `917ba9561245deea32cc3be1095af0185858d3d45d8eb7ff40e4a7b4c361771f`
- Historical Stage6/7 acceptance is scoped to the *predecessor*, not the 2026-10-25 working successor.

## Resume — order of authority

1. `main/PROJECT-BOOTSTRAP.md`
2. `main/LINGUISTIC-QA-AUTHORITY-POLICY.json` and `main/Prompt/START-PROMPT-v3.3.6.md`
3. `main/PROJECT-STATE.json`, and `main/WORKSTREAM-RESUME-CURRENTNESS-POLICY.json`
4. This README and `Workspaces/nomen-verb-verbindungen/08-lean-working/REVIEW-AUTHORITY-CURRENT.json`
5. `Workspaces/nomen-verb-verbindungen/08-lean-working/CURRENT.json`; `07-independent-audit/LATEST.json`; latest accepted successor portable ZIP/technical receipt (newer authority outranks stale branch metadata)
6. `Workspaces/nomen-verb-verbindungen/CHECKPOINT.json` for historical LOCKED lineage; `00-source/SOURCE-MANIFEST.json` for source
7. Actual Stage4 AI linguistic disposition of all open cases; then Stage5/6/7 as independently required.

Do not rewrite or delete original older reports merely to remove old reviewer wording. The active override supersedes it, without falsifying history.
