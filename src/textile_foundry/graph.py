"""LangGraph assembly and offline-first execution entry point."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from textile_foundry.config import Settings
from textile_foundry.nodes.cost_estimator import make_cost_estimator
from textile_foundry.nodes.process_designer import make_process_designer
from textile_foundry.nodes.requirement_analyzer import make_requirement_analyzer
from textile_foundry.repositories.cost_repository import CostRepository
from textile_foundry.repositories.fabric_repository import FabricRepository
from textile_foundry.routing.cost_router import (
    route_after_cost,
    route_after_design,
    route_after_requirement,
)
from textile_foundry.services.cost_service import CostService
from textile_foundry.services.design_service import DesignService
from textile_foundry.services.llm_service import (
    RequirementModel,
    RuleBasedRequirementModel,
    build_online_requirement_model,
)
from textile_foundry.services.validation_service import ValidationService
from textile_foundry.state import RunStatus, TextileState


@dataclass(frozen=True)
class EngineDependencies:
    """Injectable services used to build a graph for production or tests."""

    requirement_model: RequirementModel
    fabric_repository: FabricRepository
    cost_repository: CostRepository


def build_dependencies(data_dir: Path, offline: bool, settings: Settings) -> EngineDependencies:
    """Build repositories and select offline or explicit online model mode."""
    fabric_repository = FabricRepository(data_dir)
    cost_repository = CostRepository(data_dir)
    model: RequirementModel = (
        RuleBasedRequirementModel() if offline else build_online_requirement_model(settings)
    )
    return EngineDependencies(model, fabric_repository, cost_repository)


def build_graph(dependencies: EngineDependencies) -> Any:
    """Compile the three-node StateGraph with read-only conditional routes."""
    validator = ValidationService(dependencies.fabric_repository)
    designer = DesignService(dependencies.fabric_repository, validator)
    estimator = CostService(dependencies.cost_repository, dependencies.fabric_repository)
    graph = StateGraph(TextileState)
    graph.add_node(
        "requirement_analyzer",
        cast(Any, make_requirement_analyzer(dependencies.requirement_model, validator)),
    )
    graph.add_node("process_designer", cast(Any, make_process_designer(designer)))
    graph.add_node("cost_estimator", cast(Any, make_cost_estimator(estimator)))
    graph.add_edge(START, "requirement_analyzer")
    graph.add_conditional_edges(
        "requirement_analyzer",
        route_after_requirement,
        {"process_designer": "process_designer", "END": END},
    )
    graph.add_conditional_edges(
        "process_designer",
        route_after_design,
        {"cost_estimator": "cost_estimator", "END": END},
    )
    graph.add_conditional_edges(
        "cost_estimator",
        route_after_cost,
        {"process_designer": "process_designer", "END": END},
    )
    return graph.compile()


def initial_state(user_request: str, max_revisions: int = 2) -> TextileState:
    """Create a fresh run with safe defaults."""
    now = datetime.now(UTC)
    state: TextileState = {
        "run_id": str(uuid4()),
        "user_request": user_request,
        "design_history": [],
        "revision_feedback": [],
        "warnings": [],
        "errors": [],
        "data_source_ids": [],
        "status": RunStatus.PARSING,
        "revision_count": 0,
        "max_revisions": max_revisions,
        "created_at": now,
        "updated_at": now,
        "model_provider": None,
        "model_name": None,
    }
    return state


def run_request(
    user_request: str,
    *,
    offline: bool = True,
    data_dir: Path | None = None,
    settings: Settings | None = None,
) -> TextileState:
    """Run one request; default behavior is deterministic and offline."""
    effective_settings = settings or Settings()
    effective_data_dir = (data_dir or effective_settings.data_dir).resolve()
    dependencies = build_dependencies(effective_data_dir, offline, effective_settings)
    result = build_graph(dependencies).invoke(initial_state(user_request))
    return cast(TextileState, result)
