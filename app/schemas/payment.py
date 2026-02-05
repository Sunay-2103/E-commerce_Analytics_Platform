from pydantic import BaseModel

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    payment_status: str
    amount: float

class PaymentResponse(PaymentCreate):
    id: int

    class Config:
        orm_mode = True
