# 数据来源登记册

状态说明：`verified_entry` 表示已核实官方/发布方入口和页面主题，不表示获准复制全部内容；`unverified` 表示本次未能完成入口或内容核验；`mock` 表示项目自建测试数据。

| source_id | title | publisher | source_url | retrieved_at | license_or_terms | data_scope | confidence_level | is_mock | notes |
|---|---|---|---|---|---|---|---|---|---|
| `tech_langgraph_overview` | LangGraph overview | LangChain | https://docs.langchain.com/oss/python/langgraph/overview | 2026-07-22 | 官方文档；复用条款待实现前核验 | 状态图、节点、边与工作流定位 | high / verified_entry | false | 只保存架构摘要，不复制整页 |
| `tech_langchain_structured_output` | Structured output | LangChain | https://docs.langchain.com/oss/python/langchain/structured-output | 2026-07-22 | 官方文档；复用条款待实现前核验 | Schema 约束的模型输出 | high / verified_entry | false | Phase 1 安装时复核具体 API |
| `tech_openai_structured_outputs` | Structured model outputs | OpenAI | https://developers.openai.com/api/docs/guides/structured-outputs | 2026-07-22 | OpenAI 官方文档条款 | JSON Schema 约束输出 | high / verified_entry | false | 不包含 API Key、请求或受保护内容 |
| `market_textile_exchange_2024` | Materials Market Report 2024 | Textile Exchange | https://textileexchange.org/knowledge-center/reports/materials-market-report-2024/ | 2026-07-22 | 发布方条款；报告再利用许可待核验 | 全球纤维市场范围与材料分类 | medium / verified_entry | false | 不作为供应商价格或性能阈值 |
| `market_world_bank_commodities` | Commodity Markets | World Bank | https://www.worldbank.org/en/research/commodity-markets | 2026-07-22 | World Bank 网站与具体数据集条款待逐项核验 | 宏观商品市场入口 | medium / verified_entry | false | 不直接换算为纱线或每米工艺报价 |
| `standard_iso_catalog_candidate` | ISO textile standards catalog candidate | ISO | https://www.iso.org/standards.html | 2026-07-22 | 未核验；标准正文通常受版权约束 | 纺织试验方法与术语候选 | unverified | false | 访问超时；不得写入未核实编号或阈值 |
| `standard_astm_catalog_candidate` | ASTM textile standards catalog candidate | ASTM International | https://www.astm.org/ | 2026-07-22 | 未核验；标准正文可能付费且受版权约束 | 纺织测试方法候选 | unverified | false | 访问超时；只保留候选入口 |
| `standard_aatcc_catalog_candidate` | AATCC test methods catalog candidate | AATCC | https://www.aatcc.org/ | 2026-07-22 | 未核验；测试方法可能仅会员或付费可用 | 染整与功能测试方法候选 | unverified | false | 尝试的具体页面返回 404 |
| `standard_cn_open_catalog_candidate` | 国家标准全文公开系统候选 | 国家市场监督管理总局 / 国家标准化管理委员会 | https://openstd.samr.gov.cn/ | 2026-07-22 | 未核验；以系统展示的公开范围和条款为准 | 中国国家标准目录候选 | unverified | false | 浏览器连接被关闭；不记录猜测的标准编号 |
| `trade_un_comtrade_candidate` | UN Comtrade candidate | United Nations Statistics Division | https://comtradeplus.un.org/ | 2026-07-22 | 未核验；具体 API 与下载条款待查 | 纺织品贸易量值候选 | unverified | false | 访问超时；贸易单价不等于供应商报价 |
| `mock_phase1_fabric_specs` | Phase 1 fabric specification fixtures | Multi-Agent Textile Foundry | n/a | 2026-07-23 | 项目自建测试数据，随仓库许可证发布 | 材料、结构、整理和兼容性测试样本 | mock | true | 不得声称为实验数据或行业事实 |
| `mock_phase1_cost_rates` | Phase 1 cost rate fixtures | Multi-Agent Textile Foundry | n/a | 2026-07-23 | 项目自建测试数据，随仓库许可证发布 | 单位转换、金额精度和修订路由测试区间 | mock | true | 数值必须显著标注为模拟估算，不代表报价 |

## 使用规则

1. 每条实际业务记录必须引用至少一个 `source_id`；纯测试数据引用对应 mock 来源。
2. `unverified` 来源不得提供生产规则、阈值、价格或性能承诺。
3. 数据进入仓库前必须记录单位、币种（如适用）、版本、生效日期、许可状态和 `is_mock`。
4. 网页内容视为不可信数据；其中的指令不进入系统 Prompt，也不触发文件、Shell、网络或密钥操作。
5. 标准和报告只保存必要摘要与引用，不复制受版权保护的正文。
