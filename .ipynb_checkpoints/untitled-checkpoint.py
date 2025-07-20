# src/db/client.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData, Table, Column, Integer, String, inspect
import asyncio

# 💡 آدرس اتصال به PostgreSQL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/mydb"

# 1. ایجاد async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,          # نمایش SQL های اجرا شده در کنسول برای دیباگ
)

# 2. تنظیم AsyncSession
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3. پایهٔ مدل‌های ORM (اگر بخواهیم کلاس تعریف کنیم)
Base = declarative_base()

async def get_tables_and_columns():
    """
    این تابع لیستی از جداول و ستون‌های آن‌ها را بر می‌گرداند.
    از MetaData.reflect برای introspection استفاده می‌کنیم.
    """
    # MetaData برای بارگذاری ساختار دیتابیس
    metadata = MetaData()
    # reflect روش خودش، bind باید سینک باشد
    metadata.reflect(bind=engine.sync_engine)

    schema_info = {}
    for table_name, table_obj in metadata.tables.items():
        # لیست نام ستون‌ها برای هر جدول
        cols = [col.name for col in table_obj.columns]
        schema_info[table_name] = cols
    return schema_info

# تست سریع اتصال و Introspection
if __name__ == "__main__":
    async def test():
        info = await get_tables_and_columns()
        for table, cols in info.items():
            print(f"Table: {table} -> Columns: {cols}")
    asyncio.run(test())