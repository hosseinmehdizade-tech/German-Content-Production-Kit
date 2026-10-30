"""Adversarial nonactive OP-01 governance evaluator; no real Git settings touched."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import runpy
import subprocess
import sys
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "audit_op01_governance_readiness.py"
M = runpy.run_path(str(SCRIPT))
check = M["evaluate"]


def fixture():
    ident = 123
    full_name = "hosseinmehdizade-tech/German-Content-Production-Kit"
    return {
        "repo": {"full_name": full_name, "private": False, "default_branch": "main"},
        "branch": {"name": "main", "protected": True, "commit": {"sha": "a" * 40}},
        "rulesets": [{"id": ident, "target": "branch", "enforcement": "active"}],
        "details": {
            str(ident): {
                "id": ident, "target": "branch", "enforcement": "active",
                "conditions": {"ref_name": {
                    "include": ["refs/heads/main"], "exclude": []}},
                "bypass_actors": [],
                "rules": [
                    {"type": "pull_request", "parameters": {}},
                    {"type": "non_fast_forward"},
                    {"type": "deletion"},
                    {"type": "required_status_checks", "parameters": {
                        "required_status_checks": [
                            {"context": "trusted-app/preflight", "integration_id": 90210}
                        ]}},
                ],
            }
        }
    }


def inspect(snapshot=None, *, live=True):
    x = fixture() if snapshot is None else snapshot
    return check(x["repo"], x["branch"], x["rulesets"], x["details"], live=live)


def blocked(value, code):
    assert value["status"] == "BLOCKED_GOVERNANCE_READINESS", value
    assert any(code in b for b in value["blockers"]), value
    for k in ("independent_current_issuer_authenticated", "trusted_base_workflow_origin_verified",
              "required_check_source_authentication_verified", "op01_writer_granted",
              "stage4_semantic_pass", "stage5_allowed", "stage6_pass",
              "stage7_release_final", "github_settings_changed", "performed_writes"):
        assert value[k] is False, k


def test_strong_synthetic_rule_shape_only_never_authenticates_owner():
    x = inspect()
    assert x["status"] == "PASS_SCOPED_RULESET_SHAPE_ONLY_NOT_TRUSTED"
    assert x["pr_only_enforcement_structurally_seen"] is True
    assert x["non_fast_forward_and_deletion_rules_seen"] is True
    assert x["branch_protection_bit_verified"] is True
    assert x["required_check_source_authentication_verified"] is False
    assert x["independent_current_issuer_authenticated"] is False
    assert x["op01_writer_granted"] is False
    assert x["stage7_release_final"] is False
    assert x["current_git_head"] == "a" * 40


def test_same_strong_caller_snapshot_is_never_authenticated_live():
    x = inspect(live=False)
    assert x["status"] == "PASS_SCOPED_RULESET_SHAPE_ONLY_NOT_TRUSTED"
    assert x["source"] == "CALLER_SUPPLIED_UNTRUSTED_SNAPSHOT"
    assert x["branch_protection_bit_verified"] is False
    assert "CALLER_SUPPLIED_GITHUB_JSON_IS_NOT_AUTHENTICATED_EVIDENCE" in x["findings"]


def test_realistic_unprotected_empty_rulesets_block():
    x = fixture()
    x["branch"]["protected"] = False
    x["rulesets"] = []
    x["details"] = {}
    r = inspect(x)
    blocked(r, "MAIN_UNPROTECTED")
    assert "NO_ACTIVE_MAIN_BRANCH_RULESET" in r["blockers"]


def test_protected_true_bit_alone_cannot_grant():
    x = fixture()
    x["rulesets"] = []
    x["details"] = {}
    blocked(inspect(x), "NO_ACTIVE_MAIN_BRANCH_RULESET")


def test_ruleset_evaluate_mode_does_not_count_as_active():
    x = fixture()
    x["rulesets"][0]["enforcement"] = "evaluate"
    x["details"]["123"]["enforcement"] = "evaluate"
    r = inspect(x)
    blocked(r, "NO_ACTIVE_MAIN_BRANCH_RULESET")
    assert r["evaluate_ruleset_ids"] == [123]


def test_ruleset_disabled_mode_does_not_count_as_active():
    x = fixture()
    x["rulesets"][0]["enforcement"] = "disabled"
    blocked(inspect(x), "NO_ACTIVE_MAIN_BRANCH_RULESET")


@pytest.mark.parametrize("rule_type", ["pull_request", "required_status_checks",
                                        "non_fast_forward", "deletion"])
def test_missing_any_critical_rule_type_blocks(rule_type):
    x = fixture()
    x["details"]["123"]["rules"] = [
        t for t in x["details"]["123"]["rules"] if t["type"] != rule_type]
    blocked(inspect(x), "REQUIRED_RULE_TYPES_MISSING")


def test_bypass_actor_even_on_active_ruleset_rejected():
    x = fixture()
    x["details"]["123"]["bypass_actors"] = [
        {"actor_type": "RepositoryRole", "actor_id": 5, "bypass_mode": "always"}]
    blocked(inspect(x), "MAIN_RULESET_HAS_BYPASS")


def test_unreadable_bypass_list_rejected():
    x = fixture()
    del x["details"]["123"]["bypass_actors"]
    blocked(inspect(x), "BYPASS_INVENTORY_UNVERIFIABLE")


def test_missing_ruleset_detail_does_not_infer_enforcement():
    x = fixture()
    x["details"] = {}
    blocked(inspect(x), "ACTIVE_RULESET_DETAILS_MISSING_OR_MISMATCHED")


def test_ruleset_id_replacement_rejected():
    x = fixture()
    x["details"]["123"]["id"] = 999
    blocked(inspect(x), "ACTIVE_RULESET_DETAILS_MISSING_OR_MISMATCHED")


def test_not_main_target_rule_rejected():
    x = fixture()
    x["details"]["123"]["conditions"]["ref_name"]["include"] = ["refs/heads/development"]
    blocked(inspect(x), "MAIN_RULESET_CONDITIONS_NOT_EXACT")


def test_ruleset_that_excludes_main_rejected():
    x = fixture()
    x["details"]["123"]["conditions"]["ref_name"]["exclude"] = ["refs/heads/main"]
    blocked(inspect(x), "MAIN_RULESET_CONDITIONS_NOT_EXACT")


@pytest.mark.parametrize("integration_id", [None, 0, -1, True, "90210"])
def test_unpinned_or_malformed_status_source_rejected(integration_id):
    x = fixture()
    rules = x["details"]["123"]["rules"]
    rules[-1]["parameters"]["required_status_checks"][0]["integration_id"] = integration_id
    blocked(inspect(x), "STATUS_SOURCE_UNPINNED_OR_MALFORMED")


def test_ruleset_with_empty_required_checks_cannot_validate():
    x = fixture()
    x["details"]["123"]["rules"][-1]["parameters"]["required_status_checks"] = []
    blocked(inspect(x), "STATUS_SOURCE_UNPINNED_OR_MALFORMED")


def test_repo_identity_mismatch_never_passes():
    x = fixture()
    x["repo"]["full_name"] = "attacker/other-repo"
    blocked(inspect(x), "REPOSITORY_IDENTITY_OR_VISIBILITY_UNVERIFIED")


def test_private_repo_does_not_count_as_public_pilot():
    x = fixture()
    x["repo"]["private"] = True
    blocked(inspect(x), "REPOSITORY_IDENTITY_OR_VISIBILITY_UNVERIFIED")


def test_malformed_or_wrong_branch_head_fails():
    x = fixture()
    x["branch"]["commit"]["sha"] = "0" * 39
    blocked(inspect(x), "BRANCH_HEAD_SHA_MALFORMED")


def test_wrong_branch_name_rejected():
    x = fixture()
    x["branch"]["name"] = "development"
    blocked(inspect(x), "BRANCH_IDENTITY_UNVERIFIED")


def test_duplicate_ruleset_id_is_not_silently_accepted():
    x = fixture()
    x["rulesets"].append(copy.deepcopy(x["rulesets"][0]))
    blocked(inspect(x), "RULESET_INDEX_MALFORMED")


def test_missing_parent_inventory_is_fail_closed():
    x = fixture()
    x["rulesets"] = None
    blocked(inspect(x), "RULESET_INVENTORY_UNVERIFIABLE")


def test_offline_cli_blocks_unprotected_and_creates_no_file(tmp_path):
    x = fixture()
    x["branch"]["protected"] = False
    x["rulesets"] = []
    x["details"] = {}
    file = tmp_path / "snapshot.json"
    file.write_text(json.dumps(x))
    before = file.read_bytes()
    run = subprocess.run([sys.executable, "-B", str(SCRIPT), "--snapshot", str(file)],
                         capture_output=True, text=True, cwd=tmp_path)
    assert run.returncode == 2
    result = json.loads(run.stdout)
    blocked(result, "MAIN_UNPROTECTED")
    assert result["source"] == "CALLER_SUPPLIED_UNTRUSTED_SNAPSHOT"
    assert file.read_bytes() == before
    assert [p.name for p in tmp_path.iterdir()] == ["snapshot.json"]


def test_live_fetch_uses_only_public_fixed_get_endpoints():
    calls = []
    fixture_data = fixture()
    replies = {
        M["API"]: fixture_data["repo"],
        M["API"] + "/branches/main": fixture_data["branch"],
        M["API"] + "/rulesets?includes_parents=true&per_page=100&page=1": fixture_data["rulesets"],
        M["API"] + "/rulesets/123": fixture_data["details"]["123"],
    }

    class Resp:
        def __init__(self, value):
            self.value = value

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, *args):
            return json.dumps(self.value).encode()

    def fake_get(req, timeout):
        calls.append((req.full_url, req.get_method()))
        return Resp(replies[req.full_url])

    with mock.patch("urllib.request.urlopen", side_effect=fake_get):
        result = M["fetch_live"]()
    assert result[0] == fixture_data["repo"]
    assert len(calls) == 4
    assert all(method == "GET" and url.startswith(M["API"]) for url, method in calls)



def check_run_fixture(*, sha="c2aeb4fe30e47cb0150aa828472af92961e8c1b5",
                      name="op01-governance-preflight", app=15368):
    """Shape/values observed in public GitHub REST check-runs for actual PR #33."""
    return {
        "total_count": 1,
        "check_runs": [{
            "id": 123734620908, "name": name,
            "head_sha": sha,
            "status": "completed", "conclusion": "success",
            "app": {"slug": "github-actions", "id": app},
        }],
    }


def status_probe(payload=None, *, sha="c2aeb4fe30e47cb0150aa828472af92961e8c1b5",
                 name="op01-governance-preflight", paths=None,
                 app_id=15368):
    return M["assess_check_origin_snapshot"](
        check_run_fixture() if payload is None else payload,
        pr_head_sha=sha,
        expected_name=name,
        expected_app_id=app_id,
        changed_paths=(
            [".github/workflows/op01-always-on-pr-governance-pilot.yml"]
            if paths is None else paths),
    )


def assert_check_never_authorizes(result):
    assert result["status"] == "BLOCKED_CHECK_ORIGIN_NOT_AUTHENTICATED"
    for name in ("check_definition_protected_base_verified",
                 "trusted_check_origin_verified", "independent_issuer_authenticated",
                 "writer_granted", "stage4_semantic_pass", "release_final",
                 "performed_writes"):
        assert result[name] is False


def test_actual_pr33_green_workflow_mutation_is_untrusted():
    result = status_probe()
    assert result["matching_check_success_observed"] is True
    assert result["expected_app_id_matched"] is True
    assert "PR_HEAD_MODIFIED_WORKFLOW_DEFINITION" in result["blockers"]
    assert "REAL_PR33_SAME_GITHUB_ACTIONS_APP_EMITTED_BYPASSED_GREEN_JOB" in result["findings"]
    assert_check_never_authorizes(result)


def test_even_clean_pr51_green_same_actions_app_id_not_issuer():
    """PR #51 clean check app.id=15368 just like malicious PR #33."""
    sha = "fdc3aed7bb16e6e108b9be109a08ebdff8150fc2"
    payload = check_run_fixture(
        sha=sha, name="safe-packaging (ubuntu-latest)", app=15368)
    result = status_probe(
        payload, sha=sha, name="safe-packaging (ubuntu-latest)", paths=[])
    assert result["matching_check_success_observed"] is True
    assert result["expected_app_id_matched"] is True
    assert result["pr_head_workflow_mutation_observed"] is False
    assert "GITHUB_ACTIONS_INTEGRATION_ID_CANNOT_PROVE_BASE_DEFINED_CHECK" in result["findings"]
    assert_check_never_authorizes(result)


def test_wrong_pr_sha_even_if_green_blocks():
    r = status_probe(sha="f" * 40)
    assert "CHECK_RUN_WRONG_PR_HEAD_SHA" in r["blockers"]
    assert r["matching_check_success_observed"] is False
    assert_check_never_authorizes(r)


def test_wrong_provider_app_id_even_with_success_blocks():
    r = status_probe(app_id=99999)
    assert "CHECK_SOURCE_APP_ID_DRIFT" in r["blockers"]
    assert_check_never_authorizes(r)


def test_missing_required_check_name_blocks():
    r = status_probe(name="trusted-other-check")
    assert "REQUIRED_CHECK_MISSING_OR_DUPLICATED" in r["blockers"]
    assert_check_never_authorizes(r)


def test_duplicate_matching_checks_cannot_be_counted_once():
    payload = check_run_fixture()
    payload["total_count"] = 2
    payload["check_runs"].append({**payload["check_runs"][0], "id": 888})
    r = status_probe(payload)
    assert "REQUIRED_CHECK_MISSING_OR_DUPLICATED" in r["blockers"]
    assert_check_never_authorizes(r)


def test_unreadable_second_page_never_inferrs_exhaustive_check_runs():
    payload = check_run_fixture()
    payload["total_count"] = 2
    r = status_probe(payload)
    assert "CHECK_RUN_PAGINATION_UNVERIFIED" in r["blockers"]
    assert_check_never_authorizes(r)


@pytest.mark.parametrize("conclusion", ["skipped", "neutral", "failure", None])
def test_non_success_check_is_not_reinterpreted_as_green(conclusion):
    payload = check_run_fixture()
    payload["check_runs"][0]["conclusion"] = conclusion
    r = status_probe(payload)
    assert "CHECK_RUN_NOT_COMPLETED_SUCCESSFULLY" in r["blockers"]
    assert r["matching_check_success_observed"] is False
    assert_check_never_authorizes(r)


def test_pending_success_check_is_not_complete():
    payload = check_run_fixture()
    payload["check_runs"][0]["status"] = "queued"
    r = status_probe(payload)
    assert "CHECK_RUN_NOT_COMPLETED_SUCCESSFULLY" in r["blockers"]
    assert_check_never_authorizes(r)


def test_missing_workflow_file_enumeration_blocks():
    r = status_probe(paths="UNKNOWN")
    assert "PR_CHANGED_FILE_INVENTORY_UNVERIFIED" in r["blockers"]
    assert_check_never_authorizes(r)


def test_self_authored_signoff_fields_do_not_create_trust():
    payload = check_run_fixture()
    payload["check_runs"][0]["trusted"] = True
    payload["check_runs"][0]["approved_by_user"] = True
    result = status_probe(payload)
    assert result["expected_app_id_matched"] is True
    assert_check_never_authorizes(result)



def test_no_pagination_shortcuts_to_green():
    fixture_data = fixture()
    api = M["API"]
    calls = []

    class Resp:
        def __init__(self, val):
            self.val = val

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, *args):
            return json.dumps(self.val).encode()

    def fake_get(req, timeout):
        calls.append(req.full_url)
        if req.full_url == api:
            return Resp(fixture_data["repo"])
        if req.full_url.endswith("/branches/main"):
            return Resp(fixture_data["branch"])
        return Resp([{"id": i+1, "target": "branch", "enforcement": "active"} for i in range(100)])

    with mock.patch("urllib.request.urlopen", side_effect=fake_get):
        with pytest.raises(ValueError, match="PAGINATION_UNVERIFIED"):
            M["fetch_live"]()
    assert len(calls) == 3
