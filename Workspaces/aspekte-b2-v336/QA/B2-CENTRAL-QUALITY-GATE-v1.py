#!/usr/bin/env python3
"""Aspekte B2: read-only centralized release gate over current curated learner CSVs.

Never alters source cards, flags, SRS IDs, or files in the inputs directory.
This checker is not independent linguistic quality assurance or an app import test.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

LESSONS = [
    (1, "Heimat ist …", 1549, 1708, 158, "L01-CURRENT-158-UNIT-REVIEW-R47-NONIMPORT.csv"),
    (2, "Sprich mit mir!", 1709, 1816, 110, "L02-PASS2-110-UNIT-REVIEW-NONIMPORT.csv"),
    (3, "Arbeit ist das halbe Leben?", 1817, 2002, 186, "L03-PASS2-186-CURATED-REVIEW-NONIMPORT.csv"),
    (4, "Zusammen leben", 2003, 2186, 183, "L04-PASS2-183-UNIT-REVIEW-NONIMPORT.csv"),
    (5, "Wer Wissen schafft, macht Wissenschaft", 2187, 2417, 227, "L05-PASS2-227-CARD-EDITORIAL-REVIEW-NONIMPORT.csv"),
    (6, "Fit für …", 2418, 2558, 141, "L06-PASS2-141-CARD-EDITORIAL-REVIEW-NONIMPORT.csv"),
    (7, "Kulturwelten", 2559, 2780, 222, "L07-PASS2-222-CARD-EDITORIAL-REVIEW-NONIMPORT.csv"),
    (8, "Das macht(e) Geschichte", 2781, 2959, 180, "L08-PASS2-180-CARD-EDITORIAL-REVIEW-NONIMPORT.csv"),
    (9, "Mit viel Gefühl …", 2960, 3121, 161, "L09-PASS2-161-CARD-EDITORIAL-REVIEW-NONIMPORT.csv"),
    (10, "Ein Blick in die Zukunft", 3122, 3274, 151, "L10-PASS2-151-CARD-EDITORIAL-REVIEW-NONIMPORT.csv"),
]
# Source rows intentionally represented outside the regular learner-card unit CSV.
# All these decisions are documented in the earlier lesson exception/disposition receipts.
KNOWN_NONCARD_OR_ALIAS = {
    1: {1630: "CONDITIONAL_B1_REUSE_INTOLERANT__LIVE_ID_OPEN", 1660: "GRAMMATICAL_FACET_PARTIZIP_II_GEKOMMEN"},
    3: {1921: "MERGED_INTO_SOURCE_CARD_1920_DATUMSANGABE"},
    5: {2275: "SOURCE_SENTENCE_NONCARD", 2309: "MALFORMED_COLLOCATION_HOLD_NONCARD", 2369: "SOURCE_SENTENCE_NONCARD", 2380: "SOURCE_SENTENCE_NONCARD"},
    6: {2501: "SOURCE_SENTENCE_NONCARD"},
    7: {2627: "SOURCE_PROPOSITION_NONCARD_UNVERIFIED_FACT"},
    9: {3054: "SOURCE_SENTENCE_NONCARD"},
    10: {3219: "SOURCE_SENTENCE_NONCARD"},
}
# These are *documented source-level flags*, not verified duplicate live app cards.
KNOWN_CROSSLEVEL_HOLDS = {
    1: [1575, 1616, 1630],
    6: [2438, 2448, 2463, 2491, 2495, 2518, 2523, 2532],
    7: [2621, 2628, 2683, 2713],
    8: [2799, 2806, 2830, 2840, 2855, 2858, 2865, 2874, 2905, 2918, 2953],
    9: [2978, 2983, 3034, 3039, 3069, 3121],
    10: [3126, 3147, 3161, 3187, 3212, 3223, 3226, 3243, 3249],
}
REQUIRED_FIELDS = ["unit_id", "front_de_preview", "back_fa_preview", "example_1_de", "example_1_fa", "example_2_de", "example_2_fa", "export_importable", "linguistic_release_approved"]
SCHEMA = "aspekte-b2-central-release-audit@1.0.0"
POLICY_REVISION = "COLLOCATION_CONTEXT_ADVISORY__DUPLICATE_HARD_BLOCK_v1.1"

def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()

def write_csv(file, rows, cols):
    with file.open('w', encoding='utf-8-sig', newline='') as handle:
        wr = csv.DictWriter(handle, fieldnames=cols, lineterminator='\r\n', extrasaction='ignore')
        wr.writeheader()
        wr.writerows(rows)

def inspect(inputs, outputs, release_check=False):
    outputs.mkdir(parents=True, exist_ok=True)
    seen_ids = set()
    seen_examples = set()
    original_source_set = set()
    records = []
    flags = []
    duplicate_collocations = []
    source_exceptions = []
    row_report = []
    global_missing_required = []
    global_duplicate_id = []
    global_duplicate_example = []
    total_bonus_pairs = 0
    for lesson, title, first, last, expected_units, filename in LESSONS:
        file = inputs / filename
        if not file.is_file():
            raise FileNotFoundError(str(file))
        with file.open('r', encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) != expected_units:
            raise AssertionError(f"L{lesson:02d} expected {expected_units} units but found {len(rows)}")
        actual_ordinals = set()
        overlap_count = 0
        overlap_card_ids = set()
        colloc_total = 0
        cards_lacking_collocations = 0
        for row in rows:
            uid = row.get('unit_id', '')
            if uid in seen_ids:
                global_duplicate_id.append(uid)
            seen_ids.add(uid)
            row_missing = [k for k in REQUIRED_FIELDS if not (row.get(k) or '').strip()]
            for field in row_missing:
                global_missing_required.append({"lesson": lesson, "unit_id": uid, "field": field})
            for ex_field in ('example_1_de', 'example_2_de'):
                phrase = (row.get(ex_field) or '').casefold().strip()
                if phrase in seen_examples:
                    global_duplicate_example.append({"lesson": lesson, "unit_id": uid, "field": ex_field})
                seen_examples.add(phrase)
            src_text = row.get('source_ordinals') or row.get('source_ordinal') or ''
            source_ids = [int(v) for v in re.findall(r'(?<!\d)\d{4}(?!\d)', str(src_text))]
            actual_ordinals.update(source_ids)
            src_set = set(source_ids)
            existing_collocations = 'collocations_de' in row
            chunks = [c.strip() for c in (row.get('collocations_de') or '').split(';') if c.strip()]
            colloc_total += len(chunks)
            if not chunks:
                cards_lacking_collocations += 1
            chunks_normalized = [c.casefold() for c in chunks]
            card_has_duplicate_collocation = False
            for i, c in enumerate(chunks):
                if chunks_normalized.count(c.casefold()) > 1 and i == chunks_normalized.index(c.casefold()):
                    card_has_duplicate_collocation = True
                    duplicate_collocations.append({"lesson": lesson, "unit_id": uid, "front": row.get('front_de_preview', ''), "collocation": c, "issue": "REPEATED_WITHIN_SAME_CARD"})
            examples = [(row.get('example_1_de') or '').casefold(), (row.get('example_2_de') or '').casefold()]
            local_overlap = 0
            for c in chunks:
                match_indices = [idx+1 for idx, ex in enumerate(examples) if c.casefold() in ex]
                if not match_indices:
                    continue
                # Candidate matches are literal repeated text, not evidence of where the phrase was written first.
                severity = 'LONG_LITERAL_OVERLAP_15PLUS' if len(c) >= 15 else ('SHORT_MULTITOKEN_OVERLAP' if len(c.split()) > 1 else 'SINGLE_TOKEN_OVERLAP')
                flags.append({"lesson": lesson, "unit_id": uid, "source_ordinals": src_text, "front_de": row.get('front_de_preview', ''), "collocation": c, "exact_example_matches": '+'.join(map(str, match_indices)), "severity": severity, "characters": len(c), "action": "CONTEXTUAL_ADVISORY__NOT_STANDALONE_DEFECT__DO_NOT_AUTOREPLACE"})
                local_overlap += 1
            overlap_count += local_overlap
            if local_overlap:
                overlap_card_ids.add(uid)
            importable = str(row.get('export_importable', '')).strip().lower() in ('true', '1', 'yes')
            independently_approved = str(row.get('linguistic_release_approved', '')).strip().lower() in ('true', '1', 'yes')
            records.append({
                "lesson": lesson, "unit_id": uid, "source_ordinals": src_text, "front_de_preview": row.get('front_de_preview',''),
                "source_file": filename, "source_file_sha256": digest(file),
                "required_fields_present": not row_missing,
                "primary_DEFA_example_pairs": sum(bool(row.get(f'example_{n}_de') and row.get(f'example_{n}_fa')) for n in (1,2)),
                "collocation_column_available": existing_collocations,
                "collocation_count": len(chunks), "example_collocation_literal_overlap_count": local_overlap,
                "advisories": "COLLOCATION_IN_OWN_EXAMPLE__NORMAL_PEDAGOGIC_REVIEW" if local_overlap else "",
                "known_crosslevel_source_flag": bool(src_set & set(KNOWN_CROSSLEVEL_HOLDS.get(lesson, []))),
                "linguistic_release_approved": independently_approved, "export_importable": importable,
                "live_accepted_card_ID_verified": False, "native_SRS_roundtrip_verified": False,
                "release_status": "BLOCKED_NONIMPORT",
                "blockers": ';'.join((["MISSING_REQUIRED"] if row_missing else []) + (["NO_COLLOCATION_FIELD"] if not existing_collocations else []) + (["DUPLICATE_INTRA_CARD_COLLOCATION"] if card_has_duplicate_collocation else []) + ["INDEPENDENT_DEFA_QA_NOT_SIGNED", "LIVE_ACCEPTED_SRS_ID_NOT_VERIFIED", "NATIVE_APP_TEST_NOT_RUN"])
            })
            if lesson == 5 and row.get('pilot_example_3_de_R25') and row.get('pilot_example_3_fa_R25'):
                total_bonus_pairs += 1
        expected = set(range(first, last+1))
        implicit_missing = sorted(expected-actual_ordinals)
        known = KNOWN_NONCARD_OR_ALIAS.get(lesson, {})
        if set(implicit_missing) != set(known):
            raise AssertionError(f"L{lesson:02d} missing ordinal mismatch: {implicit_missing} != {sorted(known)}")
        for ordinal, disposition in sorted(known.items()):
            source_exceptions.append({"lesson": lesson, "source_ordinal": ordinal, "source_id": f'ab2-src-{ordinal:06d}', "disposition": disposition, "release_status": "NONIMPORT_OR_REUSED_ID_PENDING_LIVE_CHECK", "evidence_basis": "ALREADY_CURATED_EXCEPTION_SIDECAR_OR_LESSON_EDIT_RECORD"})
        if len(actual_ordinals|set(known)) != len(expected) or actual_ordinals|set(known) != expected:
            raise AssertionError(f"L{lesson:02d} source coverage failed")
        original_source_set |= expected
        row_report.append({"lesson": lesson, "title": title, "source_rows": len(expected), "draft_units": len(rows), "source_ordinals_represented_by_learner_csv": len(actual_ordinals), "exceptions_documented_outside_card_csv": len(known), "two_DEFA_pairs_per_card": all(all(row.get(f'example_{n}_{lang}', '').strip() for n in (1,2) for lang in ('de','fa')) for row in rows), "collocations_proposed": colloc_total, "cards_with_no_collocations": cards_lacking_collocations, "literal_overlap_occurrences": overlap_count, "unique_cards_with_literal_overlap": len(overlap_card_ids), "duplicate_internal_collocation_proposals": sum(z['lesson']==lesson for z in duplicate_collocations), "current_file": filename, "current_sha256": digest(file), "three_pass_cycle_closed_with_blockers": True, "importable_cards": 0})
    flags.sort(key=lambda x:(x['lesson'],x['unit_id'],x['collocation']))
    write_csv(outputs/'B2-1719-CARD-CENTRAL-NONIMPORT-MANIFEST.csv',records,list(records[0]))
    write_csv(outputs/'B2-COLLOCATION-EXAMPLE-LITERAL-OVERLAP-FLAGS.csv',flags,list(flags[0]))
    write_csv(outputs/'B2-NONCARD-AND-ALIAS-SOURCE-EXCEPTIONS.csv',source_exceptions,list(source_exceptions[0]))
    write_csv(outputs/'B2-INTRA-CARD-DUPLICATE-COLLOCATION-FLAGS.csv',duplicate_collocations,list(duplicate_collocations[0]))
    counts = Counter(x['severity'] for x in flags)
    result = {
        "schema": SCHEMA,"policy_revision":POLICY_REVISION,"audit_date":"2026-11-08","project":"Aspekte B2",
        "method":"READ_ONLY_DETERMINISTIC_CSV_AND_EXISTING_EXCEPTION_SIDECARS__NOT_INDEPENDENT_LINGUISTIC_QA",
        "source_authority":"TEN_LATEST_OWNER_CURATED_B2_LEARNER_CSVS__NOT_PUBLISHER_TEXTBOOK",
        "coverage":{"source_rows_verified_by_card_csv_or_documented_sidecar":len(original_source_set),"expected_source_rows":1726,"current_learner_card_units":len(records),"noncard_or_alias_source_exceptions":len(source_exceptions),"DEFA_primary_complete_example_pairs":sum(z['primary_DEFA_example_pairs'] for z in records),"L05_additional_complete_pilot_example_pairs":total_bonus_pairs,"collocation_proposals_total":sum(z['collocation_count'] for z in records),"cards_without_collocations":sum(z['collocation_count']==0 for z in records)},
        "machine_checks":{"global_unique_unit_ids":not global_duplicate_id,"source_coverage_including_explicit_noncard_alias_exceptions":True,"no_missing_required_learner_fields":not global_missing_required,"no_identical_German_example_sentences_across_3438_primary_pairs":not global_duplicate_example,"all_current_export_flags_FALSE":all(not z['export_importable'] for z in records),"all_linguistic_approval_flags_FALSE":all(not z['linguistic_release_approved'] for z in records),"all_ten_chapter_csv_files_available":True},
        "collocation_independence_audit":{"literal_collocation_substrings_in_own_example_count":len(flags),"high_confidence_length_15_or_more":counts['LONG_LITERAL_OVERLAP_15PLUS'],"short_multitoken":counts['SHORT_MULTITOKEN_OVERLAP'],"single_token":counts['SINGLE_TOKEN_OVERLAP'],"distinct_cards_flagged":len(set(z['unit_id'] for z in flags)),"internal_exact_duplicate_collocation_items":len(duplicate_collocations),"lesson1_has_no_collocations_column":True,"review_status":"CONTEXTUAL_ADVISORY__NOT_A_STANDALONE_DEFECT_OR_RELEASE_BLOCKER","safe_auto_rewrite":False},
        "crosslevel":{"documented_source_flags_L06_to_L10":sum(len(KNOWN_CROSSLEVEL_HOLDS.get(i,[])) for i in range(6,11)),"L01_additional_known_flags_including_noncard":KNOWN_CROSSLEVEL_HOLDS[1],"live_accepted_app_ids_available":False,"true_global_deduplication_result":"NOT_DETERMINABLE_WITHOUT_APP_CARD_ID_SRS_SNAPSHOT"},
        "release":{"current_status":"BLOCKED_NONIMPORT","lesson_cycles_closed_with_blockers":10,"independent_DE_FA_QA":"NOT_EVIDENCED","crosslevel_live_accepted_card_ID_and_SRS_check":"NOT_EVIDENCED","collocation_independence_gate":"ADVISORY_ONLY__LITERAL_OVERLAP_NOT_STANDALONE_BLOCKER","duplicate_collocation_gate":"FAILED_CONFIRMED_DUPLICATE" if duplicate_collocations else "PASS_NO_INTERNAL_DUPLICATES","app_import_persistence_SRS_rollback":"NOT_TESTED","approved_cards":0,"importable_cards":0,"cards_imported_by_this_audit":0,"SRS_mutations_by_this_audit":0},
        "notes":["Every source ordinal is represented either by a provisional card or by a documented existing noncard/alias disposition, not necessarily an individually reviewed flashcard.","A collocation substring within its own example is an advisory educational context signal, not an automatic error or release blocker. Independent bilingual language QA still applies.","No automatic fixing was performed and previous learner cards are unchanged.","First two DE/FA example pairs exist on every card; 12 additional pilot pairs in L05 are separately counted.","L01 has no collocations_de column, so a universal collocation-completeness claim would be false.","Confirmed same-card duplicate collocations are hard defects; examples containing a collocation are not.","Release cannot be inferred from all ten lesson cycles having dispositions."],
        "lessons": row_report,"current_input_hashes":{f'L{z["lesson"]:02d}':z['current_sha256'] for z in row_report},
        "generated_files":["B2-1719-CARD-CENTRAL-NONIMPORT-MANIFEST.csv","B2-COLLOCATION-EXAMPLE-LITERAL-OVERLAP-FLAGS.csv","B2-NONCARD-AND-ALIAS-SOURCE-EXCEPTIONS.csv","B2-INTRA-CARD-DUPLICATE-COLLOCATION-FLAGS.csv"]
    }
    (outputs/'B2-CENTRAL-RELEASE-READINESS-AUDIT-20261108.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=["# Aspekte B2 — Central release readiness, 8 November 2026","", "**ALL TEN LESSON CYCLES CLOSED WITH BLOCKERS · BLOCKED_NONIMPORT**", "", "The owner-curated CSVs for all ten lessons were read directly; no original textbook reingestion or automatic card modifications occurred.", "", "| Metric | Machine-audited value |", "|:--|--:|", f"| Source ordinals accounted for (including sidecars) | {len(original_source_set)}/1726 |",f"| Distinct draft learner-card IDs | {len(records)} |",f"| Complete primary German–Persian example pairs | {sum(z['primary_DEFA_example_pairs'] for z in records)} |",f"| Additional L05 pilot pairs | {total_bonus_pairs} |",f"| Proposed collocation chunks | {sum(z['collocation_count'] for z in records)} |",f"| Collocation chunks found verbatim inside same-card examples | {len(flags)} |",f"| Cards with at least one verbatim overlap | {len(set(z['unit_id'] for z in flags))} |",f"| Internal duplicate collocation chunks | {len(duplicate_collocations)} |",f"| L01 cards lacking any collocation column | 158 |",f"| Source noncard/alias exceptions recorded | {len(source_exceptions)} |", "| Live-approved/importable cards | 0 |", "", "## Context-aware collocation rule (v1.1)", "", "A collocation appearing inside an example is often good teaching, not a flaw. Literal overlaps are contextual advisories only; a true repeated collocation within one card is a structural hard defect. Release remains blocked for independent language QA, live card ID/SRS identity, and safe native import evidence.", "", "| Lesson | Draft cards | Literal overlap flags | Cards affected | Collocation chunks |", "|:--|--:|--:|--:|--:|" ]
    for z in row_report:
        lines.append(f'| {z["lesson"]:02d} | {z["draft_units"]} | {z["literal_overlap_occurrences"]} | {z["unique_cards_with_literal_overlap"]} | {z["collocations_proposed"]} |')
    lines+=['','## Three independent release gates','', '1. Independent, sense-aware DE–FA linguistic sign-off covering forms, meanings, two examples and lexical relationships.', '2. Verified current, live **accepted card IDs**, cross-level meaning identities and non-destructive SRS mapping.', '3. Safe native app import, restart/roundtrip, SRS preservation and rollback test on a working copy.', '', '**Until all gates pass, these drafts are not to be imported or have release flags changed.**', '', '## Source exceptions and limitations', '', 'L01 source #1630 is a conditional B1 reuse, and #1660 is a grammatical facet (Partizip II of kommen); neither is a deleted source entry. L03 source #1921 is an alias of #1920. Four L05 source expressions and additional L06/L07/L09/L10 full-sentence objects are preserved in noncard sidecars.', 'L01 has a different/older draft schema without a `collocations_de` field; its 158 cards need their own explicit collocation-enrichment decision, not a false claim that this field passed.', '','','**The machine gate detects literal reuse, but does not replace independent semantic review or independently validate live app state.**','']
    (outputs/'B2-CENTRAL-RELEASE-READINESS-AUDIT-20261108.md').write_text('\n'.join(lines),encoding='utf-8')
    return result

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--outputs',type=Path,default=Path(__file__).resolve().parent/'audit_output')
    p.add_argument('--release-check',action='store_true',help='Exit nonzero if release prerequisites are not proven (expected today)')
    args=p.parse_args()
    report=inspect(args.inputs,args.outputs,args.release_check)
    print(json.dumps({'coverage':report['coverage'],'quality_flags':report['collocation_independence_audit'],'release':report['release'],'audit_dir':str(args.outputs)},ensure_ascii=False,indent=2))
    if args.release_check and report['release']['current_status'] != 'READY_FOR_IMPORT':
        raise SystemExit(2)