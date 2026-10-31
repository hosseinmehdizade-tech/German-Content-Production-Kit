#!/usr/bin/env python3
"""Fail-closed Stage4 risk-based acceptance, based on review evidence, not perfection.
This never signs off linguistic correctness itself; it checks admissibility of genuine review evidence.
"""
import argparse
import json
import hashlib
from pathlib import Path

DECISIONS = {'KEEP_WITH_REASON', 'CORRECTED_VERIFIED', 'CLOSED_NO_FORCE', 'HOLD'}

def _hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for part in iter(lambda: fh.read(1048576), b''): h.update(part)
    return h.hexdigest()

def evaluate(policy, receipt, source_path=None):
    blockers = []
    def need(ok, code):
        if not ok: blockers.append(code)
    anchor = receipt.get('authority', {})
    need(bool(anchor.get('working_sha256')) and bool(anchor.get('registered_source_sha256')), 'AUTHORITY_UNPINNED')
    need(anchor.get('source_unchanged') is True, 'IMMUTABLE_SOURCE_UNPROVEN')
    if source_path is not None:
        need(_hash(source_path) == anchor.get('working_sha256'), 'WORKING_BYTES_SHA_MISMATCH')
    mech = receipt.get('mechanical', {})
    need(mech.get('full_population_checked') is True, 'NOT_100_PERCENT_MECHANICAL_COVERAGE')
    for key in ('identity', 'source_fidelity', 'examples', 'translations_present', 'relationships', 'render_projection', 'source_immutability'):
        need(mech.get('checks', {}).get(key) == 'PASS', 'MECHANICAL_' + key.upper())
    if not isinstance(mech.get('counts'), dict) or any(not isinstance(mech['counts'].get(k), int) or mech['counts'][k] < 0 for k in ('cards','examples','visible_combos')):
        blockers.append('INVALID_UNIVERSE_COUNTS')
    scan = receipt.get('risk_scan', {})
    identified = scan.get('flagged_ids', [])
    need(scan.get('full_population_checked') is True, 'RISK_DISCOVERY_NOT_FULL')
    valid_ids = (isinstance(identified, list)
                 and all(type(uid) is str and bool(uid.strip()) for uid in identified)
                 and len(identified) == len(set(identified)))
    need(valid_ids, 'RISK_FLAG_IDENTITIES_NOT_UNIQUE_OR_MALFORMED')
    # A claimed scan cannot silently omit risk severities, or an unresolved
    # HIGH/CRITICAL alert can be laundered into an accepted LOW/HOLD review.
    # This checks internal receipt integrity, not independent scan authenticity.
    scan_records = scan.get('flagged_items')
    scan_by_id = {}
    if not isinstance(scan_records, list):
        blockers.append('RISK_SCAN_DETAIL_REQUIRED')
    else:
        for record in scan_records:
            if not isinstance(record, dict):
                blockers.append('RISK_SCAN_RECORD_MALFORMED')
                continue
            rid = record.get('id')
            if type(rid) is not str or not rid.strip() or rid in scan_by_id:
                blockers.append('RISK_SCAN_DUPLICATE_OR_MISSING_ITEM_ID')
                continue
            severity = record.get('severity')
            flags = record.get('flags')
            if severity not in ('CRITICAL','HIGH','MEDIUM','LOW','INFO'):
                blockers.append('RISK_SCAN_ITEM_SEVERITY_MISSING_OR_INVALID:'+rid)
            if (not isinstance(flags, list) or not flags
                    or any(type(flag) is not str or not flag.strip() for flag in flags)
                    or len(flags) != len(set(flags))):
                blockers.append('RISK_SCAN_ITEM_FLAGS_MISSING_OR_INVALID:'+rid)
            scan_by_id[rid] = record
        if valid_ids:
            need(set(scan_by_id) == set(identified),
                 'RISK_SCAN_ITEM_IDS_DIFFER_FROM_FLAGGED_IDS')
    review = receipt.get('risk_dispositions', [])
    need(isinstance(review, list), 'RISK_REVIEW_INVALID')
    per_id = {}
    for item in review if isinstance(review, list) else []:
        if not isinstance(item, dict):
            blockers.append('RISK_REVIEW_RECORD_MALFORMED')
            continue
        uid = item.get('id')
        if type(uid) is not str or not uid.strip() or uid in per_id:
            blockers.append('DUPLICATE_OR_MISSING_RISK_ID'); continue
        per_id[uid] = item
        sev = item.get('severity')
        decision = item.get('decision')
        need(sev in ('CRITICAL','HIGH','MEDIUM','LOW','INFO'), 'INVALID_RISK_SEVERITY:'+str(uid))
        if uid not in scan_by_id:
            blockers.append('RISK_REVIEW_ID_NOT_IN_SCAN:'+uid)
        elif sev != scan_by_id[uid].get('severity'):
            blockers.append('RISK_SEVERITY_DISAGREES_WITH_SCAN:'+uid)
        need(decision in DECISIONS, 'INVALID_RISK_DISPOSITION:'+str(uid))
        need(bool(str(item.get('reason','')).strip()) and item.get('evidence_sha256') == anchor.get('working_sha256'), 'MISSING_RISK_REASON_OR_CURRENT_EVIDENCE:'+str(uid))
        if decision == 'HOLD' and sev in ('CRITICAL','HIGH'):
            blockers.append('UNRESOLVED_CRITICAL_OR_HIGH:'+str(uid))
        if decision == 'CORRECTED_VERIFIED':
            need(item.get('post_edit_verified') is True, 'UNVERIFIED_CORRECTION:'+str(uid))
        if item.get('source_claim') == 'VERBATIM':
            need(item.get('verbatim_locator_verified') is True, 'UNVERIFIED_VERBATIM_CLAIM:'+str(uid))
    # Family-level closure for low/medium advisory signals is allowed, but NEVER a blanket signoff.
    # All exact affected IDs, a typed scanner trigger, and representative independent reviews
    # (at least 5 or 10% per family) are mandatory. CRITICAL/HIGH are always individual.
    family_covered=set()
    all_flags={uid:set(z['flags']) for uid,z in scan_by_id.items()
               if isinstance(z.get('flags'),list) and all(isinstance(x,str) for x in z['flags'])}
    for fam in receipt.get('risk_family_dispositions',[]):
        gid=fam.get('rule_id','?')
        affected=fam.get('affected_ids',[]);trigger=fam.get('trigger_flags',[])
        need(fam.get('severity') in ('MEDIUM','LOW','INFO'), 'FAMILY_HIGH_RISK_NOT_ALLOWED:'+gid)
        need(bool(gid) and bool(trigger) and bool(fam.get('reason')) and fam.get('evidence_sha256') == anchor.get('working_sha256') and fam.get('independent_challenge') is True, 'FAMILY_NOT_EVIDENCED:'+gid)
        need(isinstance(affected,list) and len(affected)==len(set(affected)) and bool(affected) and set(affected).issubset(set(identified)), 'FAMILY_INVALID_MEMBERS:'+gid)
        need(all(a in all_flags and all_flags[a].intersection(set(trigger)) for a in affected), 'FAMILY_TRIGGER_NOT_VERIFIED:'+gid)
        scan_severity={uid:z.get('severity') for uid,z in scan_by_id.items()}
        need(not any(scan_severity.get(a) in ('CRITICAL','HIGH') for a in affected), 'FAMILY_CONTAINS_HIGH_RISK:'+gid)
        rank={'INFO':0,'LOW':1,'MEDIUM':2,'HIGH':3,'CRITICAL':4}
        need(all(rank.get(fam.get('severity'),-1)>=rank.get(scan_severity.get(a),5)
                 for a in affected), 'FAMILY_SEVERITY_DOWNGRADED:'+gid)
        rev=fam.get('representative_reviews',[])
        minimum=min(len(affected),max(5,(len(affected)+9)//10))
        need(len(rev)>=minimum,'FAMILY_UNDERSAMPLED:'+gid)
        expected_representatives=set(sorted(affected,key=lambda u:hashlib.sha256((str(anchor.get('working_sha256'))+'|'+u).encode()).digest())[:minimum])
        need(expected_representatives.issubset({z.get('id') for z in rev}), 'FAMILY_NONDETERMINISTIC_SAMPLE:'+gid)
        for z in rev:
            need(z.get('id') in affected and z.get('evidence_sha256')==anchor.get('working_sha256') and bool(z.get('reason')) and z.get('decision') in ('KEEP_WITH_REASON','CLOSED_NO_FORCE','CORRECTED_VERIFIED'),'FAMILY_REVIEW_INVALID:'+gid)
        if family_covered.intersection(set(affected)):
            blockers.append('DUPLICATE_FAMILY_COVERAGE:'+gid)
        family_covered.update(affected)
    if isinstance(identified,list):
        need(set(identified).issubset(set(per_id)|family_covered), 'UNRESOLVED_RISK_FLAGS:' + str(len(set(identified)-(set(per_id)|family_covered))))
    # Allow a modest documented non-critical residual risk, never a hard source-fidelity bypass.
    residual = [v for v in per_id.values() if v.get('decision') == 'HOLD' and v.get('severity') in ('MEDIUM','LOW','INFO')]
    need(len(residual) <= policy['acceptance']['max_documented_noncritical_holds'], 'TOO_MANY_DOCUMENTED_HOLDS')
    for v in residual:
        need(bool(v.get('owner')) and bool(v.get('followup_trigger')), 'UNMANAGED_NONCRITICAL_HOLD:'+str(v.get('id')))
    sample = receipt.get('sample', {})
    need(sample.get('method') == 'HASH_DETERMINISTIC_STRATIFIED' and sample.get('seed') == anchor.get('working_sha256'), 'SAMPLE_SELECTION_NOT_PINNED')
    strata = sample.get('strata', [])
    profile = policy.get('profiles',{}).get(receipt.get('workstream',''),{})
    min_strata = profile.get('min_strata', policy['sampling']['min_strata'])
    need(isinstance(strata,list) and len(strata) >= min_strata, 'INSUFFICIENT_STRATA')
    ids = set()
    for s in strata if isinstance(strata,list) else []:
        label = str(s.get('name',''))
        need(label and label not in ids, 'DUPLICATE_STRATUM'); ids.add(label)
        for kind, minimum in (('cards',policy['sampling']['min_cards_per_stratum']),('examples',policy['sampling']['min_examples_per_stratum']),('visible_combos',policy['sampling']['min_combos_per_stratum'])):
            available = s.get('population',{}).get(kind)
            records = s.get('reviewed',{}).get(kind,[])
            need(isinstance(available,int) and available>=0 and isinstance(records,list), 'BAD_SAMPLE_UNIVERSE:'+label+':'+kind)
            if isinstance(available,int) and isinstance(records,list):
                need(len(records)>=min(available,minimum), 'SAMPLE_UNDERCOVERAGE:'+label+':'+kind)
                need(len(set(str(a.get('id')) for a in records))==len(records), 'DUPLICATE_SAMPLE_ID:'+label+':'+kind)
            plan=s.get('planned_ids',{}).get(kind)
            if plan is not None and isinstance(records,list):
                need(set(plan).issubset({z.get('id') for z in records}), 'PLANNED_SAMPLE_NOT_REVIEWED:'+label+':'+kind)
            for item in records if isinstance(records,list) else []:
                need(item.get('decision') in ('KEEP_WITH_REASON','CORRECTED_VERIFIED','CLOSED_NO_FORCE') and bool(item.get('reason')) and item.get('evidence_sha256') == anchor.get('working_sha256'), 'UNREVIEWED_SAMPLE:'+label+':'+kind)
    expected = set(profile.get('expected_strata', []))
    need(not expected or expected.issubset(ids), 'REQUIRED_STRATA_MISSING')
    independent = receipt.get('adversarial', {})
    need(independent.get('separate_method') is True and independent.get('challenge_evidence_sha256') == anchor.get('working_sha256'), 'NO_INDEPENDENT_METHOD_REVIEW')
    need(independent.get('seeded_negative_controls_passed', 0) >= policy['acceptance']['min_negative_controls'], 'INSUFFICIENT_NEGATIVE_CONTROLS')
    need(independent.get('systemic_error_clusters_resolved') is True, 'SYSTEMIC_ERROR_CLUSTER_OPEN')
    need(receipt.get('scope_is_exact_current') is True, 'SCOPE_CURRENTNESS_UNPROVEN')
    status = 'PASS_RISK_BASED_STAGE4' if not blockers else 'BLOCKED_RISK_BASED_STAGE4'
    return {'schema':'risk-based-stage4-gate-result@1.0.0','status':status,'source_sha256':anchor.get('working_sha256'), 'blockers':sorted(set(blockers)),'counts':{'risk_ids':len(identified) if isinstance(identified,list) else None,'risk_dispositions':len(per_id),'sampled_strata':len(strata) if isinstance(strata,list) else None}, 'note':'A PASS is evidence-backed risk acceptance, not proof of 100 percent linguistic correctness. Stage5–7 are independent.'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--policy',required=True)
    p.add_argument('--receipt',required=True)
    p.add_argument('--current-bytes')
    p.add_argument('--output')
    a=p.parse_args()
    policy=json.loads(Path(a.policy).read_text())
    receipt=json.loads(Path(a.receipt).read_text())
    result=evaluate(policy,receipt,a.current_bytes)
    if a.output:Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if result['status'].startswith('PASS') else 2)
if __name__=='__main__':main()