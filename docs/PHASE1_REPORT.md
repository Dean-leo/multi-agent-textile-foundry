# Phase 1 验收报告

完成日期：2026-07-23

## 已完成

- 建立项目内 Python 3.12.13 隔离环境和 uv 锁文件。
- 实现 TypedDict LangGraph State、Pydantic 业务模型、RunStatus 和 Decimal 金额。
- 实现 Requirement Analyzer、Process Designer、Cost Estimator 三节点及只读条件路由。
- 实现离线规则解析器和显式启用的 OpenAI 兼容 structured-output 适配器。
- 实现确定性兼容性校验、单位转换、成本公式、损耗和结构化修订反馈。
- 创建材料、结构、后整理、兼容性和成本费率 mock JSON，并提供 JSON Schema 与来源登记。
- 提供 `python main.py`、`--request`、`--offline`、`--online` 和 `--show-trace`。
- 默认示例首版超预算，第一次修订后以 13.31 CNY/m 完成；10 CNY/m 用例按边界生成三版后失败。
- 只保留历史方案快照，不覆盖上一版设计。

## 文件变更

- `src/textile_foundry/`：配置、状态、模型、节点、路由、服务、仓储和 CLI。
- `main.py`、`agent_engine.py`：薄兼容入口。
- `data/`：mock 知识库、成本库、来源登记和 Schema。
- `tests/`：14 个离线单元/集成/CLI 测试。
- `pyproject.toml`、`uv.lock`、`.env.example`、`.gitignore`、`README.md`。

## 执行过的命令

```text
modelport doctor                         # 命令不存在，未安装不明软件
/Users/leonardo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m venv .venv
.venv/bin/uv pip install -e '.[dev]'
.venv/bin/uv lock
.venv/bin/python main.py --offline --show-trace
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src
.venv/bin/pytest
```

## 测试结果

- pytest：14 passed，0 failed，0 skipped。
- 覆盖率：90.47%，高于 85% 门槛。
- Ruff lint：通过。
- Ruff format check：通过。
- mypy：28 个源文件无问题。
- 默认 CLI：成功完成并输出成本明细、来源、修订追踪和免责声明。

## 关键决定

- 默认离线，真实模型调用必须显式 `--online` 并配置环境变量。
- LLM 不计算最终成本；CostService 使用 Decimal 和明确公式。
- JSON 数据均为 mock，来源 ID 为 `mock_phase1_fabric_specs` 与 `mock_phase1_cost_rates`。
- 缺失材料、工艺或费率会产生可理解的失败，不会默认为零成本。
- 根入口不复制业务逻辑，PostgreSQL/API/Web UI 留到后续阶段。

## 安全检查

- 未发现 `.env`、API Key、Token、Cookie、密码、私有路径或部署凭据。
- `.gitignore` 已忽略 `.env`、密钥扩展名、虚拟环境和缓存。
- 在线模型错误不输出请求头、Prompt 或完整配置；测试默认不触发网络调用。
- 所有价格与工艺数据都标记为 mock，不代表供应商报价或实验结果。

## 已知限制

- 当前离线解析器只覆盖有限的中文关键词和成本表达；在线模式需要用户自行配置兼容服务商凭据。
- mock 知识库不能证明真实工艺兼容性、性能或商业成本。
- Phase 1 没有持久化运行记录；历史仅存在于单次 State，数据库由 Phase 2 负责。
- 当前未创建 API、Web UI、GitHub 远端或部署配置。

## 下一阶段

Phase 2 已标记为 `READY`，但必须由用户明确开启后才实施 PostgreSQL、SQLAlchemy、Alembic、迁移、seed 和快照持久化。
