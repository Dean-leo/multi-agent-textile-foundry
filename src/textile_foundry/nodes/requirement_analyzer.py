"""Requirement Analyzer node factory."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from textile_foundry.exceptions import TextileFoundryError
from textile_foundry.services.llm_service import RequirementModel
from textile_foundry.services.validation_service import ValidationService
from textile_foundry.state import ErrorRecord, RunStatus, TextileState


def make_requirement_analyzer(
    model: RequirementModel, validator: ValidationService
) -> Callable[[TextileState], dict[str, Any]]:
    """Return a node that owns parsed requirements and safe model metadata."""

    def requirement_analyzer(state: TextileState) -> dict[str, Any]:
        try:
            parsed = model.analyze(state["user_request"])
            validator.validate_requirements(parsed)
            warnings = list(state.get("warnings", []))
            if parsed.target_cost is None:
                warnings.append("用户未指定目标成本，未执行成本约束判断。")
            return {
                "parsed_requirements": parsed,
                "target_cost_per_meter": parsed.target_cost.amount if parsed.target_cost else None,
                "status": RunStatus.DESIGNING,
                "warnings": warnings,
                "updated_at": datetime.now(UTC),
            }
        except TextileFoundryError as exc:
            error: ErrorRecord = {"category": "requirement_analysis", "message": str(exc)}
            return {
                "status": RunStatus.FAILED,
                "errors": [*state.get("errors", []), error],
                "updated_at": datetime.now(UTC),
            }

    return requirement_analyzer
