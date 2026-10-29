#!/usr/bin/env python3
from pathlib import Path
import argparse,json,hashlib,zipfile,tempfile,shutil,csv,subprocess,sys,fnmatch
from content_package_guard import guarded_zip, check_intent, PackageGuardError

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("source_dir")
ap.add_argument("output_zip")
ap.add_argument("--purpose",choices=["stage5_acceptance","final_delivery","validated_major_checkpoint","required_recovery","explicit_user_checkpoint"],default="stage5_acceptance")
ap.add_argument("--milestone-evidence",type=Path)
ap.add_argument("--user-request")
ap.add_argument("--applied-edit-proof", type=Path,
                help="Optional scoped proof of actual CURRENT TSV edit; validates local bytes only, not remote Git/Library CAS")
a=ap.parse_args()
src=Path(a.source_dir).resolve()
out=Path(a.output_zip).resolve()
if not src.is_dir():
    raise SystemExit("source_dir must be a directory; building from a previous delivery ZIP is forbidden")
try:
    check_intent(out,a.purpose,evidence=a.milestone_evidence,user_request=a.user_request)
except PackageGuardError as exc:
    raise SystemExit("CONTENT ZIP GUARD: "+str(exc))

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

# OP-01 opt-in proof: verify *actual* current bytes selected for Stage5, rather
# than merely trusting an APPLIED label in a supplied QA or editor's report.
# Default remains backward compatible; no content workstream is promoted.
applied_proof_receipt = None
if a.applied_edit_proof is not None:
    proof_file = a.applied_edit_proof.resolve()
    verifier_root = Path(__file__).resolve().parents[1] / "Verification"
    sys.path.insert(0, str(verifier_root))
    from validate_applied_edit_bytes import verify as verify_applied_edit
    try:
        proof = json.loads(proof_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit("APPLIED EDIT PROOF: missing or unreadable proof") from exc
    if not isinstance(proof, dict) or proof.get("format") != "TSV_ITEMS_V1":
        raise SystemExit("APPLIED EDIT PROOF: clean delivery accepts TSV_ITEMS_V1 only")
    errors = verify_applied_edit(proof_file)
    if errors:
        raise SystemExit("APPLIED EDIT PROOF: " + " | ".join(errors))
    if proof.get("sha256", {}).get("current") != sha256(direct):
        raise SystemExit("APPLIED EDIT PROOF: selected Stage5 TSV differs from verified CURRENT")
    applied_proof_receipt = {
        "status": "PASS_SCOPED_LOCAL_BYTE_PROOF_NOT_REMOTE_PERSISTENCE",
        "current_tsv_sha256": sha256(direct),
        "proof_file_sha256": sha256(proof_file),
        "source": "Verification/validate_applied_edit_bytes.py",
        "remote_git_or_library_cas_verified": False,
        "linguistic_stage4_certified": False
    }
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
      "optional_applied_edit_proof": applied_proof_receipt,
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

    with guarded_zip(out,purpose=a.purpose,inputs=(direct,canonical,mapping,qa),
                     evidence=a.milestone_evidence,user_request=a.user_request) as z:
        for x in sorted(root.iterdir()):
            if x.is_file(): z.write(x,arcname=f"{root.name}/{x.name}")

with tempfile.TemporaryDirectory(prefix="content-fresh-verify-") as td:
    td=Path(td)
    with zipfile.ZipFile(out) as z: z.extractall(td)
    root=next(p for p in td.iterdir() if p.is_dir())
    cp=subprocess.run(["sha256sum","-c","SHA256SUMS.txt"],cwd=root,text=True,capture_output=True)
    if cp.returncode: raise SystemExit(cp.stdout+cp.stderr)

print(json.dumps({"status":"PASS","zip":str(out),"sha256":sha256(out)},ensure_ascii=False))
