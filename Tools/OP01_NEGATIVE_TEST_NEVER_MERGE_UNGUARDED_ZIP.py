# OP01 SYNTHETIC NEGATIVE TEST ONLY — NEVER MERGE.
# This is NOT a real producer. It exists only on a disposable PR branch to
# verify the required governance CI rejects a new unguarded ZIP writer.
# This function cannot write an archive even if called (raise first).
def forbidden_unprotected_archive_writer(path):
    raise RuntimeError("OP01_NEGATIVE_TEST_ONLY_DO_NOT_RUN")
    import zipfile
    with zipfile.ZipFile(path, "w") as output:
        output.writestr("negative-test-only.txt", "never publish")
