#!/usr/bin/env python3
"""Structural/typed validation for an enriched canonical artifact.

The dataset keeps its Stage-2 source profile_id. This wrapper applies only a named
post-enrichment cardinality overlay to the validator's in-memory profile so a sparse
source-canonical profile cannot either (a) reject legitimate product enrichment or
(b) masquerade as product-completeness authority. Product completeness remains a
separate mandatory gate.
"""
from __future__ import annotations
import argparse,copy,importlib.util,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'Architecture/06-VALIDATION/validate_content.py'
spec=importlib.util.spec_from_file_location('gfp_validate_content',MOD)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True,type=Path);ap.add_argument('--source-profile',required=True,type=Path);ap.add_argument('--type-rules',required=True,type=Path);ap.add_argument('--previous',type=Path);ap.add_argument('--source-registry',required=True,type=Path);ap.add_argument('--report',required=True,type=Path);ns=ap.parse_args()
    ds=base.load_json(ns.dataset);source_profile=base.load_json(ns.source_profile);profile=copy.deepcopy(source_profile)
    # This overlay is structural only. It must not be cited as product completeness.
    profile.setdefault('examples',{}).setdefault('default',{}).update({'target':5,'minimum':4,'maximum':6,'enforcement':'range'})
    report=base.validate_dataset(ds,profile,base.load_type_rules(ns.type_rules),base.load_json(ns.previous) if ns.previous else None,base.load_json(ns.source_registry))
    report['validator']='gfp-enriched-canonical-structural-overlay'
    report['overlay_version']='1.0.0'
    report['source_profile_id']=source_profile.get('profile_id')
    report['product_completeness_authority']=False
    report['overlay']={'examples':{'target':5,'minimum':4,'maximum':6,'enforcement':'range'},'purpose':'Allow post-enrichment structural validation while preserving the exact Stage-2 source profile identity. Product completeness is validated separately.'}
    ns.report.parent.mkdir(parents=True,exist_ok=True);ns.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report.get('structural_typed_status')=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
