# tests/test_agent.py

import pytest
from src.agent.langgraph_agent import handle

@pytest.mark.asyncio
async def test_handle_users():
    ans = await handle("List all users")
    assert "Ali Rezaei" in ans or "Sara Ahmadi" in ans
