#!/usr/bin/env python3
"""Menschen A2 rich-card linguistic QA v3.

v3 keeps the proven v2 checks but removes the historical/stale generated-example
allowlist. Under active v3.1.13, learner examples added merely to satisfy density are
not an expected production class; the expected generated fallback set is empty.
Reflexive example/collocation sense-surface integrity is enforced separately by
``audit_reflexive_alignment_v1.py`` in the same Stage 4 gate.
"""
from __future__ import annotations
import json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import linguistic_qa_v2 as v2

v2.EXPECTED_GENERATED=set()

if __name__=='__main__':
    out=None
    if '--output' in sys.argv:
        try: out=Path(sys.argv[sys.argv.index('--output')+1])
        except Exception: out=None
    rc=0
    try:
        v2.main()
    except SystemExit as e:
        rc=int(e.code or 0)
    if out and out.exists():
        report=json.loads(out.read_text(encoding='utf-8'))
        report['validator_version']='3.0.0'
        report['generated_fallback_policy']='forbidden-in-production; expected set is empty'
        report['reflexive_alignment_companion']='REFLEXIVE-ALIGNMENT-AUDIT.json'
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(rc)
