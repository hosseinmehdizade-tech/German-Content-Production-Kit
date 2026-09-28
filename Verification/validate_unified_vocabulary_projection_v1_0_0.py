#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

NEUTRAL = "de-vocabulary"

def load_rows(path: Path):
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("cards"), list):
            data = data["cards"]
        if not isinstance(data, list):
            raise ValueError("JSON projection must be a card list or {cards:[...]} object")
        return data
    if path.suffix.lower() in {".tsv", ".txt"}:
        with path.open(encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f, delimiter="\t"))
    raise ValueError("supported projection formats: JSON or TSV")

def card_type(row):
    return str(row.get("cardType") or row.get("card_type") or "").strip()

def validate(rows):
    errors=[]; legacy=[]; missing=[]
    for i,row in enumerate(rows, start=1):
        cid=str(row.get("id") or f"row:{i}")
        ct=card_type(row)
        if not ct:
            missing.append(cid); errors.append({"id":cid,"error":"MISSING_CARD_TYPE"})
        elif ct != NEUTRAL:
            legacy.append({"id":cid,"card_type":ct})
            errors.append({"id":cid,"error":"NON_NEUTRAL_VOCABULARY_ENVELOPE","card_type":ct,"expected":NEUTRAL})
        category=str(row.get("category") or "").strip()
        if not category:
            errors.append({"id":cid,"error":"MISSING_SEMANTIC_CATEGORY"})
    return {"status":"PASS" if not errors else "FAIL","cards":len(rows),"neutral_card_type":NEUTRAL,"legacy_or_non_neutral":legacy,"missing_card_type":missing,"errors":errors}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("projection"); a=ap.parse_args()
    path=Path(a.projection); result=validate(load_rows(path)); result["input"]=str(path)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)

if __name__=="__main__":
    main()
