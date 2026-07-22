# Multi-Agent Textile Foundry 开发计划

> 柔性供应链多智能体编排引擎。所有性能与成本输出均为规则驱动或模型辅助的估算，必须经过打样、实验检测和真实供应商报价验证。

## 阶段状态

| 阶段 | 状态 | 目标 | 进入条件 | 停止点 |
|---|---|---|---|---|
| Phase 0：环境与架构 | `COMPLETED` | 环境审计、来源调研、架构与数据契约 | 无 | 文档验收并提交，不实现业务代码 |
| Phase 1：CLI 与 LangGraph 核心 | `COMPLETED` | 离线可测的三节点状态机、JSON 知识库、CLI | 用户已明确开启；验收通过 | 已停止；不自动进入 Phase 2 |
| Phase 2：PostgreSQL 数据层 | `COMPLETED` | 可追溯、版本化、可迁移的数据与运行记录 | Phase 1 验收通过且用户已开启 | 已停止；真实 PostgreSQL 需在可用实例上复核 |
| Phase 3：API 服务 | `COMPLETED` | 用 FastAPI 适配已验证核心引擎 | Phase 2 代码与迁移验收通过 | 已停止；不自动进入 Phase 4 |
| Phase 4：Web 产品 | `IN_PROGRESS` | Apple 风格、无障碍、可解释的产品界面 | Phase 3 验收通过 | MVP 工作台已实现；完成增强后停止 |
| Phase 5：GitHub、CI/CD 与部署 | `BLOCKED` | 公开仓库、CI、部署与在线验证 | 前置阶段通过且用户明确开启 | 远端和线上证据齐全后停止 |

Phase 0 于 2026-07-23 完成。

Phase 1 于 2026-07-23 完成，验收报告见 `docs/PHASE1_REPORT.md`。

Phase 2 于 2026-07-23 完成，验收报告见 `docs/PHASE2_REPORT.md`。

Phase 3 于 2026-07-23 完成，验收报告见 `docs/PHASE3_REPORT.md`。

Phase 4 已开始，当前为无 Node.js 依赖的静态 MVP 工作台；增强项和真实部署仍未完成。

## Phase 0：环境审计、调研与架构设计

### 交付物

- `PLANS.md`
- `ARCHITECTURE.md`
- `docs/RESEARCH_SUMMARY.md`
- `docs/DATA_SOURCES.md`
- `docs/research/2026-07-22-source-audit.md`
- `docs/DECISIONS/0001-initial-architecture.md`

### 验收标准

- 环境事实、缺失工具和 `modelport doctor` 结果均如实记录。
- 三个 Agent、三种成本结果、两次修订上限和状态契约清晰无歧义。
- 已核实来源与 `unverified` 候选明确分离，模拟数据标注 `is_mock: true`。
- 仓库中没有业务 `.py` 文件、API、Web UI、密钥、真实价格数据或部署配置。

## Phase 1：CLI 与 LangGraph 核心引擎

### 目标与技术基线

- 使用 Python 3.12、uv、LangGraph、LangChain Core、Pydantic v2、pytest、Ruff 和 mypy。
- 采用 `src/textile_foundry/` 包结构。根目录 `main.py` 与 `agent_engine.py` 仅是薄兼容入口。
- 实现 Requirement Analyzer、Process Designer、Cost Estimator 和确定性条件路由。
- 使用本地 JSON 作为可审计的离线知识库；测试默认使用 FakeLLM，不访问付费模型。

### 禁止事项

- 不创建 FastAPI、Web UI、用户系统、云资源或 PostgreSQL 迁移。
- 不写死或打印密钥；不让 LLM 直接计算最终成本。
- 不将未知材料、未知工艺或缺失价格悄悄处理为零成本。

### 交付物

- 类型化 State、业务模型、节点、路由、仓储、确定性服务和 CLI。
- `data/fabric_specs.json`、`data/cost_rates.json`、来源登记与 JSON Schema。
- 单元、集成、端到端测试以及安全脱敏测试。

### 验收标准

- `ruff check .`、`ruff format --check .`、`mypy src`、`pytest` 全部通过。
- 覆盖无目标成本、直接满足、两次修订、最终失败、金额精度、单位转换、非法模型输出、超时和日志脱敏。
- 默认执行不需要 API Key；真实模型集成测试必须显式启用且不进入默认 CI。

## Phase 2：完整 PostgreSQL 数据层

- 前置条件：Phase 1 完成且用户明确开启。
- 采用 PostgreSQL、SQLAlchemy 2.x、Alembic；JSON 保留为离线 seed。
- 数据支持来源、版本、单位、币种、生效期、软删除、事务、幂等写入和不可覆盖快照。
- 禁止自动同步替代迁移、删除迁移历史或无备份重置数据库。
- 验收：迁移升级/回退测试、约束测试、事务测试和 seed 幂等性测试通过。

## Phase 3：API 服务

- 前置条件：Phase 2 完成且用户明确开启。
- FastAPI 仅作为核心引擎适配层，提供运行创建、状态、方案、成本、修订和来源查询。
- 实现统一错误、请求 ID、超时、幂等键、事务、CORS 白名单和输入输出 Schema。
- 禁止通过 Prompt 读取任意文件、执行代码或暴露内部秘密。
- 实现：`/healthz`、`POST /api/v1/runs`、`GET /api/v1/runs/{run_id}`，统一错误结构、请求 ID、可选 CORS 白名单和数据库事务。
- 验收：OpenAPI、健康检查和 API 集成测试通过；数据库迁移仍由部署流程显式执行。

## Phase 4：Apple 风格 Web 产品

- 前置条件：Phase 3 完成且用户明确开启。
- 开始前重新审计可用设计 Skills；当前未安装名为 `apple-design` 的 Skill。
- 页面覆盖需求输入、运行状态、工艺、成本、修订对比、历史、来源和免责声明。
- 满足移动端、键盘操作、基本无障碍以及加载/空/错误状态。
- 验收：关键视口、主流程、控制台和无障碍检查通过。

## Phase 5：GitHub、CI/CD 与部署

- 前置条件：所需产品阶段完成且用户明确开启。
- 根据当时的价格、Python/PostgreSQL 支持、中国大陆可访问性和维护成本重新选择平台。
- 公开前执行历史密钥扫描、许可证审计、CI 和生产迁移验证。
- 账号登录、授权、可能产生费用或创建持久凭据时再请求用户操作。
- 验收：GitHub 可访问、CI 通过、健康检查正常、核心流程在线成功且没有秘密泄漏。
