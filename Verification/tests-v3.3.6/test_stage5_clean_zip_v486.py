"""OP-02: ACTUAL existing clean Stage5 builder + post-ZIP v486 semantic checks.

Two original synthetic cards; all ZIP files are local pytest temp files and
never committed or uploaded. Synthetic 'AI review' is only a shape fixture.
"""
from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

VERIFICATION = Path(__file__).resolve().parents[1]
ROOT = VERIFICATION.parent
sys.path.insert(0, str(VERIFICATION))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_stage5_clean_zip_v486 import audit, sha, ROOT as ZROOT
from validate_stage45_teaching_delta_parity import SCHEMA as STAGE45_SCHEMA
from validate_stage45_v486_consumer_bridge import (
    SCHEMA as BRIDGE_SCHEMA, RUNTIME_SHA, RUNTIME, VIEW_FUNCTION, READ_FUNCTION,
)
from test_stage45_v486_consumer_bridge import source, json_bytes, tsv_bytes

DIRECT = "Synthetic-Universal.tsv"
CANON = "Synthetic-canonical.json"
MAP = "Synthetic-source-output-map.tsv"
QA = "Synthetic-QA.json"
DELIVERY = "DELIVERY-MANIFEST.json"
SUMS = "SHA256SUMS.txt"


def package_members(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        return {i.filename: z.read(i.filename) for i in z.infolist()}


def repack(members):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    return stream.getvalue()


def fix_internal_sums(members):
    names = sorted(k for k in members if k != ZROOT + SUMS)
    members[ZROOT+SUMS] = "".join(
        f"{sha(members[name])}  {name[len(ZROOT):]}\n"
        for name in names
    ).encode("utf-8")


@pytest.fixture
def built(tmp_path):
    a,b,rows = source()
    b4,bq,bt = json_bytes(a),json_bytes(b),tsv_bytes(rows)
    input_dir = tmp_path / "stage5-synthetic-input"
    input_dir.mkdir()
    (input_dir / DIRECT).write_bytes(bt)
    (input_dir / CANON).write_bytes(json_bytes({"cards":a["cards"]}))
    (input_dir / MAP).write_text("source_id\tcard_id\nsynthetic\tcase-1\n", encoding="utf-8")
    (input_dir / QA).write_bytes(json_bytes({"scope":"synthetic","status":"FIXTURE_NOT_REAL_QA"}))
    dest = tmp_path / "out"
    dest.mkdir()
    output = dest / "Stage5-Synthetic-Clean-Delivery.zip"
    run = subprocess.run(
        [sys.executable, str(ROOT/"Tools"/"build_clean_delivery.py"),
         str(input_dir), str(output), "--purpose", "stage5_acceptance"],
        capture_output=True, text=True, timeout=90,
    )
    assert run.returncode == 0, run.stdout+"\n"+run.stderr
    assert output.exists() and output.stat().st_size > 100
    assert json.loads(run.stdout)["status"] == "PASS"
    blob = output.read_bytes()
    proof = {
        "schema": STAGE45_SCHEMA, "status": "NONACTIVE_VERSIONED_DRY_RUN",
        "source_authority_sha256": "e"*64,
        "stage4_sha256": sha(b4),
        "stage4_review_sha256": sha(bq),
        "stage5_tsv_sha256": sha(bt),
    }
    view = {
        "schema": BRIDGE_SCHEMA, "status": "NONACTIVE_VERSIONED_DRY_RUN",
        "runtime_version": RUNTIME, "runtime_sha256": RUNTIME_SHA,
        "presentation_function": VIEW_FUNCTION,
        "tsv_parser_function": READ_FUNCTION, "stage5_tsv_sha256": sha(bt),
    }
    return {"zip":blob,"stage4":b4,"review":bq,"proof":proof,
            "bridge":view,"output":output,"input_dir":input_dir}


def checked(built, blob=None, mutate=None, new_zip_sha=None):
    docs = {"proof":dict(built["proof"]), "bridge":dict(built["bridge"])}
    if mutate:
        mutate(docs)
    data = built["zip"] if blob is None else blob
    expected = sha(data) if new_zip_sha is None else new_zip_sha
    return audit(data, expected, built["stage4"], built["review"],
                 docs["proof"], docs["bridge"])


def tamper(built, edit, resums=False):
    members = package_members(built["zip"])
    edit(members)
    if resums:
        fix_internal_sums(members)
    return repack(members)


def test_actual_existing_stage5_builder_real_output_sha_and_deep_parity(built):
    result = checked(built)
    assert result["status"] == "PASS_SCOPED_NONACTIVE_EXACT_PACKAGED_TSV_ONLY"
    assert result["card_count"] == 2
    assert result["packaged_member_count"] == 6
    assert result["semantic_profile"] == "PASS_SCOPED_DETERMINISTIC_CONSUMER_PROFILE_ONLY"
    assert result["packaged_tsv_sha256"] == built["proof"]["stage5_tsv_sha256"]


def test_exact_postbuild_tsv_bytes_are_identical_to_builder_input(built):
    members = package_members(built["zip"])
    assert members[ZROOT+DIRECT] == (built["input_dir"]/DIRECT).read_bytes()
    assert checked(built)["status"].startswith("PASS_SCOPED")


def test_wrong_whole_zip_sha_cannot_be_downgraded_to_manifest_pass(built):
    r = checked(built,new_zip_sha="0"*64)
    assert r["status"]=="BLOCKED"
    assert "EXACT_POSTBUILD_ZIP_SHA_MISMATCH" in r["errors"]


@pytest.mark.parametrize("file", [DIRECT,CANON,MAP,QA,DELIVERY])
def test_postbuild_bare_member_mutation_rejected_by_manifest_sha(built,file):
    data=tamper(built,lambda m: m.__setitem__(
        ZROOT+file,m[ZROOT+file]+b" "))
    r=checked(built,blob=data)
    assert r["status"]=="BLOCKED"
    assert "STAGE5_INTERNAL_SHA256SUMS_CONTENT_MISMATCH" in str(r["errors"])


def test_duplicate_member_refused_even_if_bytes_equal(built):
    b=io.BytesIO(built["zip"])
    contents=package_members(built["zip"])
    s=io.BytesIO()
    with zipfile.ZipFile(s,"w") as z:
        for name,body in contents.items(): z.writestr(name,body)
        with pytest.warns(UserWarning,match="Duplicate name"):
            z.writestr(ZROOT+DIRECT,contents[ZROOT+DIRECT])
    r=checked(built,blob=s.getvalue())
    assert "STAGE5_ZIP_INVENTORY_UNSAFE" in str(r["errors"])


def test_member_path_traversal_rejected(built):
    members=package_members(built["zip"])
    members["CONTENT-DELIVERY/../secret.txt"]=b"bad"
    r=checked(built,blob=repack(members))
    assert "STAGE5_ZIP_MEMBER_UNSAFE" in str(r["errors"])


def test_manifest_role_substitution_rejected_even_with_fresh_sums(built):
    def edit(m):
        p=ZROOT+DELIVERY
        j=json.loads(m[p]);j["roles"]["direct-import-tsv"]=QA
        m[p]=json.dumps(j).encode()
    r=checked(built,blob=tamper(built,edit,True))
    assert "STAGE5_ROLE_MISSING_OR_REUSED" in str(r["errors"])


def test_extra_unapproved_file_refused_even_with_valid_sums(built):
    r=checked(built,blob=tamper(
        built,lambda m: m.__setitem__(ZROOT+"EXTRA.txt",b"unapproved"),True))
    assert "STAGE5_UNEXPECTED_OR_MISSING_MEMBER" in str(r["errors"])


def test_missing_manifest_member_refused_even_with_fresh_sums(built):
    def edit(m):m.pop(ZROOT+CANON)
    r=checked(built,blob=tamper(built,edit,True))
    assert "STAGE5_ROLE_MISSING_OR_REUSED" in str(r["errors"])


def patch_tsv(built, mutation):
    members = package_members(built["zip"])
    raw = members[ZROOT+DIRECT].decode("utf-8")
    data=list(csv.DictReader(io.StringIO(raw),delimiter="\t"))
    mutation(data)
    out=io.StringIO(newline="")
    w=csv.DictWriter(out,fieldnames=list(data[0]),delimiter="\t",lineterminator="\n")
    w.writeheader();w.writerows(data)
    blob=out.getvalue().encode("utf-8")
    members[ZROOT+DIRECT]=blob
    fix_internal_sums(members)
    return repack(members),blob


def checked_rebound(built,mutation):
    data,tsv=patch_tsv(built,mutation)
    return checked(built,blob=data,mutate=lambda d:(
        d["proof"].update(stage5_tsv_sha256=sha(tsv)),
        d["bridge"].update(stage5_tsv_sha256=sha(tsv))))


def test_self_consistent_manifest_and_rebound_sidecar_still_rejects_lost_view_bridge(built):
    def edit(rows):
        f=json.loads(rows[0]["custom_fields"])
        f.pop("kombinationen_v1")
        rows[0]["custom_fields"]=json.dumps(f,ensure_ascii=False)
    result=checked_rebound(built,edit)
    assert "MISSING_V486_VISIBLE_COMBINATION_BRIDGE" in str(result["errors"])


def test_self_consistent_manifest_and_rebound_sidecar_still_rejects_lost_teaching_delta(built):
    def edit(rows):
        f=json.loads(rows[0]["custom_fields"])
        del f["kombinationen"][0]["teaching_delta"]
        rows[0]["custom_fields"]=json.dumps(f,ensure_ascii=False)
    result=checked_rebound(built,edit)
    assert "STAGE45_COMBINATION_OR_METADATA_DRIFT" in str(result["errors"])


def test_self_consistent_manifest_and_rebound_sidecar_rejects_stale_details(built):
    def edit(rows):
        for row in rows:row["details"]="[]"
        rows[0]["details"]=json.dumps([{
            "title":"Kombinationen","items":["stale and not approved"]
        }])
    result=checked_rebound(built,edit)
    assert "STALE_DETAILS_OVERRIDE_V486_BRIDGE" in str(result["errors"])


def test_self_consistent_manifest_and_rebound_sidecar_rejects_non_neutral_card(built):
    def edit(rows): rows[0]["card_type"]="special-german-verb"
    result=checked_rebound(built,edit)
    assert ("NON_NEUTRAL_ENVELOPE_OR_CATEGORY_DRIFT" in str(result["errors"])
            or "STAGE5_EXTRACTED_NEUTRAL_PROJECTION_NOT_PASS" in str(result["errors"]))


def test_postbuild_uses_actual_inside_zip_even_when_outside_original_is_different(built):
    (built["input_dir"]/DIRECT).write_text("id\tfront\tback\nnew\tbad\tbad\n",encoding="utf-8")
    assert checked(built)["status"].startswith("PASS_SCOPED")


def test_malformed_zip_returns_blocked_not_false_pass(built):
    assert checked(built,blob=b"not-a-ZIP")["status"]=="BLOCKED"
