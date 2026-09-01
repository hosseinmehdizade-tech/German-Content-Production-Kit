# General German Content Generation Master Prompt v3.1.10
## Product Content Completeness Hotfix for Architecture v3.1.5

This file is the **normative v3.1.10 overlay** on `CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md`.
All v3.1.9 rules remain binding unless this file explicitly strengthens them. Architecture v3.1.5 and semantic contract 3.1.3 are unchanged.

## 1. New status boundary — mandatory

`CONTENT_VALIDATED` means the canonical dataset passed the architecture/schema/source-policy/linguistic gates that were actually executed. It does **not** mean every field wanted by a product card is populated.

A separate gate is required:

```text
PRODUCT_CONTENT_COMPLETE
```

A dataset may therefore be:

```text
CONTENT_VALIDATED = PASS
PRODUCT_CONTENT_COMPLETE = FAIL
```

No delivery/release report may collapse these statuses into one green status.

## 2. Completeness profile is target-owned policy

Product completeness is not added to `LEARNING-UNIT-SCHEMA.json` and does not rewrite the semantic contract. It is evaluated by a separate Content Completeness Profile. This keeps schema validity independent from a specific UI/card density target.

For the current Menschen A1 rich German Verb cards, use:

`MENSCHEN-A1-CONTENT-COMPLETENESS-v1.0.0.json`

## 3. Menschen A1 Verb completeness requirements

For every `type=verb` unit in this target:

- `core.auxiliary` is required.
- `core.reflexive` is required.
- `core.separability` is required.
- `connections[kind=collocation]`: hard minimum 3, preferred minimum 4, preferred maximum 6.
- If collocation content is present, explicit verified provenance for collocation/collocational usage is required. A generic `usage` claim alone is insufficient.
- If `details.rection` is present, explicit verified provenance for rection/valency/government is required.
- If the learner-facing headword encodes a fixed/prepositional construction, Rektion must be present.
- `details.synonyms`: preferred minimum 1, **not hard-required**.
- `details.antonyms`: preferred minimum 1, **not hard-required**.
- If synonym/antonym content is present, explicit verified provenance for synonymy/antonymy is required.

Missing preferred Synonym/Antonym is a warning. Fabricating one to silence the warning is a failure of content policy.

## 4. No fabrication to satisfy counts

A hard minimum is a release gate, **not a license to invent content**. If evidence supports only two trustworthy collocations, preserve those two, keep the unit incomplete, and report the missing third item. Never manufacture evidence, locators, synonyms, antonyms, Rektion or collocations.

## 5. Legacy `NVV1..NVV6` recovery — semantic safety rule

The old Menschen A1 legacy dataset used columns named `NVV1..NVV6` for a learner-facing enrichment section. Those column names are **not semantic proof** that each value is a canonical `kind=nvv`.

For migration/recovery:

```text
legacy NVV cell -> legacy_phrase_candidate
legacy_phrase_candidate != canonical nvv
legacy_phrase_candidate != canonical collocation
```

Each candidate must be classified against the current Connection Schema into one of:

```text
collocation
nvv
pattern
fixed_expression
prepositional_pattern
common_combination
other
```

Rules:

- Do not bulk rename `NVV` to `collocation` merely to pass the gate.
- Do not bulk preserve `NVV` as canonical `nvv` merely because of the old column label.
- Preserve candidate text losslessly during review.
- Classification must be sense-aligned with the current Learning Unit.
- Provenance must name the real lineage/evidence; do not claim Duden or another dictionary verified a phrase unless that exact claim was actually checked.
- When a legacy audit artifact is used as recovery evidence, identify it as legacy recovery/audit evidence, not as live lexicon evidence.
- Existing canonical connections must never be overwritten silently.

## 6. Evidence vocabulary

The product completeness validator intentionally requires explicit claim vocabulary for learner-facing enrichment:

```text
collocation | collocations | collocational_usage
synonymy | synonyms
antonymy | antonyms
rection | valency | government_pattern
```

A broad claim such as `usage` does not automatically authorize all of the above.

## 7. Agentic repair behavior

On `PRODUCT_CONTENT_COMPLETE = FAIL`:

1. enumerate hard failures by unit and field;
2. preserve all already-valid canonical data and stable IDs;
3. recover trustworthy prior enrichment only with explicit lineage;
4. classify legacy phrase candidates semantically;
5. enrich only from verified evidence;
6. rerun architecture/schema validation;
7. rerun linguistic audit for changed learner content;
8. rerun product completeness;
9. rebuild Delivery only after all applicable content gates pass;
10. never call a failed/review-required artifact Final.

Do not stop every ten cards. Continue until completion or a real evidence/tooling blocker.

## 8. Required validator

Run:

```text
python Verification/validate_content_completeness_v1_0_0.py <canonical.json> Prompt/MENSCHEN-A1-CONTENT-COMPLETENESS-v1.0.0.json --output <report.json>
```

Exit codes:

```text
0 = PRODUCT_CONTENT_COMPLETE PASS
1 = PRODUCT_CONTENT_COMPLETE FAIL
2 = configuration/input error
```

This validator complements; it never replaces the Architecture canonical validator or linguistic audit.
