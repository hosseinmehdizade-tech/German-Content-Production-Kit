# OP-02 Wortfamilie: V24 physical/typed inventory, no forced synchronization

**Scope:** exact user-supplied `Menschen-A1-V24-COMPLETE-DELIVERY-v505-R141-20261102(1).zip` / `Content/Menschen-A1-V24-FULL-2997-IMPORT.tsv`, **2,997 cards**; exact input TSV SHA-256 `3ff2cd60f7d22fb989f0d4e9e885949b0bc4a91f4b77fd6192701d1315ba0b5e`. Independent read-only Python inspection in the current session; no content change or runtime browser claims.

| V24 observed classification | Cards |
| --- | ---: |
| Physical `Details.Wortfamilie` and typed `WORD_FAMILY` | **52** |
| Physical `Details.Wortfamilie` only | **31** |
| Typed `WORD_FAMILY` only | **8** |
| Neither of these two exact fields | **2,906** |
| Total | **2,997** |

Exact physical Wortfamilie entries: **118** across **83** cards. Typed WORD_FAMILY records: **155 raw records counted across canonical_relations, vnext_relations and related** across **60** cards; these are NOT 155 independent family assertions because canonical/vnext projections can duplicate each other. Of 155 records, 142 have a target ID present in this same TSV and 13 lack a target ID; this is **not automatically an invalid graph link** (the latter can be freeform source assertions). No target ID pointing outside this exact TSV was found in this scoped inspection.

**Eight typed-only cards, flagged for bounded projection review, not declared learner-visible defects:** `ma1m-lu-0214` (Arbeitnehmer), `ma1m-lu-0811` (Durst), `ma1m-lu-0815` (durstig), `ma1m-lu-0817` (Hunger), `ma1m-lu-0822` (hungrig), `ma1m-lu-0826` (Frühstück), `ma1m-lu-0829` (frühstücken), `ma1m-lu-1133` (Geschenk). The runtime Wortnetz graph may display a typed relation separately from the physical details panel. The 31 visible-only cards may correctly use freeform family glosses without canonical target IDs. Do not manufacture backlinks or rewrite these 39 cards solely to make counts equal.

**Lean decision:** one Stage3 lexical/sense review and one evidence lineage; keep typed resolved edges as canonical graph facts, keep correct visible freeform details as text. Use optional `Verification/audit_wortfamilie_lean_views.py` for changed-workstream diagnosis only. Reuse risk-based Stage4; no quota, no new blocking gate, no retroactive rewrite of V24/locked artifacts. Native Study/Quick/IndexedDB display remains unobserved here and cannot be inferred from this TSV analysis. This diagnostic is not a Stage4, Stage5, Stage6 or Stage7 PASS.
