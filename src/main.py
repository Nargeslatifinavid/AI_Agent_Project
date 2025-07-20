# src/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from src.agent.langgraph_agent import handle

class QueryIn(BaseModel):
    prompt: str

class QueryOut(BaseModel):
    answer: str

app = FastAPI()

@app.post("/query", response_model=QueryOut)
async def query_endpoint(q: QueryIn):
   
    ans = await handle(q.prompt)
    return {"answer": ans}
