import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine.url import make_url

# 1) DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password123@127.0.0.1:5432/mydb",
)

# 2) Async engine for Agent
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# 3) Sync introspection for tests
def get_tables_and_columns_sync() -> dict[str, list[str]]:
    """
    بازتاب (reflect) اسکیمای دیتابیس به‌صورت همگام (psycopg2).
    اگر دیتابیس در دسترس نباشد، خطا را بالا می‌دهد.
    """
    # 3.1) ensure psycopg2 driver
    url = make_url(DATABASE_URL)
    if url.drivername.endswith("+asyncpg"):
        url = url.set(drivername="postgresql+psycopg2")

    # 3.2) force IPv4 for localhost
    if url.host in {"localhost", "::1"}:
        url = url.set(host="127.0.0.1")

    # 3.3) build sync engine
    engine_sync = create_engine(str(url), echo=False, future=True)
    metadata = MetaData()
    metadata.reflect(bind=engine_sync)

    # 3.4) collect schema
    schema: dict[str, list[str]] = {
        table_name: [col.name for col in table.columns]
        for table_name, table in metadata.tables.items()
    }

    engine_sync.dispose()
    return schema
