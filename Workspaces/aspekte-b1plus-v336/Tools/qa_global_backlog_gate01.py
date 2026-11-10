#!/usr/bin/env python3
"""Fail-closed global structural QA for B1+ learner archives (not semantic approval).

Usage: python qa_global_backlog_gate01.py CURATED_OWNER.zip
Every run checks the CURRENT primary JSONL inside that ZIP. It does not recreate
obsolete publisher data, auto-approve content, or modify the archive.
"""
import json, re, sys, zipfile, hashlib
from collections import Counter

PRIMARY = "G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl"
SOURCE_MAP = "G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv"
DETERMINERS = {"der","die","das","ein","eine","einen","einem","einer","diese","dieser","dieses","jener","jene"}
FINITE = {"reicht","entscheidet","koordiniert","läuft","prüft","schreibt","bringt","bestimmt","öffnet","organisiert","führt","hat","ist","sind","steht","arbeitet","verwendet","liefert","besucht","zeichnet","braucht","stellt","kommt","zeigt","hält","macht","kann","wird","werden","nimmt","bietet","spricht"}
def sha(data): return hashlib.sha256(data).hexdigest()

def validate(path):
    issues = []
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad: raise AssertionError("ZIP_CRC_FAILURE " + bad)
        manifest = z.read("SHA256SUMS.txt").decode().splitlines()
        for line in manifest:
            digest, name = line.split("  ", 1)
            if sha(z.read(name)) != digest: raise AssertionError("MANIFEST_SHA_MISMATCH " + name)
        cards = [json.loads(line) for line in z.read(PRIMARY).splitlines()]
        source_map = z.read(SOURCE_MAP)
    if len(cards) != 1571: issues.append("NOT_1571_CARDS")
    ids = [c.get("preview_card_id") for c in cards]
    if len(ids) != len(set(ids)): issues.append("DUPLICATE_CARD_IDS")
    if len({(c.get("lesson"),c.get("source_ordinal")) for c in cards if c.get("source_ordinal")}) < 1500:
        issues.append("SUSPICIOUS_SOURCE_ORDINAL_COVERAGE")
    count_example = 0
    for c in cards:
        if c.get("import_ready") or c.get("formal_release_approved"):
            issues.append(f"PREMATURE_RELEASE:{c.get('source_ordinal')}")
        back=c.get("back") or {}
        if back.get("Formen_section") is not None:
            issues.append(f"REDUNDANT_BACK_FORMEN:{c.get('source_ordinal')}")
        networks=back.get("semantic_network_sense_anchored_pending_qa") or []
        sense_ids={s.get("sense_id") for s in networks}
        if None in sense_ids: issues.append(f"EMPTY_NETWORK_SENSE:{c.get('source_ordinal')}")
        for field in ("existing_examples_de_fa_pending_qa","additional_examples_de_fa_pending_qa"):
            for e in back.get(field) or []:
                count_example += 1
                if not e.get("de") or not e.get("fa"):
                    issues.append(f"EMPTY_BILINGUAL_EXAMPLE:{c.get('source_ordinal')}")
                if not e.get("status"):
                    issues.append(f"MISSING_QA_STATUS:{c.get('source_ordinal')}")
                if networks and e.get("sense_id") not in sense_ids:
                    issues.append(f"ORPHAN_EXAMPLE_SENSE:{c.get('source_ordinal')}")
                if e.get("sense_ids"):
                    mult=e["sense_ids"]
                    if (len(mult)!=len(set(mult)) or not set(mult).issubset(sense_ids)
                            or e.get("sense_id") not in mult):
                        issues.append(f"INVALID_MULTISENSE_ROUTING:{c.get('source_ordinal')}")
        for s in networks:
            for p in s.get("Kombinationen_DE_FA") or []:
                de=p.get("de","")
                if not de.strip() or not p.get("fa","").strip():
                    issues.append(f"EMPTY_COLLOCATION:{c.get('source_ordinal')}")
                words=re.findall(r"\w+",de)
                if len(words)>=4 and words[0].casefold() in DETERMINERS and words[1][0].isupper() and words[2].casefold() in FINITE:
                    issues.append(f"FINITE_CLAUSE_AS_COLLOCATION:{c.get('source_ordinal')}")
    report={"schema":"aspekte-b1plus-global-structural-qa@1","card_count":len(cards),
            "source_map_sha256":sha(source_map),"examples":count_example,
            "missing_or_invalid_items":issues,
            "strict_structural_pass":not issues,
            "limits":"Finite detector is non-exhaustive. Structural PASS never certifies semantic, translation, morphology, app importer, or release."}
    return report

if __name__ == "__main__":
    result=validate(sys.argv[1])
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if result["strict_structural_pass"] else 1)
