# tests/test_db.py

import pytest
import asyncio
from src.db.client import get_tables_and_columns

@pytest.mark.asyncio
async def test_introspection():
    schema = await get_tables_and_columns()
    # جدول users حتما باید وجود داشته باشد
    assert "users" in schema
    # ستون‌های اصلی
    assert set(["id","name","email"]).issubset(set(schema["users"]))
    # جدول orders
    assert "orders" in schema
    assert set(["id","user_id","amount","status"]).issubset(set(schema["orders"]))
