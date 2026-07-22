"""LangGraph state contract."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TypedDict

from textile_foundry.models.cost import CostBreakdown, RevisionFeedback
from textile_foundry.models.process import ProcessDesign, ProcessDesignSnapshot
from textile_foundry.models.requirements import ParsedRequirements


class RunStatus(StrEnum):
    """Explicit workflow lifecycle states."""

    PARSING = "parsing"
    DESIGNING = "designing"
    COSTING = "costing"
    REVISING = "revising"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorRecord(TypedDict):
    """A safe error record without stack traces or secrets."""

    category: str
    message: str


class TextileState(TypedDict, total=False):
    """Shared LangGraph state; each node returns only owned updates."""

    run_id: str
    user_request: str
    parsed_requirements: ParsedRequirements
    process_design: ProcessDesign
    design_history: list[ProcessDesignSnapshot]
    cost_estimate: Decimal
    cost_breakdown: CostBreakdown
    target_cost_per_meter: Decimal | None
    status: RunStatus
    revision_count: int
    max_revisions: int
    revision_feedback: list[RevisionFeedback]
    warnings: list[str]
    errors: list[ErrorRecord]
    data_source_ids: list[str]
    model_provider: str | None
    model_name: str | None
    created_at: datetime
    updated_at: datetime
