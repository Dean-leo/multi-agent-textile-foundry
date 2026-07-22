"""Vercel-compatible FastAPI entrypoint."""

import os

from textile_foundry.api import create_app

if os.getenv("VERCEL"):
    os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:////tmp/textile_foundry.db")
    os.environ.setdefault("TEXTILE_API_PERSIST_RUNS", "false")

app = create_app()
