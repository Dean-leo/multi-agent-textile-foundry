"""Deterministic candidate selection for the offline Phase 1 designer."""

from decimal import Decimal

from textile_foundry.models.process import (
    BlendComponent,
    FabricStructure,
    ProcessDesign,
    YarnSpecification,
)
from textile_foundry.models.requirements import ParsedRequirements
from textile_foundry.repositories.fabric_repository import FabricRepository
from textile_foundry.services.validation_service import ValidationService

FUNCTION_TO_FINISH = {
    "quick_dry": "quick_dry",
    "antibacterial": "antibacterial",
    "water_repellent": "water_repellent",
    "uv_protection": "uv_protection",
    "soft_hand": "softener",
}


class DesignService:
    """Choose an auditable, lower-cost design on each revision."""

    def __init__(self, fabric_repository: FabricRepository, validator: ValidationService) -> None:
        self.fabric_repository = fabric_repository
        self.validator = validator

    def design(
        self,
        requirements: ParsedRequirements,
        revision_count: int,
        previous_version: int | None,
    ) -> ProcessDesign:
        """Build a candidate whose revision materially reduces mass or processing cost."""
        category = requirements.fabric_category
        structure_id = (
            "woven_plain"
            if category == "woven"
            else ("knitted_interlock" if revision_count == 0 else "knitted_jersey")
        )
        structure = self.fabric_repository.structure(structure_id)
        version = (previous_version or 0) + 1
        if revision_count == 0:
            fibers = [
                BlendComponent(material_id="polyester", percentage=Decimal("92")),
                BlendComponent(material_id="elastane", percentage=Decimal("8")),
            ]
            tradeoffs = ["双面结构提供较好的覆盖性，但单位面积质量和制造成本较高。"]
        elif revision_count == 1:
            fibers = [BlendComponent(material_id="polyester", percentage=Decimal("100"))]
            tradeoffs = ["改为单面针织并取消氨纶，以降低材料和制造成本；弹性与覆盖性可能下降。"]
        else:
            fibers = [BlendComponent(material_id="polyester", percentage=Decimal("100"))]
            tradeoffs = ["进一步采用轻量化假设；需要打样验证耐用性和手感。"]

        requested_finish_ids = [
            FUNCTION_TO_FINISH[function]
            for function in requirements.required_functions
            if function in FUNCTION_TO_FINISH
        ]
        if revision_count >= 2 and "antibacterial" in requested_finish_ids:
            # Keep requested functions, but record that the lower-cost option remains an estimate.
            tradeoffs.append("保留用户要求的抗菌整理；其有效性必须通过标准试验验证。")
        self.fabric_repository.validate_design(
            structure["category"], requested_finish_ids, [fiber.material_id for fiber in fibers]
        )
        design = ProcessDesign(
            version=version,
            fibers=fibers,
            yarn_specification=YarnSpecification(
                construction="涡流纺短纤纱（mock）",
                linear_density_tex=Decimal("20" if revision_count == 0 else "18"),
                processing_id="yarn_spinning",
            ),
            fabric_structure=FabricStructure(
                structure_id=structure["id"],
                category=structure["category"],
                areal_density_gsm=Decimal(str(structure["areal_density_gsm"]))
                - Decimal("10") * revision_count,
                mass_kg_per_meter=Decimal(str(structure["mass_kg_per_meter"]))
                - Decimal("0.01") * revision_count,
                manufacturing_process_id=structure["manufacturing_process_id"],
            ),
            dyeing_process_id="dyeing_standard",
            finishing_process_ids=requested_finish_ids,
            expected_functions=list(requirements.required_functions),
            tradeoffs=tradeoffs,
            assumptions=["材料、工艺和功能均基于本项目 mock 知识库，不代表真实生产参数。"],
            source_ids=self.fabric_repository.source_ids,
        )
        self.validator.validate_design(design)
        return design
