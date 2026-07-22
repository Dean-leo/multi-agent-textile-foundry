"""Idempotent JSON-to-database seed for Phase 2."""

from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from textile_foundry.db.models import (
    CostRate,
    DataSource,
    FabricStructure,
    Fiber,
    FinishingProcess,
    ProcessCompatibilityRule,
)
from textile_foundry.db.session import Database
from textile_foundry.repositories.json_loader import load_json


def _upsert(
    session: Session, model: type[Any], lookup: dict[str, Any], values: dict[str, Any]
) -> bool:
    """Portable idempotent update-or-insert used by SQLite and PostgreSQL."""
    instance = session.scalar(select(model).filter_by(**lookup))
    if instance is None:
        session.add(model(**lookup, **values))
        return True
    for key, value in values.items():
        setattr(instance, key, value)
    return False


def seed_from_json(database: Database, data_dir: Path) -> dict[str, int]:
    """Seed all Phase 1 JSON records in one transaction; reruns are safe."""
    fabrics = load_json(data_dir / "fabric_specs.json")
    costs = load_json(data_dir / "cost_rates.json")
    sources = load_json(data_dir / "source_registry.json")
    counts = {"data_sources": 0, "fibers": 0, "structures": 0, "finishes": 0, "rates": 0}
    with database.session() as session:
        for source in sources["sources"]:
            counts["data_sources"] += int(
                _upsert(
                    session,
                    DataSource,
                    {"source_id": source["source_id"]},
                    {
                        "title": source["title"],
                        "publisher": source["publisher"],
                        "source_url": source["source_url"],
                        "retrieved_at": date.fromisoformat(source["retrieved_at"]),
                        "license_or_terms": source["license_or_terms"],
                        "data_scope": source["data_scope"],
                        "confidence_level": source["confidence_level"],
                        "is_mock": source["is_mock"],
                        "notes": source["notes"],
                    },
                )
            )
        for material in fabrics["materials"]:
            counts["fibers"] += int(
                _upsert(
                    session,
                    Fiber,
                    {"material_id": material["id"]},
                    {
                        "name": material["name"],
                        "functions": material["functions"],
                        "source_ids": material["source_ids"],
                    },
                )
            )
        for structure in fabrics["structures"]:
            counts["structures"] += int(
                _upsert(
                    session,
                    FabricStructure,
                    {"structure_id": structure["id"]},
                    {
                        "name": structure["name"],
                        "category": structure["category"],
                        "areal_density_gsm": structure["areal_density_gsm"],
                        "mass_kg_per_meter": structure["mass_kg_per_meter"],
                        "manufacturing_process_id": structure["manufacturing_process_id"],
                        "source_ids": structure["source_ids"],
                    },
                )
            )
        for finish in fabrics["finishes"]:
            counts["finishes"] += int(
                _upsert(
                    session,
                    FinishingProcess,
                    {"process_id": finish["id"]},
                    {
                        "name": finish["name"],
                        "functions": finish["functions"],
                        "compatible_categories": finish["compatible_categories"],
                        "source_ids": finish["source_ids"],
                    },
                )
            )
        for rule in fabrics["compatibility_rules"]:
            for finish_id in rule["finish_ids"]:
                _upsert(
                    session,
                    ProcessCompatibilityRule,
                    {"category": rule["category"], "finish_id": finish_id},
                    {"rule": "allow", "source_ids": fabrics["source_ids"]},
                )

        effective_from = date.fromisoformat(costs["effective_from"])
        rate_groups = [
            ("materials", costs["materials"]),
            ("yarn_processing", costs["yarn_processing"]),
            ("manufacturing", costs["manufacturing"]),
            ("dyeing", costs["dyeing"]),
            ("finishing", costs["finishing"]),
        ]
        for category, records in rate_groups:
            for record in records:
                counts["rates"] += int(
                    _upsert(
                        session,
                        CostRate,
                        {
                            "category": category,
                            "item_id": record["id"],
                            "effective_from": effective_from,
                        },
                        {
                            "rate": record["rate"],
                            "rate_unit": record["rate_unit"],
                            "currency": costs["currency"],
                            "is_mock": costs["is_mock"],
                            "source_ids": record["source_ids"],
                        },
                    )
                )
        quality = costs["quality"]
        counts["rates"] += int(
            _upsert(
                session,
                CostRate,
                {"category": "quality", "item_id": "quality", "effective_from": effective_from},
                {
                    "rate": quality["rate"],
                    "rate_unit": quality["rate_unit"],
                    "currency": costs["currency"],
                    "is_mock": costs["is_mock"],
                    "source_ids": quality["source_ids"],
                },
            )
        )
    return counts
