# Source Sense Marker Normalization v1.0.0

Dictionary sense labels such as `[1]`, `[1a]`, `[2b]`, `[4b]` are source metadata, not learner-facing lexical content.

## Required behavior

- Preserve the lexical item itself exactly when the only defect is a leading source sense marker.
- Example: `[1a] lauschen` -> `lauschen`.
- Example: `[1a] taub sein` -> `taub sein`.
- Do not delete a synonym, antonym, collocation or other lexical item solely because such a marker is present.
- Store/retain the source sense locator in provenance/evidence metadata when available; do not expose the marker in learner-facing text.
- Normalization must not invent, merge, split, reorder, or otherwise rewrite lexical material beyond removal of the marker and surrounding whitespace.
- Lexical-quality/sense-alignment validation remains a separate gate. A relation may only be removed for an independent lexical-quality reason, never merely because the source marker existed.

## Delivery invariant

For a marker-only repair, relation counts before and after normalization must be identical. Only the learner-facing marker text may change.
