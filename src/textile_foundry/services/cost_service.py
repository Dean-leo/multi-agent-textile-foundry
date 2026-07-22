"""Deterministic cost formula implementation."""

from decimal import Decimal

from textile_foundry.models.cost import CostBreakdown
from textile_foundry.models.process import ProcessDesign
from textile_foundry.repositories.cost_repository import CostRepository
from textile_foundry.repositories.fabric_repository import FabricRepository
from textile_foundry.utilities.money import money


class CostService:
    """Calculate costs without asking a model to do arithmetic."""

    def __init__(
        self, cost_repository: CostRepository, fabric_repository: FabricRepository
    ) -> None:
        self.cost_repository = cost_repository
        self.fabric_repository = fabric_repository

    def estimate(self, design: ProcessDesign) -> CostBreakdown:
        """Return a rounded, auditable per-meter estimate."""
        material_rate = Decimal("0")
        for fiber in design.fibers:
            rate = self.cost_repository.rate("materials", fiber.material_id)
            material_rate += rate * fiber.percentage / Decimal("100")
        mass = design.fabric_structure.mass_kg_per_meter
        material_cost = mass * material_rate
        yarn_cost = mass * self.cost_repository.rate("yarn_processing", "yarn_spinning")
        manufacturing_cost = self.cost_repository.rate(
            "manufacturing", design.fabric_structure.manufacturing_process_id
        )
        dyeing_cost = self.cost_repository.rate("dyeing", design.dyeing_process_id)
        finishing_cost = sum(
            (
                self.cost_repository.rate("finishing", finish_id)
                for finish_id in design.finishing_process_ids
            ),
            start=Decimal("0"),
        )
        quality_cost = self.cost_repository.quality_rate()
        subtotal = (
            material_cost
            + yarn_cost
            + manufacturing_cost
            + dyeing_cost
            + finishing_cost
            + quality_cost
        )
        waste_cost = subtotal * self.cost_repository.waste_rate
        total = money(subtotal + waste_cost)
        return CostBreakdown(
            material_cost=money(material_cost),
            yarn_processing_cost=money(yarn_cost),
            manufacturing_cost=money(manufacturing_cost),
            dyeing_cost=money(dyeing_cost),
            finishing_cost=money(finishing_cost),
            quality_cost=money(quality_cost),
            waste_cost=money(waste_cost),
            total_cost=total,
            is_mock=self.cost_repository.is_mock,
            assumptions=["费率来自 mock_phase1_cost_rates，仅用于离线估算和流程测试。"],
            source_ids=self.cost_repository.source_ids,
        )
