#!/usr/bin/env python3
from pathlib import Path
import argparse,json,hashlib,zipfile,tempfile,shutil,csv,subprocess,sys,fnmatch,re

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("source_dir")
ap.add_argument("output_zip")
ap.add_argument("--purpose",choices=["stage5_acceptance","final_delivery","required_recovery","explicit_user_checkpoint"],default="stage5_acceptance")
a=ap.parse_args()
src=Path(a.source_dir).resolve()
out=Path(a.output_zip).resolve()
if not src.is_dir():
    raise SystemExit("source_dir must be a directory; building from a previous delivery ZIP is forbidden")
if re.search(r"(?i)(?:^|[-_.])(wip\d*|batch\d+|per[-_]?edit|scratch|micro[-_]?edit)(?:[-_.]|$)",out.stem) and a.purpose not in ("required_recovery","explicit_user_checkpoint"):
    raise SystemExit("CONTENT ZIP GUARD: routine WIP/batch/micro-edit archive refused; save editable data and compact QA instead")

def pick(patterns, role):
    # Delivery filenames are user/workstream artifacts and may vary in case
    # (for example A1-VERBEN-UNIVERSAL-v2.tsv). Resolve roles case-insensitively.
    files=[]
    for x in src.iterdir():
        if not x.is_file():
            continue
        name=x.name.lower()
        if any(fnmatch.fnmatch(name,pat.lower()) for pat in patterns):
            files.append(x)
    files=sorted(set(files),key=lambda x:x.name.lower())
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

# Unified ordinary-vocabulary presentation guard (v3.3.5+).
# This builder is itself a release gate: it MUST NOT rely on an upstream Stage 5
# validator having been run. Every direct-import vocabulary TSV must declare the
# neutral card_type explicitly and must pass the canonical validator here.
required_projection_cols={"id","front","back","card_type","category","custom_fields"}
missing_projection_cols=sorted(required_projection_cols-cols)
if missing_projection_cols:
    raise SystemExit(
        "unified vocabulary envelope violation: direct import TSV is missing required "
        f"columns {missing_projection_cols}; card_type=de-vocabulary is mandatory"
    )

non_neutral=[
    (r.get("id") or "", (r.get("card_type") or "").strip())
    for r in rows
    if (r.get("card_type") or "").strip() != "de-vocabulary"
]
if non_neutral:
    sample=non_neutral[:10]
    raise SystemExit(
        f"unified vocabulary envelope violation: expected card_type=de-vocabulary; found {sample}"
    )

validator=(Path(__file__).resolve().parents[1]/"Verification"/"validate_unified_vocabulary_projection_v1_1_0.py")
if not validator.is_file():
    raise SystemExit(f"unified vocabulary validator missing: {validator}")
validation=subprocess.run(
    [sys.executable,str(validator),str(direct)],
    text=True,capture_output=True
)
if validation.returncode:
    raise SystemExit(
        "unified vocabulary validation failed inside clean delivery builder:\n"
        + validation.stdout + validation.stderr
    )

# One tiny index per output directory avoids re-packaging identical input bytes
# under a new filename. It never deletes or scans historical archives.
input_signature=hashlib.sha256(json.dumps({
    "purpose":a.purpose,
    "source_roles":[sha256(p) for p in (direct,canonical,mapping,qa)]
},sort_keys=True).encode("utf-8")).hexdigest()
index_file=out.parent/".content-package-index.json"
if index_file.exists():
    try:
        package_index=json.loads(index_file.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise SystemExit(f"CONTENT ZIP GUARD: unreadable index; no unsafe rewrite: {exc}")
    if not isinstance(package_index,dict):
        raise SystemExit("CONTENT ZIP GUARD: invalid index")
else:
    package_index={}
prior=package_index.get(input_signature)
if prior and (out.parent/prior).is_file():
    raise SystemExit(f"CONTENT ZIP GUARD: identical content and QA already delivered as {prior}")

with tempfile.TemporaryDirectory(prefix="content-clean-stage-") as td:
    root=Path(td)/"CONTENT-DELIVERY"
    root.mkdir()
    for p in [direct,canonical,mapping,qa]:
        shutil.copy2(p,root/p.name)

    manifest={
      "artifact_type":"clean-content-delivery",
      "delivery_policy":"v3.3.5-clean-staging-semantic-presentation-separation",
      "unified_vocabulary_validation":"PASS_EMBEDDED_BUILDER_GATE",
      "unified_vocabulary_validator_version":"1.1.0",
      "required_card_type":"de-vocabulary",
      "required_presentation_contract":"gfp-vocabulary-neutral@1",
      "selector_scan":"TOP_LEVEL_PLUS_RECURSIVE_CUSTOM_FIELDS_CASE_INSENSITIVE",
      "roles":{
        "direct-import-tsv":direct.name,
        "canonical-json":canonical.name,
        "source-output-map-tsv":mapping.name,
        "qa-report":qa.name
      }
    }
    (root/"DELIVERY-MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    files=sorted(x for x in root.iterdir() if x.is_file() and x.name!="SHA256SUMS.txt")
    (root/"SHA256SUMS.txt").write_text(
      "\n".join(f"{sha256(x)}  {x.name}" for x in files)+"\n",encoding="utf-8"
    )

    if out.exists():
        raise SystemExit('Existing ZIP is immutable: refusing overwrite or unlink. Choose a new output only for a meaningful validated release.')
    with zipfile.ZipFile(out,"x",zipfile.ZIP_DEFLATED) as z:
        for x in sorted(root.iterdir()):
            if x.is_file(): z.write(x,arcname=f"{root.name}/{x.name}")

with tempfile.TemporaryDirectory(prefix="content-fresh-verify-") as td:
    td=Path(td)
    with zipfile.ZipFile(out) as z: z.extractall(td)
    root=next(p for p in td.iterdir() if p.is_dir())
    cp=subprocess.run(["sha256sum","-c","SHA256SUMS.txt"],cwd=root,text=True,capture_output=True)
    if cp.returncode: raise SystemExit(cp.stdout+cp.stderr)

# Record only verified outputs; existing archives remain immutable.
package_index[input_signature]=out.name
index_file.write_text(json.dumps(package_index,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":"PASS","zip":str(out),"sha256":sha256(out)},ensure_ascii=False))
