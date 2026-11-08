#!/usr/bin/env python3
"""Aspekte B1+ QA-only HTML Front/Back projection with examples *inside their specific sense*.
This is not German-Flashcards-Pro renderer or evidence of an actual app import.
All input source arrays are preserved; rendering duplicates nothing, and unmatched example sense ids are explicit.
"""
import html,json,zipfile,collections,re,sys
from pathlib import Path
from bs4 import BeautifulSoup
SOURCE='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
def esc(s):return html.escape(str(s),quote=True)
def pair_li(item,cat):
    return f'<li data-section="{esc(cat)}" data-de="{esc(item["de"])}" data-fa="{esc(item["fa"])}"><span lang="de">{esc(item["de"])}</span><span class="fa" lang="fa" dir="rtl">{esc(item["fa"])}</span></li>'
def render(card):
    f=card['front'];b=card['back'];ex=(b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
    ns=b.get('semantic_network_sense_anchored_pending_qa') or []
    h=[f'<article class="card" data-card-id="{esc(card["preview_card_id"])}" data-ordinal="{card["source_ordinal"]}">',
       f'<div class="front"><h2 lang="de">{esc(f["base_headword_de"])}</h2><div class="forms" lang="de">{esc(f["display_de_provisional"])}</div></div>',
       f'<div class="back"><div class="meaning" lang="fa" dir="rtl">{esc(b["meanings_fa_provisional"])}</div>']
    if not ns:
        h.append('<section class="examples"><h3>Beispiele · مثال‌ها</h3><ul>'+''.join(pair_li(x,'Beispiele') for x in ex)+'</ul></section>')
    else:
        ids={n['sense_id'] for n in ns}
        for s in ns:
            se=[e for e in ex if e.get('sense_id')==s['sense_id']]
            h += [f'<section class="sense" data-sense-id="{esc(s["sense_id"])}">',f'<h3>{esc(s["sense_de"])}</h3>',f'<p class="fa" lang="fa" dir="rtl">{esc(s["sense_fa"])}</p>', '<h4>Beispiele · مثال‌ها</h4><ul class="examples">'+''.join(pair_li(e,'Beispiele') for e in se)+'</ul>']
            for cat,label in [('Kombinationen_DE_FA','Kombinationen'),('Feste_Wendungen_DE_FA','Feste Wendungen'),('Satzmuster_DE_FA','Satzmuster')]:
                vals=s.get(cat) or []
                if vals:h.append(f'<h4>{label}</h4><ul>'+''.join(pair_li(e,cat) for e in vals)+'</ul>')
            for cat,label in [('Synonyme','Synonyme'),('Antonyme','Antonyme'),('Wortfamilie','Wortfamilie'),('Verwandte_Woerter_KEINE_Synonyme','Verwandte Wörter')]:
                vals=s.get(cat) or []
                if vals:h.append(f'<h4>{label}</h4><ul>'+''.join(f'<li>{esc(v)}</li>' for v in vals)+'</ul>')
            if s.get('usage_distinction_de'):h.append(f'<p class="usage">{esc(s["usage_distinction_de"])}</p>')
            h.append('</section>')
        unmatched=[e for e in ex if e.get('sense_id') not in ids]
        if unmatched:h.append('<section class="unresolved"><h3>Ungeklärte Sinn-Zuordnung · نیازمند بررسی</h3><ul>'+''.join(pair_li(e,'Beispiele') for e in unmatched)+'</ul></section>')
    h.append('</div></article>')
    return ''.join(h)
def qa(cards,lesson='L02'):
    results=[];errors=[];counts=collections.Counter()
    for c in cards:
        h=render(c);s=BeautifulSoup(h,'html.parser');b=c['back'];ex=(b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
        actual=[(li.get('data-de'),li.get('data-fa')) for li in s.select('li[data-section="Beispiele"]')]
        expected=collections.Counter((e['de'],e['fa']) for e in ex)
        if collections.Counter(actual)!=expected:errors.append({'ordinal':c['source_ordinal'],'reason':'EXAMPLE_PAIR_LOST_OR_DUPLICATED'})
        ns=b.get('semantic_network_sense_anchored_pending_qa') or []
        for n in ns:
            expected_sense=collections.Counter((e['de'],e['fa']) for e in ex if e.get('sense_id')==n['sense_id'])
            elem=next((x for x in s.select('section.sense') if x.get('data-sense-id')==n['sense_id']),None)
            got_sense=collections.Counter((e.get('data-de'),e.get('data-fa')) for e in elem.select('ul.examples li') if elem) if elem else {}
            if got_sense!=expected_sense:errors.append({'ordinal':c['source_ordinal'],'reason':'EXAMPLE_SENSE_ROUTING_ERROR','sense_id':n['sense_id']})
            for cat in ('Kombinationen_DE_FA','Feste_Wendungen_DE_FA','Satzmuster_DE_FA'):
                exp=collections.Counter((x['de'],x['fa']) for x in (n.get(cat) or []))
                got=collections.Counter((e.get('data-de'),e.get('data-fa')) for e in (elem.select('li[data-section="'+cat+'"]') if elem else []))
                if got!=exp:errors.append({'ordinal':c['source_ordinal'],'reason':'SENSE_COLLOCATION_OR_PHRASE_MISMATCH','section':cat})
        ids={n['sense_id'] for n in ns}
        if ns:
            unr=[e for e in ex if e.get('sense_id') not in ids]
            counts['unresolved_examples_in_cards_with_senses']+=len(unr)
            if c['lesson']==lesson and unr:errors.append({'ordinal':c['source_ordinal'],'reason':'L02_EXAMPLE_HAS_NO_DEFINED_SENSE','count':len(unr)})
        counts['examples']+=len(ex);counts['senses']+=len(ns);counts['cards']+=1
        if c['lesson']==lesson:counts['L02_cards']+=1;counts['L02_examples']+=len(ex)
        if c['back'].get('Formen_section') is not None:errors.append({'ordinal':c['source_ordinal'],'reason':'BACK_FORMS_REDUNDANT'})
        if c.get('import_ready') or c.get('formal_release_approved'):errors.append({'ordinal':c['source_ordinal'],'reason':'RELEASE_FLAG_IN_NONIMPORT'})
        results.append((c,h))
    return {'schema':'aspekte-b1plus-sense-grouped-html-QA-only@4','counts':dict(counts),'errors':errors,'pass':not errors,'actual_app_runtime_tested':False,'release_allowed':False},results
def write_html(cards,out):
    report,items=qa(cards)
    body=''.join(h for c,h in items if c['lesson']=='L02')
    css='body{font:15px system-ui,sans-serif;background:#f5f7fa;color:#162334;max-width:1280px;margin:20px auto;padding:10px}h1{font-size:24px}.tag{font-weight:bold;color:#97372c}.card{display:grid;grid-template-columns:1fr 2fr;gap:20px;padding:20px;margin:18px 0;background:white;border:1px solid #dbe2ea;border-radius:13px}.front{border-right:1px solid #e0e6ed;padding-right:18px}.front h2{font-size:20px}.forms{color:#42526b}.meaning{font-weight:bold;font-size:18px}.sense{margin-top:15px;border-top:2px solid #e0e6ed;padding-top:6px}.sense h3{font-size:17px}.sense h4{font-size:13px;color:#506076}.fa{text-align:right;display:block;margin:5px 0;color:#43556b}.usage{font-style:italic}.unresolved{background:#fff0db;padding:10px;border-radius:8px}ul{padding-left:22px}li{margin-bottom:11px}@media(max-width:800px){.card{grid-template-columns:1fr}.front{border-right:0;border-bottom:1px solid #ccc}}'
    doc='<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Aspekte B1+ L02 – 91 cards QA only</title><style>'+css+'</style></head><body><h1>Aspekte B1+ Lektion 02 — 91 Karten (Front/Back)</h1><p class="tag">QA-ONLY / NONIMPORT — dies ist NICHT die echte App-Laufzeit; alle 91 Karten bleiben RELEASE BLOCKED.</p>'+body+'</body></html>'
    Path(out).write_text(doc,encoding='utf-8')
    return report
if __name__=='__main__':
    with zipfile.ZipFile(sys.argv[1]) as z:cs=[json.loads(l) for l in z.read(SOURCE).splitlines()]
    print(json.dumps(write_html(cs,sys.argv[2]),ensure_ascii=False,indent=2))