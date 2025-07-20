# src/db/client.py

import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine.url import make_url


# همان DATABASE_URL که در .env یا docker-compose.yml تنظیم شده

# 1) بارگذاری متغیرهای محیطی
load_dotenv()  # این خط حتما در بالا باشد
DATABASE_URL = os.getenv("DATABASE_URL")
print("🔗 DATABASE_URL =", DATABASE_URL)  # برای اطمینان ببین None نیست

# 2) ایجاد async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

# 3) کانفیگ AsyncSession
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 4) پایه ORM
Base = declarative_base()

async def get_tables_and_columns() -> dict:
    """
    Introspect the database schema and return a dict of tables to their columns.
    Uses an async connection and run_sync to invoke MetaData.reflect.
    """
    metadata = MetaData()
    # باز کردن کانکشن async و اجرای reflect در آن
    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect)

    schema_info = {}
    for table_name, table_obj in metadata.tables.items():
        schema_info[table_name] = [col.name for col in table_obj.columns]
    return schema_info

def get_tables_and_columns_sync() -> dict[str, list[str]]:
    """
    Synchronous introspection via a real sync Engine with psycopg2.
    """
    # 1) ساخت یک URL از DATABASE_URL فعلی
    url = make_url(DATABASE_URL)
    # 2) اگر driver asyncpg است، به psycopg2 سوئیچ کن
    if url.get_driver_name() == "asyncpg":
        url = url.set(drivername="postgresql+psycopg2")
    # 3) ساخت یک Engine همگام
    engine_sync = create_engine(str(url), echo=False)
    # 4) reflect متادیتا
    metadata = MetaData()
    metadata.reflect(bind=engine_sync)
    # 5) جمع‌آوری نام جداول و ستون‌ها
    schema_info: dict[str, list[str]] = {
        table_name: [col.name for col in table.columns]
        for table_name, table in metadata.tables.items()
    }
    engine_sync.dispose()
    return schema_info

# تست سریع
if __name__ == "__main__":
    async def _test():
        info = await get_tables_and_columns()
        print("Detected schema:")
        for tbl, cols in info.items():
            print(f" - {tbl}: {cols}")
    asyncio.run(_test())
