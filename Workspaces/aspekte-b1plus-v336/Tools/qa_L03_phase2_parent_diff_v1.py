#!/usr/bin/env python3
import json,zipfile,hashlib,sys
PRE="G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl"
p,base=sys.argv[1:3]
with zipfile.ZipFile(p) as a,zipfile.ZipFile(base) as b:
 assert a.testzip() is None
 A=[json.loads(x) for x in a.read(PRE).splitlines()]
 B=[json.loads(x) for x in b.read(PRE).splitlines()]
 assert len(A)==len(B)==1571
 assert all(x==y for x,y in zip(A,B) if x["lesson"]!="L03")
 assert all(x["preview_card_id"]==y["preview_card_id"] for x,y in zip(A,B))
 assert all(x["linked_original_source_ordinals"]==y["linked_original_source_ordinals"] for x,y in zip(A,B))
 assert a.read("G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv")==b.read("G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv")
 L=[c for c in A if c["lesson"]=="L03"]
 assert len(L)==194
 for c in L:
  nets=c["back"].get("semantic_network_sense_anchored_pending_qa") or []
  ex=(c["back"].get("existing_examples_de_fa_pending_qa") or [])+(c["back"].get("additional_examples_de_fa_pending_qa") or [])
  assert all(x.get("de") and x.get("fa") and x.get("status") for x in ex)
  if nets:assert all(x.get("sense_id") in {n["sense_id"] for n in nets} for x in ex)
  assert c["back"].get("Formen_section") is None and not c.get("formal_release_approved") and not c.get("import_ready")
  assert c.get("curated_HOLD_content_disposition_exists")==next(y for y in B if y["preview_card_id"]==c["preview_card_id"]).get("curated_HOLD_content_disposition_exists")
 print(json.dumps({"pass":True,"L03_cards":194,"total_cards":1571,"other_lessons_identical":True,"source_map_identical":True,"import_ready":False},indent=2))
