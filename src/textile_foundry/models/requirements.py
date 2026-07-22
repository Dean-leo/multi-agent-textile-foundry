"""Structured textile requirement models."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TargetCost(BaseModel):
    """A normalized user cost target."""

    model_config = ConfigDict(frozen=True)

    amount: Decimal = Field(gt=0)
    currency: Literal["CNY"] = "CNY"
    unit: Literal["meter"] = "meter"


class ParsedRequirements(BaseModel):
    """Validated interpretation of an untrusted user request."""

    model_config = ConfigDict(frozen=True)

    application: str = Field(min_length=1)
    fabric_category: Literal["knitted", "woven", "unspecified"] = "unspecified"
    required_functions: list[str] = Field(default_factory=list)
    optional_functions: list[str] = Field(default_factory=list)
    target_cost: TargetCost | None = None
    constraints: dict[str, str] = Field(default_factory=dict)
    missing_information: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
