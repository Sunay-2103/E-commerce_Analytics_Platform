"""
Data generator for E-commerce DevOps Analytics Platform.
Generates realistic, time-spread data suitable for Power BI / Streamlit dashboards.

Usage:
    python -m data_generator.generate_data
"""

import sys
import os
import random
from datetime import datetime, timedelta

from faker import Faker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import User, Product, Order, OrderItem, Payment

fake = Faker("en_IN")  # Indian locale — realistic for an Indian e-commerce project

# ── Config ────────────────────────────────────────────────────────────────────
PRODUCT_CATEGORIES = [
    "Electronics", "Clothing", "Books", "Home & Kitchen",
    "Sports", "Beauty", "Toys", "Grocery", "Automotive", "Furniture"
]

PAYMENT_METHODS = ["card", "upi", "netbanking", "cod"]

ORDER_STATUSES = ["pending", "shipped", "delivered", "cancelled"]
# Weighted to reflect real distribution: most orders are delivered
ORDER_STATUS_WEIGHTS = [0.10, 0.15, 0.65, 0.10]

PAYMENT_STATUS_MAP = {
    "delivered": "success",
    "shipped":   "success",
    "pending":   random.choice(["success", "pending"]),
    "cancelled": random.choice(["failed", "pending"]),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def random_past_datetime(days_back: int = 180) -> datetime:
    """Returns a random datetime within the last N days — spreads data over 6 months."""
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return datetime.utcnow() - delta


# ── Generators ────────────────────────────────────────────────────────────────
def create_users(db: Session, n: int = 200) -> list[User]:
    print(f"  Creating {n} users...")
    users = [
        User(
            name=fake.name(),
            email=fake.unique.email(),
            address=fake.address(),
            created_at=random_past_datetime(365),  # users joined over the last year
        )
        for _ in range(n)
    ]
    db.add_all(users)
    db.commit()
    return users


def create_products(db: Session, n: int = 100) -> list[Product]:
    print(f"  Creating {n} products...")
    product_names = {
        "Electronics":    ["Laptop", "Smartphone", "Headphones", "Smart Watch", "Tablet", "Camera"],
        "Clothing":       ["T-Shirt", "Jeans", "Jacket", "Dress", "Saree", "Kurta"],
        "Books":          ["Novel", "Textbook", "Comic", "Biography", "Self-Help", "Cook Book"],
        "Home & Kitchen": ["Mixer", "Pressure Cooker", "Bed Sheet", "Curtains", "Pillow", "Lamp"],
        "Sports":         ["Cricket Bat", "Football", "Yoga Mat", "Dumbbells", "Cycle", "Racket"],
        "Beauty":         ["Shampoo", "Moisturizer", "Perfume", "Lipstick", "Sunscreen", "Serum"],
        "Toys":           ["LEGO Set", "Action Figure", "Doll", "Puzzle", "Board Game", "Car"],
        "Grocery":        ["Rice (5kg)", "Cooking Oil", "Masala Pack", "Tea", "Coffee", "Oats"],
        "Automotive":     ["Car Cover", "Bike Helmet", "Seat Cushion", "Air Freshener", "Tyre Gauge"],
        "Furniture":      ["Office Chair", "Study Table", "Bookshelf", "Bed Frame", "Sofa", "Wardrobe"],
    }

    products = []
    for _ in range(n):
        category = random.choice(PRODUCT_CATEGORIES)
        name = random.choice(product_names.get(category, ["Product"]))
        products.append(Product(
            name=f"{name} - {fake.word().capitalize()}",
            category=category,
            price=round(random.uniform(99, 49999), 2),
            stock=random.randint(0, 500),
            created_at=random_past_datetime(400),
        ))

    db.add_all(products)
    db.commit()
    return products


def create_orders(db: Session, users: list[User], products: list[Product], n: int = 1000):
    print(f"  Creating {n} orders with items and payments...")
    for i in range(n):
        user = random.choice(users)
        order_status = random.choices(ORDER_STATUSES, weights=ORDER_STATUS_WEIGHTS, k=1)[0]
        order_date = random_past_datetime(180)  # 6 months of data for trend charts

        order = Order(
            user_id=user.id,
            status=order_status,
            total_amount=0,
            created_at=order_date,
        )
        db.add(order)
        db.flush()  # Get order.id before creating children

        total_amount = 0
        num_items = random.randint(1, 5)

        for _ in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 4)
            item_price = float(product.price)

            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=round(item_price, 2),
            )
            total_amount += quantity * item_price
            db.add(item)

        # Update order total
        order.total_amount = round(total_amount, 2)

        # Payment status is derived from order status for data consistency
        payment_status_map = {
            "delivered": "success",
            "shipped":   "success",
            "pending":   random.choice(["success", "pending"]),
            "cancelled": random.choice(["failed", "pending"]),
        }

        payment = Payment(
            order_id=order.id,
            payment_method=random.choice(PAYMENT_METHODS),
            status=payment_status_map[order_status],
            amount=round(total_amount, 2),
            created_at=order_date + timedelta(minutes=random.randint(1, 30)),
        )
        db.add(payment)

        # Commit in batches of 100 to avoid memory buildup
        if (i + 1) % 100 == 0:
            db.commit()
            print(f"    {i + 1}/{n} orders committed...")

    db.commit()


# ── Entry Point ───────────────────────────────────────────────────────────────
def main():
    db = SessionLocal()
    print("🚀 Starting data generation...\n")

    users = create_users(db, n=200)
    products = create_products(db, n=100)
    create_orders(db, users, products, n=1000)

    db.close()
    print("\n✅ Data generation complete!")
    print("   Users:    200")
    print("   Products: 100")
    print("   Orders:   1000 (with items + payments)")


if __name__ == "__main__":
    main()
