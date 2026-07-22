"""Process Designer node factory."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from textile_foundry.exceptions import TextileFoundryError
from textile_foundry.models.process import ProcessDesignSnapshot
from textile_foundry.services.design_service import DesignService
from textile_foundry.state import ErrorRecord, RunStatus, TextileState


def make_process_designer(service: DesignService) -> Callable[[TextileState], dict[str, Any]]:
    """Return a node that appends, rather than overwrites, design history."""

    def process_designer(state: TextileState) -> dict[str, Any]:
        try:
            previous = state.get("process_design")
            revision_count = state.get("revision_count", 0)
            design = service.design(
                state["parsed_requirements"],
                revision_count,
                previous.version if previous else None,
            )
            changes = (
                []
                if previous is None
                else ["根据成本反馈降低结构质量或取消弹性纤维，形成实质性成本变化。"]
            )
            snapshot = ProcessDesignSnapshot(
                captured_at=datetime.now(UTC),
                design=design,
                changes_from_previous=changes,
            )
            return {
                "process_design": design,
                "design_history": [*state.get("design_history", []), snapshot],
                "status": RunStatus.COSTING,
                "data_source_ids": sorted(
                    set(state.get("data_source_ids", [])) | set(design.source_ids)
                ),
                "updated_at": datetime.now(UTC),
            }
        except TextileFoundryError as exc:
            error: ErrorRecord = {"category": "process_design", "message": str(exc)}
            return {
                "status": RunStatus.FAILED,
                "errors": [*state.get("errors", []), error],
                "updated_at": datetime.now(UTC),
            }

    return process_designer
