#!/usr/bin/env python3
"""Audit an entire Aspekte B1+ lesson in one pass; never grants release approval.

Usage: python qa_full_lesson_v1.py OWNER.zip L05 OUTPUT_DIR
Outputs phase1_inventory.json, phase1_cards.jsonl and phase1_summary.md.

Only structurally verified facts and risk *candidates* are reported.
Linguistic QA, German–Persian semantic equivalence and app importer remain separate gates.
"""
import csv
import hashlib
import io
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

PREVIEW = 'G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
SOURCE_MAP = 'G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'

def norm(text):
    return ''.join(ch for ch in unicodedata.normalize('NFKC', str(text)).casefold() if ch.isalnum())

def json_dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

def validated_member_hashes(z):
    checks = z.read('SHA256SUMS.txt').decode('utf-8').splitlines()
    checked = 0
    for line in checks:
        if not line.strip():
            continue
        digest, name = line.split('  ', 1)
        assert hashlib.sha256(z.read(name)).hexdigest() == digest, 'Archive member SHA mismatch: '+name
        checked += 1
    assert checked == len(z.namelist())-1, 'Manifest member count incomplete'
    assert z.testzip() is None, 'ZIP CRC failure'
    return checked

def evaluate(owner_path, lesson, outdir):
    owner_path=Path(owner_path)
    outdir=Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    owner_sha=hashlib.sha256(owner_path.read_bytes()).hexdigest()
    with zipfile.ZipFile(owner_path) as z:
        member_checks=validated_member_hashes(z)
        raw_map=z.read(SOURCE_MAP)
        source_rows=list(csv.DictReader(io.StringIO(raw_map.decode('utf-8-sig')),delimiter='\t'))
        allcards=[json.loads(line) for line in z.read(PREVIEW).splitlines() if line.strip()]
    assert len(source_rows)==1548 and len(allcards)==1571
    allids=[x['preview_card_id'] for x in allcards]
    assert len(set(allids))==len(allids), 'Duplicate learner view IDs'
    cards=[c for c in allcards if c['lesson']==lesson]
    assert cards, 'No source lesson: '+lesson
    id_set={c['preview_card_id'] for c in cards}
    lesson_source_rows=[r for r in source_rows if set(r['G2_linked_learner_unit_IDS'].split(';')) & id_set]
    expected_ordinals={int(r['source_csv_ordinal']) for r in lesson_source_rows}
    linked_ordinals={int(i) for c in cards for i in c['linked_original_source_ordinals']}
    assert expected_ordinals==linked_ordinals, f'Lesson source map mismatch: expected {len(expected_ordinals)} mapped {len(linked_ordinals)}'
    assert all(set(r['G2_linked_learner_unit_IDS'].split(';')) <= id_set for r in lesson_source_rows), 'Cross-lesson source map mapping'
    assert len(id_set)==len(cards)
   
    ledger=[]
    summary=Counter()
    status_counts=Counter()
    flagged_sources=[]
    for c in sorted(cards,key=lambda x:x['source_ordinal']):
        b=c['back']; f=c['front'];
        existing=b.get('existing_examples_de_fa_pending_qa') or []
        added=b.get('additional_examples_de_fa_pending_qa') or []
        examples=existing+added
        nets=b.get('semantic_network_sense_anchored_pending_qa') or []
        meanings=b.get('meanings_fa_provisional','')
        marked_senses=[s.strip() for s in re.split(r'[؛;]', meanings) if s.strip()]
        poly_candidate=len(marked_senses)>=3 and not nets
        exact_duplicate_groups=[]
        seen=Counter(norm(e.get('de','')) for e in examples)
        for e in examples:
            text=e.get('de',''); n=norm(text)
            if n and seen[n]>1 and text not in exact_duplicate_groups: exact_duplicate_groups.append(text)
        missing_pairs=sum(not str(e.get('de','')).strip() or not str(e.get('fa','')).strip() for e in examples)
        malformed_nets=sum(not isinstance(s.get('Kombinationen_DE_FA',[]),list) for s in nets)
        wrong_forms_section=bool(b.get('Formen_section'))
        forms_attested=f.get('morphology_independently_validated') is True
        pending_examples=sum(str(e.get('status','')).upper().startswith('PENDING') for e in examples)
        scoped_pass_examples=sum('SCOPED' in str(e.get('status','')).upper() and 'PASS' in str(e.get('status','')).upper() for e in examples)
        no_status=sum(not str(e.get('status','')).strip() for e in examples)
        semantic_complexity=len(nets)+int(poly_candidate)
        critical=[]
        if missing_pairs:critical.append('MISSING_DE_OR_FA_EXAMPLE')
        if exact_duplicate_groups:critical.append('DUPLICATE_EXAMPLE_WITHIN_CARD')
        if wrong_forms_section:critical.append('REDUNDANT_FORMEN_ON_BACK')
        if malformed_nets:critical.append('MALFORMED_SENSE_COMBINATIONS')
        if not f.get('display_de_provisional') or not f.get('base_headword_de') or not meanings:
            critical.append('MISSING_FRONT_OR_FA_MEANING')
        if not examples:critical.append('NO_DE_FA_EXAMPLES')
        if critical:priority='P0_STRUCTURAL'
        elif (not forms_attested and poly_candidate) or c.get('curated_HOLD_content_disposition_exists'):
            priority='P1_COMPLEX_OR_CURATED_HOLD'
        elif not forms_attested or poly_candidate or len(nets)>=2:
            priority='P2_LINGUISTIC_REVIEW'
        else:priority='P3_STANDARD_REQUIRED_QA'
        tracks=[]
        if not forms_attested: tracks.append('G2_FORM_EVIDENCE')
        if poly_candidate:tracks.append('G4_MULTISENSE_ROUTING_CANDIDATE')
        if nets:tracks.append('G4_SENSE_RELATIONS_REVIEW')
        if pending_examples or no_status:tracks.append('G4_BILINGUAL_EXAMPLES_REVIEW')
        if c.get('curated_HOLD_content_disposition_exists'):tracks.append('CURATED_HOLD_CHECK')
        if critical:tracks.append('STRUCTURAL_REPAIR')
        if not tracks:tracks.append('FULL_CARD_SEMANTIC_QA_REQUIRED')
        entry={
          'lesson':lesson,
          'source_ordinal':c['source_ordinal'],
          'linked_original_source_ordinals':c['linked_original_source_ordinals'],
          'preview_card_id':c['preview_card_id'],
          'lemma_de':f.get('base_headword_de'),
          'front_forms_de':f.get('display_de_provisional'),
          'meanings_fa':meanings,
          'priority':priority,
          'critical_structural_issues':critical,
          'G2_form_attested':forms_attested,
          'G2_form_status':'EVIDENCE_ATTESTED_SCOPED_NOT_FULL_CARD' if forms_attested else 'INDEPENDENT_EVIDENCE_NOT_RECORDED',
          'G4_sense_blocks':len(nets),
          'G4_semantic_network_present':bool(nets),
          'G4_multi_sense_without_network_candidate':poly_candidate,
          'G4_semicolon_meaning_segments':len(marked_senses),
          'G4_full_card_approved':c.get('formal_release_approved',False) is True,
          'existing_DE_FA_example_pairs':len(existing),
          'additional_DE_FA_example_pairs':len(added),
          'total_DE_FA_example_pairs':len(examples),
          'example_status_pending_count':pending_examples,
          'example_status_scoped_pass_count':scoped_pass_examples,
          'example_status_absent_count':no_status,
          'exact_within_card_duplicate_examples':exact_duplicate_groups,
          'curated_HOLD_content_disposition_exists':bool(c.get('curated_HOLD_content_disposition_exists')),
          'manual_review_tracks':tracks,
          'release_allowed':False,
          'audit_scope':'STRUCTURAL_INVENTORY_ONLY_NOT_INDEPENDENT_LINGUISTIC_QA'
        }
        ledger.append(entry)
        summary['cards']+=1
        summary['linked_source_occurrences']+=len(c['linked_original_source_ordinals'])
        summary['attested_forms']+=forms_attested
        summary['missing_G2_evidence']+=not forms_attested
        summary['with_sense_network']+=bool(nets)
        summary['no_sense_network']+=not bool(nets)
        summary['sense_blocks']+=len(nets)
        summary['polysemy_no_network_candidates']+=poly_candidate
        summary['examples_DE_FA']+=len(examples)
        summary['pending_example_statuses']+=pending_examples
        summary['scoped_pass_example_statuses']+=scoped_pass_examples
        summary['example_status_absent']+=no_status
        summary['example_duplicate_groups']+=len(exact_duplicate_groups)
        summary['curated_hold_records']+=bool(c.get('curated_HOLD_content_disposition_exists'))
        summary['structurally_failing_cards']+=bool(critical)
        summary['full_card_approved']+=c.get('formal_release_approved',False) is True
        summary[priority]+=1
        for e in examples:status_counts[str(e.get('status',''))]+=1
        if critical:flagged_sources.append(c['source_ordinal'])
    summary['source_map_original_rows']=len(expected_ordinals)
    summary['total_G2_card_views']=len(allcards)
    summary['total_original_source_rows']=len(source_rows)
    summary['sha256_manifest_entries_validated']=member_checks
    summary['untracked_lesson_source_rows']=len(expected_ordinals-linked_ordinals)
    report={
      'schema':'aspekte-b1plus-entire-lesson-phase1-inventory@1.0.0',
      'lesson':lesson,
      'date':'2026-11-08',
      'input_owner_sha256':owner_sha,
      'input_owner_bytes':owner_path.stat().st_size,
      'original_source_map_sha256':hashlib.sha256(raw_map).hexdigest(),
      'input_zip_integrity':'SHA256_MANIFEST_AND_ZIP_CRC_PASS',
      'status':'PHASE_1_OF_3_COMPLETE_STRUCTURAL_INVENTORY_ONLY',
      'workflow_model':{
        'stage1':'FULL_LESSON_PRECHECK_ALL_CARDS_AND_RISK_CLASSIFICATION',
        'stage2':'ALL_ISSUES_CORRECTED_IN_LESSON_WITH_SCOPED_INDEPENDENT_LINGUISTIC_QA',
        'stage3':'INDEPENDENT_FULL_LESSON_QA_AND_REAL_APP_TSV_TEST_OR_EXPLICIT_BLOCKER_LIST',
        'max_stages':3,
        'no_per_10_card_review_loops':True,
        'canonical_source':'LATEST_NONIMPORT_USER_CURATED_LIBRARY_OWNER_NOT_ORIGINAL_TEXTBOOK_CSV',
        'release_requires':'ZERO_CRITICAL_ERRORS_COMPLETE_INDEPENDENT_CARD_QA_REAL_APP_RUNTIME_AND_TSV_VERIFICATION'
      },
      'summary':dict(summary),
      'example_status_distribution':dict(status_counts),
      'P0_structurally_failing_ordinals':flagged_sources,
      'P1_high_priority_source_ordinals':[x['source_ordinal'] for x in ledger if x['priority']=='P1_COMPLEX_OR_CURATED_HOLD'],
      'P2_review_source_ordinals':[x['source_ordinal'] for x in ledger if x['priority']=='P2_LINGUISTIC_REVIEW'],
      'G2_unattested_source_ordinals':[x['source_ordinal'] for x in ledger if not x['G2_form_attested']],
      'polysemy_without_network_candidates':[x['source_ordinal'] for x in ledger if x['G4_multi_sense_without_network_candidate']],
      'source_merges_in_this_lesson':[{'preview_card_id':c['preview_card_id'],'linked_original_source_ordinals':c['linked_original_source_ordinals']} for c in cards if len(c['linked_original_source_ordinals'])>1],
      'phase2_queue_policy':'Fix entire lesson with P0 then P1 then P2 then P3; each of 155 cards must get a final per-card decision. 130 cards without Wortnetz are not automatically errors. Source/meaning retention unless independently rejected.',
      'phase3_blockers_not_auto_cleared':['ALL_CARDS_NOT_FORMALLY_APPROVED','G5_APP_RUNTIME_AND_REAL_TSV_NOT_TESTED','INDEPENDENT_GERMAN_PERSIAN_SEMANTIC_QA_NOT_DONE','GLOBAL_LEGACY_DUPLICATES_OUTSIDE_LESSON_NOT_CLEARED'],
      'current_lesson_release_approved':False,
      'facts_vs_judgments':'All counts derived mechanically from exact owner; no independent dictionary attestations produced in this phase; previous attested flags are inherited.'
    }
    (outdir/'L05-PHASE1-COMPLETE-LESSON-AUDIT.json').write_text(json_dumps(report)+'\n',encoding='utf-8')
    (outdir/'L05-PHASE1-155-CARD-DECISION-QUEUE.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in ledger),encoding='utf-8')
    (outdir/'L05-PHASE1-MANAGEMENT-SUMMARY.md').write_text(
      '# Aspekte B1+ L05 — Drei-Phasen-Plan\n\n**Status:** Phase 1 / 3 abgeschlossen (strukturierter Voll-Lektions-Audit), NONIMPORT.\n\n'
      f'- Karten: **{len(cards)}**, originale Source-Map-Zeilen: **{len(expected_ordinals)}** (1 bestätigte 610/611-Zusammenlegung).\n'
      f'- Bereits scoped G2-attestiert: **{summary["attested_forms"]}**; fehlende Einzelatteste **{summary["missing_G2_evidence"]}**, nicht automatisch Fehler.\n'
      f'- DE–FA Beispiele: **{summary["examples_DE_FA"]}**, davon **{summary["pending_example_statuses"]}** noch explizit PENDING, **{summary["scoped_pass_example_statuses"]}** scoped PASS, **{summary["example_status_absent"]}** ohne Status.\n'
      f'- Mit Wortnetz: **{summary["with_sense_network"]}** / ohne: **{summary["no_sense_network"]}**; **{summary["polysemy_no_network_candidates"]}** mehrdeutige Kandidaten ohne Bedeutungsrouten (manuell nachsehen; nicht automatisch Fehler).\n'
      f'- Kuratierte HOLD-Marker in L05: **{summary["curated_hold_records"]}**; lokale genaue Beispiel-Dubletten: **{summary["example_duplicate_groups"]}**; strukturell fehlende Kartenfelder: **{summary["structurally_failing_cards"]}**.\n'
      f'- Priorität P1/P2/P3: **{summary["P1_COMPLEX_OR_CURATED_HOLD"]}/{summary["P2_LINGUISTIC_REVIEW"]}/{summary["P3_STANDARD_REQUIRED_QA"]}** (jede Karte wird sprachlich durchgesehen, P3 ist keine Freigabe).\n\n'
      '## Nächste verbindliche Schritte\n\n'
      '1. **Phase 2 / 3:** 155-Karten-Entscheidungsqueue einmal vollständig abarbeiten, zuerst höher priorisierte Fälle. Nur nachgewiesene sprachliche Fehler berichtigen; alle Bedeutungen pro Karte behalten, G2-Formen auf Front und Beispiele/Kollokationen nach Sinn verankern. Keine 10er-Review-Schleifen.\n'
      '2. **Phase 3 / 3:** Unabhängiger vollständiger QA-Gate, reale App-TSV-Importprüfung. Erst freigegebene Karten exportieren; ungelöste Karten mit begründetem HOLD in derselben Lektionsabschlussmeldung auflisten.\n\n'
      'Das gesamte Stage-3-Preview ist nicht dasselbe wie vollständiges fachsprachliches G4-QA; die Phase-1-Prüfung ändert den Owner nicht.\n',encoding='utf-8')
    print(json_dumps({'status':report['status'],'summary':report['summary'],'merge':report['source_merges_in_this_lesson'],'high_priority':report['P1_high_priority_source_ordinals'],'P0':report['P0_structurally_failing_ordinals']}))
    return report

if __name__=='__main__':
    if len(sys.argv)!=4:
        print('Usage: python qa_full_lesson_v1.py OWNER.zip L05 OUTPUT_DIR',file=sys.stderr)
        sys.exit(2)
    evaluate(sys.argv[1],sys.argv[2],sys.argv[3])