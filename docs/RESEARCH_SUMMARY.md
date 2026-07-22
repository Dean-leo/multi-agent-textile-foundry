# Phase 0 调研总结

调研日期：2026-07-22 至 2026-07-23（Asia/Shanghai）

## 技术结论

### 工作流与结构化输出

- LangGraph 官方概览将其定位为构建可控、可长期运行、有状态 Agent 工作流的低层编排框架，适合显式节点和条件边。本项目采用 `StateGraph`，而不是让多个自由自治 Agent 互相聊天。
- LangChain 官方结构化输出文档与 OpenAI Structured Outputs 文档均支持以 Schema 约束模型结果。本项目仍使用 Pydantic 做本地二次校验，因为模型响应、兼容服务商和数据迁移都可能失败。
- LLM 适用于自然语言解析和候选方案表达，不适用于最终金额计算、单位换算或路由计数。这些逻辑必须可复现、可测试。

已核实入口：

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangChain structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [OpenAI structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

### Python 与质量工具

- Phase 1 基线定为 Python 3.12，避免依赖当前系统 Python 3.9.6。
- 使用 uv 管理隔离环境和锁文件；依赖版本在 Phase 1 安装前从各自官方发行信息核验。
- 使用 Pydantic v2、pytest、Ruff 和 mypy。其文档入口在本次浏览器检查中出现连接问题，因此当前仅作为技术候选，不在本阶段声称核实具体版本或 API。

### 数据层

- Phase 1 使用少量、结构明确、可审计的 JSON，支持完全离线测试。
- Phase 2 再引入 PostgreSQL、SQLAlchemy 2.x 和 Alembic，使用 repository 接口保持核心节点不依赖具体存储。
- 数据记录必须包含单位、币种、来源、有效期、版本、是否 mock 和置信度；设计与成本结果保存不可覆盖快照。

## 纺织数据结论

- Textile Exchange 的材料市场报告可用于了解全球纤维市场范围和分类，但不能直接充当供应商价格或工艺性能数据库。
- 世界银行 Commodity Markets 可作为宏观商品数据入口，但不能从宏观指数直接推导某家供应商、某规格纱线或某项后整理的每米报价。
- 标准目录和标准正文可能需要付费、登录或受许可约束。本次对 ISO、ASTM、AATCC 和中国国家标准公开目录的浏览器访问未能完整核实，因此全部登记为 `unverified`。
- Phase 1 不录入未经核实的标准阈值。测试所需材料、工艺和成本采用小规模 mock 数据，并明确标记 `is_mock: true`。

已核实入口：

- [Textile Exchange Materials Market Report 2024](https://textileexchange.org/knowledge-center/reports/materials-market-report-2024/)
- [World Bank Commodity Markets](https://www.worldbank.org/en/research/commodity-markets)

## 部署候选与延期决定

Phase 0 不选择或配置部署平台。Phase 5 将根据当时的官方条款比较：

- Python 长运行服务和后台任务支持。
- 托管 PostgreSQL、迁移执行方式与备份。
- 环境变量、健康检查、日志、构建限制和冷启动。
- 免费额度、信用卡要求、潜在费用以及中国大陆和常见网络环境的可访问性。
- 前后端一体或分离部署的维护成本。

任何平台的当前价格和可用性都可能变化，必须在部署当天重新核实，不能把本阶段候选当成承诺。

## 环境结论

| 项目 | 结果 | 影响 |
|---|---|---|
| `modelport doctor` | 命令不存在 | 不从不明来源安装；仅如实记录 |
| macOS / 架构 | 15.7.7 / arm64 | 选择 Apple Silicon 兼容工具 |
| Python | 3.9.6 | Phase 1 从官方来源安装 3.12，不污染系统 Python |
| Git | 2.39.5 | 可进行本地版本管理 |
| GitHub CLI | 缺失 | Phase 5 首次需要时安装 |
| Docker / Compose | 缺失 | Phase 2 首次需要时安装 |
| Node.js / npm | 缺失 | Phase 4 首次需要时安装 |
| Homebrew / uv | 缺失 | 不在 Phase 0 安装 |
| Apple Command Line Tools | 可用 | 支持 Git 和后续本机构建 |
| 磁盘 | 约 77 GiB 可用 | 足够当前文档阶段 |

## Skills 与工具审计

- 实际用于 Phase 0：Browser（只读核实网页入口）、Computer Use（尝试只读检查 Codex 窗口，但被安全策略拒绝）、Visualize（决定静态工作流使用 Mermaid）、OpenAI Docs（约束 OpenAI 资料只采用官方来源）。
- 当前没有名为 `apple-design` 的 Skill，也没有项目内 `AGENTS.md`、`.codex/`、`.agents/` 或 `skills/`。
- Phase 4 开始前重新审计设计 Skill；若仍不存在，只采用经过来源核实的设计原则，不虚构 Skill 使用记录。

## 主要风险

- 真实纺织成本高度依赖地区、规格、MOQ、汇率、能源、供应商和日期，公开数据不足以形成可靠报价。
- 标准可能受版权、付费墙和许可限制；仓库只能保存必要元数据和摘要，不能复制标准正文。
- 模型可能生成貌似专业但无来源的参数；确定性候选过滤和来源强制校验是必须的。
- 兼容 OpenAI 接口的服务商可能只兼容部分功能；Phase 1 需要 provider adapter 和离线 FakeLLM。
- 当前开发工具不足，Phase 1 启动时需要先建立隔离的 Python 3.12 环境。
