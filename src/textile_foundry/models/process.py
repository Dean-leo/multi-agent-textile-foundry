"""Validated process design models."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BlendComponent(BaseModel):
    """A material and its percentage of the fiber blend."""

    model_config = ConfigDict(frozen=True)

    material_id: str = Field(min_length=1)
    percentage: Decimal = Field(gt=0, le=100)


class YarnSpecification(BaseModel):
    """Simplified yarn specification for an explainable estimate."""

    model_config = ConfigDict(frozen=True)

    construction: str
    linear_density_tex: Decimal = Field(gt=0)
    processing_id: str


class FabricStructure(BaseModel):
    """Fabric construction and mass assumptions used for costing."""

    model_config = ConfigDict(frozen=True)

    structure_id: str
    category: str
    areal_density_gsm: Decimal = Field(gt=0)
    mass_kg_per_meter: Decimal = Field(gt=0)
    manufacturing_process_id: str


class ProcessDesign(BaseModel):
    """A single auditable process design version."""

    model_config = ConfigDict(frozen=True)

    version: int = Field(ge=1)
    fibers: list[BlendComponent] = Field(min_length=1)
    yarn_specification: YarnSpecification
    fabric_structure: FabricStructure
    dyeing_process_id: str
    finishing_process_ids: list[str] = Field(default_factory=list)
    expected_functions: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_blend_total(self) -> "ProcessDesign":
        """Require an exact 100 percent blend using decimal arithmetic."""
        total = sum((item.percentage for item in self.fibers), start=Decimal("0"))
        if total != Decimal("100"):
            raise ValueError(f"混纺比例必须合计为 100%，当前为 {total}%。")
        return self


class ProcessDesignSnapshot(BaseModel):
    """An immutable historical design snapshot."""

    model_config = ConfigDict(frozen=True)

    captured_at: datetime
    design: ProcessDesign
    changes_from_previous: list[str] = Field(default_factory=list)
