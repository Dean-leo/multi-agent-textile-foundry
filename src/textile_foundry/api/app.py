"""Synchronous, safe HTTP adapter around the offline-first engine."""

from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, Response

from textile_foundry.api.persistence import persist_state
from textile_foundry.api.schemas import (
    CreateRunRequest,
    ErrorResponse,
    RunDetail,
    RunSummary,
)
from textile_foundry.config import Settings
from textile_foundry.db.base import Base
from textile_foundry.db.models import DesignRun
from textile_foundry.db.repository import DesignRunRepository
from textile_foundry.db.session import Database
from textile_foundry.exceptions import TextileFoundryError
from textile_foundry.graph import run_request
from textile_foundry.state import TextileState


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _summary(run: DesignRun) -> RunSummary:
    estimate = (
        max(run.cost_estimates, key=lambda item: item.process_version)
        if run.cost_estimates
        else None
    )
    return RunSummary(
        run_id=run.run_id,
        status=run.status,
        revision_count=run.revision_count,
        max_revisions=run.max_revisions,
        cost_estimate=estimate.total_cost if estimate else None,
        target_cost_per_meter=run.target_cost_per_meter,
        is_mock=estimate.is_mock if estimate else None,
        warnings=[],
    )


def _detail(run: DesignRun) -> RunDetail:
    summary = _summary(run)
    latest_req = (
        max(run.requirement_snapshots, key=lambda item: item.snapshot_no)
        if run.requirement_snapshots
        else None
    )
    latest_design = (
        max(run.process_snapshots, key=lambda item: item.version) if run.process_snapshots else None
    )
    estimate = (
        max(run.cost_estimates, key=lambda item: item.process_version)
        if run.cost_estimates
        else None
    )
    breakdown = None
    if estimate:
        breakdown = {
            "total_cost": str(estimate.total_cost),
            "currency": estimate.currency,
            "unit": estimate.unit,
            "is_mock": estimate.is_mock,
            "assumptions": estimate.assumptions,
            "source_ids": estimate.source_ids,
            "items": {item.item_key: str(item.amount) for item in estimate.breakdown_items},
        }
    return RunDetail(
        **summary.model_dump(),
        user_request=run.user_request,
        parsed_requirements=latest_req.payload if latest_req else None,
        process_design=latest_design.payload if latest_design else None,
        design_history=[
            {
                "version": item.version,
                "payload": item.payload,
                "changes_from_previous": item.changes_from_previous,
            }
            for item in sorted(run.process_snapshots, key=lambda value: value.version)
        ],
        cost_breakdown=breakdown,
        revision_feedback=[
            {"from_version": item.from_version, "to_version": item.to_version, **item.feedback}
            for item in sorted(run.revisions, key=lambda value: value.to_version)
        ],
        data_source_ids=estimate.source_ids if estimate else [],
        model_provider=run.model_provider,
        model_name=run.model_name,
    )


def _detail_from_state(state: TextileState) -> RunDetail:
    requirements = state.get("parsed_requirements")
    design = state.get("process_design")
    breakdown = state.get("cost_breakdown")
    return RunDetail(
        run_id=state["run_id"],
        status=str(state.get("status", "failed")),
        revision_count=state.get("revision_count", 0),
        max_revisions=state.get("max_revisions", 2),
        cost_estimate=state.get("cost_estimate"),
        target_cost_per_meter=state.get("target_cost_per_meter"),
        is_mock=breakdown.is_mock if breakdown else None,
        warnings=list(state.get("warnings", [])),
        user_request=state["user_request"],
        parsed_requirements=requirements.model_dump(mode="json") if requirements else None,
        process_design=design.model_dump(mode="json") if design else None,
        design_history=[item.model_dump(mode="json") for item in state.get("design_history", [])],
        cost_breakdown=breakdown.model_dump(mode="json") if breakdown else None,
        revision_feedback=[
            item.model_dump(mode="json") for item in state.get("revision_feedback", [])
        ],
        errors=list(state.get("errors", [])),
        data_source_ids=list(state.get("data_source_ids", [])),
        model_provider=state.get("model_provider"),
        model_name=state.get("model_name"),
    )


def create_app(
    *,
    database_url: str | None = None,
    data_dir: Path | None = None,
    settings: Settings | None = None,
    initialize_schema: bool = False,
    allowed_origins: list[str] | None = None,
    web_dir: Path | None = None,
) -> FastAPI:
    """Build the API app; migrations remain an explicit deployment operation."""
    effective_settings = settings or Settings()
    database = Database(database_url or effective_settings.database_url)
    if initialize_schema:
        Base.metadata.create_all(database.engine)
    effective_data_dir = data_dir or effective_settings.data_dir
    app = FastAPI(
        title="柔性供应链多智能体编排引擎 API",
        description=(
            "将中文面料需求解析为结构化指标，生成工艺方案并进行确定性成本核算。"
            "所有成本和性能结论均为估算，必须经过打样、检测和真实报价验证。"
        ),
        version="0.1.0",
        docs_url="/api-docs",
        redoc_url=None,
        openapi_tags=[
            {"name": "系统", "description": "健康检查与运行状态。"},
            {"name": "面料方案", "description": "创建和查询面料企划任务。"},
        ],
    )
    if allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "X-Request-ID"],
        )
    app.state.database = database
    app.state.data_dir = effective_data_dir
    app.state.settings = effective_settings
    static_dir = web_dir or Path(__file__).resolve().parents[3] / "web"
    if static_dir.is_dir():
        app.mount("/app", StaticFiles(directory=static_dir, html=True), name="web")

    @app.middleware("http")
    async def request_context(request: Request, call_next: Callable[..., Any]) -> Response:
        request.state.request_id = request.headers.get("X-Request-ID") or str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return cast(Response, response)

    @app.exception_handler(TextileFoundryError)
    async def domain_error(request: Request, exc: TextileFoundryError) -> JSONResponse:
        body = ErrorResponse(
            error={"code": "domain_error", "message": str(exc), "request_id": _request_id(request)}
        )
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        body = ErrorResponse(
            error={
                "code": "validation_error",
                "message": "请求参数无效。",
                "request_id": _request_id(request),
            }
        )
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        body = ErrorResponse(
            error={
                "code": "not_found" if exc.status_code == 404 else "http_error",
                "message": str(exc.detail),
                "request_id": _request_id(request),
            }
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.get("/healthz", tags=["系统"], summary="检查服务是否正常")
    def health() -> dict[str, str]:
        with database.session() as session:
            session.execute(text("SELECT 1"))
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    def homepage() -> RedirectResponse:
        return RedirectResponse(url="/app/", status_code=307)

    @app.get("/docs", include_in_schema=False)
    def chinese_docs() -> RedirectResponse:
        return RedirectResponse(url="/app/api-guide.html", status_code=307)

    @app.post(
        "/api/v1/runs",
        response_model=RunDetail,
        status_code=201,
        tags=["面料方案"],
        summary="提交中文需求并生成面料方案",
        description=(
            "DeepSeek 在线模式只负责把自然语言解析为结构化需求；"
            "候选过滤、兼容性验证、成本计算和超预算路由由确定性 Python 完成。"
        ),
    )
    def create_run(payload: CreateRunRequest) -> RunDetail:
        state = run_request(
            payload.user_request,
            offline=effective_settings.api_offline,
            max_revisions=payload.max_revisions,
            data_dir=effective_data_dir,
            settings=effective_settings,
        )
        if not effective_settings.api_persist_runs:
            return _detail_from_state(state)
        persist_state(database, state)
        with database.session() as session:
            run = DesignRunRepository().get_run(session, state["run_id"])
            assert run is not None
            result = _detail(run)
            result.warnings = list(state.get("warnings", []))
            return result

    @app.get(
        "/api/v1/runs/{run_id}",
        response_model=RunDetail,
        tags=["面料方案"],
        summary="查询已保存的运行详情",
        description="仅在启用持久化数据库时可跨请求查询。Vercel 无状态演示不保存历史。",
    )
    def get_run(run_id: str) -> RunDetail:
        with database.session() as session:
            run = DesignRunRepository().get_run(session, run_id)
            if run is None:
                raise HTTPException(status_code=404, detail="运行记录不存在。")
            return _detail(run)

    return app
