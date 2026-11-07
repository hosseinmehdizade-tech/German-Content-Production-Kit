#!/usr/bin/env python3
"""Scoped, source-grounded Lesen R8 questions 051..068, parent R7 immutable."""
import hashlib,json,copy,pathlib,collections
P=pathlib.Path('/mnt/data/lesen_r8_20261107')
SRC=pathlib.Path('/mnt/data/lesen_r7_20261107/Lesen-Production-Master-v1.3.0-R7-20UNIT-Q123-CANDIDATE.json')
OUT=P/'Lesen-Production-Master-v1.3.0-R8-18UNIT-Q123-CANDIDATE.json'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
assert sha(SRC.read_bytes())=='f472a6260b29f7112bfdf71894f1004957ade61d8ec9bc842992f5a6e4c718d9'
# Each item: q01, q02, q03. None means preserve previous editorially accepted item.
# Ground each answer in its referenced p01/p06, p02, p03 respectively.
EDITS={
 51:[
 ("Welche einfache Erklärung für die männliche Dominanz in technischen Studiengängen hinterfragt der Text?", "Dass Männer und Frauen aus unterschiedlichen persönlichen Interessen verschiedene Studienfächer wählen. Der Text betont zusätzlich gesellschaftliche Prägung, Vorbilder und individuelle Erfahrungen."),
 None,None],
 52:[
 ("Warum stellt der Text die positiven Auswirkungen von KI auf Beruf und Alltag nicht als selbstverständlich dar?", "KI kann Arbeit erleichtern, bringt jedoch Risiken wie Fehler, Verzerrungen und Datenschutzprobleme mit sich. Ihre Wirkung hängt daher von der verantwortlichen Nutzung ab."),
 ("Welche Arbeiten kann KI erleichtern, und welche neuen Aufgaben bleiben dadurch für Menschen wichtig?", "Sie kann Routineaufgaben beschleunigen und Daten auswerten. Menschen gewinnen dadurch möglicherweise Zeit für kreative, soziale oder strategische Tätigkeiten."),
 ("Weshalb kann man automatisierte Entscheidungen laut Text nicht ungeprüft übernehmen?", "Automatisierte Systeme können fehlerhafte oder verzerrte Ergebnisse liefern. Hinzu kommen Datenschutzrisiken und Veränderungen am Arbeitsplatz; sie sind nicht automatisch neutral oder zuverlässig.")],
 53:[
 ("Warum lässt sich gute Bildung laut Text nicht auf messbare Prüfungsergebnisse reduzieren?", "Zu guter Bildung gehören neben Fachwissen auch Urteilsfähigkeit, Selbstständigkeit und gesellschaftliche Teilhabe. Messbare Leistungen erfassen davon nur einen Teil."),
 ("Welche Verbindung zwischen Fachwissen und überfachlichen Fähigkeiten beschreibt der Text als Bildungsziel?", "Solide Fachkenntnisse und grundlegende Kulturtechniken bleiben notwendig; zugleich sollen Lernende eigenständig urteilen, zusammenarbeiten und am gesellschaftlichen Leben teilnehmen können."),
 ("Welche Schwierigkeit entsteht, wenn Schulen zu viele Bildungsziele gleichzeitig verfolgen?", "Eine zu breite Zielsetzung kann Schulen überfordern, fachliche Standards schwächen und die begrenzte Unterrichtszeit auf zu viele Aufgaben verteilen.")],
 54:[
 ("Welches Verhältnis zwischen Zufall und eigener Vorbereitung beschreibt der Text für berufliche Karrieren?", "Unvorhergesehene Begegnungen und Gelegenheiten können neue Wege eröffnen. Wer vorbereitet und flexibel ist, kann solche Chancen besser erkennen und nutzen."),
 ("Welche ungeplanten Ereignisse können neue Karrierewege eröffnen, und welche Haltung hilft dabei?", "Unerwartete Begegnungen, Stellenangebote oder Informationen können Möglichkeiten schaffen. Neugier, Vorbereitung und Flexibilität helfen, daraus etwas zu machen."),
 ("Warum wäre es verkürzt, den Verlauf einer Karriere vor allem dem Zufall zuzuschreiben?", "Das würde eigene Entscheidungen, Ausdauer und erworbene Kompetenzen unterschätzen. Laut Text entstehen Karrieren aus Planung und unvorhersehbaren Ereignissen zusammen.")],
 55:[
 ("Warum unterscheidet der Text zwischen kurzfristiger Anspannung und dauerhaftem Lernstress?", "Kurzfristige Aktivierung kann die Aufmerksamkeit erhöhen. Langanhaltender Stress ohne Erholung beeinträchtigt dagegen Schlaf, Konzentration und Gedächtnis."),
 ("Welche Lernfunktionen leiden unter anhaltendem Stress, und was kann die Belastung begrenzen?", "Vor allem Konzentration, Schlaf und Gedächtnis können leiden. Realistische Zeitplanung und regelmäßige Pausen helfen, die Belastung zu regulieren."),
 ("Weshalb ist der Satz ‚Jeder Stress schadet beim Lernen‘ laut Text zu pauschal?", "Ein gewisses Maß an kurzfristiger Aktivierung kann Aufmerksamkeit und Leistungsbereitschaft steigern. Menschen reagieren außerdem unterschiedlich stark auf Druck.")],
 56:[
 ("Warum hält der Text öffentliche Bibliotheken trotz digitaler Informationsangebote weiterhin für wichtig?", "Digitale Angebote erleichtern die Recherche, ersetzen jedoch nicht öffentliche Lernräume, Beratung und den verlässlichen Zugang zu Wissen für alle."),
 ("Welche Vorteile digitaler Wissensangebote nennt der Text gegenüber ausschließlich gedruckten Beständen?", "E-Books, Datenbanken und Online-Archive sind ortsunabhängig zugänglich. Digitale Suchmöglichkeiten können außerdem schneller und aktueller sein."),
 ("Welche zwei Aufgaben von Bibliotheken würden bei einer rein digitalen Betrachtung übersehen?", "Bibliotheken bieten Lernräume und Beratung sowie verlässlichen Zugang zu Informationen. Diese Angebote sind gerade für Menschen ohne gute Arbeitsbedingungen oder teure Datenbanken wichtig.")],
 57:[
 ("Weshalb fordert der Text flexible Studienmodelle statt einer starren Trennung von Vollzeit und Teilzeit?", "Beruf, Kinderbetreuung oder Pflege führen zu unterschiedlichen Zeitbudgets, die sich auch ändern können. Studienmodelle sollten Wechsel ermöglichen und zugleich verlässliche Standards sichern."),
 ("Für welche Lebenssituationen sind Teilzeitmodelle besonders hilfreich, und was können angepasste Fristen bewirken?", "Sie erleichtern das Studium für Berufstätige, Eltern und pflegende Angehörige. Passende Fristen und Lehrformate können den Studienabbruch unwahrscheinlicher machen."),
 ("Welches Problem kann eine Vielzahl starrer Sonderregeln für Studierende und Verwaltung schaffen?", "Die Organisation wird komplizierter, und Studierende werden in feste Kategorien eingeteilt, obwohl sich ihre persönlichen Lebensumstände während des Studiums ändern können.")],
 58:[
 ("Warum bewertet der Text Internate nicht als grundsätzlich bessere Lernorte für alle Jugendlichen?", "Struktur und Gemeinschaft können helfen, doch Trennung von der Familie, sozialer Druck und wenig Privatsphäre können belasten. Entscheidend sind Persönlichkeit und Lebenssituation."),
 ("Wie können Internate sowohl das Lernen als auch die persönliche Entwicklung unterstützen?", "Feste Lernzeiten und Freizeitangebote geben Struktur. Die enge Gemeinschaft kann zugleich Selbstständigkeit und soziale Fähigkeiten fördern."),
 ("Welche Belastungen können sich aus dem Zusammenleben und der Entfernung zur Familie ergeben?", "Die Distanz zur Familie, ständiger sozialer Kontakt und begrenzte Privatsphäre können Druck erzeugen. Nicht für jeden Jugendlichen ist dieses Umfeld geeignet.")],
 59:[
 ("Welche verbreitete Annahme über die Eigenverantwortung im Fernstudium stellt der Text infrage?", "Dass Fernstudierende immer stärker auf sich allein gestellt seien. Auch im Präsenzstudium ist Selbstorganisation nötig; Betreuung und Lernstruktur hängen vom konkreten Programm ab."),
 None,None],
 60:[
 ("Warum ist eine private Freundschaft zwischen Lehrenden und Studierenden laut Text nicht nur Privatsache?", "Solange Lehrende Prüfungen bewerten, besteht ein Machtgefälle. Private Kontakte können Grenzen verwischen und bei anderen den Eindruck von Bevorzugung erwecken."),
 ("Welche Vorteile unterscheiden den informellen Kontakt von rein formeller Hochschulkommunikation?", "Ein informeller Austausch kann Hemmschwellen senken und Gespräche persönlicher machen. Fachliche Netzwerke erleichtern außerdem Kontakte für Projekte und berufliche Chancen."),
 ("Weshalb können private Profile und Prüfungssituationen zu einem Interessenkonflikt führen?", "Lehrende entscheiden über Bewertungen und stehen daher nicht auf derselben Ebene wie Studierende. Private Einblicke und unklare Grenzen können Druck oder den Verdacht unfairer Vorteile auslösen.")],
 61:[
 ("Wie begründet der Text, dass erfundene Fantasy-Welten einen Bildungswert haben können?", "Fiktive Welten machen Fragen nach Macht, Verantwortung und gesellschaftlichen Regeln sichtbar. Sie regen Fantasie, Perspektivwechsel und Vergleiche mit der Realität an."),
 ("Welche zwei Lernmöglichkeiten bieten Fantasy-Geschichten über reine Unterhaltung hinaus?", "Sie können moralische und gesellschaftliche Konflikte anschaulich machen. Außerdem fördern sie Vorstellungskraft, Lesemotivation und die Fähigkeit, fremde Perspektiven einzunehmen."),
 ("Warum darf man aus der Beliebtheit einer Fantasy-Geschichte nicht direkt auf ihren Lernwert schließen?", "Unterhaltung garantiert weder fachliche Richtigkeit noch pädagogische Qualität. Lernwirkung entsteht erst, wenn Inhalte aufmerksam betrachtet und reflektiert werden.")],
 62:[
 ("Welches Spannungsverhältnis beschreibt der Text zwischen öffentlicher Kulturförderung und staatlichem Einfluss?", "Förderung ermöglicht auch wenig rentable Kunst und kulturelle Teilhabe. Zugleich muss gerecht und transparent entschieden werden, welche Projekte Geld erhalten, ohne politische Einflussnahme zu verstärken."),
 ("Warum könnten bestimmte Kulturangebote ohne öffentliche Förderung verschwinden?", "Nicht alle Museen, Theater oder experimentellen Projekte erzielen genug Markteinnahmen. Öffentliche Mittel können solche Angebote sowie kulturelle Vielfalt und Teilhabe erhalten."),
 ("Welche zwei Probleme ergeben sich daraus, dass der Staat über Kulturförderung entscheidet?", "Förderung kostet begrenzte öffentliche Mittel. Außerdem ist umstritten, nach welchen Kriterien Projekte ausgewählt werden und wie politische Einflussnahme vermieden werden kann.")],
 63:[
 ("Warum kann eine Übersetzung nach Ansicht des Textes nicht immer gleichzeitig Stil und Inhalt vollständig bewahren?", "Zwischen Sprachen gibt es selten perfekte Entsprechungen. Wortspiele, Ton und kulturelle Bezüge lassen sich nicht stets gemeinsam mit der inhaltlichen Bedeutung erhalten."),
 ("Welche Priorität hat eine Übersetzung von Sachtexten gegenüber der möglichst genauen Nachbildung des Stils?", "Sie muss verständlich und inhaltlich zuverlässig sein. Gerade bei Sachtexten kann Genauigkeit wichtiger sein als das Nachahmen sprachlicher Besonderheiten."),
 ("Weshalb kann eine ausschließlich auf Informationen konzentrierte Übersetzung literarische Texte verfälschen?", "In Literatur tragen Rhythmus, Ton, Wortwahl und Mehrdeutigkeit zur Wirkung bei. Werden diese Merkmale ignoriert, kann sich die Bedeutung des Originals verändern.")],
 64:[
 ("Wie unterscheidet der Text den Nutzen von Sympathie von der fachlichen Qualität des Unterrichts?", "Sympathie erleichtert Vertrauen, Fragen und Rückmeldungen. Sie garantiert jedoch keine guten Erklärungen; fachliche Standards und professionelles Verhalten bleiben entscheidend."),
 ("Warum können positive Beziehungen zu Lehrenden die aktive Mitarbeit verbessern?", "Wer einer Lehrperson vertraut, hört aufmerksamer zu, stellt eher Fragen und nimmt konstruktive Rückmeldungen leichter an."),
 ("Welche Gefahr sieht der Text darin, eine sympathische Lehrperson automatisch für fachlich gut zu halten?", "Sympathie ist subjektiv und kann zu unkritischem Urteil führen. Eine beliebte Lehrperson vermittelt nicht zwangsläufig bessere Fachinhalte.")],
 65:[
 ("Warum stellt der Text gemeinsames Vorlesen nicht als Gegensatz zum selbstständigen Lesen dar?", "Vorlesen erweitert Wortschatz und Gesprächsmöglichkeiten. Auch selbst lesende Kinder können so gemeinsam schwierigere Texte entdecken und werden auf eigenständiges Lesen vorbereitet."),
 ("Wie unterstützt regelmäßiges Vorlesen gleichzeitig Sprache und Beziehung zwischen Kind und Erwachsenen?", "Kinder begegnen Wortschatz und Erzählmustern im Zusammenhang. Gemeinsame Gespräche über Figuren, Gefühle und Erlebnisse schaffen zudem Nähe."),
 ("Weshalb reicht Vorlesen allein nach Ansicht des Textes nicht für eine sichere spätere Lesekompetenz aus?", "Kinder entwickeln Sprache durch viele Formen der Interaktion. Vorlesen kann dabei helfen, garantiert aber nicht allein späteres Lesen; auch andere Medien können sinnvolle Impulse geben.")],
 66:[
 ("Wo zieht der Text die Grenze zwischen sinnvoller Elternbeteiligung und Einmischung in den Unterricht?", "Eltern dürfen informieren, Fragen stellen und Probleme ansprechen. Methoden und einzelne Bewertungen sollten jedoch zunächst professionell von Lehrkräften entschieden werden."),
 ("Welche Informationen können Eltern der Schule geben, und wie hilft eine regelmäßige Zusammenarbeit?", "Eltern kennen Bedürfnisse und Schwierigkeiten ihres Kindes. Ein kontinuierlicher Austausch schafft Vertrauen und kann Probleme früh sichtbar machen."),
 ("Warum können direkte Eingriffe von Eltern in Methoden und Noten problematisch sein?", "Sie schwächen die professionelle Rolle der Lehrkräfte. Außerdem sehen Eltern den Unterricht häufig nur aus der Perspektive ihres eigenen Kindes.")],
 67:[
 ("Welche Form früher Medienbildung befürwortet der Text statt eines möglichst frühen Dauerkonsums?", "Kurze, altersgerechte und begleitete Mediennutzung, bei der Erwachsene mit Kindern über Inhalte sprechen und Regeln vereinbaren. Spiel und direkte Erfahrungen bleiben wichtig."),
 ("Wie können Erwachsene Vorschulkinder zu einer bewussten statt passiven Mediennutzung anleiten?", "Sie können Geräte gemeinsam kreativ einsetzen und früh Regeln für Inhalte und Pausen einüben, bevor sich ungünstige Gewohnheiten festigen."),
 ("Welche Entwicklungserfahrungen könnten durch zu lange Bildschirmzeiten verdrängt werden?", "Vor allem Bewegung, Schlaf, freies Spiel und direkte soziale Kontakte. Kleine Kinder brauchen reale Erlebnisse und persönliche Interaktion besonders stark." )],
 68:[
 ("Warum bevorzugt der Text freiwillige Elternbildung gegenüber einer staatlichen Pflichtlizenz?", "Kostenlose Kurse und Beratung können Eltern vorbereiten, ohne das Recht auf Elternschaft von einer Prüfung abhängig zu machen. Eine Pflichtlizenz würde zu stark in persönliche Freiheiten eingreifen."),
 ("Welche zwei konkreten Formen von Unterstützung könnten Kurse für angehende Eltern bieten?", "Sie vermitteln Wissen zu Entwicklung, Gesundheit und Sicherheit. Frühzeitige Beratung kann Unsicherheiten verringern und auf typische familiäre Belastungen vorbereiten."),
 ("Warum lässt sich eine verpflichtende staatliche Zulassung zur Elternschaft schwer rechtfertigen?", "Sie greift tief in persönliche Freiheitsrechte ein und wäre kaum fair zu kontrollieren. Elternschaft ist nicht mit einer beruflichen Zulassung gleichzusetzen.")]
}
assert set(EDITS)==set(range(51,69))
a=json.loads(SRC.read_text());b=copy.deepcopy(a)
ledger=[];prompt_changes=answer_changes=0;modified_units=[];preserved=[]
for n in range(51,69):
 item=b['items'][n-1];old=a['items'][n-1];assert item['id']==f'LES-PRES-{n:03d}'
 changed=False
 for qi,edit in enumerate(EDITS[n]):
  oldq=old['questions'][qi];newq=item['questions'][qi]
  if edit is None:
   assert n in [51,59] and qi in [1,2]
   assert oldq['prompt_de'] not in ["Welche zwei Argumente sprechen im Text für eine positive Bewertung?","Welches Gegenargument wird genannt?"]
   preserved.append([n,qi+1]);continue
  prompt,answer=edit
  assert prompt.endswith('?') and len(prompt)>50 and len(answer)>65
  assert (prompt,answer)!=(oldq['prompt_de'],oldq['answer_de'])
  assert len(newq['evidence_section_ids'])>0
  secid=newq['evidence_section_ids'][0]
  sec=next(s for s in item['reading']['sections'] if s['id']==secid)
  ledger.append({'unit_id':item['id'],'title_de':item['title_de'],'question_id':newq['id'],'evidence_section_ids':newq['evidence_section_ids'],'source_section_de':sec['text'],'old_prompt_de':oldq['prompt_de'],'new_prompt_de':prompt,'old_answer_de':oldq['answer_de'],'new_answer_de':answer,'review_type':'EDITORIAL_SOURCE_GROUNDED__NOT_INDEPENDENT_STAGE4'})
  prompt_changes+=oldq['prompt_de']!=prompt;answer_changes+=oldq['answer_de']!=answer
  newq['prompt_de']=prompt;newq['answer_de']=answer;changed=True
 if changed: modified_units.append(item['id'])
assert prompt_changes==answer_changes==50,(prompt_changes,answer_changes)
assert len(ledger)==50 and len(modified_units)==18 and len(preserved)==4
b['content_version']='1.3.0-R8-Q123-051-068-CANDIDATE'
b['status']='EDITORIAL_CANDIDATE_NOT_CURATED_CURRENT_NOT_STAGE4_6_7'
b['qa_summary']={'scope':'051..068 q01..q03 only; existing q02/q03 in lessons 051/059 preserved','source_master_parent_sha256':sha(SRC.read_bytes()),'reviewed_units':18,'question_prompt_changes':50,'question_answer_changes':50,'preserved_approved_questions':preserved,'passages_translations_grammar_unchanged':True,'formal_semantic_stage4':'HOLD','browser_stage6':'NOT_RUN','release_stage7':'NOT_FINAL'}
OUT.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
(P/'LESEN-R8-50Q-SOURCE-EVIDENCE.json').write_text(json.dumps({'schema':'lesen-r8-source-bound-question-evidence@1.0.0','baseline_master_sha256':sha(SRC.read_bytes()),'candidate_master_sha256':sha(OUT.read_bytes()),'changes':ledger,'preserved_approved_questions':preserved,'scope':'50 Q/A pairs 051–068; source text recorded for each','note':'AI editorial grounding is not independent semantic Stage4 certification.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'master_sha256':sha(OUT.read_bytes()),'bytes':OUT.stat().st_size,'modified_units':modified_units,'prompts':prompt_changes,'answers':answer_changes,'preserved':preserved,'unique_first_four':[len({u['questions'][i]['prompt_de'] for u in b['items']}) for i in range(4)]},ensure_ascii=False,indent=2))