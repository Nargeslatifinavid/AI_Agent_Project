from langgraph.graph import StateGraph, START, END


async def db_query_node(state: AgentState) -> AgentState:
    # کوئری به جدول users اگر prompt شامل "users" باشد
    prompt = state.get("prompt", "")
    async with AsyncSessionLocal() as session:
        if "users" in prompt.lower():
            result = await session.execute("SELECT * FROM users;")
            rows = result.fetchall()
        else:
            rows = []
    return {"prompt": prompt, "rows": rows}



class DBQueryNode(Node):
    async def run(self, prompt: str):
        async with AsyncSessionLocal() as session:
            if "users" in prompt.lower():
                result = await session.execute(text("SELECT * FROM users;"))
                return result.fetchall()
        return []





import os
import asyncio
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END  # ← Import صحیح :contentReference[oaicite:0]{index=0}
from src.db.client import AsyncSessionLocal
from transformers import AutoTokenizer, AutoModelForCausalLM
from sqlalchemy import text

# 1) بارگذاری مدل سبک (gpt2) از .env یا پیش‌فرض
model_id = os.getenv("LLM_MODEL", "gpt2")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
model.eval()

# 2) تعریف ساختار State با TypedDict
class AgentState(TypedDict, total=False):
    prompt: str
    rows: list
    answer: str

# 3) تعریف نودها به‌صورت توابع

def parse_node(state: AgentState) -> AgentState:
    # ورودی کاربر را مستقیماً در state می‌گذارد
    return {"prompt": state["prompt"]}


class DBQueryNode(Node):
    async def run(self, prompt: str):
        async with AsyncSessionLocal() as session:
            if "users" in prompt.lower():
                result = await session.execute(text("SELECT * FROM users;"))
                return result.fetchall()
        return []



def lm_node(state: AgentState) -> AgentState:
    # خلاصه‌سازی خروجی DB با LLM
    rows = state.get("rows", [])
    text = "\n".join(str(r) for r in rows)
    inputs = tokenizer(f"Data:\n{text}\nSummarize:", return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=50)
    answer = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"answer": answer}

# 4) مونتاژ گراف: START → parse → db_query → lm → END
graph = StateGraph(AgentState)
graph.add_node("parse", parse_node)
graph.add_node("db_query", db_query_node)
graph.add_node("lm", lm_node)

graph.add_edge(START, "parse")
graph.add_edge("parse", "db_query")
graph.add_edge("db_query", "lm")
graph.add_edge("lm", END)

# 5) کامپایل گراف
app = graph.compile()

# ۵) تابع handler برای فراخوانی گراف
async def handle(prompt: str) -> str:
    init_state = {"prompt": prompt}
    result_state = await app.ainvoke(init_state)
    return result_state.get("answer", "")

# ۶) تست سریع زمانی که ماژول مستقیماً اجرا می‌شود
if __name__ == "__main__":
    prompt = "List all users"
    ans = asyncio.run(handle(prompt))
    print("Prompt:", prompt)
    print("Answer:", ans)




#test agent


import asyncio
import pytest
from src.agent.langgraph_agent import handle

@pytest.mark.asyncio
async def test_list_all_users():
    """
    این تست اطمینان می‌دهد که handle
    حداقل یکی از کاربران seed شده را بازمی‌گرداند.
    """
    ans = await handle("List all users")
    assert "Ali Rezaei" in ans or "Sara Ahmadi" in ans

@pytest.mark.asyncio
async def test_non_user_query_returns_empty_summary():
    """
    اگر prompt شامل 'users' نباشد،
    نود DB لیست خالی می‌دهد و مدل هم یک پاسخ خالی یا کوتاه.
    """
    ans = await handle("Show me something else")
    # مدل احتمالا یه خلاصه خالی یا یه جمله‌ی کوتاه برمی‌گردونه:
    assert isinstance(ans, str)
