# Source Access Protocol v1.0.0

Status: STABLE
Scope: German Flashcards Pro / German Content Production Kit

This protocol defines how every new or resumed chat finds and identifies books, PDFs, audio archives, exports and other source material without asking the user to re-upload or reconstruct project history.

## Source model

- **Project Sources** = primary active source shelf.
- **ChatGPT Library** = persistent redundant/fallback shelf.
- **GitHub** = durable source identity, hashes, manifests, checkpoints and derived production artifacts; raw copyrighted books are not stored here by default.

A file in both Project Sources and Library is one logical source when SHA-256 matches. Do not process it twice.

## Mandatory resolution order

1. Explicitly newer/replacement source supplied by the user in the current chat, when identified as current/latest.
2. Project Sources using canonical title/aliases from `SOURCE-REGISTRY.json` and the workstream `SOURCE-MANIFEST.json`.
3. Verify SHA-256 when raw bytes are available.
4. ChatGPT Library using the same canonical identity and hash.
5. Matching current-chat attachment as fallback.
6. Ask the user only if no valid source or unresolved edition/hash conflict remains.

Transient ChatGPT file IDs are not durable identity. Durable identity is stable `source_id` plus SHA-256/source version.

## Hash and edition rule

Same source + same SHA-256 = same mirror even if filename differs. Same title + different SHA-256 must not be silently substituted. A user-declared replacement is registered as a new source version and only dependent stages are invalidated.

## Registration policy

Register sources when they first become active in a workstream. The user's whole Library does not need to be pre-registered. Each active source gets a stable source ID, canonical title/aliases, hash where available, storage expectation and workstream/checkpoint pointer.

## Startup behavior

Read both repository bootstraps/states, this protocol, `SOURCE-REGISTRY.json`, the relevant `CHECKPOINT.json` and `SOURCE-MANIFEST.json`; resolve Project Sources first and Library second; resume from durable checkpoints rather than repeating source extraction.

## Stability

This protocol is intentionally stable. Do not keep editing Project Instructions for routine source-management changes. Project Instructions point to Bootstrap; operational rules are versioned here.