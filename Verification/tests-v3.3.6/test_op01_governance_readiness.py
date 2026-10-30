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
