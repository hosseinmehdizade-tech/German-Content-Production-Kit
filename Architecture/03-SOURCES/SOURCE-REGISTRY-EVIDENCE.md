# Source Registry Evidence — v3.1.3

Date: 2026-08-25

این فایل Evidence مربوط به **انتخاب/ثبت Registry** است، نه Evidence تأیید محتوای یک Learning Unit. حضور یک Source در این فایل هیچ کارت آینده‌ای را verified نمی‌کند.

## Official pages checked in this hardening run

- Duden Online Wörterbuch — `https://www.duden.de/woerterbuch` — German meaning, grammar, usage.
- grammis / IDS Mannheim — `https://grammis.ids-mannheim.de/` — German grammar authority.
- Langenscheidt Deutsch–Englisch — `https://de.langenscheidt.com/deutsch-englisch/` — bilingual DE↔EN.
- PONS Deutsch–Englisch — `https://de.pons.com/übersetzung/deutsch-englisch` — bilingual DE↔EN.
- Collins German–English — `https://www.collinsdictionary.com/dictionary/german-english` — bilingual DE↔EN.
- Cambridge Deutsch–Englisch — `https://dictionary.cambridge.org/dictionary/german-english/` — bilingual DE↔EN learner reference.
- Oxford Learner’s Dictionaries browse — `https://www.oxfordlearnersdictionaries.com/browse/` — includes German–English / English–German dictionaries.
- Langenscheidt Deutsch–Persisch — `https://de.langenscheidt.com/deutsch-persisch/` — bilingual DE↔FA.
- Wort.ir — `https://www.wort.ir/` — German–Persian bilingual dictionary.
- B-Amooz — `https://dic.b-amooz.com/de/dictionary` / project pages — German–Persian learning dictionary.
- PONS Persisch–Deutsch / Deutsch–Persisch dictionaries — official PONS product pages.

## DWDS note
DWDS remains an approved German monolingual/corpus source from the established project policy. Direct page retrieval in this hardening run was blocked by robots.txt, so this run does **not** claim a fresh web-access verification of DWDS itself. Future content runs must record actual access status honestly (`verified`, `blocked`, `not_found`, `unverified`).

## Independence note
Collins states that its German bilingual dictionary has a long collaboration lineage with Langenscheidt. For conservative two-source checks, `collins_de_en` and `langenscheidt_de_en` therefore share an `independence_group`; PONS, Cambridge and Oxford remain separate groups.
