# Phase 3 — Exact source and package byte attestation

**Status:** scoped verification of one dated existing real workstream, not a blanket production or release PASS.

## What changes compared with Phase 2?

Phase 2 classified the Git-index path and SHA as **declared metadata only**. Phase 3 adds independent readback of the actual original user source and one Library ZIP artifact; checks the package's own SHA256 manifest and exact embedded source/content hashes; optionally reruns a pre-approved, *exact Git-blob-pinned* Stage4 **risk-evidence acceptance** script from the bundle.

## First real source profile: 250 Verben mit Präpositionen R7

- Profile: `Profiles/VMP-R7-EXACT-ARTIFACT-20261105.json`, a *dated* source+ZIP identity. It must not override a newer explicit validated user artifact.
- Original source: user PDF `250 _verben_mit_Praeposition.Deutschweb.pdf`.
- Artifact: `250-Verben-Lexical-Enrichment-v1.8-R7-OFFICIAL-STAGE4-PASS-V505-FULL-TSV-IMPORT-QA-20261104.zip`.
- Independent checks: full original PDF SHA, ZIP bytes/size SHA, CRC, exact 24/24 manifest coverage, embedded PDF byte identity, and TSV SHA.
- Recheck: bundled risk-based Stage4 gate is executed only after its exact script and policy Git-blob hashes equal the independently stored source profile pins. The acceptance is **risk-review admissibility**, not certification of 100% linguistic accuracy.
- Historical `Workspaces/250-verben-mit-praepositionen-lexical-enrichment-v1/LATEST.json` and R7 Stage4 receipt are named for audit traceability. They are not promoted to CURRENT runtime.
- Historical v1.7 release, LOCKED, source PDF and cards remain unchanged.

Run in an environment where both actual files exist:

```bash
python -B Tools/attest_source_package_bytes_v1.py \
  --profile Optimization-Program/Control-Center/Profiles/VMP-R7-EXACT-ARTIFACT-20261105.json \
  --archive /path/to/250-Verben-Lexical-Enrichment-v1.8-R7-OFFICIAL-STAGE4-PASS-V505-FULL-TSV-IMPORT-QA-20261104.zip \
  --original-source /path/to/250\ _verben_mit_Praeposition.Deutschweb.pdf \
  --output /tmp/VMP-R7-SCOPED-ATTESTATION.json
```

The real user PDF and Library ZIP are **not included in the GitHub checkout**. CI tests only synthetic fixtures and deliberately cannot claim real artifact readback. A dated exact real-file receipt is saved separately in `Optimization-Program/Verification/`. Recheck with source bytes before relying on the result, especially if a newer artifact is submitted.

## Fail-closed contract

Reject unexpected archive SHA/size, incorrect original PDF SHA, incorrect source member/content member SHA, duplicate/partial/false manifest, invalid paths, encrypted ZIP, symlink, too large ZIP population, or a changed/unpinned Stage4 gate. Do not silently repair or normalize any learner data.

## Acceptance boundary

- Exact-byte content provenance: yes, for this scoped original + R7 artifact and 24-entry manifest.
- Risk-based Stage4 official gate rerun: yes, scoped; does not guarantee every German/Persian choice is perfect.
- Stage5 official final content acceptance: **not run**.
- Stage6 real browser import/persistence: **not run**.
- Stage7 final release: **not run**.
- Remaining workstreams (34): **not globally certified**.
