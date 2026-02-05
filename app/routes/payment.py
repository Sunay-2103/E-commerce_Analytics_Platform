from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.crud.payment import create_payment, get_payments

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/payments", response_model=PaymentResponse)
def add_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db, payment)

@router.get("/payments", response_model=list[PaymentResponse])
def list_payments(db: Session = Depends(get_db)):
    return get_payments(db)
