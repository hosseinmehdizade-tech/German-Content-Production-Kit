#!/usr/bin/env python3
"""R15->R16: 22 German topic-specific conclusions grounded in the original, already
specific Persian/English translations. Scoped exact grammar, no false native rerun.
The manually accepted R15 master is the only editorial source, NOT original PDFs.
"""
import pathlib,copy,json,hashlib,collections,re
P=pathlib.Path('/mnt/data/lesen_r16_20261107'); P.mkdir(exist_ok=True)
BASE=pathlib.Path('/mnt/data/lesen_r15_20261107/Lesen-Production-Master-v1.3.0-R15-25CONCLUSIONS-TRILINGUAL-CANDIDATE.json')
OUT=P/'Lesen-Production-Master-v1.3.0-R16-22CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
LED=P/'LESEN-R16-22CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json'
EXPECTED='efa0fa9ece712f3a045ef47c802efe9230fe1baa366cb43e7f3ba5a8573e4c67'
sha=lambda b:hashlib.sha256(b).hexdigest()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(BASE.read_bytes())==EXPECTED
A=json.loads(BASE.read_text());B=copy.deepcopy(A)
G={'p02':'Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.','p03':'Ein Vorteil auf der einen Seite kann also durchaus neue Probleme auf der anderen Seite erzeugen.'}
# Each German concluding sentence was authored to convey the EXISTING specific
# meaning of the sentence-three German->Persian and English translations.
# Retaining their correct translations avoids degrading user-accepted content.
# The two earlier sentences and both complete FA/EN texts remain byte-identical.
E={
25:{'p02':'Realistische Lernpläne schaffen Freiräume, die auf Dauer konzentriertes Arbeiten und höhere Produktivität ermöglichen.'},
26:{'p02':'Eine gelungene Verfilmung kann zum Einstieg in ein literarisches Werk werden, das man anschließend selbst lesen möchte.',
    'p03':'Was den Film schnell zugänglich macht, kann zugleich einen Teil der eigenen Vorstellung beim Lesen verdrängen.'},
27:{'p02':'Solche Lerngewohnheiten und Gespräche erleichtern Jugendlichen den Übergang an die Hochschule.',
    'p03':'Elterliche Unterstützung kann deshalb ins Gegenteil umschlagen, wenn sie zur Kontrolle der Studienwahl wird.'},
28:{'p02':'Regelmäßige echte Sprachpraxis ist daher oft wirksamer als viele Lernstunden, die ohne klare Anwendung unregelmäßig bleiben.',
    'p03':'Eine Lernmethode, die eine Person motiviert, kann andere mit einem anderen Lerntempo überfordern.'},
29:{'p02':'Kommentierte Ausgaben schaffen einen Zugang, der historische Sprache und ihren Kontext verständlicher macht.'},
30:{'p02':'Bei bestimmten Bewerbungen kann ein bekannter Hochschulname ein Vorteil sein, der zusätzliche Aufmerksamkeit erzeugt.',
    'p03':'Ein bekannter Name garantiert daher weder eine bessere Betreuung noch eine bessere persönliche Studienerfahrung.'},
31:{'p02':'Mit klaren Aufgaben kann das Smartphone zu einem Lernwerkzeug werden, das mehr bietet als bloßen Medienkonsum.',
    'p03':'Das gleiche Gerät, das spontan beim Lernen hilft, kann durch Benachrichtigungen zugleich die Konzentration stören.'},
32:{'p02':'Technische Hilfen können Sicherheit und Selbstständigkeit fördern, die für viele Menschen im Alltag entscheidend sind.',
    'p03':'Größere technische Fähigkeiten bedeuten daher nicht automatisch, dass Maschinen bessere Entscheidungen für Menschen treffen.'},
33:{'p02':'Musikunterricht vermittelt Fähigkeiten, die weit über das bloße Erlernen von Instrumenten hinausgehen.'},
34:{'p02':'Wer berufliche Netzwerke gezielt nutzt, kann Kontakte gewinnen, die echte Karrierechancen eröffnen.',
    'p03':'Mehr Sichtbarkeit im Internet ist deshalb nicht automatisch ein Vorteil für die berufliche Entwicklung.'},
36:{'p02':'Schulen können eine Ernährungskompetenz vermitteln, die Kindern bei bewussten Entscheidungen im Alltag hilft.',
    'p03':'Ernährungsbildung sollte deshalb informieren, statt Familien wegen ihrer Lebensweise zu beurteilen.'},
37:{'p02':'Auch Hochschulen brauchen pädagogische Fähigkeiten, die über bloße Fachkenntnisse hinausgehen.'},
38:{'p02':'Ein breiterer Hochschulzugang kann gesellschaftliche Vorteile bringen, die sich aus mehr Vielfalt und neuen Perspektiven ergeben.',
    'p03':'Wer Studienplätze ausweitet, ohne mehr Lehrkräfte, Betreuung und Geld bereitzustellen, gefährdet die Bildungsqualität.'}
}
assert sorted(E)==[25,26,27,28,29,30,31,32,33,34,36,37,38]
assert sum(map(len,E.values()))==22
retired=0;curated_retargets=0;new_grammar=0; ledger=[]
for n,edits in E.items():
 u=B['items'][n-1];old=A['items'][n-1];assert u['id']==f'LES-PRES-{n:03d}'
 for sid,de in edits.items():
  sec=next(x for x in u['reading']['sections'] if x['id']==sid);prior=next(x for x in old['reading']['sections'] if x['id']==sid)
  assert len(sec['sentences'])==3 and sec['sentences'][-1]['id']==sid+'-s03'
  assert prior['sentences'][-1]['text']==G[sid],(n,sid)
  assert de.endswith('.') and len(de)>65 and de != G[sid]
  # Preserve user-accepted FA/EN exactly: they ALREADY articulate the specific conclusion.
  tr_sentences={}
  for lang in ['fa','en']:
   parts=re.split(r'(?<=[.!?؟])\s+',prior['translations'][lang])
   assert len(parts)==3,(n,sid,lang,parts)
   tr_sentences[lang]=parts[-1]
   assert len(parts[-1])>=35
  sec['sentences'][-1]['text']=de
  sec['text']=' '.join(s['text'] for s in sec['sentences'])
  assert sec['translations']==prior['translations']
  for cur in u['grammar']['curated_annotations']:
   if cur['section_id']==sid and cur['sentence_id']==sid+'-s03':
    assert sid=='p02' and cur['grammar_key']=='relative_clause',(n,sid,cur)
    assert re.search(r', (die|der|das|denen|dem)\b',de),(n,de)
    cur['target_text']=de
    cur['annotation_source']='editorial_reviewed_relative_clause_r16'
    cur['derivation_method']='existing_curated_sample_reanchored_to_real_r16_relative_clause_not_native_ninelens'
    curated_retargets+=1
  obsolete=[z for z in old['grammar']['full_text_occurrences'] if z['section_id']==sid and z['sentence_id']==sid+'-s03']
  assert len(obsolete)==(4 if sid=='p02' else 2),(n,sid,len(obsolete))
  retired+=len(obsolete)
  gone={x['id'] for x in obsolete}
  u['grammar']['full_text_occurrences']=[z for z in u['grammar']['full_text_occurrences'] if z['id'] not in gone]
  # Reconnect the REAL relative clause in the 10 reworked examples used by curated g06.
  if any(q['section_id']==sid and q['sentence_id']==sid+'-s03' and q['grammar_key']=='relative_clause' for q in u['grammar']['curated_annotations']):
   m=re.search(r', (die|der|das|denen|dem)\b',de)
   assert m,(n,de)
   target=de[m.start()+2:-1]  # relative pronoun through clause-final verb, excluding punctuation
   assert target and target in de
   spanstart=sec['text'].index(target,sec['text'].index(de))
   gid=f'ftg-r16-{n:03d}-{sid}-relative'
   assert gid not in {q['id'] for q in u['grammar']['full_text_occurrences']}
   obj={'id':gid,'grammar_key':'relative_clauses_all','label_de':'Relativsatz (manuell geprüft)',
        'section_id':sid,'sentence_id':sid+'-s03','start':spanstart,'end':spanstart+len(target),
        'target_text':target,'explanation_de':'Das Relativpronomen bezieht sich auf ein Nomen im Hauptsatz; im Relativsatz steht das finite Verb am Ende.',
        'explanation_fa':'ضمیر موصولی به اسم جملهٔ اصلی برمی‌گردد و فعل صرف‌شده در جملهٔ موصولی در پایان قرار می‌گیرد.',
        'details':{'relative_pronoun':m.group(1),'review_scope':'r16_exact_topic_specific_last_sentence'},
        'confidence':'high','annotation_source':'manual_scoped_verified_r16',
        'derivation_method':'explicit_relative_pronoun_with_clause_final_verb_not_native_ninelens'}
   assert sec['text'][obj['start']:obj['end']]==target
   u['grammar']['full_text_occurrences'].append(obj);new_grammar+=1
  ledger.append({'id':u['id'],'title_de':u['title_de'],'section_id':sid,
    'before_de':prior['sentences'][-1]['text'],'after_de':de,
    'existing_approved_fa_conclusion':tr_sentences['fa'],'existing_approved_en_conclusion':tr_sentences['en'],
    'preserve_full_fa_en':True,'source_first_two_de_preserved':prior['sentences'][:2]==sec['sentences'][:2],
    'retired_invalid_grammar_occurrences':obsolete,
    'meaning_alignment_reason':'German conclusion revised to express the already-specific FA/EN translations and the source first two sentences; no general knowledge inserted.'})
 u['reading']['word_count_de']=len(' '.join(z['text'] for z in u['reading']['sections']).split())
 u['quality']['content_hash']=sha(' '.join(z['text'] for z in u['reading']['sections']).encode())[:16]
 u['quality']['app_mapping_status']='r16_source_aligned_conclusions_candidate_preentry_only'
 g=u['grammar']['full_text_lens_summary'];g['occurrences']=len(u['grammar']['full_text_occurrences']);g['counts']=dict(collections.Counter(z['grammar_key'] for z in u['grammar']['full_text_occurrences']))
 g['scope_note_de']='R16: alte Marker der ersetzten Schlusssätze entfernt; zehn neue Relativsätze manuell und exakt verankert. Keine vollständige Neun-Linsen-Neuaufbereitung.'
 g['scope_note_fa']='در R16 نشانگرهای قدیمی جمله‌های جایگزین‌شده حذف و ده جملهٔ موصولی جدید با موقعیت دقیق بررسی شدند؛ اجرای کامل موتور اصلی انجام نشده است.'
 for cur in u['grammar']['curated_annotations']:
  s=next(z for z in u['reading']['sections'] if z['id']==cur['section_id'])
  sent=next(z for z in s['sentences'] if z['id']==cur['sentence_id'])
  assert cur['target_text'] in sent['text'],(n,cur['id'])
assert len(ledger)==22 and retired==70 and curated_retargets==10 and new_grammar==10,(len(ledger),retired,curated_retargets,new_grammar)
assert [i+1 for i,(old,new) in enumerate(zip(A['items'],B['items'])) if old!=new]==sorted(E)
allocc=[x for it in B['items'] for x in it['grammar']['full_text_occurrences']]
assert len(allocc)==4160,len(allocc)
for u in B['items']:
 for x in u['grammar']['full_text_occurrences']:
  s=next(y for y in u['reading']['sections'] if y['id']==x['section_id'])
  sent=next(y for y in s['sentences'] if y['id']==x['sentence_id'])
  assert s['text'][x['start']:x['end']]==x['target_text'] and x['target_text'] in sent['text'],(u['id'],x['id'])
 assert len({x['id'] for x in u['grammar']['full_text_occurrences']})==len(u['grammar']['full_text_occurrences'])
qa=B['full_text_grammar_qa'];qa['occurrences']=len(allocc);qa['offset_exact_matches']=len(allocc);qa['counts']=dict(collections.Counter(z['grammar_key'] for z in allocc))
qa['result']='R16_SCOPED_EXACT_P02_P03_CONCLUSIONS_AND_10_MANUAL_RELATIVE_CLAUSES__NATIVE_FULL_ENGINE_NOT_RERUN'
qa['r16_scope']={'units':len(E),'sections':len(ledger),'retired_old_span_count':retired,'retargeted_curated_relative_examples':curated_retargets,'new_manual_exact_relative_occurrences':new_grammar,'native_full_ninelens_rerun':False}
wcs=[u['reading']['word_count_de'] for u in B['items']];B['qa_summary']['word_count_de']={'min':min(wcs),'mean':round(sum(wcs)/len(wcs),1),'max':max(wcs)}
B['qa_summary']['r16_scope']='22_GERMAN_GENERIC_CONCLUSIONS_REALIGNED_TO_EXISTING_SPECIFIC_FA_EN_IN_13_UNITS'
B['translation_qa']['r16_review_status']='EXISTING_USER_ACCEPTED_FA_EN_PRESERVED__22_GERMAN_ENDINGS_ALIGNED__NO_INDEPENDENT_STAGE4'
B['content_version']='1.3.0-R16-CANDIDATE';B['status']='R16_22_SOURCE_BOUND_TRILINGUAL_ALIGNMENT_CANDIDATE__STAGE4_6_7_HOLD'
write(OUT,B)
remaining={sid:sum(next(s for s in u['reading']['sections'] if s['id']==sid)['sentences'][-1]['text']==G[sid] for u in B['items']) for sid in G}
assert remaining=={'p02':28,'p03':21},remaining
record={'schema':'lesen-r16-22-source-aligned-conclusions-grammar-ledger@1.0.0','date':'2026-11-07',
 'parent_r15_sha256':EXPECTED,'candidate_sha256':sha(OUT.read_bytes()),'candidate_bytes':OUT.stat().st_size,
 'changed_units':[f'LES-PRES-{n:03d}' for n in E],'changed_sections':22,'unchanged_units':55,
 'changed_de_sentences':22,'preserved_specific_fa_en_translations':44,
 'obsolete_context_grammar_retired':retired,'curated_relative_examples_retargeted':curated_retargets,
 'new_exact_manual_relative_occurrences':new_grammar,'grammar_before':4220,'grammar_after':len(allocc),
 'remaining_identical_generic_p02':remaining['p02'],'remaining_identical_generic_p03':remaining['p03'],
 'source_native_nine_lens_rerun':False,'full_independent_stage4':'HOLD','browser_stage6':'NOT_RUN','release_stage7':'NOT_RELEASED',
 'changes':ledger}
write(LED,record)
print(json.dumps({k:v for k,v in record.items() if k!='changes'},ensure_ascii=False,indent=2))