from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---- Alembic Config ----
config = context.config
config.set_main_option(
    "sqlalchemy.url",
    os.environ.get("DATABASE_URL")
)


# ---- Logging ----
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---- Import DB + Models ----
from db.database import Base  # Base.metadata
from db import models         # IMPORTANT: ensures models are registered

target_metadata = Base.metadata


def get_database_url():
    return os.getenv("DATABASE_URL")


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
