#!/usr/bin/env python3
"""Resolve a new lexical candidate to an existing *canonical* family owner.

Route is a security/scope check, NOT content Stage4 or a substitute for exact
SOURCE_CURRENT verification. Unknown and unattributed families fail closed.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROUTE="Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
NON_LEXICAL={"bildkarten-piloten","grammatik-aktiv-a1-b1","grammatik-aktiv-a1-c1",
 "grammatik-aktiv-b2-c1","lesen","schreiben"}

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()

def verify_family(family_id:str,review_path:Path,root:Path=ROOT)->dict:
    if not isinstance(family_id,str) or not re.fullmatch(r"family:[a-z0-9-]+",family_id):
        raise ValueError("INVALID_FAMILY_ID")
    reg_path=root/ROUTE
    if not reg_path.is_file() or reg_path.is_symlink():raise ValueError("MISSING_CANONICAL_FAMILY_ROUTER")
    reg=json.loads(reg_path.read_text(encoding="utf-8"))
    if reg.get("schema")!="gcpk-canonical-family-workspace-routing@1.0.0":
        raise ValueError("UNEXPECTED_FAMILY_ROUTER_VERSION")
    matches=[f for f in reg["families"] if f.get("family_id")==family_id]
    if len(matches)!=1:raise ValueError("UNKNOWN_OR_DUPLICATED_FAMILY")
    family=matches[0]
    if family_id.removeprefix("family:") in NON_LEXICAL:
        raise ValueError("NOT_STANDARD_LEXICAL_FAMILY")
    owner=family.get("canonical_git_workspace")
    if not isinstance(owner,str) or not owner.startswith("Workspaces/"):
        raise ValueError("LEXICAL_FAMILY_HAS_NO_ATTESTED_GIT_OWNER")
    parent=family.get("active_content_sha256")
    if not isinstance(parent,str) or not re.fullmatch("[a-f0-9]{64}",parent):
        raise ValueError("LEXICAL_FAMILY_CURATED_CURRENT_UNATTESTED")
    if not review_path.is_file() or review_path.is_symlink():
        raise ValueError("CROSS_TILE_REVIEW_MISSING_FOR_FAMILY")
    evidence=json.loads(review_path.read_text(encoding="utf-8"))
    if evidence.get("workstream") not in (owner,owner.removeprefix("Workspaces/")):
        raise ValueError("CROSS_TILE_WRONG_CANONICAL_OWNER")
    if evidence.get("curated_current_parent_sha256")!=parent:
        raise ValueError("CROSS_TILE_PARENT_IS_NOT_ATTESTED_CURRENT")
    if not family.get("route_state","").startswith("CANONICAL_ROUTED__USER_ACCEPTED_CURATED_OWNER_PIN"):
        raise ValueError("FAMILY_ROUTE_NOT_USER_ACCEPTED_CURATED_OWNER")
    return {"family_id":family_id,"canonical_git_workspace":owner,
        "parent_sha256":parent,"route_file_sha256":sha(reg_path.read_bytes()),
        "verified_scope":"FAMILY_OWNER_PIN_ONLY_NOT_STAGE4_OR_STAGE6"}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("family_id");p.add_argument("cross_tile_review",type=Path)
    a=p.parse_args()
    try:print(json.dumps(verify_family(a.family_id,a.cross_tile_review),ensure_ascii=False))
    except (ValueError,OSError,TypeError) as e:
        p.exit(2,"FAMILY_RELEASE_ROUTE_BLOCKED:"+str(e)+"\n")
