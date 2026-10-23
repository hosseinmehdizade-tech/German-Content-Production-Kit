# R70 source-linked reviewer workspace — exact recovery
R70 full ZIP SHA-256: `84f9cd4b39c64d2f40f06594589184f3551848384766d6068384bb7c52d37180`
Builder Python SHA-256: `9be73f503bc354205faea1f0d1d26c7a7946029c866c02f7375922945369b5ba`
The Python builder was saved in Git as gzip-compressed base64 text, because Library is full. Decode it with Python's standard library:
```bash
python -c "import base64,gzip,pathlib; p=pathlib.Path('BUILD_R70_REVIEWER_WORKSPACE.py.gz.b64'); pathlib.Path('BUILD_R70_REVIEWER_WORKSPACE.py').write_bytes(gzip.decompress(base64.b64decode(p.read_text().strip())))"
```
Verify its SHA-256, then run:
```bash
python BUILD_R70_REVIEWER_WORKSPACE.py --r67 R67.zip --r69 R69.zip --r68 R68_CANONICAL_ASSIGNMENTS_MERGE.py --output R70.zip
```
Exact required inputs:
- R67 SHA-256 `84299acfdd23649c114d01068724e3ffcc404a24950ea0f9dbdd1286353b328d`
- R69 SHA-256 `65009ba4aa15b30e3ee4f996d4883fc0f5327518449c2252dce7746f7518b1da`
- R68 source Python SHA-256 `2712226605b8a90a096a9269e4218d41f2a0ee88ca121b1a668561edff74e873`
- R66 content source SHA-256 `630bfcd30be7439f397c634ed7c5f197db54833455a88569b27b7ef79c73a21b`
R70 binds 1,411 review items to R69 source screenshot locations and preserves R67 item identities and R68 export/merge contract. It embeds no original screenshot images; authorized experts need separate controlled source access.
**No qualified independent approvals (0/1411)**; Stage4 BLOCKED, Stage5–7 NOT_RUN, no import.
