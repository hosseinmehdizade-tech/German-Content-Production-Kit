#!/usr/bin/env python3
"""Bound source-faithful R74 12-visible-synonym qualified-review supplement.
Creates reviewer packet only. Never authorizes card edits or expert signoff.
"""
import argparse,csv,hashlib,html,io,json,zipfile
from pathlib import Path
SRC_SHA='630bfcd30be7439f397c634ed7c5f197db54833455a88569b27b7ef79c73a21b'
R70_SHA='84f9cd4b39c64d2f40f06594589184f3551848384766d6068384bb7c52d37180'
CAN_SHA='77e29cbe28803b8534ad4e6cc0ece16df639a8aa01c98c116fd3ce114ebe59a7'
REVIEW_FINGERPRINT='794ade6af612bce219d47a0b90f0ebff90f40ef9cf09f65b774c4f7e277886df'
BASE='93-Stage4-Rechnung-Translation-And-Synonym-Triage-R66/'
TARGETS=[('0015','den Wohnort wechseln','NO_TYPED_RELATION'),('0028','verpacken','NO_TYPED_RELATION'),('0050','aussuchen','NO_TYPED_RELATION'),('0070','begeistern','RELATED_ONLY'),('0073','abfahren','NO_TYPED_RELATION'),('0122','produzieren','RELATED_ONLY'),('0141','ermitteln','RELATED_ONLY'),('0148','verblüffen','NO_TYPED_RELATION'),('0225','beanstanden','NO_TYPED_RELATION'),('0244','klauen','NO_TYPED_RELATION'),('0245','davonlaufen','NO_TYPED_RELATION'),('0290','zu spät kommen','NO_TYPED_RELATION')]
KEYS=['id','card_id','headword','headword_fa','definition_de','display_synonym','relation_status','related_relation_id','related_relation_scope','provenance_stage','editorial_review_status','source_locator','source_original_row','original_source_image_sha256','card_batch','fingerprint']
def H(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def ensure(b,msg):
 if not b:raise ValueError(msg)
def fetch(src,r70):
 src=Path(src);r70=Path(r70)
 ensure(H(src.read_bytes())==SRC_SHA,'R66_SHA256_MISMATCH');ensure(H(r70.read_bytes())==R70_SHA,'R70_SHA256_MISMATCH')
 with zipfile.ZipFile(src) as z:
  ensure(z.testzip() is None,'R66_BAD_CRC')
  can=z.read(BASE+'CANDIDATE-IMPORT-NOT-FINAL.tsv');ensure(H(can)==CAN_SHA,'ACTIVE_CANDIDATE_SHA_MISMATCH')
  candidate=list(csv.DictReader(io.StringIO(can.decode('utf-8-sig')),delimiter='\t'))
  rdata=json.loads(z.read(BASE+'REVIEW-DATA.json'))
  ensure(rdata['data_fingerprint']==REVIEW_FINGERPRINT,'REVIEW_DATA_FINGERPRINT_MISMATCH')
  ensure(len(candidate)==292 and len(rdata['synonyms'])==243 and len(rdata['examples'])==1168,'BAD_ORIGINAL_UNIVERSE')
 with zipfile.ZipFile(r70) as z:
  ensure(z.testzip() is None,'R70_BAD_CRC')
  references=list(csv.DictReader(io.StringIO(z.read('R69-SOURCE-LOCATORS-BY-CARD-292.tsv').decode()),delimiter='\t'))
 ref={x['card_id']:x for x in references};ensure(len(ref)==292,'R70_SOURCE_CARDS_NOT_292')
 # Independently reproduce the R73 full-population count, rather than just trusting the twelve target IDs.
 visible_total=0; typed_total=0; unmatched=[];hidden=[]
 for rr in candidate:
  cc=json.loads(rr['custom_fields']); sections=json.loads(rr['details']); visible=[s for s in sections if s.get('title')=='Synonyme']
  ensure(len(visible)<=1,'DUPLICATE_VISIBLE_SYNONYM_SECTION')
  terms=visible[0].get('items',[]) if visible else []
  ensure(isinstance(terms,list),'NONLIST_VISIBLE_SYNONYM_ITEMS')
  typed=[rel for rel in cc['canonical_relations'] if rel.get('relation_type')=='SYNONYM']
  visible_total+=len(terms);typed_total+=len(typed)
  if len(terms)>len(typed):unmatched.append(rr['id'])
  if len(cc['canonical_unit']['details'].get('synonyms',[]))>len(terms):hidden.append(rr['id'])
 ensure(visible_total==255 and typed_total==243,'UNEXPECTED_GLOBAL_SYNONYM_COUNTS')
 ensure(unmatched==['ma2-lu-'+n for n,_,_ in TARGETS],'UNEXPECTED_EXTRA_UNREVIEWED_VISIBLE_SYNONYMS')
 ensure(hidden==['ma2-lu-0288'],'UNEXPECTED_HIDDEN_DETAIL_SYNONYM')
 allcard={x['id']:x for x in candidate}; out=[]
 for i,(n,term,expected) in enumerate(TARGETS,1):
  cid='ma2-lu-'+n;r=allcard[cid];cf=json.loads(r['custom_fields']);syn=cf['canonical_unit']['details']['synonyms'];rels=cf['canonical_relations'];
  ensure(term in syn,'CANONICAL_DETAIL_SYNONYM_MISSING '+cid)
  sections=json.loads(r['details']); visible=next((section['items'] for section in sections if section.get('title')=='Synonyme'),[])
  ensure(len(visible)==1 and term in str(visible[0]),'VISIBLE_SECTION_SYNONYM_MISSING '+cid)
  ensure(sum(x.get('relation_type')=='SYNONYM' for x in rels)==0,'UNEXPECTED_TYPED_SYNONYM '+cid)
  matching=[x for x in rels if (x.get('value',{}).get('term','') if isinstance(x.get('value'),dict) else x.get('value'))==term]
  kind='RELATED_ONLY' if len(matching)==1 and matching[0].get('relation_type')=='RELATED' else 'NO_TYPED_RELATION' if not matching else 'UNKNOWN'
  ensure(kind==expected,'RELATION_STATUS_MISMATCH '+cid)
  overlay=cf.get('lexical_editorial_overlay',{})
  ensure(term in overlay.get('synonyms_added',[]),'NOT_IN_EDITORIAL_OVERLAY '+cid)
  lookup=ref[cid];
  raw=matching[0]['value'] if matching else {}
  info={'id':f'R74-DISPLAY-SYN-{n}-001','card_id':cid,'headword':r['front'],'headword_fa':r['back'],'definition_de':cf['vnext_definition_de'],'display_synonym':term,'relation_status':kind,'related_relation_id':matching[0]['relation_id'] if matching else '', 'related_relation_scope':raw.get('scope','') if isinstance(raw,dict) else '', 'provenance_stage':overlay.get('origin',''),'editorial_review_status':overlay.get('independent_stage4',''), 'source_locator':lookup['all_image_row_locators'],'source_original_row':lookup['all_raw_source_rows'], 'original_source_image_sha256':lookup['primary_image_sha256'],'card_batch':lookup['batch_id']}
  info['fingerprint']=H(canonical(info));out.append(info)
 ensure(len(out)==12 and len({x['fingerprint'] for x in out})==12 and len({x['id'] for x in out})==12,'R74_UNIQUE_ITEMS_ERROR')
 ensure(sum(x['relation_status']=='RELATED_ONLY' for x in out)==3,'R74_RELATED_SPLIT_CHANGED')
 return out

def reviewer_html(data):
 # Static data is escaped for HTML/script context; no source images are embedded.
 safe=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
 return '''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R74 — 12 Synonym-Anzeigen extern prüfen</title><style>
body{font:16px system-ui,Arial,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem;line-height:1.45;color:#192b35;background:#f5f7fa}h1{font-size:1.6rem}.box{background:white;padding:1.1rem;border:1px solid #d2dae0;border-radius:12px;margin-bottom:1rem}.g{display:grid;grid-template-columns:1fr 1fr;gap:.6rem}label{font-weight:600;display:block}input,select,textarea{box-sizing:border-box;width:100%;font:inherit;border:1px solid #adb9c0;padding:.55rem;border-radius:6px}textarea{min-height:4.8rem}button{padding:.75rem 1.4rem;border:0;background:#17496e;color:white;border-radius:8px;cursor:pointer}small,.hint{color:#586971}.id{font-family:monospace;font-size:.85rem}header p{max-width:900px}strong{color:#183b58}article{border-bottom:1px solid #d8e0e5;padding:1.3rem 0}article:last-child{border:0}.warning{color:#914500}.wide{grid-column:1/-1}details{font-size:.9rem}@media(max-width:650px){.g{grid-template-columns:1fr}}</style></head><body>
<header><h1>R74 — Ergänzende Expertenprüfung: 12 sichtbare Synonyme</h1><p class="warning">Keine automatische Freigabe. Fachliche Unabhängigkeit und Qualifikation müssen außerhalb dieses Formulars geprüft werden. R66 und die bisherigen 1.411 Review-Items bleiben unverändert.</p><p>Originalkurszeilen belegen nur die Quelle des Lernworts, nicht automatisch das später kuratierte Synonym. Keine Kursbilder in dieser Datei enthalten.</p></header>
<section class="box g"><div><label>Reviewer-ID (pseudonym möglich)<input id="reviewer_id" placeholder="z.B. EXT-DE-01"></label></div><div><label>Qualifikation (Angabe, noch nicht überprüft)<input id="qualification" placeholder="z.B. Deutsch-Linguistik, Ausbildung ..."></label></div><div class="wide"><label><input style="width:auto" type="checkbox" id="independent"> Ich habe fachlich unabhängig selbst geprüft und bin nicht das produzierende KI-Modell.</label></div></section><main id="main" class="box"></main><div class="box"><button id="export" type="button">JSON exportieren (lokal)</button><p class="hint" id="status">Es werden keine Daten an einen Server gesendet. Eine JSON-Datei ist noch kein Experten-PASS.</p></div>
<script>
const R=__DATA__;const choices=[['NOT_REVIEWED','Noch nicht geprüft'],['SCOPED_SYNONYM','Nur als bedeutungsbegrenztes Synonym zulassen'],['KEEP_RELATED_REMOVE_SYNONYM_DISPLAY','RELATED beibehalten, aus Synonyme-Anzeige entfernen'],['REMOVE_FROM_SYNONYM_DISPLAY','Nicht als Synonym anzeigen'],['NEEDS_CORRECTION','Korrektur erforderlich'],['UNSURE','Unklar; weitere Prüfung']];
function el(tag,cls,txt){const x=document.createElement(tag);if(cls)x.className=cls;if(txt!==undefined)x.textContent=txt;return x}
function field(parent,title,value){const box=el('div');box.append(el('strong',null,title+': '),document.createTextNode(String(value||'–')));parent.append(box)}
const main=document.getElementById('main');
R.items.forEach((x,i)=>{const art=el('article');art.dataset.id=x.id;const hd=el('h2',null,(i+1)+'. '+x.headword+' → '+x.display_synonym);art.append(hd);field(art,'Karte',x.card_id+' / '+x.headword_fa);field(art,'Definition DE',x.definition_de);field(art,'Technischer Status',x.relation_status+(x.related_relation_id?' / '+x.related_relation_id:''));if(x.related_relation_scope)field(art,'RELATED-Scope',x.related_relation_scope);const d=el('details');d.append(el('summary',null,'Quelle & Identität (zur manuellen Verifikation)'));field(d,'Originalfundstelle',x.source_locator);field(d,'Originalkurszeile',x.source_original_row);field(d,'Originalbild SHA256',x.original_source_image_sha256);field(d,'Item-SHA256',x.fingerprint);art.append(d);
const group=el('div','g');const l=el('label');l.textContent='Fachliche Einstufung';const sel=el('select');sel.dataset.kind='decision';for(const [code,txt] of choices){const op=el('option');op.value=code;op.textContent=txt;sel.append(op)}l.append(sel);group.append(l);
const l2=el('label');l2.textContent='Zulässiger deutscher Bedeutungs-/Satzbau-Scope';const scope=el('textarea');scope.dataset.kind='scope';scope.placeholder='Nur wenn ... / Nicht bei ...';l2.append(scope);group.append(l2);
const l3=el('label','wide');l3.textContent='Begründung und ggf. Gegenbeispiel';const note=el('textarea');note.dataset.kind='rationale';note.placeholder='Begründung mit Kontext, Register, Valenz ...';l3.append(note);group.append(l3);art.append(group);main.append(art)});
document.getElementById('export').addEventListener('click',()=>{const reviewer_id=document.getElementById('reviewer_id').value.trim(), qualification=document.getElementById('qualification').value.trim(), independent=document.getElementById('independent').checked;
if(!reviewer_id||!qualification||!independent){document.getElementById('status').textContent='Reviewer-ID, Qualifikation und Unabhängigkeits-Erklärung sind erforderlich.';return}
const decisions=[...main.querySelectorAll('article')].map(a=>({item_id:a.dataset.id, item_fingerprint:R.items.find(x=>x.id===a.dataset.id).fingerprint,decision:a.querySelector('[data-kind=decision]').value,proposed_scope:a.querySelector('[data-kind=scope]').value.trim(),rationale:a.querySelector('[data-kind=rationale]').value.trim()}));
for(const d of decisions){if(d.decision!=='NOT_REVIEWED'&&d.rationale.length<15){document.getElementById('status').textContent='Mindestens 15 Zeichen fachliche Begründung für '+d.item_id;return}if(d.decision==='SCOPED_SYNONYM'&&d.proposed_scope.length<15){document.getElementById('status').textContent='Bedeutungs-Scope für '+d.item_id+' fehlt';return}}
const result={schema:'ma2-r74-extra-visible-synonym-decisions@1.0.0',source_r66_sha256:R.source_r66_sha256,source_candidate_sha256:R.candidate_sha256,source_review_fingerprint:R.source_review_fingerprint,supplement_fingerprint:R.supplement_fingerprint,reviewer:{reviewer_id,qualification_claim:qualification,independent_attestation:independent,qualification_external_verified:false},decisions};const blob=new Blob([JSON.stringify(result,null,2)+'\\n'],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='R74-visible-synonym-review-'+reviewer_id.replace(/[^A-Za-z0-9_-]/g,'_')+'.json';a.click();URL.revokeObjectURL(url);document.getElementById('status').textContent='JSON erstellt. Externe fachliche Qualifikation noch NICHT verifiziert.'});
</script></body></html>'''.replace('__DATA__',safe).encode('utf-8')

def package(src,r70,out):
 items=fetch(src,r70)
 fingerprint=H(canonical([{k:v for k,v in i.items() if k!='fingerprint'} for i in items]))
 data={'schema':'ma2-r74-visible-synonym-review-supplement@1.0.0','source_r66_sha256':SRC_SHA,'candidate_sha256':CAN_SHA,'source_review_fingerprint':REVIEW_FINGERPRINT,'source_r70_sha256':R70_SHA,'source_1411_review_count':1411,'source_example_count':1168,'source_formal_synonym_count':243,'source_visible_synonym_count':255,'supplement_items':12,'supplement_fingerprint':fingerprint,'role':'SUPPLEMENTAL_REVIEW_NOT_A_NEW_CONTENT_OR_STAGE4_AUTHORITY','items':items,'qualifications_confirmed':False,'independent_real_decisions_received':0,'final_stage4':False,'original_display_was_editorial_enrichment_not_necessarily_course_text':True,'notes':'The three RELATED_ONLY entries were explicitly preserved as RELATED by prior R66 adjudication. No automatic reclassification.'}
 t=io.StringIO(newline='');w=csv.DictWriter(t,fieldnames=KEYS,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(items)
 readme='''# R74 — ergänzende Prüfung der 12 sichtbaren Synonyme / بررسی تکمیلی ۱۲ مترادف نمایشی\n\nR66 ist unverändert: 292 Karten, 1168 Beispiele, 243 strukturelle SYNONYM-Relationen. R70 und R68 bleiben für die ursprünglichen 1411 Entscheidungen gültig. Diese Ergänzung **ersetzt oder vermehrt keine fachliche Freigabe automatisch**.\n\n9 sichtbare Synonyme aus `lexical_editorial_overlay.synonyms_added` sind ohne typisierte Relation; 3 sind bewusst als RELATED erfasst (begeistern, produzieren, ermitteln). Es wäre fachlich falsch, diese ohne Prüfung pauschal zu SYNONYM hochzustufen.\n\n1. Exakte R66- und R70-ZIP bereitstellen.\n2. `python VALIDATE_R74_REVIEW.py selftest --source R66.zip --workspace R70.zip --data R74-REVIEW-DATA.json`\n3. `R74-REVIEWER.html` offline öffnen, 12 Entscheidungen mit Begründung exportieren.\n4. `python VALIDATE_R74_REVIEW.py validate --source R66.zip --workspace R70.zip --data R74-REVIEW-DATA.json --export decisions.json --report result.json`\n5. Qualifikation, Unabhängigkeit und Quellenbezug durch andere zuständige Person nachprüfen. Entscheiden, welche Synonyme als SYNONYM mit Scope, als RELATED (mit anderer Anzeige) oder als nicht belegbar klassifiziert werden. Erst dann neuen R66-Nachfolger und neu gebundenes Reviewer-Universum erstellen.\n\nNOTE: Das Originalbild belegt die Kurszeile, nicht das nachträglich kuratierte Synonym. No source image bytes are included. `result.json` cannot assert Stage4 PASS.\n'''
 files={'R74-REVIEW-DATA.json':json.dumps(data,ensure_ascii=False,indent=2).encode('utf-8')+b'\n','R74-12-VISIBLE-SYNONYMS.tsv':t.getvalue().encode('utf-8'),'R74-REVIEWER.html':reviewer_html(data),'README-FA-DE.md':readme.encode('utf-8'),'VALIDATE_R74_REVIEW.py':Path(__file__).with_name('VALIDATE_R74_REVIEW.py').read_bytes(),'BUILD_R74_SUPPLEMENT.py':Path(__file__).read_bytes()}
 files['SHA256SUMS.json']=(json.dumps({k:H(v) for k,v in sorted(files.items())},indent=2)+'\n').encode('utf-8')
 out=Path(out);out.parent.mkdir(exist_ok=True,parents=True)
 with zipfile.ZipFile(out,'w') as z:
  for k,v in sorted(files.items()):
   inf=zipfile.ZipInfo(k,date_time=(2026,10,23,6,0,0));inf.compress_type=zipfile.ZIP_DEFLATED;inf.external_attr=0o644<<16;z.writestr(inf,v)
 ensure(zipfile.ZipFile(out).testzip() is None,'OUTPUT_CRC_ERROR')
 print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'sha256':H(out.read_bytes()),'members':len(files),'items':len(items),'source_r66_sha256':SRC_SHA,'fingerprint':fingerprint}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--workspace',required=True);p.add_argument('--output',required=True);a=p.parse_args();package(a.source,a.workspace,a.output)
