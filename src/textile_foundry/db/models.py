"""Normalized, source-aware SQLAlchemy schema for textile design runs."""

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from textile_foundry.db.base import Base, TimestampMixin


class DataSource(TimestampMixin, Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    publisher: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000))
    retrieved_at: Mapped[date] = mapped_column(Date, nullable=False)
    license_or_terms: Mapped[str] = mapped_column(Text, nullable=False)
    data_scope: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(40), nullable=False)
    is_mock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")


class Fiber(TimestampMixin, Base):
    __tablename__ = "fibers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    functions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    properties: Mapped[list["FiberProperty"]] = relationship(
        back_populates="fiber", cascade="all, delete-orphan"
    )


class FiberProperty(TimestampMixin, Base):
    __tablename__ = "fiber_properties"
    __table_args__ = (UniqueConstraint("fiber_id", "property_name", name="uq_fiber_property"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fiber_id: Mapped[int] = mapped_column(
        ForeignKey("fibers.id", ondelete="CASCADE"), nullable=False
    )
    property_name: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[str] = mapped_column(String(200), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(40))
    fiber: Mapped[Fiber] = relationship(back_populates="properties")


class YarnSpec(TimestampMixin, Base):
    __tablename__ = "yarn_specs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    yarn_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    construction: Mapped[str] = mapped_column(String(200), nullable=False)
    linear_density_tex: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class FabricStructure(TimestampMixin, Base):
    __tablename__ = "fabric_structures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    structure_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    areal_density_gsm: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    mass_kg_per_meter: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    manufacturing_process_id: Mapped[str] = mapped_column(String(120), nullable=False)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class FinishingProcess(TimestampMixin, Base):
    __tablename__ = "finishing_processes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    functions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    compatible_categories: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class ProcessCompatibilityRule(TimestampMixin, Base):
    __tablename__ = "process_compatibility_rules"
    __table_args__ = (UniqueConstraint("category", "finish_id", name="uq_process_compatibility"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    finish_id: Mapped[str] = mapped_column(String(120), nullable=False)
    rule: Mapped[str] = mapped_column(String(40), nullable=False, default="allow")
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class CostRate(TimestampMixin, Base):
    __tablename__ = "cost_rates"
    __table_args__ = (
        UniqueConstraint("category", "item_id", "effective_from", name="uq_cost_rate_version"),
        CheckConstraint("rate >= 0", name="ck_cost_rate_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    item_id: Mapped[str] = mapped_column(String(120), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    rate_unit: Mapped[str] = mapped_column(String(40), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CNY")
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date)
    is_mock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class DesignRun(TimestampMixin, Base):
    __tablename__ = "design_runs"
    __table_args__ = (
        CheckConstraint("revision_count >= 0", name="ck_design_run_revision_nonnegative"),
        CheckConstraint("max_revisions >= 0", name="ck_design_run_max_revisions_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    user_request: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    revision_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_revisions: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    target_cost_per_meter: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    model_provider: Mapped[str | None] = mapped_column(String(80))
    model_name: Mapped[str | None] = mapped_column(String(160))
    requirement_snapshots: Mapped[list["RequirementSnapshot"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    process_snapshots: Mapped[list["ProcessDesignSnapshot"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    revisions: Mapped[list["DesignRevision"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    cost_estimates: Mapped[list["CostEstimate"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    model_runs: Mapped[list["ModelRun"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    validation_events: Mapped[list["ValidationEvent"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class RequirementSnapshot(TimestampMixin, Base):
    __tablename__ = "requirement_snapshots"
    __table_args__ = (UniqueConstraint("run_id", "snapshot_no", name="uq_requirement_snapshot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("design_runs.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_no: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    run: Mapped[DesignRun] = relationship(back_populates="requirement_snapshots")


class ProcessDesignSnapshot(TimestampMixin, Base):
    __tablename__ = "process_design_snapshots"
    __table_args__ = (UniqueConstraint("run_id", "version", name="uq_process_design_snapshot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("design_runs.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    changes_from_previous: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    run: Mapped[DesignRun] = relationship(back_populates="process_snapshots")


class DesignRevision(TimestampMixin, Base):
    __tablename__ = "design_revisions"
    __table_args__ = (UniqueConstraint("run_id", "to_version", name="uq_design_revision_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("design_runs.id", ondelete="CASCADE"), nullable=False
    )
    from_version: Mapped[int] = mapped_column(Integer, nullable=False)
    to_version: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    run: Mapped[DesignRun] = relationship(back_populates="revisions")


class CostEstimate(TimestampMixin, Base):
    __tablename__ = "cost_estimates"
    __table_args__ = (
        UniqueConstraint("run_id", "process_version", name="uq_cost_estimate_version"),
        CheckConstraint("total_cost >= 0", name="ck_cost_estimate_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("design_runs.id", ondelete="CASCADE"), nullable=False
    )
    process_version: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CNY")
    unit: Mapped[str] = mapped_column(String(40), nullable=False, default="meter")
    is_mock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    assumptions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    run: Mapped[DesignRun] = relationship(back_populates="cost_estimates")
    breakdown_items: Mapped[list["CostBreakdownItem"]] = relationship(
        back_populates="estimate", cascade="all, delete-orphan"
    )


class CostBreakdownItem(TimestampMixin, Base):
    __tablename__ = "cost_breakdown_items"
    __table_args__ = (
        UniqueConstraint("cost_estimate_id", "item_key", name="uq_cost_breakdown_item"),
        CheckConstraint("amount >= 0", name="ck_cost_breakdown_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost_estimate_id: Mapped[int] = mapped_column(
        ForeignKey("cost_estimates.id", ondelete="CASCADE"), nullable=False
    )
    item_key: Mapped[str] = mapped_column(String(80), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False, default="meter")
    estimate: Mapped[CostEstimate] = relationship(back_populates="breakdown_items")


class ModelRun(TimestampMixin, Base):
    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("design_runs.id", ondelete="CASCADE"), nullable=False
    )
    node_name: Mapped[str] = mapped_column(String(80), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80))
    model_name: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    run: Mapped[DesignRun] = relationship(back_populates="model_runs")


class ValidationEvent(TimestampMixin, Base):
    __tablename__ = "validation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("design_runs.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    run: Mapped[DesignRun] = relationship(back_populates="validation_events")
