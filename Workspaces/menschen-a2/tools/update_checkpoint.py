#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('checkpoint',type=Path); ap.add_argument('--stage',type=int,required=True); ap.add_argument('--state',required=True); ap.add_argument('--pass-commit'); ap.add_argument('--summary'); ap.add_argument('--resume'); ap.add_argument('--blocker'); ns=ap.parse_args()
 cp=json.loads(ns.checkpoint.read_text(encoding='utf-8'))
 st=next(x for x in cp['stages'] if int(x['stage'])==ns.stage); st['state']=ns.state
 if ns.pass_commit is not None: st['pass_commit']=ns.pass_commit
 if ns.summary is not None: st['summary']=ns.summary
 if ns.resume is not None: cp['resume_instruction']=ns.resume
 if ns.blocker:
  cp.setdefault('blockers',[]).append({'stage':ns.stage,'reason':ns.blocker})
 elif ns.state=='PASS':
  cp['blockers']=[b for b in cp.get('blockers',[]) if b.get('stage')!=ns.stage]
 ns.checkpoint.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__': main()
