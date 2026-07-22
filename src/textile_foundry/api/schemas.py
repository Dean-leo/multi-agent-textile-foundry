"""Validated public request and response contracts."""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateRunRequest(BaseModel):
    """创建一次面料方案分析所需的内容。"""

    model_config = ConfigDict(extra="forbid")

    user_request: str = Field(
        min_length=1,
        max_length=5_000,
        description="用中文描述用途、功能、面料类型和目标成本。",
        examples=["开发一款适合夏季户外、15元/米以内的速干抗菌针织面料。"],
    )
    max_revisions: int = Field(
        default=2, ge=0, le=5, description="成本超标后允许重新设计的最大次数。"
    )


class RunSummary(BaseModel):
    run_id: str = Field(description="本次分析的唯一编号。")
    status: str = Field(description="运行状态，例如 completed 或 failed。")
    revision_count: int = Field(description="实际发生的重新设计次数。")
    max_revisions: int = Field(description="允许的最大重新设计次数。")
    cost_estimate: Decimal | None = Field(default=None, description="每米预估成本，单位 CNY。")
    target_cost_per_meter: Decimal | None = Field(
        default=None, description="用户提出的每米目标成本。"
    )
    is_mock: bool | None = Field(default=None, description="成本数据是否为演示数据。")
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
