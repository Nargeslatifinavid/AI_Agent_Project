# — Load model —
#model_id = os.getenv("LLM_MODEL", "tiiuae/falcon-7b-instruct")
#tokenizer = AutoTokenizer.from_pretrained(model_id)
#model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
import os
import asyncio
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from src.db.client import AsyncSessionLocal
#from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sqlalchemy import text
import argparse
# 1) 
#model_id = os.getenv("LLM_MODEL", "gpt2")
model_id = os.getenv("LLM_MODEL", "google/flan-t5-small")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
model.eval()

# 2) structure State
class AgentState(TypedDict, total=False):
    prompt: str
    rows: list
    answer: str

# 3) nodes
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
    text_data = "\n".join(str(r) for r in rows)
    inputs = tokenizer(f"Data:\n{text_data}\nSummarize:", return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=150)
    #answer = tokenizer.decode(output[0], skip_special_tokens=True)
    answer = tokenizer.decode(output[0], skip_special_tokens=True).strip()
    return {"answer": answer}

# 4) graph
graph = StateGraph(AgentState)
graph.add_node("parse", parse_node)
graph.add_node("db_query", db_query_node)
graph.add_node("lm", lm_node)

graph.add_edge(START, "parse")
graph.add_edge("parse", "db_query")
graph.add_edge("db_query", "lm")
graph.add_edge("lm", END)

# 5) کامپایل
app = graph.compile()

# 6) handler
async def handle(prompt: str) -> str:
    init_state = {"prompt": prompt}
    result_state = await app.ainvoke(init_state)
    return result_state.get("answer", "")

# 7) test
if __name__ == "__main__":
 

    parser = argparse.ArgumentParser(description="Run the LangGraph Agent")
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        required=True,
        help="The prompt to send to the Agent (e.g. \"List all users\")",
    )
    args = parser.parse_args()

    # run with propmt
    answer = asyncio.run(handle(args.prompt))
    print(f"Prompt: {args.prompt}")
    print(f"Answer: {answer}")
