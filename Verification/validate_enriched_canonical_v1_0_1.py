#!/usr/bin/env python3
"""Structural/typed validation for enriched canonical content under v3.1.13.

Architecture v3.1.5 remains unchanged. This validator applies two explicit in-memory
compatibility overlays only for the post-enrichment artifact:

1. example cardinality 4..6, because the Stage-2 source profile is intentionally sparse;
2. optional ``details.rection`` on Phrase-Family units, using exactly the VERB rule's
   declared Rektion field specification.

The second overlay resolves a validator/type-rule integration gap: v3.1.13's Product
Floor requires explicit government for learner-facing phrase constructions such as
``sich an jdn. kuscheln`` or ``bestehen aus (Dat.)``, while Phrase-Family@2.0.1 did
not declare the otherwise canonical ``details.rection`` field. The overlay widens
validation only; it never creates, deletes, flattens, or weakens Rektion content.
Product completeness and evidence remain separate hard gates.
"""
from __future__ import annotations
import argparse,copy,importlib.util,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'Architecture/06-VALIDATION/validate_content.py'
spec=importlib.util.spec_from_file_location('gfp_validate_content',MOD)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)


def build_rules_overlay(type_rules_dir: Path):
    rules=copy.deepcopy(base.load_type_rules(type_rules_dir))
    verb=next((r for r in rules if 'verb' in r.get('applies_to',[])),None)
    phrase=next((r for r in rules if 'phrase' in r.get('applies_to',[])),None)
    if not verb or not phrase:
        raise ValueError('VERB and PHRASE-FAMILY type rules must both resolve')
    rection=(verb.get('detail_fields') or {}).get('rection')
    if not isinstance(rection,dict):
        raise ValueError('VERB rule must declare details.rection')
    phrase.setdefault('detail_fields',{})['rection']=copy.deepcopy(rection)
    return rules,verb.get('rule_id'),phrase.get('rule_id')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dataset',required=True,type=Path)
    ap.add_argument('--source-profile',required=True,type=Path)
    ap.add_argument('--type-rules',required=True,type=Path)
    ap.add_argument('--previous',type=Path)
    ap.add_argument('--source-registry',required=True,type=Path)
    ap.add_argument('--report',required=True,type=Path)
    ns=ap.parse_args()

    ds=base.load_json(ns.dataset)
    source_profile=base.load_json(ns.source_profile)
    profile=copy.deepcopy(source_profile)
    profile.setdefault('examples',{}).setdefault('default',{}).update({'target':5,'minimum':4,'maximum':6,'enforcement':'range'})
    rules,verb_rule_id,phrase_rule_id=build_rules_overlay(ns.type_rules)
    report=base.validate_dataset(
        ds,profile,rules,
        base.load_json(ns.previous) if ns.previous else None,
        base.load_json(ns.source_registry)
    )
    report['validator']='gfp-enriched-canonical-structural-overlay'
    report['overlay_version']='1.0.1'
    report['source_profile_id']=source_profile.get('profile_id')
    report['product_completeness_authority']=False
    report['architecture_mutated']=False
    report['overlays']={
        'examples':{'target':5,'minimum':4,'maximum':6,'enforcement':'range'},
        'phrase_rektion':{
            'purpose':'Permit canonical details.rection on Phrase-Family enriched units without mutating Architecture v3.1.5.',
            'phrase_rule_id':phrase_rule_id,
            'field_spec_copied_from':verb_rule_id+'.detail_fields.rection',
            'content_mutation':False
        }
    }
    ns.report.parent.mkdir(parents=True,exist_ok=True)
    ns.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report.get('structural_typed_status')=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
