"""Cost Estimator node and deterministic budget routing preparation."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from textile_foundry.exceptions import TextileFoundryError
from textile_foundry.models.cost import RevisionFeedback
from textile_foundry.services.cost_service import CostService
from textile_foundry.state import ErrorRecord, RunStatus, TextileState


def make_cost_estimator(service: CostService) -> Callable[[TextileState], dict[str, Any]]:
    """Return a node that calculates money and prepares a pure route decision."""

    def cost_estimator(state: TextileState) -> dict[str, Any]:
        try:
            breakdown = service.estimate(state["process_design"])
            target = state.get("target_cost_per_meter")
            updates: dict[str, Any] = {
                "cost_breakdown": breakdown,
                "cost_estimate": breakdown.total_cost,
                "data_source_ids": sorted(
                    set(state.get("data_source_ids", [])) | set(breakdown.source_ids)
                ),
                "updated_at": datetime.now(UTC),
            }
            if target is None:
                updates["status"] = RunStatus.COMPLETED
                return updates
            if breakdown.total_cost <= target:
                updates["status"] = RunStatus.COMPLETED
                return updates

            revision_count = state.get("revision_count", 0)
            feedback = RevisionFeedback(
                design_version=state["process_design"].version,
                estimated_cost=breakdown.total_cost,
                target_cost=target,
                overage=breakdown.total_cost - target,
                dominant_cost_items=["material_cost", "manufacturing_cost", "finishing_cost"],
                requested_changes=["降低单位质量或制造成本，同时保留用户明确要求的功能。"],
            )
            updates["revision_feedback"] = [*state.get("revision_feedback", []), feedback]
            if revision_count < state.get("max_revisions", 2):
                updates["revision_count"] = revision_count + 1
                updates["status"] = RunStatus.REVISING
            else:
                updates["status"] = RunStatus.FAILED
                updates["errors"] = [
                    *state.get("errors", []),
                    {"category": "budget", "message": "达到最大修订次数后仍未满足目标成本。"},
                ]
            return updates
        except TextileFoundryError as exc:
            error: ErrorRecord = {"category": "cost_estimation", "message": str(exc)}
            return {
                "status": RunStatus.FAILED,
                "errors": [*state.get("errors", []), error],
                "updated_at": datetime.now(UTC),
            }

    return cost_estimator
