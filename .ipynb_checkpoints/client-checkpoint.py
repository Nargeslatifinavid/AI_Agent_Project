# src/db/client.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine.url import make_url

# --------------------------------------------------------------------------- #
# 1) DATABASE_URL: اگر متغیر محیطی موجود نباشد، به مقدار پیش‌فرض زیر برمی‌گردد.
#    این مقدار دقیقاً با docker-compose.yml (سرویس db) هماهنگ است.            #
# --------------------------------------------------------------------------- #
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password123@127.0.0.1:5432/mydb",
)

# --------------------------------------------------------------------------- #
# 2) Async engine + session برای کد Agent                                     #
# --------------------------------------------------------------------------- #
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# --------------------------------------------------------------------------- #
# 3) تابع همگام برای introspection (تست DB)                                   #
# --------------------------------------------------------------------------- #
def get_tables_and_columns_sync() -> dict[str, list[str]]:
    """
    جداول و ستون‌های دیتابیس را به‌صورت دیکشنری {table: [columns]} برمی‌گرداند.
    این تابع *هیچ* دادهٔ فیک تولید نمی‌کند؛ در صورت نبودن اتصال یا اعتبار اشتباه،
    همان خطا را بالا می‌دهد تا تست شکست بخورد.
    """
    # 3.1) اگر URL از درایور asyncpg استفاده می‌کند، به psycopg2 سوییچ کن
    url = make_url(DATABASE_URL)
    if url.drivername.endswith("+asyncpg"):
        url = url.set(drivername="postgresql+psycopg2")

    # 3.2) اطمینان از IPv4 برای localhost
    if url.host in {"localhost", "::1"}:
        url = url.set(host="127.0.0.1")

    # 3.3) ساخت یک Engine همگام و Reflect متادیتا
    engine_sync = create_engine(str(url), echo=False, future=True)
    metadata = MetaData()
    metadata.reflect(bind=engine_sync)

    schema: dict[str, list[str]] = {
        table_name: [c.name for c in table.columns]
        for table_name, table in metadata.tables.items()
    }

    engine_sync.dispose()
    return schema
gine_sync.dispose()
    return schema
