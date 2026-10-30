"""Non-destructive packaging guard for content ZIP builders."""
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import tempfile
import zipfile

PURPOSES = ("stage5_acceptance", "final_delivery", "validated_major_checkpoint", "required_recovery", "explicit_user_checkpoint")
WIP = re.compile(r"(?:^|[-_.])(wip\d*|batch\d+|per[-_]?edit|scratch|micro[-_]?edit)(?:[-_.]|$)", re.I)

class PackageGuardError(ValueError):
    pass

def check_intent(output, purpose, evidence=None, user_request=None):
    out = Path(output)
    if out.suffix.lower() != ".zip" or purpose not in PURPOSES:
        raise PackageGuardError("invalid archive path or purpose")
    if out.exists() or out.is_symlink():
        raise PackageGuardError("existing archive is immutable")
    if WIP.search(out.stem) and purpose not in ("required_recovery", "explicit_user_checkpoint"):
        raise PackageGuardError("routine WIP/batch ZIP refused")
    if purpose in ("required_recovery", "validated_major_checkpoint"):
        if evidence is None or not Path(evidence).is_file():
            raise PackageGuardError("missing milestone/recovery evidence")
        try:
            data = json.loads(Path(evidence).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise PackageGuardError("invalid evidence") from exc
        if not isinstance(data, dict):
            raise PackageGuardError("evidence must be object")
        if purpose == "required_recovery" and not str(data.get("recovery_gap") or "").strip():
            raise PackageGuardError("documented recovery gap required")
        if purpose == "validated_major_checkpoint" and data.get("status") not in ("PASS", "CLOSED", "VERIFIED"):
            raise PackageGuardError("validated milestone required")
    if purpose == "explicit_user_checkpoint" and not (user_request or "").strip():
        raise PackageGuardError("explicit user scope required")

def check_aber_hallo_active_pointer(z):
    """Fail closed on inconsistent active CURRENT metadata before ZIP publication.

    Narrowly activates for the Aber Hallo eight-folder archive layout.
    Legacy parent/historical SHA fields are not treated as active roles.
    The producer must generate CURRENT, working state and manifest from the
    same final canonical/import bytes. This is NOT issuer or Stage4-7 proof.
    """
    pointer="07-Checkpoint-State/CURRENT-WORKSTREAM-POINTER.json"
    working="07-Checkpoint-State/WORKING-STATE.json"
    canonical="02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json"
    imported="01-Final-Import/IMPORT.WORKING.tsv"
    names=set(z.namelist())
    roles={pointer,working,canonical,imported,"MANIFEST.json"}
    marker="MANIFEST.json"
    if marker not in names:
        if pointer in names:
            raise PackageGuardError("Aber Hallo active pointer lacks MANIFEST")
        return False
    if not ({pointer,working,canonical,imported} & names):
        return False

    def strict(raw):
        def pairs(items):
            obj={}
            for k,v in items:
                if k in obj:
                    raise PackageGuardError("duplicate active JSON key")
                obj[k]=v
            return obj
        def nonfinite(v):
            raise PackageGuardError("nonfinite active JSON number")
        try:
            return json.loads(raw.decode("utf-8"),object_pairs_hook=pairs,
                              parse_constant=nonfinite)
        except (ValueError,UnicodeError) as exc:
            raise PackageGuardError("malformed active JSON metadata") from exc

    manifest=strict(z.read(marker))
    if not isinstance(manifest,dict) or manifest.get("workstream")!="aber-hallo-listen-tabellen":
        if pointer in names:
            raise PackageGuardError("Aber Hallo pointer with foreign or malformed MANIFEST workstream")
        return False
    if not roles.issubset(names):
        raise PackageGuardError("Aber Hallo package missing active CURRENT role")
    summary=manifest.get("summary")
    status=summary.get("status") if isinstance(summary,dict) else None
    m=re.fullmatch(r"CURRENT_WIP([1-9][0-9]*)_[A-Z0-9_]+",status) if isinstance(status,str) else None
    if m is None:
        raise PackageGuardError("Aber Hallo MANIFEST has no exact active CURRENT WIP")
    ver=m.group(1)
    dcanonical=hashlib.sha256(z.read(canonical)).hexdigest()
    dimport=hashlib.sha256(z.read(imported)).hexdigest()
    for k,actual in (("canonical_sha256",dcanonical),("import_sha256",dimport)):
        if summary.get(k)!=actual:
            raise PackageGuardError("Aber Hallo MANIFEST active "+k+" is stale")
    p=strict(z.read(pointer))
    w=strict(z.read(working))
    if not isinstance(p,dict) or p.get("workstream")!="aber-hallo-listen-tabellen":
        raise PackageGuardError("Aber Hallo active pointer workstream mismatch")
    if not isinstance(p.get("current"),str) or not p["current"].startswith("WIP"+ver+"_"):
        raise PackageGuardError("Aber Hallo embedded CURRENT pointer version stale")
    for k,actual in (
        ("canonical_sha256",dcanonical),("import_sha256",dimport),
        ("working_canonical_sha256",dcanonical),("working_import_sha256",dimport),
    ):
        if p.get(k)!=actual:
            raise PackageGuardError("Aber Hallo embedded CURRENT pointer "+k+" stale")
    if not isinstance(w,dict):
        raise PackageGuardError("Aber Hallo WORKING-STATE must be object")
    for k,actual in (
        ("canonical_sha256",dcanonical),("import_sha256",dimport),
        ("working_canonical_sha256",dcanonical),("working_import_sha256",dimport),
    ):
        if w.get(k)!=actual:
            raise PackageGuardError("Aber Hallo WORKING-STATE "+k+" stale")
    if not isinstance(w.get("status"),str) or not w["status"].startswith("WORKING_WIP"+ver+"_"):
        raise PackageGuardError("Aber Hallo WORKING-STATE active status/version stale")
    return True


def archive_fingerprint(z, purpose):
    """Hash the actual ZIP members, not an incomplete caller-selected input list.

    Compression, ZIP timestamps and write order are ignored. A changed README,
    manifest, QA result, or added package file results in a different signature.
    Read payloads in chunks to keep memory bounded for large content ZIPs.
    """
    names = z.namelist()
    if not names or len(names) != len(set(names)):
        raise PackageGuardError("invalid or duplicate archive members")
    check_aber_hallo_active_pointer(z)
    h = hashlib.sha256(b"gfp-content-archive-payload-v2\0" + purpose.encode("utf-8"))
    for name in sorted(names):
        part = PurePosixPath(name)
        if (name.startswith(("/", "\\")) or "\\" in name or
                ":" in part.parts[0] or ".." in part.parts):
            raise PackageGuardError("unsafe ZIP member path")
        info = z.getinfo(name)
        h.update(b"\0" + name.encode("utf-8") + b"\0" + str(info.file_size).encode("ascii"))
        if not info.is_dir():
            with z.open(info) as source:
                for chunk in iter(lambda: source.read(1048576), b""):
                    h.update(chunk)
    return h.hexdigest()


def read_index(path):
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PackageGuardError("unreadable package index") from exc
    if not isinstance(data, dict):
        raise PackageGuardError("invalid package index")
    return data

@contextmanager
def guarded_zip(output, *, purpose="stage5_acceptance", inputs=(), evidence=None,
                user_request=None, compression=zipfile.ZIP_DEFLATED, compresslevel=9):
    """Make a verified temporary ZIP, then publish without replacing any old file.

    This is not a substitute for content Stage4-7 or post-package acceptance.
    """
    out = Path(output)
    check_intent(out, purpose, evidence=evidence, user_request=user_request)
    out.parent.mkdir(parents=True, exist_ok=True)
    signature = None  # computed from all verified ZIP members after closing
    index_path = out.parent / ".content-package-index.json"
    fd, temp_name = tempfile.mkstemp(prefix=".content-zip-", suffix=".tmp", dir=out.parent)
    os.close(fd)
    tmp = Path(temp_name)
    try:
        with zipfile.ZipFile(tmp, "w", compression=compression, compresslevel=compresslevel) as z:
            yield z
        with zipfile.ZipFile(tmp) as z:
            signature = archive_fingerprint(z, purpose)
        # Lock only the short publication/index section, not ZIP generation.
        # Separate workstreams sharing one output directory cannot clobber the index.
        lock_dir = out.parent / ".content-package-index.lock"
        try:
            lock_dir.mkdir()
        except FileExistsError as exc:
            raise PackageGuardError("another archive publisher is committing; retry later") from exc
        try:
            if out.exists() or out.is_symlink():
                raise PackageGuardError("output appeared during build")
            if signature:
                index = read_index(index_path)
                prior = index.get(signature)
                if prior and (out.parent / prior).is_file():
                    raise PackageGuardError("identical content concurrently packaged: " + prior)
            os.link(tmp, out)
            if signature:
                index[signature] = out.name
                fd, index_temp = tempfile.mkstemp(prefix=".content-index-", dir=out.parent)
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        json.dump(index, f, ensure_ascii=False, sort_keys=True)
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(index_temp, index_path)
                finally:
                    if os.path.exists(index_temp):
                        os.unlink(index_temp)
        finally:
            lock_dir.rmdir()
    finally:
        tmp.unlink(missing_ok=True)
