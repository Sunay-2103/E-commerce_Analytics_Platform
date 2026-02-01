from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int

class ProductResponse(ProductCreate):
    id: int

    class Config:
        orm_mode = True
