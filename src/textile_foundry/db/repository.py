"""Transactional persistence for immutable design run history."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from textile_foundry.db.models import (
    CostBreakdownItem,
    CostEstimate,
    DesignRevision,
    DesignRun,
    ProcessDesignSnapshot,
    RequirementSnapshot,
)
from textile_foundry.exceptions import DataValidationError
from textile_foundry.models.cost import CostBreakdown, RevisionFeedback
from textile_foundry.models.process import ProcessDesign
from textile_foundry.models.requirements import ParsedRequirements


class SnapshotConflictError(DataValidationError):
    """Raised when an existing immutable version is written with different data."""


class DesignRunRepository:
    """Repository that keeps each requirement, design and estimate version."""

    def create_run(
        self,
        session: Session,
        *,
        run_id: str,
        user_request: str,
        target_cost_per_meter: Decimal | None,
        max_revisions: int = 2,
        model_provider: str | None = None,
        model_name: str | None = None,
    ) -> DesignRun:
        """Create an idempotent run record."""
        existing = session.scalar(select(DesignRun).where(DesignRun.run_id == run_id))
        if existing is not None:
            return existing
        run = DesignRun(
            run_id=run_id,
            user_request=user_request,
            status="parsing",
            revision_count=0,
            max_revisions=max_revisions,
            target_cost_per_meter=target_cost_per_meter,
            model_provider=model_provider,
            model_name=model_name,
        )
        session.add(run)
        session.flush()
        return run

    def save_requirement_snapshot(
        self, session: Session, run: DesignRun, requirements: ParsedRequirements
    ) -> RequirementSnapshot:
        """Append a requirement snapshot without overwriting prior snapshots."""
        snapshot_no = (
            session.scalar(
                select(RequirementSnapshot.snapshot_no)
                .where(RequirementSnapshot.run_id == run.id)
                .order_by(RequirementSnapshot.snapshot_no.desc())
                .limit(1)
            )
            or 0
        ) + 1
        snapshot = RequirementSnapshot(
            run_id=run.id,
            snapshot_no=snapshot_no,
            payload=requirements.model_dump(mode="json"),
        )
        session.add(snapshot)
        session.flush()
        return snapshot

    def save_process_snapshot(
        self,
        session: Session,
        run: DesignRun,
        design: ProcessDesign,
        changes_from_previous: list[str],
    ) -> ProcessDesignSnapshot:
        """Write one immutable process version idempotently."""
        payload = design.model_dump(mode="json")
        existing = session.scalar(
            select(ProcessDesignSnapshot).where(
                ProcessDesignSnapshot.run_id == run.id,
                ProcessDesignSnapshot.version == design.version,
            )
        )
        if existing is not None:
            if existing.payload != payload:
                raise SnapshotConflictError(
                    "同一运行的工艺版本已存在且内容不同，拒绝覆盖历史快照。"
                )
            return existing
        snapshot = ProcessDesignSnapshot(
            run_id=run.id,
            version=design.version,
            payload=payload,
            changes_from_previous=changes_from_previous,
        )
        session.add(snapshot)
        session.flush()
        return snapshot

    def save_revision(
        self,
        session: Session,
        run: DesignRun,
        feedback: RevisionFeedback,
        *,
        from_version: int,
    ) -> DesignRevision:
        """Record one redesign edge idempotently."""
        existing = session.scalar(
            select(DesignRevision).where(
                DesignRevision.run_id == run.id,
                DesignRevision.to_version == feedback.design_version + 1,
            )
        )
        if existing is not None:
            return existing
        revision = DesignRevision(
            run_id=run.id,
            from_version=from_version,
            to_version=feedback.design_version + 1,
            feedback=feedback.model_dump(mode="json"),
        )
        session.add(revision)
        session.flush()
        return revision

    def save_cost_estimate(
        self,
        session: Session,
        run: DesignRun,
        design: ProcessDesign,
        breakdown: CostBreakdown,
    ) -> CostEstimate:
        """Persist one estimate and all component rows in one transaction."""
        existing = session.scalar(
            select(CostEstimate).where(
                CostEstimate.run_id == run.id,
                CostEstimate.process_version == design.version,
            )
        )
        if existing is not None:
            if existing.total_cost != breakdown.total_cost:
                raise SnapshotConflictError("同一工艺版本的成本估算已存在且金额不同，拒绝覆盖。")
            return existing
        estimate = CostEstimate(
            run_id=run.id,
            process_version=design.version,
            total_cost=breakdown.total_cost,
            currency=breakdown.currency,
            unit=breakdown.unit,
            is_mock=breakdown.is_mock,
            assumptions=breakdown.assumptions,
            source_ids=breakdown.source_ids,
        )
        session.add(estimate)
        session.flush()
        component_values = {
            "material_cost": breakdown.material_cost,
            "yarn_processing_cost": breakdown.yarn_processing_cost,
            "manufacturing_cost": breakdown.manufacturing_cost,
            "dyeing_cost": breakdown.dyeing_cost,
            "finishing_cost": breakdown.finishing_cost,
            "quality_cost": breakdown.quality_cost,
            "waste_cost": breakdown.waste_cost,
        }
        session.add_all(
            [
                CostBreakdownItem(
                    cost_estimate_id=estimate.id,
                    item_key=item_key,
                    amount=amount,
                    unit=breakdown.unit,
                )
                for item_key, amount in component_values.items()
            ]
        )
        session.flush()
        return estimate

    def update_run_status(
        self,
        session: Session,
        run: DesignRun,
        *,
        status: str,
        revision_count: int | None = None,
    ) -> DesignRun:
        """Update only mutable run routing metadata."""
        run.status = status
        if revision_count is not None:
            run.revision_count = revision_count
        session.flush()
        return run

    def get_run(self, session: Session, run_id: str) -> DesignRun | None:
        """Load a run with all historical children for audit views."""
        return session.scalar(
            select(DesignRun)
            .where(DesignRun.run_id == run_id)
            .options(
                selectinload(DesignRun.requirement_snapshots),
                selectinload(DesignRun.process_snapshots),
                selectinload(DesignRun.revisions),
                selectinload(DesignRun.cost_estimates).selectinload(CostEstimate.breakdown_items),
            )
        )
