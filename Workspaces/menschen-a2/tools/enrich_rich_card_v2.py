#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,time
from copy import deepcopy
from datetime import date
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup,Tag

UA={'User-Agent':'Mozilla/5.0 (compatible; German-Content-Production-Kit/3.1.13; +https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit)'}
PREPS={'an','auf','aus','bei','durch','für','gegen','in','mit','nach','über','um','unter','von','vor','zu','zwischen'}
FIXED_CASE={'aus':'Dativ','außer':'Dativ','bei':'Dativ','mit':'Dativ','nach':'Dativ','seit':'Dativ','von':'Dativ','zu':'Dativ','gegenüber':'Dativ','durch':'Akkusativ','für':'Akkusativ','gegen':'Akkusativ','ohne':'Akkusativ','um':'Akkusativ'}

def norm(s): return re.sub(r'\s+',' ',str(s or '').replace('\u00ad',' ')).strip()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,o): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def lookup_lemma(h):
    h=norm(h); h=re.sub(r'^sich\s+','',h,flags=re.I); h=re.sub(r'\b(?:jdn\.?|jdm\.?|jmdn\.?|jmdm\.?|etw\.?|etwas)\b','',h,flags=re.I)
    toks=[t for t in re.split(r'\s+',h) if t]
    candidates=[t.strip('.,;:()[]') for t in toks if t.casefold().strip('.,;:()[]') not in PREPS and not t.startswith('+')]
    return candidates[-1] if candidates else ''
def heading_level(tag): return int(tag.name[1]) if isinstance(tag,Tag) and tag.name and re.fullmatch(r'h[1-6]',tag.name) else None
def section_nodes(soup,pattern):
    for h in soup.find_all(re.compile(r'^h[1-6]$')):
        title=norm(h.get_text(' ',strip=True))
        if re.search(pattern,title,re.I):
            lvl=heading_level(h); out=[]
            for sib in h.next_siblings:
                sl=heading_level(sib)
                if sl is not None and sl<=lvl: break
                out.append(sib)
            return out
    return []
def raw_lines(nodes):
    out=[]
    for n in nodes:
        if not isinstance(n,Tag): continue
        lis=n.find_all('li') if n.name!='li' else [n]
        for li in lis:
            text=norm(li.get_text(' ',strip=True))
            if text: out.append(text)
    return out
def parse_marked(lines,maxlen=240):
    out=[]; seen=set()
    for line in lines:
        m=re.match(r'^\s*\[([^\]]+)\]\s*(.*)$',line); sense=m.group(1).strip() if m else ''; text=m.group(2) if m else line
        text=norm(re.sub(r'\s*\(Audio\s*\(Info\)\)\s*',' ',text,flags=re.I)).strip(' ,;:')
        if not text or len(text)>maxlen: continue
        k=(sense,text.casefold())
        if k not in seen: seen.add(k); out.append({'sense':sense,'text':text})
    return out
def wiki_fetch(session,lemma):
    url='https://de.wiktionary.org/wiki/'+quote(lemma.replace(' ','_'),safe='')
    r=session.get(url,headers=UA,timeout=25); r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser')
    return {
      'url':url,
      'definitions':parse_marked(raw_lines(section_nodes(soup,r'^Bedeutungen'))),
      'collocations':parse_marked(raw_lines(section_nodes(soup,r'Charakteristische Wortkombinationen')),180),
      'synonyms':parse_marked(raw_lines(section_nodes(soup,r'^(Synonyme|Sinnverwandte Wörter)')),100),
      'antonyms':parse_marked(raw_lines(section_nodes(soup,r'^(Gegenwörter|Antonyme)')),100),
    }
def headword_preps(h): return [p for p in PREPS if re.search(rf'\b{re.escape(p)}\b',norm(h),re.I)]
def source_example(unit): return next((norm(x.get('text')) for x in unit.get('examples',[]) if isinstance(x,dict) and norm(x.get('text'))), '')
def source_preps(unit):
    hp=headword_preps(unit.get('headword',''))
    if hp: return hp
    ex=source_example(unit).casefold(); return [p for p in PREPS if re.search(rf'\b{re.escape(p)}\b',ex)][:2]
def sense_match(entries,anchors):
    if not entries: return None
    if anchors:
        for e in entries:
            low=e['text'].casefold()
            if any(re.search(rf'\b{re.escape(a)}\b',low) for a in anchors): return e
    return entries[0]
def same_sense(entries,sense,lemma,anchors,limit):
    out=[]; seen=set()
    for e in entries:
        if sense and e.get('sense') and sense.split(',')[0].strip()!=e['sense'].split(',')[0].strip(): continue
        text=norm(e.get('text')); low=text.casefold()
        if not text or text.casefold()==lemma.casefold(): continue
        if anchors and not any(re.search(rf'\b{re.escape(a)}\b',low) for a in anchors):
            # allow sense-marked relation even if it does not repeat the governed preposition
            if not (sense and e.get('sense')): continue
        if low not in seen: seen.add(low); out.append(text)
        if len(out)>=limit: break
    return out
def tatoeba_fetch(session,query,pages=3):
    results=[]
    for page in range(1,pages+1):
        url='https://tatoeba.org/en/api_v0/search?from=deu&query='+quote(query)+'&page='+str(page)
        r=session.get(url,headers=UA,timeout=25); r.raise_for_status(); data=r.json()
        batch=data.get('results') or []; results.extend(batch)
        if len(batch)<10: break
        time.sleep(.08)
    return results
def tatoeba_examples(items,anchors,reflexive,limit=5):
    out=[]; seen=set()
    for item in items:
        text=norm(item.get('text')); low=text.casefold()
        if not text or len(text)<12 or len(text)>180: continue
        if anchors and not all(re.search(rf'\b{re.escape(a)}\b',low) for a in anchors[:1]): continue
        if reflexive and not re.search(r'\b(mich|dich|sich|uns|euch)\b',low): continue
        en=''
        for grp in item.get('translations') or []:
            for tr in grp or []:
                if tr.get('lang')=='eng' and norm(tr.get('text')): en=norm(tr.get('text')); break
            if en: break
        if not en: continue
        k=text.casefold()
        if k in seen: continue
        seen.add(k); out.append({'sentence_id':item.get('id'),'text':text,'en':en})
        if len(out)>=limit: break
    return out
def derive_rection(unit):
    h=norm(unit.get('headword','')); raw=' '.join(norm(s.get('evidence_note')) for s in (unit.get('provenance') or {}).get('sources',[]) if isinstance(s,dict))
    vals=[]
    # Decode explicit source shorthand [+D]/[+A] when present in the authoritative raw bundle.
    case=''
    if re.search(r'\[\+D\]',raw,re.I): case='Dativ'
    elif re.search(r'\[\+A\]',raw,re.I): case='Akkusativ'
    for p in headword_preps(h):
        c=case or FIXED_CASE.get(p)
        if c: vals.append(f'{p} + {c}')
    # Explicit object placeholders without preposition.
    if not vals:
        if re.search(r'\bjdn\.?\b|\bjmdn\.?\b',h,re.I): vals.append('jemanden + Akkusativ')
        if re.search(r'\bjdm\.?\b|\bjmdm\.?\b',h,re.I): vals.append('jemandem + Dativ')
    return list(dict.fromkeys(vals))
def add_source(unit,source_id,claims,locator,note,status='verified'):
    if not claims: return
    srcs=unit.setdefault('provenance',{}).setdefault('sources',[])
    srcs.append({'source_id':source_id,'source_kind':'other','what_was_verified':sorted(set(claims)),'verification_status':status,'locator':locator,'accessed_at':str(date.today()),'evidence_note':note})

def enrich(ds,seed,cache,max_units=None,delay=.12):
    out=deepcopy(ds); sess=requests.Session(); attempts=[]; failures=[]; counts={'definitions_added':0,'tatoeba_examples_added':0,'collocations_added':0,'synonyms_added':0,'antonyms_added':0,'rection_added':0}
    wiki_cache=cache.setdefault('wiktionary',{}); tatoeba_cache=cache.setdefault('tatoeba',{})
    for idx,u in enumerate(out.get('learning_units',[])):
        if max_units and idx>=max_units: break
        uid=u['id']; typ=u.get('type'); lemma=lookup_lemma(u.get('headword','')); anchors=source_preps(u); claims=[]; sources=[]; success=False; errs=[]
        if not lemma:
            attempts.append({'id':uid,'type':typ,'status':'failed','sources':[],'reason':'lemma-resolution-failed'}); continue
        # Source/generated first example + current reviewed EN/FA translation seed.
        s=seed.get(uid,{})
        if not u.get('examples'):
            g=norm(s.get('german_example'))
            if g:
                u['examples']=[{'id':f'{uid}-ex-001','lang':'de-DE','text':g,'order':1,'translations':[]}]
                add_source(u,'assistant_pedagogical_example',[],f'generated://{uid}/example-1','Generated pedagogical example because source row had no usable example.',status='unverified')
        if u.get('examples'):
            ex=u['examples'][0]
            trs=[]
            if norm(s.get('translation_fa')): trs.append({'lang':'fa-IR','text':norm(s['translation_fa'])})
            if norm(s.get('translation_en')): trs.append({'lang':'en-US','text':norm(s['translation_en'])})
            if trs: ex['translations']=trs
        # Wiktionary evidence cached by lemma.
        wd=wiki_cache.get(lemma)
        if wd is None:
            try: wd=wiki_fetch(sess,lemma); wiki_cache[lemma]=wd; time.sleep(delay)
            except Exception as e: wd={'error':type(e).__name__+': '+str(e)}; wiki_cache[lemma]=wd
        if not wd.get('error'):
            success=True; sources.append('de_wiktionary_live')
            selected=sense_match(wd.get('definitions',[]),anchors); sense=selected.get('sense','') if selected else ''
            if typ=='verb' and selected and not norm(u.get('definition_de')):
                u['definition_de']=selected['text']; counts['definitions_added']+=1; claims.append('german_sense')
            if typ=='verb':
                coll=same_sense(wd.get('collocations',[]),sense,lemma,anchors,6)
                if coll:
                    existing={norm(x.get('text')).casefold() for x in u.get('connections',[]) if isinstance(x,dict) and x.get('kind')=='collocation'}
                    for x in coll:
                        if x.casefold() not in existing:
                            u.setdefault('connections',[]).append({'kind':'collocation','text':x}); existing.add(x.casefold()); counts['collocations_added']+=1
                    claims.append('collocation')
                syn=same_sense(wd.get('synonyms',[]),sense,lemma,anchors,3)
                if syn:
                    u.setdefault('details',{})['synonyms']=syn; counts['synonyms_added']+=len(syn); claims.append('synonymy')
                ant=same_sense(wd.get('antonyms',[]),sense,lemma,anchors,3)
                if ant:
                    u.setdefault('details',{})['antonyms']=ant; counts['antonyms_added']+=len(ant); claims.append('antonymy')
            if claims: add_source(u,'de_wiktionary_live',claims,wd.get('url',''),'Live German Wiktionary; definitions and lexical relations are accepted only from explicit sections and relations are restricted to the selected sense marker when available.')
        else: errs.append('wiktionary:'+wd['error'])
        # Deterministic explicit-headword rection.
        rv=derive_rection(u)
        if rv:
            d=u.setdefault('details',{}); old=d.get('rection') if isinstance(d.get('rection'),list) else []
            merged=list(dict.fromkeys(old+rv)); d['rection']=merged; counts['rection_added']+=max(0,len(merged)-len(old))
            add_source(u,'deterministic_headword_grammar',['rection'],f'canonical-headword://{uid}', 'Rektion decodes only explicit learner-facing placeholders/prepositions and explicit source [+A]/[+D] notation; no ambiguous case is guessed.')
        # Tatoeba corpus examples + human-authored English translations.
        query=' '.join(([lemma]+anchors[:1])) if anchors else lemma
        key=query.casefold(); td=tatoeba_cache.get(key)
        if td is None:
            try: td={'query':query,'results':tatoeba_fetch(sess,query)}; tatoeba_cache[key]=td; time.sleep(delay)
            except Exception as e: td={'query':query,'error':type(e).__name__+': '+str(e),'results':[]}; tatoeba_cache[key]=td
        if td.get('results'):
            success=True; sources.append('tatoeba_corpus')
            reflexive=bool((u.get('core') or {}).get('reflexive')) or norm(u.get('headword')).casefold().startswith('sich ')
            tx=tatoeba_examples(td['results'],anchors,reflexive,limit=6)
            existing={norm(x.get('text')).casefold() for x in u.get('examples',[]) if isinstance(x,dict)}
            ids=[]
            for item in tx:
                if len(u.get('examples',[]))>=5: break
                if item['text'].casefold() in existing: continue
                n=len(u.get('examples',[]))+1
                u.setdefault('examples',[]).append({'id':f'{uid}-ex-{n:03d}','lang':'de-DE','text':item['text'],'order':n,'translations':[{'lang':'en-US','text':item['en']}]})
                existing.add(item['text'].casefold()); ids.append(str(item['sentence_id'])); counts['tatoeba_examples_added']+=1
            if ids: add_source(u,'tatoeba_corpus',['example_attestation','english_example_translation'],'https://tatoeba.org/en/sentences/show/'+','.join(ids),'German example sentences and their English translations retrieved from Tatoeba search results; sentence IDs are retained in the locator.')
        elif td.get('error'): errs.append('tatoeba:'+td['error'])
        status='success' if success else ('failed' if errs else 'no_evidence')
        attempts.append({'id':uid,'type':typ,'headword':u.get('headword'),'lemma':lemma,'status':status,'sources':sources,'errors':errs,'examples_after':len(u.get('examples',[])),'has_definition':bool(norm(u.get('definition_de'))),'lexical_detail_count':sum(1 for c in u.get('connections',[]) if isinstance(c,dict) and norm(c.get('text')))+sum(len((u.get('details') or {}).get(f,[]) or []) for f in ('rection','synonyms','antonyms','variants'))})
        if errs: failures.append({'id':uid,'errors':errs})
    return out,attempts,failures,counts,cache

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--canonical',required=True); ap.add_argument('--seed',required=True); ap.add_argument('--out',required=True); ap.add_argument('--evidence',required=True); ap.add_argument('--cache',required=True); ap.add_argument('--max-units',type=int); ap.add_argument('--delay',type=float,default=.12); a=ap.parse_args()
    ds=load(a.canonical); seed=load(a.seed).get('items',{}); cp=Path(a.cache); cache=load(cp) if cp.exists() else {'schema_version':'1.0.0','accessed_at':str(date.today())}
    out,attempts,failures,counts,cache=enrich(ds,seed,cache,a.max_units,a.delay)
    if a.max_units:
        out['learning_units']=out['learning_units'][:a.max_units]
    dump(a.out,out); dump(a.cache,cache)
    verbs=[u for u in out.get('learning_units',[]) if u.get('type')=='verb']; phrases=[u for u in out.get('learning_units',[]) if u.get('type')=='phrase']
    ev={'schema_version':'2.0.0','dataset':'menschen-a2','stage':3,'status':'RUNNING','canonical_units':len(out.get('learning_units',[])),'external_lexical_enrichment_used':any(a['status']=='success' for a in attempts if a.get('type')=='verb'),'external_evidence_attempts':attempts,'failures':failures,'counts':counts,'coverage':{'verbs':len(verbs),'phrases':len(phrases),'verbs_with_definition':sum(bool(norm(u.get('definition_de'))) for u in verbs),'units_with_4plus_examples':sum(len(u.get('examples',[]))>=4 for u in out.get('learning_units',[])),'verbs_with_any_lexical_detail':sum((sum(1 for c in u.get('connections',[]) if isinstance(c,dict) and norm(c.get('text')))+sum(len((u.get('details') or {}).get(f,[]) or []) for f in ('rection','synonyms','antonyms','variants')))>0 for u in verbs)},'evidence_sources':['menschen_a2_user_screenshots','de_wiktionary_live','tatoeba_corpus','deterministic_headword_grammar','assistant_translation_review','assistant_pedagogical_example']}
    dump(a.evidence,ev); print(json.dumps(ev['coverage']|counts,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
