# Menschen B1 Verben — v3.3.6 Stage3B NVV Closure

Status: **PASS_NVV_100_PERCENT_DISPOSITION**

## Scope
This milestone continues the post-lock v3.3.6 compatibility re-audit from the completed argument-slots checkpoint and closes only the `nvv_links` dimension plus evidence-backed expression classification repairs required by the dedicated NVV/idiom authorities.

## Result
- 395/395 `nvv_links` cells reviewed and finalized.
- 31 `VERIFIED_PRESENT`.
- 364 `CLOSED_NO_FORCE`.
- 0 unresolved `nvv_links`.
- 16 conservative evidence-backed NVV relations appended.
- 15 intrinsic NVV expressions recognized.
- Total Stage3 unresolved cells reduced from 1416 to 1021.

## Expression classification repairs
Four existing expressions were corrected from dedicated-source evidence without changing stable IDs, meanings, examples, source membership, or audio:
- `mb1m-lu-0016` — `das Vertrauen verlieren`: collocation -> nvv
- `mb1m-lu-0134` — `infrage kommen`: multiword_expression -> nvv
- `mb1m-lu-0222` — `ein Referat halten`: collocation -> nvv
- `mb1m-lu-0107` — `Recht sprechen`: nvv -> idiom

## Validation
- v3.3.6 enrichment completeness baseline: PASS
- candidate ledger working-mode validation: PASS
- targeted NVV delta validation: PASS
- prior 2510 relations preserved byte-identically; exactly 16 new NVV relations appended
- 395-card neutral projection: PASS
- all projected cardType = `de-vocabulary`
- all projected presentation contract = `gfp-vocabulary-neutral@1`
- ZIP CRC: PASS
- 41/41 internal SHA256SUMS: PASS
- Library rematerialization: PASS exact SHA-256 and byte compare

The inherited parent canonical contains legacy relation records with null target_type values, so the strict global v411 bundle validator is not used as this milestone's gate. This is a pre-existing parent-envelope issue unrelated to the new NVV delta; targeted validation proves the exact new changes.

## Checkpoint
- `Menschen-B1-Verben-v3.3.6-PostLock-Compatibility-Stage3B-NVV-CLOSURE-CHECKPOINT.zip`
- SHA-256: `9cab2f96edee908cdf9675bcda1fd354ad44d71431a3ad96fe4feb7041420720`
- Canonical SHA-256: `f5213fc8dee198f58904e41ac3b6bc09dd9e334cef07abb4ef713ae6cd8e08db`
- Library path: `/German-Content-Production-Kit/Checkpoints/Menschen-B1-Verben-v3.3.6-PostLock-Compatibility-Stage3B-NVV-CLOSURE-CHECKPOINT.zip`
- Library file id: `file_000000001bac82439e0b454f55956bd6`
- Library stable id: `libfile_16cdef4c3f948191855ed53c5be54b3b`

## Next action
Continue Stage3B with synonym, antonym, collocation, word_family and related gaps plus source-governance revalidation of the existing flagged relation evidence. Preserve completed argument_slots and nvv_links dispositions. No density forcing.
