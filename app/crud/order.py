from sqlalchemy.orm import Session
from app.models.models import Order

def create_order(db: Session, order):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session):
    return db.query(Order).all()
