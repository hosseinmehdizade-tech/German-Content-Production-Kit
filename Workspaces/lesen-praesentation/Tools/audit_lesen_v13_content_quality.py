#!/usr/bin/env python3
"""Read-only source-native Lesen v1.3.0 pedagogical repetition audit.
Does not certify semantic Stage4 or mutate user content.
"""
import argparse, collections, csv, hashlib, json, pathlib, zipfile
from datetime import date

MASTER_MEMBER='01-Final-Content/Lesen-Production-Master-v1.3.0.json'
REPEATED_QUESTION_THRESHOLD=20
REPEATED_SENTENCE_THRESHOLD=10


def audit(archive: pathlib.Path):
    archive_bytes=archive.read_bytes()
    sha=hashlib.sha256(archive_bytes).hexdigest()
    with zipfile.ZipFile(archive) as z:
        master_bytes=z.read(MASTER_MEMBER)
        master=json.loads(master_bytes)
    units=master['items']
    prompts=collections.defaultdict(list)
    answers=collections.defaultdict(list)
    sentences=collections.defaultdict(list)
    sections=collections.defaultdict(list)
    by_id={u['id']:u for u in units}
    for unit in units:
        uid=unit['id']
        for q in unit['questions']:
            prompts[q['prompt_de']].append((uid,q['id'],q['type']))
            answers[q['answer_de']].append((uid,q['id'],q['type']))
        for s in unit['reading']['sections']:
            sections[s['text']].append((uid,s['id']))
            for sentence in s['sentences']:
                sentences[sentence['text']].append((uid,s['id'],sentence['id']))

    repeated_prompts={p:v for p,v in prompts.items() if len(v)>=REPEATED_QUESTION_THRESHOLD}
    repeated_answers={p:v for p,v in answers.items() if len(v)>=REPEATED_QUESTION_THRESHOLD}
    repeated_sentences={s:v for s,v in sentences.items() if len(v)>=REPEATED_SENTENCE_THRESHOLD}
    any_repeat_affected=sorted({uid for vs in repeated_prompts.values() for uid,*_ in vs})
    repeat_affected=sorted(uid for uid in any_repeat_affected if sum(q['prompt_de'] in repeated_prompts for q in by_id[uid]['questions'])>=3)
    partially_affected=sorted(set(any_repeat_affected)-set(repeat_affected))
    rows=[]
    for uid in repeat_affected:
        u=by_id[uid]
        qissues=[]
        for q in u['questions']:
            if q['prompt_de'] in repeated_prompts:qissues.append({'id':q['id'],'type':q['type'],'reason':'PROMPT_HIGH_REUSE', 'occurrences':len(repeated_prompts[q['prompt_de']])})
            if q['answer_de'] in repeated_answers:qissues.append({'id':q['id'],'type':q['type'],'reason':'ANSWER_HIGH_REUSE', 'occurrences':len(repeated_answers[q['answer_de']])})
        sent_count=sum(1 for sec in u['reading']['sections'] for ss in sec['sentences'] if ss['text'] in repeated_sentences)
        exact_section_count=sum(1 for sec in u['reading']['sections'] if len(sections[sec['text']])>1)
        rows.append({'unit_id':uid,'title_de':u['title_de'],'shared_question_issue_count':len(qissues),'shared_sentence_occurrences_threshold10':sent_count,'repeated_full_sections':exact_section_count,'severity':'EDITORIAL_REVIEW_REQUIRED_NOT_INVALIDATED','question_issues':qissues})
    high_freq_prompts=[{'text':k,'count':len(v),'unit_ids':[t[0] for t in v]} for k,v in sorted(repeated_prompts.items(),key=lambda kv:(-len(kv[1]),kv[0]))]
    high_freq_answers=[{'text':k,'count':len(v)} for k,v in sorted(repeated_answers.items(),key=lambda kv:(-len(kv[1]),kv[0]))]
    high_freq_sentences=[{'text':k,'count':len(v)} for k,v in sorted(repeated_sentences.items(),key=lambda kv:(-len(kv[1]),kv[0]))]
    all_repeated_groups=[v for v in sentences.values() if len(v)>1]
    return {
      'schema':'lesen-v13-quality-repetition-audit@1.0.0',
      'audit_date':'2026-11-07','audit_scope':'ALL_68_UNITS_DETERMINISTIC_TEXT_DUPLICATION_AND_SPOT_SEMANTIC_REVIEW',
      'artifact_sha256':sha,'master_sha256':hashlib.sha256(master_bytes).hexdigest(),
      'unit_count':len(units),'question_count':sum(len(u['questions']) for u in units),
      'sentence_count':sum(len(s['sentences']) for u in units for s in u['reading']['sections']),
      'unique_sentences':len(sentences),
      'sentence_extra_duplicates':sum(len(v)-1 for v in all_repeated_groups),
      'sentence_occurrences_in_repeated_groups':sum(map(len,all_repeated_groups)),
      'exact_reused_section_groups':sum(1 for v in sections.values() if len(v)>1),
      'units_with_any_repeated_sentences':len({uid for v in all_repeated_groups for uid,*_ in v}),
      'high_reuse_question_threshold':REPEATED_QUESTION_THRESHOLD,
      'high_reuse_sentence_threshold':REPEATED_SENTENCE_THRESHOLD,
      'high_reuse_affected_units':len(rows),'high_reuse_affected_unit_ids':repeat_affected,
      'single_shared_prompt_only_units':partially_affected,
      'high_reuse_questions':high_freq_prompts,'high_reuse_answers':high_freq_answers,
      'high_reuse_sentences':high_freq_sentences,
      'review_queue':rows,
      'verified_targeted_examples':[
       {'unit':'LES-PRES-051','issue':'QUESTION_SEMANTIC_SCOPE_MISMATCH','question':'Welche zwei Argumente sprechen im Text für eine positive Bewertung?','why':'Text discusses causes of male underrepresentation; a positive valuation is not the asked scientific causal question. Repeated sentence "Dadurch kann ein Nutzen entstehen" is semantically misaligned with this causal section.','proposal':'Welche Gründe für die ungleiche Geschlechterverteilung in technischen Studiengängen werden genannt?','proposal_status':'REVIEW_ONLY_NOT_APPLIED'},
       {'unit':'LES-PRES-059','issue':'QUESTION_SPECIFICITY','question':'Welche zwei Argumente sprechen im Text für eine positive Bewertung?','why':'Question does not identify what is evaluated; section debates self-organization requirement of distance education.','proposal':'Welche Anforderungen an die Selbstorganisation und welche Vorteile des Fernstudiums nennt der Text?','proposal_status':'REVIEW_ONLY_NOT_APPLIED'},
       {'unit':'LES-PRES-035','issue':'QUESTION_SPECIFICITY','question':'Warum spielt die konkrete Ausgestaltung eine so wichtige Rolle?','why':'Generic question and identical answer appear in 58 lessons; does not test device-specific constraints in sections p04–p05.','proposal':'Welche Bedingungen müssen Schulen erfüllen, damit digitale Geräte den Unterricht sinnvoll unterstützen?','proposal_status':'REVIEW_ONLY_NOT_APPLIED'}
      ],
      'boundaries':['Repeated educational templates are risk signals, not proof every use is factually wrong','No wholesale linguistic Stage4 PASS; targeted samples only','No content bytes, runtime, UI, SRS/FSRS or source changed','No publisher fidelity equality requirement','Do not auto-generate replacements or rewrite immutable source']
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('archive',type=pathlib.Path)
    ap.add_argument('--json-report',type=pathlib.Path,required=True)
    ap.add_argument('--csv-queue',type=pathlib.Path,required=True)
    args=ap.parse_args()
    report=audit(args.archive)
    args.json_report.parent.mkdir(parents=True,exist_ok=True)
    args.json_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with args.csv_queue.open('w',encoding='utf-8',newline='') as f:
      wr=csv.DictWriter(f,fieldnames=['unit_id','title_de','shared_question_issue_count','shared_sentence_occurrences_threshold10','repeated_full_sections','severity'])
      wr.writeheader();wr.writerows({key:row[key] for key in wr.fieldnames} for row in report['review_queue'])
    print(json.dumps({k:report[k] for k in ['unit_count','question_count','sentence_count','unique_sentences','sentence_extra_duplicates','sentence_occurrences_in_repeated_groups','exact_reused_section_groups','high_reuse_affected_units']},indent=2))
    print('QA HOLD: pedagogical duplication: no content auto-edit')

if __name__=='__main__':main()