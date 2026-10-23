#!/usr/bin/env python3
import csv,hashlib,io,json,pathlib,sys,zipfile
work=pathlib.Path(__file__).resolve().parent
parent=pathlib.Path(sys.argv[1])
patch=json.loads((work/"ACTIVE-FA-EDIT-PATCH.json").read_text("utf-8"))
assert hashlib.sha256(parent.read_bytes()).hexdigest()==patch["parent_sha256"]
a_key="04-Enrichment-Work/ACCEPTED-KOMBINATIONEN-1934.json"
p_key="01-Final-Import/A1-VERBEN-PROJECTED-CARDS-KOMBINATIONEN.json"
t_key="01-Final-Import/A1-VERBEN-UNIVERSAL-v2-KOMBINATIONEN.tsv"
with zipfile.ZipFile(parent) as z:
 assert z.testzip() is None
 original={k:z.read(k) for k in (a_key,p_key,t_key)}
a=json.loads(original[a_key]);p=json.loads(original[p_key])
r=list(csv.DictReader(io.StringIO(original[t_key].decode("utf-8")),delimiter="\t"))
cols=list(r[0]);pc={x["id"]:x for x in p["cards"]};rows={x["id"]:x for x in r}
assert len(r)==len(pc)==len(a["items_by_card"])==310
def edit_item(items,e):
 match=[v for v in items if v["de"]==e["de"] and v["fa"]==e["before_fa"]]
 assert len(match)==1,(e["card_id"],e["de"],"ambiguous")
 match[0]["fa"]=e["after_fa"]
def edit_detail(details,e):
 ss=[s for s in details if s["title"]=="Kombinationen"]
 assert len(ss)==1
 old=e["de"]+" — "+e["before_fa"]
 assert ss[0]["items"].count(old)==1
 ss[0]["items"][ss[0]["items"].index(old)]=e["de"]+" — "+e["after_fa"]
for e in patch["edits"]:
 cid=e["card_id"];x=a["items_by_card"][cid];c=pc[cid];row=rows[cid]
 assert x["front"]==c["front"]==row["front"]
 edit_item(x["items"],e)
 backend=json.loads(x["accepted_combination_backend_json"])
 edit_item(backend["items"],e)
 x["accepted_combination_backend_json"]=json.dumps(backend,ensure_ascii=False,separators=(",",":"))
 edit_item(c["customFields"]["kombinationen_v1"]["items"],e)
 edit_detail(c["details"],e)
 cf=json.loads(row["custom_fields"]);edit_item(cf["kombinationen_v1"]["items"],e)
 row["custom_fields"]=json.dumps(cf,ensure_ascii=False)
 details=json.loads(row["details"]);edit_detail(details,e)
 row["details"]=json.dumps(details,ensure_ascii=False)
 assert cf["kombinationen_v1"]["items"]==c["customFields"]["kombinationen_v1"]["items"]
 assert details==c["details"]
w=io.StringIO(newline="");writer=csv.DictWriter(w,fieldnames=cols,delimiter="\t",lineterminator="\n")
writer.writeheader();writer.writerows(r)
payloads={
 "A1-VERBEN-ACCEPTED-KOMBINATIONEN-WORKING.json":(json.dumps(a,ensure_ascii=False,indent=2)+"\n").encode(),
 "A1-VERBEN-PROJECTED-CARDS-WORKING.json":(json.dumps(p,ensure_ascii=False,indent=2)+"\n").encode(),
 "A1-VERBEN-UNIVERSAL-v2-WORKING.tsv":w.getvalue().encode()}
assert sum(len(x["items"]) for x in a["items_by_card"].values())==1934
assert len({x["id"] for x in r})==310
expected=json.loads((work/"ACTIVE-FA-EDIT-QA.json").read_text("utf-8"))["outputs"]
for name,b in payloads.items():
 actual=hashlib.sha256(b).hexdigest()
 assert actual==expected[name]["after_sha256"],(name,actual)
 (work/name).write_bytes(b)
print("PASS scoped 20 edits, 310 IDs, 1934 items, all 3 SHA256 exact; NOT FINAL")
