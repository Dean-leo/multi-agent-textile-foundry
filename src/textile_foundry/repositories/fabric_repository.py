"""Repository for the Phase 1 fabric specification JSON."""

from pathlib import Path
from typing import Any, cast

from textile_foundry.exceptions import CompatibilityError, DataNotFoundError
from textile_foundry.repositories.json_loader import load_json, validate_schema


class FabricRepository:
    """Read-only access to mock materials, structures, finishes and compatibility."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.document = load_json(data_dir / "fabric_specs.json")
        validate_schema(self.document, data_dir / "schemas" / "fabric_specs.schema.json")

    @property
    def source_ids(self) -> list[str]:
        return list(self.document["source_ids"])

    def material(self, material_id: str) -> dict[str, Any]:
        for material in self.document["materials"]:
            if material["id"] == material_id:
                return cast(dict[str, Any], material)
        raise DataNotFoundError(f"知识库中没有材料：{material_id}")

    def structure(self, structure_id: str) -> dict[str, Any]:
        for structure in self.document["structures"]:
            if structure["id"] == structure_id:
                return cast(dict[str, Any], structure)
        raise DataNotFoundError(f"知识库中没有织物结构：{structure_id}")

    def finish(self, finish_id: str) -> dict[str, Any]:
        for finish in self.document["finishes"]:
            if finish["id"] == finish_id:
                return cast(dict[str, Any], finish)
        raise DataNotFoundError(f"知识库中没有后整理：{finish_id}")

    def validate_design(
        self, category: str, finish_ids: list[str], material_ids: list[str]
    ) -> None:
        """Perform deterministic compatibility checks before any model suggestion."""
        if category not in {"knitted", "woven"}:
            raise CompatibilityError(f"不支持的织物类别：{category}")
        allowed: list[str] = next(
            (
                rule["finish_ids"]
                for rule in self.document["compatibility_rules"]
                if rule["category"] == category
            ),
            [],
        )
        for finish_id in finish_ids:
            self.finish(finish_id)
            if finish_id not in allowed:
                raise CompatibilityError(f"后整理 {finish_id} 与 {category} 不兼容。")
        for material_id in material_ids:
            self.material(material_id)
