#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, time
from copy import deepcopy
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup, Tag

HEADERS={"User-Agent":"Mozilla/5.0 (compatible; German-Content-Production-Kit/3.1.11; +https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit)"}
TSV_HEADERS=['id','card_type','domain','category','source','level','lesson','deck','front','back','front_label','back_label','front_lang','back_lang','typing_target','examples','related','opposites','details','custom_fields','tags','notes','order']
STOPWORDS={'der','die','das','den','dem','des','ein','eine','einen','einem','einer','eines','und','oder','mit','von','zu','in','auf','für','an','über','unter','vor','nach','bei','aus','sich','etwas','jemand','jemanden','jemandem','einer','einem','einen','sein','haben','werden','können','müssen','sollen','wollen','dürfen','sehr','etwas'}
BOUNDARY_LABELS={'Bedeutungen','Herkunft','Synonyme','Sinnverwandte Wörter','Gegenwörter','Antonyme','Oberbegriffe','Unterbegriffe','Beispiele','Redewendungen','Sprichwörter','Charakteristische Wortkombinationen','Wortbildungen','Übersetzungen','Referenzen und weiterführende Informationen','Quellen'}

def norm(x): return re.sub(r'\s+',' ',str(x or '').replace('\u00ad','').strip())
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cell(x):
    if isinstance(x,(dict,list,bool,int,float)): x=json.dumps(x,ensure_ascii=False,separators=(',',':'))
    x=str(x or '').replace('\t',' ').replace('\r',' ').replace('\n',' ')
    return re.sub(r'\s{2,}',' ',x).strip()

def lemma_from_headword(headword):
    h=norm(headword)
    h=re.sub(r'^sich\s+','',h,flags=re.I)
    h=re.sub(r'\s+(?:an|auf|aus|bei|durch|für|gegen|in|mit|nach|über|um|unter|von|vor|zu|zwischen)\s+(?:etw\.|jdn\.|jdm\.|etwas|jemanden|jemandem).*$','',h,flags=re.I)
    h=re.sub(r'\s*\+\s*(?:Akk\.?|Dat\.?|Gen\.?).*$','',h,flags=re.I)
    return h.split()[0] if h else ''

def heading_text(h): return norm(h.get_text(' ',strip=True))
def block_after_heading(h):
    lvl=int(h.name[1]); out=[]
    for sib in h.next_siblings:
        if isinstance(sib,Tag) and re.fullmatch(r'h[1-6]',sib.name or '') and int(sib.name[1])<=lvl: break
        out.append(sib)
    return out

def tokens(s):
    return {w.casefold() for w in re.findall(r'[A-Za-zÄÖÜäöüß]{3,}',norm(s)) if w.casefold() not in STOPWORDS}

def candidate_verb_blocks(soup,unit):
    c=[]
    for h in soup.find_all(re.compile(r'^h[1-6]$')):
        t=heading_text(h)
        if not re.search(r'\bVerb\b',t,re.I): continue
        block=block_after_heading(h); text=norm(' '.join(x.get_text(' ',strip=True) for x in block if isinstance(x,Tag)))
        score=len(tokens(unit.get('definition_de','')) & tokens(text))*4
        sep=str((unit.get('core') or {}).get('separability','')).casefold()
        if sep=='separable': score += 12 if re.search(r'trennbar',t,re.I) and not re.search(r'untrennbar',t,re.I) else -4
        elif sep=='inseparable': score += 12 if re.search(r'untrennbar',t,re.I) else (2 if not re.search(r'trennbar',t,re.I) else -4)
        elif sep=='non_prefixed': score += 5 if not re.search(r'trennbar|untrennbar',t,re.I) else 0
        # Form agreement is a strong sense/POS signal.
        core=unit.get('core') or {}
        for form in [core.get('present_3sg'),core.get('preterite_3sg'),core.get('perfect')]:
            if form and norm(form).casefold() in text.casefold(): score+=3
        c.append((score,h,block,text,t))
    return sorted(c,key=lambda x:x[0],reverse=True)

def flatten_block(block):
    lines=[]
    for x in block:
        if not isinstance(x,Tag): continue
        txt=x.get_text('\n',strip=True)
        for line in txt.splitlines():
            line=norm(line)
            if line: lines.append(line)
    return lines

def clean_number_prefix(s):
    s=norm(s)
    s=re.sub(r'^\[[^\]]+\]\s*','',s)
    s=re.sub(r'^\d+[.:)]\s*','',s)
    s=re.sub(r'\s*\(Audio\s*\(Info\)\).*?$','',s,flags=re.I)
    return norm(s).strip(' ,;:')

def section_lines(lines,label_names):
    starts=[]
    for i,line in enumerate(lines):
        bare=line.rstrip(':').strip()
        if any(bare.casefold()==lab.casefold() for lab in label_names): starts.append(i)
    if not starts:return []
    i=starts[0]+1; out=[]
    for line in lines[i:]:
        bare=line.rstrip(':').strip()
        if bare in BOUNDARY_LABELS: break
        if bare.casefold()=='bearbeiten': continue
        out.append(line)
    return out

def extract_anchor_terms(block,label_names):
    # Locate the label node in DOM order and collect anchors until the next lexical label.
    nodes=[]; active=False
    for root in block:
        if not isinstance(root,Tag): continue
        seq=[root,*root.find_all(True)]
        for node in seq:
            txt=heading_text(node)
            bare=txt.rstrip(':').strip()
            if not active and any(bare.casefold()==lab.casefold() for lab in label_names):
                active=True; continue
            if active and bare in BOUNDARY_LABELS and not any(bare.casefold()==lab.casefold() for lab in label_names):
                return nodes
            if active and node.name=='a':
                t=clean_number_prefix(node.get_text(' ',strip=True))
                if t and len(t)<=70 and not re.search(r'^(Bearbeiten|Info|Audio|Deutsch|Verb|Adjektiv)$',t,re.I): nodes.append(t)
    return nodes

def split_terms(lines):
    out=[]; seen=set()
    for line in lines:
        s=clean_number_prefix(line)
        s=re.sub(r'^\[[^\]]+\]\s*','',s)
        for p in re.split(r'\s*[,;]\s*',s):
            p=clean_number_prefix(p)
            if not p or len(p)>70: continue
            p=re.sub(r'^\[[0-9, ]+\]\s*','',p)
            if ':' in p and len(p.split(':',1)[0])<30: p=p.split(':',1)[1].strip()
            k=p.casefold()
            if p and k not in seen: seen.add(k); out.append(p)
    return out

def clean_combo_line(line,lemma):
    s=clean_number_prefix(line)
    if ':' in s and len(s.split(':',1)[0])<45: s=s.split(':',1)[1].strip()
    s=re.sub(r'\s*\(Audio.*$','',s,flags=re.I)
    # Split only when each component independently contains the lemma.
    parts=[clean_number_prefix(x) for x in re.split(r'\s*,\s*',s)]
    if len(parts)>1 and all(lemma.casefold() in p.casefold() for p in parts): return parts
    return [s]

def extract_collocations(lines,lemma):
    out=[];seen=set()
    for line in lines:
        for c in clean_combo_line(line,lemma):
            c=norm(c).strip(' ,;:')
            if not c or len(c)>120:continue
            if lemma.casefold() not in c.casefold():continue
            # Reject bare inflection/derivation masquerading as a phrase.
            words=re.findall(r'[A-Za-zÄÖÜäöüß]+',c)
            if len(words)<2:continue
            k=c.casefold()
            if k not in seen:seen.add(k);out.append(c)
    return out[:6]

def fetch_live(session,unit):
    lemma=lemma_from_headword(unit.get('headword',''))
    if not lemma:return None
    url='https://de.wiktionary.org/wiki/'+quote(lemma,safe='')
    r=session.get(url,headers=HEADERS,timeout=25);r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser')
    blocks=candidate_verb_blocks(soup,unit)
    if not blocks:return {'url':url,'lemma':lemma,'error':'NO_VERB_BLOCK'}
    score,h,block,text,title=blocks[0]; lines=flatten_block(block)
    combos=extract_collocations(section_lines(lines,['Charakteristische Wortkombinationen']),lemma)
    # Syn/ant anchors are safer than flattened text; restrict to selected verb block.
    syn=extract_anchor_terms(block,['Synonyme']) or extract_anchor_terms(block,['Sinnverwandte Wörter'])
    ant=extract_anchor_terms(block,['Gegenwörter']) or extract_anchor_terms(block,['Antonyme'])
    def clean_lex(vals):
        out=[];seen=set()
        for x in vals:
            x=clean_number_prefix(x)
            if not x or len(x)>60 or x.casefold()==lemma.casefold():continue
            if re.search(r'^(Flexion|Wortart|Hilfe|Referenzen|Übersetzungen)$',x,re.I):continue
            k=x.casefold()
            if k not in seen:seen.add(k);out.append(x)
        return out[:4]
    return {'url':url,'lemma':lemma,'heading':title,'score':score,'collocations':combos,'synonyms':clean_lex(syn),'antonyms':clean_lex(ant)}

def add_live_source(u,wd,claims):
    if not claims:return
    sources=u.setdefault('provenance',{}).setdefault('sources',[])
    sources=[s for s in sources if s.get('source_id')!='de_wiktionary_pos_scoped_live']
    sources.append({'source_id':'de_wiktionary_pos_scoped_live','source_kind':'lexicon','what_was_verified':sorted(set(claims)),'verification_status':'verified','locator':wd['url'],'accessed_at':'2026-09-01','evidence_note':f"Current-only, POS-scoped German Wiktionary extraction from selected subsection '{wd.get('heading','Verb')}'. The scraper does not cross into adjective or alternate verb-sense blocks."})
    u['provenance']['sources']=sources

def enrich(ds,delay=.05):
    out=deepcopy(ds);session=requests.Session();rep={'pipeline':'v354-current-only-pos-scoped-wiktionary','legacy_inputs_used':False,'units':len(out.get('learning_units',[])),'verbs':0,'pages_ok':0,'pages_failed':0,'collocations':0,'verbs_with_collocations':0,'synonym_units':0,'antonym_units':0,'failures':[]}
    for u in out.get('learning_units',[]):
        # Remove every previous generated/current-only enrichment trace; baseline itself is the target content.
        u.pop('connections',None)
        if u.get('type')!='verb':continue
        rep['verbs']+=1
        try:wd=fetch_live(session,u)
        except Exception as e:
            rep['pages_failed']+=1;rep['failures'].append({'id':u.get('id'),'headword':u.get('headword'),'reason':type(e).__name__});continue
        if not wd or wd.get('error'):
            rep['pages_failed']+=1;rep['failures'].append({'id':u.get('id'),'headword':u.get('headword'),'reason':(wd or {}).get('error','NO_DATA')});continue
        rep['pages_ok']+=1; claims=[]
        if wd['collocations']:
            u['connections']=[{'text':x,'kind':'collocation'} for x in wd['collocations']];claims.append('collocation');rep['collocations']+=len(wd['collocations']);rep['verbs_with_collocations']+=1
        d=u.setdefault('details',{})
        if wd['synonyms']:
            d['synonyms']=wd['synonyms'][:2];claims.append('synonymy');rep['synonym_units']+=1
        elif 'synonyms' in d:
            # Keep baseline validated synonyms, but do not label them as live-verified.
            pass
        if wd['antonyms']:
            d['antonyms']=wd['antonyms'][:2];claims.append('antonymy');rep['antonym_units']+=1
        else:
            # Avoid carrying unverified/ambiguous antonyms into the corrected runtime artifact.
            d.pop('antonyms',None)
        add_live_source(u,wd,claims);time.sleep(delay)
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
    ap=argparse.ArgumentParser();ap.add_argument('--baseline',required=True);ap.add_argument('--outdir',required=True);ap.add_argument('--delay',type=float,default=.05);a=ap.parse_args()
    base=load(a.baseline);out,rep=enrich(base,a.delay);od=Path(a.outdir);od.mkdir(parents=True,exist_ok=True)
    canon=od/'MENSCHEN-A1-CANONICAL-v354-CURRENT-VALIDATED.json';tsv=od/'MENSCHEN-A1-UNIVERSAL-v2-v354-CURRENT.tsv'
    dump(canon,out);write_tsv(out,tsv)
    # Focused semantic regression for the card that exposed the previous contamination.
    first=out['learning_units'][0]; assert first['headword']=='überlegen'
    assert 'unterlegen' not in [str(x).casefold() for x in (first.get('details') or {}).get('antonyms',[])]
    bad={'überlegene','was machen überlegen','jemanden lange vor der antwort überlegen'}
    assert not bad.intersection({str(c.get('text','')).casefold() for c in first.get('connections',[])})
    dump(od/'BUILD-REPORT.json',{**rep,'canonical_sha256':sha(canon),'tsv_sha256':sha(tsv),'tsv_rows':len(out['learning_units']),'transport':'v354 raw-tab Universal v2; JSON cells are not CSV-quoted','legacy_inputs_used':False})
    print(json.dumps(rep,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
