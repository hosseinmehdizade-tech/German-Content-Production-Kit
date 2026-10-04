# Replay boundary

This Git workstream stores compact evidence and reference scripts. ZIPs, exact canonical payloads, screenshots and browser output dumps are deliberately outside Git.

The original execution root is `C:/Users/hosse/Documents/German-Flashcards-Workspace/Content-Repair-2026-10-03`. Run the commands in REPORT.md from its workspace parent. Do not run a copied script directly from this Git folder: its `__dirname`/`__file__` expects the materialized execution-root layout.

For another host, materialize the exact parents and v3.3.6 framework/current runtime from CHECKPOINT.json and ARTIFACTS.json; verify their hashes first. Restore the `parents`, `framework`, `runtime`, `staging`, and level input ZIP/row fixture layout recorded by the reference bootstrap scripts. SOURCE-RAW-BINDING.json also requires the registered original A2 source images for independent image-hash verification. Rebase filesystem locators without changing artifact identity. Gate commands and observed results are recorded in GATE-RESULTS.json and INDEPENDENT-POSTPACKAGE-REAUDIT.json.

Do not rerun the immutable package builder over existing output filenames. Create a new attempt identity if package bytes change. A1/A2 relocked filenames are exact byte copies of the tested candidate ZIPs; finality is in the acceptance sidecar. B1 remains blocked: the measured Wortnetz display duplicate must pass on then-CURRENT before any relock.
