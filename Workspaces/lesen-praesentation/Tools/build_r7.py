#!/usr/bin/env python3
"""Lesen R7: human-authored, passage-anchored questions 1–3 in lessons 031–050.
Preserve old manually repaired questions from lesson 035; question-only successor, no Stage4 claim.
"""
from pathlib import Path
import json,hashlib,copy,collections
ROOT=Path('/mnt/data/lesen_r7_20261107')
PARENT=Path('/mnt/data/lesen_r6_20261107/Lesen-Production-Master-v1.3.0-R6-20UNIT-Q123-CANDIDATE.json')
OUT=ROOT/'Lesen-Production-Master-v1.3.0-R7-20UNIT-Q123-CANDIDATE.json'
DELTA=ROOT/'LESEN-R7-20UNIT-QUESTION-EVIDENCE.json'
EXPECTED_SHA='3a727fc2575b5c041808803b6a97d2a77239aa3089f6bf88570c39e959d26f5c'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(PARENT.read_bytes())==EXPECTED_SHA
parent=json.loads(PARENT.read_text(encoding='utf-8'));result=copy.deepcopy(parent)
# Each entry is (question DE, model answer DE), source evidence for q01/p01+p06,
# q02/p02, q03/p03 unchanged in the historic contract.
changes={
31:[
('Wie bewertet der Text den Einsatz von Smartphones als Lernmedien?', 'Smartphones können Lernen durch viele sofort verfügbare Funktionen unterstützen. Ohne klare Einsatzregeln lenken dieselben Geräte aber leicht ab; deshalb wird ihr gezielter Einsatz statt dauernder Nutzung befürwortet.'),
('Welche beiden Lernmöglichkeiten eröffnen Smartphones im Unterricht?', 'Lernapps, Wörterbücher, Kameras und Recherchen stehen spontan bereit. Außerdem lernen Schülerinnen und Schüler, ihr Alltagsgerät aktiv und produktiv für Aufgaben zu nutzen.'),
('Warum kann dieselbe Vielseitigkeit von Smartphones den Unterricht stören?', 'Benachrichtigungen, soziale Medien und Spiele beanspruchen Aufmerksamkeit. Da Smartphones auf häufige Nutzung ausgelegt sind, kann ein Wechsel zur Unterhaltung die Konzentration unterbrechen.')],
32:[
('Wo zieht der Text die Grenze zwischen nützlicher Robotik und dem Ersatz menschlicher Beziehungen?', 'Roboter sind vor allem bei gefährlichen, anstrengenden oder eintönigen Aufgaben hilfreich. Sie sollen Menschen unterstützen, in Pflege und Betreuung aber persönliche Zuwendung nicht ersetzen.'),
('Bei welchen zwei Aufgabenfeldern wird ein Vorteil von Robotern genannt?', 'Sie können gefährliche, monotone oder körperlich belastende Arbeit übernehmen. Assistenzsysteme können zudem ältere oder körperlich eingeschränkte Menschen im Alltag unterstützen.'),
('Welche Probleme wirft die Automatisierung hinsichtlich Arbeit und Verantwortung auf?', 'Roboter verändern Beschäftigung und können Abhängigkeiten schaffen. Bei Fehlern autonomer Systeme ist die Verantwortung möglicherweise unklar, und Maschinen verstehen menschliche Bedürfnisse nicht automatisch.')],
33:[
('Warum betrachtet der Text Musikunterricht als Teil einer breiten Schulbildung?', 'Musikunterricht schult nicht nur instrumentale Fertigkeiten, sondern gemeinsames Zuhören, Kreativität und kulturelle Ausdrucksfähigkeit. Sein Stellenwert hängt dennoch von den verfügbaren Ressourcen ab.'),
('Welche sozialen und kreativen Kompetenzen kann gemeinsames Musizieren stärken?', 'Das Musizieren verlangt Konzentration, Zuhören und Zusammenarbeit. Zugleich lernen Kinder kulturelle Ausdrucksformen kennen und entwickeln kreative Fähigkeiten.'),
('Welche zwei Schwierigkeiten können den Musikunterricht an Schulen begrenzen?', 'Die Stundenpläne sind bereits voll, und nicht alle Schülerinnen und Schüler interessieren sich gleichermaßen für Musik. Instrumente, Räume und qualifizierte Lehrkräfte benötigen zusätzliche Mittel.')],
34:[
('Unter welchen Bedingungen können soziale Medien eine berufliche Laufbahn unterstützen?', 'Fachliche Netzwerke und ein gezielt gepflegtes berufliches Profil können Kontakte und Sichtbarkeit fördern. Der Text betont aber, dass echte Kompetenz und Berufserfahrung wichtiger bleiben als ständige Online-Präsenz.'),
('Wie helfen digitale Netzwerke bei Stellensuche und beruflicher Sichtbarkeit?', 'Fachliche Netzwerke erleichtern den Zugang zu Stellenangeboten, Kontakten und Lerninhalten. Ein professionelles Profil kann außerdem dazu beitragen, von Arbeitgebern wahrgenommen zu werden.'),
('Warum kann die Vermischung von privater und beruflicher Online-Präsenz problematisch werden?', 'Dauernde Selbstdarstellung erzeugt Druck, und persönliche Beiträge können beruflich anders interpretiert werden. Weil Online-Informationen lange abrufbar bleiben, verschwimmen private und berufliche Grenzen.')],
35:[
('Welchen Maßstab legt der Text an den Einsatz elektronischer Geräte in Schulen an?', 'Laptops und Tablets sollten eine konkrete Lernhandlung verbessern und nicht Selbstzweck sein. Entscheidend sind faire Zugangsbedingungen, verlässliche Technik und didaktisch sinnvolle Aufgaben.'),
None,
None],
36:[
('Welches Ziel soll Ernährungsbildung in der Schule erreichen, ohne Kinder zu bevormunden?', 'Kinder sollen Werbung, Zutaten und Nährwerte selbstständig beurteilen können. Die Schule soll Handlungskompetenz vermitteln, nicht Familiengewohnheiten kontrollieren oder einzelne Kinder beschämen.'),
('Welche zwei konkreten Beiträge kann Schule zu bewusster Ernährung leisten?', 'Im Unterricht können Kinder Lebensmittelwerbung und Nährwertinformationen kritisch beurteilen lernen. Schulessen und praktische Projekte wie gemeinsames Kochen erleichtern die Umsetzung im Alltag.'),
('Warum warnt der Text vor moralischem Druck beim Thema Ernährung?', 'Ernährung hängt von Kultur, Geld und persönlichen Umständen ab. Wenn die Schule Lebensmittel pauschal bewertet oder Familiengewohnheiten kontrollieren will, können Kinder beschämt und Unterschiede verstärkt werden.')],
37:[
('Warum brauchen auch Hochschullehrende pädagogische Kompetenzen?', 'Fachwissen allein ermöglicht noch keine verständliche Lehre. Auch Erwachsene profitieren von klaren Lernzielen, Beispielen und Feedback; gleichzeitig müssen Hochschulen Selbstständigkeit und wissenschaftliche Tiefe bewahren.'),
('Welche didaktischen Mittel unterstützen Studierende besonders?', 'Eine klare Struktur, verständliche Erklärungen und konstruktives Feedback helfen beim Lernen. Gute Lehre fördert zudem Selbstständigkeit, ohne Studierende mit Schwierigkeiten allein zu lassen.'),
('Welche Besonderheiten der Hochschule erschweren eine Übertragung schulischer Lehrmethoden?', 'Studierende sollen mehr Eigenverantwortung tragen. Zugleich muss Hochschullehre Forschung, fachliche Vertiefung und oft große Gruppen berücksichtigen, statt einfach die Schule zu imitieren.')],
38:[
('Unter welcher Voraussetzung lassen sich mehr Studienplätze und gute Lehre vereinbaren?', 'Ein breiter Hochschulzugang muss von ausreichend Personal, Räumen, Betreuung und Infrastruktur begleitet werden. Steigende Studierendenzahlen allein führen nicht zwangsläufig zu schlechterer Bildung.'),
('Welche Chancen nennt der Text für einen breiteren Hochschulzugang?', 'Mehr Menschen erhalten die Möglichkeit zu einem akademischen Abschluss. Größere und vielfältigere Studierendengruppen können außerdem neue Perspektiven an Hochschulen einbringen.'),
('Warum können wachsende Studierendenzahlen die Lehrqualität verschlechtern?', 'Seminare und Vorlesungen können überfüllt werden, wenn Räume, Lehrkräfte und Beratung nicht mitwachsen. Ohne zusätzliche Ressourcen leiden Betreuung und Lernbedingungen.')],
39:[
('Warum lehnt der Text einen einheitlichen Wohnkostenbeitrag junger Erwachsener ab?', 'Ein Beitrag sollte sich nach Einkommen und Lebenssituation richten. Wer schon voll verdient, kann anders beitragen als jemand in Ausbildung; Geld darf nicht zum Druckmittel werden.'),
('Welche Vorteile kann ein angemessener Beitrag zum Familienhaushalt haben?', 'Junge Erwachsene lernen, reale Wohnkosten und finanzielle Verantwortung zu berücksichtigen. Wenn sie eigenes Einkommen haben, können sie damit zugleich ihre Eltern entlasten.'),
('Weshalb können pauschale Zahlungsverpflichtungen für junge Erwachsene ungerecht sein?', 'Studierende und Auszubildende verfügen häufig nur über wenig Geld. Familien haben unterschiedliche Voraussetzungen; hohe Forderungen können zudem verhindern, dass junge Menschen für einen Auszug sparen.')],
40:[
('Wie unterscheidet der Text fachliche Autorität von autoritärem Verhalten?', 'Fachliche Autorität entsteht durch Kompetenz, Fairness und Verlässlichkeit. Autoritäres Verhalten fordert dagegen Gehorsam aufgrund einer Machtposition; Lernende sollten trotzdem kritisch nachfragen dürfen.'),
('Wodurch können Lehrende im Unterricht berechtigte Autorität gewinnen?', 'Fachliche Kompetenz und klare Regeln geben Orientierung. Wer Lernprozesse verlässlich strukturiert und Konflikte fair moderiert, kann Respekt und Vertrauen aufbauen.'),
('Warum kann zu viel Autoritätsdenken an Hochschulen die Bildung gefährden?', 'Wenn Autorität als Macht oder Forderung nach Gehorsam verstanden wird, geraten Kritik und selbstständiges Denken in den Hintergrund. Gerade Hochschulen sollen jedoch Diskussion und Widerspruch ermöglichen.')],
41:[
('Wie verteilt der Text Verantwortung für die Pflege älterer Menschen?', 'Professionelle Versorgung und faire Mindeststandards dürfen nicht allein von Familien abhängen. Angehörige können Nähe bieten; deshalb wird ein öffentlich gesichertes Netz mit freiwilliger familiärer Unterstützung befürwortet.'),
('Warum spricht der Text für staatlich abgesicherte Pflegeangebote?', 'Professionelle Pflege soll unabhängig von Wohnort oder Vermögen zugänglich sein. Öffentliche Systeme können Mindeststandards, Finanzierung und gerechtere Versorgung sichern.'),
('Was kann der Staat bei der Pflege trotz professioneller Angebote nicht vollständig ersetzen?', 'Staatliche Systeme schaffen nicht automatisch persönliche Kontinuität oder emotionale Nähe. Individuelle Beziehungen und die Unterstützung von Angehörigen bleiben deshalb wichtig.')],
42:[
('Weshalb ist Arbeiten im Ausland mehr als ein Karriereschritt?', 'Der Text betrachtet internationale Arbeit als sprachliche, kulturelle und persönliche Lernerfahrung. Gegen die Chancen müssen aber Verträge, Lebenshaltungskosten und die Trennung von Familie oder Freunden abgewogen werden.'),
('Welche beruflichen und persönlichen Fähigkeiten kann Auslandserfahrung fördern?', 'Beschäftigte lernen neue Arbeitskulturen, Sprachen und Lösungswege kennen. Sie erweitern außerdem ihre Flexibilität sowie berufliche Kontakte und Netzwerke.'),
('Warum ist ein Jobangebot im Ausland nicht automatisch ein Fortschritt?', 'Umzug und Bürokratie, Distanz zur Familie und unsichere Arbeitsbedingungen können stark belasten. Ein höheres Gehalt oder Auslandsaufenthalt garantiert noch keinen beruflichen Erfolg.')],
43:[
('Was versteht der Text unter fairer Teilhabe von Studierenden mit Behinderung?', 'Teilhabe setzt barrierefreie Räume, zugängliche digitale Materialien und flexible Organisation voraus. Nachteilsausgleiche sollen gleiche Möglichkeiten schaffen, fachliche Leistung zu zeigen, nicht Anforderungen beliebig senken.'),
('Welche Barrieren können durch Beratung und flexible Studienbedingungen verringert werden?', 'Barrierefreie Räume, zugängliche digitale Unterlagen und angepasste Prüfungen erleichtern die Teilnahme. Frühzeitige Beratung kann zusätzliche organisatorische Hindernisse verhindern.'),
('Warum reichen standardisierte Lösungen für die Inklusion an Hochschulen nicht immer aus?', 'Die Umsetzung von Inklusion erfordert Ressourcen, sorgfältige Planung und individuelle Lösungen. Nicht jede Barriere lässt sich sofort beseitigen; Standardlösungen reichen wegen unterschiedlicher Bedürfnisse nicht immer aus.')],
44:[
('Warum hält der Text eine Mischung aus Grundsicherung und ergänzender Altersvorsorge für sinnvoll?', 'Staatliche Sicherung soll das Existenzminimum im Alter schützen; ergänzende Vorsorge kann helfen, weitere Wünsche abzudecken. Da Einkommen und Erwerbswege stark variieren, reicht eine rein private Lösung nicht für alle.'),
('Welche zwei sozialen Vorteile hat ein gemeinschaftlich finanziertes Rentensystem?', 'Ein öffentliches System kann auch Menschen mit niedrigem Einkommen grundlegende Sicherheit geben. Durch gemeinsame Beiträge lassen sich soziale Risiken auf viele Schultern verteilen.'),
('Welche langfristigen Probleme belasten staatliche Systeme der Altersvorsorge?', 'Demografischer Wandel und unterbrochene Erwerbsbiografien erhöhen den Finanzierungsdruck. Beiträge lassen sich nicht unbegrenzt steigern, ohne neue Belastungen zu erzeugen.')],
45:[
('Warum erklärt der Text beruflichen Erfolg weder allein durch Fleiß noch allein durch Zufall?', 'Menschen beeinflussen ihren Weg durch Motivation und Entscheidungen. Gleichzeitig hängen Chancen von Herkunft, Gesundheit, Bildungskontakten und wirtschaftlichen Voraussetzungen ab.'),
('Welche persönlichen und sozialen Faktoren können einen Bildungsweg positiv beeinflussen?', 'Motivation, Ausdauer und Entscheidungen prägen die eigene Entwicklung. Mentorinnen und Mentoren, Familie und geeignete Lerngelegenheiten können weitere Türen öffnen.'),
('Warum ist es problematisch, Erfolg nur als persönliche Leistung zu betrachten?', 'Herkunft, gesundheitliche Voraussetzungen, finanzielle Bedingungen und Zufall verteilen Chancen ungleich. Nicht alle Menschen beginnen mit denselben Möglichkeiten oder Unterstützungsangeboten.')],
46:[
('Was macht künstlerische Fächer nach dem Text zu mehr als einer Erholungspause?', 'Kunst, Theater, Tanz und Musik trainieren kreative Entscheidungen und Ausdruck. Die Fächer brauchen ernsthafte Aufgaben und Übung, sollen aber nicht nur nach technischer Perfektion bewertet werden.'),
('Welche Fähigkeiten fördern künstlerische Projekte neben reiner Gestaltung?', 'Sie stärken Ausdrucksfähigkeit, Kreativität und Selbstvertrauen. Gemeinsame Projekte können außerdem Kooperation und kulturelle Teilhabe ermöglichen.'),
('Warum konkurrieren künstlerische Fächer mit anderen Unterrichtszielen?', 'Schulstunden sind begrenzt, während auch Kernfächer genügend Raum benötigen. Künstlerische Angebote brauchen teilweise besondere Räume, Material und spezialisierte Lehrkräfte.')],
47:[
('Warum weist der Text eine Rangliste zwischen Natur- und Geisteswissenschaften zurück?', 'Naturwissenschaften liefern Modelle und technische Lösungen; Geisteswissenschaften helfen, Werte und gesellschaftliche Folgen zu beurteilen. Große Probleme wie Klimawandel brauchen beide Blickwinkel.'),
('Welche unterschiedlichen Aufgaben erfüllen beide Wissenschaftsbereiche laut Text?', 'Naturwissenschaften entwickeln technische, medizinische und ökologische Erkenntnisse. Geisteswissenschaften untersuchen Sprache, Geschichte, Werte und gesellschaftliche Konflikte.'),
('Welche Gefahr sieht der Text in der Gegenüberstellung der Wissenschaftsbereiche?', 'Eine starre Rangordnung spielt verschiedene Methoden und Aufgaben künstlich gegeneinander aus. Komplexe Fragen verlangen aber Faktenwissen ebenso wie ethische und historische Orientierung.')],
48:[
('Welche Unterscheidung ist dem Text bei alternativen Heilmethoden besonders wichtig?', 'Subjektives Wohlbefinden ist nicht dasselbe wie wissenschaftlich nachgewiesene Wirksamkeit. Ergänzende Verfahren dürfen notwendige Diagnose und wirksame Behandlung nicht verzögern oder ersetzen.'),
('Warum fühlen sich manche Patientinnen und Patienten von ergänzenden Verfahren angesprochen?', 'Ausführliche Gespräche und ein ganzheitlicher Blick werden als hilfreich erlebt. Bestimmte Verfahren können subjektives Wohlbefinden und die Bereitschaft zur Therapie unterstützen, ohne Wirksamkeit gegen Krankheiten zu belegen.'),
('Welche gesundheitlichen Risiken können bei unzureichend geprüften Heilmethoden entstehen?', 'Für viele Verfahren fehlen belastbare Belege zu Wirksamkeit und Sicherheit. Besonders gefährlich wird es, wenn dadurch medizinisch notwendige Untersuchungen oder Therapien verschoben werden.')],
49:[
('Wie soll soziales Engagement Jugendlicher gefördert werden, ohne Freiwilligkeit aufzugeben?', 'Schulen und Gemeinden sollten vielfältige, leicht zugängliche Angebote vorstellen und begleiten. Eine generelle Pflicht könnte Motivation und Freiwilligkeit schwächen, besonders bei Jugendlichen mit wenig freier Zeit.'),
('Welche Lernchancen bietet freiwilliges Engagement außerhalb der Schule?', 'Jugendliche üben Verantwortung und Empathie und sammeln praktische Erfahrungen. Dabei lernen sie andere Menschen und Lebenssituationen außerhalb ihres vertrauten Umfelds kennen.'),
('Weshalb kann verpflichtendes Engagement Jugendlichen schaden?', 'Ein Zwangsdienst verliert den freiwilligen Charakter und erzeugt Zeitdruck. Junge Menschen haben wegen Schule, Ausbildung oder familiärer Aufgaben unterschiedlich viel freie Zeit.')],
50:[
('Woran sollte sich der weltweite Einfluss einer Person messen lassen?', 'Entscheidend sind Reichweite, Dauer und reale Folgen von Entscheidungen oder Ideen. Öffentliche Bekanntheit und Followerzahlen allein zeigen weder langfristige Wirkung noch verantwortliches Handeln.'),
('Welche unterschiedlichen Personengruppen können internationale Entwicklungen prägen?', 'Politische oder wirtschaftliche Entscheidungsträger beeinflussen Gesetze und Ressourcen direkt. Auch Forschende, Unternehmer, Kunstschaffende und Aktivisten können Debatten und Veränderungen auslösen.'),
('Warum ist große Online-Bekanntheit kein zuverlässiger Beleg für nachhaltigen Einfluss?', 'Soziale Medien erzeugen oft kurzfristige Aufmerksamkeit, die sich nicht in dauerhafte Veränderungen übersetzt. Prominenz sagt auch nichts darüber aus, ob die Wirkung einer Person positiv ist.')]
}
assert set(changes)==set(range(31,51))
ledger=[]
for i in range(31,51):
 item=result['items'][i-1];old=parent['items'][i-1]
 assert item['id']==f'LES-PRES-{i:03d}'
 assert set(item)==set(old)
 for j,entry in enumerate(changes[i]):
  if entry is None:
   assert i==35 and j in (1,2)
   ledger.append({'unit_id':item['id'],'question_id':f'q0{j+1}','action':'PRESERVED_ALREADY_CUSTOM_REVIEWED','before':old['questions'][j]})
   continue
  prompt,answer=entry
  q=item['questions'][j];o=old['questions'][j]
  assert o['id']==f'q0{j+1}'
  assert prompt.endswith('?') and len(prompt)>50 and len(answer)>60
  assert prompt!=o['prompt_de']
  q['prompt_de']=prompt
  if not (i==43 and j==2):q['answer_de']=answer
  else:assert answer==o['answer_de'],'Pre-reviewed answer must remain byte identical'
  ledger.append({'unit_id':item['id'],'title_de':item['title_de'],'question_id':q['id'],'action':'PROMPT_ONLY_PREVIOUS_ACCEPTED_ANSWER_PRESERVED' if i==43 and j==2 else 'PROMPT_AND_ANSWER_CHANGED','evidence_section_ids':q['evidence_section_ids'],'source_excerpt':(old['reading']['sections'][0 if j==0 else 1 if j==1 else 2]['text'])[:430],'before':{'prompt_de':o['prompt_de'],'answer_de':o['answer_de']},'after':{'prompt_de':q['prompt_de'],'answer_de':q['answer_de']}})
result['content_version']='1.3.0-R7-Q123-031-050-CANDIDATE'
result['status']='EDITORIAL_CANDIDATE_NOT_CURATED_CURRENT_NOT_STAGE4_6_7'
result['qa_summary']={'scope':'031..050 q01..q03 only; 035 q02/03 previously reviewed retained; 043 q03 answer retained','source_master_parent_sha256':sha(PARENT.read_bytes()),'reviewed_units':20,'changed_question_prompt_count':58,'changed_answer_count':57,'untouched_fulltext_and_translations':True,'formal_semantic_stage4':'HOLD','native_browser_stage6':'NOT_RUN','release_stage7':'NOT_FINAL'}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
DELTA.write_text(json.dumps({'schema':'lesen-r7-question-delta-evidence@1.0.0','baseline_sha256':sha(PARENT.read_bytes()),'current_master_sha256':sha(OUT.read_bytes()),'changes':ledger,'scope_warning':'AI editorial evidence based on current curated passage; NOT independent semantic Stage4; cited source excerpts are partial, consult full unchanged passage for QA.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'candidate_master_sha256':sha(OUT.read_bytes()),'candidate_master_bytes':OUT.stat().st_size,'ledger_count':len(ledger),'changed_prompts':sum(z['action']!='PRESERVED_ALREADY_CUSTOM_REVIEWED' for z in ledger),'preserved':sum(z['action']=='PRESERVED_ALREADY_CUSTOM_REVIEWED' for z in ledger),'changed_answers':sum(z['action']=='PROMPT_AND_ANSWER_CHANGED' for z in ledger)},indent=2))