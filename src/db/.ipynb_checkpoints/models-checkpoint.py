from pydantic import BaseModel, Field
from typing import List, Dict

class User(BaseModel):
    id: int
    name: str
    email: str

class Order(BaseModel):
    id: int
    user_id: int
    amount: float
    status: str

class DBSchema(BaseModel):
    tables: Dict[str, List[str]]
