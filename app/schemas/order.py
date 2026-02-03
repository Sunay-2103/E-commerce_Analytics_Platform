from pydantic import BaseModel

class OrderCreate(BaseModel):
    user_id: int
    total_amount: float
    status: str

class OrderResponse(OrderCreate):
    id: int

    class Config:
        orm_mode = True
