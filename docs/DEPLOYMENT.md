# 网站运行与部署说明

## 本机运行

在项目根目录启动：

```bash
.venv/bin/uvicorn textile_foundry.api:create_app --factory --host 127.0.0.1 --port 8000
```

随后访问：

- 工作台：`http://127.0.0.1:8000/app/`
- API 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/healthz`

`127.0.0.1` 只允许当前电脑访问。关闭运行该服务的进程后，网页也会停止。

## GitHub 与在线网站的区别

GitHub 仓库保存和展示源代码，但不会自动运行 Python、数据库或 LangGraph。若要获得任何人都能访问的正式网址，需要额外部署 Python 服务和数据库，并在部署平台中安全配置环境变量。

当前公开仓库：

`https://github.com/Dean-leo/multi-agent-textile-foundry`

## 生产部署前置条件

- 选择支持 Python 3.12 和 PostgreSQL 的托管平台。
- 在平台中配置 `DATABASE_URL`，不要提交 `.env`。
- 如果启用 DeepSeek，只在平台的 Secret/Environment Variables 中配置 `DEEPSEEK_API_KEY`。
- 执行 Alembic 数据库迁移。
- 验证 `/healthz`、完整设计流程和日志脱敏。
- 配置 HTTPS、超时、速率限制和费用上限。

本项目尚未声称已经完成正式在线部署。
