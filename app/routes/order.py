from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.order import OrderCreate, OrderResponse
from app.crud.order import create_order, get_orders

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/orders", response_model=OrderResponse)
def add_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, order)

@router.get("/orders", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return get_orders(db)
