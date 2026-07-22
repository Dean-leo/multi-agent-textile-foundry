"""Deterministic validation of structured requirements and designs."""

from decimal import Decimal

from textile_foundry.exceptions import CompatibilityError
from textile_foundry.models.process import ProcessDesign
from textile_foundry.models.requirements import ParsedRequirements
from textile_foundry.repositories.fabric_repository import FabricRepository


class ValidationService:
    """Enforce constraints before design and before costing."""

    def __init__(self, fabric_repository: FabricRepository) -> None:
        self.fabric_repository = fabric_repository

    def validate_requirements(self, requirements: ParsedRequirements) -> None:
        """Reject impossible structural requirements early."""
        if requirements.target_cost is not None and requirements.target_cost.amount <= Decimal("0"):
            raise CompatibilityError("目标成本必须大于 0。")

    def validate_design(self, design: ProcessDesign) -> None:
        """Validate materials, category and finishes deterministically."""
        self.fabric_repository.validate_design(
            design.fabric_structure.category,
            design.finishing_process_ids,
            [fiber.material_id for fiber in design.fibers],
        )
