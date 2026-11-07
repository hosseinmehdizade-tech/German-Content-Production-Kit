#!/usr/bin/env python3
"""R16→R17: source-grounded p02/p03 generic conclusion repair, 039–052.
Never restore original book or overwrite user-accepted earlier edits.
"""
import pathlib, json, copy, hashlib, re, collections
P=pathlib.Path('/mnt/data/lesen_r17_20261107')
BASE=pathlib.Path('/mnt/data/lesen_r16_20261107/Lesen-Production-Master-v1.3.0-R16-22CONCLUSIONS-TRILINGUAL-CANDIDATE.json')
OUT=P/'Lesen-Production-Master-v1.3.0-R17-23CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
LED=P/'LESEN-R17-23CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json'
BASESHA='0b31f21ed6cd65b2562d3806e58269294196d161b05ba87cc7af35e3ab87ffa5'
sha=lambda b:hashlib.sha256(b).hexdigest()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(BASE.read_bytes())==BASESHA
A=json.loads(BASE.read_text(encoding='utf8'));B=copy.deepcopy(A)
G={'p02':'Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.',
   'p03':'Ein Vorteil auf der einen Seite kann also durchaus neue Probleme auf der anderen Seite erzeugen.'}
# Every German sentence was individually authored from the previously curated, concrete
# preceding German sentences and accepted FA/EN third sentence, unless a translation correction is explicit.
E={
39:{'p02':'Ein fair vereinbarter Beitrag kann so finanzielle Selbstständigkeit und eine Entlastung der Eltern miteinander verbinden.',
    'p03':'Eine pauschale Regel wäre deshalb unangemessen, wenn sie Einkommen und Ausbildungssituation junger Erwachsener nicht berücksichtigt.'},
40:{'p02':'So entsteht eine Form fachlicher Autorität, die den Unterricht stützt und zugleich kritische Fragen zulässt.',
    'p03':'Autorität, die kritische Fragen unterdrückt, widerspricht dem Ziel selbstständigen Denkens an Hochschulen.'},
41:{'p02':'Eine öffentliche Grundversorgung kann damit Ungleichheiten verringern, die aus unterschiedlichen familiären Möglichkeiten entstehen.'},
42:{'p02':'Auslandserfahrung kann Fähigkeiten fördern, die auch bei späteren beruflichen Aufgaben von Nutzen sind.',
    'p03':'Berufliche Chancen im Ausland können deshalb mit erheblichen persönlichen Belastungen verbunden sein.'},
43:{'p02':'Barrierefreiheit ist damit kein freiwilliger Zusatz, sondern ein wesentlicher Bestandteil guter Hochschullehre.',
    'p03':'Eine gute Inklusionspolitik braucht deshalb klare Ziele und praktische Schritte, die unterschiedliche Bedürfnisse berücksichtigen.'},
44:{'p02':'Ein öffentliches Sicherungsnetz kann so Altersarmut vorbeugen, die besonders Menschen mit geringen Einkommen bedroht.',
    'p03':'Ein langfristig tragfähiges Rentensystem muss daher unterschiedliche Finanzierungsquellen und Absicherungsmechanismen verbinden.'},
45:{'p02':'Individuelle Anstrengung bleibt deshalb wichtig, wirkt aber nie unabhängig von familiären und gesellschaftlichen Bedingungen.'},
46:{'p02':'Künstlerischer Unterricht vermittelt damit Kompetenzen, die über das bloße Erlernen künstlerischer Techniken hinausgehen.',
    'p03':'Wenn Schulen künstlerische Angebote ausbauen, müssen sie auch Raum, Materialien und qualifizierte Lehrkräfte einplanen.'},
47:{'p02':'Beide Wissenschaftsbereiche beantworten somit unterschiedliche, aber gleichermaßen wichtige gesellschaftliche Fragen.',
    'p03':'Natur- und Geisteswissenschaften sollten bei komplexen Problemen zusammenwirken, statt gegeneinander ausgespielt zu werden.'},
48:{'p02':'Bedürfnisse nach Gespräch und Zuwendung sind Aspekte, die in der Behandlung nicht übersehen werden sollten.',
    'p03':'Subjektives Wohlbefinden ersetzt deshalb keine wissenschaftlichen Belege für Wirksamkeit und Sicherheit.'},
49:{'p02':'Freiwilliges Engagement eröffnet Jugendlichen Perspektiven, die sie in ihrem gewohnten Umfeld kaum kennenlernen würden.'},
50:{'p02':'Einfluss kann deshalb viele Formen annehmen, die nicht auf politische Macht beschränkt sind.',
    'p03':'Kurzfristige Bekanntheit in sozialen Medien ist daher kein zuverlässiger Maßstab für nachhaltigen gesellschaftlichen Einfluss.'},
52:{'p02':'KI kann so Freiräume schaffen, die Menschen für kreative, soziale oder strategische Aufgaben nutzen können.',
    'p03':'Mehr Geschwindigkeit durch KI ist deshalb nur dann ein Gewinn, wenn Entscheidungen geprüft und Risiken begrenzt werden.'}
}
assert sum(map(len,E.values()))==23 and len(E)==13
# These FOUR approved translations were ALSO generic; only their third sentence is revised.
T={
 (46,'p03'):{'fa':'پس گسترش درس‌های هنری باید با برنامه‌ریزی برای زمان، فضای آموزشی، تجهیزات و معلمان متخصص همراه باشد.',
              'en':'Expanding arts education therefore also requires planning for time, space, materials, and qualified teachers.'},
 (47,'p03'):{'fa':'پس علوم طبیعی و علوم انسانی باید برای حل مسائل پیچیده با هم همکاری کنند، نه اینکه در برابر یکدیگر قرار گیرند.',
              'en':'The natural sciences and humanities should therefore work together on complex problems instead of being set against one another.'},
 (50,'p03'):{'fa':'بنابراین شهرت کوتاه‌مدت در شبکه‌های اجتماعی معیار قابل‌اعتمادی برای سنجش نفوذ پایدار در جامعه نیست.',
              'en':'Short-term fame on social media is therefore not a reliable measure of lasting influence on society.'},
 (52,'p02'):{'fa':'به این ترتیب هوش مصنوعی می‌تواند زمانی آزاد کند که افراد آن را صرف کارهای خلاقانه، اجتماعی یا راهبردی کنند.',
              'en':'AI can thus free up time that people can devote to creative, social, or strategic tasks.'}
}
# Only nine p02 replacement conclusions have a previously accepted g06 curated relative-clause link.
RELATIVE_UNITS={40,41,42,44,46,48,49,50,52}
retired=0;rel_added=0;curated_retargeted=0;new_tr=0;changes=[]
for n, edits in E.items():
 u=B['items'][n-1];old=A['items'][n-1];assert u['id']==f'LES-PRES-{n:03d}'
 for sid,de in edits.items():
  sec=next(s for s in u['reading']['sections'] if s['id']==sid)
  oldsec=next(s for s in old['reading']['sections'] if s['id']==sid)
  assert len(sec['sentences'])==3 and sec['sentences'][-1]['id']==sid+'-s03'
  assert oldsec['sentences'][-1]['text']==G[sid] and de!=G[sid]
  assert len(de)>80 and de.endswith('.'),(n,sid,de)
  before=copy.deepcopy(sec)
  oldtr={l:re.split(r'(?<=[.!?؟])\s+',sec['translations'][l]) for l in ('fa','en')}
  assert all(len(p)==3 for p in oldtr.values()),(n,sid,oldtr)
  sec['sentences'][-1]['text']=de
  sec['text']=' '.join(z['text'] for z in sec['sentences'])
  if (n,sid) in T:
   for lang in ('fa','en'):
    newlast=T[n,sid][lang]
    assert newlast and newlast!=oldtr[lang][-1] and newlast.endswith('.')
    sec['translations'][lang]=' '.join(oldtr[lang][:2]+[newlast])
   new_tr+=1
  else: assert sec['translations']==before['translations']
  oldspans=[g for g in old['grammar']['full_text_occurrences'] if g['section_id']==sid and g['sentence_id']==sid+'-s03']
  assert len(oldspans)==(4 if sid=='p02' else 2),(n,sid,len(oldspans))
  gone={g['id'] for g in oldspans}; retired+=len(gone)
  u['grammar']['full_text_occurrences']=[g for g in u['grammar']['full_text_occurrences'] if g['id'] not in gone]
  cur=[g for g in u['grammar']['curated_annotations'] if g['section_id']==sid and g['sentence_id']==sid+'-s03']
  assert (len(cur)==1)==(sid=='p02' and n in RELATIVE_UNITS),(n,sid,cur)
  if cur:
   c=cur[0];assert c['grammar_key']=='relative_clause'
   mm=re.search(r', (die|der|das)\b(.*?)(?=\.)',de)
   assert mm,(n,de)
   clause=mm.group(1)+mm.group(2)
   assert clause.split()[-1] in {'entstehen','zulässt','sind','bedroht','hinausgehen','sollten','würden','sind','können'},(n,clause)
   c['target_text']=de;c['annotation_source']='editorial_source_aligned_relative_clause_r17'
   c['derivation_method']='existing_curated_g06_retargeted_to_attested_r17_sentence_not_native_nine_lens'
   curated_retargeted+=1
   spanstart=sec['text'].index(clause,sec['text'].index(de));ident=f'ftg-r17-{n:03d}-{sid}-relative'
   g={'id':ident,'grammar_key':'relative_clauses_all','label_de':'Relativsatz (redaktionell geprüft)',
      'section_id':sid,'sentence_id':sid+'-s03','start':spanstart,'end':spanstart+len(clause),
      'target_text':clause,'explanation_de':'Der Relativsatz erläutert das Bezugsnomen; das konjugierte Verb steht im Relativsatz am Ende.',
      'explanation_fa':'جملهٔ موصولی اسمِ پیش از خود را توضیح می‌دهد و فعل صرف‌شده در پایان جملهٔ موصولی می‌آید.',
      'details':{'pronoun':mm.group(1),'scope':'manually_validated_p02_conclusion_r17'},'confidence':'high',
      'annotation_source':'manual_scoped_r17','derivation_method':'attested_exact_relative_clause_not_full_native_engine'}
   assert sec['text'][g['start']:g['end']]==clause
   u['grammar']['full_text_occurrences'].append(g);rel_added+=1
  changes.append({'lesson_id':u['id'],'title_de':u['title_de'],'section_id':sid,'sentence_id':sid+'-s03',
    'before_de':before['sentences'][-1]['text'],'after_de':de,
    'before_fa_conclusion':oldtr['fa'][-1],'after_fa_conclusion':re.split(r'(?<=[.!?؟])\s+',sec['translations']['fa'])[-1],
    'before_en_conclusion':oldtr['en'][-1],'after_en_conclusion':re.split(r'(?<=[.!?؟])\s+',sec['translations']['en'])[-1],
    'translation_revised':(n,sid) in T,'first_two_de_preserved':before['sentences'][:2]==sec['sentences'][:2],
    'retired_old_grammar_ids':[g['id'] for g in oldspans],
    'curated_relative_retargeted':bool(cur),'reason':'Replace a generic conclusion with a claim grounded in the prior two source sentences and preserved specific translations; revise only previously generic FA/EN conclusions.'})
 u['reading']['word_count_de']=len(' '.join(s['text'] for s in u['reading']['sections']).split())
 u['quality']['content_hash']=sha(' '.join(s['text'] for s in u['reading']['sections']).encode())[:16]
 u['quality']['app_mapping_status']='r17_scoped_p02_p03_conclusion_candidate_preentry_only'
 u['grammar']['full_text_lens_summary']['occurrences']=len(u['grammar']['full_text_occurrences'])
 u['grammar']['full_text_lens_summary']['counts']=dict(collections.Counter(g['grammar_key'] for g in u['grammar']['full_text_occurrences']))
 u['grammar']['full_text_lens_summary']['scope_note_de']='R17: alte Marker der pauschalen Schlusssätze entfernt; neun reale Relativsätze redaktionell verankert. Keine Neuberechnung aller neun Linsen.'
 u['grammar']['full_text_lens_summary']['scope_note_fa']='در R17 نشانگرهای جمله‌های کلی حذف و ۹ جملهٔ موصولی واقعی به‌صورت محدود ثبت شدند؛ موتور کامل دوباره اجرا نشده است.'
 for c in u['grammar']['curated_annotations']:
  s=next(z for z in u['reading']['sections'] if z['id']==c['section_id']);ss=next(z for z in s['sentences'] if z['id']==c['sentence_id']);assert c['target_text'] in ss['text'],(n,c['id'])
assert len(changes)==23 and new_tr==4 and retired==72 and rel_added==curated_retargeted==9,(len(changes),new_tr,retired,rel_added,curated_retargeted)
assert [i+1 for i,(o,n) in enumerate(zip(A['items'],B['items'])) if o!=n]==sorted(E)
allg=[g for u in B['items'] for g in u['grammar']['full_text_occurrences']]
assert len(allg)==4097,len(allg)
for u in B['items']:
 for g in u['grammar']['full_text_occurrences']:
  sec=next(s for s in u['reading']['sections'] if s['id']==g['section_id'])
  ss=next(s for s in sec['sentences'] if s['id']==g['sentence_id'])
  assert sec['text'][g['start']:g['end']]==g['target_text'] and g['target_text'] in ss['text'],(u['id'],g['id'])
 assert len({g['id'] for g in u['grammar']['full_text_occurrences']})==len(u['grammar']['full_text_occurrences'])
qa=B['full_text_grammar_qa'];qa['occurrences']=len(allg);qa['offset_exact_matches']=len(allg);qa['counts']=dict(collections.Counter(g['grammar_key'] for g in allg))
qa['result']='R17_SOURCE_ALIGNED_23_CONCLUSIONS__SCOPED_GRAMMAR_NOT_FULL_NATIVE'
qa['r17_scope']={'lessons':len(E),'sections':len(changes),'old_generic_spans_retired':retired,'new_manual_real_relative_clauses':rel_added,'curated_examples_retargeted':curated_retargeted,'native_full_nine_lens_engine_rerun':False}
ws=[u['reading']['word_count_de'] for u in B['items']];B['qa_summary']['word_count_de']={'min':min(ws),'mean':round(sum(ws)/len(ws),1),'max':max(ws)}
B['qa_summary']['r17_scope']='23_GENERIC_CONCLUSIONS_039_TO_052__FOUR_FA_EN_TAILS_SOURCE_ALIGNED'
B['translation_qa']['r17_review_status']='19_APPROVED_FA_EN_ENDINGS_PRESERVED__FOUR_GENERIC_TAILS_REVISED__AI_SCOPED_NOT_INDEPENDENT_STAGE4'
B['content_version']='1.3.0-R17-CANDIDATE';B['status']='R17_23_SOURCE_ALIGNED_CONCLUSIONS_CANDIDATE__STAGE4_6_7_HOLD'
write(OUT,B)
rem={sid:sum(next(s for s in u['reading']['sections'] if s['id']==sid)['sentences'][-1]['text']==G[sid] for u in B['items']) for sid in G}
assert rem=={'p02':15,'p03':11},rem
ledger={'schema':'lesen-r17-23-conclusions-grammar-ledger@1','date':'2026-11-07','parent_r16_sha256':BASESHA,
 'candidate_sha256':sha(OUT.read_bytes()),'bytes':OUT.stat().st_size,'changed_units':sorted(E),'changed_sections':23,
 'unchanged_units':55,'preserved_original_fa_en_conclusions':38,'revised_fa_en_pairs':4,
 'grammar_before':4160,'obsolete_old_markers_retired':retired,'curated_g06_relative_retargets':curated_retargeted,
 'new_scoped_real_relative':rel_added,'grammar_after':len(allg),'remaining_generic_p02':rem['p02'],
 'remaining_generic_p03':rem['p03'],'formal_semantic_stage4':'HOLD','native_browser_stage6':'NOT_RUN','full_nine_lens_rerun':False,'changes':changes}
write(LED,ledger);print(json.dumps({k:v for k,v in ledger.items() if k!='changes'},ensure_ascii=False,indent=2))