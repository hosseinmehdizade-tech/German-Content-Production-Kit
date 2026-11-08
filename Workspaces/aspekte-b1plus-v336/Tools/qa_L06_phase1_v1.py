#!/usr/bin/env python3
"""Aspekte B1+ L06 structural whole-lesson Phase 1. No curated-card mutations.
Reads ONLY the latest verified user-curated owner ZIP; never reopens old textbook CSV.
Writes full 177-card decision queue and QA-only report/browse view; no import output.
"""
import argparse, collections, csv, hashlib, html, io, json, re, zipfile
from pathlib import Path

MAIN = 'G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
SOURCE_MAP = 'G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
EXPECTED_OWNER_SHA = '31d8d0640d5bacdb080f0a379aa926542498a905c82b4e3d2f3d670d7bb2aca4'
MIN_SOURCE, MAX_SOURCE = 672, 846
LESSON = 'L06'
DATE = '2026-11-09'

def sha(b): return hashlib.sha256(b).hexdigest()
def norm(s): return re.sub(r'\W+', '', str(s or '').casefold())
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def load_verified_owner(path):
    assert sha(path.read_bytes()) == EXPECTED_OWNER_SHA, 'OWNER_SHA256_MISMATCH_STOP'
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None, 'ZIP_CRC_FAIL'
        names=set(z.namelist())
        manifest={}
        for entry in z.read('SHA256SUMS.txt').decode().splitlines():
            digest,n=entry.split('  ',1)
            assert n not in manifest,'DUPLICATE_MANIFEST_ENTRY'
            manifest[n]=digest
        assert names-{'SHA256SUMS.txt'} == set(manifest),'ZIP_MANIFEST_COVERAGE_FAIL'
        assert all(sha(z.read(n))==digest for n,digest in manifest.items()),'ZIP_MEMBER_HASH_FAIL'
        card_bytes=z.read(MAIN);map_bytes=z.read(SOURCE_MAP)
    cards=[json.loads(line) for line in card_bytes.splitlines()]
    mapping=list(csv.DictReader(io.StringIO(map_bytes.decode('utf-8')),delimiter='\t'))
    assert len(cards)==1571 and len(mapping)==1548,'BASE_COUNTS_MISMATCH'
    ids=[c['preview_card_id'] for c in cards]
    assert len(set(ids))==1571,'CARD_ID_NOT_UNIQUE'
    by_id={c['preview_card_id']:c for c in cards}
    assert [int(x['source_csv_ordinal']) for x in mapping] == list(range(1,1549)),'SOURCE_ORDINAL_MAP_GAP'
    for row in mapping:
        ord_num=int(row['source_csv_ordinal'])
        mapped=[x for x in row['G2_linked_learner_unit_IDS'].split(';') if x]
        assert mapped,'SOURCE_WITHOUT_CARD_ID'
        for cid in mapped:
            assert cid in by_id,'SOURCE_CARD_ID_NOT_FOUND '+cid
            assert ord_num in by_id[cid]['linked_original_source_ordinals'],'CARD_MISSING_SOURCE_LINK '+cid
    assert all(c.get('formal_release_approved') is False and c.get('import_ready') is False for c in cards),'UNEXPECTED_RELEASED_CARD'
    return cards,mapping,card_bytes,map_bytes,len(manifest)

def examples(card):
    b=card['back']
    return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])

def audit(owner,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    cards,mapping,mainbytes,mapbytes,verified_members=load_verified_owner(owner)
    selected=[c for c in cards if c.get('lesson')==LESSON]
    assert len(selected)==177,'LESSON_CARD_COUNT_CHANGED'
    wanted=set(range(MIN_SOURCE,MAX_SOURCE+1))
    owner_links=collections.defaultdict(list)
    for c in cards:
        for ordinal in c['linked_original_source_ordinals']:
            if ordinal in wanted: owner_links[ordinal].append(c)
    assert set(owner_links)==wanted,'LESSON_SOURCE_ORDINAL_UNMAPPED'
    crosslesson={str(n):[{'lesson':c['lesson'],'source_ordinal':c['source_ordinal'],'card_id':c['preview_card_id'],'headword':c['front']['base_headword_de']} for c in xs] for n,xs in owner_links.items() if any(c['lesson']!=LESSON for c in xs)}
    missing_primary=sorted(wanted-{c['source_ordinal'] for c in selected})
    duplicates_primary={str(n):v for n,v in sorted(collections.Counter(c['source_ordinal'] for c in selected).items()) if v>1}
    assert missing_primary==[733,762],f'UNEXPECTED_PRIMARY_MERGES {missing_primary}'
    assert sorted(duplicates_primary)==['679','714','771','773'],'UNEXPECTED_SPLITS'
    assert '733' in crosslesson and any(c['lesson']=='L01' for c in owner_links[733]),'CROSSLESSON_733_LOST'
    assert any(c['source_ordinal']==761 for c in owner_links[762]),'L06_761_762_MERGE_LOST'
    qa_status=collections.Counter();priority=collections.Counter();risk_types=collections.Counter()
    summary=collections.Counter();duplicate_examples=[];invalid_references=[]
    rows=[];countable_networks=[]
    for c in selected:
        b=c['back']; f=c['front']; ex=examples(c); networks=b.get('semantic_network_sense_anchored_pending_qa') or []
        card_id=c['preview_card_id'];ordn=c['source_ordinal'];headword=f.get('base_headword_de','')
        existing=b.get('existing_examples_de_fa_pending_qa') or []
        extra=b.get('additional_examples_de_fa_pending_qa') or []
        ids={n['sense_id'] for n in networks}
        unrouted=[{'de':e.get('de'),'fa':e.get('fa'),'present_sense_id':e.get('sense_id')} for e in ex if networks and e.get('sense_id') not in ids]
        incorrect_refs=[{'de':e.get('de'),'sense_id':e.get('sense_id')} for e in ex if e.get('sense_id') and e.get('sense_id') not in ids]
        invalid_references.extend({'card_id':card_id,**d} for d in incorrect_refs)
        statusless=[{'de':e.get('de'),'fa':e.get('fa')} for e in ex if not e.get('status')]
        empties=[e for e in ex if not str(e.get('de','')).strip() or not str(e.get('fa','')).strip()]
        assert not empties,'BLANK_DE_FA_EXAMPLE_FIELDS'
        repeated=collections.defaultdict(list)
        for e in ex:
            normalized=norm(e.get('de'))
            if normalized:repeated[normalized].append(e)
            qa_status[e.get('status') or 'MISSING']+=1
        duplicated=[{'de':v[0]['de'],'count':len(v),'fa_variants':[e.get('fa','') for e in v]} for v in repeated.values() if len(v)>1]
        for d in duplicated: duplicate_examples.append({'card_id':card_id,'ordinal':ordn,'headword':headword,**d})
        reasons=[];actions=[]
        if c.get('curated_HOLD_content_disposition_exists'):
            reasons.append('INHERITED_CURATED_HOLD');actions.append('Resolve retained HOLD with explicit evidence; no automatic clearing')
        if not ex:
            reasons.append('ZERO_BILINGUAL_EXAMPLES');actions.append('Draft natural DE–FA example(s) with relevant meaning, mark pending language QA')
        if duplicated:
            reasons.append('INTRA_CARD_DUPLICATE_DE_EXAMPLE');actions.append('Adjudicate exact duplicate examples, preserving distinct valid FA wording if useful')
        if statusless:
            reasons.append('EXAMPLES_WITHOUT_EXPLICIT_QA_STATUS');actions.append('Assign explicit PENDING/QA provenance; do not automatically mark PASS')
        if unrouted:
            reasons.append('NETWORKED_EXAMPLES_WITHOUT_VALID_SENSE_ID');actions.append('Route each example to exactly evidenced sense; retain ambiguity HOLD where contextual evidence insufficient')
        if incorrect_refs:
            reasons.append('INVALID_EXAMPLE_SENSE_REFERENCE');actions.append('Repair or remove invalid sense IDs after editorial review')
        if not f.get('morphology_independently_validated'):
            reasons.append('MORPHOLOGY_NOT_SCOPE_ATTESTED');actions.append('Check article/plural, conjugation or invariant category where relevant; absence of evidence is not a grammatical error')
        if not networks and any(token in str(b.get('meanings_fa_provisional','')) for token in ['؛']):
            reasons.append('MULTISENSE_HEURISTIC_REVIEW_CANDIDATE');actions.append('Distinguish genuinely separate senses from simple synonyms; keep all accepted meanings in one card')
        if extra:
            reasons.append('ADDITIONAL_EDITORIAL_EXAMPLES_PRESENT');actions.append('Verify supplemental examples have independent DE–FA wording and status')
        if not reasons:
            actions.append('Check whole card once for natural DE/FA, morphology, combinations and final evidence; no automatic signoff')
        if any(k in reasons for k in ['INHERITED_CURATED_HOLD','ZERO_BILINGUAL_EXAMPLES','INTRA_CARD_DUPLICATE_DE_EXAMPLE','EXAMPLES_WITHOUT_EXPLICIT_QA_STATUS','NETWORKED_EXAMPLES_WITHOUT_VALID_SENSE_ID','INVALID_EXAMPLE_SENSE_REFERENCE']): priority_level='P1'
        elif any(k in reasons for k in ['MORPHOLOGY_NOT_SCOPE_ATTESTED','MULTISENSE_HEURISTIC_REVIEW_CANDIDATE','ADDITIONAL_EDITORIAL_EXAMPLES_PRESENT']):priority_level='P2'
        else:priority_level='P3'
        priority[priority_level]+=1;risk_types.update(reasons)
        summary['original_lesson_cards']+=1
        summary['existing_examples']+=len(existing);summary['additional_examples']+=len(extra)
        summary['example_pairs']+=len(ex); summary['missing_examples_cards']+=int(not ex)
        summary['missing_QA_status_examples']+=len(statusless)
        summary['cards_with_missing_QA_status']+=bool(statusless)
        summary['morphology_scoped_attestations']+=bool(f.get('morphology_independently_validated'))
        summary['curated_HOLD_cards']+=bool(c.get('curated_HOLD_content_disposition_exists'))
        summary['wordnet_cards']+=bool(networks)
        summary['sense_blocks']+=len(networks)
        summary['examples_on_wordnet_cards']+=len(ex) if networks else 0
        summary['unrouted_examples_on_wordnet_cards']+=len(unrouted)
        summary['linked_examples_on_wordnet_cards']+=len(ex)-len(unrouted) if networks else 0
        summary['combinations_in_lesson']+=sum(len(n.get('Kombinationen_DE_FA',[])) for n in networks)
        countable_networks.extend(networks)
        rows.append({'lesson':LESSON,'source_ordinal':ordn,'linked_original_source_ordinals':c['linked_original_source_ordinals'],
          'card_id':card_id,'headword_de':headword,'front_display_de':f.get('display_de_provisional'),
          'meanings_fa_current':b.get('meanings_fa_provisional'),
          'priority':priority_level,'risk_flags':reasons,'phase2_actions':actions,
          'examples':[{'de':e.get('de'),'fa':e.get('fa'),'status':e.get('status') or 'MISSING',
              'sense_id':e.get('sense_id'),'origin':e.get('provenance')} for e in ex],
          'semantic_network_blocks':networks,
          'source_row_mappings':c['linked_original_source_ordinals'],
          'morphology_scope_attested':bool(f.get('morphology_independently_validated')),
          'curated_HOLD':bool(c.get('curated_HOLD_content_disposition_exists')),
          'duplicate_DE_example_groups':duplicated,'statusless_examples':statusless,
          'unrouted_meaning_examples':unrouted,
          'phase1_data_mutation':False,'formal_language_release_approved':False})
    assert summary['example_pairs']==370 and summary['wordnet_cards']==18 and summary['sense_blocks']==26,'L06_INPUT_UNEXPECTED'
    assert summary['linked_examples_on_wordnet_cards']==1 and summary['unrouted_examples_on_wordnet_cards']==36,'SENSE_ROUTING_COUNT_UNEXPECTED'
    assert summary['curated_HOLD_cards']==33 and summary['morphology_scoped_attestations']==108,'MORPHOLOGY_HOLD_COUNT_UNEXPECTED'
    assert summary['missing_QA_status_examples']==16 and summary['missing_examples_cards']==4,'EXAMPLE_QA_COUNT_UNEXPECTED'
    assert len(duplicate_examples)==2,'DUPLICATE_COUNT_UNEXPECTED'
    assert len(rows)==177 and len({r['card_id'] for r in rows})==177,'QUEUE_COMPLETENESS_FAIL'
    rows.sort(key=lambda r:({'P1':0,'P2':1,'P3':2}[r['priority']],r['source_ordinal'],r['headword_de']))
    global_duplicates=[]
    for c in cards:
        grouped=collections.Counter(norm(e.get('de')) for e in examples(c) if norm(e.get('de')))
        for key,n in grouped.items():
            if n>1:global_duplicates.append({'card_id':c['preview_card_id'],'lesson':c['lesson'],'source_ordinal':c['source_ordinal'],'count':n})
    assert len(global_duplicates)==5,'GLOBAL_DUPLICATE_REGRESSION'
    summary['forms_lacking_scoped_lexicographic_evidence']=177-summary['morphology_scoped_attestations']
    report={'schema':'aspekte-b1plus-whole-lesson-audit@L06-phase1-v1','date':DATE,
      'lesson':LESSON,'phase':1,'phases_total':3,
      'status':'L06_PHASE1_WHOLE_177_CARD_DETERMINISTIC_AUDIT_COMPLETE_NONIMPORT_NO_CARD_TEXT_EDITS',
      'owner_path_basename':owner.name,'owner_sha256':sha(owner.read_bytes()),'owner_primary_card_sha256':sha(mainbytes),
      'owner_source_map_sha256':sha(mapbytes), 'owner_zip_manifest_entries_verified':verified_members,
      'owner_zip_crc':'PASS', 'owner_card_objects_modified':0,
      'global_card_views':len(cards),'global_original_source_rows':len(mapping),'lesson_card_views':len(selected),
      'lesson_source_range_inclusive':[MIN_SOURCE,MAX_SOURCE],'lesson_source_rows_in_range':len(wanted),
      'lesson_source_rows_globally_mapped':len(owner_links),'source_split_ordinals':duplicates_primary,
      'primary_ordinal_missing_due_to_merge_or_crosslink':missing_primary,'cross_lesson_links':crosslesson,
      'merge_evidence':{'762':'L06 ordinal 761 einhalten already linked to ordinal 762',
         '733':'L01 ordinal 18 Darauf kommt’s an linked to original L06 source ordinal 733'},
      'totals':dict(summary),'example_status_counts':dict(qa_status),
      'per_card_priority_counts':dict(priority),'risk_tag_counts':dict(risk_types),
      'within_card_exact_duplicate_examples':duplicate_examples,
      'all_corpus_duplicate_example_groups_inherited':global_duplicates,
      'invalid_nonempty_example_sense_ids':invalid_references,
      'cards_missing_examples':[{'ordinal':r['source_ordinal'],'word':r['headword_de'],'card_id':r['card_id']} for r in rows if not r['examples']],
      'all_177_dispositions':True,'all_cards_release_blocked':True,'formal_full_card_release_approved':0,
      'actual_app_import_render_tested':False,'import_ready':False,
      'critical_status':'P1_P2_P3_ARE_QUEUES_NOT_APPROVALS',
      'limitations':['Phase1 is deterministic structural and risk inventory only: no independent German–Persian full-card content QA.',
                     'A missing grammar attestation does not prove the grammar is wrong.',
                     'Potential sense splits based on semicolons are review candidates only; Persian synonyms can use semicolons.',
                     'No learner-card content was changed, no actual TSV app import was performed.',
                     'Existing sense networks/collocations were counted, not signed off as natural.']}
    assert sum(priority.values())==177
    dump(outdir/'L06-PHASE1-FULL-LESSON-AUDIT.json',report)
    (outdir/'L06-PHASE1-177-CARD-DECISION-QUEUE.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    plan=f'''# Aspekte B1+ · Lektion 06 · verbindlicher Drei-Phasen-Plan

**Stand {DATE} · Phase 1 of 3 DONE (whole lesson structural inventory); Phase 2 NEXT; NONIMPORT.**

## Authority / No regressions
The **latest SHA-verified user-curated** B1+ Library owner (L04 Phase3 ZIP SHA256 `{report['owner_sha256']}`) remains the sole learner-card authority. The owner is *unchanged* by Phase1. Do not return to textbook CSV. Full corpus of 1571 existing candidate cards and all 1548 source-row mappings remains valid; do not count old source files as new card data.

## Phase 1 whole-lesson findings
- **177 current L06 cards** across original source ordinals **672–846** (175 rows): every source row mapped. Legitimate dual-lexeme splits at **679**, **714**, **771**, **773** (2 cards each). Original row **762** merged into existing L06 ordinal 761 	4einhalten	4; source ordinal **733** crosslinked to existing L01 ordinal 18 	4Darauf kommt's an	4. Do not create replacement cards or delete valid split cards.
- **370 current DE–FA examples** = {summary['existing_examples']} existing + {summary['additional_examples']} supplemental, with 0 empty DE/FA pairs. **Four cards have no examples** (the separate lexical items 	4denkbar	4, 	4undenkbar	4, 	4erwünscht	4 and 	4unerwünscht	4). **16 examples** missing explicit QA status on {summary['cards_with_missing_QA_status']} cards; missing does not equal approved.
- **108 scoped form evidence flags / 69 not attested**; **33 inherited curated HOLD cards**. **18 cards with 26 existing meaning-network blocks**, but only **1/37** examples on those cards has a matching sense ID; **36 unrouted** (not necessarily 36 grammar errors). 2 exact within-card DE example duplicate groups in 	4die Besprechung	4 (ordinal 760) and 	4hin und her	4 (ordinal 820). **Five corpus-wide old duplicate groups remain**; two are in L06.
- Each of 177 cards has a case-specific Phase2 decision in the JSONL: **P1={priority['P1']}** (direct structural blockers / inherited HOLD / invalid or missing sense routes), **P2={priority['P2']}** (form evidence, examples and meaning heuristics), **P3={priority['P3']}** (remaining cards, still requiring full QA). These priorities are **not semantic or release approval**.

## Phase 2: whole 177-card editorial correction (NEXT)
- Work **all 177 in one lesson-level unit**, using P1 then P2 then P3 risk order; not 10-word Review loops. First adjudicate the 2 exact duplicate groups preserving all useful distinct translation variants, and add missing DE/FA example(s) to 4 zero-example cards.
- Review 36 unrouted network examples by their specific sense; do NOT force ambiguous context to a sense. Fill 16 example QA statuses with honest PENDING/verified evidence rather than automatic PASS. Recheck all 33 inherited HOLDs individually and 69 unverified forms where relevant.
- For ALL cards, review German + Persian meaning hierarchy, front morphology, example naturalness, sense-linked Synonyme/Antonyme/Wortfamilie/Kombinationen. Keep polysemy inside a single lemma card and preserve cross-lesson mapping.
- **Mandatory persistence regression:** when producing a corrected ZIP, verify the changed **primary 1571-card JSONL member** really contains the claimed card diffs; sidecars alone never count. Compare all non-L06 objects and the exact 1548-row map with parent, verify CRC/member SHA hashes and Library byte readback.

## Phase 3: full quality & import gate (LATER)
- Evaluate every case with explicit German–Persian content decisions and deterministic QA, record reasoned HOLDs (no fictitious external human examiner required).
- Test actual German-Flashcards-Pro TSV importer and real rendered front/back if available; offline TSV/HTML projection is NOT an app import.
- Finish with RELEASED for fully approved/tested cases, or an explicit RELEASE_BLOCKED/NONIMPORT lesson outcome with a concrete blocker ledger; never invent release approvals.
'''.replace('\u0094','`')
    (outdir/'L06-THREE-PHASE-PLAN.md').write_text(plan,encoding='utf-8')
    body=[]
    for r in rows:
        ex=''.join('<li>'+html.escape(e.get('de') or '')+'<div dir="rtl">'+html.escape(e.get('fa') or '')+'</div><small>'+html.escape(e.get('status') or '')+'</small></li>' for e in r['examples'])
        actions=''.join('<li>'+html.escape(s)+'</li>' for s in r['phase2_actions'])
        net=''.join('<li>'+html.escape(n.get('sense_de',''))+' / '+html.escape(n.get('sense_fa',''))+'</li>' for n in r['semantic_network_blocks'])
        body.append('<article data-key="'+html.escape((r['headword_de']+' '+r['meanings_fa_current']+' '+r['priority']).casefold(),quote=True)+'"><h2><span>'+r['priority']+'</span> '+html.escape(r['headword_de'])+' <small>#'+str(r['source_ordinal'])+'</small></h2><p dir="rtl">'+html.escape(r['meanings_fa_current'] or '')+'</p><p><b>Front:</b> '+html.escape(r['front_display_de'] or '')+'</p><details><summary>Examples ('+str(len(r['examples']))+')</summary><ul>'+ex+'</ul></details><details><summary>Meaning networks ('+str(len(r['semantic_network_blocks']))+')</summary><ul>'+net+'</ul></details><h4>Phase2 actions</h4><ul>'+actions+'</ul></article>')
    page='''<!doctype html><html lang="de"><meta charset="utf-8"><title>Aspekte B1+ L06 · 177 cards · QA only</title><style>body{font:15px system-ui,sans-serif;max-width:950px;margin:1.5rem auto;padding:0 1rem;background:#f7f8fa;color:#182536}header{position:sticky;top:0;background:#f7f8fa;padding:1rem 0}input{width:95%;padding:.8rem;font:inherit;border:1px solid #9aaaba;border-radius:8px}article{border:1px solid #ccd4de;background:white;border-radius:12px;padding:1rem 1.5rem;margin:1rem 0}small{color:#63748a}h2 span{background:#e8ebfa;color:#324779;padding:.2rem .45rem;border-radius:5px;font-size:.75rem}li{margin:.3rem 0;line-height:1.5}summary{cursor:pointer}h2{font-size:1.15rem}</style><header><h1>Lektion 06 · 177 cards · NONIMPORT</h1><p>Structural inventory; no card edits or release QA. Search by German, Persian or priority.</p><input id="find" placeholder="Wort, معنی, P1/P2/P3 ..."></header>'''+''.join(body)+'''<script>document.getElementById('find').oninput=function(){const q=this.value.toLocaleLowerCase();for(const a of document.querySelectorAll('article'))a.hidden=!a.dataset.key.includes(q)}</script></html>'''
    (outdir/'L06-PHASE1-177-CARD-REVIEW-QA-ONLY.html').write_text(page,encoding='utf-8')
    print(json.dumps({'audit_status':'PASS_L06_PHASE1_177_CARDS_NONIMPORT','summary':report,'files':[p.name for p in outdir.iterdir()]},ensure_ascii=False,indent=2)[:12000])
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('owner_zip',type=Path);p.add_argument('outdir',type=Path)
    a=p.parse_args();audit(a.owner_zip,a.outdir)
if __name__=='__main__':main()
