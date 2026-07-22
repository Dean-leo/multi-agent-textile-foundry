"""Workflow routing and end-to-end CLI tests."""

from textile_foundry.cli import main
from textile_foundry.graph import run_request
from textile_foundry.state import RunStatus


def test_default_request_revises_once_then_completes():
    state = run_request("开发一款夏季户外15元/米以内的速干抗菌针织面料")
    assert state["status"] == RunStatus.COMPLETED
    assert state["revision_count"] == 1
    assert [item.design.version for item in state["design_history"]] == [1, 2]
    assert state["cost_estimate"] <= state["target_cost_per_meter"]


def test_without_target_cost_completes_with_warning():
    state = run_request("开发一款夏季户外速干抗菌针织面料")
    assert state["status"] == RunStatus.COMPLETED
    assert any("未指定目标成本" in warning for warning in state["warnings"])


def test_two_revision_limit_is_not_off_by_one():
    state = run_request("开发一款成本控制在10元/米以内的速干抗菌针织面料")
    assert state["status"] == RunStatus.FAILED
    assert state["revision_count"] == 2
    assert [item.design.version for item in state["design_history"]] == [1, 2, 3]
    assert any("最大修订次数" in error["message"] for error in state["errors"])


def test_cli_outputs_disclaimer_and_trace(capsys):
    exit_code = main(["--offline", "--show-trace"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "免责声明" in output
    assert "方案追踪" in output
    assert "API_KEY" not in output


def test_cli_returns_nonzero_for_unmet_target(capsys):
    exit_code = main(["--offline", "--request", "成本控制在10元/米以内的速干针织面料"])
    output = capsys.readouterr().out
    assert exit_code == 1
    assert "failed" in output
