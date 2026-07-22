# Phase 2 验收报告

完成日期：2026-07-23

## 已完成

- 引入 SQLAlchemy 2.x、Alembic 和 psycopg 依赖，并更新 `uv.lock`。
- 建立 16 张可迁移的数据库表：来源、纤维、纤维属性、纱线、织物结构、后整理、兼容规则、成本费率、设计运行、需求快照、工艺快照、设计修订、成本估算、成本明细、模型运行和校验事件。
- 增加主键、唯一约束、外键级联、非负金额/费率/修订次数 Check Constraint、单位/币种/有效日期、mock 标识和来源字段。
- 实现 `DesignRunRepository`：运行创建、需求快照、不可覆盖工艺快照、修订记录、成本明细、状态更新和审计读取。
- 实现统一事务边界：成功提交，异常回滚；同一版本重复写入幂等，内容冲突拒绝覆盖。
- 创建 Alembic 初始迁移 `alembic/versions/0843d820a5e7_create_traceable_textile_schema.py`。
- 实现 `scripts/seed_database.py`，将 Phase 1 JSON 数据幂等写入数据库。
- 增加 `docker-compose.yml`，提供官方 PostgreSQL 16 Alpine 本地服务配置，不在本阶段自动启动。

## 执行过的命令

```text
.venv/bin/uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/uv lock
DATABASE_URL=sqlite+pysqlite:///... .venv/bin/alembic revision --autogenerate -m "create traceable textile schema"
.venv/bin/alembic upgrade head
.venv/bin/alembic downgrade base
DATABASE_URL=sqlite+pysqlite:///... .venv/bin/python scripts/seed_database.py
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src scripts
.venv/bin/pytest
```

## 测试结果

- pytest：19 passed，0 failed，0 skipped。
- 覆盖率：93.19%，高于 85% 门槛。
- Ruff lint：通过。
- Ruff format check：通过。
- mypy：36 个源文件无问题。
- Alembic SQLite upgrade/downgrade：通过。
- JSON seed：重复执行后第二次所有新增计数均为 0。
- 事务回滚：违反修订 Check Constraint 后没有残留运行记录。
- 快照冲突：同版本内容不同会拒绝覆盖。

## 数据库状态与限制

- 本机没有 `postgres`、`psql` 或 Docker，因此本阶段没有启动真实 PostgreSQL 服务。
- 迁移使用 SQLAlchemy 可移植类型，并已在 SQLite 上验证升级、回退、约束和事务；这不等同于生产 PostgreSQL 验收。
- 获得 PostgreSQL 后，运行 `docker compose up -d postgres`，再使用 `DATABASE_URL` 执行 seed 和同一套测试，完成真实方言复核。
- 数据仍是 Phase 1 mock 资料，不代表真实供应商报价或实验结果。

## 安全检查

- 连接 URL 只从环境变量/参数读取；seed 脚本只打印计数，不打印 URL、密码或连接对象。
- `.env`、数据库文件、密钥文件和虚拟环境已忽略。
- 没有执行数据库重置、删除、生产迁移或付费云操作。

## 下一阶段

Phase 3 已标记为 `READY`，但必须由用户明确开启后才实现 FastAPI 适配层。真实 PostgreSQL 可用后应先完成一次线上方言迁移复核，再部署 API。
