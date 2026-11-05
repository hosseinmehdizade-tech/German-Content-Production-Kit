#!/usr/bin/env python3
"""Fail closed on avoidable artifact churn. This gate does not delete files."""
import argparse
import json
from pathlib import Path

SHA = set('0123456789abcdef')

def sha_ok(s):
    return isinstance(s, str) and len(s) == 64 and all(c in SHA for c in s)

def evaluate(intent, inventory):
    errors = []
    def need(ok, code):
        if not ok: errors.append(code)
    need(isinstance(intent, dict) and isinstance(inventory, dict), 'INPUT_SHAPE')
    if not isinstance(intent, dict) or not isinstance(inventory, dict):
        return {'status':'BLOCKED', 'reasons':errors}
    kind = intent.get('kind')
    need(kind in ('MILESTONE', 'WORKING_RECOVERY', 'QA_ONLY'), 'UNKNOWN_ARTIFACT_CLASS')
    need(bool(intent.get('workstream')), 'WORKSTREAM_REQUIRED')
    before, after = intent.get('working_sha_before'), intent.get('working_sha_after')
    need(sha_ok(before) and sha_ok(after), 'CURRENT_BYTES_SHA_REQUIRED')
    need(intent.get('source_unchanged') is True, 'SOURCE_PROTECTION_UNPROVEN')
    need(inventory.get('verified_live_inventory') is True, 'LIVE_LIBRARY_INVENTORY_REQUIRED')
    assets = inventory.get('items')
    if not isinstance(assets,list):
        errors.append('LIBRARY_ITEMS_REQUIRED'); assets = []
    for a in assets:
        if not isinstance(a,dict) or not sha_ok(a.get('archive_sha256')) or not sha_ok(a.get('working_sha256')) or not isinstance(a.get('stage'),str) or a.get('role') not in ('IMMUTABLE','RELEASE','MILESTONE','ACTIVE_WORKING','HISTORICAL'):
            errors.append('UNVERIFIED_INVENTORY_ENTRY'); break
    if kind == 'QA_ONLY':
        errors.append('QA_ONLY_MUST_STAY_IN_GIT_OR_WORKSPACE_NO_NEW_ZIP')
    if sha_ok(after) and any(a.get('working_sha256') == after and a.get('stage') == intent.get('stage_after') for a in assets if isinstance(a,dict)):
        errors.append('EXACT_DUPLICATE_ALREADY_STORED')
    delta = intent.get('changed_units')
    need(type(delta) is int and delta >= 0, 'CHANGED_UNITS_REQUIRED')
    stage_change = intent.get('stage_before') != intent.get('stage_after')
    if kind == 'MILESTONE':
        need(stage_change, 'MILESTONE_WITHOUT_STAGE_TRANSITION')
        need(intent.get('stage_acceptance_evidence_verified') is True, 'MILESTONE_STAGE_GATE_UNVERIFIED')
    if kind == 'WORKING_RECOVERY':
        need(not stage_change, 'WORKING_RECOVERY_CANNOT_CHANGE_STAGE')
        need(delta is not None and delta > 0 and before != after, 'NO_SUBSTANTIVE_WORKING_DELTA')
        need(sum(a.get('role')=='ACTIVE_WORKING' for a in assets if isinstance(a,dict)) == 0, 'ACTIVE_WORKING_CHECKPOINT_ALREADY_EXISTS')
    if before == after and not stage_change:
        errors.append('NO_CONTENT_OR_STAGE_CHANGE')
    return {'status':'PASS_PREPUBLISH_ONLY' if not errors else 'BLOCKED', 'reasons':sorted(set(errors)),
            'note':'Gate checks intent and verified inventory manifest; no auto-upload, deletion, Stage4 or release signoff.'}

def self_test():
    A='a'*64;B='b'*64
    inv={'verified_live_inventory':True,'items':[{'archive_sha256':B,'working_sha256':A,'stage':'3','role':'MILESTONE'}]}
    base=dict(kind='MILESTONE',workstream='nvv',working_sha_before=A,working_sha_after=A,source_unchanged=True,stage_before='3',stage_after='4',changed_units=0,stage_acceptance_evidence_verified=True)
    good=evaluate(base,inv);assert good['status']=='PASS_PREPUBLISH_ONLY',good
    bad=dict(base,stage_after='3');assert evaluate(bad,inv)['status']=='BLOCKED'
    bad=dict(base,kind='QA_ONLY');assert 'QA_ONLY_MUST_STAY_IN_GIT_OR_WORKSPACE_NO_NEW_ZIP' in evaluate(bad,inv)['reasons']
    bad=dict(base,stage_acceptance_evidence_verified=False);assert 'MILESTONE_STAGE_GATE_UNVERIFIED' in evaluate(bad,inv)['reasons']
    bad=dict(base,working_sha_after=A);inv2={'verified_live_inventory':True,'items':[{'archive_sha256':B,'working_sha256':A,'stage':'4','role':'RELEASE'}]};assert 'EXACT_DUPLICATE_ALREADY_STORED' in evaluate(bad,inv2)['reasons']
    working=dict(base,kind='WORKING_RECOVERY',stage_after='3',working_sha_after=B,changed_units=3);assert evaluate(working,inv)['status']=='PASS_PREPUBLISH_ONLY'
    working['changed_units']=0;assert 'NO_SUBSTANTIVE_WORKING_DELTA' in evaluate(working,inv)['reasons']
    working['changed_units']=3;inv3={'verified_live_inventory':True,'items':[{'archive_sha256':B,'working_sha256':A,'stage':'3','role':'ACTIVE_WORKING'}]};assert 'ACTIVE_WORKING_CHECKPOINT_ALREADY_EXISTS' in evaluate(working,inv3)['reasons']
    inv4={'verified_live_inventory':False,'items':[]};assert 'LIVE_LIBRARY_INVENTORY_REQUIRED' in evaluate(base,inv4)['reasons']
    print('9/9 PASS (synthetic tests, not proof of global adoption)')

def main():
    p=argparse.ArgumentParser();p.add_argument('--intent');p.add_argument('--inventory');p.add_argument('--self-test',action='store_true');a=p.parse_args()
    if a.self_test:return self_test()
    if not a.intent or not a.inventory:p.error('--intent and --inventory required')
    try:
        result=evaluate(json.loads(Path(a.intent).read_text(encoding='utf-8')),json.loads(Path(a.inventory).read_text(encoding='utf-8')))
    except (OSError,ValueError) as e:
        print(json.dumps({'status':'BLOCKED','reasons':['INPUT_NOT_READABLE: '+str(e)]}));raise SystemExit(2)
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if result['status']=='PASS_PREPUBLISH_ONLY' else 2)
if __name__=='__main__':main()
