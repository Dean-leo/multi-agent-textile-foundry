# 2026-07-22 来源访问审计

本记录只保存页面入口、访问结果和与项目有关的简短摘要，不保存网页全文、Cookie、Token、环境变量或个人浏览历史。检查使用 Codex 内置浏览器的只读导航和页面标题/描述读取。

## 已核实入口

| URL | 观察到的页面 | 结果 |
|---|---|---|
| https://docs.langchain.com/oss/python/langgraph/overview | `LangGraph overview - Docs by LangChain` | 页面入口与主题可访问 |
| https://docs.langchain.com/oss/python/langchain/structured-output | `Structured output - Docs by LangChain` | 页面入口与主题可访问 |
| https://developers.openai.com/api/docs/guides/structured-outputs | `Structured model outputs \| OpenAI API` | 官方入口、JSON Schema 主题可访问 |
| https://textileexchange.org/knowledge-center/reports/materials-market-report-2024/ | `Materials Market Report 2024 - Textile Exchange` | 发布方入口与报告主题可访问 |
| https://www.worldbank.org/en/research/commodity-markets | `Commodity Markets` | 官方宏观商品入口可访问 |

“已核实入口”只说明页面身份和主题已确认，不表示页面全部数据已审计、许可已完成或适合直接进入数据库。

## 未完成核实

| 候选 | 观察结果 | 处理决定 |
|---|---|---|
| Pydantic 与 pytest 官方文档 | `ERR_CONNECTION_CLOSED` | Phase 1 安装前重试官方入口，不记录具体版本/API |
| ISO 具体标准页 | 导航超时 | 标记 `unverified`，不猜测编号、版本或阈值 |
| ASTM 具体标准页 | 导航超时 | 标记 `unverified`，不复制或引用未核实内容 |
| AATCC 尝试的具体测试方法页 | 返回 404 | 只保留组织官网候选，后续从目录重新检索 |
| 国家标准全文公开系统 | `ERR_CONNECTION_CLOSED` | 标记 `unverified`，不记录猜测的国标编号 |
| UN Comtrade | 导航超时 | 仅列为贸易数据候选，不用于成本报价 |
| NIST 尝试的 SI Units 页面 | 返回 404 | 不登记为已核实来源；Phase 1 重新查找官方单位入口 |

## 搜索限制

一次针对 ISO 目录的 Bing 搜索触发了人机验证。未请求用户解决，也未绕过验证；该搜索没有作为事实来源。没有切换到用户的私人浏览记录、登录会话或其他个人文件。

## 数据准入结论

- Phase 1 允许使用的真实资料仅限来源元数据和不受争议的分类参考。
- 所有费率和用于触发路由的数值必须是项目自建 mock，并带 `is_mock: true`。
- 任何标准编号、试验条件、性能阈值和许可证结论都必须在二次核验后单独登记。
- 市场报告或贸易量值不得换算成伪精确的供应商每公斤或每米报价。
