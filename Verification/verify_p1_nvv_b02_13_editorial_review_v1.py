#!/usr/bin/env python3
"""Independent, nonpublishing verification of NVV B02 Stage3 evidence review.

The 100-card parent baseline has already been authenticated by the Library
provider. GitHub CI sees review metadata and the owner recovery receipt, not
private Library card bytes. Never infer owner Stage4 acceptance from review.
"""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REVIEW="Optimization-Program/Verification/P1-NVV-B02-13-OWNER-PROPOSAL-EDITORIAL-REVIEW-NONIMPORT-20261105.json"
QA="Optimization-Program/Verification/P1-NVV-B02-13-OWNER-PROPOSAL-INDEPENDENT-QA-NONIMPORT-20261105.json"
OWNER="Workspaces/nomen-verb-verbindungen/B02-SOURCE-FIRST-RECOVERY-20261105.json"
OWNER_BLOB="bc50c938ed83486523cf2c96cab9da03b33896dd"
BASE_SHA="c2d64272971030978e457a5c57e21249a838add8717e1c0b96b1510a28b7d821"
ORIGINAL_LOST="f604f265ea1483d800590f5a66adef99abbdb574240171db777201eaacaee96e"
class VerifyError(ValueError):pass
def check(v,code):
    if not v:raise VerifyError(code)
def read_bytes(root,p):
    path=root/p
    check(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),"FILE_MISSING_OR_UNSAFE")
    return path.read_bytes().replace(b"\r\n",b"\n")
def git_sha(blob):
    return hashlib.sha1(b"blob "+str(len(blob)).encode("ascii")+b"\0"+blob).hexdigest()
def sha(blob):
    return hashlib.sha256(blob).hexdigest()
def verify(root=ROOT,report=None,qa=None):
    root=Path(root)
    ob=read_bytes(root,OWNER)
    check(git_sha(ob)==OWNER_BLOB,"OWNER_BLOB_DRIFT")
    owner=json.loads(ob)
    rb=read_bytes(root,REVIEW)
    qb=read_bytes(root,QA)
    r=report if report is not None else json.loads(rb)
    q=qa if qa is not None else json.loads(qb)
    check(r.get("schema")=="nvv-b02-stage3-candidate-editorial-evidence-review@1.0.0" and
          r.get("status")=="PASS_13_CANDIDATES_EDITORIALLY_TRIAGED_9_LEXICAL_4_EXISTING_RELATIONS__163_EXTERNALLY_ATTESTED_ORIGINAL_HOLD_REMAINS__NOT_STAGE4","REVIEW_SCOPE_FALSE")
    check(q.get("schema")=="nvv-b02-stage3-independent-editorial-qa@1.0.0" and
          q.get("status")=="PASS_SOURCE_BOUND_OWNER_13_OF_13_REVIEWED_11_DISPOSITIONS_UNMODIFIED_NOT_STAGE4","QA_SCOPE_FALSE")
    check(r["authority"]["original_parent_baseline_sha256"]==q["source_baseline_sha256"]==BASE_SHA and
          r["authority"]["source_owner_git_blob"]==OWNER_BLOB and
          r["authority"]["source_owner_missing_working_sha256"]==ORIGINAL_LOST and
          r["authority"]["source_original_pdf_not_reverified"] is True,
          "PARENT_OR_ORIGINAL_SOURCE_DRIFT")
    if report is None:
        check(q["editorial_report_sha256"]==sha(rb),"QA_REPORT_SHA_DRIFT")
    count=r["counts"]
    check(count["base_cards_checked"]==100 and
          count["owner_proposals_triaged"]==len(owner["proposed"])==len(r["candidates"])==13 and
          count["owner_dispositions_recorded_unchanged"]==len(owner["dispositions"])==len(r["dispositions"])==11 and
          count["existing_relation_links_without_new_cards"]==4 and
          count["external_lexical_or_combination_candidates"]==9 and
          count["draft_examples_new_nonimport"]==10 and
          count["owner_open_holds"]==1 and
          all(count[key]==0 for key in ("new_cards_approved","source_card_mutations","stage4_acceptance","adopted_producers")),
          "FALSE_COUNTS_OR_ADOPTION")
    flags=r["safety"]
    check(all(v is True for v in flags.values()) and
          q["checks"] and all(v is True for v in q["checks"].values()),"FALSE_PRESERVATION_CLAIM")
    check(q["reviewed_count"]==13 and q["owner_dispositions_count"]==11 and
          q["original_holder_position_163"]["owner_hold_unresolved"] is True and
          q["original_holder_position_163"]["external_phrase_direct_attested"] is True,
          "OWNER_HOLD_FALSE")
    index={(p["position"],p["section"],p["term_de"]):p for p in owner["proposed"]}
    reviewkeys={(p["position"],p["section"],p["term_de"]) for p in r["candidates"]}
    check(set(index)==reviewkeys and len(reviewkeys)==13,"EDITORIAL_OWNER_PROPOSAL_MISMATCH")
    links=[]
    for p in r["candidates"]:
        old=index[(p["position"],p["section"],p["term_de"])]
        check(p["relationship_target_position"]==old["related_target_position"] and
              p["source_owner_stage4"]==old["stage4"]=="PENDING" and
              old["graph_mutation"] is False and
              p["card_write_authorized"] is False and p["relation_write_authorized"] is False and
              p["formal_stage3_content_acceptance"] is False,
              "FORGED_EDITORIAL_PROMOTION")
        check(p["card_id"]==f'dah-nvv-exp-{p["position"]-2:05d}' and
              re.fullmatch(r"[a-f0-9]{64}",p["card_base_sha256"]) and
              q["source_existing_parent_hashes"][f'{p["position"]}:{p["term_de"]}']==p["card_base_sha256"],
              "SOURCE_CARD_HASH_OR_ID_DRIFT")
        check(p["evidence_scope"]=="EXTERNAL_LEXICAL_NOT_ORIGINAL_NVV_PDF" and
              p["external_evidence_url"].startswith("https://") and
              not p["external_evidence_url"].startswith("https://fake."),
              "SOURCE_SCOPE_OR_LEXICAL_REFERENCE_FALSE")
        if p["relationship_target_position"] is not None:
            check(p["editorial_assessment"]=="EXISTING_TARGET_RELATION_ONLY" and
                  p["relationship_target_canonical_form"]==p["term_de"] and
                  p["relationship_target_id"]==f'dah-nvv-exp-{p["relationship_target_position"]-2:05d}' and
                  p["optional_new_example_DRAFT_DE_FA_EN"] is None,
                  "DUPLICATE_CANONICAL_TARGET_CARD")
            links.append(p["relationship_target_position"])
        else:
            check(p["editorial_assessment"] in ("EXTERNAL_LEXEME_EDITORIAL_CANDIDATE","EXACT_PHRASE_EXTERNAL_EDITORIAL_CANDIDATE") and
                  set(p["optional_new_example_DRAFT_DE_FA_EN"])=={"de","fa","en"},
                  "NONLINK_DRAFT_EXAMPLE_MISSING")
    check(sorted(links)==[124,148,159,166]==sorted(q["duplicate_relation_target_positions"]),
          "RELATED_GRAPH_CARD_TARGETS_DRIFT")
    check({p["position"] for p in r["candidates"] if p["term_de"]=="beanspruchen"}=={143,144} and
          q["lexical_distinct_senses"]=={"beanspruchen_143":"rights_claim","beanspruchen_144":"usage_and_resource_load"},
          "BEANSPRUCHEN_SENSE_COLLAPSE")
    ds={(d["position"],d["term_de"]):d for d in owner["dispositions"]}
    got={(d["position"],d["term_de"]):d for d in r["dispositions"]}
    check(set(ds)==set(got),"OWNER_DISPOSITION_COUNT_DRIFT")
    for key,d in got.items():
        check(d["source_owner_decision_unchanged"]==ds[key]["decision"] and
              d["source_owner_redecision_made"] is False,"OWNER_DISPOSITION_MUTATED")
    h=got[(163,"eine Anzahlung auf den Kaufpreis leisten")]
    ev=h["new_external_attestation"]
    check(h["source_owner_decision_unchanged"]=="HOLD_DIRECT_PHRASE_EVIDENCE" and
          ev["exact_phrase"]=="eine Anzahlung auf den Kaufpreis leisten" and
          ev["status"]=="EXACT_PHRASE_ATTESTED_IN_A_QUESTION_NOT_STAGE4_APPROVAL" and
          ev["original_hold_remains"] is True and
          ev["proposed_next_owner_decision"]=="REVIEW_HOLD_FOR_EDITORIAL_REEVALUATION_NOT_AUTOCLOSE" and
          ev["url"]=="https://www.afi-auktion.de/de/auktionen/fragenkaufen.html",
          "EXTERNAL_ATTESTATION_FALSE_STAGE4")
    return {"status":"PASS_13_EDITORIAL_PROPOSALS_AND_11_DISPOSITIONS_PINNED_NOT_STAGE4","sources":13,"new_lexical_candidates_not_approved":9,"existing_relation_links_no_card_clone":4,"unresolved_original_hold_163":1,"cards_approved":0,"P1_ADOPTED":0,
            "limitations":"Git CI validates owner/review metadata only; private Library base bytes and web evidence checked outside CI"}
def main():
    try: result=verify()
    except (VerifyError,KeyError,TypeError,ValueError,OSError,UnicodeError) as exc:
        print("P1_NVVB02_EDITORIAL_REVIEW_DENIED:"+str(exc),file=sys.stderr)
        return 2
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return 0
if __name__=="__main__":raise SystemExit(main())
