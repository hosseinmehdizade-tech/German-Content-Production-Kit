# Aspekte B2 — Kapitel 1 R35: 17 evidence-based HOLD dispositions, 7 display patches

**Date:** 2026-11-06. **Scope:** only B2 dedicated Library and GitHub workspace. **Release:** NOT APPROVED; **importable cards:** 0.

## What changed
- Read existing R34 full 160-row working CSV, source user-only sanitized CSV and R34 hold decision matrix.
- Independently cross-checked selected grammatical/semantic distinctions against public German lexical evidence; sources are used only for **interpretation, never to change lexical inventory**.
- **7 display-only proposed fixes** added to a NEW non-importable copy, source ordinals **1586, 1588, 1610, 1647, 1660, 1675, 1693**. No example sentences altered in R35.
- **17 HOLDs still OPEN**: each has a row-specific evidence type, reason, and next gate. Some internal meaning ambiguities are documented; external proof and final signoff remain missing.
- Original source headword/FA meaning/original examples preserved exactly for all 160 rows; 320 German draft sentences + 320 Persian draft translations unchanged.
- The exact duplicate #1640/#1641 remains two immutable source rows, with only **proposed** canonical+alias mapping. No merge.

## Concrete bilingual decisions (editorial, not final release)
| Source | German editorial learner-unit proposal | Persian editorial meaning | Status |
|---|---|---|---|
| #1586 | vielsprachig [Adj.] / die Mehrsprachigkeit [Nomen] | چندزبانه / چندزبانگی | two typed units proposed; split not executed |
| #1588 | die Vielsprachigkeit; context of language diversity | حضور یا تنوع زبان‌ها؛ چندزبانگی | synonym link to Mehrsprachigkeit unresolved |
| #1610 | in mehrere Bereiche **geteilt** = in + **Akk.**; separate idiom geteilter Meinung sein | به بخش‌ها تقسیم‌شده؛ اختلاف‌نظر داشتن (عبارت مستقل) | source says in+D, unresolved original discrepancy |
| #1647 | Ausländerquote: share/percentage **or** prescribed quota | سهم/درصد اتباع خارجی **یا** سهمیهٔ مقرر | example-specific sense distinction retained |
| #1660 | gekommen = Partizip II of kommen, ist gekommen | آمده/رسیده؛ شکل سوم فعل kommen | not automatic new standalone lemma |
| #1675 | (sich) einig sein; mit jdm. über etw. einig sein; in einer Frage einig sein | هم‌عقیده بودن / اتفاق‌نظر داشتن | typed constructions, no blanket Rektion rule |
| #1693 | der Juryvorsitz = office/leadership, not jury-chair person | ریاست هیئت داوران (سمت)، نه شخص رئیس | source Persian wrong sense retained in source column |

## Critical external card identity remains unproven
- #1575 ständig: B1 candidate `mb1m-lu-1040` exact but NONIMPORT.
- #1630 intolerant: B1 candidate `mb1m-lu-2779` exact but NONIMPORT.
- #1609 entscheidend: B1 contains expression `im Voraus entscheidend`, not identical standalone unit.
- #1671 zerreißen: earlier B1+ **source** overlap only, not approved learner card.
- #1556 abenteuerlich, #1616 Art, #1697 Kinokasse, plus others still have no independently verified earlier accepted card identity.

## References (German meaning support, not source vocabulary)
- https://www.duden.de/rechtschreibung/vielsprachig
- https://www.duden.de/rechtschreibung/Mehrsprachigkeit
- https://www.duden.de/rechtschreibung/Multilingualismus
- https://www.duden.de/rechtschreibung/teilen
- https://www.duden.de/rechtschreibung/Quote
- https://www.duden.de/rechtschreibung/gekommen
- https://www.duden.de/rechtschreibung/einig
- https://www.duden.de/rechtschreibung/Vorsitzender

## QA and remaining work
- Deterministic source-integrity for all 160 rows: PASS. Source example strings preserved, source metadata excluded from export, no blank generated examples, all `importable=FALSE`, `stage3_card_created=FALSE`.
- Targeted lexical-reference check: **7 display distinctions**, not a full independent bilingual QA.
- Exactly **17** release gates remain OPEN; no source row dropped, no suppression/merger, no card published.
- **Stage2 approval FALSE; Stage3–7 NOT STARTED**. Next decisive work: full independent German–Persian semantic QA of 160 rows and direct accepted-card proof/split/merge signoff.