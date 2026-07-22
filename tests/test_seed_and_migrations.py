"""Idempotent seed and Alembic migration tests."""

from pathlib import Path

from alembic.config import Config
from sqlalchemy import inspect, select

from alembic import command
from textile_foundry.db.base import Base
from textile_foundry.db.models import CostRate, DataSource, Fiber
from textile_foundry.db.seed import seed_from_json
from textile_foundry.db.session import Database


def test_json_seed_is_idempotent(tmp_path: Path, data_dir: Path):
    database = Database(f"sqlite+pysqlite:///{tmp_path / 'seed.db'}")
    Base.metadata.create_all(database.engine)
    first = seed_from_json(database, data_dir)
    second = seed_from_json(database, data_dir)
    assert first["data_sources"] == 2
    assert first["fibers"] == 6
    assert first["rates"] == 17
    assert second == {key: 0 for key in first}
    with database.session() as session:
        assert len(session.scalars(select(DataSource)).all()) == 2
        assert len(session.scalars(select(Fiber)).all()) == 6
        assert len(session.scalars(select(CostRate)).all()) == 17
    database.dispose()


def test_alembic_upgrade_and_downgrade(tmp_path: Path, monkeypatch):
    database_path = tmp_path / "migration.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{database_path}")
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    inspector = inspect(Database(f"sqlite+pysqlite:///{database_path}").engine)
    tables = set(inspector.get_table_names())
    assert "design_runs" in tables
    assert "cost_breakdown_items" in tables
    command.downgrade(config, "base")
    inspector = inspect(Database(f"sqlite+pysqlite:///{database_path}").engine)
    assert "design_runs" not in set(inspector.get_table_names())
