# Menschen B1 Verben — v3.3.6 Compatibility Re-Audit / Stage 2B + Stage 3A

Status: **PASS_STAGE2B_STAGE3A__STAGE3B_REQUIRED**

This is a post-lock compatibility re-audit of the immutable 395-card Repair1 authority. No card identity, example, source-audio, runtime or UI content was mutated in this milestone.

## Authorities
- Parent B1 release: German-Flashcards-Pro-v451-R85-Menschen-B1-Verben-v3.3.2-Repair1-RELOCKED.zip
- Parent SHA-256: 8c25db09eadc5cf4d9bdecd95c07faf81ab727c87de51fcc3edd434b199a4014
- Canonical SHA-256: e431a855027bae94166be776c562704ace03e6607f47bdd555aa69d605a32273
- Direct-import TSV SHA-256: 16321ecb5798b4fee6ff707f79d988f3cd18df70005f3b8fea158722043e44c6
- Framework: v3.3.6 portable authority SHA-256 61ecccdd1ae0819ae7e15b5d3335bc576dcb896a393765c257687b900ec3915c
- CURRENT/VERIFIED runtime: v451-R85 SHA-256 27da34ebecde9274aa7323a300aad979325914522460b914139e71f966131be4

## Stage 2B
- 441 generic source occurrences: PASS
- 395 active canonical targets
- Identity closure: 0 unresolved
- MEM-009 merge/retirement decisions preserved exactly

## Stage 3A baseline
- 6157 dimension cells
- 1446 unresolved cells
- unresolved: synonym 50; antonym 373; collocation 82; word_family 148; related 368; nvv_links 395; expression argument_slots 30
- source_audio: 393 VERIFIED_PRESENT + 2 CLOSED_NO_FORCE (source has no audio)
- all 395 Rektion cells already VERIFIED_PRESENT
- all 279 applicable morphology cells VERIFIED_PRESENT
- all 116 expressions have structure components and explicit component relations

## Latest-source governance finding
331 existing evidence-required relation claims currently have no globally approved evidence source under the v3.3.6 registry:
- COLLOCATION 174
- SYNONYM 113
- WORD_FAMILY 37
- REKTION 5
- ANTONYM 2

285 currently rely only on DUDEN_ONLINE; 46 rely only on MENSCHEN_B1_SOURCE (including two duplicate source refs).

This is not a semantic-failure verdict. The claims remain unchanged, but they must be re-evidenced from approved authorities or go through an explicit source-governance decision before v3.3.6 Stage 3C closure. The global registry was not silently changed.

## Checkpoint
- Menschen-B1-Verben-v3.3.6-PostLock-Compatibility-Stage2B-Stage3A-PASS-CHECKPOINT.zip
- SHA-256: adc033712ceb09280cbfc53637b2133a1055243a58cf3f92a2ce711fe970611c
- Library: /German-Content-Production-Kit/Checkpoints/Menschen-B1-Verben-v3.3.6-PostLock-Compatibility-Stage2B-Stage3A-PASS-CHECKPOINT.zip
- Library rematerialization: PASS_EXACT_SHA256_AND_BYTE_COMPARE

## Next action
Stage 3B gap-driven enrichment/revalidation. Close every applicable unresolved cell as VERIFIED_PRESENT or justified CLOSED_NO_FORCE; no density forcing, no identity regeneration, and no silent source-registry expansion.
