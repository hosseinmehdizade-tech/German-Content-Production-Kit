#!/usr/bin/env python3
from pathlib import Path
import argparse,json,hashlib,zipfile,tempfile,shutil,csv,subprocess

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("source_dir")
ap.add_argument("output_zip")
a=ap.parse_args()
src=Path(a.source_dir).resolve()
out=Path(a.output_zip).resolve()
if not src.is_dir():
    raise SystemExit("source_dir must be a directory; building from a previous delivery ZIP is forbidden")

def pick(patterns, role):
    files=[]
    for pat in patterns: files.extend(src.glob(pat))
    files=sorted(set(x for x in files if x.is_file()))
    if not files: raise SystemExit(f"missing required delivery role: {role}")
    return files[0]

direct=pick(["*Universal*.tsv","*import*.tsv","*cards*.tsv"],"direct-import-tsv")
if "source-inventory" in direct.name.lower() or "source_inventory" in direct.name.lower():
    raise SystemExit("source inventory TSV cannot satisfy direct-import-tsv")
canonical=pick(["*canonical*.json"],"canonical-json")
mapping=pick(["*source-output-map*.tsv"],"source-output-map-tsv")
qa=pick(["*verification*.json","*QA*.json","*qa*.json"],"qa-report")

with direct.open(encoding="utf-8-sig",newline="") as f:
    rows=list(csv.DictReader(f,delimiter="\t"))
if not rows: raise SystemExit("direct import TSV is empty")
cols=set(rows[0])
if not {"id","front","back"}<=cols:
    raise SystemExit("direct import TSV must contain id/front/back columns")

if "card_type" in cols:
    non_neutral=[(r.get("id") or "", (r.get("card_type") or "").strip()) for r in rows if (r.get("card_type") or "").strip() != "de-vocabulary"]
    if non_neutral:
        sample=non_neutral[:10]
        raise SystemExit(f"unified vocabulary envelope violation: expected card_type=de-vocabulary; found {sample}")

with tempfile.TemporaryDirectory(prefix="content-clean-stage-") as td:
    root=Path(td)/"CONTENT-DELIVERY"
    root.mkdir()
    for p in [direct,canonical,mapping,qa]:
        shutil.copy2(p,root/p.name)
    manifest={"artifact_type":"clean-content-delivery","delivery_policy":"v3.2.3-clean-staging","roles":{"direct-import-tsv":direct.name,"canonical-json":canonical.name,"source-output-map-tsv":mapping.name,"qa-report":qa.name}}
    (root/"DELIVERY-MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    files=sorted(x for x in root.iterdir() if x.is_file() and x.name!="SHA256SUMS.txt")
    (root/"SHA256SUMS.txt").write_text("\n".join(f"{sha256(x)}  {x.name}" for x in files)+"\n",encoding="utf-8")
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for x in sorted(root.iterdir()):
            if x.is_file(): z.write(x,arcname=f"{root.name}/{x.name}")

with tempfile.TemporaryDirectory(prefix="content-fresh-verify-") as td:
    td=Path(td)
    with zipfile.ZipFile(out) as z: z.extractall(td)
    root=next(p for p in td.iterdir() if p.is_dir())
    cp=subprocess.run(["sha256sum","-c","SHA256SUMS.txt"],cwd=root,text=True,capture_output=True)
    if cp.returncode: raise SystemExit(cp.stdout+cp.stderr)

print(json.dumps({"status":"PASS","zip":str(out),"sha256":sha256(out)},ensure_ascii=False))
