"""Repository for mock cost rates."""

from decimal import Decimal
from pathlib import Path
from typing import Any

from textile_foundry.exceptions import DataNotFoundError
from textile_foundry.repositories.json_loader import load_json, validate_schema


class CostRepository:
    """Read-only access to effective mock rate records."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.document = load_json(data_dir / "cost_rates.json")
        validate_schema(self.document, data_dir / "schemas" / "cost_rates.schema.json")

    @property
    def source_ids(self) -> list[str]:
        return list(self.document["source_ids"])

    @property
    def is_mock(self) -> bool:
        return bool(self.document["is_mock"])

    @property
    def waste_rate(self) -> Decimal:
        return Decimal(str(self.document["waste_rate"]))

    def rate(self, category: str, item_id: str) -> Decimal:
        records: list[dict[str, Any]] = self.document[category]
        for record in records:
            if record["id"] == item_id:
                if record["rate_unit"] not in {"kg", "meter"}:
                    raise DataNotFoundError(f"费率单位不支持：{record['rate_unit']}")
                return Decimal(str(record["rate"]))
        raise DataNotFoundError(f"成本知识库缺少 {category} 费率：{item_id}")

    def quality_rate(self) -> Decimal:
        record = self.document["quality"]
        if record["rate_unit"] != "meter":
            raise DataNotFoundError("质量检测费率单位必须是 meter。")
        return Decimal(str(record["rate"]))
