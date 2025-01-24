import asyncio
from alembic import command
from alembic.config import Config

async def run_migrations(alembic_ini_path: str):
    """
    Run Alembic migrations.

    :param alembic_ini_path: Path to the Alembic `alembic.ini` file.
    """
    config = Config(alembic_ini_path)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, command.upgrade, config, "head")
