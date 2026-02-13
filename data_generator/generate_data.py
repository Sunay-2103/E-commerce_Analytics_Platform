import sys
import os
import random
from faker import Faker

# Fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import User, Product, Order, OrderItem, Payment

fake = Faker()


def create_users(db: Session, n=100):
    users = []
    for _ in range(n):
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            address=fake.address()
        )
        users.append(user)

    db.add_all(users)
    db.commit()
    return users


def create_products(db: Session, n=100):
    products = []
    for _ in range(n):
        product = Product(
            name=fake.word().capitalize(),
            price=round(random.uniform(100, 5000), 2),
            stock=random.randint(10, 500)
        )
        products.append(product)

    db.add_all(products)
    db.commit()
    return products


def create_orders(db: Session, users, products, n=1000):
    for _ in range(n):
        user = random.choice(users)

        order = Order(
            user_id=user.id,
            status=random.choice(["pending", "shipped", "delivered"])
        )

        db.add(order)
        db.flush()  # VERY IMPORTANT

        total_amount = 0

        for _ in range(random.randint(1, 5)):
            product = random.choice(products)
            quantity = random.randint(1, 3)

            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )

            total_amount += quantity * product.price
            db.add(item)

        payment = Payment(
            order_id=order.id,
            amount=round(total_amount, 2),
            status=random.choice(["success", "failed", "pending"])
        )

        db.add(payment)

    db.commit()


def main():
    db = SessionLocal()

    print("🚀 Generating users...")
    users = create_users(db, 100)

    print("📦 Generating products...")
    products = create_products(db, 100)

    print("🧾 Generating orders + payments...")
    create_orders(db, users, products, 1000)

    db.close()
    print("✅ Data generation completed!")


if __name__ == "__main__":
    main()
