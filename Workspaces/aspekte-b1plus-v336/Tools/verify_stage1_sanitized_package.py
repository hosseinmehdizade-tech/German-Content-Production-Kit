#!/usr/bin/env python3
"""Verify a user's PRIVATE, nonimport Stage1 Aspekte B1+ ZIP. Never print raw learner rows."""
import argparse,csv,hashlib,io,zipfile,re
from collections import Counter

ARCHIVE_SHA="8f4c2b76cbd1c6b8bce66c052e26092bb66b64a70a91478f6d4aa140022636c1"
SOURCE_SHA="cca32df935397a81367b38f9b51ee33aac357ea135947a131b712969f0339033"
LESSON_COUNTS={1:71,2:91,3:195,4:158,5:156,6:175,7:153,8:157,9:185,10:207}
HEADERS=["source_csv_ordinal","Learnable","Definition","Audio","Beispiel","Level tags"]
def digest(raw): return hashlib.sha256(raw).hexdigest()
def verify(path):
    raw=open(path,"rb").read()
    assert digest(raw)==ARCHIVE_SHA,"STAGE1_ZIP_SHA_MISMATCH"
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None,"ZIP_CRC_FAIL"
        members=set(z.namelist())
        manifest=z.read("SHA256SUMS").decode("utf-8").splitlines()
        assert len(manifest)==len(members)-1
        seen=set()
        for line in manifest:
            h,name=line.split("  ",1)
            assert name in members and name not in seen
            assert digest(z.read(name))==h, "ZIP_MEMBER_SHA_FAIL:"+name
            seen.add(name)
        s=z.read("Source/Aspekte-B1plus-CSV-ONLY-SOURCE-SANITIZED.csv")
        assert digest(s)==SOURCE_SHA,"SANITIZED_SHA_MISMATCH"
        rows=list(csv.DictReader(io.StringIO(s.decode("utf-8-sig"),newline="")))
        assert len(rows)==1548
        assert list(rows[0])==HEADERS,"UNEXPECTED_FIELDS"
        assert [int(x["source_csv_ordinal"]) for x in rows]==list(range(1,1549))
        assert len(set(x["Learnable"] for x in rows))==1541
        assert sum(bool(x["Beispiel"].strip()) for x in rows)==224
        assert sum(bool(x["Audio"].strip()) for x in rows)==1375
        counts=Counter()
        for x in rows:
            m=re.fullmatch(r"Aspekte_B1[+]/B2::([0-9]{2})_B1[+]:_(10|[1-9])_–_(.+)", x["Level tags"])
            assert m,"UNEXPECTED_LEVEL_TAG"
            section,lesson=int(m.group(1)),int(m.group(2))
            assert section in (2*lesson-1,2*lesson)
            counts[lesson]+=1
        assert dict(counts)==LESSON_COUNTS
        ledger=list(csv.DictReader(io.StringIO(z.read("Content/ASPEKTE-B1PLUS-STAGE1-ALL-1548-SOURCE-LEDGER.csv").decode(),newline="")))
        assert len(ledger)==1548
        assert len({x["b1plus_source_id"] for x in ledger})==1548
        assert all(x["row_decision"]=="HOLD_PENDING_STAGE2" for x in ledger)
        assert all(ledger[i]["Learnable_exact"]==rows[i]["Learnable"] and ledger[i]["Definition_exact"]==rows[i]["Definition"] for i in range(1548))
        assert len(list(csv.DictReader(io.StringIO(z.read("Content/L01-71-SOURCE-ONLY-NONIMPORT.csv").decode(),newline=""))))==71
    print("PASS: byte-exact archive, member SHA, 1548 sanitized source rows, 10 lessons, L01 71, no import status.")
    print("NOT VERIFIED: original 3275-row unredacted CSV SHA; Stage2 semantics; real MP3; importer.")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("zip_path")
    args=p.parse_args()
    verify(args.zip_path)
