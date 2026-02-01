from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.product import ProductCreate, ProductResponse
from app.crud.product import create_product, get_products

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/products", response_model=ProductResponse)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, product)

@router.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return get_products(db)
