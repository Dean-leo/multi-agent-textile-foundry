"""Persistence adapter translating an engine state into immutable DB records."""

from textile_foundry.db.repository import DesignRunRepository
from textile_foundry.db.session import Database
from textile_foundry.state import TextileState


def persist_state(database: Database, state: TextileState) -> None:
    """Persist every available state snapshot in one transaction."""
    repository = DesignRunRepository()
    with database.session() as session:
        run = repository.create_run(
            session,
            run_id=state["run_id"],
            user_request=state["user_request"],
            target_cost_per_meter=state.get("target_cost_per_meter"),
            max_revisions=state.get("max_revisions", 2),
            model_provider=state.get("model_provider"),
            model_name=state.get("model_name"),
        )
        requirements = state.get("parsed_requirements")
        if requirements is not None:
            repository.save_requirement_snapshot(session, run, requirements)
        for snapshot in state.get("design_history", []):
            repository.save_process_snapshot(
                session, run, snapshot.design, snapshot.changes_from_previous
            )
        feedback_items = state.get("revision_feedback", [])
        for feedback in feedback_items:
            repository.save_revision(session, run, feedback, from_version=feedback.design_version)
        design = state.get("process_design")
        breakdown = state.get("cost_breakdown")
        if design is not None and breakdown is not None:
            repository.save_cost_estimate(session, run, design, breakdown)
        repository.update_run_status(
            session,
            run,
            status=str(state.get("status", "failed")),
            revision_count=state.get("revision_count", 0),
        )
