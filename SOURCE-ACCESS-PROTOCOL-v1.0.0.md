# Source Access Protocol v1.0.0

Status: STABLE
Scope: German Flashcards Pro / German Content Production Kit

This protocol defines how every new or resumed chat finds and identifies books, PDFs, audio archives, exports and other source material without asking the user to re-upload or reconstruct project history.

> Operating model: `PROJECT-OPERATING-MODE-v2.md` — artifact-first, async Git.

## 1. Source/storage model

1. **Project Sources** = primary active source shelf for this ChatGPT Project.
2. **ChatGPT Library** = persistent redundant/fallback shelf and a valid place for portable checkpoint/release bundles.
3. **Current conversation files** = immediate authority when the user explicitly supplies a newer/current replacement.
4. **GitHub** = identity, provenance, contracts, code history, compact checkpoint/hash metadata and asynchronous durability mirror. It is not the default binary/source transport.

A file existing in both Project Sources and Library is one logical source when its SHA-256 is identical. Do not extract or process it twice.

## 2. Mandatory source resolution order

For a named source/workstream, resolve the source in this order:

1. If the user explicitly uploads a newer/replacement source in the current chat and identifies it as current/latest, use that file immediately as working authority.
2. Search Project Sources by canonical title and aliases from `SOURCE-REGISTRY.json` / source `SOURCE-MANIFEST.json` when available.
3. Verify the resolved file against the registered SHA-256 whenever raw bytes are available.
4. If Project Sources are unavailable or no matching source is found, search ChatGPT Library using the same canonical title/aliases and verify SHA-256 when possible.
5. Current-chat attachments may be used as a fallback when they match the registered source identity.
6. Consult GitHub manifests/registry/checkpoints when needed to resolve source identity, provenance or ambiguity; do not make deep Git inspection a prerequisite when the source/state is already unambiguous.
7. Ask the user only if no valid source can be resolved or if an unresolved hash/edition conflict remains.

Do not rely on transient internal file IDs as durable identity. Durable identity is `source_id + source_version/hash + source manifest`.

## 3. Hash/edition rule

- Same canonical source + same SHA-256 = same source mirror, regardless of filename or storage surface.
- Same title + different SHA-256 = potentially different scan/edition/revision. Do not silently substitute it.
- If the user explicitly declares a different-hash file to be the replacement/current source, treat it as the new working source version and invalidate only workstream stages whose source fidelity depends on the changed bytes.
- Filename differences alone do not create a new source version.

## 4. Registration policy

`SOURCE-REGISTRY.json` is the cross-workstream index. It does not need to list every book in the user's Library in advance.

Register a source when it first becomes active in a production workstream. Each active source should have:

- stable `source_id`
- canonical title
- useful filename/title aliases
- SHA-256 when raw bytes are available
- source type and language/domain
- active workstream/checkpoint pointer when applicable
- storage expectation (`project_sources`, `library`, or both)

The source-specific workspace remains authoritative for detailed chapter/unit inventory and provenance. Git synchronization of registry/checkpoint metadata may happen asynchronously at a meaningful milestone.

## 5. Startup behavior for new chats

For substantial content work:

1. Read `PROJECT-BOOTSTRAP.md` and `PROJECT-OPERATING-MODE-v2.md`.
2. Resolve the newest verified portable workstream state/checkpoint from current files, Project Sources or Library.
3. Read `PROJECT-STATE.json`, this protocol, `SOURCE-REGISTRY.json` and the workstream manifest/checkpoint only as needed to resolve authority or rules for the task.
4. Resolve the required raw source from explicit current upload → Project Sources → Library.
5. Resume from the newest verified checkpoint; do not re-extract completed source inventory unless invalidated.
6. Inspect the Flashcards repository only when runtime/import/presentation compatibility actually matters.

The user should normally only need to say which workstream to continue. They should not need to explain where the source file is stored.

## 6. GitHub must not block work

GitHub is an asynchronous durability mirror and coordination layer. If GitHub is unavailable, stale or unhealthy but the registered source and newest verified checkpoint/artifact can be resolved from Project/Library/current context, continue safe work.

- Make at most one Git repair/sync attempt in a normal production turn unless the user explicitly asks for Git repair.
- Keep quality state and `persistence.git` separate.
- Do not call a result **Git-backed PASS/FINAL/VERIFIED** until required Git persistence is complete.
- Do not use GitHub Actions/Base64 chunking to reconstruct generated checkpoint/release ZIPs merely for persistence.
- Persist compact manifests/hashes/checkpoint metadata to Git at meaningful boundaries when practical.

## 7. Source-access failure behavior

If a source cannot be resolved:

- report the missing canonical `source_id` and expected title/hash;
- try Library before asking the user to upload again;
- do not replace it with a web copy or a similar edition without explicit authorization;
- continue unrelated workstreams that do not depend on the missing source.

## 8. Stability rule

This v1.0 protocol is intended to remain stable. Do not keep changing Project Instructions for ordinary source-management improvements. Operational refinements belong in `PROJECT-OPERATING-MODE-v2.md`, this protocol or workstream state when they affect actual source access.
