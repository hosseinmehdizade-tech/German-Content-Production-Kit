#!/usr/bin/env python3
"""Independent read-only verification for R19; no editing of candidate files."""
from pathlib import Path
import json,hashlib,copy,collections,re
R=Path('/mnt/data/lesen_r19_20261108');P=Path('/mnt/data/lesen_r18_20261107')
p0=P/'Lesen-Production-Master-v1.3.0-R18-26CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
r0=P/'Lesen-R18-v505-26CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'
p1=R/'Lesen-Production-Master-v1.3.0-R19-10P06-TRILINGUAL-CANDIDATE.json'
r1=R/'Lesen-R19-v505-10P06-RUNTIME-PREENTRY-CANDIDATE.json'
L=R/'LESEN-R19-10P06-EDITORIAL-GRAMMAR-LEDGER.json'
J=lambda p:json.loads(p.read_text(encoding='utf-8'))
h=lambda x:hashlib.sha256(x).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
s=J(p1);t=J(r1);os=J(p0);ot=J(r0);log=J(L)
assert h(p0.read_bytes())=='bfd469d4027f59d97cb25baabbefd79b0576f47f13acdc965f82850fc8a63c37'
assert h(r0.read_bytes())=='a4d9669ff3db155380a69c74dcad5006d307e68718abdf8fa8a24fe83c64fe9f'
checks=0; failures=[]
def ok(test,label):
 global checks
 checks+=1
 if not test:failures.append(label)
base='Wichtig ist, dass die Entscheidung nachvollziehbar begründet wird und nicht allein auf Gewohnheit, Idealvorstellungen oder kurzfristigen Eindrücken beruht.'
ok(len(s['items'])==len(t['entries'])==68,'68 units')
ok(len(log['changes'])==10,'10 edits in ledger')
ok(s['content_version']=='1.3.0-R19-CANDIDATE','master version')
ok(t['compiled_from']['sha256']==h(p1.read_bytes()),'runtime master hash')
ok(t['integrity']['entries_sha256']==h(canon(t['entries'])),'runtime entries digest')
ok(t['integrity']['payload_sha256']==h(canon({k:v for k,v in t.items() if k!='integrity'})),'runtime payload digest')
changed_ids=set(f'LES-PRES-{i:03d}' for i in range(11,21))
ct=collections.Counter();seen_ids=set();new_gram=0;old_removed=0
for i,(a,b,ra,rb) in enumerate(zip(s['items'],os['items'],t['entries'],ot['entries'])):
 id=a['id'];ok(id==b['id']==ra['source_item_id']==rb['source_item_id'],'source_id:'+id)
 ok(a['title_de']==b['title_de'] and a['questions']==b['questions'] and a['vocabulary']==b['vocabulary'],'questions vocab fixed:'+id)
 ok(ra['exercises']==rb['exercises'] and ra['unit']['vocabulary_target_ids']==rb['unit']['vocabulary_target_ids'],'runtime exercise fixed:'+id)
 ok(a['grammar']['curated_annotations']==b['grammar']['curated_annotations'],'curated grammar fixed:'+id)
 if id not in changed_ids:
  ok(a==b,'unmodified source unit:'+id)
  ok(ra==rb,'unmodified runtime entry:'+id)
 else:
  sec=next(x for x in a['reading']['sections'] if x['id']=='p06');orig=next(x for x in b['reading']['sections'] if x['id']=='p06')
  rp=next(x for x in ra['unit']['passages'] if x['r38']['source_section_id']=='p06');op=next(x for x in rb['unit']['passages'] if x['r38']['source_section_id']=='p06')
  ok(sec['sentences'][0]==orig['sentences'][0],'unchanged first p06 sentence:'+id)
  ok(orig['sentences'][1]['text']==base and sec['sentences'][1]['text']!=base,'new source-grounded p06-s02:'+id)
  ok(len(sec['sentences'])==2 and sec['text']==' '.join(x['text'] for x in sec['sentences']),'updated full section text:'+id)
  ok(rp['text_de']==sec['text'] and rp['translations']==sec['translations'],'runtime trilingual projection:'+id)
  ok([x for x in a['reading']['sections'] if x['id']!='p06']==[x for x in b['reading']['sections'] if x['id']!='p06'],'non-p06 sections exact:'+id)
  ok([x for x in ra['unit']['passages'] if x['r38']['source_section_id']!='p06']==[x for x in rb['unit']['passages'] if x['r38']['source_section_id']!='p06'],'non-p06 runtime exact:'+id)
  ok(ra['unit']['r38']['grammar']==a['grammar'],'runtime grammar exact:'+id)
  new=[g for g in a['grammar']['full_text_occurrences'] if g['section_id']=='p06' and g['sentence_id']=='p06-s02']
  previous=[g for g in b['grammar']['full_text_occurrences'] if g['section_id']=='p06' and g['sentence_id']=='p06-s02']
  ok(len(previous)==4 and len(new)==1 and new[0]['annotation_source']=='R19_MANUAL_SCOPED_EDITORIAL','manual grammar provenance:'+id)
  ok([g for g in a['grammar']['full_text_occurrences'] if not(g['section_id']=='p06' and g['sentence_id']=='p06-s02')]==sorted([g for g in b['grammar']['full_text_occurrences'] if not(g['section_id']=='p06' and g['sentence_id']=='p06-s02')],key=lambda g:(g['section_id'],g['start'],g['end'],g['id'])),'preserved all other grammar:'+id)
  new_gram+=len(new);old_removed+=len(previous)
  ledger=next(row for row in log['changes'] if row['source_item_id']==id)
  ok(ledger['after']['de']==sec['sentences'][1]['text'] and ledger['after']['fa']==sec['translations']['fa'] and ledger['after']['en']==sec['translations']['en'],'before-after ledger:'+id)
  ok(ledger['before']['de']==orig['sentences'][1]['text'] and ledger['before']['fa']==orig['translations']['fa'] and ledger['before']['en']==orig['translations']['en'],'old translation evidence:'+id)
  ok(('translation_pair' in ledger) or ('changed_translation_pair' in ledger),'translation preservation documented:'+id)
  ok(ra['unit']['r38']['word_count_de']==a['reading']['word_count_de'],'word count metadata mirrored:'+id)
 sec_ids={x['id'] for x in a['reading']['sections']};ok(sec_ids=={x['id'] for x in b['reading']['sections']} and len(sec_ids) in (7,9),'unchanged original section structure:'+id)
 ok(len(a['questions'])==5,'5 questions:'+id)
 ok(len(ra['exercises'])==5,'5 runtime exercises:'+id)
 ok(len(a['grammar']['curated_annotations'])==len(b['grammar']['curated_annotations']),'curated count stable:'+id)
 ok(len(a['vocabulary'])==len(b['vocabulary']),'vocab count stable:'+id)
 gs=a['grammar']['full_text_occurrences'];ids=[g['id'] for g in gs];ok(len(ids)==len(set(ids)),'unique grammar ids within lesson:'+id)
 gram_counter=collections.Counter(g['grammar_key'] for g in gs)
 ok(all(a['grammar']['full_text_lens_summary']['counts'].get(k,0)==gram_counter.get(k,0) for k in set(a['grammar']['full_text_lens_summary']['counts'])|set(gram_counter)),'fulltext lens summary counts:'+id)
 ok(len(gs)==a['grammar']['full_text_lens_summary']['occurrences'],'fulltext per-item count:'+id)
 ok(gs==ra['unit']['r38']['grammar']['full_text_occurrences'],'runtime fulltext matches:'+id)
 for sec in a['reading']['sections']:
  ok(bool(sec['translations']['fa']) and bool(sec['translations']['en']),'complete translations:'+id+sec['id'])
  ok(sec['text']==' '.join(y['text'] for y in sec['sentences']),'full section equals sentences:'+id+sec['id'])
  ok(len(set(y['id'] for y in sec['sentences']))==len(sec['sentences']),'sentence IDs unique:'+id+sec['id'])
  ok(sec['text']==next(x for x in ra['unit']['passages'] if x['r38']['source_section_id']==sec['id'])['text_de'],'runtime section text:'+id+sec['id'])
  ok(sec['translations']==next(x for x in ra['unit']['passages'] if x['r38']['source_section_id']==sec['id'])['translations'],'runtime translations exact:'+id+sec['id'])
 for g in gs:
  ct[g['grammar_key']]+=1
  sec=next(y for y in a['reading']['sections'] if y['id']==g['section_id'])
  text=sec['text'];st,ed=g['start'],g['end'];ok(isinstance(st,int) and isinstance(ed,int) and 0<=st<ed<=len(text),'valid grammar bounds:'+id+g['id'])
  ok(text[st:ed]==g['target_text'],'exact grammar anchor:'+id+g['id'])
  sent=next((y for y in sec['sentences'] if y['id']==g['sentence_id']),None)
  ok(sent is not None and g['target_text'] in sent['text'],'grammar sentence scope:'+id+g['id'])
 assert len(a['questions'])==5
ok(sum(len(z['grammar']['full_text_occurrences']) for z in s['items'])==4011,'total grammar 4011')
ok(s['full_text_grammar_qa']['occurrences']==4011 and s['full_text_grammar_qa']['counts']==dict(ct),'global grammar QA summary exact')
ok(t['counts']['full_text_grammar']==4011,'runtime global grammar count')
ok(t['counts']['passages']==478 and t['counts']['exercises']==340 and t['counts']['vocabulary_entries']==350,'runtime totals intact')
ok(sum(len(z['grammar']['curated_annotations']) for z in s['items'])==669,'669 curated grammar unchanged')
ok(new_gram==10 and old_removed==40,'scope grammar 40 removed + 10 observed added')
ok(sum(x['reading']['sections'][5]['sentences'][1]['text']==base for x in s['items'])==48,'generic p06 residual 48')
ok(sum(1 for z in log['changes'] if z['changed_translation_pair'])==8,'8 translation pairs updated')
ok(sum(1 for z in log['changes'] if not z['changed_translation_pair'])==2,'2 approved translations preserved')

def run_negative():
 f=[]
 def probes(obj):
  # Return pass/fail using a genuinely separate invariant; no stubs.
  errs=[]
  src=obj['items'];
  if len(src)!=68:errs.append('wrong lesson count')
  ids=[i['id'] for i in src]
  if len(set(ids))!=len(ids):errs.append('duplicate source item')
  for x in src:
   sec={z['id']:z for z in x['reading']['sections']}
   if not all(z['translations'].get('fa') and z['translations'].get('en') for z in sec.values()):errs.append('missing translation')
   if any(z['text']!=' '.join(v['text'] for v in z['sentences']) for z in sec.values()):errs.append('broken sentence projection')
   if len(x['questions'])!=5:errs.append('invalid question number')
   if len({z['id'] for z in x['grammar']['full_text_occurrences']})!=len(x['grammar']['full_text_occurrences']):errs.append('duplicate grammar id')
   for g in x['grammar']['full_text_occurrences']:
    if g['section_id'] not in sec:errs.append('invalid section reference');continue
    st,ed=g['start'],g['end']
    if not(isinstance(st,int) and isinstance(ed,int) and 0<=st<ed<=len(sec[g['section_id']]['text']) and sec[g['section_id']]['text'][st:ed]==g['target_text']):errs.append('corrupt grammar offset')
  return errs
 variants=[('bad count',lambda d:d['items'].pop()),('duplicate lesson',lambda d:d['items'][0].update(id=d['items'][1]['id'])),('no fa',lambda d:d['items'][10]['reading']['sections'][5]['translations'].update(fa='')),('no en',lambda d:d['items'][10]['reading']['sections'][5]['translations'].update(en='')),('wrong sentence',lambda d:d['items'][10]['reading']['sections'][5]['sentences'][1].update(text='Ausgetauschter Satz.')),('bad question count',lambda d:d['items'][10]['questions'].pop()),('duplicate grammar ID',lambda d:d['items'][10]['grammar']['full_text_occurrences'][0].update(id=d['items'][10]['grammar']['full_text_occurrences'][1]['id'])),('corrupt offset',lambda d:d['items'][10]['grammar']['full_text_occurrences'][0].update(start=99999)),('wrong target',lambda d:d['items'][10]['grammar']['full_text_occurrences'][0].update(target_text='does_not_exist'))]
 for name,mut in variants:
  a=copy.deepcopy(s);mut(a);errs=probes(a);f.append({'name':name,'rejected':bool(errs),'error_count':len(errs),'examples':errs[:2]})
 return f
neg=run_negative();ok(all(x['rejected'] for x in neg),'all nine adversarial cases rejected')
result={'schema':'lesen-r19-independent-qa@1','date':'2026-11-08','status':'PASS_SCOPED_STRUCTURE_ONLY' if not failures else 'FAIL',
 'source_master_sha256':h(p1.read_bytes()),'runtime_sha256':h(r1.read_bytes()),'structural_checks':checks,'failures':failures,
 'negative_probes':neg,'counts':{'lesson_count':68,'translation_sections':478,'questions':340,'vocab_items':350,'curated_grammar':669,'grammar_fulltext_occurrences':4011,'changed_lessons':10,'unchanged_lessons':58,'new_grammar':new_gram,'retired_old_grammar':old_removed,'generic_p06_s02_remaining':48,'fa_en_changed_pairs':8,'fa_en_preserved_pairs':2},
 'scope_limitations':{'independent_full_semantic_stage4':'HOLD','original_full_nine_lens_grammar_engine':'NOT_RERUN','browser_indexeddb_stage6':'NOT_RUN','final_stage7':'NOT_RELEASED'},
 'notes':['All other 58 lesson objects and runtime entries retained exactly.','All fulltext offsets exact in complete section text, and target phrase present in designated sentence.','Grammar annotation source explicit for manual scoped additions.']}
(R/'LESEN-R19-INDEPENDENT-SOURCE-QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'structural_checks':checks,'negative_rejected':sum(x['rejected'] for x in neg),'fulltext_grammar':4011,'failures':failures[:20]},ensure_ascii=False,indent=2))
if failures:raise SystemExit(1)