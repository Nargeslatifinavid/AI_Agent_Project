# src/db/client.py

import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData

# 1) بارگذاری متغیرهای محیطی از .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

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
    جدول‌ها و ستون‌های دیتابیس را introspect می‌کند.
    خروجی: { table_name: [column1, column2, ...], ... }
    """
    metadata = MetaData()
    # برای reflect از engine.sync_engine استفاده می‌شود
    metadata.reflect(bind=engine.sync_engine)

    info = {}
    for tname, tobj in metadata.tables.items():
        info[tname] = [c.name for c in tobj.columns]
    return info

# تست سریع
if __name__ == "__main__":
    async def _test():
        schema = await get_tables_and_columns()
        print("Detected schema:")
        for tbl, cols in schema.items():
            print(f" - {tbl}: {cols}")
    asyncio.run(_test())
