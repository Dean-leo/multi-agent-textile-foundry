# ADR 0001：初始架构与阶段隔离

- 状态：Accepted
- 日期：2026-07-23
- 决策者：项目 Phase 0

## 背景

项目需要把自然语言需求、纺织候选设计和成本约束连接成可解释流程。LLM 输出具有不确定性，纺织公开数据又存在许可、单位、地区和时效差异。如果同时开发数据库、API 和 UI，会让尚未验证的核心规则难以定位和修复。

## 决策

1. 使用 LangGraph `StateGraph` 编排三个明确节点：Requirement Analyzer、Process Designer、Cost Estimator。
2. LLM 只负责语言解析和合法候选中的建议；兼容性、单位、混纺比例、金额和路由使用确定性 Python。
3. 顶层 State 使用 `TypedDict`，嵌套业务对象使用 Pydantic v2；状态使用枚举，金额使用 `Decimal`。
4. Cost Estimator 返回成本和路由准备字段；条件路由是只读函数，不产生隐藏状态变更。
5. `max_revisions=2` 表示初始方案后最多两次重新设计，即最多三版方案。
6. Phase 1 使用带 Schema、来源和 mock 标识的 JSON，以支持离线测试和人工审计。
7. Phase 2 通过 repository 接口迁移到 PostgreSQL、SQLAlchemy 和 Alembic，保留 JSON 作为 seed，不改写核心节点。
8. 所有方案、修订和成本保存历史快照；后续结果不能覆盖以前版本。
9. 默认测试使用 FakeLLM，真实付费模型调用必须显式开启且不进入默认 CI。
10. API、Web UI、远端 GitHub 和部署分别由后续阶段开启；当前阶段不提前实现。

## 结果

### 正面影响

- 成本与路由可以完全离线、可重复地测试。
- LLM 或模型供应商可以通过依赖注入替换，不污染确定性核心。
- Phase 2 可替换存储而不改变 Agent 业务语义。
- 来源、假设、警告和历史版本成为一等数据，便于解释与审计。

### 代价

- Phase 1 需要维护 Pydantic 模型与 LangGraph State 之间的明确边界。
- JSON 数据量有限，不能代表完整行业知识库。
- 在标准和价格来源完成许可与时效核验前，只能展示 mock 成本估算。

## 被否决的方案

- **让 LLM 直接输出最终成本**：不可复现，金额精度和单位难以保证。
- **一次完成 CLI、数据库、API 与 UI**：扩大故障面并破坏阶段验收。
- **Phase 1 直接依赖 PostgreSQL**：增加环境门槛，妨碍默认离线测试。
- **把网页内容直接放入 Prompt**：增加 Prompt Injection、版权和来源污染风险。
- **用浮点数表示金额**：可能产生不可接受的舍入误差。

## 后续复核

- Phase 1 实现前确认 LangGraph、LangChain、Pydantic 和 OpenAI 兼容层的实际版本与 API。
- Phase 2 复核 JSON 到 PostgreSQL 的字段映射、迁移策略和快照约束。
- Phase 4 开始前重新审计 Apple 设计相关 Skill 和无障碍工具。
- Phase 5 根据当时平台条款、费用和网络可访问性重新做部署 ADR。
