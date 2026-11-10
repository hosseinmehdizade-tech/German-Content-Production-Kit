# Flasch kart — Project Control Dashboard (v1)

**First working artifact:** offline, interactive, **read-only** HTML for the whole Flasch kart portfolio, verified on **2026-11-10**. This is a subcomponent of the EXISTING **Project Control Center**, not a new framework, source-owner registry, app release or user-data operation.

## Open the dashboard

Personal ChatGPT Library folder:
`/Flasch kart/German-Content-Production-Kit/Project-Control/`

- `Flasch-kart-Project-Control-Dashboard-2026-11-10.html` (Library `libfile_910827c1b700819190348a575445a956`; SHA256 `ae1dc49c35c3e4eca4504deca0c48e9be4130b765e079cc5a0dea9c9cd3d2c44`) — open directly in Chrome/Edge/Firefox.
- `Flasch-kart-Project-Control-Dashboard-v1.zip` (Library `libfile_af9a5ea3e6a0819185bb20f489c8c29a`; SHA256 `4eccdc48b8d94ef13575f3916b07f40303a1dbd633dda788065507d324577c9f`) — one portable recovery package.
- `Flasch-kart-Project-Control-Snapshot-20261110.json` (Library `libfile_e68fa1001da481919f603cae0645643b`; SHA256 `cc0ac7e2c021a950c19599fa913b6738d8363a336d5e21c6bcc0570e203d61f4`) — inspectable machine snapshot.

Verified **exact remote Library re-materialization/byte parity for all three**; Chromium headless smoke exercised all 25 cards, search, status filtering, details, dark/light switching and mobile 390px no horizontal overflow. No page errors. It is a browser-friendly offline HTML, **NOT** a deployed web service or live GitHub API integration.

## Scope

- **21** existing canonical content families from [canonical router](../CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json), plus **4** views (app desktop, GFM mobile, Deep Audit and Optimization).
- **9** entries with accepted *content* baseline, **3** in-progress, **6** needing action, **7** unverified/no adequate source-owner status.
- Each project card has status, dated evidence, blocker, next action, direct GitHub owner/issue link and a copyable cross-chat continuation prompt.
- Local filter, search, date sorting, dark/light toggle and JSON export.
- Sunday 18:00 Europe/Berlin reporting automation exists independently. It does **not** auto-write this HTML or its JSON.

## Source-of-truth rules

1. Before a refresh, first read `PROJECT-BOOTSTRAP.md` and `PROJECT-STATE.json` in **both** repositories, then the relevant source-owner `LATEST.json` / `CHECKPOINT.json`, and newer explicit user-accepted artifacts where present.
2. For GFM, read [Issue #3](https://github.com/hosseinmehdizade-tech/German-Flashcards-Mobile/issues/3) and `docs/GFM-STATUS-BOARD.json`. For Deep Audit, [Issue #39](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/issues/39).
3. Use [master catalog](../MASTER-PROJECT-CATALOG-v1.json) for family identity and [curated portfolio](../DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json) only as an as-of navigation snapshot; real source-owner current content always governs.
4. Never translate a passed content checkpoint into passed independent native Stage6/Stage7 or FINAL app release. Unknown remains **unverified**; never make up completion percentages.
5. This is navigation/reporting only. No app/runtime/UI/FSRS/SRS change, no content mutation, no source deletion, no automatic promotion.
6. Updating the management snapshot is a *new dated version* plus exact Library readback and CAS-safe update of [DASHBOARD-LATEST.json](DASHBOARD-LATEST.json). Preserve prior versions; do not silently overwrite accepted baselines.

## Current limitation & next bounded enhancement

This version is **not connected live** to GitHub because the repositories can be private, the standalone HTML stores no token, and browser direct private-API reads cannot be assumed. The refresh button copies a prompt to request a source-aware refresh within ChatGPT. A future event-driven regenerated snapshot is an optional engineering improvement and must be verified using the actual accessible provider and owner checkpoints rather than pretending a live browser connection.

See [DASHBOARD-LATEST.json](DASHBOARD-LATEST.json) for exact file identities and test scope.
