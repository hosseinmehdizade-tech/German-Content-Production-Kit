# Aber Hallo Selected Pages v3.3.6 — Stage7 Independent Final Audit

**Verdict: PASS / CONTENT LOCKED / exact v467-R101 bytes preserved.**

Final artifact: `German-Flashcards-Pro-v467-R101-Aber-Hallo-v3.3.6-LOCKED-CONTENT.zip`  
SHA-256: `28c255cf898ca8e4bbea346c396c966d11a8dc50be514dedc457474dcf272104`  
Size: 5,203,239 bytes

- Stage6 candidate and Stage7 final archive are byte-identical.
- ZIP CRC PASS; 366 members; no duplicate members.
- Root `SHA256SUMS.txt`: 365/365 PASS.
- Runtime-control consistency PASS; strict v467 version guard PASS; release hygiene PASS.
- 787 lexical cards remain unchanged: 647 verbs + 140 adjectives.
- Grammar baseline 168 units / 346 exercises preserved; one tested Aber Hallo unit `ahl-lu-0001` is added, yielding 169 units / 346 exercises.
- Grammar Node and Chromium extension tests PASS; Pomodoro regression PASS; shell cohort PASS; runtime JS and inline-script syntax PASS.
- No CSS/layout redesign; visible change remains version label only.
- Library rematerialization is exact SHA-256 + byte-compare PASS.
- Embedded package CANDIDATE controls remain immutable by project policy; external Stage7 sidecar owns overall content finality.

## Remaining boundary

Aber Hallo content/package work is complete. The app repository still has a pending full coherent v467 `01-App` source mirror, so do not call the runtime Git-backed fully verified until that separate durability step is complete.
