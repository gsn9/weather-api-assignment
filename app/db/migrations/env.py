import os
import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv
from app.db.schema import Base  

# Load environment variables from the .env file
load_dotenv()

config = context.config



if config.config_file_name is not None:
    fileConfig(config.config_file_name)


database_url = os.getenv("DATABASE_URL")
print(f"Using DATABASE_URL: {database_url}")

if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set.")
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine. By skipping the Engine creation,
    we don't even need a DBAPI to be available.

    # Calls to context.execute() here emit the given string to the
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


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Create async engine
    connectable: AsyncEngine = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
        echo=False,  # Enable SQL debugging logs
    )

    # Connect and configure the context
    async with connectable.connect() as connection:
        print(f"Connected to: {connection}")
        try:
            await connection.run_sync(
                lambda sync_connection: context.configure(
                    connection=sync_connection,
                    target_metadata=target_metadata,
                    compare_type=True,  # Compare column types
                    compare_server_default=True,  # Compare default values
                    render_as_batch=True,  # Enable batch mode (if needed)
                    process_bind=True,  # Proper handling of dialect bindings
                    echo=False,  # Log generated SQL
                )
            )
            await connection.run_sync(lambda _: context.run_migrations())

            # Explicitly commit the transaction
            await connection.commit()  # Ensure changes are persisted
            print("Migrations completed successfully and committed.")
        except Exception as e:
            print(f"Migration failed: {e}")
            raise  # Re-raise exception for debugging/logging

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
