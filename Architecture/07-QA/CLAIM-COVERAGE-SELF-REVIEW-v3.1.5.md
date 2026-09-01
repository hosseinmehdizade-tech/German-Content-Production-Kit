# v3.1.5 Claim-Coverage Self-Review

## Scope
This patch does not change the Canonical Learning Unit schema, Example count model, runtime-state gate, Presentation, Practice, or SRS.

## Decisions verified
- DE remains the source/anchor Example.
- FA/EN translations, when present, remain children of that same Example and Stable ID.
- Required translation languages remain Dataset-Profile driven; they are not globally hard-coded.
- Non-empty `details.rection` in a Profile that requires verified sources now requires an explicit verified `rection` provenance claim.
- Generic `grammar` evidence does not silently cover Rektion.
- `grammis` remains preferred for Rektion.
- Duden is permitted to claim Rektion only when the exact entry/grammar/examples explicitly attest the learner-facing pattern.
- DE↔FA sources remain forbidden as final German Rektion authority.
- Source Registry content identity is now `gfp-approved-language-sources@1.1.0`.

## Regression evidence
- Unit tests: 64/64 PASS.
- Draft 2020-12 schema meta-validation: 6/6 schemas PASS.
- Schema instances: 19/19 PASS.
- Existing runtime-state-aware import gate tests remain green.

## Pilot evidence
The existing 30-verb v3.1.4 pilot remains transport-valid, but v3.1.5 correctly blocks production finality for 29 Units that contain `details.rection` without a dedicated verified `rection` claim. This is expected and demonstrates the new gate is active.
