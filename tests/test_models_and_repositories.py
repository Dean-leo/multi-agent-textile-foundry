"""Model, schema, repository and deterministic utility tests."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from textile_foundry.exceptions import CompatibilityError, DataNotFoundError
from textile_foundry.models.process import BlendComponent, ProcessDesign
from textile_foundry.repositories.cost_repository import CostRepository
from textile_foundry.repositories.fabric_repository import FabricRepository
from textile_foundry.services.cost_service import CostService
from textile_foundry.utilities.money import length_rate_to_meter, money


def test_mock_repositories_validate_json_schema(data_dir):
    fabrics = FabricRepository(data_dir)
    costs = CostRepository(data_dir)
    assert fabrics.source_ids == ["mock_phase1_fabric_specs"]
    assert costs.is_mock is True


def test_blend_must_total_one_hundred_percent():
    with pytest.raises(ValidationError, match="100"):
        ProcessDesign(
            version=1,
            fibers=[BlendComponent(material_id="polyester", percentage=Decimal("99"))],
            yarn_specification={
                "construction": "mock",
                "linear_density_tex": 20,
                "processing_id": "yarn_spinning",
            },
            fabric_structure={
                "structure_id": "knitted_jersey",
                "category": "knitted",
                "areal_density_gsm": 140,
                "mass_kg_per_meter": 0.18,
                "manufacturing_process_id": "knitting_jersey",
            },
            dyeing_process_id="dyeing_standard",
        )


def test_money_and_length_conversion_are_decimal():
    assert money(Decimal("1.005")) == Decimal("1.01")
    assert length_rate_to_meter(Decimal("100"), "kilometer") == Decimal("0.100")


def test_unknown_material_and_finish_are_rejected(data_dir):
    fabrics = FabricRepository(data_dir)
    with pytest.raises(DataNotFoundError):
        fabrics.material("made_up_fiber")
    with pytest.raises(CompatibilityError):
        fabrics.validate_design("unknown", [], [])
    costs = CostRepository(data_dir)
    service = CostService(costs, fabrics)
    with pytest.raises(DataNotFoundError):
        service.estimate(
            ProcessDesign(
                version=1,
                fibers=[BlendComponent(material_id="made_up_fiber", percentage=100)],
                yarn_specification={
                    "construction": "mock",
                    "linear_density_tex": 20,
                    "processing_id": "yarn_spinning",
                },
                fabric_structure={
                    "structure_id": "knitted_jersey",
                    "category": "knitted",
                    "areal_density_gsm": 140,
                    "mass_kg_per_meter": 0.18,
                    "manufacturing_process_id": "knitting_jersey",
                },
                dyeing_process_id="dyeing_standard",
            )
        )
