#!/usr/bin/env python3
"""Stage5 wrapper: run source-neutral learner-visible morphology transport gate BEFORE official clean builder.

This wrapper doesn't alter canonical data, cards, importer, presentation UI or SRS; it only
makes the currently optional transport check mandatory for producers opting into this tool.
Producer-specific adoption must be separately tested; --min-checked can enforce expected scope.
"""
import argparse, csv, json, subprocess, sys
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('source_dir',type=Path)
parser.add_argument('output_zip',type=Path)
parser.add_argument('--purpose',choices=['stage5_acceptance','final_delivery','validated_major_checkpoint','required_recovery','explicit_user_checkpoint'],default='stage5_acceptance')
parser.add_argument('--min-checked',type=int,default=1)
parser.add_argument('--milestone-evidence',type=Path)
parser.add_argument('--user-request')
parser.add_argument('--family-id')
parser.add_argument('--receipt',type=Path)
parser.add_argument('--policy-report',type=Path)
parser.add_argument('--stage4-receipt',type=Path)
parser.add_argument('--cross-tile-review',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parent.parent
sourcedir=args.source_dir.resolve()
options=list(sourcedir.glob('*cards.tsv'))
if len(options)!=1:
    raise SystemExit('FRONT_GATE_INPUT: expected exactly one *cards.tsv input, found '+str(len(options)))
validator=root/'Verification'/'validate_lexical_front_projection_transport_v1.py'
cmd=[sys.executable,str(validator),str(options[0])]
try:
    gate=subprocess.run(cmd,check=False,text=True,capture_output=True)
    result=json.loads(gate.stdout)
except (ValueError, OSError) as exc:
    raise SystemExit('FRONT_GATE_BAD_OUTPUT '+str(exc))
if gate.returncode or result.get('status')!='PASS':
    raise SystemExit('FRONT_GATE_BLOCKED '+json.dumps({'status':result.get('status'),
        'checked':result.get('checked_source_attested_cards'),'issues':result.get('issues'),'samples':result.get('samples',[])[:2]},ensure_ascii=False))
if result.get('checked_source_attested_cards',0)<args.min_checked:
    raise SystemExit('FRONT_GATE_INSUFFICIENT_COVERAGE')
print('FRONT_GATE_PASS '+json.dumps({'checked':result['checked_source_attested_cards'],'source_attested_fields':result['source_attested_form_fields']},ensure_ascii=False),flush=True)
# The morphology transport PASS is not content/semantic approval.
# New lexical acceptance MUST go via the cross-family source-owner + Stage4 gate.
if args.purpose == 'stage5_acceptance':
    required={
        'family-id':args.family_id,
        'receipt':args.receipt,
        'policy-report':args.policy_report,
        'stage4-receipt':args.stage4_receipt,
        'cross-tile-review':args.cross_tile_review}
    missing=[name for name,value in required.items() if value is None or value=='']
    if missing:
        raise SystemExit('LEXICAL_QUALITY_EVIDENCE_REQUIRED_BEFORE_STAGE5:'+','.join(missing))
    cmd=[sys.executable,str(root/'Tools'/'build_quality_gated_lexical_candidate_v1.py'),
         str(sourcedir),str(args.output_zip.resolve()),
         '--family-id',args.family_id,
         '--receipt',str(args.receipt),'--policy-report',str(args.policy_report),
         '--stage4-receipt',str(args.stage4_receipt),
         '--cross-tile-review',str(args.cross_tile_review)]
elif args.purpose in ('required_recovery','explicit_user_checkpoint'):
    # Archival/recovery copies retain their existing immutable package guard.
    # They do NOT constitute Stage4/Stage5 acceptance.
    print('RECOVERY_OR_USER_CHECKPOINT_ONLY_NOT_CONTENT_ACCEPTANCE',flush=True)
    cmd=[sys.executable,str(root/'Tools'/'build_clean_delivery.py'),str(sourcedir),
         str(args.output_zip.resolve()),'--purpose',args.purpose]
    if args.milestone_evidence:
        cmd.extend(['--milestone-evidence',str(args.milestone_evidence)])
    if args.user_request:cmd.extend(['--user-request',args.user_request])
else:
    raise SystemExit('FINAL_OR_VALIDATED_STAGE5_REQUIRES_DISTINCT_GOVERNED_RELEASE_PROOF')
completed=subprocess.run(cmd,check=False)
raise SystemExit(completed.returncode)
