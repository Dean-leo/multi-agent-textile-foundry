"""Human-readable terminal interface."""

import argparse
import json
import sys
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from textile_foundry.exceptions import TextileFoundryError
from textile_foundry.graph import run_request
from textile_foundry.utilities.redaction import redact

DEFAULT_REQUEST = "开发一款适用于夏季户外、成本控制在15元/米以内的速干抗菌针织面料。"


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (datetime, StrEnum)):
        return str(value)
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    raise TypeError(f"不可序列化类型：{type(value).__name__}")


def state_to_json(state: dict[str, Any]) -> str:
    """Serialize state without exposing configuration or prompts."""
    return json.dumps(state, ensure_ascii=False, indent=2, default=_json_default)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-Agent Textile Foundry 离线 CLI")
    parser.add_argument("--request", default=DEFAULT_REQUEST, help="一段中文面料企划需求")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="使用离线规则解析器（默认）")
    mode.add_argument("--online", action="store_true", help="显式启用 OpenAI 兼容模型")
    parser.add_argument("--show-trace", action="store_true", help="显示方案版本和修订追踪")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        state = run_request(args.request, offline=not args.online)
    except TextileFoundryError as exc:
        print(redact(str(exc)), file=sys.stderr)
        return 2
    print(f"状态：{state.get('status', 'unknown')}")
    print(f"运行 ID：{state['run_id']}")
    print(f"需求：{state['user_request']}")
    parsed = state.get("parsed_requirements")
    if parsed:
        print(f"功能：{', '.join(parsed.required_functions) or '未识别'}")
        print(f"目标成本：{state.get('target_cost_per_meter') or '未指定'} CNY/m")
    if state.get("process_design"):
        design = state["process_design"]
        print(f"方案：v{design.version} / {design.fabric_structure.structure_id}")
        print(f"后整理：{', '.join(design.finishing_process_ids) or '无'}")
    if state.get("cost_breakdown"):
        breakdown = state["cost_breakdown"]
        print(f"估算成本：{breakdown.total_cost} CNY/m（mock={breakdown.is_mock}）")
        print(f"成本明细：{state_to_json(breakdown.model_dump())}")
    print(f"修订次数：{state.get('revision_count', 0)}")
    for warning in state.get("warnings", []):
        print(f"警告：{warning}")
    for error in state.get("errors", []):
        print(f"错误：{error['message']}")
    if args.show_trace:
        versions = [snapshot.design.version for snapshot in state.get("design_history", [])]
        print(f"方案追踪：{versions or '无'}")
        print(f"来源：{', '.join(state.get('data_source_ids', [])) or '无'}")
    print("免责声明：这是 mock 数据支持的估算，必须通过打样、检测和真实供应商报价验证。")
    return 0 if state.get("status") != "failed" else 1
