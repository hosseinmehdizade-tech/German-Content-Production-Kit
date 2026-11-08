# Lesen R20 — scoped p06-s02 editorial delta, LES-PRES-021–030 (2026-11-08)

**Status: LOCAL CANDIDATE / SCOPED QA PASS, NOT CURRENT, NOT FINAL.** Git report is a durable text receipt; Library uploads of new bytes were attempted but failed with `container_session_unavailable`. Do not treat this as Library-saved content or Stage4/6/7 acceptance.

## Exact immediate parent
- R19 Master SHA256 `1a1fa9be4f61dd34a04264050cf12531168cd75920517f3d9315780b11acf4ff`.
- R19 v505 Runtime SHA256 `365b774d8478bd98f6e111cafa66677abc1688cad76674102f6061109825254f`.
- Original curated CURRENT ZIP v1.3.0 SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` remains unchanged.

## Ten exact new German p06-s02 sentences
- 021 — **Ehemaligenvereine an Hochschulen:** Alumni-Vereine sollten Mentoring-Angebote allen Interessierten zugänglich machen, damit nicht nur gut vernetzte Absolventen davon profitieren.
- 022 — **Werken und Handarbeit in der Schule:** Bei der Auswahl von Schulprojekten sollte man deshalb von klaren Lernzielen ausgehen.
- 023 — **Weiterbildung nach Studium oder Ausbildung:** Die Verantwortung für berufliche Weiterbildung sollte deshalb klar und fair zwischen Unternehmen und Beschäftigten verteilt werden.
- 024 — **Zu Hause oder in der Bibliothek lernen?:** Entscheidend ist, den Lernort bewusst zu wählen, statt einfach der Gewohnheit zu folgen.
- 025 — **Gute Organisation beim Lernen und Studieren:** Ein guter Plan sollte dem Lernenden dienen und nicht umgekehrt.
- 026 — **Können Verfilmungen Bücher ersetzen?:** Buch und Verfilmung sollten deshalb als Ergänzung und nicht als Konkurrenz betrachtet werden.
- 027 — **Wie können Eltern Kinder auf ein Studium vorbereiten?:** Der verständliche Wunsch nach Sicherheit darf jedoch nicht dazu führen, dass Eltern die Studienwahl ihrer Kinder kontrollieren.
- 028 — **Herausforderungen beim Fremdsprachenlernen:** Eine Sprache entwickelt sich, wenn sie aktiv benutzt wird, und nicht allein durch das Lernen von Regeln.
- 029 — **Sollte man ältere Literaturtexte sprachlich an heutige Normen anpassen?:** Änderungen sollten deshalb transparent gemacht und nachvollziehbar begründet werden.
- 030 — **Muss man an einer bekannten Hochschule studieren?:** Die Studienwahl sollte sich deshalb an der Passung des Studiengangs und den tatsächlichen Studienbedingungen orientieren, nicht allein am Namen der Hochschule.

## Translation deltas
Only the final FA/EN sentences for 021 and 027 were changed; eight already semantic-aligned FA/EN pairs were preserved exactly:
- 021 FA: انجمن‌های فارغ‌التحصیلان باید فرصت‌های راهنمایی را برای همهٔ علاقه‌مندان فراهم کنند تا فقط فارغ‌التحصیلان دارای ارتباطات قوی از آن سود نبرند.
- 021 EN: Alumni associations should make mentoring accessible to everyone interested, so that well-connected graduates are not the only ones who benefit.
- 027 FA: با این حال، خواستِ قابل‌درکِ والدین برای اطمینان از آینده نباید باعث شود که انتخاب رشتهٔ فرزندشان را کنترل کنند.
- 027 EN: However, parents’ understandable wish for security must not lead them to control their children’s choice of degree program.

Old generic p06-s02 sentence was removed from each of 021–030, with all other sections and p06-s01 unchanged. 58 untouched source lesson objects and their v505 runtime entries remain exact. All 340 questions, 350 vocabulary entries, 669 curated grammar IDs retained. 40 prior p06-s02 grammar markers retired and exactly ten manually attested fulltext spans created (do not imply native nine-lens rerun); 4011 → 3981 exact grammar occurrences, 48 → 38 repeated generic p06-s02.

## QA (executed on locally materialized exact sources)
- Independent source/runtime checks: **18,701 / 18,701 PASS**, zero errors; **9/9** adversarial structural mutations rejected.
- Real current v505 `reading-content-import-v38.js`, SHA256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`: isolated Node-VM validator **PASS, zero warnings**, **10/10** malformed inputs rejected; in-memory projection **68 units / 340 exercises**.
- New content SHA256 `a9a440f184bc9d771e7820b066c6097ab7e5fea62d41d283266bac3ba7cefa98` (6,064,310 bytes).
- New runtime SHA256 `ac8acd6b7dec495451751d8e12032c034a39eea3819065f7d9cc198abe38b8b2` (6,510,760 bytes).
- Trilingual grammar delta ledger SHA256 `000bd68cadd4471d4b570e8d187e0eafb8789dbb9b5246758145e149872ee404`.
- QA + handoff JSON SHA256 `af11618a79e0315eeb954a6919c3f7d90ee42ee6aae597412ee7b31a60bd807f`.
- Portable conversation recovery checkpoint ZIP SHA256 `63880331de1723c4bf6ced12bd62f630dde944c92907c81fdd2cd28b227bc448`; ZIP CRC PASS, 10/10 member SHA256, 11 members including checksum list. **Not saved in Library**.

## Required remaining gates
Full independent DE/FA/EN Stage4 **HOLD**, complete native nine-lens grammar **NOT RERUN**, browser/IndexedDB Stage6 **NOT RUN**, Stage7 **NOT RELEASED**. R20 is not a successor CURRENT promotion. The old `Workspaces/lesen-praesentation/CHECKPOINT.json` remains historical Stage1-only pipeline bookkeeping and must not overwrite the owner-local editorial line.

**Next:** if R20 exact ZIP becomes accessible, verify hash and resume lessons 031–040 p06-s02. If unavailable, use independently verified R19 Library parent and these precise source-target deltas for recovery; do not silently treat R19 as the edited R20. Preserve source and existing Library files.
