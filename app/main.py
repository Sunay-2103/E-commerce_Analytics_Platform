from fastapi import FastAPI
from app.database import engine, Base
from app.models import models

# Import all route modules
from app.routes import user, product, order, payment

# Create FastAPI app
app = FastAPI(
    title="E-commerce DevOps Analytics Platform",
    description="Backend APIs for Users, Products, Orders, and Payments",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(payment.router)

# Root endpoint
@app.get("/")
def home():
    return {"message": "E-commerce DevOps Analytics Platform is running"}
