# Changelog v3.1.11

## Purpose

v3.1.11 hardens lexical quality, target-runtime acceptance, and subsequent-source execution after the Menschen A1 repair exposed failure modes that were not blocked by v3.1.10 density/completeness checks alone.

## Changes

- Quality outranks field density; collocation count is preferred coverage, not a fabrication incentive.
- Example-derived phrases may not be promoted to collocations.
- Collocations must be atomic, evidence-backed and sense-aligned.
- Broad POS synonym/antonym extraction is rejected when it cannot be bound to the selected sense.
- Explicit learner valency requires explicit Rektion and evidence.
- Final delivery requires version-pinned importer/presentation acceptance, not only parse/transport validation.
- External lexical retrieval is incremental and cached; failed subsets are retried instead of refetching the full dataset.
- Legacy enrichment/NVV/history is disabled by default.
- A generic rich-card completeness profile is provided for new sources; source-specific profiles must not be reused across different books/levels.
- Added a New Source Agentic Runbook with fixed inventory, cache, gate order, final deliverables, and no arbitrary batch-stop behavior.

Architecture v3.1.5 and semantic contract 3.1.3 are unchanged.
