# Source Access Protocol v1.0.0

Status: STABLE
Scope: German Flashcards Pro / German Content Production Kit

This protocol defines how every new or resumed chat finds and identifies books, PDFs, audio archives, exports and other source material without asking the user to re-upload or reconstruct project history.

## 1. Three-layer source model

1. **Project Sources** = primary active source shelf for this ChatGPT Project. Sources currently used by active workstreams should be present here.
2. **ChatGPT Library** = persistent redundant source shelf / fallback. A source may exist in both Project Sources and Library.
3. **GitHub** = identity, provenance, checkpoint and derived-artifact layer. Do not store copyrighted source PDFs in GitHub unless the user explicitly requests and rights allow it. Store canonical source IDs, filenames/aliases, SHA-256 hashes, manifests, checkpoints and derived production artifacts instead.

A file existing in both Project Sources and Library is one logical source when its SHA-256 is identical. Do not extract or process it twice.

## 2. Mandatory source resolution order

For a named source/workstream, resolve the source in this order:

1. If the user explicitly uploads a newer/replacement source in the current chat and identifies it as current/latest, use that file immediately as working authority and register/update its identity when Git is available.
2. Search Project Sources by canonical title and aliases from `SOURCE-REGISTRY.json` / source `SOURCE-MANIFEST.json`.
3. Verify the resolved file against the registered SHA-256 whenever raw bytes are available.
4. If Project Sources are unavailable or no matching source is found, search ChatGPT Library using the same canonical title/aliases and verify SHA-256 when possible.
5. Current-chat attachments may be used as a fallback when they match the registered source identity.
6. Ask the user only if no valid source can be resolved or if an unresolved hash/edition conflict remains.

Do not rely on transient internal file IDs as durable identity. File IDs are resolved live per chat/session. Durable identity is `source_id + source_version/hash + source manifest`.

## 3. Hash/edition rule

- Same canonical source + same SHA-256 = same source mirror, regardless of filename or storage surface.
- Same title + different SHA-256 = potentially different scan/edition/revision. Do not silently substitute it.
- If the user explicitly declares a different-hash file to be the replacement/current source, register it as a new source version and invalidate only workstream stages whose source fidelity depends on the changed bytes.
- Filename differences alone do not create a new source version.

## 4. Registration policy

`SOURCE-REGISTRY.json` is the cross-workstream index. It does not need to list every book in the user's Library in advance.

Register a source when it first becomes active in a production workstream. Each active source must have:

- stable `source_id`
- canonical title
- useful filename/title aliases
- SHA-256 when raw bytes are available
- source type and language/domain
- active workstream/checkpoint pointer when applicable
- storage expectation (`project_sources`, `library`, or both)

The source-specific workspace remains authoritative for detailed chapter/unit inventory and provenance.

## 5. Startup behavior for new chats

For substantial content work:

1. Read `PROJECT-BOOTSTRAP.md` and `PROJECT-STATE.json` in both repositories.
2. Read this protocol and `SOURCE-REGISTRY.json`.
3. Read the relevant workstream `CHECKPOINT.json` and source `SOURCE-MANIFEST.json`.
4. Resolve the required raw source from Project Sources first, then Library.
5. Resume from the durable checkpoint; do not re-extract completed source inventory unless invalidated.

The user should normally only need to say which workstream to continue. They should not need to explain where the source file is stored.

## 6. GitHub must not block work

GitHub is the durable coordination layer. If GitHub is unavailable but the registered source and newest checkpoint/artifact can be resolved from Project Sources/current context, continue safe work. Persist the next durable checkpoint when Git access returns. Do not claim Git-backed PASS/FINAL/VERIFIED until required persistence is complete.

## 7. Source-access failure behavior

If a source cannot be resolved:

- report the missing canonical `source_id` and expected title/hash;
- try Library before asking the user to upload again;
- do not replace it with a web copy or a similar edition without explicit authorization;
- continue unrelated workstreams that do not depend on the missing source.

## 8. Stability rule

This v1.0 protocol is intended to remain stable. Do not keep changing Project Instructions for ordinary source-management improvements. Project Instructions point chats to `PROJECT-BOOTSTRAP.md`; operational refinements belong here or in GitHub state/checkpoints. Change this protocol only for a real architecture/source-authority requirement, and version the change explicitly.