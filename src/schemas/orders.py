from pydantic import BaseModel
from uuid import UUID



class OrderResponse(BaseModel):
    id: UUID
    title: str
    price: float
    description: str
    status: str


class OrderCreate(BaseModel):
    title: str
    price: float
    description: str = ""