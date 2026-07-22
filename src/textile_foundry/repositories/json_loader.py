"""Safe JSON and JSON Schema loading."""

import json
from pathlib import Path
from typing import Any

from textile_foundry.exceptions import DataValidationError


def load_json(path: Path) -> dict[str, Any]:
    """Load one object JSON document with a safe error message."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataValidationError(f"无法读取数据文件：{path.name}") from exc
    if not isinstance(value, dict):
        raise DataValidationError(f"数据文件必须是 JSON 对象：{path.name}")
    return value


def validate_schema(document: dict[str, Any], schema_path: Path) -> None:
    """Validate a document against a local JSON Schema when jsonschema is available."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:  # pragma: no cover - dependency is a dev install
        raise DataValidationError("缺少 jsonschema 依赖，无法校验本地知识库。") from exc
    schema = load_json(schema_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda item: item.path)
    if errors:
        raise DataValidationError(f"数据文件 Schema 校验失败：{errors[0].message}")
