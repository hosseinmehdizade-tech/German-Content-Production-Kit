#!/usr/bin/env python3
"""Read-only producer prepublish check for original Aber Hallo ZIP candidates.

Exit 0 means narrowly scoped archive-pointer coherence ONLY, not release.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
from content_package_guard import check_aber_hallo_active_pointer, PackageGuardError

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("archive",type=Path)
    p.add_argument("--expected-milestone",required=True)
    p.add_argument("--expected-sha256")
    args=p.parse_args(argv)
    e=[]
    ver=re.match(r"^WIP([1-9][0-9]*)_",args.expected_milestone)
    if ver is None:
        e.append("EXPECTED_MILESTONE_INVALID")
    if args.expected_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}",args.expected_sha256):
        e.append("EXPECTED_ZIP_SHA_INVALID")
    if args.archive.is_symlink() or not args.archive.is_file():
        e.append("ORIGINAL_ZIP_UNAVAILABLE_OR_SYMLINK")
    elif args.archive.stat().st_size <= 0 or args.archive.stat().st_size > 256_000_000:
        e.append("ORIGINAL_ZIP_SIZE_OUT_OF_BOUNDS")
    if not e:
        try:
            data=args.archive.read_bytes()
            if args.expected_sha256 is not None and hashlib.sha256(data).hexdigest()!=args.expected_sha256:
                e.append("EXTERNAL_ZIP_SHA_DRIFT")
            else:
                with zipfile.ZipFile(args.archive,"r") as z:
                    if z.testzip() is not None:
                        e.append("ARCHIVE_CRC_FAILURE")
                    elif not check_aber_hallo_active_pointer(z):
                        e.append("NOT_ABER_HALLO_EIGHT_FOLDER_ARCHIVE")
                    else:
                        summary=json.loads(z.read("MANIFEST.json"))["summary"]["status"]
                        if not summary.startswith("CURRENT_WIP"+ver.group(1)+"_"):
                            e.append("MANIFEST_VS_EXPECTED_MILESTONE_DRIFT")
        except (OSError,ValueError,KeyError,zipfile.BadZipFile,PackageGuardError) as exc:
            e.append("ARCHIVE_READ_OR_METADATA_BLOCKED:"+str(exc))
    out={
      "schema":"gcpk-op02-aber-hallo-prepublish-shadow@1",
      "status":"BLOCKED" if e else "PASS_SCOPED_METADATA_COHERENCE_ONLY",
      "errors":e,
      "archive":args.archive.name,
      "expected_milestone":args.expected_milestone,
      "publisher_authenticated":False,
      "stage4_semantic_pass":False,
      "stage5_7_pass":False,
      "git_current_promoted":False,
      "writer_granted":False,
      "performed_writes":False,
    }
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return 2 if e else 0

if __name__=="__main__":
    sys.exit(main())
