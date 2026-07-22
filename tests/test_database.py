"""SQLite-compatible tests for PostgreSQL-ready schema and repository semantics."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from textile_foundry.db.base import Base
from textile_foundry.db.models import DesignRun
from textile_foundry.db.repository import DesignRunRepository, SnapshotConflictError
from textile_foundry.db.session import Database
from textile_foundry.graph import run_request


@pytest.fixture()
def database():
    database = Database("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(database.engine)
    yield database
    database.dispose()


def test_run_snapshots_and_breakdown_are_persisted(database):
    state = run_request("开发一款成本控制在15元/米以内的速干抗菌针织面料")
    repository = DesignRunRepository()
    with database.session() as session:
        run = repository.create_run(
            session,
            run_id=state["run_id"],
            user_request=state["user_request"],
            target_cost_per_meter=state["target_cost_per_meter"],
        )
        repository.save_requirement_snapshot(session, run, state["parsed_requirements"])
        for snapshot in state["design_history"]:
            repository.save_process_snapshot(
                session, run, snapshot.design, snapshot.changes_from_previous
            )
        for index, snapshot in enumerate(state["design_history"][:-1]):
            feedback = state["revision_feedback"][index]
            repository.save_revision(session, run, feedback, from_version=snapshot.design.version)
        repository.save_cost_estimate(
            session, run, state["process_design"], state["cost_breakdown"]
        )
        repository.update_run_status(
            session,
            run,
            status=str(state["status"]),
            revision_count=state["revision_count"],
        )
    with database.session() as session:
        loaded = repository.get_run(session, state["run_id"])
        assert loaded is not None
        assert len(loaded.process_snapshots) == 2
        assert len(loaded.cost_estimates) == 1
        assert len(loaded.cost_estimates[0].breakdown_items) == 7


def test_snapshot_write_is_idempotent_but_conflicts_are_rejected(database):
    state = run_request("开发一款成本控制在18元/米以内的速干针织面料")
    repository = DesignRunRepository()
    with database.session() as session:
        run = repository.create_run(
            session,
            run_id=state["run_id"],
            user_request=state["user_request"],
            target_cost_per_meter=state["target_cost_per_meter"],
        )
        first = repository.save_process_snapshot(session, run, state["process_design"], [])
        second = repository.save_process_snapshot(session, run, state["process_design"], [])
        assert first.id == second.id
        conflict_design = state["process_design"].model_copy(
            update={"tradeoffs": ["different historical content"]}
        )
        with pytest.raises(SnapshotConflictError):
            repository.save_process_snapshot(session, run, conflict_design, [])


def test_database_check_constraint_rolls_back_invalid_write(database):
    with pytest.raises(IntegrityError), database.session() as session:
        session.add(
            DesignRun(
                run_id="invalid",
                user_request="test",
                status="failed",
                revision_count=-1,
                max_revisions=2,
            )
        )
    with database.session() as session:
        assert session.scalar(select(DesignRun).where(DesignRun.run_id == "invalid")) is None
