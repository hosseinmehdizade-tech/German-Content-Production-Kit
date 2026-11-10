# Aspekte B1+ — app-side integration handoff (Draft PR #41)

**Date:** 2026-11-10  
**State:** SOURCE BRANCH CREATED · CODE REVIEWABLE · FULL APP INTEGRATION NOT YET COMMITTED · `RELEASE_BLOCKED_NONIMPORT`

## What was actually done

1. Reconfirmed the app's **CURRENT** `v505-R141 WORDLINKS_FRONTBACK_R3` user Library ZIP SHA256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`, exact current mirror branch commit `02b83543e46aebaa6fc345818930406b1607a83c` and original `01-App/index.html` SHA256 `f38877d7ff39ad24294303125ae60d77955c251768fffa059cf7452a0a3aef26`. Never worked from historical main `01-App`.
2. Reconstructed combined Gate06/07 changes on a local copy of original v505; patched index SHA256 `5ed1b188586e97e1fd5cae755b843c5ed5dca879c0ffb90adfabe209e798fcf4`; both added Guard modules preserved byte-exact. Executed the actual browser source and **40 JS assets** in isolated Chromium with TSV/JSON/ZIP Preview+Submit handler hooks; **10/10 bounded assertions PASS**. No IndexedDB write, durable reload, actual release or right-card test.
3. Created a **separate app Git branch** `candidate/b1plus-preimport-guards-review-20261110` from exact CURRENT source, plus [Draft Pull Request #41](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/pull/41) targeting `candidate/v505-r141-wordlinks-r3-exact-20261107`, not `main`.
4. The Draft PR actually contains **two Guard JS modules** under `01-App/modules`, **exact 5.4 kB unified integration patch**, reproducible SHA-256-pinned Python staging builder, README and focused browser-results JSON. The GitHub-review branch **does not modify the large `01-App/index.html`** because the single-blob transfer hit a connector payload transport limit; current `index.html` blob remains `82feb57a09372256727a1fd179e8c676b5a1a25f`. Therefore the PR is **review-ready as a proposal, NOT merge-ready as a working app**.
5. Parent app [Issue #40](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/issues/40) received an exact follow-up comment linking the PR and enumerating remaining blockers.

## Frozen user data authority

- **Current curated 1571-card owner:** Library `libfile_261160dae9508191904f55a410076d40`; archive SHA256 `a2fa93f3389b43db12e562331cc3302e24e51f0cb028a494ce61b3e825e6a50b`, primary JSONL SHA256 `829a1d9e16df96cf1467659835f7fcaa14aefa705f7d639910a150e9d37bfe22`. No card changes. All **359 HOLD** markers and all **3524 DE–FA example pairs** preserved.
- Current installed/user app Library original was not changed or promoted.

## Explicit release blockers / decisions required

- **Not security-complete:** known draft marker checks are editable; define trusted release authority and signed/approved content transport, not a cosmetic file flag.
- Review & apply original patch to exact current app source, decide source ownership/branch, reconcile versioned HTML twin, service worker shell, integrity/release manifests.
- Run native **valid** TSV/JSON/ZIP durable import + reload, SRS state and right-card multi-sense/Wortnetz rendering on a supported stable origin; previous local-origin attempts were blocked by environment policy. Do not falsely assert these tests passed.
- Additional import surfaces may bypass this guard. Audit full app ingress matrix before promotion.
- Linguistic and semantic QA still incomplete, 359 HOLDs unresolved: **no learner import permitted**.
- **Next substantive step:** App owner reviews PR #41 and Issue #40; only then implement/validate the final runtime merge. Do not restart L10 or synthetic Gate01–07 cycles.

**Deutsch:** Es existiert ein echter, separater Review-Branch mit Draft PR #41 und reproduzierbarem Patch. Die produktive App und die kuratierten Lernkarten sind unverändert; Freigabe bleibt gesperrt.
