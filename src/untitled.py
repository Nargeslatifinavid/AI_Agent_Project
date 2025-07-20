import os
import asyncio
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from sqlalchemy import text
from src.db.client import AsyncSessionLocal
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# —— 1) بارگذاری مدل instruction-tuned سبک ——
model_id = os.getenv("LLM_MODEL", "google/flan-t5-small")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
model.eval()

# —— 2) تعریف ساختار state ——
class AgentState(TypedDict, total=False):
    prompt: str
    rows: list
    answer: str

# —— 3) گره‌های گراف ——
def parse_node(state: AgentState) -> AgentState:
    return {"prompt": state["prompt"]}

async def db_query_node(state: AgentState) -> AgentState:
    prompt = state.get("prompt", "")
    async with AsyncSessionLocal() as session:
        if "users" in prompt.lower():
            result = await session.execute(text("SELECT * FROM users;"))
            rows = result.fetchall()
        else:
            rows = []
    return {"prompt": prompt, "rows": rows}

def lm_node(state: AgentState) -> AgentState:
    rows = state.get("rows", [])
    if not rows:
        return {"answer": ""}
    # آماده‌سازی پرامپت خلاصه‌سازی
    text_data = "\n".join(str(r) for r in rows)
    prompt = f"summarize: {text_data}"
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=100)
    answer = tokenizer.decode(output[0], skip_special_tokens=True).strip()
    return {"answer": answer}

# —— 4) مونتاژ StateGraph ——
graph = StateGraph(AgentState)
graph.add_node("parse", parse_node)
graph.add_node("db_query", db_query_node)
graph.add_node("lm", lm_node)
graph.add_edge(START, "parse")
graph.add_edge("parse", "db_query")
graph.add_edge("db_query", "lm")
graph.add_edge("lm", END)
app = graph.compile()

# —— 5) تابع handler که تست می‌کند ——
async def handle(prompt: str) -> str:
    init_state = {"prompt": prompt}
    result_state = await app.ainvoke(init_state)
    return result_state.get("answer", "")

# —— 6) CLI با آرگیومنت ——
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the LangGraph Agent")
    parser.add_argument(
        "--prompt", "-p", type=str, required=True, help="Agent prompt"
    )
    args = parser.parse_args()
    ans = asyncio.run(handle(args.prompt))
    print("Prompt:", args.prompt)
    print("Answer:", ans)
