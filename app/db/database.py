from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from app.db.schema import Base


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure DATABASE_URL uses the asyncpg driver
# Example: postgresql+asyncpg://root:root@localhost:5432/local_db
if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise ValueError("DATABASE_URL must use the 'postgresql+asyncpg://' scheme for async support.")

# Create an asynchronous engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to False in production
    future=True
)

# Create an asynchronous sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to provide an AsyncSession
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)