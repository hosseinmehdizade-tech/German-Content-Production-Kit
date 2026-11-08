#!/usr/bin/env python3
"""Aspekte B1+ G4 QA v3. Detect exact examples, punctuated clauses, and some unpunctuated finite sentences in Kombinationen.
Run: python Tools/qa_combinationen_finite_clause_v3.py owner.zip [report.json]
Exits nonzero on confirmed structural risks. It does NOT replace full German linguistic QA.
"""
import json, zipfile, re, unicodedata, sys
from pathlib import Path
FILE='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
FINITE={"besucht","hält","liefert","liegt","arbeitet","hat","ist","sind","macht","zeigt","sagt","führt","kommt","geht","kann","muss","soll","wird","steht","braucht","zahlt","erklärt","spielt","übernimmt","bringt","bietet","verläuft","wächst","wohnt","leitet","unterstützt","reist","nimmt","fährt","findet","wählt","stellt","spricht","liest","prüft"}
ART={"der","die","das","ein","eine","einer","eines","dieser","diese","dieses","jener","jene","welcher","welche","welches"}
def norm(s):
 return ' '.join(re.sub(r'[^\w\s]',' ',unicodedata.normalize('NFKC',s).casefold()).split())
def finite_candidate(s):
 t=re.findall(r'[\wÄÖÜäöüß-]+',s)
 return bool(t and t[0].casefold() in ART and any(t[i].casefold() in FINITE and any(w[:1].isupper() for w in t[1:i]) for i in range(2,min(len(t),5))))
def audit(cards):
 issues=[];n=0
 for c in cards:
  b=c['back'];ex=(b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
  e=[norm(x['de']) for x in ex]
  for net in b.get('semantic_network_sense_anchored_pending_qa',[]) or []:
   for combo in net.get('Kombinationen_DE_FA',[]) or []:
    n+=1;de=combo['de'];s=norm(de);why=[]
    if s in e:why.append('EXACT_EXAMPLE_COPY')
    if len(s.split())>=4 and any(s in x for x in e):why.append('FULL_PHRASE_SUBSTRING_IN_EXAMPLE')
    if de.strip().endswith(('.', '!', '?')) or len(de.split())>10:why.append('PUNCTUATED_OR_LONG_SENTENCE')
    if finite_candidate(de):why.append('HIGH_CONFIDENCE_FINITE_CLAUSE')
    if why:issues.append({'source_ordinal':c['source_ordinal'],'sense_id':net.get('sense_id'), 'de':de,'flags':why})
 return {'cards_scanned':len(cards),'combinations_scanned':n,'issues':issues,'issue_count':len(issues),'structural_pass':len(issues)==0,'scope_limit':'Conservative finite-verb heuristic; misses some syntactic full sentences; independent language QA is still needed.'}
if __name__=='__main__':
 with zipfile.ZipFile(sys.argv[1]) as z:cards=[json.loads(x) for x in z.read(FILE).splitlines()]
 res=audit(cards)
 if len(sys.argv)>2:Path(sys.argv[2]).write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(res,ensure_ascii=False,indent=2));sys.exit(0 if res['structural_pass'] else 1)
