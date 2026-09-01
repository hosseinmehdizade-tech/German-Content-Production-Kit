#!/usr/bin/env python3
from __future__ import annotations
import sys,time
from pathlib import Path
import requests
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_menschen_a1_v354_runtime_current as base

_CACHE={}
_original=base.fetch_wikitext

def fetch_wikitext_retry(session,lemma):
    key=lemma.casefold()
    if key in _CACHE:return _CACHE[key]
    last=None
    for attempt in range(5):
        try:
            result=_original(session,lemma)
            _CACHE[key]=result
            return result
        except requests.HTTPError as e:
            last=e
            status=getattr(e.response,'status_code',None)
            if status not in {429,502,503,504}:raise
            retry=getattr(e.response,'headers',{}).get('Retry-After') if getattr(e,'response',None) is not None else None
            try:wait=max(float(retry),1.0) if retry else 1.5*(attempt+1)
            except Exception:wait=1.5*(attempt+1)
            time.sleep(wait)
    raise last

base.fetch_wikitext=fetch_wikitext_retry
if __name__=='__main__':base.main()
