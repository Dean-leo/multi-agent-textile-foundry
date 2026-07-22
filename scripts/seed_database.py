"""Run migrations and idempotently seed the Phase 1 JSON into DATABASE_URL."""

import argparse
import os
from pathlib import Path

from alembic.config import Config

from alembic import command
from textile_foundry.db.seed import seed_from_json
from textile_foundry.db.session import Database


def main() -> int:
    parser = argparse.ArgumentParser(description="迁移并填充 Textile Foundry 数据库")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--skip-migrate", action="store_true")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("请通过 DATABASE_URL 或 --database-url 配置数据库连接。")
    if not args.skip_migrate:
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", args.database_url.replace("%", "%%"))
        command.upgrade(config, "head")
    database = Database(args.database_url)
    counts = seed_from_json(database, args.data_dir.resolve())
    database.dispose()
    print("Seed 完成：" + ", ".join(f"{key}={value}" for key, value in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
