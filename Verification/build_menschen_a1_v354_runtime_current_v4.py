#!/usr/bin/env python3
from __future__ import annotations
import sys,time
from pathlib import Path
from urllib.parse import quote
import requests
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_menschen_a1_v354_runtime_current as base

_original_enrich=base.enrich

def chunks(xs,n):
    for i in range(0,len(xs),n):yield xs[i:i+n]

def prefetch(ds):
    lemmas=[];seen=set()
    for u in ds.get('learning_units',[]):
        if u.get('type')!='verb':continue
        l=base.lemma_from_headword(u.get('headword',''))
        if l and l.casefold() not in seen:seen.add(l.casefold());lemmas.append(l)
    cache={};s=requests.Session()
    for batch in chunks(lemmas,25):
        params={'action':'query','titles':'|'.join(batch),'prop':'revisions','rvprop':'content','rvslots':'main','format':'json','formatversion':'2','redirects':'1'}
        last=None
        for attempt in range(5):
            try:
                r=s.get(base.API,params=params,headers=base.HEADERS,timeout=30)
                if r.status_code in {429,502,503,504}:
                    last=requests.HTTPError(f'{r.status_code}',response=r);time.sleep(2.0*(attempt+1));continue
                r.raise_for_status();data=r.json();break
            except requests.RequestException as e:
                last=e;time.sleep(2.0*(attempt+1))
        else:raise last
        q=data.get('query',{});alias={}
        for x in q.get('normalized',[]) or []:alias[x.get('from')]=x.get('to')
        for x in q.get('redirects',[]) or []:alias[x.get('from')]=x.get('to')
        pages={p.get('title'):p for p in q.get('pages',[]) or []}
        def target(name):
            cur=name
            for _ in range(5):
                nxt=alias.get(cur)
                if not nxt or nxt==cur:break
                cur=nxt
            return cur
        for lemma in batch:
            t=target(lemma);p=pages.get(t)
            if not p:
                # Case-normalization fallback.
                p=next((v for k,v in pages.items() if str(k).casefold()==str(t).casefold()),None)
            if p and p.get('revisions'):
                rev=p['revisions'][0];content=((rev.get('slots') or {}).get('main') or {}).get('content')
                if content is not None:cache[lemma.casefold()]=(content,'https://de.wiktionary.org/wiki/'+quote(str(p.get('title') or lemma),safe=''))
        time.sleep(.8)
    return cache

def enrich_prefetched(ds,delay=.0):
    cache=prefetch(ds)
    def cached(session,lemma):
        v=cache.get(lemma.casefold())
        if not v:raise RuntimeError('WIKTIONARY_PAGE_MISSING')
        return v
    base.fetch_wikitext=cached
    out,rep=_original_enrich(ds,0)
    rep['wiktionary_batch_prefetched']=len(cache)
    return out,rep

base.enrich=enrich_prefetched
if __name__=='__main__':base.main()
