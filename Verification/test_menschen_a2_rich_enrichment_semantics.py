#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'Workspaces/menschen-a2/tools';sys.path.insert(0,str(TOOLS))
spec=importlib.util.spec_from_file_location('v6',TOOLS/'enrich_rich_card_v6.py');v6=importlib.util.module_from_spec(spec);spec.loader.exec_module(v6)

assert v6.v5.lookup_lemma('bestehen aus (Dat.)')=='bestehen'
assert v6.v5.lookup_lemma('auf etw. (Dat.) bestehen')=='bestehen'
assert v6.v5.lookup_lemma('sich an jdn. kuscheln')=='kuscheln'
assert v6.v5.contains_anchor('Er besteht darauf, dass wir warten.','auf')
assert v6.v5.contains_anchor('Woraus besteht Glas?','aus')
assert not v6.v5.contains_anchor('Er besteht die Prüfung.','aus')

phrase={'type':'phrase','headword':'sich an jdn. kuscheln'}
assert v6.v5.structural_example_ok(phrase,'Er kuschelte sich an sie und streichelte sie zärtlich.')
assert v6.v5.structural_example_ok(phrase,'Als sie sich an ihn kuscheln wollte, lächelte er.')
assert not v6.v5.structural_example_ok(phrase,'Sie kuschelt mit ihren Teddybären.')
assert not v6.v5.structural_example_ok(phrase,'Die beiden kuschelten zusammen.')

phrase2={'type':'phrase','headword':'bestehen aus (Dat.)'}
assert v6.v5.structural_example_ok(phrase2,'Materie besteht aus Atomen.')
assert v6.v5.structural_example_ok(phrase2,'Woraus besteht Seife?')
assert not v6.v5.structural_example_ok(phrase2,'Er besteht die Prüfung.')

print('PASS A2 lemma resolution + da-compound + phrase-structure sense regressions')
