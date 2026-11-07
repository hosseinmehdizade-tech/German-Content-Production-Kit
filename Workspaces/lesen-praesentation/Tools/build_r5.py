#!/usr/bin/env python3
"""R5 editorial delta: improve 55 generic q04 comprehension questions and repair 3 malformed q03 answers.

Always begins from the exact independently pinned R3 content. NO reading text, translations,
lexical, grammar annotations, SRS identities, or pre-existing other question edits are changed.
"""
import copy, hashlib, json, pathlib, collections, re, sys
ROOT=pathlib.Path('/mnt/data')
PARENT=ROOT/'lesen_r3_20261107/Lesen-Production-Master-v1.3.0-R3-3UNIT-GRAMMAR-CANDIDATE.json'
OUTDIR=ROOT/'lesen_r5_20261107'
EXPECTED='2b7e29acb973d34e878f76df5135be740c0819934b457265a1fd281ca97c2a8e'
# Every q04/answer pair was explicitly authored against p04 (and checked against p05 where indicated).
# Numbers are durable owner order, NOT publication rank.
LINES=r'''
11 | Weshalb gelten einkommensabhängige Beiträge als sozial verträglicher als hohe einheitliche Studiengebühren? | Sie berücksichtigen die finanzielle Lage der Studierenden. Stipendien und sozialer Ausgleich können zudem verhindern, dass Familien mit geringem Einkommen vom Studium abgeschreckt werden.
12 | Wie kann Sportunterricht auch Kinder fördern, die in Wettkämpfen weniger erfolgreich sind? | Durch unterschiedliche Bewegungsangebote und eine Bewertung individueller Fortschritte statt ausschließlich von Kraft, Schnelligkeit und Wettbewerb.
13 | Unter welchen Bedingungen kann Tourismus eher zu respektvollem interkulturellem Austausch beitragen? | Wenn Reisende lokale Angebote respektvoll nutzen und die Regionen Besucherströme nachhaltig steuern, statt die Begegnungen allein dem Massentourismus zu überlassen.
14 | Wie könnte eine Schule klassische Literatur vermitteln, ohne die Lesefreude zu vernachlässigen? | Indem sie klassische und aktuelle Texte kombiniert und Schülerinnen und Schülern bei der Lektüre mehr Wahlmöglichkeiten eröffnet.
15 | Warum sollte die Studienwahl weder nur nach Interesse noch allein nach Arbeitsmarktprognosen erfolgen? | Weil persönliche Interessen und Fähigkeiten ebenso wichtig sind wie realistische Arbeitsmarktdaten; die Entscheidung sollte diese Gesichtspunkte gemeinsam berücksichtigen.
16 | Welche zwei Gewohnheiten können negative Folgen sozialer Medien für persönliche Beziehungen begrenzen? | Bewusst begrenzte Nutzungszeiten und die Pflege direkter persönlicher Begegnungen können helfen, digitale Kommunikation und unmittelbaren Kontakt auszubalancieren.
17 | Wie können Grundschulen Interesse an Naturwissenschaften wecken, ohne Kinder früh unter Leistungsdruck zu setzen? | Indem MINT-Angebote spielerisch und experimentell gestaltet werden, ohne sie sofort mit Noten oder früher Spezialisierung zu verbinden.
18 | Warum ist konkretes Lob für die Anstrengung sinnvoller als pauschales Lob für angebliche Begabung? | Konkretes, glaubwürdiges Lob würdigt die tatsächliche Anstrengung. Es legt den Schwerpunkt auf beeinflussbares Verhalten statt auf eine vermeintlich feste Eigenschaft.
19 | Nach welchen Kriterien sollte beurteilt werden, wie wichtig eine Erfindung wirklich war? | Neben ihrem unmittelbaren Nutzen sollten ihre Zugänglichkeit und ihre langfristigen Folgen berücksichtigt werden. So wird nicht nur der erste Eindruck bewertet.
20 | Was muss ein Fernstudienangebot leisten, damit fehlende Präsenzkontakte nicht zum Nachteil werden? | Es braucht zuverlässige Betreuung, Möglichkeiten zum Austausch und klare Lernstrukturen. Ohne diese Angebote kann die Selbstorganisation unnötig erschwert werden.
21 | Wie lassen sich Ehemaligenvereine so gestalten, dass nicht nur etablierte Absolventen profitieren? | Die Angebote sollten offen und transparent sein und ausdrücklich auch Berufseinsteigerinnen und Berufseinsteigern den Zugang ermöglichen.
22 | Wie lässt sich praktisches Werken in bestehende Schulfächer integrieren? | Praktische Projekte können mit Technik, Kunst oder Nachhaltigkeit verknüpft werden, sodass handwerkliche Erfahrungen mehrere Lernziele zugleich unterstützen.
23 | Welche Unterstützung durch Arbeitgeber macht Weiterbildung nach einem Abschluss realistischer? | Freie Zeit für das Lernen, eine Beteiligung an den Kosten und nachvollziehbare berufliche Entwicklungswege erleichtern die Weiterbildung.
24 | Warum kann es sinnvoll sein, je nach Lernaufgabe zwischen Wohnung und Bibliothek zu wechseln? | Verschiedene Aufgaben erfordern unterschiedliche Umgebungen. Lernende sollten ihre Wahl an der konkreten Tätigkeit und ihrer persönlichen Arbeitsweise ausrichten.
25 | Welche Funktion haben Pufferzeiten in einem realistischen Lernplan? | Sie schaffen Spielraum für unerwartete Aufgaben oder Verzögerungen. Ein Lernplan sollte deshalb regelmäßig angepasst werden, statt jede Minute festzulegen.
26 | Warum ist es problematisch, Buch und Verfilmung als vollständig austauschbare Produkte zu betrachten? | Buch und Film sind unterschiedliche Kunstformen. Ein sinnvoller Vergleich berücksichtigt die Möglichkeiten beider Medien, statt sie als identische Versionen zu behandeln.
27 | Wie können Eltern bei der Studienentscheidung helfen, ohne dem Kind die Entscheidung abzunehmen? | Sie können informieren, beraten und unterstützen, sollten aber mit zunehmendem Alter die endgültige Entscheidung dem Kind selbst überlassen.
28 | Wie lassen sich Schwierigkeiten beim Fremdsprachenlernen durch die Gestaltung des Lernens verringern? | Mit kleinen, konkreten Lernzielen und regelmäßigen Anwendungen in echten Situationen wird das Lernen überschaubarer und praxisnäher.
29 | Wie können Schulen diskriminierende oder veraltete Formulierungen in älteren Literaturwerken behandeln, ohne den Originaltext zu verändern? | Die Originalfassung bleibt erhalten; Vorworte, Fußnoten und Gespräche im Unterricht können problematische Stellen historisch einordnen.
30 | Warum kann die persönliche Passung eines Studiengangs wichtiger sein als der Rang einer Universität? | Inhalte, Betreuungsqualität, Kosten und persönliche Bedürfnisse beeinflussen das Studium unmittelbar. Ein Ranking allein bildet diese Unterschiede nicht ausreichend ab.
31 | Unter welchen Voraussetzungen kann das Smartphone im Unterricht ein Lernwerkzeug statt einer Ablenkung sein? | Klare Regeln, zeitlich begrenzte Einsatzphasen und konkrete Lernaufträge verringern die Gefahr, dass Benachrichtigungen oder Unterhaltung vom Unterricht ablenken.
32 | Welche Voraussetzungen nennt der Text für einen verantwortbaren Einsatz von Robotern im Alltag? | Sicherheitsregeln, die Klärung von Haftungsfragen und die Möglichkeit menschlicher Kontrolle müssen verbindlich geregelt sein.
33 | Warum sollte Musikunterricht nicht allein die Leistung am Instrument bewerten? | Ein vielfältiger Unterricht kann unterschiedlichen Fähigkeiten Raum geben und vermeidet, dass musikalische Bildung ausschließlich vom instrumentalen Leistungsstand abhängt.
34 | Was sollten Auszubildende und Berufstätige beachten, wenn sie soziale Medien für ihre Karriere einsetzen? | Sie sollten Privatsphäre, Zielgruppe und veröffentlichte Inhalte bewusst steuern, damit ihre Online-Präsenz zu beruflichen Zielen und persönlichen Grenzen passt.
36 | Wie lässt sich gesunde Ernährung in der Schule thematisieren, ohne Schülerinnen und Schüler zu beschämen? | Der Unterricht sollte sachlich und praxisnah sein und auf persönliche Abwertung verzichten. So können Ernährungsfragen besprochen werden, ohne einzelne Kinder bloßzustellen.
37 | Welche Verantwortung tragen Lehrende und Studierende gemeinsam für guten Hochschulunterricht? | Hochschullehrende sollten didaktische Grundkompetenzen entwickeln. Studierende müssen zugleich Verantwortung für ihr eigenes Lernen übernehmen.
38 | Welche konkreten Ressourcen müssen bei steigenden Studierendenzahlen mitwachsen? | Hochschulen müssen Personal, Räume und digitale Systeme entsprechend ausbauen, damit mehr Studierende nicht automatisch schlechtere Lernbedingungen bedeuten.
39 | Was wäre eine faire Grundlage für einen Kostenbeitrag junger Erwachsener im Elternhaus? | Der Beitrag sollte sich am tatsächlichen Einkommen, der Lebensphase und den realen Wohnkosten orientieren und nicht pauschal festgesetzt werden.
40 | Wodurch unterscheidet sich pädagogisch begründete Autorität von Einschüchterung? | Sie stützt sich auf Kompetenz, Fairness und Verantwortung, nicht auf Angst oder die bloße Durchsetzung von Macht.
41 | Wie können Staat und Familie die Pflege älterer Menschen sinnvoll aufteilen? | Professionelle Pflegeangebote können mit freiwilliger Unterstützung durch Angehörige verbunden werden, statt die gesamte Verantwortung nur einer Seite zuzuweisen.
42 | Welche Punkte sollte man vor einer Entscheidung für eine Arbeit im Ausland prüfen? | Eigene Ziele, die konkreten Vertragsbedingungen und die persönliche Lebenssituation sollten realistisch geprüft werden, bevor ein Umzug beschlossen wird.
43 | Was ist bei der Umsetzung von Nachteilsausgleichen für Studierende mit Behinderung besonders wichtig? | Die Betroffenen müssen systematisch einbezogen werden, und individuelle Nachteilsausgleiche sollten zuverlässig umgesetzt werden statt nur auf dem Papier zu stehen.
44 | Weshalb kann die Kombination staatlicher und zusätzlicher Vorsorge sinnvoller sein als eine ausschließliche Lösung? | Eine staatliche Grundsicherung lässt sich durch private oder betriebliche Vorsorge ergänzen; so werden unterschiedliche Formen der Altersabsicherung miteinander verbunden.
45 | Warum reicht es nicht, den beruflichen Werdegang allein mit persönlicher Leistung zu erklären? | Neben individuellem Handeln prägen strukturelle Rahmenbedingungen die Chancen. Beides muss gemeinsam berücksichtigt werden.
46 | Wie könnten Schulen trotz begrenzter Unterrichtszeit unterschiedliche künstlerische Interessen fördern? | Sie können passende Schwerpunkte wählen und verschiedene künstlerische Angebote miteinander kombinieren, statt nur eine Ausdrucksform vorzusehen.
47 | Welchen Nutzen hat die Zusammenarbeit von Natur- und Geisteswissenschaften? | Durch gezielte interdisziplinäre Zusammenarbeit lassen sich unterschiedliche Perspektiven verbinden, anstatt die beiden Wissenschaftsbereiche gegeneinander auszuspielen.
48 | Welche Grenzen müssen alternative Heilmethoden nach dem Text einhalten? | Sie sollten über wissenschaftliche Evidenz, Grenzen und Risiken transparent informieren und notwendige medizinische Diagnostik nicht ersetzen.
49 | Wie können Jugendliche für soziales Engagement gewonnen werden, ohne sie dazu zu verpflichten? | Freiwillige Angebote sollten vielfältig, leicht zugänglich und gut begleitet sein, damit Jugendliche passende Möglichkeiten finden können.
50 | Warum sollte der Einfluss einer bekannten Person nicht allein an ihrer Reichweite gemessen werden? | Auch die Dauer ihres Einflusses, dessen konkrete Folgen und die damit verbundene Verantwortung zählen bei der Bewertung.
52 | Was ist nötig, damit der Einsatz künstlicher Intelligenz verantwortbar bleibt? | Transparenz, menschliche Kontrolle und klar zugewiesene Verantwortlichkeiten müssen verbindlich geregelt sein.
53 | Warum gehören zu guter Bildung neben Fachkenntnissen auch überfachliche Kompetenzen? | Die Verbindung fachlicher Grundlagen mit überfachlichen Fähigkeiten ermöglicht ein breiteres Bildungsverständnis, statt Wissen auf einzelne Inhalte zu beschränken.
54 | Wie lässt sich eine Karriere planen und trotzdem Raum für Zufälle lassen? | Man kann eigene Ziele verfolgen und zugleich offen für ungeplante Möglichkeiten bleiben, statt jede Abweichung vom Plan auszuschließen.
55 | Unter welchen Bedingungen kann Leistungsanforderung beim Lernen sinnvoll sein, ohne zu Überlastung zu führen? | Anforderungen sollten realistisch gestaltet und durch ausreichende Erholungsphasen ergänzt werden.
56 | Warum sollten Bibliotheken digitale und physische Angebote miteinander verbinden? | Auf diese Weise können sie unterschiedliche Nutzungsformen unterstützen, statt digitale Informationen und klassische Bibliotheksangebote als Gegensätze zu behandeln.
57 | Was macht ein Teilzeitstudium zu einer echten Alternative und nicht nur zu einem reduzierten Stundenplan? | Der Wechsel zwischen Vollzeit und Teilzeit sollte einfach sein, und Mindeststandards müssen in beiden Modellen gelten.
58 | Welche Bedingungen können die Belastungen des Lebens in einem Internat abfedern? | Professionelle Betreuung und regelmäßiger Kontakt zur Familie können helfen, den Schul- und Wohnalltag besser zu bewältigen.
60 | Wie können Lehrende und Studierende in sozialen Netzwerken professionelle Grenzen wahren? | Berufliche Plattformen oder klar getrennte Nutzerkonten machen die Rollen deutlicher und vermeiden eine Vermischung privater und prüfungsbezogener Kontakte.
61 | Wie können Fantasy-Geschichten im Unterricht zum Nachdenken über die Wirklichkeit anregen? | Wenn die Geschichten mit Fragen, Vergleichen und Hintergrundwissen verbunden werden, können Lernende Parallelen zwischen erfundenen und realen Konflikten erkennen.
62 | Welche Regeln können verhindern, dass staatliche Kulturförderung von einzelnen Vorlieben abhängt? | Klare Kriterien, unabhängige Gremien und nachvollziehbare Budgets machen Förderentscheidungen überprüfbar.
63 | Warum müssen Übersetzer je nach Textsorte verschiedene Prioritäten setzen? | Weil etwa Inhalt, Stil und Wirkung nicht immer gleichzeitig gleich gut übertragen werden können. Die Prioritäten und Entscheidungen sollten transparent sein.
64 | Warum ist ein respektvoller Umgang wichtiger als persönliche Sympathie zwischen Lehrenden und Lernenden? | Lehrende können respektvoll und professionell handeln, ohne persönliche Nähe herzustellen. Gute Betreuung sollte nicht von gegenseitiger Sympathie abhängen.
65 | Was bedeutet es, Vorlesen als Dialog mit dem Kind zu gestalten? | Kinder können Fragen stellen, Bilder beschreiben oder Geschichten weitererzählen, statt nur schweigend zuzuhören.
66 | Wie lässt sich die Mitwirkung von Eltern an der Schule von Eingriffen in den Unterricht abgrenzen? | Klare Kommunikationswege, Elternabende und geregelte Beschwerden ermöglichen Austausch, ohne fachliche Entscheidungen der Lehrkräfte zu ersetzen.
67 | Woran erkennt man altersgerechte digitale Mediennutzung im Vorschulalter? | Sie bleibt kurz und begleitet und orientiert sich am Entwicklungsstand der Kinder statt an möglichst langer Bildschirmzeit.
68 | Welche Alternative zu einem verpflichtenden Elternführerschein wird im Text nahegelegt? | Kostenlose, leicht zugängliche und freiwillige Kurse sowie gezielte Unterstützung können Eltern helfen, ohne Elternschaft von einer Prüfung abhängig zu machen.
'''

def norm(s):return re.sub(r'\s+',' ',s.strip())
M={}
for line in LINES.strip().splitlines():
 bits=[x.strip() for x in line.split('|')]
 assert len(bits)==3,(line,len(bits))
 n=int(bits[0]);assert n not in M
 M[n]=(bits[1],bits[2])
assert len(M)==55, len(M)

def sha(b):return hashlib.sha256(b).hexdigest()
assert sha(PARENT.read_bytes())==EXPECTED
P=json.loads(PARENT.read_text('utf8'));D=copy.deepcopy(P)
GENERIC='Warum spielt die konkrete Ausgestaltung eine so wichtige Rolle?'
removed_q03=[];changed=[];old_to_new=[]
for item in D['items']:
 n=item['order']; q4=item['questions'][3]
 if n in M:
  assert q4['prompt_de']==GENERIC, (n,q4['prompt_de'])
  p04=item['reading']['sections'][3]['text'];assert 'Entscheidend ist deshalb die konkrete Ausgestaltung.' in p04,(n,p04[:100])
  prompt,answer=M[n]; assert prompt.endswith('?') and len(answer)>=50
  before=copy.deepcopy(q4)
  q4['prompt_de']=norm(prompt);q4['answer_de']=norm(answer)
  # Evidence is p04 or p05; both were checked manually for the authored answers.
  assert q4['evidence_section_ids']==['p04','p05']
  old_to_new.append({'lesson':n,'unit_id':item['id'],'title_de':item['title_de'],'question_id':q4['id'],'from':before,'to':copy.deepcopy(q4),'evidence_p04':p04,'evidence_p05':item['reading']['sections'][4]['text']})
  changed.append(item['id'])
 if n in (11,31,43):
  q3=item['questions'][2];old=q3['answer_de'];p3=item['reading']['sections'][2]['text'];assert 'Es besteht die Gefahr, dass' in p3
  if n==11:
   new='Das Gegenargument lautet, dass Studiengebühren Menschen aus einkommensschwachen Familien vom Studium abschrecken können. Bildungschancen sollten nicht vom Einkommen der Eltern abhängen.'
  elif n==31:
   new='Benachrichtigungen, soziale Medien und Spiele können stark ablenken. Das ist besonders problematisch, weil Smartphones gezielt auf Aufmerksamkeit und häufige Nutzung ausgerichtet sind.'
  else:
   new='Die Umsetzung von Inklusion erfordert Ressourcen, sorgfältige Planung und individuelle Lösungen. Nicht jede Barriere lässt sich sofort beseitigen; Standardlösungen reichen wegen unterschiedlicher Bedürfnisse nicht immer aus.'
  assert old!=new
  q3['answer_de']=new
  removed_q03.append({'lesson':n,'question_id':'q03','before':old,'after':new,'evidence_p03':p3})
D['content_version']='1.3.0-R5-Q04-55-REVIEWED-CANDIDATE'
D['status']='R5_55_QUESTION_Q04_REPLACEMENTS_3_Q03_REPAIRS__NO_TEXT_OR_GRAMMAR_CHANGE__STAGE4_STAGE6_HOLD'
D['qa_summary']=copy.deepcopy(P['qa_summary'])
D['qa_summary']['r5_scope']='55 generic q04 interpretive prompts and answers made text specific; 3 malformed q03 answer repairs; no passage or grammar changes'
D['qa_summary']['r5_pending']='Generic q01/q02/q03 prompts and templated passages remain. Not full lexical/semantic Stage4; not Stage6.'
# Preserve original quality/content-hash per lesson because reading text hasn't changed.
assert all(x['reading']==y['reading'] and x['grammar']==y['grammar'] and x['vocabulary']==y['vocabulary'] and x['quality']==y['quality'] for x,y in zip(P['items'],D['items']))
assert all([q['id'] for q in x['questions']]==[q['id'] for q in y['questions']] for x,y in zip(P['items'],D['items']))
assert [x['id'] for x in P['items']]==[x['id'] for x in D['items']]
assert sum(q['prompt_de']==GENERIC for x in D['items'] for q in x['questions'])==0
assert len(set(x['questions'][3]['prompt_de'] for x in D['items']))==68
OUTDIR.mkdir(parents=True,exist_ok=True)
masterpath=OUTDIR/'Lesen-Production-Master-v1.3.0-R5-55Q-CANDIDATE.json'
masterpath.write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
manifest={'schema':'lesen-r5-55q-editorial-delta@1.0.0','date':'2026-11-07','from_r3_sha256':EXPECTED,'r5_sha256':sha(masterpath.read_bytes()),'changed_units':len(changed),'changed_unit_ids':changed,'q04_replacements':len(old_to_new),'q03_answer_repairs':len(removed_q03),'questions_total':sum(len(x['questions']) for x in D['items']),'reading_passages_unchanged':478,'grammatical_occurrences_unchanged':4620,'original_current_unmodified':True,'semantic_status':'AUTHOR_REVIEWED_55_Q04_NOT_INDEPENDENT_STAGE4','stage6':'NOT_RUN','r5_questions':old_to_new,'r5_q03_repairs':removed_q03}
(OUTDIR/'LESEN-R5-QUESTION-DELTA-20261107.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in manifest.items() if k not in ('r5_questions','r5_q03_repairs')},indent=2))