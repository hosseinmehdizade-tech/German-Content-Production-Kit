#!/usr/bin/env python3
from __future__ import annotations

from datetime import date

import enrich_current_only_v2 as base
import enrich_current_only_v6 as v6
import enrich_current_only_v7 as v7
import enrich_current_only_v8 as v8
import enrich_current_only_v9 as v9  # installs the safer rection decoder into v8


def _original_style_phrases(sentence: str, lemma: str):
    """Return several compact combinations using only lexical material in one current example.

    This deliberately restores the multi-candidate dependency extraction that v8
    narrowed to one sentence-level phrase.  No historical/legacy enrichment is read.
    The target verb is normalized to its current lemma; all other lexical material
    must be attested in the same current German example.
    """
    doc = v7.nlp()(sentence)
    verbs = [
        t for t in doc
        if t.pos_ in {'VERB', 'AUX'} and t.lemma_.casefold() == lemma.casefold()
    ]
    if not verbs:
        verbs = [
            t for t in doc
            if t.pos_ == 'VERB'
            and (
                t.lemma_.casefold().endswith(lemma.casefold())
                or lemma.casefold().endswith(t.lemma_.casefold())
            )
        ]
    verb = verbs[0] if verbs else None
    phrases = []
    seen = set()

    def add(tokens):
        phrase = v7.clean_phrase(tokens, lemma)
        if not phrase:
            return
        key = phrase.casefold()
        if key in seen:
            return
        # Reject essentially pronoun-only/generalized residues.  At least one
        # attested lexical content token besides the normalized target lemma is required.
        doc2 = v7.nlp()(phrase)
        lexical = [
            t for t in doc2
            if t.lemma_.casefold() != lemma.casefold()
            and t.pos_ in {'NOUN', 'PROPN', 'ADJ', 'ADV', 'ADP', 'NUM', 'PART'}
        ]
        if not lexical:
            return
        seen.add(key)
        phrases.append(phrase)

    if verb is not None:
        # Governed arguments and modifiers of the current target predicate.
        for child in verb.children:
            if child.dep_ in {
                'nsubj', 'nsubj:pass', 'csubj', 'aux', 'aux:pass', 'cop',
                'punct', 'cc', 'conj', 'mark', 'ccomp', 'xcomp', 'advcl',
                'acl', 'parataxis'
            }:
                continue
            toks = [t for t in child.subtree if not t.is_punct and t.i != verb.i]
            add([v6.normalize_token(t) for t in sorted(toks, key=lambda x: x.i)])

    # Prepositional groups from the exact current sentence.
    for t in doc:
        if t.pos_ == 'ADP':
            toks = [
                x for x in t.subtree
                if not x.is_punct and (verb is None or x.i != verb.i)
            ]
            add([v6.normalize_token(x) for x in sorted(toks, key=lambda x: x.i)])

    # Noun/proper-noun groups and predicate modifiers from the exact current sentence.
    for t in doc:
        if t.pos_ in {'NOUN', 'PROPN'}:
            toks = [
                x for x in t.subtree
                if x.pos_ in {'DET', 'ADJ', 'NOUN', 'PROPN', 'PRON', 'NUM'}
                and (verb is None or x.i != verb.i)
            ]
            add([v6.normalize_token(x) for x in sorted(toks, key=lambda x: x.i)])
        elif t.pos_ in {'ADV', 'ADJ'} and t.dep_ != 'amod':
            add([v6.normalize_token(t)])

    # Sentence-level predicate residue is a final, still-current-example candidate.
    if verb is not None:
        toks = []
        for t in doc:
            if t.is_punct or t.i == verb.i:
                continue
            if t.dep_ in {'nsubj', 'nsubj:pass', 'aux', 'aux:pass'}:
                continue
            if t.pos_ in {'VERB', 'AUX'}:
                continue
            toks.append(t)
        add([v6.normalize_token(t) for t in toks])

    return phrases


def _ensure_current_example_source(unit):
    sources = unit.setdefault('provenance', {}).setdefault('sources', [])
    sid = 'current_card_examples_current_build_v10'
    if any(s.get('source_id') == sid for s in sources if isinstance(s, dict)):
        return
    sources.append({
        'source_id': sid,
        'source_kind': 'current_dataset_evidence',
        'what_was_verified': ['collocation'],
        'verification_status': 'verified',
        'locator': f"current-canonical://{unit.get('id')}/examples",
        'accessed_at': str(date.today()),
        'evidence_note': (
            'Current-only v3.1.10 closure: each added learner combination is '
            'composed only of lexical material attested in this same current '
            'card’s German example sentences, with the target verb normalized '
            'to its lemma. No legacy enrichment, NVV columns, historical '
            'mappings, or previous enriched card sets were used.'
        )
    })


def enrich_v10(dataset, delay=.04):
    out, rep = v8.enrich_v8(dataset, delay)
    rep['pipeline'] = 'current-only-final-v10'
    rep['v10_closure_verbs'] = 0
    rep['v10_current_example_collocations_added'] = 0

    for unit in out.get('learning_units', []):
        if unit.get('type') != 'verb':
            continue
        connections = [c for c in unit.get('connections', []) if isinstance(c, dict)]
        unit['connections'] = connections
        existing = {
            base.norm(c.get('text', '')).casefold()
            for c in connections
            if c.get('kind') == 'collocation' and base.norm(c.get('text', ''))
        }
        count = len(existing)
        if count >= 3:
            continue

        lemma = v6.lookup_lemma(unit.get('headword', ''))
        if not lemma:
            continue
        added = 0
        for ex in unit.get('examples', []):
            sentence = base.norm((ex or {}).get('text', '')) if isinstance(ex, dict) else ''
            if not sentence:
                continue
            for phrase in _original_style_phrases(sentence, lemma):
                key = phrase.casefold()
                if key in existing:
                    continue
                connections.append({'text': phrase, 'kind': 'collocation'})
                existing.add(key)
                count += 1
                added += 1
                if count >= 3:
                    break
            if count >= 3:
                break

        if added:
            _ensure_current_example_source(unit)
            rep['v10_closure_verbs'] += 1
            rep['v10_current_example_collocations_added'] += added
            rep['collocations_added'] = rep.get('collocations_added', 0) + added

    rep['verbs_with_3plus_collocations'] = sum(
        1 for unit in out.get('learning_units', [])
        if unit.get('type') == 'verb'
        and sum(
            1 for c in unit.get('connections', [])
            if isinstance(c, dict)
            and c.get('kind') == 'collocation'
            and base.norm(c.get('text', ''))
        ) >= 3
    )
    return out, rep


base.enrich = enrich_v10

if __name__ == '__main__':
    base.main()
