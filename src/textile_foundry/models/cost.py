"""Deterministic cost output models."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CostBreakdown(BaseModel):
    """Per-meter cost components calculated by Python."""

    model_config = ConfigDict(frozen=True)

    material_cost: Decimal = Field(ge=0)
    yarn_processing_cost: Decimal = Field(ge=0)
    manufacturing_cost: Decimal = Field(ge=0)
    dyeing_cost: Decimal = Field(ge=0)
    finishing_cost: Decimal = Field(ge=0)
    quality_cost: Decimal = Field(ge=0)
    waste_cost: Decimal = Field(ge=0)
    total_cost: Decimal = Field(ge=0)
    currency: Literal["CNY"] = "CNY"
    unit: Literal["meter"] = "meter"
    is_mock: bool
    assumptions: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)


class RevisionFeedback(BaseModel):
    """Structured budget feedback for the next deterministic redesign."""

    model_config = ConfigDict(frozen=True)

    design_version: int = Field(ge=1)
    estimated_cost: Decimal = Field(ge=0)
    target_cost: Decimal = Field(gt=0)
    overage: Decimal = Field(gt=0)
    dominant_cost_items: list[str] = Field(default_factory=list)
    requested_changes: list[str] = Field(default_factory=list)
