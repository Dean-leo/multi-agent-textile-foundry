# Multi-Agent Textile Foundry

柔性供应链多智能体编排引擎的 Phase 1 CLI。系统使用 LangGraph 依次完成需求解析、候选工艺设计和确定性成本估算，并在成本超标时最多修订两次。

> 所有性能与成本结果都是 mock 数据支持的规则驱动或模型辅助估算，不代表实验室检测、生产可行性或真实供应商报价。使用前必须打样、检测并获取正式报价。

## 快速开始

```bash
.venv/bin/python main.py --offline
.venv/bin/python main.py --request "开发一款成本控制在18元/米以内的防晒速干面料" --offline
.venv/bin/python main.py --offline --show-trace
```

默认使用离线规则解析器，不需要 API Key，也不会产生模型费用。在线模式必须显式使用 `--online` 并通过环境变量配置：

```text
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=
OPENAI_TIMEOUT_SECONDS=30
OPENAI_MAX_RETRIES=2
```

不得提交真实 `.env`，不得在日志或错误输出中展示密钥。

## 质量检查

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src
.venv/bin/pytest
```

架构、来源和项目限制分别见 `ARCHITECTURE.md`、`docs/DATA_SOURCES.md` 和 `PLANS.md`。

## Phase 3 API

API 是核心引擎的同步适配层，默认完全离线运行并将每次运行写入数据库。它不接收或返回模型密钥，也不会根据用户 Prompt 读取本地文件。

```bash
.venv/bin/uvicorn textile_foundry.api:create_app --factory --host 127.0.0.1 --port 8000
```

可用端点：

- `GET /healthz`：数据库健康检查。
- `POST /api/v1/runs`：创建离线分析运行。
- `GET /api/v1/runs/{run_id}`：读取需求、方案历史、成本和修订记录。
- `GET /docs`：面向初学者的全中文使用与 API 手册。
- `GET /api-docs`：FastAPI 自动生成的交互式调试页面。

若从项目根目录启动，打开 `http://127.0.0.1:8000/app/` 可使用静态面料企划工作台。当前工作台为无 Node.js 依赖的离线 MVP。

生产环境应先执行 Alembic 迁移，再通过 `DATABASE_URL` 配置数据库；不要让应用启动隐式修改生产 schema。

仓库包含 Vercel FastAPI 入口和配置。在线演示使用无状态模式，不依赖 Vercel 不支持的持久 SQLite；密钥只在 Vercel 控制台中配置，绝不能写入仓库。具体边界见 `docs/DEPLOYMENT.md`。

## Phase 2 数据库

数据库层使用 SQLAlchemy 2.x、Alembic 和 PostgreSQL；JSON 仍作为可审计 seed。当前环境没有 PostgreSQL 或 Docker，因此默认测试使用同一套迁移在 SQLite 上验证事务、约束、快照和幂等 seed；这不等同于真实 PostgreSQL 已启动验证。

拥有 PostgreSQL 后，可通过官方 Docker 镜像启动本地数据库：

```bash
docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://textile:textile@localhost:5432/textile_foundry \
  .venv/bin/python scripts/seed_database.py
```

Seed 命令不会打印连接 URL 或密码，重复执行不会重复插入基础数据。
