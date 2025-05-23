\
from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# This line allows Alembic to find your models.py and database.py
# Assuming env.py is in backend/migrations/ and models.py is in backend/
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file, particularly DATABASE_URL
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Import Base from your database module and models to ensure they're registered with Base.metadata
from database import Base
import models  # This imports your models so they register with Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the SQLAlchemy URL in the Alembic config if it's in the environment
db_url = os.getenv("DATABASE_URL")
if db_url:
    # For Alembic, we want the synchronous form of the URL
    if "postgresql+asyncpg://" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # Remove sslmode parameter which is specific to asyncpg
    if "?sslmode=require" in db_url:
        db_url = db_url.replace("?sslmode=require", "")
    elif "&sslmode=require" in db_url:
        db_url = db_url.replace("&sslmode=require", "")
    
    # If there's an empty query string, remove it
    if db_url.endswith("?"):
        db_url = db_url[:-1]
        
    config.set_main_option('sqlalchemy.url', db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
