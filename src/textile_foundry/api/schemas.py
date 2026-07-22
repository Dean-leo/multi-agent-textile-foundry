"""Validated public request and response contracts."""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_request: str = Field(min_length=1, max_length=5_000)
    max_revisions: int = Field(default=2, ge=0, le=5)


class RunSummary(BaseModel):
    run_id: str
    status: str
    revision_count: int
    max_revisions: int
    cost_estimate: Decimal | None = None
    target_cost_per_meter: Decimal | None = None
    is_mock: bool | None = None
    warnings: list[str] = Field(default_factory=list)


class RunDetail(RunSummary):
    user_request: str
    parsed_requirements: dict[str, Any] | None = None
    process_design: dict[str, Any] | None = None
    design_history: list[dict[str, Any]] = Field(default_factory=list)
    cost_breakdown: dict[str, Any] | None = None
    revision_feedback: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[dict[str, str]] = Field(default_factory=list)
    data_source_ids: list[str] = Field(default_factory=list)
    model_provider: str | None = None
    model_name: str | None = None


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody
