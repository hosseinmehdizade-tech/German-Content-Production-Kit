# 250 Verben mit Präpositionen — Kombinationen successor

Status: **Stage3B Batch08 PASS** under German Content Production Kit v3.3.6.

This workstream is an explicit semantic successor to the immutable 292-card LOCKED release. It adopts `Prompt/LEXICAL-KOMBINATIONEN-ENRICHMENT-POLICY-v1.0.0.md` without mutating the historical parent.

Current coverage: **160/292 cards**, **696 accepted Kombinationen**, **132 cards remaining**.

Batch08 covers `usrin-vmp-u-0141..0160`. It changes only `details` + `custom_fields` on those 20 targets; the other **272/272** raw TSV lines are byte-identical to Batch07 ACCEPTED, and prior Batch01–07 rows **140/140** remain byte-identical. Canonical identity, examples, relations and source lineage remain unchanged.

Batch08: **20 cards / 84 accepted items / 84 FA + EN translations / 20/20 one visible Kombinationen section / QA PASS**. Provenance is parent-grounded only: **79 parent-example items + 5 parent-canonical-relation items + 0 curated items**.

One parent example on `usrin-vmp-u-0147` — `Wir sind über den Unfall informiert.` — is explicitly excluded from the Kombinationen projection because it realizes `informiert sein über`, not the reflexive target `sich informieren über`. The parent example itself remains untouched.

Learner-facing rule: exactly one section titled **Kombinationen**. Legacy visible Rektion/Kollokationen/NVV entries are preserved in backend metadata instead of separate visible subsections.

Next: Batch09 `usrin-vmp-u-0161..usrin-vmp-u-0180`.
