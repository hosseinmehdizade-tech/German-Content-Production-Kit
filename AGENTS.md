# AGENTS.md — German Flashcards cross-project work

These repo-root rules apply to coding assistants, agents, and ChatGPT sessions working with this repository.

1. First read `PROJECT-BOOTSTRAP.md`, `PROJECT-STATE.json`, `EXECUTION-SAFETY-POLICY.json`, and **`EXECUTION-OUTCOME-EFFICIENCY-POLICY.json`**. When relevant, check both German-Flashcards-Pro and German-Content-Production-Kit repositories before substantial work.
2. When told **continue / ادامه بده**, continue the current *major* stage or explicitly bounded deliverable. Do not terminate simply after 3–5 card edits, another small QA pass, ZIP, Git commit, or status report. Work through all evidence-supported reviewable items until stage PASS/CLOSED, a concrete BLOCKER, a material conflict, or hard safety/tool boundary. Never fabricate edits to fill a quota.
3. Report work-item outcomes (reviewed unique / corrected / kept / held / unreviewed) separately from overall Stage completion. Scoped PASS or Git sync does **not** mean Stage4-7 or final release PASS. Use validated outcome receipts at significant milestones: `python Verification/validate_execution_outcome_receipt.py <receipt.json>`.
4. Apply safe corrections to the single mutable working state, not LOCKED originals. One logical writer per mutable workstream; parallel chats should audit read-only or work in disjoint workstreams/shards. Read newest LATEST + parent SHA before writing, use optimistic compare-and-swap, and never silently overwrite a concurrent update.
5. Avoid heavy inherited ZIPs, Library churn, per-edit Git/report loops and re-reading unchanged giant state files. Favor content/code execution, targeted tests, exact recoverable patches, and Git sync at a meaningful validated boundary. Preserve required verified CURRENT runtime releases and final one-ZIP delivery contracts.
6. Content streams use WORKSTREAM-LEAN-EDIT-POLICY.json, the local workstream LATEST/receipt, registered source and active START-PROMPT. Respect frozen NVV baselines; all Stage4-7 gates remain mandatory.
7. Other running chats are **not** remotely updated by this file. It takes effect when the agent next reads the repo/bootstraps. Never claim cross-chat automatic synchronization or background work.

If a policy conflicts with exact primary source, mandated independent QA, runtime/currentness, data safety or explicit user approval, retain those higher-fidelity safeguards and record the decision.
