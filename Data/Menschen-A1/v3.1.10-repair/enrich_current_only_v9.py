#!/usr/bin/env python3
from __future__ import annotations
import re
import enrich_current_only_v2 as base
import enrich_current_only_v7 as v7
import enrich_current_only_v8 as v8

_ORIGINAL=v7.derive_rection

def safe_rection(headword):
    vals=_ORIGINAL(headword)
    if vals: return vals
    h=' '+base.norm(headword).casefold()+' '
    fixed={'aus':'Dativ','außer':'Dativ','bei':'Dativ','mit':'Dativ','nach':'Dativ','seit':'Dativ','von':'Dativ','zu':'Dativ','gegenüber':'Dativ','durch':'Akkusativ','für':'Akkusativ','gegen':'Akkusativ','ohne':'Akkusativ','um':'Akkusativ'}
    for prep,case in fixed.items():
        if re.search(rf'\b{re.escape(prep)}\s+',h): return [f'{prep} + {case}']
    return []

v8.derive_rection_v8=safe_rection
base.enrich=v8.enrich_v8

if __name__=='__main__':
    base.main()
