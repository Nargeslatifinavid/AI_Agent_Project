
# tests/test_db.py

import pytest
from src.db.client import get_tables_and_columns_sync

def test_introspection():
    schema = get_tables_and_columns_sync()
    assert "users" in schema
    assert "orders" in schema
    assert set(["id", "name", "email"]).issubset(set(schema["users"]))
