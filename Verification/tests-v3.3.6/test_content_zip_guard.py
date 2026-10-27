"""Content ZIP anti-churn, evidence and non-destructive publishing tests."""
import json
from pathlib import Path
import sys
import zipfile
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Tools"))
from content_package_guard import guarded_zip, PackageGuardError, check_intent

def test_wip_refused(tmp_path):
    out=tmp_path/"A2-WIP24.zip"
    with pytest.raises(PackageGuardError,match="WIP"):
        with guarded_zip(out) as z:z.writestr("cards.tsv","rows")
    assert not out.exists()

def test_existing_final_immutable(tmp_path):
    out=tmp_path/"final.zip"
    out.write_bytes(b"protected")
    with pytest.raises(PackageGuardError,match="immutable"):
        with guarded_zip(out,purpose="final_delivery") as z:z.writestr("a","b")
    assert out.read_bytes()==b"protected"

def test_duplicate_input_is_not_packaged_twice(tmp_path):
    source=tmp_path/"content.tsv"
    source.write_text("same")
    first=tmp_path/"final-v1.zip"
    with guarded_zip(first,purpose="final_delivery",inputs=(source,)) as z:z.writestr("a","b")
    assert zipfile.ZipFile(first).testzip() is None
    with pytest.raises(PackageGuardError,match="identical"):
        with guarded_zip(tmp_path/"final-v2.zip",purpose="final_delivery",inputs=(source,)) as z:z.writestr("a","b")
    assert not (tmp_path/"final-v2.zip").exists()
    source.write_text("updated")
    with guarded_zip(tmp_path/"final-v2.zip",purpose="final_delivery",inputs=(source,)) as z:z.writestr("a","changed")

def test_recovery_requires_evidence(tmp_path):
    out=tmp_path/"rescue-WIP11.zip"
    with pytest.raises(PackageGuardError):
        with guarded_zip(out,purpose="required_recovery") as z:z.writestr("a","b")
    receipt=tmp_path/"recovery.json"
    receipt.write_text(json.dumps({"recovery_gap":"latest exact editable bytes missing"}))
    with guarded_zip(out,purpose="required_recovery",evidence=receipt) as z:z.writestr("a","b")
    assert out.exists()

def test_major_milestone_needs_pass(tmp_path):
    receipt=tmp_path/"receipt.json"
    receipt.write_text(json.dumps({"status":"RUNNING"}))
    with pytest.raises(PackageGuardError):
        check_intent(tmp_path/"major.zip","validated_major_checkpoint",evidence=receipt)
    receipt.write_text(json.dumps({"status":"PASS"}))
    with guarded_zip(tmp_path/"major.zip",purpose="validated_major_checkpoint",evidence=receipt) as z:z.writestr("a","b")

def test_failure_cannot_publish_partial_zip(tmp_path):
    out=tmp_path/"final.zip"
    with pytest.raises(RuntimeError):
        with guarded_zip(out,purpose="final_delivery") as z:
            z.writestr("data","x")
            raise RuntimeError("simulated interruption")
    assert not out.exists()
    assert not list(tmp_path.glob(".content-zip-*"))

def test_reject_unsafe_member(tmp_path):
    out=tmp_path/"final.zip"
    with pytest.raises(PackageGuardError):
        with guarded_zip(out,purpose="final_delivery") as z:z.writestr("../escape","x")
    assert not out.exists()

def test_explicit_user_checkpoint(tmp_path):
    out=tmp_path/"review-WIP4.zip"
    with pytest.raises(PackageGuardError):check_intent(out,"explicit_user_checkpoint")
    with guarded_zip(out,purpose="explicit_user_checkpoint",user_request="user requested portable recovery") as z:z.writestr("checkpoint.json","{}")
    assert out.exists()

def test_three_builders_are_wired():
    files=["Tools/build_clean_delivery.py",
           "Workspaces/menschen-a2/tools/package_release.py",
           "Workspaces/menschen-a2/tools/package_release_corrective.py"]
    for path in files:
        content=(ROOT/path).read_text(encoding="utf-8")
        assert "from content_package_guard import guarded_zip" in content
        assert "with guarded_zip(" in content


def test_dedupe_uses_full_archived_payload_not_just_source_inputs(tmp_path):
    source=tmp_path/"unchanged.tsv"
    source.write_text("same original",encoding="utf-8")
    one=tmp_path/"first.zip"
    two=tmp_path/"second.zip"
    with guarded_zip(one,purpose="final_delivery",inputs=(source,)) as z:
        z.writestr("cards.tsv","same")
        z.writestr("reports/qa.json",'{"approved": false}')
    with guarded_zip(two,purpose="final_delivery",inputs=(source,)) as z:
        z.writestr("cards.tsv","same")
        z.writestr("reports/qa.json",'{"approved": true}')
    assert one.exists() and two.exists()


def test_unlisted_manifest_change_does_not_get_falsely_blocked(tmp_path):
    with guarded_zip(tmp_path/"first.zip",purpose="final_delivery") as z:
        z.writestr("cards.tsv","same")
        z.writestr("manifest.json",'{"version": 1}')
    with guarded_zip(tmp_path/"second.zip",purpose="final_delivery") as z:
        z.writestr("cards.tsv","same")
        z.writestr("manifest.json",'{"version": 2}')
    assert len(list(tmp_path.glob("*.zip")))==2


def test_exact_payload_repeat_without_input_hint_is_rejected(tmp_path):
    with guarded_zip(tmp_path/"first.zip",purpose="final_delivery") as z:
        z.writestr("a.txt","one")
        z.writestr("b.txt","two")
    with pytest.raises(PackageGuardError,match="identical"):
        with guarded_zip(tmp_path/"duplicate.zip",purpose="final_delivery") as z:
            z.writestr("b.txt","two")
            z.writestr("a.txt","one")
    assert not (tmp_path/"duplicate.zip").exists()


def test_win_style_unsafe_member_refused(tmp_path):
    for member in ("..\\escape.txt","C:/drive-file.txt"):
        with pytest.raises(PackageGuardError,match="unsafe"):
            with guarded_zip(tmp_path/"bad.zip",purpose="final_delivery") as z:
                z.writestr(member,"no")
        assert not (tmp_path/"bad.zip").exists()


def test_no_new_unguarded_python_zip_writers():
    """Prospective CI guard; pinned legacy recovery builders remain unmodified.

    Inspect tracked Python sources (not prose or rendered reports) and reject new
    direct ZIP writers. Existing historical rescue tools are deliberately frozen.
    This doesn't intercept agents that create ZIPs outside the repository.
    """
    import ast
    import subprocess

    legacy={
      "Workspaces/menschen-verben-bounded-repair-2026-10-03/package_repair.py",
      "Workspaces/menschen-a2-verben-kombinationen-v336/Recovery/R66/BUILD_R66_FROM_R62.py",
      "Workspaces/menschen-a2-verben-kombinationen-v336/Recovery/R62/BUILD_R62_FROM_R60.py",
      "Workspaces/menschen-a2-verben-kombinationen-v336/Recovery/R62/REBUILD_R60_FROM_R59.py",
      "Workspaces/menschen-a2-verben-kombinationen-v336/Recovery/R74/BUILD_R74_SUPPLEMENT.py",
      "Workspaces/menschen-a2-verben-kombinationen-v336/Recovery/R69/BUILD_R69_SOURCE_CROSSWALK.py",
      "Workspaces/menschen-a2-verben-kombinationen-v336/Recovery/R67/R67_REVIEW_PIPELINE.py",
      "Workspaces/menschen-a2-verben-kombinationen-v336/Recovery/R68/R68_CANONICAL_ASSIGNMENTS_MERGE.py",
      "Workspaces/menschen-a2-verben-kombinationen-v336/Verification/TEST_SOURCE_PERFEKT_NEGATIVE.py",
      "Tools/content_package_guard.py",
    }
    tracked=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode("utf-8").split("\0")
    violations=[]
    for relative in tracked:
        if not relative.endswith(".py") or relative in legacy:
            continue
        if relative.startswith(("Verification/test","Verification/tests-")):
            continue
        file=ROOT/relative
        if not file.is_file():
            continue
        source=file.read_text(encoding="utf-8-sig")
        if "ZipFile" not in source and "make_archive" not in source:
            continue
        try:
            tree=ast.parse(source,filename=relative)
        except SyntaxError:
            violations.append(relative+":cannot statically inspect ZIP-related Python")
            continue
        for node in ast.walk(tree):
            if not isinstance(node,ast.Call):
                continue
            attr=node.func
            method=attr.attr if isinstance(attr,ast.Attribute) else (attr.id if isinstance(attr,ast.Name) else "")
            if method=="make_archive":
                violations.append(relative+":shutil.make_archive")
                continue
            if method!="ZipFile":
                continue
            mode_node=node.args[1] if len(node.args)>1 else None
            for k in node.keywords:
                if k.arg=="mode":
                    mode_node=k.value
            mode=mode_node.value if isinstance(mode_node,ast.Constant) and isinstance(mode_node.value,str) else ("r" if mode_node is None else "unknown")
            if mode in ("w","a","x","unknown"):
                violations.append(relative+":"+str(node.lineno)+":"+mode)
    assert not violations, ("New direct ZIP producer(s) must use Tools/content_package_guard.py: "
                            + ", ".join(violations))


def test_no_new_unguarded_workflow_zip_writers():
    """New workflows may not write ZIPs directly; historical A1 jobs stay frozen."""
    import re
    import subprocess
    legacy={
        ".github/workflows/menschen-a1-current-only-v4.yml",
        ".github/workflows/menschen-a1-current-only-v5.yml",
        ".github/workflows/menschen-a1-current-only-v6.yml",
        ".github/workflows/menschen-a1-current-only-v7.yml",
        ".github/workflows/menschen-a1-current-only-repair.yml",
        ".github/workflows/menschen-a1-current-only-one-shot.yml",
        ".github/workflows/menschen-a1-current-only-final-v9.yml",
    }
    tracked=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode("utf-8").split("\0")
    unexpected=[]
    for rel in tracked:
        if not rel.startswith(".github/workflows/") or not rel.endswith((".yml",".yaml")) or rel in legacy:
            continue
        text=(ROOT/rel).read_text(encoding="utf-8")
        # Workflow inline Python writers and shell ZIP invocations require
        # the same controlled publication path.
        direct_zip=bool(re.search(r"\b(?:zipfile\.)?ZipFile\([^\n]*['\"](?:w|x|a)['\"]",text))
        shell_zip=bool(re.search(r"(?m)^\s*(?:zip\s+-(?:r|[^\s]*r[^\s]*)|7z\s+a)\b",text))
        if direct_zip or shell_zip:
            unexpected.append(rel)
    assert not unexpected, "Unguarded workflow archive writer(s): "+", ".join(unexpected)


def test_competing_publish_lock_never_damages_existing_files(tmp_path):
    existing=tmp_path/"current.zip"
    with guarded_zip(existing,purpose="final_delivery") as z:
        z.writestr("cards.tsv","protected")
    old=existing.read_bytes()
    (tmp_path/".content-package-index.lock").mkdir()
    with pytest.raises(PackageGuardError,match="another archive publisher"):
        with guarded_zip(tmp_path/"candidate.zip",purpose="final_delivery") as z:
            z.writestr("cards.tsv","candidate")
    assert existing.read_bytes()==old
    assert not (tmp_path/"candidate.zip").exists()
    assert not list(tmp_path.glob(".content-zip-*.tmp"))


def test_corrupted_dedupe_index_fails_closed(tmp_path):
    (tmp_path/".content-package-index.json").write_text("{malformed",encoding="utf-8")
    with pytest.raises(PackageGuardError,match="index"):
        with guarded_zip(tmp_path/"candidate.zip",purpose="final_delivery") as z:
            z.writestr("cards.tsv","ok")
    assert not (tmp_path/"candidate.zip").exists()


# Library publication is a separate pre-upload gate: no Library writes here.
from library_publish_preflight import audit as library_audit
import hashlib


def _zip_candidate(tmp_path, name="ready.zip", content="v1"):
    path=tmp_path/name
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("01-Final-Import/cards.tsv",content)
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    ev=tmp_path/"quality.json"
    ev.write_text(json.dumps({"status":"PASS","stage7":"PASS","archive_sha256":sha}))
    return path,sha,ev


def _library_run(path, ev, cat, purpose="final_delivery"):
    return library_audit(path, purpose=purpose,
                         destination="/German-Content-Production-Kit/Final/"+path.name,
                         workstream="sample-corpus", catalog=cat, evidence=ev)


def test_library_preflight_allow_complete_verified_scope(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path)
    result=_library_run(z,ev,{"complete":True,"scope":"workstream",
                              "workstream":"sample-corpus","entries":[]})
    assert result["decision"]=="ALLOW"
    assert result["archive_sha256"]==sha


def test_library_preflight_skip_verified_exact_copy_without_reupload(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path)
    catalog={"complete":False,"entries":[{"path":"/Flasch kart/reusable.zip",
        "sha256":sha,"hash_verified":True,"library_file_id":"libfile_exact"}]}
    result=_library_run(z,ev,catalog)
    assert result["decision"]=="SKIP_IDENTICAL"
    assert result["library_file_id"]=="libfile_exact"


def test_library_preflight_reject_filename_size_as_proof(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path)
    catalog={"complete":True,"scope":"library","entries":[{
        "path":"/Old/ready.zip","size_bytes":z.stat().st_size,
        "library_file_id":"libfile_unknown"}]}
    result=_library_run(z,ev,catalog)
    assert result["decision"]=="HOLD"
    assert result["reason"]=="POSSIBLE_DUPLICATE_NEEDS_HASH_READBACK"


def test_library_preflight_block_conflicting_destination(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path)
    catalog={"complete":True,"scope":"library","entries":[{
        "path":"/German-Content-Production-Kit/Final/ready.zip",
        "sha256":"0"*64,"hash_verified":True,
        "library_file_id":"libfile_different"}]}
    assert _library_run(z,ev,catalog)["reason"]=="DESTINATION_OCCUPIED_BY_DIFFERENT_BYTES"


def test_library_preflight_hold_when_catalog_incomplete(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path)
    result=_library_run(z,ev,{"complete":False,"scope":"library","entries":[]})
    assert result["reason"]=="INCOMPLETE_LIBRARY_CATALOG"


def test_library_preflight_reject_normal_wip_and_stage5_upload(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path,"Aber-Hallo-WIP24.zip")
    cat={"complete":True,"scope":"library","entries":[]}
    assert _library_run(z,ev,cat)["reason"]=="ROUTINE_WIP_ZIP"
    good,sha,ev=_zip_candidate(tmp_path,"stage5-candidate.zip")
    assert _library_run(good,ev,cat,purpose="stage5_acceptance")["decision"]=="BLOCK"


def test_library_preflight_evidence_must_match_exact_bytes(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path)
    ev.write_text(json.dumps({"status":"PASS","stage7":"PASS","archive_sha256":"a"*64}))
    assert _library_run(z,ev,{"complete":True,"scope":"library","entries":[]})["reason"]=="EVIDENCE_HASH_NOT_CURRENT"


def test_library_preflight_explicit_user_and_recovery_exceptions(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path,"review-WIP7.zip")
    cat={"complete":True,"scope":"workstream","workstream":"sample-corpus","entries":[]}
    dest="/German-Content-Production-Kit/Final/"+z.name
    args={"purpose":"explicit_user_checkpoint","destination":dest,
          "workstream":"sample-corpus","catalog":cat}
    assert library_audit(z,**args)["decision"]=="BLOCK"
    assert library_audit(z,user_request="Store this exact restore point",**args)["decision"]=="ALLOW"
    ev.write_text(json.dumps({"archive_sha256":sha,"recovery_gap":"original missing"}))
    args["purpose"]="required_recovery"
    assert library_audit(z,evidence=ev,**args)["decision"]=="ALLOW"


def test_library_preflight_preserves_data_and_never_writes(tmp_path):
    z,sha,ev=_zip_candidate(tmp_path)
    before=z.read_bytes()
    _library_run(z,ev,{"complete":True,"scope":"library","entries":[]})
    assert z.read_bytes()==before
    assert {p.name for p in tmp_path.iterdir()}=={"ready.zip","quality.json"}
