#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'Workspaces/menschen-a2/tools';sys.path.insert(0,str(TOOLS))
spec=importlib.util.spec_from_file_location('v7',TOOLS/'enrich_rich_card_v7.py');v7=importlib.util.module_from_spec(spec);spec.loader.exec_module(v7)

assert v7.v5.lookup_lemma('bestehen aus (Dat.)')=='bestehen'
assert v7.v5.lookup_lemma('auf etw. (Dat.) bestehen')=='bestehen'
assert v7.v5.lookup_lemma('sich an jdn. kuscheln')=='kuscheln'
assert v7.v5.contains_anchor('Er besteht darauf, dass wir warten.','auf')
assert v7.v5.contains_anchor('Woraus besteht Glas?','aus')
assert not v7.v5.contains_anchor('Er besteht die Prüfung.','aus')

phrase={'type':'phrase','headword':'sich an jdn. kuscheln'}
assert v7.v5.structural_example_ok(phrase,'Er kuschelte sich an sie und streichelte sie zärtlich.')
assert v7.v5.structural_example_ok(phrase,'Als sie sich an ihn kuscheln wollte, lächelte er.')
assert not v7.v5.structural_example_ok(phrase,'Sie kuschelt mit ihren Teddybären.')
assert not v7.v5.structural_example_ok(phrase,'Die beiden kuschelten zusammen.')

phrase2={'type':'phrase','headword':'bestehen aus (Dat.)'}
assert v7.v5.structural_example_ok(phrase2,'Materie besteht aus Atomen.')
assert v7.v5.structural_example_ok(phrase2,'Woraus besteht Seife?')
assert not v7.v5.structural_example_ok(phrase2,'Er besteht die Prüfung.')

# Stage-2 semantic repair + deterministic rection: only an explicitly bound direct
# complement creates direct-object Rektion; bare source shorthand may not reappear.
assert v7.derive_rection_v7({'headword':'sich etw. (Dat.) verschließen','provenance':{'sources':[]}})==['etwas + Dativ']
assert v7.derive_rection_v7({'headword':'los sein','provenance':{'sources':[{'evidence_note':'Raw German bundle: los sein [+A]'}]}})==[]
assert 'auf + Dativ' in v7.derive_rection_v7({'headword':'bestehen aus (Dat.)','provenance':{'sources':[]}})
assert 'für + Akkusativ' in v7.derive_rection_v7({'headword':'sich interessieren für (Akk.)','provenance':{'sources':[]}})

# Residual Verbformen top-up is exact-lemma evidence plus conservative surface filters.
rv={'type':'verb','headword':'sich ausruhen','core':{'reflexive':True}}
assert v7.residual_example_ok(rv,'Nach der Arbeit ruht er sich aus.','ausruhen')
assert not v7.residual_example_ok(rv,'Nach der Arbeit ruht er aus.','ausruhen')
nrv={'type':'verb','headword':'vorstellen','core':{'reflexive':False}}
assert v7.residual_example_ok(nrv,'Er stellt den neuen Kollegen vor.','vorstellen')
assert not v7.residual_example_ok(nrv,'Er stellt sich eine Reise vor.','vorstellen')

lex_phrase={'type':'phrase','headword':'aufzeigen','examples':[{'text':'Der Bericht zeigt Fehler auf.'}]}
assert v7.residual_example_ok(lex_phrase,'Die Grafik zeigt deutliche Unterschiede auf.','aufzeigen')
unanchored={'type':'phrase','headword':'nicht vorbereitet sein','examples':[{'text':'Ich bin nicht vorbereitet.'}]}
assert not v7.residual_example_ok(unanchored,'Wir sind heute gut vorbereitet.','sein')
source_alt={'type':'phrase','headword':'sich auf etw. einrichten','examples':[{'text':'Darauf bin ich nicht eingerichtet.'}]}
assert v7.residual_example_ok(source_alt,'Wir sind auf solche Änderungen eingerichtet.','einrichten')

print('PASS A2 v7 lemma + phrase sense + rection + residual-example regressions')
