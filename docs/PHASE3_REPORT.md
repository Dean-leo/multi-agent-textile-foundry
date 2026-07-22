# Phase 3 验收报告

日期：2026-07-23

## 已完成

- 添加 FastAPI 应用工厂 `textile_foundry.api.create_app`。
- 提供健康检查、运行创建和运行详情查询。
- 将 Phase 1 LangGraph 状态通过 Phase 2 repository 在单事务中持久化。
- 添加 Pydantic API 输入输出契约、请求 ID、统一验证/HTTP/领域错误结构和可选 CORS 白名单。
- API 默认使用离线规则模型；未提供任何在线模型调用入口，不会打印秘密。
- 添加 API 集成和 Prompt 注入边界测试。

## 文件变更

- `src/textile_foundry/api/app.py`
- `src/textile_foundry/api/persistence.py`
- `src/textile_foundry/api/schemas.py`
- `src/textile_foundry/api/__init__.py`
- `tests/test_api.py`
- `pyproject.toml`、`uv.lock`、`src/textile_foundry/config.py`、`src/textile_foundry/graph.py`

## 验证结果

```text
ruff check .                 passed
ruff format --check .        passed
mypy src                     passed
pytest                       23 passed, 1 warning
coverage                    94.07%
```

测试使用临时 SQLite 数据库；当前环境没有 PostgreSQL 或 Docker，因此没有声称完成真实 PostgreSQL 运行验证。

## 已知限制

- 数据库 schema 迁移仍需在部署阶段显式执行。
- API 当前只提供离线运行，在线模型和认证/速率限制留在后续产品阶段。
- 未登录 GitHub、未创建远端、未部署线上服务。

## 安全检查

- 未创建 `.env` 或写入 API Key。
- API 响应不包含环境变量、请求头或内部堆栈。
- Prompt 被作为不可信文本交给离线解析器，不具备文件或 Shell 工具。

## 下一步

Phase 4：在用户明确开启后，先重新审计 Apple 设计相关 Skill，再设计 Web 产品；本阶段不自动开始。
