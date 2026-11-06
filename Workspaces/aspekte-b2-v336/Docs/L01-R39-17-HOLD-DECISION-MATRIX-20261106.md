# Aspekte B2 — Kapitel 1 R39, evidence-based HOLD triage

Date: 2026-11-06. This is a **non-importable source-preserving editorial QA checkpoint**, not an independent bilingual sign-off.

The sole lexical inventory is the user's B2 sanitized CSV (1726 source rows; SHA256 `e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5`). L01 source ordinals 1549–1708 were matched byte-for-byte at the per-cell text level for lemma, original Persian meaning and original example. All 13 original source examples and 320 DE/320 FA drafted example pairs remain. The 160-row R37 CSV and eight-row R38 semantic overlay were NOT changed.

## Decomposition of the 17 unreleased HOLD source rows

| Gate class | Ordinals | Count | What must happen |
| --- | --- | ---: | --- |
| Accepted prior card evidence missing | 1556, 1575, 1609, 1616, 1630, 1671, 1697 | 7 | Find actual **accepted/imported** learner-unit ID and meaning; B1 NONIMPORT candidates or embedded phrase do not justify suppression |
| Learner-unit design still needed | 1586, 1588, 1640, 1641, 1660 | 5 | Decide source-linked typed split, near-synonym, lossless canonical+alias for exact duplicate, and Partizip II linkage |
| Linguistic construction meaning provisionally supported, awaiting full independent QA | 1610, 1611, 1647, 1675, 1693 | 5 | Review full German/Persian examples, cases and intended sense; no automatic release |

- #1586: `vielsprachig` is an adjective and `die Mehrsprachigkeit` a noun, both from a single immutable source row.
- #1640/#1641: exact same original lemma and FA meaning. Propose one learner unit with both source IDs retained; **no merge or deletion was performed**.
- #1660: `gekommen` is the Partizip II of `kommen`, not a separate infinitive.
- #1671: `zerreißen` transitive uses `hat zerrissen`, intransitive `ist zerrissen`; earlier B1+ source is not accepted-card proof.
- #1693: `Juryvorsitz` means the office/role, not the person. The source original is preserved.
- #1611: new **one-row, unapplied** draft front-field correction: `hilfreich (bei + Dat.; für + Akk.)`; the existing R37 examples illustrate both constructions.

Evidence dictionaries were consulted for grammatical and semantic checking **only**, not for adding entries: Duden `vielsprachig`, `Mehrsprachigkeit`, `teilen`, `einig`, `kommen`, `zerreißen`, `Vorsitz` and `Quote`.

## Verified library artifacts (B2 only)

- `Reports/L01-R39-17-HOLD-DECISION-LEDGER.csv`: `libfile_cc0ee0c38ae081919581731a75d923e8`, SHA256 `4ef2c9b345d9a84d5e6ddc370a1be509c39ee323ac37cc769c884cee93868b69`.
- `Current/L01-R39-ONE-REKTION-FRONT-PATCH.csv`: `libfile_036a6c14a604819198c4363a3fdbf93f`, SHA256 `f79e017f34ef3b7ca78b228f1ffddaea10b9388cc6b8d3f7915a5a1c462b874d`.
- `Checkpoints/Aspekte-B2-L01-R39-17-HOLDS-1-REKTION-PATCH-NONIMPORT-20261106.zip`: `libfile_32e93e3c1e1c8191a7f8b90a39c26c5c`, SHA256 `9ba33a21f5e1f99b8acbbfd092b175c1ce0803cd4c7cf5ef79ea86e2a8b06ea4`, 6961 bytes, exact Library byte readback, ZIP CRC and manifest PASS.

The ZIP contains the full decision ledger, one-row patch, report, JSON summary and hashes. Global L05 R25 portable project checkpoint remains unchanged.

**Release gates:** 17 source HOLDs open; historic R38 48 FIXes do not have independent semantic signoff. Stage 2 NOT approved; Stage3–7 NOT started; no importable cards and no source suppressions or merges.
