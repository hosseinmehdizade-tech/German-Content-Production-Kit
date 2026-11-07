#!/usr/bin/env python3
"""Source-bound manual editorial R6: 20 Lesen units / 60 q01-q03 question-answer replacements.
No generative mass rewriting; 20 explicitly authored and evidence-linked triples.
Does not change user current source, paragraphs, translations, grammar, vocabulary or identities.
"""
from pathlib import Path
import json,hashlib,copy,collections
ROOT=Path('/mnt/data/lesen_r6_20261107')
BASE=Path('/mnt/data/lesen_r5_20261107/Lesen-Production-Master-v1.3.0-R5-55Q-CANDIDATE.json')
OUT=ROOT/'Lesen-Production-Master-v1.3.0-R6-20UNIT-Q123-CANDIDATE.json'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='6371522e011333c836969ae2983c69ecbc259743632a6b44226b3bc5ef7ab764'
# (central-argument, specific-text-detail, counterargument) — prompt + model answer, in German.
EDIT={
11:[
('Welchen Ausgleich zwischen Hochschulfinanzierung und Zugang zum Studium fordert der Text?', 'Hochschulen müssen dauerhaft gut finanziert werden, doch das Studium soll grundsätzlich unabhängig von der finanziellen Lage einer Familie zugänglich bleiben.'),
('Welche zwei Vorteile erwarten Befürworter von Studiengebühren?', 'Die Gebühren könnten zusätzliche Mittel für Lehre und Infrastruktur bereitstellen und den wahrgenommenen Wert eines Studienplatzes erhöhen.'),
('Warum könnten Studiengebühren die Chancengleichheit beeinträchtigen?', 'Menschen aus einkommensschwachen Familien könnten aus finanziellen Gründen auf ein Studium verzichten, obwohl Bildungschancen nicht vom Einkommen der Eltern abhängen sollten.')],
12:[
('Welche Haltung nimmt der Text zum verpflichtenden Sportunterricht und zu seiner Bewertung ein?', 'Sport soll zum festen Schulangebot gehören; Unterrichtsformen und Notengebung müssen jedoch unterschiedliche Fähigkeiten stärker berücksichtigen.'),
('Welche gesundheitlichen und sozialen Wirkungen des Schulsports werden angeführt?', 'Bewegung kann Gesundheit, Konzentration und Stressbewältigung fördern; Teamspiele trainieren Fairness, Zusammenarbeit und den Umgang mit Niederlagen.'),
('Weshalb kann einseitige Leistungsbewertung im Sport Kinder benachteiligen?', 'Leistungsdruck trifft besonders Kinder mit geringerer Sportlichkeit oder gesundheitlichen Einschränkungen, weil körperliche Voraussetzungen und Interessen stark variieren.')],
13:[
('Welche Spannung zwischen kulturellem Austausch und wirtschaftlichen Interessen zeigt der Text beim Tourismus?', 'Tourismus kann kulturell bereichern, wenn echte Begegnungen stattfinden; wirtschaftliche Interessen stehen diesem Ziel jedoch häufig im Weg.'),
('Welche Chancen für Begegnungen und für die regionale Wirtschaft eröffnet der Tourismus?', 'Reisen ermöglichen Kontakte mit fremden Sprachen und Lebensweisen; touristische Infrastruktur kann zugleich wirtschaftliche Möglichkeiten in den Regionen schaffen.'),
('Warum garantiert eine hohe Zahl touristischer Besuche noch kein interkulturelles Verständnis?', 'Massentourismus kann lokale Kultur vereinfachen oder verdrängen, und kurze Kontakte mit Gästen führen nicht automatisch zu gegenseitigem Verständnis.')],
14:[
('Wie sollte Literatur nach Auffassung des Textes in der Schule vermittelt werden?', 'Literatur sollte Teil des Unterrichts bleiben, aber dialogischer und lebensnäher behandelt werden, weil nicht jeder Text zu jeder Lerngruppe passt.'),
('Welche sprachlichen und gesellschaftlichen Fähigkeiten kann die Beschäftigung mit Literatur fördern?', 'Literatur kann Empathie, Perspektivwechsel und sprachliches Feingefühl stärken und Einblicke in historische sowie gesellschaftliche Erfahrungen vermitteln.'),
('Warum kann eine starre Pflichtlektüre die Lesefreude beeinträchtigen?', 'Verpflichtende Texte können Widerstand auslösen, wenn Interessen, Lesefähigkeiten und sprachliche Voraussetzungen der Schülerinnen und Schüler nicht berücksichtigt werden.')],
15:[
('Welchen Stellenwert räumt der Text Arbeitsmarktprognosen bei der Studienwahl ein?', 'Berufliche Perspektiven sind ein wichtiges Kriterium, dürfen persönliche Interessen und die Motivation für ein mehrjähriges Studium aber nicht verdrängen.'),
('Wie können Beschäftigungsaussichten und Arbeitsmarktdaten Studieninteressierten helfen?', 'Gute Aussichten können finanzielle Sicherheit und einen leichteren Berufseinstieg ermöglichen; Arbeitsmarktinformationen helfen, unrealistische Erwartungen früh zu korrigieren.'),
('Weshalb ist eine Studienentscheidung allein nach aktuellen Berufschancen riskant?', 'Eine rein ökonomische Wahl kann Interessen und Motivation vernachlässigen; zudem verändern sich Arbeitsmärkte, sodass heutige Prognosen keine Zukunftsgarantie bieten.')],
16:[
('Welche grundlegende Haltung zur Nutzung sozialer Medien vertritt der Text?', 'Soziale Medien sind weder grundsätzlich gut noch schlecht; sie sollten bewusst genutzt werden, weil Plattformen gezielt um Aufmerksamkeit konkurrieren.'),
('Auf welche zwei Arten können soziale Medien Menschen beim Austausch unterstützen?', 'Sie erleichtern den Kontakt über große Entfernungen und das Finden von Gemeinschaften; Informationen, Erfahrungen und Hilfe können rasch geteilt werden.'),
('Weshalb ist ständige digitale Erreichbarkeit kein Ersatz für emotionale Nähe?', 'Online-Kommunikation kann oberflächlich bleiben und psychischen Druck auslösen; viele digitale Kontakte bedeuten nicht automatisch tiefere persönliche Beziehungen.')],
17:[
('Welches Ziel sollte frühe naturwissenschaftliche und technische Bildung laut Text verfolgen?', 'Grundschulkinder sollen neugierig werden und Dinge ausprobieren, nicht durch frühe Spezialisierung oder Leistungsauslese unter Druck geraten.'),
('Welche zwei Lernchancen bieten frühe Experimente und Einblicke in technische Berufe?', 'Experimente fördern Neugier und problemlösendes Denken; Begegnungen mit MINT-Berufen können stereotype Berufsvorstellungen früh aufbrechen.'),
('Warum kann eine zu frühe MINT-Spezialisierung der Grundschule schaden?', 'Sie könnte andere Interessen verdrängen und Leistungsdruck erhöhen, obwohl die Grundschule breite Grundlagen und Freude am Entdecken vermitteln soll.')],
18:[
('Wie unterscheidet der Text hilfreiche Anerkennung von übertriebenem Kinderlob?', 'Kinder brauchen ehrliche Anerkennung, aber kein künstliches Dauerlob; auch kritische Rückmeldungen gehören zur Entwicklung.'),
('Was leisten ehrliche Anerkennung und auf das Verhalten bezogenes Lob?', 'Sie können Selbstvertrauen und Motivation stärken und dem Kind zeigen, welche Anstrengung oder Handlung konkret gelungen ist.'),
('Welche Gefahr besteht, wenn Kinder ständig pauschal gelobt werden?', 'Sie können von äußerer Bestätigung abhängig werden und Schwierigkeiten entwickeln, Fehler oder durchschnittliche Leistungen zu akzeptieren.')],
19:[
('Nach welchem Maßstab sollten technische Erfindungen laut Text beurteilt werden?', 'Nicht allein ihre Neuheit zählt, sondern vor allem ihr langfristiger Nutzen für die Gesellschaft; selbst hilfreiche Technologien können missbraucht werden.'),
('Welche zwei größeren Wirkungen können grundlegende Erfindungen entfalten?', 'Sie können Kommunikation, Mobilität oder Gesundheit vieler Menschen verbessern und weitere wirtschaftliche sowie wissenschaftliche Entwicklungen auslösen.'),
('Weshalb ist technischer Fortschritt nicht automatisch nur positiv?', 'Große Neuerungen können unvorhergesehene Nebenwirkungen und Abhängigkeiten schaffen; deshalb ist nicht jede technische Veränderung ein gesellschaftlicher Fortschritt.')],
20:[
('Unter welchen Umständen hält der Text ein Fernstudium für eine sinnvolle Alternative?', 'Ein Fernstudium eignet sich besonders, wenn zeitliche und räumliche Flexibilität wichtiger ist als das Campusleben; persönliche Studienerfahrungen lassen sich online aber nicht vollständig ersetzen.'),
('Für welche Lernenden erleichtern flexible Online-Angebote den Hochschulzugang?', 'Berufstätige und Eltern können zeitlich flexibler lernen, während Menschen außerhalb großer Städte leichter an Hochschulbildung teilnehmen können.'),
('Welche Schwierigkeiten können beim Fernstudium trotz seiner Flexibilität entstehen?', 'Fehlende persönliche Kontakte, hoher Bedarf an Selbstorganisation und weniger spontane Hilfe belasten vor allem Lernende, die nicht gut allein arbeiten können.')],
21:[
('Wann sind Alumni-Netzwerke aus Sicht des Textes sinnvoll?', 'Sie haben einen Wert, wenn sie Gemeinschaft und gegenseitige Unterstützung fördern statt nur Status, und sie ersetzen keine persönliche berufliche Leistung.'),
('Wie profitieren Absolventinnen und Absolventen sowie Hochschulen von Alumni-Netzwerken?', 'Ehemalige können Kontakte, Mentoring und Erfahrungsaustausch bieten; Hochschulen gewinnen langfristige Beziehungen zur Berufspraxis und zu Fördernden.'),
('Unter welchen Umständen könnten Alumni-Vereine soziale Unterschiede verstärken?', 'Wenn sie elitär auftreten oder vor allem wirtschaftliche Interessen bedienen, profitieren Menschen mit schlechterem Zugang zu Netzwerken weniger davon.')],
22:[
('Welche Rolle sollte praktische Arbeit im modernen Schulunterricht spielen?', 'Praktische Bildung soll erhalten bleiben, aber zeitgemäß und projektorientiert organisiert werden; nicht jede traditionelle Handarbeit passt in gleicher Form.'),
('Was können Schülerinnen und Schüler beim Werken anders lernen als in theoretischen Fächern?', 'Praktische Aufgaben schulen Feinmotorik, Planung und Problemlösen; Kinder erleben unmittelbar, wie aus einer eigenen Idee ein konkretes Ergebnis wird.'),
('Welche Ressourcenprobleme erschweren zusätzlichen Werkunterricht?', 'Die Unterrichtszeit ist begrenzt, und Materialien, geeignete Räume sowie qualifizierte Lehrkräfte müssen zusätzlich finanziert und organisiert werden.')],
23:[
('Warum sollte Weiterbildung nach dem Abschluss nicht allein Privatsache bleiben?', 'Lebenslanges Lernen ist sinnvoll, aber Unternehmen profitieren ebenfalls von aktuellem Wissen und müssen Verantwortung für Lernmöglichkeiten übernehmen.'),
('Weshalb wird Weiterbildung durch den Wandel der Arbeitswelt wichtiger?', 'Technische und organisatorische Veränderungen können bisheriges Wissen entwerten; neue Qualifikationen verbessern berufliche Chancen und ermöglichen Spezialisierung.'),
('Welche Schattenseite kann ständiger Weiterbildungsdruck für Beschäftigte haben?', 'Er kann Menschen zeitlich und finanziell belasten, obwohl manche erworbene Qualifikation im Beruf überhaupt nicht eingesetzt wird.')],
24:[
('Warum gibt es nach dem Text keinen für alle Menschen idealen Lernort?', 'Wohnung und Bibliothek haben unterschiedliche Vorzüge; Lerngewohnheiten, Konzentrationsfähigkeit und Aufgaben können einen Wechsel sinnvoll machen.'),
('Welche Eigenschaften einer Bibliothek können regelmäßiges Lernen erleichtern?', 'Ruhige feste Arbeitsplätze und die Trennung von Lernen und Freizeit geben Struktur; andere Lernende können zusätzlich motivieren.'),
('Welche praktischen Gründe sprechen für manche Lernende gegen die Bibliothek?', 'Anfahrt, begrenzte Öffnungszeiten und wenig Privatsphäre können hinderlich sein; manche arbeiten zu Hause konzentrierter und flexibler.')],
25:[
('Wie versteht der Text eine hilfreiche Lernorganisation?', 'Organisation soll entlasten und ist kein Selbstzweck; ein nachhaltiger Lernplan muss auch Spontaneität und Erholung berücksichtigen.'),
('Wie wirken realistische Zeitplanung und Prioritäten gegen Überforderung?', 'Regelmäßige Planung macht Arbeit leichter überschaubar, und klare Prioritäten helfen, wichtige Aufgaben von bloß dringenden Tätigkeiten zu unterscheiden.'),
('Warum können sehr starre Lernpläne ihren Zweck verfehlen?', 'Ungeplante Aufgaben und wechselnde Energie lassen rigide Pläne scheitern; der zusätzliche Planungsdruck kann Stress verstärken.')],
26:[
('Welche Gesamtposition vertritt der Text zum Verhältnis von Buch und Verfilmung?', 'Filme können Bücher sinnvoll ergänzen, aber wegen ihrer unterschiedlichen Darstellungsformen nicht vollständig ersetzen.'),
('Wodurch können Verfilmungen Menschen auch für literarische Vorlagen interessieren?', 'Filme vermitteln komplexe Geschichten anschaulich und emotional und können das Interesse an Büchern wecken, die man sonst nicht gelesen hätte.'),
('Warum können Filme eine literarische Vorlage nie vollständig wiedergeben?', 'Eine Verfilmung muss auswählen, kürzen und interpretieren; beim Lesen entstehen dagegen eigene Bilder und ein individuelles Erzähltempo.')],
27:[
('Was bedeutet nach Ansicht des Textes eine gute elterliche Vorbereitung auf ein Studium?', 'Eltern sollten Selbstständigkeit und Orientierung fördern, anstatt mit Leistungsdruck die Studienentscheidung des Kindes vorwegzunehmen.'),
('Mit welchen zwei Formen der Unterstützung können Eltern früh auf ein Studium vorbereiten?', 'Sie können eigenständiges Lernen und verlässliche Gewohnheiten fördern sowie über Bildungswege und realistische Erwartungen informieren.'),
('Warum kann zu starke elterliche Steuerung die Studienwahl erschweren?', 'Feste Vorgaben erzeugen Druck und verdrängen eigene Interessen; langfristige Motivation muss auch von den jungen Menschen selbst ausgehen.')],
28:[
('Welche Grundhaltung zum erfolgreichen Fremdsprachenlernen empfiehlt der Text?', 'Regelmäßigkeit und die Bereitschaft zu sprechen sind wichtiger als sofortige Perfektion; Grammatik und Genauigkeit sollen dennoch schrittweise wachsen.'),
('Warum sind regelmäßiger Sprachkontakt und aktives Ausprobieren so hilfreich?', 'Häufiger Kontakt unterstützt den Fortschritt stärker als seltene Lernblöcke; aktives Sprechen trotz Fehlern stärkt Ausdrucks- und Hörkompetenz.'),
('Welche Faktoren können Lernende beim Spracherwerb demotivieren?', 'Angst vor Fehlern, unklare Ziele und zu viele neue Wörter auf einmal können überfordern, zumal Menschen unterschiedlich schnell lernen.')],
29:[
('Welche Lösung bevorzugt der Text für problematische Sprache in älterer Literatur?', 'Historische Begriffe sollten meist erklärt und eingeordnet statt stillschweigend umgeschrieben werden; für jüngere Zielgruppen können Ausnahmen begründet sein.'),
('Was können kommentierte oder behutsam angepasste Ausgaben für heutige Leser leisten?', 'Erläuterungen machen ältere Texte zugänglicher, und bestimmte Anpassungen können verletzende oder diskriminierende Formulierungen weniger belastend machen.'),
('Weshalb kann das Umschreiben alter Literatur historisch problematisch sein?', 'Eingriffe können den ursprünglichen Charakter verändern und Konflikte aus der Entstehungszeit unsichtbar machen, obwohl Literatur auch Zeitzeugnis ist.')],
30:[
('Welchen Stellenwert sollte der Ruf einer Hochschule bei der Studienwahl haben?', 'Renommee darf ein Faktor sein, aber nicht allein entscheiden; in manchen Branchen ist es wichtig, die persönliche Passung des Studiengangs bleibt jedoch zentral.'),
('Welche Vorteile können bekannte Hochschulen beim Studium und Berufseinstieg bieten?', 'Sie verfügen oft über Netzwerke, Spezialangebote und starke Forschung; ihr Name kann bei Bewerbungen erste Aufmerksamkeit erzeugen.'),
('Warum lässt sich aus einer Hochschulrangliste nicht auf gute Betreuung schließen?', 'Größe und Ruf zeigen die konkrete Betreuungsqualität nicht zuverlässig; kleinere Hochschulen können persönlicher und praxisnäher arbeiten.')]
}
assert set(EDIT)==set(range(11,31))
base=json.loads(BASE.read_text(encoding='utf8'));out=copy.deepcopy(base)
assert len(out['items'])==68
changes=[]
for n,triples in EDIT.items():
 item=out['items'][n-1];prev=base['items'][n-1]
 assert item['id']==f'LES-PRES-{n:03d}'
 assert len(item['questions'])==5
 sections={s['id']:s for s in item['reading']['sections']}
 for i,(prompt,answer) in enumerate(triples):
  old=item['questions'][i]
  assert old['id']==f'q{i+1:02d}'
  assert old['evidence_section_ids']==(['p01','p06'] if i==0 else ['p02'] if i==1 else ['p03']),(n,old)
  assert old['type']==['global','detail','argumentation'][i]
  assert prompt.endswith('?') and len(prompt)>45 and len(answer)>85,(n,i,prompt,answer)
  oldprompt,oldanswer=old['prompt_de'],old['answer_de']
  old['prompt_de']=prompt;old['answer_de']=answer
  changes.append({'unit_id':item['id'],'question_id':old['id'],'evidence_section_ids':old['evidence_section_ids'],'before':{'prompt_de':oldprompt,'answer_de':oldanswer},'after':{'prompt_de':prompt,'answer_de':answer},'evidence_de':{'p01':sections['p01']['text'] if i==0 else None,'p06':sections['p06']['text'] if i==0 else None,'p02':sections['p02']['text'] if i==1 else None,'p03':sections['p03']['text'] if i==2 else None},'review':'AI_EDITORIAL_SOURCE_SCOPED__NOT_INDEPENDENT_STAGE4'})
  assert prev['questions'][i]['prompt_de']!=prompt
 for j in [3,4]:assert prev['questions'][j]==item['questions'][j]
 assert item['reading']==prev['reading'] and item['grammar']==prev['grammar']
assert len(changes)==60
all_prompts=[[item['questions'][i]['prompt_de'] for item in out['items']] for i in range(4)]
metrics={'q01':len(set(all_prompts[0])),'q02':len(set(all_prompts[1])),'q03':len(set(all_prompts[2])),'q04':len(set(all_prompts[3]))}
assert metrics=={'q01':31,'q02':34,'q03':33,'q04':68},metrics
out['content_version']='1.3.0-R6-Q123-20UNIT-CANDIDATE'
out['status']='EDITORIAL_CANDIDATE__QUESTION_SCOPE__STAGE4_6_7_HOLD'
out['qa_summary']=copy.deepcopy(base['qa_summary']);out['qa_summary']['editorial_r6']={'date':'2026-11-07','changed_units':20,'changed_prompts':60,'changed_answers':60,'scope':'LES-PRES-011..030 q01..q03 only','not_full_semantic_stage4':True,'original_r5_master_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest()}
# Only intentional changed top-level fields: content_version, status, qa_summary, items (questions of 20 units).
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
receipt={'schema':'lesen-r6-20unit-60question-evidence@1','date':'2026-11-07','current_working_parent_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'r6_candidate_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'changed_units':list(f'LES-PRES-{i:03d}' for i in range(11,31)),'q01_q02_q03_updated_each':20,'total_prompt_answer_pairs_changed':60,'unique_question_prompts_after':metrics,'changed':changes,'evidence_status':'AI source-text review, independently verifiable anchors, not external human review or formal Stage4','remaining':'38 q01, 35 q02 and 36 q03 duplicate instances by prior group; generic p04 passages remain'}
(ROOT/'LESEN-R6-60Q-SEMANTIC-EVIDENCE-20261107.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in receipt.items() if k!='changed'},ensure_ascii=False,indent=2))