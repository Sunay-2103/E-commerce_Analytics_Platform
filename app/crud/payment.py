from sqlalchemy.orm import Session
from app.models.models import Payment

def create_payment(db: Session, payment):
    db_payment = Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payments(db: Session):
    return db.query(Payment).all()
