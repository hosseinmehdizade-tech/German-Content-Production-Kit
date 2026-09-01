#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, time
from copy import deepcopy
from pathlib import Path
from urllib.parse import quote
import requests

HEADERS={"User-Agent":"Mozilla/5.0 (compatible; German-Content-Production-Kit/3.1.11)"}
API='https://de.wiktionary.org/w/api.php'
TSV_HEADERS=['id','card_type','domain','category','source','level','lesson','deck','front','back','front_label','back_label','front_lang','back_lang','typing_target','examples','related','opposites','details','custom_fields','tags','notes','order']
STOP={'der','die','das','den','dem','des','ein','eine','einen','einem','einer','eines','und','oder','mit','von','zu','in','auf','für','an','über','unter','vor','nach','bei','aus','sich','etwas','jemand','jemanden','jemandem','sein','haben','werden','können','müssen','sollen','wollen','dürfen','sehr','nicht','noch'}

def norm(x):return re.sub(r'\s+',' ',str(x or '').replace('\u00ad','').strip())
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cell(x):
    if isinstance(x,(dict,list,bool,int,float)):x=json.dumps(x,ensure_ascii=False,separators=(',',':'))
    return re.sub(r'\s{2,}',' ',str(x or '').replace('\t',' ').replace('\r',' ').replace('\n',' ')).strip()

def lemma_from_headword(h):
    toks=re.findall(r'[A-Za-zÄÖÜäöüß]+',norm(h));bad={'jdn','jdm','etw','akk','dat','gen','sich'}
    vals=[x for x in toks if x.casefold() not in bad]
    return vals[-1] if vals else ''

def toks(s):return {x.casefold() for x in re.findall(r'[A-Za-zÄÖÜäöüß]{3,}',norm(s)) if x.casefold() not in STOP}

def fetch_wikitext(session,lemma):
    p={'action':'parse','page':lemma,'prop':'wikitext','format':'json','formatversion':'2','redirects':'1'}
    r=session.get(API,params=p,headers=HEADERS,timeout=25);r.raise_for_status();d=r.json()
    if 'error' in d:raise RuntimeError(d['error'].get('code','mediawiki_error'))
    return d['parse']['wikitext'],'https://de.wiktionary.org/wiki/'+quote(lemma,safe='')

def verb_blocks(wt):
    ms=list(re.finditer(r'(?m)^===\s*(.*?)\s*===\s*$',wt));out=[]
    for i,m in enumerate(ms):
        head=m.group(1);end=ms[i+1].start() if i+1<len(ms) else len(wt);block=wt[m.end():end]
        if re.search(r'\{\{Wortart\|Verb\|Deutsch',head,re.I):out.append((head,block))
    return out

def score_block(unit,head,block):
    score=len(toks(unit.get('definition_de','')) & toks(block))*4;sep=str((unit.get('core') or {}).get('separability','')).casefold();hl=head.casefold()
    if sep=='separable':score+=20 if ('trennbar' in hl and 'untrennbar' not in hl) else -8
    elif sep=='inseparable':score+=20 if 'untrennbar' in hl else (-8 if 'trennbar' in hl else 2)
    elif sep=='non_prefixed':score+=5 if 'trennbar' not in hl else 0
    core=unit.get('core') or {}
    for f in [core.get('present_3sg'),core.get('preterite_3sg')]:
        if f and norm(f).casefold() in block.casefold():score+=4
    perf=norm(core.get('perfect',''))
    if perf:
        for x in perf.split():
            if len(x)>3 and x.casefold() in block.casefold():score+=2
    return score

def section(block,names):
    pat='|'.join(re.escape(x) for x in names);m=re.search(r'(?mi)^\{\{(?:'+pat+r')\}\}\s*$',block)
    if not m:return ''
    tail=block[m.end():];nxt=re.search(r'(?m)^\{\{[A-ZÄÖÜ][^\n{}]*\}\}\s*$',tail)
    return tail[:nxt.start()] if nxt else tail

def plain_wiki(s):
    s=re.sub(r'<ref[^>]*>.*?</ref>',' ',s,flags=re.I|re.S);s=re.sub(r'<ref[^>]*/>',' ',s,flags=re.I)
    s=re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]',r'\2',s);s=re.sub(r'\[\[([^\]]+)\]\]',r'\1',s)
    s=re.sub(r'\{\{L\|([^|}]+)(?:\|[^}]*)?\}\}',r'\1',s);s=re.sub(r'\{\{K\|([^}]*)\}\}',lambda m:m.group(1).replace('|',', '),s)
    s=re.sub(r'\{\{[^{}]*\}\}',' ',s);s=re.sub(r"'{2,}",'',s)
    return norm(s).strip(' ,;:')

def numbered_lines(sec):
    out=[]
    for line in sec.splitlines():
        if not re.match(r'^\s*[:*#;]',line):continue
        line=re.sub(r'^\s*[:*#;]+\s*','',line);line=re.sub(r'^\[[0-9, –-]+\]\s*','',line);x=plain_wiki(line)
        if x:out.append(x)
    return out

def lexical_terms(sec,lemma):
    out=[];seen=set()
    for line in numbered_lines(sec):
        for x in re.split(r'\s*[,;]\s*',line):
            x=norm(x).strip(' ,;:');x=re.sub(r'^\[[0-9, –-]+\]\s*','',x)
            if not x or len(x)>70 or x.casefold()==lemma.casefold():continue
            if re.search(r'\b(Audio|Info|Wortart|Flexion|Übersetzung)\b',x,re.I):continue
            k=x.casefold()
            if k not in seen:seen.add(k);out.append(x)
    return out[:4]

def collocations(sec,lemma):
    out=[];seen=set()
    for line in numbered_lines(sec):
        for x in [norm(y).strip(' ,;:') for y in re.split(r'\s*;\s*',line)]:
            if not x or len(x)>140:continue
            words=re.findall(r'[A-Za-zÄÖÜäöüß]+',x)
            if len(words)<2:continue
            low=x.casefold();stem=lemma.casefold()[:-2] if len(lemma)>5 else lemma.casefold()
            if lemma.casefold() not in low and stem not in low:continue
            if re.search(r'\b(Wortbildung|Ableitung|Konjugation)\b',x,re.I):continue
            if low not in seen:seen.add(low);out.append(x)
    return out[:6]

def fetch_live(session,unit):
    lemma=lemma_from_headword(unit.get('headword',''))
    if not lemma:return {'error':'NO_LEMMA'}
    wt,url=fetch_wikitext(session,lemma);blocks=verb_blocks(wt)
    if not blocks:return {'url':url,'lemma':lemma,'error':'NO_VERB_BLOCK'}
    score,head,block=sorted([(score_block(unit,h,b),h,b) for h,b in blocks],reverse=True,key=lambda z:z[0])[0]
    return {'url':url,'lemma':lemma,'heading':plain_wiki(head),'score':score,'collocations':collocations(section(block,['Charakteristische Wortkombinationen']),lemma),'synonyms':lexical_terms(section(block,['Synonyme','Sinnverwandte Wörter']),lemma),'antonyms':lexical_terms(section(block,['Gegenwörter','Antonyme']),lemma)}

def add_src(u,wd,claims):
    if not claims:return
    ss=u.setdefault('provenance',{}).setdefault('sources',[]);ss=[s for s in ss if not str(s.get('source_id','')).startswith('de_wiktionary_')]
    ss.append({'source_id':'de_wiktionary_pos_scoped_wikitext','source_kind':'lexicon','what_was_verified':sorted(set(claims)),'verification_status':'verified','locator':wd['url'],'accessed_at':'2026-09-01','evidence_note':"Current-only extraction from the selected German Wiktionary Verb POS/sense block. Collocations are copied only from that block's explicit 'Charakteristische Wortkombinationen' section; no example-derived or legacy enrichment is used."});u['provenance']['sources']=ss

def enrich(ds,delay=.04):
    out=deepcopy(ds);s=requests.Session();rep={'pipeline':'v354-current-only-pos-scoped-wikitext-v2','legacy_inputs_used':False,'units':len(out.get('learning_units',[])),'verbs':0,'pages_ok':0,'pages_failed':0,'collocations':0,'verbs_with_collocations':0,'verbs_with_3plus_collocations':0,'synonym_units':0,'antonym_units':0,'failures':[]}
    for u in out.get('learning_units',[]):
        u.pop('connections',None)
        if u.get('type')!='verb':continue
        rep['verbs']+=1
        try:wd=fetch_live(s,u)
        except Exception as e:rep['pages_failed']+=1;rep['failures'].append({'id':u.get('id'),'headword':u.get('headword'),'reason':type(e).__name__});continue
        if wd.get('error'):rep['pages_failed']+=1;rep['failures'].append({'id':u.get('id'),'headword':u.get('headword'),'reason':wd['error']});continue
        rep['pages_ok']+=1;claims=[]
        if wd['collocations']:
            u['connections']=[{'text':x,'kind':'collocation'} for x in wd['collocations']];claims.append('collocation');rep['collocations']+=len(wd['collocations']);rep['verbs_with_collocations']+=1
            if len(wd['collocations'])>=3:rep['verbs_with_3plus_collocations']+=1
        d=u.setdefault('details',{})
        if wd['synonyms']:d['synonyms']=wd['synonyms'][:2];claims.append('synonymy');rep['synonym_units']+=1
        if wd['antonyms']:d['antonyms']=wd['antonyms'][:2];claims.append('antonymy');rep['antonym_units']+=1
        else:d.pop('antonyms',None)
        add_src(u,wd,claims);time.sleep(delay)
    return out,rep

def row_for(u,ds):
    d=u.get('details') if isinstance(u.get('details'),dict) else {};core=u.get('core') if isinstance(u.get('core'),dict) else {}
    cf={'entry_type':u.get('type'),'canonical_entry_type':u.get('type'),'learning_unit_id':u.get('id'),'semantic_identity':u.get('id'),'german_learning_contract':'gfp-german-learning-content@1.0.0','semantic_contract':'gfp-german-language-content@3.1.3','source_profile_id':ds.get('profile_id'),'german_definition':u.get('definition_de',''),'english':u.get('english_gloss',''),'presentation_examples':u.get('examples',[]),'canonical_unit':u}
    if u.get('type')=='verb':cf.update({'present':core.get('present_3sg',''),'preterite':core.get('preterite_3sg',''),'perfect':core.get('perfect',''),'auxiliary':core.get('auxiliary',''),'reflexive':core.get('reflexive',False),'is_reflexive':core.get('reflexive',False),'is_separable':core.get('separability')=='separable','rection':'; '.join(d.get('rection',[])) if isinstance(d.get('rection'),list) else d.get('rection','')})
    return {'id':u.get('id',''),'card_type':'de-vocabulary','domain':'German','category':u.get('type',''),'source':'Menschen A1','level':'A1','lesson':'Menschen A1','deck':'Verben' if u.get('type')=='verb' else 'Redemittel','front':u.get('headword',''),'back':u.get('persian_meaning',''),'front_label':'Deutsch','back_label':'فارسی','front_lang':'de-DE','back_lang':'fa-IR','typing_target':'front-core','examples':u.get('examples',[]),'related':d.get('synonyms',[]) if isinstance(d.get('synonyms'),list) else [],'opposites':d.get('antonyms',[]) if isinstance(d.get('antonyms'),list) else [],'details':[],'custom_fields':cf,'tags':'; '.join((u.get('metadata') or {}).get('tags',[]) or []),'notes':'','order':(u.get('metadata') or {}).get('unit_order','')}

def write_tsv(ds,path):
    rows=[row_for(u,ds) for u in ds.get('learning_units',[])]
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        f.write('\t'.join(TSV_HEADERS)+'\n')
        for r in rows:f.write('\t'.join(cell(r.get(k,'')) for k in TSV_HEADERS)+'\n')
    lines=Path(path).read_text(encoding='utf-8').splitlines();assert len(lines)==len(rows)+1
    for i,line in enumerate(lines,1):assert len(line.split('\t'))==23,(i,len(line.split('\t')))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--baseline',required=True);ap.add_argument('--outdir',required=True);ap.add_argument('--delay',type=float,default=.04);a=ap.parse_args()
    base=load(a.baseline);out,rep=enrich(base,a.delay);od=Path(a.outdir);od.mkdir(parents=True,exist_ok=True);canon=od/'MENSCHEN-A1-CANONICAL-v354-CURRENT-VALIDATED.json';tsv=od/'MENSCHEN-A1-UNIVERSAL-v2-v354-CURRENT.tsv';dump(canon,out);write_tsv(out,tsv)
    first=out['learning_units'][0];assert first['headword']=='überlegen';assert 'unterlegen' not in [str(x).casefold() for x in (first.get('details') or {}).get('antonyms',[])]
    bad={'überlegene','was machen überlegen','jemanden lange vor der antwort überlegen'};assert not bad.intersection({str(c.get('text','')).casefold() for c in first.get('connections',[])})
    dump(od/'BUILD-REPORT.json',{**rep,'canonical_sha256':sha(canon),'tsv_sha256':sha(tsv),'tsv_rows':len(out['learning_units']),'transport':'v354 raw-tab Universal v2; JSON cells are not CSV-quoted','legacy_inputs_used':False});print(json.dumps(rep,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
