# OP-02 — Source-only route triage for the 105 unresolved Menschen A1 V22 combinations

**Scope:** NONACTIVE, read-only diagnostic / NOT a Stage5, Stage6, Stage7, runtime or semantic release approval. Original V22 source, learner content, application UI/SRS and official checkpoints remain unchanged.

**Bound exact original:** `Menschen-A1-V22-STAGE5-CLEAN-CONTENT-DELIVERY-NO-IMPORT-20261031.zip` SHA256 `74cdbf5b6d0121421fac8235124e738929b9764f3696db532cc54f9509f5757d`. The existing Stage5→Stage6 queue contains **105 source-hashed PENDING items across 66 cards**, whose accepted-TSV DE/FA/EN parity is independently checked. Source ledger 2180 items; 2075 physical bilingual `Details.Kombinationen` matches.

## Precisely measured, mutually compatible occurrence categories

- **89/105** have an exactly matching German string in *another* non-Kombinationen `details` section (typically `Verwandte Wörter`).
- **24/105** have that German string as an *exact case-sensitive substring* of at least one of these TSV text columns: `front`, `back`, `examples`, `related`, `opposites`, `notes`.
- **13** overlap the above groups; therefore `89 + 24 - 13 = 100` with at least one source-side alternate occurrence.
- **5/105** have no such German-string occurrence in those scanned alternative surfaces. They are the best **source-driven first probes** for exact-CURRENT native Study/Quick, not proven missing or wrong in the app.
- Per field hit occurrences (non-exclusive): `front=10`, `examples=12`, `related=11`, `back=0`, `opposites=0`, `notes=0`.
- Of five source-only-first probes: three `AUTO_BRIDGE_NEEDS_CURRENT_RUNTIME_PROOF`, two `EXISTING_PARTIAL_SECTION_CONFLICT`.

| First probe | Lesson | Exact source-side German | Category |
| --- | --- | --- | --- |
| `ma1m-lu-1662` | A1-L14 | `in jdn. (Akk.) dringen` | Auto bridge candidate |
| `ma1m-lu-1846` | A1-L15 | `jdn. mit dem Auto hinfahren` | Auto bridge candidate |
| `ma1m-lu-1885` | A1-L16 | `aufeinander passen` | Existing partial-section conflict |
| `ma1m-lu-2279` | A1-L18 | `jdm. vorkommen` | Auto bridge candidate |
| `ma1m-lu-2933` | A1-L23 | `nicht mal ein bisschen` | Existing partial-section conflict |

**Strict interpretation:** A source-side occurrence of German text is *not* proof of a bilingual DE/FA displayed combination or correct lesson placement. Conversely, absence of a source-side duplicate is *not* proof of learner-visible absence, because runtime may project `custom_fields.kombinationen_v1`. Case-sensitive substring hits do not imply semantic equivalence or user visibility, and inflection/aliases may escape this bounded scan. `custom_fields` is intentionally excluded from alternative display fields, since it is the backend authority under test and counting it would trivially report 105/105 as present.

## Repeatable nonactive check

`Verification/audit_op02_source_display_routes.py --zip <exact-V22-ZIP> --zip-sha256 74cdb... --queue <exact-PENDING-queue.json> --output <new-report.json>`

The script independently regenerates the queue from the original SHA-pinned archive, rejects any changed queue/source unit hashes or duplicate card source IDs, and writes the report once without overwriting an input. The CLI returns **exit 2** even when it successfully writes a report: no current-runtime Stage6 evidence exists. It never imports cards or modifies the app/UI. Independent synthetic negative/positive checks are in `Verification/tests-v3.3.6/test_op02_source_display_routes.py`; the baseline 33+13 suites remain separate.

**Next acceptance requirement:** Obtain externally authorized exact current runtime ZIP from the current `RUNTIME-AUTHORITY-PIN.json` (currently v505-R141, nonfinal); verify archive and `01-App/index.html` hashes; run isolated native TSV import / Study+Quick actual browser DOM against the 105 source-unit evidence cases; record source-grounded didactic rationale and independent adversarial review for every case, with write-once version-specific evidence. The existing OP-01 writer `DENY_ALL` and all formal Stage5/6/7 gates remain unchanged. Do not force hidden items into `details.Kombinationen` or infer human/AI approval from string searches.