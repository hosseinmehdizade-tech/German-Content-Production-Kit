# OP-02: Exact CURRENT v505 projector source-level finding — NOT Stage 6

**Scope**: Continuous Optimization, source-level compatibility only, no learner content/app changes.

## Newly verified CURRENT evidence

- Official `German-Flashcards-Pro/RUNTIME-AUTHORITY-PIN.json` states CURRENT nonfinal `v505-R141`, ZIP SHA256 `482b285bc4a1364e5595f721ecbf0caddcb95ba0eb2cdf9958d9aa11c889416e`, app `01-App/index.html` SHA256 `0b7358d2755a80d1563e5b4791f62ec72c6a42279914739d551aef1f4d2a0ea5`.
- The source was fetched as GitHub blob `f416070ded93843ec5370052be251b2ac7919af5` on branch `candidate/v505-r141-committed-storage-20261101` rather than through ordinary `fetch_file`, which returned no content because the HTML is large.
- **Independent SHA-256 of actual UTF-8 blob:** 3,481,553 bytes, hash exactly **`0b7358d2755a80d1563e5b4791f62ec72c6a42279914739d551aef1f4d2a0ea5`**. This authenticates the app HTML **component**, not the full packaged ZIP or native import state.
- Current `presentationProjectedDetailsV459` function SHA256 is **`51645e4cfafabcd0370d2659ca75ef5b83bc3ad53049a262a396ba397bcfc378`**, identical to the original cryptographically pinned v486 function. The text normalization, detail preparation, detail kind, detail visibility, and TSV import functions also have matching length and 64-bit byte fingerprints (see machine-readable report). The 64-bit hashes are diagnostic comparison fingerprints, not standalone cryptographic proof.
- Higher-level **`presentationDetailSectionsV339` differs** in v505; it now also filters `card_design_studio.hidden_sections`. Study details default to full, Quick to a collapsed three-section subset; mode-specific settings may differ. Accordingly, don't report all 2,132 eligible items as confirmed visible to the learner.

## Read-only original V22 replay

- Exact immutable A1 V22 ZIP SHA256 `74cdbf5b6d0121421fac8235124e738929b9764f3696db532cc54f9509f5757d`, import TSV exact SHA256 `024ee77efbb3675a0720491af1da2286e2186bd00bc83bcbb9dfef22b0656c9a`.
- 2,997 cards; 1,123 cards with structured combinations; 2,180 backend combinations.
- Executing the byte-identical source projector in an isolated Node VM against original V22 card input gives **2,132 matches in projected `Kombinationen`**, with **57 recovered through the auto-bridge**, and **48 not projected** across **27 cards** because an existing partial `Kombinationen` section preempts the bridge.
- Four behavioral negative/positive controls PASS: invalid selector blocks bridge; removed partial section restores bridge; correct selector projects; existing partial section remains unchanged.
- The five first browser probes remain `ma1m-lu-1662`, `ma1m-lu-1846`, `ma1m-lu-1885`, `ma1m-lu-2279`, `ma1m-lu-2933` (all five are *priorities*, not proved missing from the actual UI). Review queue's 105 items remain PENDING.

## Approval boundary

`PASS_SCOPED_EXACT_CURRENT_CODE_EQUIVALENCE__NATIVE_STAGE6_BLOCKED` means the **exact currently pinned code-level projector** has been tied to the original V22 input and replayed; it does **not** mean `Stage5 PASS`, `Stage6 PASS`, direct browser evidence, or an app release. The original v505 full ZIP cannot yet be independently raw-byte materialized and checked in this workspace. Do not auto-insert 48 combinations: 35 have exact German-only occurrences under `Verwandte Wörter`, three under `Kollokationen`, and ten no exact match in other Details; educational intent must be adjudicated first.

**Reproduction**: `build_op02_v505_source_projector_evidence.py --output <newfile.json>` uses pinned original V22 and pinned historical v486 bundles solely because the seven relevant function fragments are verified equal to v505. It outputs a scoped report and does not edit source ZIP, locked workstreams, UI, or runtime. The original v505 app blob must be re-fetched independently if re-attesting the component SHA. The script cannot itself attest the current remote blob without a connector retrieval.