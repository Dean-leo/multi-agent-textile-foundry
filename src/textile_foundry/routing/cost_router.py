"""Pure conditional route functions."""

from typing import Literal

from textile_foundry.state import RunStatus, TextileState

Route = Literal["process_designer", "cost_estimator", "END"]


def route_after_requirement(state: TextileState) -> Literal["process_designer", "END"]:
    """Stop immediately on a parsed requirement failure."""
    return "END" if state.get("status") == RunStatus.FAILED else "process_designer"


def route_after_design(state: TextileState) -> Literal["cost_estimator", "END"]:
    """Stop immediately on a design or compatibility failure."""
    return "END" if state.get("status") == RunStatus.FAILED else "cost_estimator"


def route_after_cost(state: TextileState) -> Literal["process_designer", "END"]:
    """Read status only; revision_count is incremented by Cost Estimator."""
    return "process_designer" if state.get("status") == RunStatus.REVISING else "END"
