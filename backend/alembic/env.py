from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# ----------------------------------------------------
# Add src directory to Python path
# ----------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ----------------------------------------------------
# Import Base and all models
# ----------------------------------------------------

from app.models.base import Base

# Import every model so SQLAlchemy registers metadata
import app.models

# ----------------------------------------------------
# Alembic Configuration
# ----------------------------------------------------

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ----------------------------------------------------
# Offline migrations
# ----------------------------------------------------

def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ----------------------------------------------------
# Online migrations
# ----------------------------------------------------

def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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